# Research: subset-b-004873

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8180/rtl8225se.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8180/rtl8225se.c

## Purpose
This file implements RTL8225-SE radio tuning for the RTL8187SE/RTL8180-family PCI driver. It is a table-driven RF/baseband initializer plus the `rtl818x_rf_ops` implementation used by the main RTL8180 driver to detect, initialize, stop, and retune the radio.

## Important APIs, Types, And Functions
The exported entry point is `rtl8187se_detect_rf()`, which returns the static `rtl8225se_ops` object. That ops table provides `rtl8225se_rf_init()`, `rtl8225se_rf_stop()`, and `rtl8225se_rf_set_channel()`.

Low-level register access is handled by `rtl8187se_three_wire_io()`, `rtl8187se_rf_readreg()`, and `rtl8187se_rf_writereg()`, which program the RTL8187SE three-wire software interface through `SW_3W_*` registers and selected `rtl818x_csr` fields. Baseband writes go through inline helpers from `rtl8225se.h`, ultimately calling `rtl8180_write_phy()`.

The main static tuning helpers are `rtl8225se_write_zebra_agc()`, `rtl8187se_write_ofdm_config()`, `rtl8187se_write_rf_gain()`, `rtl8187se_write_initial_gain()`, and `rtl8225sez2_rf_set_tx_power()`. Hardware constants are held in RF gain, CCK/OFDM gain, channel, AGC, and OFDM configuration tables.

## Control Flow
Initialization first selects RF page 1 and reads registers 8 and 9 to infer whether the radio is D-cut. It then writes a long sequence of RF page 0/page 1 values, loads gain tables, performs sleeps required by the hardware, applies optional crystal calibration from `priv->xtal_cal`, writes power-save and baseband CCK/OFDM values, loads the Zebra AGC table, enables RF twice, enables the baseband, and ends by setting initial gain level 4.

Channel changes convert `conf->chandef.chan->center_freq` to an IEEE channel number, apply EEPROM-derived CCK/OFDM TX power from `priv->channels[channel - 1].hw_value`, write the PLL channel register, verify part of that register, retry if needed, and delay for settling.

Stop disables OFDM RXIQ matrix values, writes RF registers 4 and 0 to zero, waits, then powers down analog blocks via `rtl8180_set_anaparam()` and `rtl8180_set_anaparam2()`.

## State And Persistence
Persistent state is mostly external in `struct rtl8180_priv`: channel power values, crystal calibration values, and the memory-mapped register block. The file writes durable hardware state into RF registers, PHY registers, TX gain registers, antenna selection, and analog parameter registers, but does not maintain software state beyond stack temporaries.

## Dependencies And Integration Points
This file depends on `rtl8180.h` for `struct rtl8180_priv`, I/O helpers, analog-parameter helpers, and `rtl8180_write_phy()`. It depends on `rtl818x.h` register aliases such as `SW_3W_CMD1`, `SI_DATA_REG`, and `REG_ADDR*`. It is integrated into the larger RTL8180 PCI driver through `struct rtl818x_rf_ops`; the main device code calls the returned ops during start, stop, and channel configuration.

## Risks
The RF sequence is delay-sensitive and built from magic vendor values; reordering writes or reducing sleeps can leave the radio uncalibrated. `rtl8187se_three_wire_io()` casts byte buffers to integer pointers, so it assumes valid alignment and native endianness consistent with the existing driver environment. Channel indexes are based on 1-based 2.4 GHz channels and assume mac80211 will not request an unsupported channel. Failed three-wire busy waits are logged but not propagated, so later writes may proceed after hardware communication trouble.

## Test Signals
Useful signals are successful RF initialization messages showing D or non-D cut, association on all 2.4 GHz channels, TX power matching EEPROM-derived per-channel values, no three-wire busy warnings, stable receive sensitivity after AGC programming, and clean stop/start cycles without analog-power leakage. Channel-switch testing should verify the retry write on RF register 7 and absence of device stalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8180/rtl8225se.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8180/rtl8225se.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8180/rtl8225se.h

## Purpose
This header declares the RTL8225-SE radio interface used by the RTL8187SE path and defines analog power constants and PHY write helpers for CCK/OFDM baseband programming.

## Important APIs, Types, And Functions
The public declarations are `rtl8187se_detect_rf()`, `rtl8225se_rf_stop()`, `rtl8225se_rf_set_channel()`, `rtl8225se_rf_conf_erp()`, and `rtl8225se_rf_init()`. The file also defines `enum rtl8187se_power_state`, although the enum is not used by `rtl8225se.c` itself.

`rtl8225se_write_phy_ofdm()` and `rtl8225se_write_phy_cck()` are inline wrappers around `rtl8180_write_phy()`. The CCK helper ORs in `0x10000`, which is the local convention for selecting the CCK PHY address space.

## Control Flow
The header has no runtime control flow. It shapes how the C file writes baseband registers and exposes the RF ops provider to the parent driver.

## State And Persistence
The analog constants (`RTL8225SE_ANAPARAM_*`, `RTL8225SE_ANAPARAM2_*`, `RTL8225SE_ANAPARAM3`) are persisted only when the C file writes them into hardware through `rtl8180_set_anaparam*()`. There is no software state in the header.

## Dependencies And Integration Points
It depends on `struct ieee80211_hw`, `struct ieee80211_conf`, `struct ieee80211_bss_conf`, and `struct rtl818x_rf_ops` being visible through included driver headers. It is consumed by `rtl8225se.c` and by any RTL8180-side code that calls the declared RF functions.

## Risks
The declaration `rtl8225se_rf_conf_erp()` has no implementation in the paired source file, so callers must not require it unless implemented elsewhere. The analog constants encode board-power policy; incorrect reuse on a different chip revision could power down the wrong blocks.

## Test Signals
Compilation with `CONFIG_RTL8180`/RTL8187SE support is the main header signal. Runtime validation comes indirectly through successful RF init/stop/channel operations and correct CCK/OFDM writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8180/rtl8225se.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8180/sa2400.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8180/sa2400.c

## Purpose
This file provides Philips SA2400 RF support for RTL8180 devices. It programs SA2400 RF registers, maps RSSI values, configures antenna/baseband settings, and exports an `rtl818x_rf_ops` instance for the parent RTL8180 driver.

## Important APIs, Types, And Functions
The exported object is `const struct rtl818x_rf_ops sa2400_rf_ops`, with `.name = "Philips"`, `.init = sa2400_rf_init`, `.stop = sa2400_rf_stop`, `.set_chan = sa2400_rf_set_channel`, and `.calc_rssi = sa2400_rf_calc_rssi`.

`write_sa2400()` writes a 4-bit RF address and 24-bit data word through `RFPinsOutput`; unlike RTL8225-SE it explicitly notes that MAC bit-banging is used and the software three-wire interface is not. `sa2400_write_phy_antenna()` chooses the baseband antenna register value from `SA2400_ANTENNA`, `RF_PARAM_ANTBDEFAULT`, and channel 14 attenuation. `sa2400_rf_calc_rssi()` maps AGC/SQ data through `sa2400_rf_rssi_map`.

## Control Flow
Initialization derives analog power settings from `priv->rfparam & RF_PARAM_ANALOGPHY`. It enables analog power through `rtl8180_set_anaparam()`, writes the default channel and RF registers, performs VCO and filter calibration, optionally performs analog-PHY DC calibration through TX loopback, switches to RTX mode, and writes baseband configuration registers including antenna diversity and carrier-sense threshold.

Channel setup converts the current center frequency to a channel number, reads per-channel TX power from `priv->channels`, writes the power to SA2400 register 7, sets antenna bits, and writes the channel PLL and supporting registers. Stop simply writes zero to SA2400 register 4.

## State And Persistence
The file uses `struct rtl8180_priv` for EEPROM-derived channel power, analog parameter defaults, RF parameter flags, and carrier-sense threshold. Hardware state persists in SA2400 registers and RTL8180 PHY/CSR registers until changed by another RF operation or device reset.

## Dependencies And Integration Points
It depends on Linux PCI/delay/mac80211 headers, `rtl8180.h` for I/O and analog helpers, and `sa2400.h` for constants. The parent RTL8180 code selects `sa2400_rf_ops` when the hardware has this radio and then invokes the ops from device start/configuration/stop paths.

## Risks
This is highly timing-sensitive: `write_sa2400()` sleeps 3 ms after every register write, and comments rely on that delay to satisfy calibration timings. RSSI mapping ignores `agc` and uses SQ-specific lookup logic, so signal reporting quality depends on the historical table. The channel table is 2.4 GHz only and expects valid 1-14 channel input. Analog vs digital PHY branches configure power blocks differently; incorrect `rfparam` bits can break calibration.

## Test Signals
Signals include successful initialization on SA2400 boards, clean channel tuning on channels 1-14, valid antenna behavior for ANT B default and channel 14, RSSI values that move sensibly with attenuation, and no TX loopback residue after analog DC calibration. Stop/start cycles should leave RF register 4 and analog parameters in expected states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8180/sa2400.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8180/sa2400.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8180/sa2400.h

## Purpose
This header contains the SA2400-specific constants needed by `sa2400.c` and declares the RF ops object exported to the RTL8180 driver.

## Important APIs, Types, And Functions
The only symbol declaration is `extern const struct rtl818x_rf_ops sa2400_rf_ops`. Constants include antenna base value, analog/digital power bits for `ANAPARAM`, maximum sensitivity, and the FIR DAC shift used in SA2400 register 4.

## Control Flow
The header has no runtime control flow. It supplies compile-time constants that control analog power and RF calibration writes in the C file.

## State And Persistence
No software state is defined. The constants influence hardware state only when `sa2400_rf_init()` writes analog and RF registers.

## Dependencies And Integration Points
It requires `struct rtl818x_rf_ops` from the shared RTL818x definitions. It is included by the SA2400 implementation and indirectly supports RF detection/selection in the parent driver.

## Risks
The constants are specific to SA2400-on-RTL8180 boards. Reusing them for other RF front ends would misconfigure analog power, antenna selection, and sensitivity.

## Test Signals
Compile coverage and successful SA2400 RF initialization are the primary signals. Runtime checks should confirm that the selected ops name is `Philips` and that power/calibration behavior matches SA2400 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8180/sa2400.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8187/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8187/Makefile

## Purpose
This Makefile builds the RTL8187 USB mac80211 driver from its device, RF, LED, and rfkill implementation files.

## Important APIs, Types, And Functions
`rtl8187-objs := dev.o rtl8225.o leds.o rfkill.o` defines the composite module object list. `obj-$(CONFIG_RTL8187) += rtl8187.o` connects the module to Kconfig. `ccflags-y += -I $(src)/..` exposes the parent `rtl818x.h` include directory.

## Control Flow
Build flow is controlled by Kbuild: when `CONFIG_RTL8187` is enabled, Kbuild links the listed objects into `rtl8187.o`.

## State And Persistence
No runtime state is defined. Build state is the object composition and include path.

## Dependencies And Integration Points
The object list matches source-level dependencies: `dev.c` owns USB/mac80211 registration, `rtl8225.c` owns RF/register helpers, `leds.c` owns optional LED class integration, and `rfkill.c` owns wiphy rfkill polling. The include flag allows local includes of `../rtl818x.h`.

## Risks
Because `leds.o` is always listed but its contents are guarded by `CONFIG_RTL8187_LEDS`, Kconfig/build coverage must ensure empty-object behavior remains acceptable. Removing the parent include path would break `rtl8187.h`'s `rtl818x.h` include.

## Test Signals
Signals are successful module build with `CONFIG_RTL8187=y/m`, successful build with LED support enabled and disabled, and link availability of `rtl8187_driver` plus helper symbols from all four objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8187/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8187/dev.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8187/dev.c

## Purpose
This is the core RTL8187/RTL8187B USB wireless driver. It registers the USB device table and `ieee80211_ops`, reads EEPROM data, detects chip/RF revisions, initializes hardware, submits TX/RX/status URBs, handles mac80211 interface/configuration callbacks, and wires LED/rfkill support into device probe and disconnect.

## Important APIs, Types, And Functions
The exported module binding is `module_usb_driver(rtl8187_driver)`, with `rtl8187_probe()` and `rtl8187_disconnect()`. mac80211 integration is through the static `rtl8187_ops`, including `tx`, `start`, `stop`, `add_interface`, `remove_interface`, `config`, `bss_info_changed`, multicast/filter callbacks, `conf_tx`, `rfkill_poll`, and `get_tsf`.

Important data and control helpers include `rtl8187_tx()`/`rtl8187_tx_cb()`, `rtl8187_rx_cb()`, `rtl8187_init_urbs()`, `rtl8187b_init_status_urb()`/`rtl8187b_status_cb()`, `rtl8187_init_hw()`, `rtl8187b_init_hw()`, `rtl8187_start()`, `rtl8187_stop()`, `rtl8187_work()` for non-B retry reporting, `rtl8187_beacon_work()`, `rtl8187_conf_erp()`, EEPROM access callbacks, and `rtl8187_set_anaparam()`.

## Control Flow
Probe allocates `ieee80211_hw`, initializes private USB/control mutex state, copies 2.4 GHz channel/rate tables, sets wiphy/mac80211 capabilities, reads EEPROM width/MAC/TX power/base power, detects ASIC/chip revision, handles RTL8187B misidentified as RTL8187, selects the RTL8225 RF ops through `rtl8187_detect_rf()`, sets queue count and TX headroom, registers mac80211 hardware, then initializes LEDs and rfkill polling.

Start takes `conf_mutex`, runs the RTL8187 or RTL8187B hardware init sequence, initializes the USB anchor, sets RX/TX configuration registers, submits RX URBs, and for RTL8187B submits a status URB. RTL8187B uses four data queues and endpoint mapping; non-B uses one TX endpoint and a delayed work item to read cumulative retry count from register `0xFFFA`.

TX allocates a URB, builds a chip-specific TX descriptor in skb headroom, sets rate, no-encryption, fragmentation, RTS/CTS or CTS-to-self duration, optionally assigns software sequence numbers, selects endpoint, anchors and submits the bulk URB. Completion strips the descriptor and reports status immediately, queues RTL8187B frames until a status packet matches sequence bits, or queues non-B frames for delayed retry-count processing.

RX completion unlinks the skb from `rx_queue`, parses a trailing RTL8187 or RTL8187B RX descriptor, derives signal from AGC, fills `ieee80211_rx_status`, trims the skb to descriptor length, reports it to mac80211, then allocates and submits a replacement RX URB. Errors free the skb and do not refill unless allocation/submission succeeds.

BSS/config callbacks update MAC/BSSID/MSR registers, ERP timing, beacon work, RX filter bits, channel changes, TSF reads, and EDCA/CW settings. Stop disables interrupts/TX/RX, stops RF, powers analog blocks down, sets VCO off, kills anchored URBs, flushes queued TX-status skbs, and cancels delayed work for non-B chips.

## State And Persistence
`struct rtl8187_priv` holds persistent driver state: USB device, register map base, RF ops, active vif pointer, channel/rate/band tables, RX config, anchored URBs, delayed work, EEPROM-derived power values, ASIC/hardware revision, RX queue, signal/noise, slot time/AIFSN, rfkill mask/state, TX status queue, DMA-safe control buffer, and software sequence number. Per-vif beacon state lives in `struct rtl8187_vif`.

Hardware state is persisted in RTL818x CSR registers, RF registers, PHY tables, EEPROM-loaded defaults, analog power registers, USB endpoint URBs, and LED/rfkill state. Most hardware state is rebuilt on every `start()` after reset.

## Dependencies And Integration Points
The file depends on Linux USB core, mac80211/cfg80211, `eeprom_93cx6`, `etherdevice`, `rtl8187.h`, `rtl8225.h`, optional `leds.h`, and `rfkill.h`. It integrates with `rtl8225.c` for low-level register I/O and RF tuning, with `leds.c` for LED classdev registration, and with `rfkill.c` through the mac80211 rfkill poll callback.

## Risks
URB lifetime and skb ownership are central risks: TX completion, RTL8187B status matching, RX refill, and stop-time `usb_kill_anchored_urbs()` must not double-free or leak skbs. RTL8187B status matching compares truncated sequence-control bits and can misattribute ACK status under wrap or fragmentation. Non-B retry reporting uses a static cumulative retry variable and averages over queued packets, so rate control receives approximate status. Register sequences contain raw offsets and magic delays; incorrect ordering can hang the device. The driver supports only one active station/adhoc vif, and beaconing is software scheduled rather than hardware timed.

## Test Signals
Signals include successful probe for all USB IDs, correct MAC/TX power/RF revision logging, start/stop without URB leaks, RX delivery with sane dBm signal values, TX ACK/retry status on RTL8187 and RTL8187B, station and adhoc operation, channel changes without device stalls, software beaconing in IBSS, rfkill polling, LED triggers, suspend/disconnect cleanup, and lockdep/KASAN/USB debugging around anchored URBs and queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8187/dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8187/leds.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8187/leds.c

## Purpose
This file implements optional LED class support for RTL8187 devices when `CONFIG_RTL8187_LEDS` is enabled. It maps EEPROM customer IDs to LED pins and registers radio, TX, and RX LED class devices using mac80211 LED trigger names.

## Important APIs, Types, And Functions
The public functions are `rtl8187_leds_init()` and `rtl8187_leds_exit()`. Internal helpers include `rtl8187_register_led()`, `rtl8187_unregister_led()`, `rtl8187_led_brightness_set()`, `led_turn_on()`, and `led_turn_off()`.

The code controls GPIO0 or PGSELECT LED bits depending on `ledpin` (`LED_PIN_GPIO0`, `LED_PIN_LED0`, `LED_PIN_LED1`, or hardware-controlled `LED_PIN_HW`). `struct rtl8187_led` stores the LED classdev, parent hardware pointer, pin mode, name, and radio-vs-activity flag.

## Control Flow
Initialization reads the customer ID passed from EEPROM handling in `dev.c`, selects a pin policy, initializes delayed work items in `rtl8187_priv`, and registers radio, TX, and RX LEDs. If later registrations fail, it unregisters earlier LEDs.

Brightness callbacks do not touch hardware directly. For the radio LED they queue on/off work and track a static `radio_on` flag. For TX/RX activity they blink by queuing off work immediately and on work after `HZ / 20`, but only while the radio LED is considered on. The delayed work functions lock `conf_mutex`, check that a vif exists and the LED is registered, then write GPIO/PGSELECT state.

Exit unregisters all LED class devices, flushes/cancels delayed work, and clears device pointers.

## State And Persistence
LED state is held in `rtl8187_priv` under `CONFIG_RTL8187_LEDS`: three `rtl8187_led` objects and `led_on`/`led_off` work. A file-static `radio_on` boolean gates TX/RX blinking. Hardware state persists in GPIO0, GP_ENABLE, and PGSELECT bits until changed or the device is stopped/reset.

## Dependencies And Integration Points
This file depends on mac80211 LED trigger naming, the Linux LED class, USB device ownership for classdev registration, EEPROM customer IDs from `dev.c`, and RTL8187 register I/O helpers. It shares `conf_mutex` with device configuration because LED writes touch the same hardware register space.

## Risks
The static `radio_on` flag is global across devices, which can be wrong if multiple RTL8187 adapters are present. Both on/off workers always use `priv->led_tx` as the selected LED object, so radio/RX class state mainly drives the same pin behavior rather than independent LEDs. Work cancellation and unregister ordering must prevent callbacks from using a cleared `led->dev`. Hardware LED mode (`LED_PIN_HW`) intentionally does nothing in software.

## Test Signals
Build with and without `CONFIG_RTL8187_LEDS`, probe devices with different EEPROM customer IDs, verify radio/TX/RX LED class entries and triggers, test TX/RX blink while associated, unload/disconnect under active LED work, and test multiple adapters for cross-device `radio_on` interference.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8187/leds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8187/leds.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8187/leds.h

## Purpose
This header declares optional RTL8187 LED support and defines the LED pin/customer-ID contract shared by `dev.c`, `leds.c`, and `rtl8187_priv`.

## Important APIs, Types, And Functions
Under `CONFIG_RTL8187_LEDS`, it defines `RTL8187_LED_MAX_NAME_LEN`, LED pin enums, EEPROM customer ID enums, `struct rtl8187_led`, and declarations for `rtl8187_leds_init()` and `rtl8187_leds_exit()`.

## Control Flow
There is no runtime control flow. Conditional compilation removes all declarations when LED support is disabled, while `rtl8187.h` also wraps LED fields in the same config guard.

## State And Persistence
`struct rtl8187_led` stores LED registration state: parent `ieee80211_hw`, `led_classdev`, selected pin, device name, and radio flag. Persistent hardware effects occur only in `leds.c`.

## Dependencies And Integration Points
The header depends on Linux LED and type declarations and is included by `rtl8187.h` and `leds.c`. Customer ID values correspond to EEPROM values read in `rtl8187_probe()`.

## Risks
Because declarations are hidden when `CONFIG_RTL8187_LEDS` is off, call sites must be guarded consistently. The max LED name length is small, so names depend on bounded `snprintf()` truncation behavior.

## Test Signals
Compile both LED-enabled and LED-disabled configurations. Runtime validation is covered by LED class registration and trigger behavior in `leds.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8187/leds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8187/rfkill.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8187/rfkill.c

## Purpose
This file implements hardware radio-switch polling for RTL8187 devices and reports state to cfg80211/wiphy rfkill.

## Important APIs, Types, And Functions
The public functions are `rtl8187_rfkill_init()`, `rtl8187_rfkill_poll()`, and `rtl8187_rfkill_exit()`. `rtl8187_is_radio_enabled()` reads GPIO state using `priv->rfkill_mask` and is the low-level switch sampler.

## Control Flow
Initialization samples GPIO, logs whether the switch is on or off, sets the wiphy hardware rfkill state to the inverse of enabled, and starts wiphy rfkill polling. mac80211 calls `rtl8187_rfkill_poll()` through `rtl8187_ops.rfkill_poll`; the poll locks `conf_mutex`, resamples the switch, logs transitions, and updates wiphy rfkill state. Exit stops polling.

## State And Persistence
`priv->rfkill_mask` is selected during probe from product ID and EEPROM GPIO selection. `priv->rfkill_off` stores the last sampled enabled state. Hardware state lives in GPIO0/GPIO1 bits.

## Dependencies And Integration Points
It depends on `rtl8187.h` for private state and register I/O, and on mac80211/cfg80211 wiphy rfkill APIs. `dev.c` initializes the mask, calls init/exit, and exposes the poll callback in `ieee80211_ops`.

## Risks
The field name `rfkill_off` stores enabled/on state, which is easy to misread. Sampling writes GPIO0 with the mask cleared before reading GPIO1, so GPIO side effects must match the hardware design. Wrong mask selection for 8197/8198 variants will invert or miss the hardware switch. Polling is serialized with `conf_mutex`, but long register I/O delays could still interact with stop/disconnect timing.

## Test Signals
Test physical switch transitions on RTL8187/8189/8197/8198-style devices, verify `rfkill list` state, check logs for on/off transitions, confirm blocked devices stop association/TX via mac80211, and ensure polling stops before disconnect frees the hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8187/rfkill.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8187/rfkill.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8187/rfkill.h

## Purpose
This header declares the RTL8187 rfkill integration functions used by `dev.c`.

## Important APIs, Types, And Functions
It declares `rtl8187_rfkill_init()`, `rtl8187_rfkill_poll()`, and `rtl8187_rfkill_exit()`.

## Control Flow
No runtime control flow is present. The declarations support probe, mac80211 polling, and disconnect paths.

## State And Persistence
No state is defined here. State lives in `struct rtl8187_priv` and wiphy rfkill core state.

## Dependencies And Integration Points
The declarations take `struct ieee80211_hw *`, matching mac80211 hardware objects. `dev.c` includes this header to wire rfkill into `ieee80211_ops` and probe/disconnect.

## Risks
The header is intentionally small; the main risk is missing include coverage for `struct ieee80211_hw` if include order changes.

## Test Signals
Compile-time use by `dev.c` and runtime rfkill polling covered by `rfkill.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8187/rfkill.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8187/rtl8187.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8187/rtl8187.h

## Purpose
This header defines the RTL8187 USB driver's private data structures, EEPROM/register request constants, RX/TX descriptor layouts, device revision enums, and register I/O function declarations.

## Important APIs, Types, And Functions
Important structures are `struct rtl8187_priv`, `struct rtl8187_vif`, `struct rtl8187_rx_info`, `struct rtl8187_rx_hdr`, `struct rtl8187b_rx_hdr`, `struct rtl8187_tx_hdr`, and `struct rtl8187b_tx_hdr`. It declares `rtl8187_write_phy()` and indexed USB register accessors `rtl818x_ioread{8,16,32}_idx()` and `rtl818x_iowrite{8,16,32}_idx()`, plus inline index-zero wrappers.

Constants define EEPROM offsets for MAC and TX power, USB vendor request IDs, max RX size, rfkill masks, and retry count. The device enum distinguishes RTL8187 from RTL8187B, and `hw_rev` distinguishes RTL8187B cut variants.

## Control Flow
The header itself has no runtime flow, but its inline I/O wrappers define the normal path used by `dev.c`, `rtl8225.c`, `leds.c`, and `rfkill.c` for register access.

## State And Persistence
`struct rtl8187_priv` is the central persistent driver state: common RTL818x register map/RF ops/vif pointer, configuration and I/O mutexes, USB device, channel/rate/band tables, RX configuration, URB anchor, delayed work, EEPROM power and revision fields, RX queue, signal/noise, EDCA fields, rfkill state, TX status queue, DMA-safe control buffer, and sequence counter. Optional LED state is embedded under `CONFIG_RTL8187_LEDS`.

## Dependencies And Integration Points
It includes `rtl818x.h` for the CSR map and RF ops and `leds.h` for optional LED fields. The header is the shared contract for all RTL8187 objects and also maps mac80211 private vif storage through `struct rtl8187_vif`.

## Risks
Descriptor structs are packed and must match hardware byte layout. `io_dmabuf` is cacheline-aligned and shared by synchronous USB control operations, so all access must remain protected by `io_mutex`. The `vif` pointer expresses a single-interface design; adding concurrent interfaces would require larger state changes. The `rfkill_off` name is semantically confusing because it stores radio-enabled state.

## Test Signals
Compile-time structure-size assumptions are partly exercised by descriptor use and `dev->extra_tx_headroom`. Runtime signals include correct descriptor parsing, no unaligned descriptor faults, clean synchronized USB register I/O, and valid single-vif operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8187/rtl8187.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8187/rtl8225.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8187/rtl8225.c

## Purpose
This file provides RTL8225/RTL8225z2 RF support and USB register I/O for the RTL8187 USB driver. It contains the synchronous USB control read/write primitives used by the driver and the RF/baseband initialization, calibration, TX power, stop, channel, and RF detection logic.

## Important APIs, Types, And Functions
The exported driver I/O functions are `rtl818x_ioread8_idx()`, `rtl818x_ioread16_idx()`, `rtl818x_ioread32_idx()`, and matching `rtl818x_iowrite*_idx()` functions. The exported RF selector is `rtl8187_detect_rf()`.

RF access helpers include `rtl8225_write_bitbang()`, `rtl8225_write_8051()`, `rtl8225_write()`, and `rtl8225_read()`. RF ops implementations are `rtl8225_rf_init()`, `rtl8225z2_rf_init()`, `rtl8225z2_b_rf_init()`, `rtl8225_rf_stop()`, and `rtl8225_rf_set_channel()`. TX power is handled by chip-family helpers `rtl8225_rf_set_tx_power()`, `rtl8225z2_rf_set_tx_power()`, and `rtl8225z2_b_rf_set_tx_power()`.

## Control Flow
The USB register accessors serialize through `priv->io_mutex`, use `priv->io_dmabuf`, and issue vendor control requests on endpoint zero. RF writes use either 8051 USB requests or GPIO-style bit-banging based on `priv->asic_rev`; reads always bit-bang RF pins and restore pin state afterward.

RF detection writes page selectors, reads RF registers 8 and 9 on non-B chips, and chooses `rtl8225` or `rtl8225z2`; RTL8187B always uses the z2-B ops. Hardware initialization writes RF register tables, performs calibration by toggling RF register 2 and checking register 6 bit 7, loads RX gain and AGC tables, initializes OFDM/CCK PHY registers, sets antenna defaults, sets TX power for channel 1, and writes sensitivity defaults. The RTL8187B z2-B variant uses different AGC/OFDM tables and PHY offsets.

Channel changes select the correct TX power routine based on the selected init function, write RF register 7 from the 14-entry channel PLL table, and delay for settling. Stop writes RF register 4 to `0x1f`.

## State And Persistence
Software state is external in `rtl8187_priv`: `asic_rev`, `is_rtl8187b`, `hw_rev`, `txpwr_base`, EEPROM channel values, `io_mutex`, and `io_dmabuf`. Hardware state is extensive: RF registers, RF pin GPIO state, PHY CCK/OFDM tables, AGC tables, TX gain registers, antenna selection, and analog parameter 2.

## Dependencies And Integration Points
The file depends on USB control messaging, mac80211 wiphy logging, `rtl8187.h` private state, and `rtl8225.h` analog constants and PHY helpers. `dev.c` calls the exported register accessors throughout probe/start/configuration and uses `rtl8187_detect_rf()` during probe to populate `priv->rf`.

## Risks
Register access ignores USB control transfer return values, so transient USB failures may silently produce stale reads or lost writes. RF bit-banging and 8051 write paths are timing- and pin-state-sensitive. TX power calculations rely on EEPROM values and chip revision-specific offsets; wrong cut detection can over/under-drive power. RF calibration failure only warns and continues. The code compares function pointers in `rtl8225_rf_set_channel()` to select the power routine, so refactoring ops initialization could break behavior.

## Test Signals
Signals include correct RF name detection (`rtl8225` vs `rtl8225z2`), no RF calibration warnings, successful operation on RTL8187 and RTL8187B cut B/D/E, valid TX power across channels including channel 14 CCK tables, stable RX sensitivity after AGC load, and USB error-injection tests around control transfers. Channel change and repeated start/stop testing should watch for pin-state or calibration regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8187/rtl8225.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8187/rtl8225.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8187/rtl8225.h

## Purpose
This header defines RTL8225 analog power constants for RTL8187/RTL8187B, declares RF detection, and provides inline OFDM/CCK PHY write helpers for `rtl8225.c`.

## Important APIs, Types, And Functions
The public declaration is `rtl8187_detect_rf()`. Inline helpers `rtl8225_write_phy_ofdm()` and `rtl8225_write_phy_cck()` call `rtl8187_write_phy()`, with the CCK helper setting the `0x10000` selector bit.

Analog constants cover non-B and B variants: `RTL8187_RTL8225_ANAPARAM_*` and `RTL8187B_RTL8225_ANAPARAM*_*`.

## Control Flow
No runtime flow is present. The header determines which constants and helper semantics the RF implementation uses during init/stop/power transitions.

## State And Persistence
No software state is declared. The analog constants are persisted into device registers by `dev.c` and `rtl8225.c`.

## Dependencies And Integration Points
It depends on `struct ieee80211_hw`, `struct rtl818x_rf_ops`, and `rtl8187_write_phy()` from `rtl8187.h`. It is included by `dev.c` for RF detection and analog constants and by `rtl8225.c` for implementation.

## Risks
Analog constants are chip-family-specific and should not be mixed between RTL8187 and RTL8187B. The CCK selector bit is a local PHY-write convention; changing `rtl8187_write_phy()` semantics would require updating both helpers.

## Test Signals
Compile-time include coverage plus successful RF detect/init/stop paths. Runtime validation comes through correct analog on/off transitions and CCK/OFDM baseband writes in `rtl8225.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8187/rtl8225.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl818x.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl818x.h

## Purpose
This shared header defines the RTL818x CSR register layout, register bit definitions, RTL8187SE raw-offset aliases, RF operation callback type, and common TX/RX descriptor flags used by RTL8180/RTL8187-family drivers.

## Important APIs, Types, And Functions
The central type is `struct rtl818x_csr`, a packed map of the device register space with unions for chip-specific interpretations. `struct rtl818x_rf_ops` defines the RF callback contract: name, init, stop, set channel, and optional RSSI calculation.

Important definitions cover command bits, interrupt bits for classic chips and RTL8187SE, TX/RX configuration bits, EEPROM command bits, analog/config bits, media status, RF pin registers, TX gain/antenna fields, contention/EDCA registers, RTL8187B revision IDs, and AC parameter shifts. `REG_ADDR1/2/4` and aliases such as `SW_3W_DB0`, `SW_3W_CMD1`, and `SI_DATA_REG` expose non-standard RTL8187SE offsets beyond the packed CSR.

## Control Flow
There is no runtime control flow. This file provides the symbolic contract that lets separate PCI/USB/RF files perform register I/O safely enough to be maintainable.

## State And Persistence
`struct rtl818x_csr` represents persistent hardware state, not allocated software state. The packed layout maps MAC address, multicast hash, TSF, TX/RX config, EEPROM command, analog parameters, PHY/RF pins, GPIO, gain, EDCA, and related registers.

## Dependencies And Integration Points
The header is shared by RTL8180 PCI and RTL8187 USB code. RTL8187 code treats `priv->map` as a pointer at register base `0xFF00`, while RTL8180 code maps actual MMIO. RF files use `rtl818x_rf_ops`; descriptor flags are shared by TX/RX descriptor construction and parsing.

## Risks
Packed register layouts and unions are fragile: an incorrect offset affects real hardware programming. Some fields have different meanings on RTL8187B or RTL8187SE, requiring raw-address workarounds. The `REG_ADDR*` macros assume a local variable named `priv`, which is convenient but brittle. TX and RX descriptor flags intentionally overlap bit positions with different meanings, so callers must use them in the correct direction.

## Test Signals
Compile coverage across RTL8180, RTL8187, and RTL8187SE paths is important. Runtime signals are correct register writes during probe/start/config, no endian/packing warnings, valid interrupts/configuration on each supported chip family, and descriptor flags matching observed TX/RX behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl818x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl8xxxu/8188e.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl8xxxu/8188e.c

## Purpose
This file is the RTL8188EU chip-specific backend for the generic `rtl8xxxu` mac80211 USB driver. It supplies MAC/PHY/RF initialization tables, chip identification, efuse parsing, firmware loading, channel setup, power sequencing, RF enable/disable, calibration, LED control, CCK RSSI conversion, and a software rate-adaptation implementation exposed through `rtl8188eu_fops`.

## Important APIs, Types, And Functions
The exported object is `struct rtl8xxxu_fileops rtl8188eu_fops`. Its callbacks include `identify_chip`, `parse_efuse`, `load_firmware`, `power_on`, `power_off`, `reset_8051`, `llt_init`, PHY/RF init, LC/IQ calibration, channel config, RX descriptor and phystats parsing, aggregation init, RF enable/disable, USB quirks, TX power, rate-mask update, connect/RSSI reporting, TX descriptor fill, crystal-cap setting, CCK RSSI, LED brightness, and chip-specific page/buffer constants.

Important internal routines are `rtl8188eu_identify_chip()`, `rtl8188eu_config_channel()`, `rtl8188eu_parse_efuse()`, `rtl8188eu_reset_8051()`, `rtl8188eu_init_phy_bb()`, `rtl8188eu_init_phy_rf()`, `rtl8188eu_phy_iq_calibrate()`, `rtl8188eu_power_on()`, `rtl8188eu_power_off()`, `rtl8188e_enable_rf()`, `rtl8188e_disable_rf()`, `rtl8188e_usb_quirks()`, `rtl8188e_cck_rssi()`, `rtl8188eu_led_brightness_set()`, `rtl8188e_handle_ra_tx_report2()`, and `rtl8188e_ra_info_init_all()`.

## Control Flow
Chip identification names the chip `8188EU`, sets one RF/RX/TX path, rejects unsupported test chips and cut I, identifies vendor from `REG_SYS_CFG`, and configures USB endpoints. Efuse parsing validates RTL ID `0x8129`, copies MAC address, CCK and HT40 power indexes, and crystal calibration.

Power-on moves disabled to emulation, waits for power-ready, resets BB, disables hardware powerdown/suspend, enables MAC through the APS FSM, switches LDO to normal mode, and enables DMA/protocol/security/caltimer blocks while delaying MAC TX/RX enable until USB quirks run. Power-off flushes FIFO, stops TX report timing, turns off RF, enters low-power state, self-resets firmware if in RAM, resets MCU and MCU-ready state, disables 32K control, moves through active-to-emu and emu-to-disabled, and resets GPIO/wrapper state.

Channel configuration handles 20 and 40 MHz widths, updates BW opmode, response-rate sideband bits, FPGA RF mode, CCK/OFDM sideband registers, RF channel/bandwidth fields, and RF path loops. PHY init enables BB/RF blocks, writes the large PHY and AGC tables, and initializes RF path A from the radio table.

IQ calibration runs up to three calibration attempts, saving ADDA/MAC/BB registers on the first pass, switching to PI mode if needed, performing TX and RX path A IQK, comparing result similarity, selecting a candidate matrix, filling IQK matrix A, and restoring saved state. CCK RSSI derives dBm from LNA/VGA indexes with separate cut-I and normal tables, although cut I is rejected earlier.

Rate adaptation consumes TX report type 2 data in `rtl8188e_handle_ra_tx_report2()`, updates retry/drop totals, makes rate up/down decisions using penalty and threshold tables, adjusts dynamic TX report timing, and maintains one `rtl8xxxu_ra_info` instance. LED brightness manipulates `REG_LEDCFG2` for off, on, or hardware LED control.

## State And Persistence
Persistent software state is in `struct rtl8xxxu_priv`: chip identity, efuse-derived MAC/power/crystal values, RF path counts, RA info, IQK backup/result fields, CFO tracking, current vifs, and shared rtl8xxxu hardware state. Hardware state includes firmware RAM, MAC table registers, PHY/AGC/RF tables, power FSM bits, TX report timer, LED config, rate-report registers, channel/BW registers, and RF gain/power registers.

## Dependencies And Integration Points
The file depends on shared `rtl8xxxu` infrastructure in `regs.h` and `rtl8xxxu.h`: USB register access, efuse reading, firmware loading, LLT init, PHY/RF table writers, calibration helpers, RX descriptor parsers, TX descriptor filling, gen2 reporting, and shared TX-power/crystal helpers from the 8188F support code (`rtl8188f_set_tx_power()` and `rtl8188f_set_crystal_cap()`).

## Risks
Power sequencing has a documented hardware bug requiring MAC TX/RX enable after `REG_TRXFF_BNDY`; moving `rtl8188e_usb_quirks()` earlier can corrupt RX FIFO boundaries. The software RA engine is stateful and only uses macid 0 in station mode, so AP/multi-station behavior would need expansion. IQK contains many magic values and partial failure fallback; bad candidate selection can degrade EVM/RSSI. Cut-I handling is contradictory in places: identification rejects cut I while RSSI/rate code still has cut-I branches. Efuse values are trusted with little range validation compared with 8188F.

## Test Signals
Signals include firmware load of `rtlwifi/rtl8188eufw.bin`, successful probe without cut-I rejection, correct MAC and TX power from efuse, association on 20/40 MHz channels, stable power on/off cycles, valid TX report handling and rate movement, LED class brightness behavior, CCK/OFDM RSSI plausibility, IQK debug output with selected candidates, and no RX FIFO boundary issues after initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl8xxxu/8188e.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl8xxxu/8188f.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl8xxxu/8188f.c

## Purpose
This file is the RTL8188FU chip-specific backend for the generic `rtl8xxxu` USB wireless driver. It provides initialization tables, chip identification, efuse parsing with power-index sanitization, firmware loading, channel and spur calibration, statistics setup, PHY/RF init, LC/IQ calibration, power sequencing, RF enable/disable, USB quirks, crystal-cap programming, CCK RSSI conversion, and the exported `rtl8188fu_fops` callback table.

## Important APIs, Types, And Functions
The exported object is `struct rtl8xxxu_fileops rtl8188fu_fops`. Public/shared functions include `rtl8188f_channel_to_group()`, `rtl8188f_set_tx_power()`, `rtl8188f_phy_lc_calibrate()`, and `rtl8188f_set_crystal_cap()`.

Key internals are `rtl8188fu_identify_chip()`, `rtl8188f_spur_calibration()`, `rtl8188fu_config_channel()`, `rtl8188fu_init_aggregation()`, `rtl8188fu_init_statistics()`, `rtl8188fu_parse_efuse()`, `rtl8188fu_init_phy_bb()`, `rtl8188fu_init_phy_rf()`, `rtl8188fu_iqk_path_a()`, `rtl8188fu_rx_iqk_path_a()`, `rtl8188fu_phy_iq_calibrate()`, the disabled/emu/active/LPS power transition helpers, `rtl8188f_enable_rf()`, `rtl8188f_disable_rf()`, `rtl8188f_usb_quirks()`, and `rtl8188f_cck_rssi()`.

## Control Flow
Identification names the chip `8188FU`, sets single-path Wi-Fi capabilities, rejects test chips, identifies vendor with a two-bit field, and configures endpoints. Efuse parsing validates RTL ID `0x8129`, copies MAC address and power indexes, clamps invalid CCK/HT40 power entries to defaults, loads OFDM/HT20 differences, and stores crystal calibration.

TX power setup maps channels into power groups, writes CCK, OFDM, and MCS AGC registers from efuse-derived indexes plus per-rate differences, and honors HT20/HT40 selection. Channel configuration first writes the RF channel, runs spur calibration to optionally enable CSI notch masks for known 2.4 GHz spurs, configures 20/40 MHz baseband and RF bandwidth, sets sideband/subchannel registers, response-rate bandwidth flags, RF filter bandwidth, and gain/CCA RF registers.

PHY baseband init enables BB/RF, writes an RF IQ adjustment value, writes the PHY and AGC tables, and initializes RF path A using a cut-B-specific table for chip cut 1 or the default table otherwise. LC calibration blocks TX or disables continuous TX, starts RF LC calibration, polls for completion, warns on timeout, and restores original TX/LSTF state.

IQ calibration saves path selection, ADDA/MAC/BB registers, runs repeated TX/RX path A LOK/IQK attempts with LOK result reuse, compares candidate similarity, fills IQK matrix A when successful, saves recovery registers, and restores S0/S1 path selection. Power-on/off flows move through disabled/emu/active states with APS FSM polling, MAC/DMA/security enable, FIFO flush, interrupt clear, TX report timer stop, firmware self-reset, MCU reset, active-to-LPS, active-to-emu, and emu-to-disabled transitions.

RF enable optionally reads a power-trim efuse byte at offset `0xee`, converts signed BB gain trim into RF register 0x55 fields, enables RF clocks/resets, sets OFDM TX/RX path A, and unpauses TX. USB quirks enable MAC TX/RX and set TXDMA offset drop-data behavior. Statistics initialization programs NHM timers and thresholds.

## State And Persistence
Software state lives in `rtl8xxxu_priv`: chip identity/cut/vendor, efuse power arrays and diffs, crystal/CFO tracking, RF path counts, IQK backup/result registers, S0/S1 path state, and shared rtl8xxxu runtime state. Hardware state includes firmware RAM, MAC/PHY/AGC/RF tables, power FSM bits, RF path and bandwidth registers, spur notch CSI masks, NHM statistics thresholds, TX power AGC registers, TX report timer, and crystal capacitor fields.

## Dependencies And Integration Points
The file depends on shared rtl8xxxu register definitions and helpers for firmware, efuse, LLT, PHY/RF table programming, gen2 rate/RSSI reporting, RX descriptor parsing, TX descriptor fill v2, burst initialization, antenna selection, and mac80211 channel definitions. `8188e.c` also reuses the 8188F TX-power and crystal-cap helpers.

## Risks
Spur calibration temporarily disables CCK, changes initial gain, disables/enables 3-wire access, and uses PSD thresholds; incomplete restoration would damage receive behavior. Channel configuration mutates the channel variable for HT40 center-channel handling and later writes it to RF mode, so sideband logic must stay consistent. Power state transitions poll hardware bits and return `-EBUSY` on timeout; callers need to handle partial power-up/down. IQK has many magic RF/BB writes and saves/restores S0/S1 path selection, which is easy to regress. Efuse power trimming reads an extra raw offset because it is not part of the earlier parsed efuse structure.

## Test Signals
Signals include firmware load of `rtlwifi/rtl8188fufw.bin`, successful operation on supported chip cuts including cut-B RF table selection, sane clamped TX power on devices with invalid efuse bytes, channel 5/6/7/8/11/13/14 spur-mask behavior, 20/40 MHz association, NHM statistic availability, LC/IQ calibration completion without timeouts, correct AP/concurrent support from fileops, stable power cycles, and plausible CCK RSSI from LNA/VGA mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl8xxxu/8188f.c -->
