# Research: subset-b-004975

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_chip.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_chip.c

## Purpose
Implements the ZD1211/ZD1211B chip abstraction above USB register commands and below mac80211/RF-specific drivers. It initializes the MAC/BBP register blocks, reads EEPROM policy and calibration data, serializes register access, manages RF callbacks, configures channel/rates/beacon/LED state, and exposes chip lifecycle helpers to `zd_mac.c`.

## Important APIs, Types, And Functions
Public entry points include `zd_chip_init()`, `zd_chip_clear()`, `zd_chip_init_hw()`, `zd_chip_read_mac_addr_fw()`, `zd_ioread16/32()`, `zd_iowrite16/32()`, `zd_ioread32v()`, `zd_iowrite32a()`, `zd_chip_set_channel()`, `zd_read_regdomain()`, `zd_write_mac_addr()`, `zd_write_bssid()`, `zd_chip_switch_radio_on/off()`, `zd_chip_enable_int()`, `zd_chip_disable_int()`, `zd_chip_enable_rxtx()`, `zd_chip_disable_rxtx()`, `zd_chip_enable_hwint()`, `zd_chip_disable_hwint()`, `zd_chip_set_basic_rates()`, `zd_chip_control_leds()`, `zd_set_beacon_interval()`, `zd_rx_rate()`, `zd_chip_set_multicast_hash()`, and `zd_chip_get_tsf()`. Internal helpers convert 32-bit register IO into 16-bit USB requests, read EEPROM POD/calibration fields, lock/unlock PHY registers, reset ZD1211/ZD1211B PHY tables, initialize HMAC registers, and apply optional EEPROM-driven RF/BBP patches.

## Control Flow
`zd_chip_init()` zeroes the composite state and initializes USB and RF subobjects. Hardware bring-up in `zd_chip_init_hw()` runs under `chip->mutex`: marks `CR_AFTER_PNP`, discovers firmware register base, disables GPI and hardware interrupts, reads POD flags and RF type, writes BBP/HMAC defaults, calls `zd_rf_init_hw()`, records firmware version, reads calibration/integration tables, and prints a device ID. Runtime channel changes lock PHY registers, invoke the RF driver's `set_channel`, update per-channel power/integration/OFDM calibration when the RF wants it, patch CCK gain and 6M band-edge settings, then unlock PHY registers. RX/TX and interrupt methods delegate to the USB layer while preserving the chip mutex contract.

## State And Persistence
Persistent state lives in `struct zd_chip`: `zd_usb`, `zd_rf`, `mutex`, firmware register base, EEPROM-derived power calibration arrays for 14 channels, OFDM calibration tables, link LED selection, PA type, and patch capability bits. Register writes persist in device firmware/hardware until reset. The code deliberately keeps all USB register access serialized by `chip->mutex`; many locked helpers assert that contract in debug builds.

## Dependencies And Integration Points
Depends on `zd_usb` register/RF write primitives, `zd_rf` RF callbacks, `zd_mac` rate and PLCP definitions, Linux mutexes, mac80211 interface type constants, and device logging. It integrates upward with mac80211 operations through `zd_mac.c` and downward with firmware over USB vendor requests and interrupt endpoints.

## Risks
Register ordering is fragile, especially PHY lock/unlock, ZD_CR204 before ZD_CR203, and beacon timing register invariants. `read_values()` packs EEPROM words into byte tables with legacy indexing; off-by-one or guard errors affect transmit power. Channel 1/11 band-edge comments note regulatory-domain assumptions. Several APIs return zeroed/default behavior after hardware IO errors, such as TSF read returning 0. Any caller bypassing `chip->mutex` can race USB command buffers or RF state.

## Test Signals
Probe should log firmware version and full chip/RF identity. Exercise ZD1211 and ZD1211B devices, each supported RF type, channels 1/11/14, interface start/stop, beacon interval changes, multicast filter updates, LED association/scanning transitions, suspend/reset restore, and failed USB IO paths. DEBUG builds should not trip `ZD_ASSERT(mutex_is_locked(&chip->mutex))`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_chip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_chip.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_chip.h

## Purpose
Defines the ZD1211/ZD1211B chip register map, EEPROM layout, firmware register offsets, bit definitions, chip state object, and chip API used by MAC, USB, and RF code. It is the central hardware contract for BBP/MAC/HMAC register access.

## Important APIs, Types, And Functions
Important constants include address-space bases `CR_START`, `FW_START`, `E2P_START`, helpers `CTL_REG()`, `E2P_DATA()`, `FWRAW_DATA()`, hundreds of `ZD_CR*` and `CR_*` register addresses, interrupt bits, RX filter masks, beacon mode bits, rate masks, encryption modes, retry defaults, `HWINT_ENABLED`, calibration table sizes, EEPROM offsets, and firmware LED/link register values. `struct zd_chip` embeds USB/RF state and EEPROM-derived calibration/policy fields. Inline helpers map between `zd_usb`, `zd_rf`, and `zd_chip`, wrap locked 16/32-bit IO, expose encryption/basic-rate/beacon helpers, and manipulate multicast hash bits.

## Control Flow
No independent runtime flow exists, but the header defines the register and locking contract implemented by `zd_chip.c`: callers either use public wrappers that take `chip->mutex`, or locked wrappers while already holding it. RF drivers call `zd_rfwrite_locked()` and CR write helpers while chip code has PHY registers unlocked.

## State And Persistence
`struct zd_chip` is long-lived for the USB interface lifetime. Its calibration arrays mirror EEPROM contents and are reused for every channel switch. The register constants describe persistent device-side state such as basic/mandatory rate tables, RX filter, group hash, beacon FIFO/semaphore, LED registers, HMAC retry settings, TSF, and encryption mode.

## Dependencies And Integration Points
Includes mac80211 plus local `zd_rf.h` and `zd_usb.h`. It is consumed by every ZD1211RW implementation file and exposes the boundary between mac80211-facing operations and USB vendor command transport.

## Risks
This is a large hardware ABI surface with many vendor-derived magic values. Incorrect address-space assumptions are easy because control registers are byte-addressed while firmware/EEPROM areas are word-addressed. `zd_mc_add_addr()` uses only high bits of the last MAC byte, matching hardware but giving coarse multicast filtering. `zd_chip_reset()` is declared but not implemented in this file set, so users must not assume it is available unless linked elsewhere.

## Test Signals
Build coverage catches missing declarations and bad constants. Runtime validation comes from successful firmware upload, register reads/writes, EEPROM parsing, channel switching, beacon programming, multicast filtering, RX/TX interrupts, and TSF reads on both ZD1211 and ZD1211B variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_chip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_def.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_def.h

## Purpose
Provides small shared definitions for the ZD1211RW driver: the `zd_addr_t` register-address type, debug logging helpers, debug assertions, and debug-only memory poisoning.

## Important APIs, Types, And Functions
Defines `typedef u16 zd_addr_t`, `dev_printk_f()`, `dev_dbg_f()`, `dev_dbg_f_limit()`, `dev_dbg_f_cond()`, `ZD_ASSERT()`, and `ZD_MEMCLEAR()`. In non-DEBUG builds, debug helpers compile to no-op forms that preserve argument type checking minimally and avoid side effects except `(void)(dev)`.

## Control Flow
No runtime flow beyond conditional debug logging/assertion. In DEBUG builds, failed assertions print file/line/expression and dump the stack; `ZD_MEMCLEAR()` fills memory with `0xff` after teardown.

## State And Persistence
No persistent state. The file influences teardown diagnostics by optionally poisoning structs after clear functions.

## Dependencies And Integration Points
Depends on Linux kernel, stringify, and device logging headers. Included by the ZD1211RW C and header files as the baseline local utility header.

## Risks
Debug-only behavior can hide bugs in production builds, especially assertions around locking. `ZD_MEMCLEAR()` is intentionally a no-op outside DEBUG, so clear paths must explicitly release resources before invoking it.

## Test Signals
Compile with and without `DEBUG` to confirm both macro sets. DEBUG runs should surface lock contract violations during register IO, RF operations, USB async command batching, and teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_def.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_mac.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_mac.c

## Purpose
Implements the mac80211 softmac layer for ZD1211RW. It describes 2.4 GHz channels/rates, allocates/registers `ieee80211_hw`, implements ieee80211 operations, translates TX/RX frames to and from Zydas firmware formats, tracks ACK status, configures interface filters/multicast/beacons, and runs LED and beacon watchdog work.

## Important APIs, Types, And Functions
Exports `zd_mac_alloc_hw()`, `zd_mac_clear()`, `zd_mac_preinit_hw()`, `zd_mac_init_hw()`, `zd_mac_rx()`, `zd_mac_tx_failed()`, `zd_mac_tx_to_dev()`, `zd_op_start()`, `zd_op_stop()`, and `zd_restore_settings()`. Static mac80211 ops include `zd_op_tx`, `zd_op_add_interface`, `zd_op_remove_interface`, `zd_op_config`, `zd_op_prepare_multicast`, `zd_op_configure_filter`, `zd_op_bss_info_changed`, and `zd_op_get_tsf`. Key helpers include `fill_ctrlset()`, `zd_calc_tx_length_us()`, `filter_ack()`, `zd_mac_tx_status()`, `zd_mac_config_beacon()`, `zd_process_intr()`, beacon watchdog handlers, and link LED housekeeping.

## Control Flow
Probe allocates `ieee80211_hw`, initializes local channel/rate tables and work items, then reads the permanent MAC before registration. `start` initializes USB hardware if needed, enables USB interrupts, sets basic rates/filter/hash, powers radio, enables RX/TX and hardware interrupts, then starts periodic work. TX prepends `struct zd_ctrlset`, computes PLCP service/current length, stores the hw pointer in skb metadata, and submits through USB. TX completion either reports immediate status or queues the frame for ACK matching; retry-fail USB interrupts call `zd_mac_tx_failed()`. RX validates length/status, builds `ieee80211_rx_status`, filters ACKs into TX status, copies data into a new skb, and calls `ieee80211_rx_irqsafe()`. AP/IBSS/mesh beacon changes write the beacon FIFO under a hardware semaphore and watchdog recovery resets stale beacon state.

## State And Persistence
`struct zd_mac` persists the current vif/type, regulatory domain, channel, multicast hash, association state, filter flags, ack wait queue, pending ACK signal, channel/rate tables, and delayed work. `beacon.cur_beacon` caches the last programmed beacon to avoid redundant writes. Hardware state persists through chip registers and is restored by `zd_restore_settings()` after USB reset/resume.

## Dependencies And Integration Points
Depends on mac80211/cfg80211 APIs, netdevice helpers, USB reset queueing, local chip/RF/USB APIs, global `zd_workqueue`, and Linux skb/workqueue/spinlock infrastructure. It is called by the USB probe/reset paths and calls into chip methods for all hardware register updates.

## Risks
ACK accounting is heuristic and queue-based; lost or reordered retry-fail/ACK interrupts can misreport TX status. Beacon programming can wedge if `CR_BCN_FIFO_SEMAPHORE` is not released, so the code resets the USB device on timeout. RX uses unlocked reads of filter flags by design. Single-vif assumptions are enforced by `mac->type != UNSPECIFIED`. `set_mac_and_bssid()` returns `-1` when no vif exists rather than a conventional errno. Repeated copies on RX and beacon writes are simple but not zero-copy.

## Test Signals
Validate station, AP, ad-hoc, mesh, and monitor-like filter cases; TX status under success, retry fail, no-ACK, queue pressure, and AP buffered multicast after beacon; RX bad-FCS pass-through, control-frame pass-through, ACK filtering, QoS/A4 padding; regulatory hints from EEPROM; beacon semaphore timeout recovery; reset/resume restore; LED scanning/associated behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_mac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_mac.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_mac.h

## Purpose
Defines ZD1211RW MAC-layer packet formats, rate encodings, RX/TX status formats, per-device MAC state, regulatory/channel constants, and public MAC APIs.

## Important APIs, Types, And Functions
Key types are packed `struct zd_ctrlset`, `rx_length_info`, `rx_status`, `tx_retry_rate`, `tx_status`, `housekeeping`, `beacon`, and `zd_mac`. Constants define Zydas CCK/OFDM rates, PLCP header sizes, ctrlset control bits, RX error/decryption bits, regulatory domains, channel bounds, and maximum ACK waiters. Inline helpers expose PLCP rate extraction and conversions between `ieee80211_hw`, `zd_mac`, `zd_chip`, and `zd_usb`.

## Control Flow
The header sets the binary contract used by TX and RX paths. TX prepends `zd_ctrlset`; RX receives a PLCP header plus trailing `rx_status` and sometimes an `rx_length_info` trailer for merged USB frames. Public functions are invoked by USB probe/completion/reset and mac80211 registration.

## State And Persistence
`struct zd_mac` is the long-lived mac80211 private area. It embeds `struct zd_chip`, spinlocks, vif pointer, work items, multicast hash, interrupt buffer, channel/rate arrays, ack queue, and filter/association flags. `beacon.cur_beacon` owns an skb until replaced or disabled.

## Dependencies And Integration Points
Includes Linux kernel and mac80211 headers plus `zd_chip.h`. The declarations are shared between `zd_mac.c`, `zd_usb.c`, and chip code that needs rate/RX status definitions.

## Risks
Packed firmware-facing structs must remain layout-compatible. `info->rate_driver_data` is used by TX/USB code for private pointers and timestamps, so any mac80211 API changes can break assumptions. ACK waiter limit bounds memory but may produce status for old frames without exact hardware confirmation.

## Test Signals
Compile with structure layout warnings enabled, run TX/RX across all supported rates and short preamble settings, receive merged USB frames, pass FCS-failed/control frames, and verify AP beacon/TIM refresh behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_mac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_rf.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_rf.c

## Purpose
Provides the common RF transceiver abstraction for ZD1211RW. It maps EEPROM RF type IDs to names and RF-specific initializer modules, installs per-RF callbacks, and wraps channel/radio operations with chip PHY-register locking.

## Important APIs, Types, And Functions
Exports `zd_rf_name()`, `zd_rf_init()`, `zd_rf_clear()`, `zd_rf_init_hw()`, `zd_rf_scnprint_id()`, `zd_rf_set_channel()`, `zd_switch_radio_on()`, `zd_switch_radio_off()`, `zd_rf_patch_6m_band_edge()`, and `zd_rf_generic_patch_6m()`. It dispatches to `zd_rf_init_rf2959()`, `zd_rf_init_al2230()`, `zd_rf_init_al7230b()`, and `zd_rf_init_uw2453()`.

## Control Flow
`zd_rf_init()` defaults `update_channel_int` on. During chip init, `zd_rf_init_hw()` selects an RF implementation by type, stores the type, locks PHY registers, calls the RF `init_hw` callback, then unlocks. Later channel and radio state calls validate channel range and invoke installed callbacks under the chip mutex and, for radio on/off, PHY lock/unlock.

## State And Persistence
`struct zd_rf` stores RF type, current channel, capability bits, optional private data, and callback pointers. The RF-specific register programming persists in hardware until channel changes, radio state changes, or device reset.

## Dependencies And Integration Points
Depends on `zd_chip` for lock/register helpers and `zd_mac.h` for channel bounds. Integrated from `zd_chip_init_hw()` after EEPROM POD parsing.

## Risks
Unsupported RF IDs fail probe. Callback pointers must be installed correctly before `zd_rf_init_hw()` calls `rf->init_hw`. Channel validation only enforces 1..14, not regulatory permissions. The RF abstraction assumes callers already hold `chip->mutex`.

## Test Signals
Probe each supported RF, verify unsupported IDs return `-ENODEV`, switch channels 1..14, toggle radio on/off, and inspect debug identity strings for correct RF names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_rf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_rf.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_rf.h

## Purpose
Declares RF type IDs, RF write bit widths, `struct zd_rf`, RF callback contracts, common RF operations, and initializer entry points for each supported RF chip.

## Important APIs, Types, And Functions
Defines IDs such as `AL2230_RF`, `AL7230B_RF`, `UW2453_RF`, `AL2230S_RF`, and `RF2959_RF`; `RF_CHANNEL(ch)` table indexing; `RF_REG_BITS`, `RF_VALUE_BITS`, and `RF_RV_BITS`; callback members `init_hw`, `set_channel`, `switch_radio_on`, `switch_radio_off`, `patch_6m_band_edge`, and `clear`; and inline capability checks `zd_rf_should_update_pwr_int()` and `zd_rf_should_patch_cck_gain()`.

## Control Flow
No standalone flow. The header defines how RF implementation files register behavior and how chip code queries RF capabilities during channel calibration and optional patches.

## State And Persistence
`struct zd_rf` persists current channel, RF type, capability flags, private implementation data, and function pointers for the device lifetime.

## Dependencies And Integration Points
Included by chip, MAC, and RF implementation files. The chip object embeds `struct zd_rf` and converts back through `zd_rf_to_chip()`.

## Risks
The callback interface has no NULL checks in hot paths after init. RF private data ownership belongs to the RF implementation's `clear` callback. Incorrect capability flags can double-apply or skip EEPROM calibration.

## Test Signals
Build all RF implementation files, probe hardware with each EEPROM RF ID, and verify RF-specific `clear` paths under disconnect/reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_rf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_rf_al2230.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_rf_al2230.c

## Purpose
Implements RF programming for Airoha AL2230 and AL2230S transceivers on ZD1211 and ZD1211B devices. It contains per-channel RF register tables, initialization sequences, channel switching, radio power control, and AL2230S-specific adjustments.

## Important APIs, Types, And Functions
Exports `zd_rf_init_al2230()`. Internal functions include `zd1211_al2230_init_hw()`, `zd1211b_al2230_init_hw()`, `zd1211_al2230_set_channel()`, `zd1211b_al2230_set_channel()`, `zd1211_al2230_switch_radio_on()`, `zd1211b_al2230_switch_radio_on()`, `al2230_switch_radio_off()`, and `zd1211b_al2230_finalize_rf()`. Tables `zd1211_al2230_table` and `zd1211b_al2230_table` hold per-channel RF words; `ioreqs_init_al2230s` patches AL2230S register values.

## Control Flow
Initialization chooses ZD1211 or ZD1211B sequences based on `zd_chip_is_zd1211b()`. Each sequence writes BBP CR tables, optional AL2230S overrides, RF channel/default words, PLL enable/disable sequences, phase-noise/yield fixes, and final CR203/CR240 state. Channel changes write the per-channel RF words and finalize the RF. Radio on/off toggles CR11 and CR251 values appropriate to chip generation.

## State And Persistence
No private heap state. Behavior depends on `chip->al2230s_bit`, `rf.type`, and `chip->new_phy_layout`. `rf->patch_cck_gain` is enabled and `rf->patch_6m_band_edge` points to the generic chip patch.

## Dependencies And Integration Points
Uses chip locked write helpers, RF serial writes, CR register definitions, and RF type from EEPROM POD. Installed through `zd_rf_init_hw()` in the common RF layer.

## Risks
Magic register sequences are vendor-derived and order-sensitive. AL2230S detection combines EEPROM bit and RF type; wrong detection changes band-edge and init values. ZD1211B uses faster CR-based RF writes for many values while original ZD1211 uses USB RF writes; mixing paths would break programming.

## Test Signals
Probe AL2230 and AL2230S devices on both ZD1211 and ZD1211B, switch all channels, test channels 1/11 for band-edge patching, toggle radio, and compare TX power/receive sensitivity against vendor-driver behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_rf_al2230.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_rf_al7230b.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_rf_al7230b.c

## Purpose
Implements RF programming for the Airoha AL7230B transceiver. It supports both original ZD1211 and ZD1211B register sequences, including new/old PHY layout differences and a ZD1211B-specific 6M band-edge patch.

## Important APIs, Types, And Functions
Exports `zd_rf_init_al7230b()`. Internal functions include `zd1211_al7230b_init_hw()`, `zd1211b_al7230b_init_hw()`, `zd1211_al7230b_set_channel()`, `zd1211b_al7230b_set_channel()`, radio on/off helpers, `zd1211b_al7230b_finalize()`, and `zd1211b_al7230b_patch_6m()`. Tables `chan_rv`, `std_rv`, `rv_init1`, `rv_init2`, and `ioreqs_sw` encode common RF and BBP programming.

## Control Flow
Initialization writes AL7230B-specific CR values, RF standard words, channel-1 values, PLL cycles, and final CR203/CR240 state. ZD1211B setup branches on `chip->new_phy_layout` for several CR values. Channel switching powers PLL down, rewrites standard RF words and channel words, applies switch registers, powers PLL back on, and finalizes. Radio on/off uses CR11 plus CR251 generation-specific PLL values.

## State And Persistence
No private heap state. The selected callback set persists in `struct zd_rf`; chip fields `new_phy_layout` and generation determine programming. Non-B ZD1211 enables CCK gain patching, while B uses a custom `patch_6m_band_edge`.

## Dependencies And Integration Points
Uses common RF/chip locked register helpers and is selected by `AL7230B_RF` from EEPROM. It relies on chip-level channel calibration and optional 6M patch invocation.

## Risks
Many values differ subtly from AL2230 despite comments noting similarity. Channel 11 band-edge logic is explicitly flagged as regulatory-domain sensitive. New/old PHY detection changes RF performance. Finalization must reapply CR203 after a split write marker.

## Test Signals
Probe AL7230B on ZD1211 and ZD1211B with old/new PHY layouts, switch all 2.4 GHz channels, validate channel 1/11 edge behavior, run AP beacon/TX tests after channel changes, and confirm radio power toggles leave PLL state usable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_rf_al7230b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_rf_rf2959.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_rf_rf2959.c

## Purpose
Implements RF programming for RFMD RF2959 transceivers on original ZD1211 devices. It initializes BBP/RF registers, programs per-channel synthesizer values, and toggles radio power.

## Important APIs, Types, And Functions
Exports `zd_rf_init_rf2959()`. Internal functions include `rf2959_init_hw()`, `rf2959_set_channel()`, `rf2959_switch_radio_on()`, and `rf2959_switch_radio_off()`. `rf2959_table` maps channels to two RF words. A disabled debug block decodes RF2959 register-write bitfields for diagnostics.

## Control Flow
`zd_rf_init_rf2959()` rejects ZD1211B with `-ENODEV`, then installs callbacks. Hardware init writes a CR table and a default RF register vector. Channel switching writes the two per-channel RF words. Radio on/off writes CR10/CR11 combinations specific to RF2959.

## State And Persistence
No private heap state or special capability flags. Hardware RF/BBP register state persists until channel change, radio power change, or reset.

## Dependencies And Integration Points
Uses chip locked IO and RF serial write helpers. Selected from EEPROM RF ID `RF2959_RF` by the common RF layer.

## Risks
RF2959 is not supported for ZD1211B. Some register choices are documented as departures from vendor defaults to avoid CTS/TX continuation issues. The table includes comments about undocumented/bogus RF register references, which increases regression risk.

## Test Signals
Probe original ZD1211 RF2959 hardware, verify ZD1211B rejection, switch all channels including 14, run TX/RX stability tests, and check radio off/on recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_rf_rf2959.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_rf_uw2453.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_rf_uw2453.c

## Purpose
Implements Ubec UW2453/Maxim-new RF programming with documented synthesizer/VCO configuration, PLL lock probing, autocal fallback, per-channel tuning, and per-channel TX gain derived from EEPROM integration values.

## Important APIs, Types, And Functions
Exports `zd_rf_init_uw2453()`. Key helpers include `uw2453_synth_set_channel()`, `uw2453_write_vco_cfg()`, `uw2453_init_mode()`, `uw2453_set_tx_gain_level()`, `uw2453_init_hw()`, `uw2453_set_channel()`, `uw2453_switch_radio_on()`, `uw2453_switch_radio_off()`, and `uw2453_clear()`. Tables encode standard/autocal synth values, divide ratios, VCO configs, and TX gain values. `struct uw2453_priv` stores the selected VCO configuration index, with `-1` meaning autocal.

## Control Flow
Initialization writes BBP defaults, initial RF mode/filter/gain words, enters calibration modes, then iterates standard VCO configurations on channel 1. It clears and reads `UW2453_INTR_REG` to detect PLL lock, stores the next configuration after the one that locked, or falls back to autocal. Channel changes program synth/divide values, choose VCO config or autocal, enter RX/TX mode, write common CR values, update TX gain from EEPROM integration table, and set CR203. Radio on enters RX/TX mode and chooses CR251 value by chip generation; radio off enters idle and powers PLL down.

## State And Persistence
Allocates `rf->priv` as `struct uw2453_priv` and frees it through `uw2453_clear()`. Disables common chip channel-integration updates because it manages TX gain itself. Hardware state includes selected VCO, synth, TX gain, and RF mode registers.

## Dependencies And Integration Points
Uses locked chip IO, RF serial writes, EEPROM `pwr_int_values`, and `UW2453_INTR_REG` from the chip header. Selected for `MAXIM_NEW_RF` and `UW2453_RF`.

## Risks
PLL lock probing and use of the next VCO table entry are subtle vendor-compatible behavior. If no lock is detected, autocal behavior differs from standard tables. Out-of-range EEPROM integration values silently skip TX gain programming. Private allocation failure prevents RF init.

## Test Signals
Probe UW2453/MAXIM_NEW devices, confirm PLL lock or autocal debug path, switch all channels, validate TX gain from EEPROM values including high indices, run reset/disconnect to verify `uw2453_clear()`, and test radio off/on.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_rf_uw2453.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_usb.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_usb.c

## Purpose
Implements the USB bus driver and transport for ZD1211RW. It matches USB IDs, ejects virtual installer devices, uploads firmware, initializes hardware, manages interrupt/RX/TX URBs, implements register and RF vendor commands, detects TX/RX stalls, handles USB reset/resume, and registers/unregisters mac80211 hardware.

## Important APIs, Types, And Functions
Exports `zd_usb_init()`, `zd_usb_clear()`, `zd_usb_init_hw()`, `zd_usb_read_fw()`, `zd_usb_enable_int()`, `zd_usb_disable_int()`, `zd_usb_enable_rx()`, `zd_usb_disable_rx()`, `zd_usb_enable_tx()`, `zd_usb_disable_tx()`, `zd_usb_tx()`, `zd_tx_watchdog_enable()`, `zd_tx_watchdog_disable()`, `zd_usb_reset_rx_idle_timer()`, `zd_usb_scnprint_id()`, `zd_usb_ioread16v()`, `zd_usb_iowrite16v_async_start/end()`, `zd_usb_iowrite16v_async()`, `zd_usb_iowrite16v()`, and `zd_usb_rfwrite()`. Driver callbacks include `probe`, `disconnect`, `pre_reset`, `post_reset`, module init/exit, and URB completions `int_urb_complete`, `rx_urb_complete`, and `tx_urb_complete`.

## Control Flow
Probe resets the USB device, allocates `ieee80211_hw`, sets ZD1211B flag from ID table, reads the permanent MAC over the pre-firmware interface, and registers mac80211. First `zd_op_start()` calls `zd_usb_init_hw()`, which uploads boot/helper firmware, resets USB configuration, and invokes MAC/chip init. Interrupt URB completion handles register-read replies, hardware interrupt status, and retry-fail TX status, then resubmits. RX enables five bulk URBs, handles split/merged USB frames, passes complete packets to `zd_mac_rx()`, and resets RX if idle for 30 seconds. TX creates one bulk URB per skb, anchors it, tracks queue pressure, reports completion to MAC, and uses a watchdog to queue device reset after a 5-second stuck skb. Register reads send a request on EP_REGS_OUT and wait for a matching interrupt reply with retry handling; writes batch asynchronous URBs through an anchor.

## State And Persistence
`struct zd_usb` owns the USB interface reference, command anchors, async write state, request buffer, interrupt URB/buffer/completion, RX URB array and fragment buffer, TX submitted skb queue/anchor/count, and flags `is_zd1211b`, `initialized`, `was_running`, and `in_async`. Firmware remains in device memory until reset. `pre_reset` records whether the device was running, stops transport, and holds `chip->mutex`; `post_reset` unlocks and resumes if needed.

## Dependencies And Integration Points
Depends on Linux USB core, firmware loader, workqueues/tasklets, mac80211, skb queues, and local MAC/chip definitions. Integrates firmware files `zd1211/zd1211_{ur,ub,uphr}` and `zd1211/zd1211b_{ur,ub,uphr}`, mac80211 registration, and USB device reset callbacks.

## Risks
URB lifetime, anchors, coherent buffers, and skb ownership are delicate. Register reads depend on interrupt endpoint availability and can be overridden by retry-fail or CR_INTERRUPT events; stale replies are filtered by address matching. `zd_usb_iowrite16v_async_end()` timeout semantics depend on anchor state and `cmd_error`. RX fragment detection uses packet-size modulus heuristics. Reset paths lock `chip->mutex` across USB reset callbacks, so lock ordering must stay consistent. Firmware version mismatch handling is intentionally less invasive than the vendor driver.

## Test Signals
Probe all listed ZD1211/ZD1211B IDs, installer eject IDs, full/high-speed devices, missing firmware, firmware version mismatch, repeated register read/write batches, RF writes with min/max bit counts, RX merged and split frames, TX queue stop/wake thresholds, TX watchdog reset, RX idle reset, disconnect during traffic, and USB pre/post reset resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_usb.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_usb.h

## Purpose
Defines the ZD1211RW USB transport contract: endpoint numbers, vendor request formats, interrupt packet formats, RX/TX transport state, command batching state, timing thresholds, and exported USB APIs.

## Important APIs, Types, And Functions
Defines device types, endpoints, transfer limits, RF write bit limits, control request IDs, packed request structs (`usb_req_read_regs`, `usb_req_write_regs`, `usb_req_rfwrite`), interrupt structs (`usb_int_header`, `usb_int_regs`, `usb_int_retry_fail`), `read_regs_int`, `zd_ioreq16`, `zd_ioreq32`, `zd_usb_interrupt`, `zd_usb_rx`, `zd_usb_tx`, and `zd_usb`. Inline helpers map USB structures to `usb_device` and `ieee80211_hw`.

## Control Flow
No independent flow, but the declarations enforce that chip code uses 16-bit read/write batches, RF code uses `zd_usb_rfwrite()`, and MAC code uses RX/TX enable/disable and `zd_usb_tx()`. Interrupt replies complete register reads asynchronously.

## State And Persistence
`zd_usb_interrupt` persists interrupt URB state and pending register-read metadata. `zd_usb_rx` persists RX URBs, fragment buffer, idle work, and reset tasklet. `zd_usb_tx` persists enabled/stopped flags, submitted skb queue, URB anchor, submitted count, and watchdog work. `zd_usb` holds global async command batching state and transport flags.

## Dependencies And Integration Points
Includes Linux completion, netdevice, spinlock, skb, USB, and `zd_def.h`. Used by chip, MAC, RF, and USB implementation files.

## Risks
The fixed `req_buf[64]` is sized to current request maxima; changing maxima requires rechecking build assertions. Packed USB protocol structs must not change layout. Tasklet initialization in the C file relies on fields declared here. TX high/low watermarks directly affect mac80211 queue flow control.

## Test Signals
Compile with `BUILD_BUG_ON` request-size checks, run register batches at maximum counts, RF writes at bit-count limits, RX fragment handling, TX queue throttling, and interrupt enable/disable races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_usb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wwan/Kconfig

## Purpose
Defines Kconfig options for the Linux WWAN core and WWAN device drivers in this tree, including core WWAN support, optional debugfs support, simulation, MHI control/MBIM, Qualcomm BAM-DMUX, RPMSG control, Intel IOSM, and MediaTek T7xx.

## Important APIs, Types, And Functions
Key symbols are `WWAN`, `WWAN_DEBUGFS`, `WWAN_HWSIM`, `MHI_WWAN_CTRL`, `MHI_WWAN_MBIM`, `QCOM_BAM_DMUX`, `RPMSG_WWAN_CTRL`, `IOSM`, and `MTK_T7XX`. `IOSM` depends on `PCI` and selects `NET_DEVLINK` plus `RELAY` when debugfs is enabled. `WWAN` depends on `GNSS || GNSS = n`.

## Control Flow
Kconfig controls which objects in the WWAN Makefiles are built. The `if WWAN` block gates all subordinate driver options on the WWAN core.

## State And Persistence
No runtime state. Configuration choices persist in the kernel build config and determine module availability and selected dependencies.

## Dependencies And Integration Points
Integrates with Linux Kconfig, PCI, MHI bus, RPMSG, DMA/PM/Qualcomm SMEM state, DEBUG_FS, RELAY, NET_DEVLINK, and GNSS symbols.

## Risks
Incorrect dependency/select relationships can create build failures or silently omit required support. `WWAN_DEBUGFS` defaults to yes when available, which affects IOSM/MTK debug trace object inclusion through Makefiles.

## Test Signals
Run allmodconfig/allnoconfig and targeted configs for each WWAN driver. Verify IOSM builds as built-in and module with/without `WWAN_DEBUGFS`, and that selected `NET_DEVLINK` is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wwan/Makefile

## Purpose
Maps WWAN Kconfig symbols to object files and subdirectories for the top-level WWAN driver directory.

## Important APIs, Types, And Functions
Build rules include `obj-$(CONFIG_WWAN) += wwan.o`, `wwan-objs += wwan_core.o`, and conditional objects for `wwan_hwsim.o`, `mhi_wwan_ctrl.o`, `mhi_wwan_mbim.o`, `qcom_bam_dmux.o`, `rpmsg_wwan_ctrl.o`, `iosm/`, and `t7xx/`.

## Control Flow
Kbuild includes objects according to the resolved configuration. When `CONFIG_IOSM` is enabled, Kbuild descends into `drivers/net/wwan/iosm/`.

## State And Persistence
No runtime state. Build outputs and module composition are determined by these rules.

## Dependencies And Integration Points
Integrates with the Kconfig symbols in the same directory and each driver's source subtree.

## Risks
Object names must match source files and module expectations. Missing subdirectory rules would make enabled Kconfig options produce no driver.

## Test Signals
Run `make M=drivers/net/wwan` or equivalent targeted kernel builds under configs enabling each symbol singly and together.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/Makefile

## Purpose
Defines the object composition of the Intel IOSM WWAN driver module.

## Important APIs, Types, And Functions
`iosm-y` includes task queue, IMEM, MMIO, port, WWAN, uevent, PM, PCIe, IRQ, channel config, protocol, mux, devlink, flash, and coredump objects. `iosm-$(CONFIG_WWAN_DEBUGFS)` adds `iosm_ipc_debugfs.o` and `iosm_ipc_trace.o`. `obj-$(CONFIG_IOSM) := iosm.o` builds the aggregate module/object.

## Control Flow
Kbuild links the listed objects into `iosm.o` when `CONFIG_IOSM` is enabled. Debugfs-specific objects are included only when `CONFIG_WWAN_DEBUGFS` is set.

## State And Persistence
No runtime state. It determines which IOSM features are compiled into the module.

## Dependencies And Integration Points
Integrates with IOSM C files and WWAN debugfs Kconfig. The files in this work item are part of the listed core and debugfs object sets.

## Risks
Ordering is not usually semantic for linking, but missing objects break symbols such as devlink, flash, coredump, or trace hooks. Debugfs stub headers must match Makefile conditional inclusion.

## Test Signals
Build IOSM with `CONFIG_IOSM=y/m` and `CONFIG_WWAN_DEBUGFS=y/n`. Check that devlink flash/coredump symbols resolve and trace/debugfs objects are included only in debugfs builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_chnl_cfg.c -->
# sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_chnl_cfg.c

## Purpose
Provides the IOSM modem IPC channel configuration table and a helper to copy a channel's pipe, descriptor, buffer, WWAN port, and IRQ accumulation settings to callers.

## Important APIs, Types, And Functions
Exports `ipc_chnl_cfg_get()`. The static `modem_cfg[]` table describes IP mux, RPC, AT, trace, loopback, MBIM, and flash/coredump channels. Local constants define maximum downlink buffer sizes, transfer descriptor counts, and accumulation backoff values.

## Control Flow
Callers pass a channel index. `ipc_chnl_cfg_get()` bounds-checks it, assigns mux-specific accumulation backoff for `IPC_MEM_MUX_IP_CH_IF_ID`, otherwise disables backoff, then copies the corresponding `modem_cfg` fields to the output struct.

## State And Persistence
The channel table is static read-mostly configuration. No dynamic state is retained. Output state is persisted by callers such as IMEM channel initialization.

## Dependencies And Integration Points
Depends on WWAN port type constants and IOSM mux constants from `iosm_ipc_mux.h`. Used by IOSM setup paths, including devlink flash/coredump channel initialization.

## Risks
`index` is checked only for upper bound; negative values would index before the array if passed. Channel zero is noted as reserved for flash, but the first table entry is IP mux and flash/coredump appears at control channel ID 7, so callers must use the intended enum/index consistently. Buffer sizes and TD counts directly affect DMA ring sizing and memory use.

## Test Signals
Exercise every valid channel index, invalid high index, and ideally negative-index hardening. Verify WWAN port exposure for AT/RPC/MBIM and flash/coredump channel operation through devlink.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_chnl_cfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_chnl_cfg.h -->
# sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_chnl_cfg.h

## Purpose
Declares IOSM IPC channel IDs, trace channel sizing constants, `struct ipc_chnl_cfg`, and `ipc_chnl_cfg_get()`.

## Important APIs, Types, And Functions
Defines `IPC_MEM_TDS_TRC`, `IPC_MEM_MAX_DL_TRC_BUF_SIZE`, `enum ipc_channel_id` from IP channel 0 through control channel 7, and `struct ipc_chnl_cfg` fields for interface ID, uplink/downlink pipes, TD counts, downlink buffer size, WWAN port type, and accumulation backoff.

## Control Flow
No independent runtime flow. Callers allocate or stack-initialize `ipc_chnl_cfg` and call `ipc_chnl_cfg_get()` before creating IOSM IPC channels.

## State And Persistence
The struct carries copied configuration into channel initialization and persists according to caller storage.

## Dependencies And Integration Points
Includes `iosm_ipc_mux.h` for mux constants and is used by IOSM IMEM/devlink/channel setup code.

## Risks
Enum values are used as array indices in the C file, so reordering changes behavior. The comment says `index` is up to MAX_CHANNELS, but no max symbol is declared here.

## Test Signals
Build consumers after enum/table changes, and validate channel setup for mux, AT, trace, MBIM, loopback, and flash/coredump.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_chnl_cfg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_coredump.c -->
# sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_coredump.c

## Purpose
Implements IOSM modem coredump list retrieval and per-file coredump data collection for devlink regions.

## Important APIs, Types, And Functions
Exports `ipc_coredump_collect()` and `ipc_coredump_get_list()`. `ipc_coredump_collect()` allocates a vmalloc buffer, sends `rpsi_cmd_coredump_get`, and reads data in chunks up to `MAX_DATA_SIZE`. `ipc_coredump_get_list()` allocates a `MAX_CD_LIST_SIZE` table, sends start/end/list commands, reads the table, validates entry count and file sizes, updates `devlink->cd_file_info[]`, and emits devlink flash status notifications for filenames and sizes.

## Control Flow
Devlink snapshot invokes `ipc_coredump_collect()` with a region entry. Collection uses the actual file size from `cd_file_info`, but allocates the default region size passed by the caller. Start-list flow sends an RPSI command, reads exactly 4 KiB, validates the number of entries against `IOSM_NOF_CD_REGION`, and stores each modem-reported actual size if it does not exceed the default.

## State And Persistence
Coredump metadata persists in `iosm_devlink.cd_file_info`, specifically `actual_size` populated from modem list entries. Collected snapshot data is vmalloc-owned and later freed by the devlink region destructor.

## Dependencies And Integration Points
Depends on `iosm_ipc_devlink.h`, devlink status notifications, RPSI command constants, and IMEM devlink read/write helpers. Called from `iosm_ipc_devlink.c` snapshot and init flows.

## Risks
If `ipc_imem_sys_devlink_read()` returns zero bytes without error during collection, the loop would not make progress. `size` is declared `u8[MAX_SIZE_LEN]` but passed to `snprintf()` as a char buffer. The code requires an exact 4 KiB list read and rejects any short read. File-size validation prevents modem-reported sizes from exceeding default region sizes.

## Test Signals
Test coredump start/list/end, zero entries, too many entries, oversized file entries, short list reads, chunked data reads over 64 KiB, read errors mid-file, and devlink region snapshot cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_coredump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_coredump.h -->
# sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_coredump.h

## Purpose
Declares IOSM coredump table wire formats, size limits, and coredump collection APIs.

## Important APIs, Types, And Functions
Defines `MAX_CD_LIST_SIZE`, `MAX_DATA_SIZE`, `MAX_SIZE_LEN`, packed `struct iosm_cd_list_entry`, packed `struct iosm_cd_list`, packed `struct iosm_cd_table`, and prototypes for `ipc_coredump_collect()` and `ipc_coredump_get_list()`.

## Control Flow
No independent flow. Devlink code uses these declarations to retrieve coredump metadata and snapshot data from the modem.

## State And Persistence
Packed structs represent modem-provided coredump list data. Each list entry carries a little-endian size and filename.

## Dependencies And Integration Points
Includes `iosm_ipc_devlink.h` for `struct iosm_devlink`, filename length constants, coredump region count, and RPSI integration.

## Risks
The flexible `entry[]` table is parsed from a fixed-size buffer; callers must validate `num_entries`. Packed layout and endian conversion must match modem firmware.

## Test Signals
Build and run coredump list parsing on modem firmware variants, including boundary filename lengths and max region counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_coredump.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_debugfs.c

## Purpose
Initializes and tears down IOSM debugfs integration under the WWAN debugfs directory, including trace channel setup.

## Important APIs, Types, And Functions
Exports `ipc_debugfs_init()` and `ipc_debugfs_deinit()`. Init calls `wwan_get_debugfs_dir()`, creates a module-named debugfs directory, starts trace support with `ipc_trace_init()`, and warns on trace setup failure. Deinit calls `ipc_trace_deinit()`, removes the debugfs directory recursively, and releases the WWAN debugfs dir reference.

## Control Flow
Called by IOSM device setup/teardown when compiled with `CONFIG_WWAN_DEBUGFS`. Trace initialization happens after debugfs directory creation; teardown reverses trace and directory ownership.

## State And Persistence
Stores debugfs directory dentries and trace pointer in `struct iosm_imem`. Debugfs entries persist until device teardown or module unload.

## Dependencies And Integration Points
Depends on Linux debugfs, WWAN debugfs helpers, IOSM IMEM state, and IOSM trace support.

## Risks
The code does not check `debugfs_create_dir()` failure before trace init. Deinit assumes init either populated or safely left nullable fields acceptable to trace/debugfs cleanup helpers.

## Test Signals
Build/run with `CONFIG_WWAN_DEBUGFS`, inspect `debugfs/wwan/wwanX/<module>`, verify trace channel creation, then unplug/unload and confirm recursive removal and WWAN debugfs ref release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_debugfs.h

## Purpose
Declares IOSM debugfs init/deinit hooks and provides no-op stubs when WWAN debugfs support is disabled.

## Important APIs, Types, And Functions
Exports `ipc_debugfs_init(struct iosm_imem *)` and `ipc_debugfs_deinit(struct iosm_imem *)` under `CONFIG_WWAN_DEBUGFS`; otherwise defines static inline empty stubs.

## Control Flow
Compile-time selection lets IOSM core call debugfs hooks unconditionally without linking debugfs objects in non-debugfs builds.

## State And Persistence
No state in the header. Enabled implementation stores state in `struct iosm_imem`.

## Dependencies And Integration Points
Relies on a forward-visible `struct iosm_imem` from including C files. Coupled with `iosm/Makefile`, which only adds debugfs/trace objects under `CONFIG_WWAN_DEBUGFS`.

## Risks
Stub signatures must stay identical to enabled declarations. Any caller requiring trace side effects must be guarded by the same config or tolerate no-ops.

## Test Signals
Build IOSM with `CONFIG_WWAN_DEBUGFS=y` and `n`, ensuring no unresolved symbols and no unused-function issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_devlink.c -->
# sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_devlink.c

## Purpose
Implements IOSM devlink integration for modem flashing, runtime devlink parameters, and modem coredump regions. It creates devlink regions for coredump files, sends RPSI commands over the IOSM devlink system channel, and wires devlink flash update to IOSM PSI/EBL/FLS flash helpers.

## Important APIs, Types, And Functions
Exports `ipc_devlink_send_cmd()`, `ipc_devlink_init()`, and `ipc_devlink_deinit()`. Internal functions include devlink param get/set for `erase_full_flash`, `ipc_devlink_get_flash_comp_type()`, `ipc_devlink_flash_update()`, `ipc_devlink_coredump_snapshot()`, `ipc_devlink_create_region()`, and `ipc_devlink_destroy_region()`. Static coredump metadata lists `report.json`, `coredump.fcd`, `cdd.log`, `eeprom.bin`, `bootcore_trace.bin`, and `bootcore_prev_trace.bin`.

## Control Flow
Initialization allocates a devlink instance, stores PCIe/device pointers, registers params, creates all coredump regions, obtains flash/coredump channel configuration for `IPC_MEM_CTRL_CHL_ID_7`, initializes that IPC channel, initializes read completion and RX list, and registers devlink. Flash update validates the IOSM image header and magic, allocates a modem response buffer, selects component type by image type string (`PSI`, `EBL`, or `FLS`), then calls the matching flash sequence and reports devlink status. Region snapshot calls `ipc_coredump_collect()`, and the final region sends coredump end; failures also end coredump collection. Deinit unregisters devlink, destroys regions, unregisters params, completes pending waits when needed, purges RX list if safe, closes the devlink system channel, and frees devlink.

## State And Persistence
`struct iosm_devlink` stores devlink context, PCIe/device pointers, runtime param `erase_full_flash`, coredump region ops/handles, shared coredump file info, and devlink SIO queue/completions. The static coredump `list[]` is shared metadata and receives per-entry `entry` numbers during region creation. Devlink regions persist until deinit.

## Dependencies And Integration Points
Depends on Linux devlink, vmalloc destructors for region snapshots, IOSM channel config, coredump helpers, flash helpers, IMEM sys devlink read/write/open/close, and PCIe/IMEM state. Kconfig selects `NET_DEVLINK` for IOSM.

## Risks
Static `list[]` is mutated with entry numbers and shared among devices, which can be problematic for multiple IOSM devices if per-device state differs. Error unwinding before channel init does not need to close the channel, but post-registration deinit must handle pending readers carefully. Flash component matching uses `strncmp()` over fixed length, so image type padding matters. `ipc_devlink_send_cmd()` CRC is a simple XOR over little-endian command words and must match modem firmware.

## Test Signals
Test devlink registration/unregistration, param get/set for `erase_full_flash`, flash updates for PSI/EBL/FLS/invalid images, invalid magic and short firmware, coredump region creation failure unwinding, snapshots for all six regions, pending read deinit, and multi-device behavior if supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_devlink.c -->
