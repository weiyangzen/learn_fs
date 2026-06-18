# subset-b-004981 NFC driver research

This grouped report covers the requested NFC driver source files under `sources/distributed-fs/ceph-client/drivers/nfc`. Each section is delimited for deterministic splitting into the matching source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/port100.c -->
# sources/distributed-fs/ceph-client/drivers/nfc/port100.c

## Purpose
`port100.c` is a USB driver for Sony Port-100/RCS380 NFC readers. It binds Sony USB IDs, speaks the Port-100 extended frame protocol over bulk endpoints, and registers a `nfc_digital_dev` with the kernel digital NFC stack for reader and target-mode operations.

## Important APIs, types, and functions
- `struct port100` owns the USB device/interface, input/output URBs, command completion work, selected command type, and the single in-flight `struct port100_cmd`.
- `struct port100_frame` and `struct port100_ack_frame` model Sony wire frames; helpers such as `port100_tx_frame_init()`, `port100_tx_frame_finish()`, `port100_rx_frame_is_valid()`, and `port100_rx_frame_is_ack()` enforce start-frame, length-checksum, data-checksum, and postamble conventions.
- `port100_send_cmd_async()` is the central command launcher. It wraps a caller payload in a Port-100 frame, allocates a response buffer, installs callbacks, submits the OUT URB, and starts waiting for ACK then response on the IN URB.
- `port100_in_configure_hw()`, `port100_in_send_cmd()`, `port100_tg_configure_hw()`, `port100_tg_send_cmd()`, `port100_listen_mdaa()`, `port100_switch_rf()`, and `port100_abort_cmd()` implement `struct nfc_digital_ops`.
- Static RF/framing tables (`in_rf_settings`, `tg_rf_settings`, `in_protocols`, `tg_protocols`) translate digital-core technologies/framings into Port-100 proprietary settings.

## Control flow
Probe finds USB bulk endpoints, allocates URBs, negotiates a supported command type, logs firmware version, allocates/registers the digital NFC device, and then the digital core drives operations through `port100_digital_ops`. A command follows a strict sequence: build extended frame, submit OUT URB, submit IN URB for ACK, resubmit IN URB for the command response, validate the response command code, and finish in `cmd_complete_work`. Synchronous helpers wait on a completion wrapper around the async callback.

Reader mode configures RF and protocol tables, prepends timeouts to `IN_COMM_RF`, and strips status/collision fields from responses. Target mode builds `TG_COMM_RF` headers, supports MDAA activation checks, and handles target activation masks differently for command type 0 and 1. RF-off calls `port100_abort_cmd()` first, sending a Port-100 ACK frame that cancels the last issued device command and killing the IN URB.

## State and persistence
State is in memory only: command type, one outstanding command, URBs, cancel flag/completion, and registered digital device. There is no persistent storage or firmware file use. The digital stack serializes commands, so the driver only protects the OUT URB and cancellation path with `out_urb_lock`.

## Dependencies and integration points
The file depends on USB core, `net/nfc/digital.h`, sk_buffs, workqueues, and the NFC digital core. It supports Jewel, MIFARE, Felica, NFC-DEP, ISO14443 A/B protocols. USB IDs cover Sony RCS380S and RCS380P.

## Risks
Frame parsing trusts the declared datalen after validation and relies on response buffers sized to `PORT100_FRAME_MAX_PAYLOAD_LEN`. Cancellation merges repeated ACK-cancel attempts through `cmd_cancel`, so races around RF-off and command completion are concentrated there. `port100_get_command_type_mask()` and firmware-version helpers return zero on allocation/command failure, which collapses detailed failure causes during probe. Target-mode parsing assumes responses are at least the proprietary header size; malformed short responses are partially checked but target response length validation is less explicit than reader mode.

## Test signals
Useful tests include USB probe/remove with both product IDs, command type negotiation fallback from type 1 to type 0, checksum rejection for malformed frames, ACK timeout/cancel behavior, RF on/off during an outstanding command, reader exchanges across all configured framings, target-mode MDAA activation timeout handling, and disconnect while a command completion work item is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/port100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/s3fwrn5/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/nfc/s3fwrn5/Kconfig

## Purpose
This Kconfig fragment defines build options for the Samsung S3FWRN5 NFC core, its I2C physical layer, and the related S3FWRN82 UART physical layer.

## Important symbols
- `NFC_S3FWRN5` is a hidden tristate selected by physical-layer drivers. It selects `CRYPTO_LIB_SHA1` because firmware download hashes images with SHA1.
- `NFC_S3FWRN5_I2C` is user-visible, depends on `NFC_NCI && I2C`, selects the shared core, and builds `s3fwrn5_i2c.ko`.
- `NFC_S3FWRN82_UART` is user-visible, depends on `NFC_NCI && SERIAL_DEV_BUS`, selects the same core, and builds `s3fwrn82_uart.ko`.

## Control flow and integration
The build graph keeps common NCI/firmware logic in the core object while letting I2C and UART choose their transport dependencies. Runtime integration is through the Linux NCI stack, not the digital or HCI stacks.

## State, persistence, and dependencies
Kconfig state is compile-time only. The important dependency signal is that firmware update support is always present when the core is selected, and UART support is tied to serdev rather than tty line disciplines.

## Risks
The UART option is S3FWRN82-specific but selects the S3FWRN5 core; regressions in common mode/firmware code can affect both chips. Missing `NFC_NCI` or transport dependencies prevent physical-layer visibility.

## Test signals
Config tests should cover built-in and module combinations for core, I2C, and UART; dependency pruning when `I2C` or `SERIAL_DEV_BUS` is disabled; and that selecting either physical layer pulls in `CRYPTO_LIB_SHA1` through the core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/s3fwrn5/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/s3fwrn5/Makefile -->
# sources/distributed-fs/ceph-client/drivers/nfc/s3fwrn5/Makefile

## Purpose
This Makefile maps S3FWRN5/S3FWRN82 Kconfig symbols to kernel objects.

## Important build objects
- `s3fwrn5-objs = core.o firmware.o nci.o phy_common.o` builds the shared NCI core, firmware-update protocol, proprietary NCI RF configuration, and GPIO mode helpers.
- `s3fwrn5_i2c-objs = i2c.o` builds the I2C transport module.
- `s3fwrn82_uart-objs = uart.o` builds the serdev UART transport module.

## Control flow and integration
`obj-$(CONFIG_NFC_S3FWRN5)` emits the shared module, while the I2C and UART objects are separate modules selected by their transport configs. Physical modules call exported symbols from the shared object.

## State, dependencies, and risks
There is no runtime state. The build is sensitive to symbol/module ordering because `i2c.o` and `uart.o` depend on exported `s3fwrn5_probe()`, `s3fwrn5_remove()`, common PHY helpers, and firmware/NCI receive paths from the core module.

## Test signals
Build tests should compile the shared core alone, each physical transport as a module, and all objects built-in to detect missing exports or module metadata regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/s3fwrn5/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/s3fwrn5/core.c -->
# sources/distributed-fs/ceph-client/drivers/nfc/s3fwrn5/core.c

## Purpose
`core.c` is the shared Samsung S3FWRN5 NCI glue layer. It allocates/registers the NCI device, exposes common probe/remove entry points for physical layers, routes inbound frames to NCI or firmware-update handlers by mode, and performs post-setup firmware/RF-reg updates.

## Important APIs, types, and functions
- `s3fwrn5_probe()` and `s3fwrn5_remove()` are exported for I2C/UART physical drivers.
- `s3fwrn5_nci_ops` implements NCI `open`, `close`, `send`, and `post_setup`, plus proprietary RF-reg ops from `nci.c`.
- `s3fwrn5_nci_open()` transitions from COLD to NCI mode and asserts wake; `s3fwrn5_nci_close()` drops wake and returns to COLD.
- `s3fwrn5_nci_send()` serializes sends with `info->mutex`, rejects non-NCI mode, delegates to the physical `write`, and consumes/frees skb appropriately.
- `s3fwrn5_nci_post_setup()` optionally requests firmware, performs bootloader update, then resets and initializes the NCI core.
- `s3fwrn5_recv_frame()` dispatches inbound sk_buffs to `nci_recv_frame()` in NCI mode or `s3fwrn5_fw_recv_frame()` in firmware mode.

## Control flow
Physical-layer probe calls `s3fwrn5_probe()` with a `phy_id` and `s3fwrn5_phy_ops`. The core initializes mode COLD, allocates an NCI device supporting Jewel, MIFARE, Felica, ISO14443 A/B, and ISO15693, binds driver data, registers with NCI, and stores the NCI pointer back to the physical driver. After NCI setup, firmware init tries to load `sec_s3fwrn5_firmware.bin`; failure skips bootloader mode. If present, firmware mode is entered, boot info is read, versions are compared against `manufact_specific_info`, download may run, then NCI mode is used to push `sec_s3fwrn5_rfreg.bin` before a core reset/init.

## State and persistence
Runtime state is `struct s3fwrn5_info`: NCI device pointer, physical opaque id, device pointer, physical ops, firmware info, and a send mutex. Persistent inputs are external firmware files requested through the firmware loader; no driver state is written back to disk. Chip mode is delegated to physical ops and represented as COLD/NCI/FW.

## Dependencies and integration points
This file integrates with `net/nfc/nci_core.h`, firmware helpers, proprietary NCI RF-reg helpers, and physical transport implementations. It depends on physical layers honoring mode and wake semantics for safe bootloader/NCI transitions.

## Risks
Firmware request failure intentionally skips update, which may hide missing firmware deployment. `s3fwrn5_get_mode()` returns an enum but uses `-EOPNOTSUPP` if an op is missing; because the enum is unsigned-like logic, missing ops can produce confusing mode comparisons. Post-setup returns immediately if NCI reset fails after leaving wake asserted, so physical state cleanup on partial failure depends on later close/remove.

## Test signals
Tests should cover probe/register failure cleanup, open while not COLD returning `-EBUSY`, send rejection outside NCI mode, firmware absent path, firmware present but no update path, update plus RF-reg configuration path, and inbound frame routing in all three modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/s3fwrn5/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/s3fwrn5/firmware.c -->
# sources/distributed-fs/ceph-client/drivers/nfc/s3fwrn5/firmware.c

## Purpose
`firmware.c` implements Samsung S3FWRN5 bootloader communication and firmware download. It parses the firmware image header, determines hardware-specific base address/signature selection, compares versions, hashes image data, sends update commands, and completes request/response transactions using inbound firmware frames.

## Important APIs, types, and functions
- `s3fwrn5_fw_init()`, `s3fwrn5_fw_request_firmware()`, `s3fwrn5_fw_setup()`, `s3fwrn5_fw_check_version()`, `s3fwrn5_fw_download()`, `s3fwrn5_fw_cleanup()`, and `s3fwrn5_fw_recv_frame()` are the core-facing API.
- `s3fwrn5_fw_prep_msg()` builds firmware headers, toggling the parity bit in `fw_info->parity`.
- `s3fwrn5_fw_send_msg()` writes through the physical layer and waits up to one second for `fw_info->completion`.
- Bootloader commands include GET_BOOTINFO, ENTER_UPDATE_MODE, UPDATE_SECTOR, and COMPLETE_UPDATE_MODE.
- The image header contains date, version, signature offsets/sizes, image offset/sector count, and custom-signature offsets/sizes.

## Control flow
The core first initializes `fw_info`, requests a named firmware blob, and parses fixed offsets. Setup sends GET_BOOTINFO in firmware mode, maps hardware version to a base address, records sector size, and chooses standard or custom signature based on `hw_version[2]`. Version comparison treats larger major, build1, or build2 fields as needing update. Download computes SHA1 over `sector_size * image_sectors`, enters update mode with hash and signature, then writes each sector as one UPDATE_SECTOR command followed by sixteen 256-byte data packets. Completion sends COMPLETE_UPDATE_MODE.

## State and persistence
`struct s3fwrn5_fw_info` stores the requested firmware object, parsed pointers into the firmware blob, selected signature, sector/base metadata, completion, pending response skb, firmware name, and parity. The firmware blob is read-only external persistent input and is released by cleanup; no persistent state is stored by the driver.

## Dependencies and integration points
The file depends on `request_firmware()`, `release_firmware()`, SHA1 from `crypto/sha1.h`, sk_buffs, completions, and `s3fwrn5_write()`. It expects the physical layer to be in firmware mode and inbound frames to call `s3fwrn5_fw_recv_frame()`.

## Risks
Firmware header offsets and sizes are copied from the blob but not fully bounds-checked beyond the 44-byte minimum; malformed images could create out-of-range pointers or image sizes. `s3fwrn5_fw_update_sector()` sends fixed sixteen 256-byte packets, assuming sector size and bootloader expectations align. Version comparison is lexicographic but does not check target field. A stale `fw_info->rsp` triggers `WARN_ON` and drops a frame, so duplicate/unexpected responses can derail an update.

## Test signals
Exercise malformed firmware headers, unknown hardware versions, custom-signature selection, no-update version comparison, update success over multiple sectors, timeout from `s3fwrn5_fw_send_msg()`, non-success bootloader return codes, duplicate response handling, and cleanup after setup failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/s3fwrn5/firmware.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/s3fwrn5/firmware.h -->
# sources/distributed-fs/ceph-client/drivers/nfc/s3fwrn5/firmware.h

## Purpose
`firmware.h` defines the S3FWRN5 firmware-update wire protocol structures, return codes, parsed firmware-image representation, firmware runtime state, and exported firmware helper prototypes.

## Important APIs, types, and constants
- Message types are `S3FWRN5_FW_MSG_CMD`, `S3FWRN5_FW_MSG_RSP`, and `S3FWRN5_FW_MSG_DATA`.
- Return codes enumerate bootloader failures such as invalid command, authentication failure, flash failure, address out of range, and invalid parameter.
- `struct s3fwrn5_fw_header` is the packed 4-byte firmware frame header with type, code, and length.
- Command payload structs describe GET_BOOTINFO response, ENTER_UPDATE_MODE sizes, and UPDATE_SECTOR base address.
- `struct s3fwrn5_fw_image` stores parsed firmware-blob metadata and pointers.
- `struct s3fwrn5_fw_info` stores firmware runtime state, selected signature, base/sector metadata, completion, pending response, and parity.

## Control flow and integration
The header is consumed by `firmware.c`, `core.c`, and physical readers that need `S3FWRN5_FW_HDR_SIZE` to distinguish firmware frames from NCI frames. Its prototypes are the only interface the shared core needs for optional update handling.

## State and persistence
The types model in-memory state only. Firmware persistence is external to the driver through Linux firmware files; pointers in `s3fwrn5_fw_image` are valid only while the requested firmware object is held.

## Dependencies and risks
The header relies on kernel integer types, `struct firmware`, `struct completion`, `struct sk_buff`, and `struct nci_dev` through included/including files. Protocol structs use native-endian integer fields as written by the C code; portability depends on the chip and firmware format matching the driver's endianness assumptions.

## Test signals
Compile coverage should verify all consumers agree on header size and struct layout. Runtime tests should validate command/response parsing against real bootloader frames and check return-code mapping to driver errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/s3fwrn5/firmware.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/s3fwrn5/i2c.c -->
# sources/distributed-fs/ceph-client/drivers/nfc/s3fwrn5/i2c.c

## Purpose
`i2c.c` is the S3FWRN5 I2C physical layer. It owns GPIOs, optional clock enablement, IRQ-driven reads, I2C writes, and mode-specific frame extraction before handing frames to the shared S3FWRN5 core.

## Important APIs, types, and functions
- `struct s3fwrn5_i2c_phy` wraps `struct phy_common`, the I2C client, optional clock, and `irq_skip`.
- `s3fwrn5_i2c_set_mode()` uses common power control and suppresses the next IRQ after mode transition.
- `s3fwrn5_i2c_write()` sends sk_buff data with a standby retry on `-EREMOTEIO`.
- `s3fwrn5_i2c_read()` reads either an NCI control header or firmware header, then reads the declared payload and passes the skb to `s3fwrn5_recv_frame()`.
- `s3fwrn5_i2c_probe()` acquires `en` and `wake` GPIOs, enables an optional clock, calls `s3fwrn5_probe()`, and registers a threaded IRQ.

## Control flow
On probe, the physical object starts in COLD with IRQ skip enabled. The common core controls mode/wake through `i2c_phy_ops`. IRQ thread validates context, locks the common mutex, skips one IRQ after power transitions, then reads only in NCI or FW mode. Reads are two-stage: header first, payload second. Remove delegates to `s3fwrn5_remove()`.

## State and persistence
Runtime state includes mode/wake GPIO values, optional clock enablement managed by devm, IRQ skip, and the common NCI device pointer. There is no persistent storage.

## Dependencies and integration points
This file integrates with I2C, GPIO descriptor API, optional clocks, threaded IRQs, NCI header definitions, S3FWRN5 firmware header definitions, and the shared core. Device tree compatible is `samsung,s3fwrn5-i2c`.

## Risks
The read path uses NCI control-header length even though data/notification packet header formats can differ; correctness depends on the chip interrupting for control-like frames or common header compatibility. Payload lengths are trusted after the header read. `irq_skip` may drop a legitimate first frame if a device asserts IRQ immediately after a mode transition. Standby retry only handles `-EREMOTEIO`.

## Test signals
Test probe with missing GPIOs, optional clock failures, standby write retry, short header read, short payload read, IRQ during COLD mode, firmware-mode frame routing, and removal after IRQ registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/s3fwrn5/i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/s3fwrn5/nci.c -->
# sources/distributed-fs/ceph-client/drivers/nfc/s3fwrn5/nci.c

## Purpose
`nci.c` implements S3FWRN5 proprietary NCI operations, mainly RF-register configuration after firmware update.

## Important APIs, types, and functions
- `s3fwrn5_nci_prop_ops` registers response handlers for proprietary commands `SET_RFREG`, `START_RFREG`, `STOP_RFREG`, and `FW_CFG`.
- `s3fwrn5_nci_prop_rsp()` completes an NCI request with the returned status byte.
- `s3fwrn5_nci_rf_configure()` loads an RF register firmware file, computes a checksum, sends default clock config, starts RF-reg update, sends 252-byte chunks with incrementing index, and stops with checksum.

## Control flow
The shared core calls `s3fwrn5_nci_rf_configure()` after a successful firmware download and a switch back to NCI mode. The function requests `sec_s3fwrn5_rfreg.bin`, sends `FW_CFG`, then `START_RFREG`, multiple `SET_RFREG` commands, and finally `STOP_RFREG`. Each command is synchronous through `nci_prop_cmd()` and uses the proprietary response ops to complete.

## State and persistence
The RF-reg blob is external persistent input read through Linux firmware APIs. Driver state is temporary: checksum, chunk index, and stack command structs. No data is persisted by the driver.

## Dependencies and integration points
The file depends on NCI proprietary command support, firmware loader, and `struct s3fwrn5_info`. It is wired into `s3fwrn5_nci_ops` from `core.c`.

## Risks
Checksum loops in 4-byte increments over `fw->size` and casts firmware data to `u32 *`, so unaligned or non-multiple-of-four firmware sizes are risky. Chunk payload uses a fixed 252-byte buffer and sends `len + 1`; malformed or zero-length RF-reg files should be tested. Clock defaults are hard-coded for external crystal.

## Test signals
Test missing RF-reg file, short/non-multiple-of-four RF-reg file, command failure at each stage, checksum correctness, final release of firmware, and successful configuration after firmware update.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/s3fwrn5/nci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/s3fwrn5/nci.h -->
# sources/distributed-fs/ceph-client/drivers/nfc/s3fwrn5/nci.h

## Purpose
`nci.h` defines S3FWRN5 proprietary NCI opcodes and command/response payload layouts used for RF-register and firmware clock configuration.

## Important APIs and types
- `NCI_PROP_SET_RFREG`, `NCI_PROP_START_RFREG`, `NCI_PROP_STOP_RFREG`, and `NCI_PROP_FW_CFG` are proprietary command identifiers under the NCI proprietary group.
- `struct nci_prop_set_rfreg_cmd` carries a section index plus up to 252 data bytes.
- `struct nci_prop_stop_rfreg_cmd` carries the final checksum.
- `struct nci_prop_fw_cfg_cmd` carries clock type, speed, and request settings.
- The header exports `s3fwrn5_nci_prop_ops` and `s3fwrn5_nci_rf_configure()`.

## Control flow and integration
The shared NCI ops in `core.c` register these proprietary response handlers. Firmware-update flow calls RF configuration through the exported function after returning the chip to NCI mode.

## State, dependencies, and risks
There is no standalone state. The layouts must match firmware expectations exactly; `set_rfreg` has a fixed 252-byte payload that matches the chunk size in `nci.c`. Endianness of the checksum field should be verified against chip documentation because the code writes native `__u16`.

## Test signals
Build tests should catch declaration drift between `nci.c` and the header. Runtime tests should validate the wire payloads for all four proprietary commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/s3fwrn5/nci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/s3fwrn5/phy_common.c -->
# sources/distributed-fs/ceph-client/drivers/nfc/s3fwrn5/phy_common.c

## Purpose
`phy_common.c` provides GPIO-based wake and mode/power sequencing shared by S3FWRN5 I2C and S3FWRN82 UART physical layers.

## Important APIs and functions
- `s3fwrn5_phy_set_wake()` sets the firmware wake GPIO and waits when waking.
- `s3fwrn5_phy_power_ctrl()` changes COLD/NCI/FW mode, drives enable and wake GPIOs, and performs required 20 ms waits.
- `s3fwrn5_phy_set_mode()` wraps power control in the common mutex.
- `s3fwrn5_phy_get_mode()` returns the current mode under the same mutex.

## Control flow
Mode changes first short-circuit if already in the requested mode. Otherwise the function updates `phy->mode`, asserts enable, drops wake, asserts wake for firmware mode, and for non-COLD modes pulses enable low after waits. Wake control is separate and can be used by NCI open/close and firmware update steps.

## State and persistence
The only state is the in-memory `phy_common.mode` plus hardware GPIO output levels. There is no persistent state.

## Dependencies and integration points
The helpers depend on GPIO descriptors, mutexes, delays, and `struct phy_common`. They are exported for transport modules and used through `s3fwrn5_phy_ops`.

## Risks
Mode is updated before GPIO sequencing completes, so failures are not representable because GPIO set calls are void for already acquired descriptors. Fixed waits may be marginal on slow boards. `s3fwrn5_phy_set_wake()` locks the same common mutex as mode changes, preventing direct races but making wake latency blocking.

## Test signals
Tests should verify GPIO transitions for COLD/NCI/FW, no-op same-mode transitions, wake timing expectations, and concurrent wake/mode calls from send/open/firmware paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/s3fwrn5/phy_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/s3fwrn5/phy_common.h -->
# sources/distributed-fs/ceph-client/drivers/nfc/s3fwrn5/phy_common.h

## Purpose
`phy_common.h` declares the shared S3FWRN5 physical-layer state and GPIO helper API.

## Important APIs and types
- `S3FWRN5_EN_WAIT_TIME` defines the 20 ms wait used during enable/wake sequencing.
- `struct phy_common` stores the NCI device pointer, enable GPIO, firmware-wake GPIO, mutex, and current S3FWRN5 mode.
- Function prototypes expose wake, power control, mode set, and mode get helpers.

## Control flow and integration
Transport drivers embed `struct phy_common` as their first/common member and pass it directly to helper operations via `phy_id`. The shared core uses these helpers indirectly through `struct s3fwrn5_phy_ops`.

## State, dependencies, and risks
The header depends on GPIO descriptors, mutexes, NCI core types, and `s3fwrn5.h`. The risk is structural coupling: helper implementations cast `void *phy_id` to `struct phy_common *`, so embeddings must keep the common object address compatible with what they pass.

## Test signals
Compile tests for both I2C and UART transports, plus runtime tests of mode/wake paths, provide coverage for this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/s3fwrn5/phy_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/s3fwrn5/s3fwrn5.h -->
# sources/distributed-fs/ceph-client/drivers/nfc/s3fwrn5/s3fwrn5.h

## Purpose
`s3fwrn5.h` defines the shared Samsung S3FWRN5 core contract between physical layers, firmware code, and NCI glue.

## Important APIs and types
- `enum s3fwrn5_mode` defines COLD, NCI, and firmware modes.
- `struct s3fwrn5_phy_ops` abstracts wake, mode set/get, and write operations supplied by physical layers.
- `struct s3fwrn5_info` stores the NCI device, physical id, parent device, physical ops, firmware state, and core mutex.
- Inline wrappers `s3fwrn5_set_mode()`, `s3fwrn5_get_mode()`, `s3fwrn5_set_wake()`, and `s3fwrn5_write()` validate operation presence and call through to the transport.
- Prototypes expose shared probe/remove and inbound frame routing.

## Control flow and integration
Physical drivers call `s3fwrn5_probe()` and provide `s3fwrn5_phy_ops`; the core uses inline wrappers everywhere else. Receive paths in transports call `s3fwrn5_recv_frame()` with the current mode.

## State and persistence
The header describes in-memory runtime state only. Firmware persistence is represented indirectly through `struct s3fwrn5_fw_info`.

## Dependencies and risks
It depends on Linux NFC/NCI types and `firmware.h`. The inline `s3fwrn5_get_mode()` returns `-EOPNOTSUPP` through an enum return type when missing, so all physical ops should be complete. The `set_wake` argument is named `sleep` in the function pointer but used as wake semantics by callers, which can confuse maintainers.

## Test signals
Build tests should catch missing physical ops. Runtime tests should verify each physical implementation obeys the mode/wake/write contract expected by `core.c` and `firmware.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/s3fwrn5/s3fwrn5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/s3fwrn5/uart.c -->
# sources/distributed-fs/ceph-client/drivers/nfc/s3fwrn5/uart.c

## Purpose
`uart.c` is the serdev UART transport for Samsung S3FWRN82 using the shared S3FWRN5 NCI core and common GPIO power helpers.

## Important APIs, types, and functions
- `struct s3fwrn82_uart_phy` embeds `phy_common`, the serdev device, and an accumulating receive skb.
- `s3fwrn82_uart_write()` writes complete sk_buffs using `serdev_device_write()`.
- `s3fwrn82_uart_read()` is the serdev receive callback; it accumulates bytes until the NCI header and declared payload length are present, then calls `s3fwrn5_recv_frame()`.
- `s3fwrn82_uart_probe()` opens/configures serdev at 115200 baud, disables flow control, obtains `en` and `wake` GPIOs, and calls `s3fwrn5_probe()`.
- `s3fwrn82_uart_remove()` removes the shared core, closes serdev, and frees the receive skb.

## Control flow
Probe allocates an initial receive skb and sets the device COLD. Incoming bytes are appended one by one. Once at least 3 NCI header bytes exist and `len - 3` reaches the payload length byte, the skb is delivered to the shared receive router and accumulation restarts with a new allocation on the next byte. TX is direct and blocking with an infinite schedule timeout.

## State and persistence
Runtime state is serdev open/configuration, common GPIO/mode state, and the partially filled receive skb. There is no persistent storage.

## Dependencies and integration points
The file depends on serdev, GPIO descriptors, NFC/NCI packet format, and the shared S3FWRN5 core. Device tree compatible is `samsung,s3fwrn82`.

## Risks
Receive parsing is NCI-header-specific and does not branch for firmware headers, so firmware-update receive over UART may not be supported even though the shared core has firmware mode. The receive buffer is fixed at 258 bytes; invalid length bytes could fill the skb to its limit without explicit overflow checks beyond skb behavior. Probe preallocates `recv_skb`, but `s3fwrn82_uart_read()` also allocates when it is NULL after delivery.

## Test signals
Test probe error unwinding for baud mismatch, missing GPIOs, and core probe failure; byte-by-byte frame assembly; multiple frames in one receive callback; short frames; maximum-length frames; and remove while a partial skb exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/s3fwrn5/uart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/st-nci/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/nfc/st-nci/Kconfig

## Purpose
This Kconfig fragment defines the STMicroelectronics NCI-family core and its I2C/SPI physical-layer options.

## Important symbols
- `NFC_ST_NCI` is a hidden tristate core selected by transports and contains chipset NCI logic.
- `NFC_ST_NCI_I2C` depends on `NFC_NCI && I2C`, selects the core, and builds `st-nci_i2c`.
- `NFC_ST_NCI_SPI` depends on `NFC_NCI && SPI`, selects the core, and builds `st-nci_spi`.

## Control flow and integration
The build layout separates the common NCI/HCI/SE/vendor implementation from physical links. Runtime transport registration flows through `ndlc_probe()` into `st_nci_probe()`.

## State, dependencies, and risks
Kconfig state is compile-time only. Correct dependency expression is important because both transports need the NCI stack and the shared NDLC/core code. The help text identifies the family-level nature of these drivers, so compatible strings in I2C/SPI source determine exact chip coverage.

## Test signals
Configuration tests should cover built-in/module combinations, disabling `NFC_NCI`, disabling individual buses, and verifying each transport selects the core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/st-nci/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/st-nci/Makefile -->
# sources/distributed-fs/ceph-client/drivers/nfc/st-nci/Makefile

## Purpose
This Makefile builds the ST NCI shared module and optional I2C/SPI transport modules.

## Important build objects
- `st-nci-objs = ndlc.o core.o se.o vendor_cmds.o` combines the low-level transport state machine, NCI glue, secure-element support, and vendor command handlers.
- `st-nci_i2c-objs = i2c.o` and `st-nci_spi-objs = spi.o` build physical links.

## Control flow and integration
Transport modules call into exported NDLC and core symbols from the shared module. The object grouping ensures secure-element and vendor-command hooks are present whenever the core is selected.

## State, dependencies, and risks
There is no runtime state. Build risks are missing exports or mismatched module symbol names, especially because the module name uses a hyphen while transport object names use underscore forms.

## Test signals
Build all combinations as modules and built-ins, and run modpost to catch missing exported symbols between physical and shared modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/st-nci/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/st-nci/core.c -->
# sources/distributed-fs/ceph-client/drivers/nfc/st-nci/core.c

## Purpose
`core.c` is the common NCI driver for STMicroelectronics ST_NCI chips. It registers an NCI device on top of an NDLC transport, initializes proprietary NFC mode, exposes secure-element hooks, and registers ST vendor commands.

## Important APIs, types, and functions
- `st_nci_probe()` allocates `struct st_nci_info`, allocates/registers the NCI device, registers vendor commands, and initializes secure-element state.
- `st_nci_remove()` closes NDLC, unregisters, and frees the NCI device.
- `st_nci_open()`/`st_nci_close()` manage `ST_NCI_RUNNING` and call `ndlc_open()`/`ndlc_close()`.
- `st_nci_send()` checks running state, stores the NCI device in `skb->dev`, and queues through `ndlc_send()`.
- `st_nci_init()` sends proprietary `ST_NCI_CORE_PROP` / `ST_NCI_SET_NFC_MODE` to enable NFC mode.
- `st_nci_get_rfprotocol()` maps proprietary ISO15693 protocol id `0x83` to `NFC_PROTO_ISO15693_MASK`.

## Control flow
Physical I2C/SPI probe creates NDLC, then calls `st_nci_probe()`. NCI registration exposes protocols including Jewel, MIFARE, Felica, ISO14443 A/B, ISO15693, and NFC-DEP. Open powers the NDLC link and sets the running bit; send queues frames into NDLC; close sends a proprietary mode-off during NDLC close and disables the transport. Secure-element and HCI callbacks are wired directly into `st_nci_ops`.

## State and persistence
State lives in `struct st_nci_info`: NDLC pointer, flags, and `st_nci_se_info`. There is no file persistence. HCI session identity and secure-element discovery are handled by `se.c` during NCI/HCI setup.

## Dependencies and integration points
The core depends on `net/nfc/nci_core.h`, NDLC, secure-element helpers, and vendor-command registration. It is transport-neutral; I2C and SPI provide `struct nfc_phy_ops` to NDLC.

## Risks
`st_nci_remove()` closes NDLC regardless of current running state. `st_nci_send()` returns `-EBUSY` without freeing the skb if not running, relying on NCI core ownership conventions. Vendor command init failure and NCI register failure share cleanup but do not explicitly unregister vendor commands.

## Test signals
Test probe failure at allocation/vendor/register stages, open/close idempotence, send while stopped, proprietary init response handling, ISO15693 RF protocol mapping, and secure-element hook invocation through NCI core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/st-nci/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/st-nci/i2c.c -->
# sources/distributed-fs/ceph-client/drivers/nfc/st-nci/i2c.c

## Purpose
`i2c.c` is the I2C physical layer for ST_NCI chips. It resets/enables the controller, transfers NDLC-framed NCI packets over I2C, services IRQs, and starts the shared NDLC/core stack.

## Important APIs, types, and functions
- `struct st_nci_i2c_phy` stores the I2C client, NDLC pointer, IRQ active flag, reset GPIO, and secure-element presence flags.
- `st_nci_i2c_enable()` toggles reset low/high with delays and enables IRQ when appropriate.
- `st_nci_i2c_disable()` disables IRQ.
- `st_nci_i2c_write()` sends an skb over I2C and retries once for standby errors.
- `st_nci_i2c_read()` reads a 4-byte NDLC/NCI prefix, validates declared length up to 250, allocates an skb, and reads the payload.
- The threaded IRQ reads frames only when powered and passes valid skbs to `ndlc_recv()`.

## Control flow
Probe checks I2C functionality, gets reset GPIO, reads `ese-present` and `uicc-present` properties, calls `ndlc_probe()` with I2C phy ops and headroom/tailroom, then registers a threaded IRQ. Runtime open from the NCI core calls through NDLC to `enable`; IRQs deliver received frames into the NDLC state machine; writes originate from NDLC send queue.

## State and persistence
Runtime state includes reset GPIO level, `irq_active`, NDLC powered/hard-fault state, and secure-element presence booleans read from firmware/ACPI/device tree. No persistent data is written.

## Dependencies and integration points
Dependencies include I2C, GPIO, ACPI GPIO mapping, OF matching, threaded IRQs, `ndlc_probe()`, and ST_NCI secure-element status. Compatible strings include `st,st21nfcb-i2c`, `st,st21nfcb_i2c`, and `st,st21nfcc-i2c`; ACPI IDs include `SMO2101` and `SMO2102`.

## Risks
The length field is read from bytes 2-3 after an initial 4-byte read and trusted for allocation/payload read. IRQ is initially considered active before `devm_request_threaded_irq()` succeeds. `st_nci_i2c_disable()` may be called even if IRQ was not enabled, so IRQ active state must stay coherent. Read errors are mostly dropped in IRQ context and not always promoted to `hard_fault`.

## Test signals
Test reset timing, IRQ enable/disable during open/close, standby write/read retries, invalid length, short payload read, device properties for SE discovery, ACPI/OF matching, and remove cleanup through `ndlc_remove()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/st-nci/i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/st-nci/ndlc.c -->
# sources/distributed-fs/ceph-client/drivers/nfc/st-nci/ndlc.c

## Purpose
`ndlc.c` implements the ST low-level NDLC transport state machine used beneath the ST_NCI NCI core. It adds/removes packet control bytes, queues outgoing and incoming frames, handles supervisor ACK/NACK/WAIT frames, retransmits on timeout, and detects hard link faults.

## Important APIs, types, and functions
- `ndlc_probe()` allocates `struct llt_ndlc`, initializes timers/queues/work, then calls `st_nci_probe()`.
- `ndlc_open()` enables the physical link and marks it powered.
- `ndlc_close()` toggles reset, sends proprietary NFC mode off, marks unpowered, and disables the physical link.
- `ndlc_send()` prepends a data-frame PCB and queues an skb for worker processing.
- `ndlc_recv()` queues inbound skbs and schedules the state-machine work; NULL receive marks hard fault and closes the link.
- Internal helpers process send queue, receive queue, retransmission, and T1/T2 timer expiry.

## Control flow
Outgoing NCI frames are wrapped with a data PCB and appended to `send_q`. The worker writes each frame through physical ops, records send jiffies in `skb->cb`, moves it to `ack_pending_q`, and arms T1 for supervisor acknowledgement plus T2 for chip availability. Incoming supervisor ACK frees one pending skb and stops timers; NACK requeues pending frames with retransmit bits; WAIT extends T1. Incoming data frames strip the PCB and enter `nci_recv_frame()`. T1 expiry requeues pending data; T2 expiry closes NDLC and sets `hard_fault = -EREMOTEIO`.

## State and persistence
State is in-memory queues (`rcv_q`, `send_q`, `ack_pending_q`), timers, active flags, work item, powered flag, and `hard_fault`. There is no persistence. `skb->cb` temporarily records send time.

## Dependencies and integration points
NDLC depends on transport `struct nfc_phy_ops` for write/enable/disable, NCI core for receive, timers, sk_buff queues, and ST_NCI proprietary mode commands. I2C/SPI transports call `ndlc_recv()` from IRQ contexts.

## Risks
No explicit locking protects queues/timer flags beyond skb queue internals and serialized work assumptions; races between IRQ receive, send, close, and remove need care. ACK handling dequeues one pending skb without checking NULL. `ndlc_remove()` purges `rcv_q` and `send_q` but not `ack_pending_q`, which may leak pending skbs. T2 timeout calls `ndlc_close()` from worker context and sends an NCI proprietary command during fault handling.

## Test signals
Unit-style tests should cover ACK/NACK/WAIT PCBs, T1 retransmit, T2 hard fault, write failure hard fault, data-frame receive, NULL receive, close while pending frames exist, and remove with nonempty `ack_pending_q`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/st-nci/ndlc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/st-nci/ndlc.h -->
# sources/distributed-fs/ceph-client/drivers/nfc/st-nci/ndlc.h

## Purpose
`ndlc.h` declares the ST low-level transport object and exported NDLC lifecycle/send/receive API.

## Important APIs and types
- `struct llt_ndlc` stores the NCI device, physical ops/id, T1/T2 timers and active flags, receive/send/ack-pending queues, state-machine work item, parent device, hard-fault code, and powered flag.
- Prototypes expose `ndlc_open()`, `ndlc_close()`, `ndlc_send()`, `ndlc_recv()`, `ndlc_probe()`, and `ndlc_remove()`.

## Control flow and integration
Physical drivers allocate NDLC through `ndlc_probe()` and receive back an `llt_ndlc *`. The ST_NCI core opens/closes/sends through NDLC, while physical IRQ handlers feed received skbs through `ndlc_recv()`.

## State, dependencies, and risks
The structure concentrates link state shared across core and physical layers. `hard_fault` is the transport-wide latch for unrecoverable hardware errors. Consumers must respect that the header does not provide external locking; all state transitions are expected to go through NDLC functions and worker/timer callbacks.

## Test signals
Compile tests should validate both I2C and SPI users. Runtime tests should ensure hard-fault, powered, and queue states stay consistent across open, send, receive, close, and remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/st-nci/ndlc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/st-nci/se.c -->
# sources/distributed-fs/ceph-client/drivers/nfc/st-nci/se.c

## Purpose
`se.c` implements ST_NCI secure-element and HCI-session support. It loads dynamic HCI pipe state, manages UICC/eSE discovery and activation, handles APDU reader and connectivity events, and enforces APDU timeout recovery.

## Important APIs, types, and functions
- `st_nci_hci_load_session()` connects the device-management gate, queries existing pipe lists/info, maps open pipes into the NCI HCI gate tables, and connects link management.
- `st_nci_discover_se()`, `st_nci_enable_se()`, `st_nci_disable_se()`, and `st_nci_se_io()` implement secure-element NCI ops.
- `st_nci_hci_event_received()` dispatches HCI events by gate to admin, APDU reader, and connectivity handlers.
- `st_nci_hci_cmd_received()` counts opened pipes during activation.
- `st_nci_hci_network_init()` creates an HCI access connection, sets gate init data/session id, initializes HCI session, and enables/disables NFCEE based on factory mode.
- Timers `bwi_timer` and `se_active_timer` handle APDU wait extension and hot-plug/pipe activation waits.

## Control flow
During secure-element discovery, HCI network initialization creates an NFCEE HCI connection and session. Unless factory mode is set, a whitelist is programmed from device properties and UICC/eSE entries are added to NFC core. Enabling an SE calls `nci_nfcee_mode_set()`, waits for hot-plug/open-pipe completion, rechecks host list, and for eSE reads ATR plus sends a soft reset. APDU I/O stores the caller callback/context, starts BWI timeout, and sends APDU data on the APDU reader gate. APDU reader transmit responses stop the timer and call the callback; WTX events extend the timer. Connectivity transaction events parse AID/parameters TLVs and report through `nfc_se_transaction()`.

## State and persistence
`struct st_nci_se_info` stores secure-element presence pointer, ATR, request completion, BWI timeout, activation timeout, active flags, exchange-error toggle, APDU callback, and callback context. HCI session id is generated from `"ST21BH"` plus a bitmap-selected device number, but the bitmap is not cleared in visible remove code. No file persistence is used.

## Dependencies and integration points
The file depends on NCI HCI APIs, NCI core connection APIs, NFC secure-element APIs, timer/completion APIs, and ST_NCI device-management gates. It consumes `ese-present` and `uicc-present` status supplied by physical layers.

## Risks
Host-list scanning reads `sk_host_list->data[i]` after a loop that can end at `i == len`, risking out-of-bounds if the host is absent. Several event parse error paths return without freeing skb, depending on caller handling. `st_nci_se_deinit()` exists but `st_nci_remove()` does not call it directly. BWI timeout calls the APDU callback from timer context after sending reset events, so callback assumptions matter.

## Test signals
Test pipe-list discovery with existing dynamic pipes, factory mode skipping SE activation, host list absent/present cases, UICC/eSE enable/disable, ATR-derived BWI timeout, WTX extension, APDU response callback, APDU timeout soft/hard reset alternation, and malformed connectivity transaction TLVs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/st-nci/se.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/st-nci/spi.c -->
# sources/distributed-fs/ceph-client/drivers/nfc/st-nci/spi.c

## Purpose
`spi.c` is the SPI physical layer for ST_NCI chips. It mirrors the I2C transport's reset/IRQ behavior while using SPI transfers and feeding full-duplex received bytes back into NDLC.

## Important APIs, types, and functions
- `struct st_nci_spi_phy` stores SPI device, NDLC pointer, IRQ active flag, reset GPIO, and secure-element status.
- `st_nci_spi_enable()`/`st_nci_spi_disable()` reset the chip and manage IRQ active state.
- `st_nci_spi_write()` sends the skb over SPI and allocates an skb from the simultaneous RX buffer to pass to `ndlc_recv()`.
- `st_nci_spi_read()` reads the 4-byte prefix and declared payload via SPI receive-only transfers.
- Probe gets reset GPIO, reads SE properties, calls `ndlc_probe()`, and registers a threaded IRQ.

## Control flow
Runtime open enables reset/IRQ through NDLC. Writes are synchronous SPI transfers; because SPI is full duplex, any MISO data received during TX is wrapped and submitted to NDLC. IRQ-triggered reads perform a two-step size/payload receive and forward complete frames to NDLC. Remove calls `ndlc_remove()`.

## State and persistence
State is reset GPIO, IRQ active flag, NDLC powered/hard-fault state, and SE presence booleans. No persistent data is written.

## Dependencies and integration points
Dependencies include SPI core, GPIO/ACPI/OF, threaded IRQs, NCI packet sizes, and NDLC. Compatible string is `st,st21nfcb-spi`; ACPI ID includes `SMO2101`.

## Risks
`st_nci_spi_write()` feeds RX bytes from every TX transaction into NDLC without validating whether they are meaningful, relying on NDLC to discard/handle them. Invalid length in `st_nci_spi_read()` sets `hard_fault = 1`, unlike I2C, producing a permanent failure latch. The stack buffer is sized for max SPI frame plus headers; future max-size changes must keep it aligned.

## Test signals
Test write full-duplex receive handling, invalid length hard fault, IRQ read while unpowered, reset timing, SE property propagation, SPI/ACPI/OF matching, and cleanup through NDLC remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/st-nci/spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/st-nci/st-nci.h -->
# sources/distributed-fs/ceph-client/drivers/nfc/st-nci/st-nci.h

## Purpose
`st-nci.h` is the shared header for ST_NCI core, NDLC, secure-element support, and vendor commands.

## Important APIs, types, and constants
- Defines runtime flags `ST_NCI_RUNNING` and `ST_NCI_FACTORY_MODE`.
- Defines proprietary core command IDs `ST_NCI_CORE_PROP` and `ST_NCI_SET_NFC_MODE`.
- `struct st_nci_se_status` carries platform-provided UICC/eSE presence.
- `struct st_nci_se_info` stores ATR, completions, timers, callback state, and SE activity flags.
- `enum nfc_vendor_cmds` enumerates ST vendor subcommands for factory mode, HCI device-management operations, firmware update, loopback, measurement, comparison, and manufacturer info.
- `struct st_nci_info` combines NDLC pointer, flags, and SE info.
- Prototypes expose core probe/remove, SE hooks, HCI callbacks, and vendor init.

## Control flow and integration
The header ties `core.c`, `se.c`, `vendor_cmds.c`, `ndlc.c`, and physical transports together. NCI ops in the core refer to SE and vendor functions declared here, while transports pass `st_nci_se_status` into NDLC/core probe.

## State and persistence
The header describes in-memory driver state. SE presence comes from firmware properties, while HCI session identity is created at runtime by `se.c`.

## Dependencies and risks
It includes `ndlc.h`, creating a mutual conceptual dependency between core and transport definitions. The vendor command enum is ABI-relevant for userspace vendor command callers; reordering would break subcommand expectations.

## Test signals
Compile all ST_NCI objects together and run vendor-command ABI tests that validate subcommand numbers, SE callback prototypes, and factory-mode flag behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/st-nci/st-nci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/st-nci/vendor_cmds.c -->
# sources/distributed-fs/ceph-client/drivers/nfc/st-nci/vendor_cmds.c

## Purpose
`vendor_cmds.c` registers ST_NCI vendor commands exposed through the NFC generic netlink vendor interface. These commands proxy HCI device-management operations, factory mode, loopback, firmware-update staging, measurements, and manufacturer-specific data.

## Important APIs, types, and functions
- `st_nci_vendor_cmds_init()` installs `st_nci_vendor_cmds` with `nci_set_vendor_cmds()`.
- Factory mode toggles `ST_NCI_FACTORY_MODE` in driver flags.
- HCI DM helpers send PUTDATA, UPDATE_AID, GETINFO, GETDATA, FWUPD_START/STOP, LOAD, RESET, FIELD_GENERATOR, VDC measurement, and VDC comparison commands to `ST_NCI_DEVICE_MGNT_GATE`.
- Reply-producing helpers allocate vendor reply skbs and attach `NFC_ATTR_VENDOR_DATA`.
- `st_nci_loopback()` uses `nci_nfcc_loopback()`.
- `st_nci_manufacturer_specific()` returns `ndev->manufact_specific_info`.

## Control flow
Userspace sends an NFC vendor command with ST OUI and a subcommand from `enum nfc_vendor_cmds`. Most handlers synchronously send an HCI command and either return the status or wrap returned data in a vendor reply. Firmware download uses a state bit in `nfc_dev`: `FWUPD_START` sets `fw_download_in_progress`, `DIRECT_LOAD` is accepted only once while the flag is set and then clears it, and `FWUPD_END` sends the stop command.

## State and persistence
State changes include factory-mode flag and `nfc_dev->fw_download_in_progress`. No persistent files are written. Vendor replies expose current chip/HCI/manufacturer data to userspace.

## Dependencies and integration points
The file depends on generic netlink attributes, NFC vendor command APIs, NCI HCI helpers, NCI loopback, and ST_NCI gate/command constants. It is initialized during `st_nci_probe()`.

## Risks
Many commands pass arbitrary userspace vendor data directly to HCI device-management commands; validation is limited to a few length checks. `st_nci_hci_dm_reset()` ignores the return from `nci_hci_send_cmd()` and always returns 0 after a fixed 200 ms sleep. Firmware direct load clears the in-progress flag before sending, so a failed load requires another start. `nci_set_vendor_cmds()` receives `sizeof(st_nci_vendor_cmds)`, matching existing kernel API expectations but worth checking if API changes.

## Test signals
Test each vendor subcommand, invalid payload lengths, vendor reply allocation failures, factory mode effect on SE discovery, firmware update sequencing start/load/end, loopback echo, manufacturer data reply, and reset behavior on HCI command failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/st-nci/vendor_cmds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/st21nfca/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/nfc/st21nfca/Kconfig

## Purpose
This Kconfig fragment defines the ST21NFCA HCI core and its I2C transport.

## Important symbols
- `NFC_ST21NFCA` is a hidden tristate core option selecting `CRC_CCITT` for HCI LLC frame CRC handling.
- `NFC_ST21NFCA_I2C` depends on `NFC_HCI && I2C && NFC_SHDLC`, selects the core, and builds `st21nfca_i2c`.

## Control flow and integration
The core is HCI-based rather than NCI-based and is used by the I2C physical layer with the SHDLC LLC. The I2C driver registers a `nfc_hci_dev` through `st21nfca_hci_probe()`.

## State, dependencies, and risks
Kconfig state is compile-time only. Missing `CRC_CCITT` would break frame validation; missing `NFC_SHDLC` would break the selected LLC path.

## Test signals
Config tests should cover dependency pruning, module and built-in builds, and that enabling I2C selects the HCI core and CRC support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/st21nfca/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/st21nfca/Makefile -->
# sources/distributed-fs/ceph-client/drivers/nfc/st21nfca/Makefile

## Purpose
This Makefile builds the ST21NFCA HCI core module and I2C transport module.

## Important build objects
- `st21nfca_hci-objs = core.o dep.o se.o vendor_cmds.o` combines HCI core logic, NFC-DEP handling, secure-element support, and vendor commands.
- `st21nfca_i2c-objs = i2c.o` builds the I2C physical layer.

## Control flow and integration
The I2C module calls exported core symbols. The core object group ensures DEP, SE, and vendor hooks are linked into the HCI device implementation.

## State, dependencies, and risks
There is no runtime state. Build risks are missing exports and mismatches between the configured LLC name in I2C and HCI core allocation.

## Test signals
Build tests should compile core-only and I2C-enabled combinations as both module and built-in, with modpost checking exported symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/st21nfca/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/st21nfca/core.c -->
# sources/distributed-fs/ceph-client/drivers/nfc/st21nfca/core.c

## Purpose
`core.c` is the HCI-based ST21NFCA NFC driver. It creates the HCI device, loads dynamic pipe sessions, configures polling/card-emulation gates, translates discovered gates into NFC targets, handles data exchange dispatch, and wires DEP, secure-element, and vendor-command helpers.

## Important APIs, types, and functions
- `st21nfca_hci_probe()` allocates `struct st21nfca_hci_info`, builds HCI init data/gates/session id, allocates/registers `nfc_hci_dev`, and initializes DEP/SE/vendor support.
- `st21nfca_hci_remove()` deinitializes DEP/SE and unregisters/frees the HCI device.
- `st21nfca_hci_load_session()` queries device-management pipe lists and maps already-open dynamic pipes into HCI tables.
- `st21nfca_hci_open()`, `st21nfca_hci_close()`, `st21nfca_hci_ready()`, and `st21nfca_hci_xmit()` implement core lifecycle.
- Polling and target helpers include `st21nfca_hci_start_poll()`, `st21nfca_hci_stop_poll()`, `st21nfca_hci_target_from_gate()`, `st21nfca_hci_complete_target_discovered()`, `st21nfca_hci_im_transceive()`, and `st21nfca_hci_check_presence()`.
- `st21nfca_hci_ops` exposes HCI, DEP, SE, and vendor-event callbacks to the NFC HCI core.

## Control flow
Probe initializes a session id `"ST21AH%2x"` from a bitmap device number, registers with protocols Jewel/MIFARE/Felica/ISO14443 A/B/ISO15693/NFC-DEP, sets a short-clear HCI quirk, then initializes submodules. Open enables the physical layer and moves state from COLD to READY. Ready programs secure-element whitelist, enables NFC mode if needed, ends any reader-A operation, and logs software version. Start poll closes unused reader gates, configures Type F datarate and polling request, starts reader-A operation for initiator protocols, and configures card-F parameters for target-mode NFC-DEP. Events are dispatched by gate to admin, DEP card-F, connectivity, APDU reader, or loopback handlers.

## State and persistence
`struct st21nfca_hci_info` stores physical ops/id, HCI device, SE status pointer, state, mutex, async callback state, DEP state, SE state, and vendor loopback state. HCI session id is persistent from the HCI core's perspective but generated from an in-memory device bitmap. No files are written.

## Dependencies and integration points
The file depends on `net/nfc/hci.h`, physical `nfc_phy_ops`, SHDLC LLC name from I2C, ST21NFCA DEP/SE/vendor helpers, and NFC target/secure-element APIs.

## Risks
The device-number bitmap is set during probe but not visibly cleared on remove, so repeated probe/remove can exhaust IDs over time. Several gate/protocol checks use gate constants as bit masks against protocol sets, which is easy to misread and should be validated against HCI core conventions. `st21nfca_get_iso15693_inventory()` pulls two bytes before checking final length and then uses `data[1]` for DSFID, so malformed short inventory responses are risky. Async callback state is shared across operations.

## Test signals
Test HCI session load with preexisting dynamic pipes, open/close state transitions, ready path NFC_MODE programming, all polling protocol combinations, target discovery for Type F/A/ISO15693, DEP link up/down, transceive routing for reader gates, presence checks, admin hot-plug events, and probe/remove ID reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/st21nfca/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/st21nfca/dep.c -->
# sources/distributed-fs/ceph-client/drivers/nfc/st21nfca/dep.c

## Purpose
`dep.c` implements NFC-DEP/NFCIP-1 handling for ST21NFCA in both target mode and initiator mode. It builds/parses ATR, PSL, and DEP request/response PDUs and bridges them to the NFC core's DEP activation/data callbacks.

## Important APIs, types, and functions
- PDU structs model ATR_REQ/RES, PSL_REQ/RES, and DEP_REQ/RES.
- Target-mode handlers receive ATR_REQ/PSL_REQ/DEP_REQ on card-F events and send ATR_RES/PSL_RES/DEP_RES.
- Initiator-mode functions `st21nfca_im_send_atr_req()` and `st21nfca_im_send_dep_req()` send reader-F exchange commands and process async responses.
- `st21nfca_dep_event_received()` dispatches card-F HCI events.
- `st21nfca_dep_init()` initializes delayed TX work and default DEP state; `st21nfca_dep_deinit()` cancels it.

## Control flow
Target mode receives card-F send-data events, distinguishes NFCIP request commands, replies to ATR_REQ using peer NFCID3/general bytes, reports activation with `nfc_tm_activated()`, handles PSL speed changes, and passes DEP payloads to `nfc_tm_data_received()`. Initiator mode sends ATR_REQ with local general bytes and target NFCID3/random fallback, waits for ATR_RES, stores remote general bytes, reports link-up, and optionally sends PSL if the remote LRI differs. DEP_REQ/RES handling maintains the current packet number information (PNI) and handles supervisor PDUs by rewrapping and resending.

## State and persistence
`struct st21nfca_dep_info` stores pending TX skb, work item, current PNI, target index, timeout, DID, bitrate, and length-reduction information. State is runtime-only and reset during init/link activation.

## Dependencies and integration points
The file depends on HCI async command/event APIs, NFC DEP target-mode and initiator callbacks, random bytes for NFCID3 fallback, and the async callback fields in `struct st21nfca_hci_info`.

## Risks
Several callbacks return early on parse errors without freeing received skbs, relying on HCI callback ownership conventions that should be verified. `st21nfca_im_recv_dep_res_cb()` uses `ST21NFCA_NFC_DEP_PFB_PNI(dep_res->pfb + 1)`, which appears suspicious because it increments the PFB before masking. Async callback fields are global to the device and can be overwritten by overlapping operations. `st21nfca_tx_work()` uses `tx_pending` without NULL checks.

## Test signals
Test ATR_REQ/RES with and without general bytes, ATR length bounds, PSL bitrate changes, DEP I-PDU/ACK/NACK/supervisor handling, PNI progression, target-mode activation, initiator link-up callback, async callback overwrite prevention, and work cancellation on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/st21nfca/dep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/st21nfca/i2c.c -->
# sources/distributed-fs/ceph-client/drivers/nfc/st21nfca/i2c.c

## Purpose
`i2c.c` is the ST21NFCA I2C physical layer and HCI LLC framing implementation. It handles enable GPIO, proprietary reboot, byte-stuffed SOF/EOF framing, CRC-CCITT, IRQ-driven multi-read receive assembly, and registration of the HCI core over SHDLC.

## Important APIs, types, and functions
- `struct st21nfca_i2c_phy` stores I2C client, HCI device, enable GPIO, SE status, pending receive skb, read sequence state, CRC retry count, power/run state, hard fault, and a bus mutex.
- `st21nfca_hci_platform_init()` sends a proprietary reboot command and waits for fill bytes.
- `st21nfca_hci_i2c_write()` adds length/CRC, SOF/EOF, byte stuffing, retries I2C writes, and restores the skb before returning.
- `st21nfca_hci_i2c_read()` reads variable chunks from `len_seq` until EOF, handles repeated SOF, and calls repack.
- `st21nfca_hci_i2c_repack()` removes byte stuffing, validates CRC, strips header/CRC, and returns the LLC payload size.
- IRQ thread reads/retries frames and calls `nfc_hci_recv_frame()`.

## Control flow
Probe allocates the physical object and pending skb, gets enable GPIO, reads SE properties, reboots the chip, registers IRQ, and calls `st21nfca_hci_probe()` with `LLC_SHDLC_NAME` and frame headroom/tailroom. On write, the NFC HCI core supplies an skb that is temporarily modified for wire encoding then restored. On IRQ, the driver accumulates chunks of 16, 24, 12, and 29 bytes until an EOF byte is seen; valid frames are delivered to HCI, incomplete frames await more IRQs, CRC errors retry a bounded number of times, and fatal errors notify HCI with NULL.

## State and persistence
Runtime state includes power/run mode, current read length index, CRC trial count, pending skb, hard-fault latch, and GPIO level. Persistent inputs are ACPI/OF properties and no data is written.

## Dependencies and integration points
The file depends on I2C, GPIO, ACPI/OF, IRQs, CRC-CCITT, firmware headers, NFC HCI/LLC/SHDLC, and the ST21NFCA core. Compatible strings include `st,st21nfca-i2c` and `st,st21nfca_i2c`; ACPI ID is `SMO2100`.

## Risks
Write mutates the caller skb while encoding and assumes `st21nfca_hci_remove_len_crc()` fully restores it. Byte unstuffing uses index arithmetic that must be robust against malformed escape-at-end frames. CRC error retry frees/reallocates pending skbs; allocation failure creates a hard fault. The protocol has no explicit length field, so sync recovery depends on SOF/EOF and fixed read sequences.

## Test signals
Test platform reboot success/failure, write byte-stuffing and CRC restoration, read chunk sequencing, repeated SOF resynchronization, CRC retry exhaustion, hard fault on I2C error/allocation failure, SE property propagation, and remove while powered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/st21nfca/i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/st21nfca/se.c -->
# sources/distributed-fs/ceph-client/drivers/nfc/st21nfca/se.c

## Purpose
`se.c` implements secure-element support for the HCI-based ST21NFCA driver. It discovers UICC/eSE presence, activates/deactivates secure elements via device-management events, handles APDU exchange through the APDU reader gate, and reports connectivity/transaction events.

## Important APIs, types, and functions
- `st21nfca_hci_discover_se()`, `st21nfca_hci_enable_se()`, `st21nfca_hci_disable_se()`, and `st21nfca_hci_se_io()` implement the HCI secure-element ops.
- `st21nfca_hci_control_se()` sends UICC/eSE activate/deactivate events, waits for hot-plug/pipe completion, and validates host-list state.
- `st21nfca_se_get_atr()` and `st21nfca_se_get_bwi()` derive APDU wait timeout from ATR.
- `st21nfca_connectivity_event_received()` reports connectivity and transaction events to NFC core.
- `st21nfca_apdu_reader_event_received()` completes APDU I/O and sends end-of-transfer.
- BWI timeout is split between timer callback and `timeout_work` to avoid doing reset work directly in timer context.

## Control flow
Discovery adds UICC/eSE entries unless factory mode is set. Enable sends the correct activation event, starts a hot-plug timer, waits for completion, validates the host list, and for eSE reads ATR then soft-resets the SE. APDU I/O stores callback context, arms BWI timer, and sends transmit-data on the APDU reader gate. Response events cancel timer/work, send end-of-transfer to device management, and call the user callback. WTX events extend the BWI timer. Timeout work alternates soft reset and hard reset, then calls the callback with `-ETIME`.

## State and persistence
`struct st21nfca_se_info` stores ATR, completion, BWI/activation timers, active flags, expected/count pipes, exchange-error toggle, callback/context, and timeout work. State is runtime-only; presence booleans come from platform properties.

## Dependencies and integration points
The file depends on NFC HCI APIs, NFC secure-element APIs, timers, workqueues, and event handlers called from `core.c`.

## Risks
Host-list scanning can read past the skb if the requested host id is absent. Error returns in transaction parsing may leave skb ownership ambiguous. APDU callbacks are stored globally per device, so concurrent APDU requests would race. Disable does not perform the eSE end-of-transfer best-effort path used by ST_NCI.

## Test signals
Test factory mode discovery suppression, UICC/eSE enable/disable success and absent-host failure, ATR/BWI parsing, APDU success and WTX extension, APDU timeout soft/hard reset alternation, end-of-transfer failure handling, and malformed transaction TLVs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/st21nfca/se.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/st21nfca/st21nfca.h -->
# sources/distributed-fs/ceph-client/drivers/nfc/st21nfca/st21nfca.h

## Purpose
`st21nfca.h` declares shared constants, state structures, and cross-file APIs for the HCI-based ST21NFCA driver.

## Important APIs, types, and constants
- Defines HCI LLC frame sizes, max payload, custom gates, eSE host id, ST OUI, factory-mode quirk bit, and device count.
- `struct st21nfca_se_status` carries platform-provided SE presence.
- `enum st21nfca_state` distinguishes COLD and READY.
- `enum nfc_vendor_cmds` defines userspace-visible vendor subcommands.
- `struct st21nfca_vendor_info`, `st21nfca_dep_info`, `st21nfca_se_info`, and `st21nfca_hci_info` store loopback, DEP, SE, and whole-device state.
- Prototypes expose HCI probe/remove, DEP helpers, SE event handlers/ops, loopback event handling, and vendor command init.

## Control flow and integration
All ST21NFCA implementation files include this header. The I2C physical layer calls the HCI probe/remove prototypes; `core.c` calls DEP/SE/vendor helpers; `dep.c`, `se.c`, and `vendor_cmds.c` access the shared `st21nfca_hci_info` state via HCI clientdata.

## State and persistence
The header models runtime state only. HCI session identity and device index are generated during probe, while platform SE presence comes from firmware properties.

## Dependencies and risks
The header depends on NFC HCI, sk_buffs, and workqueues. The vendor command enum is ABI-sensitive; changing order changes userspace subcommand numbers. `struct st21nfca_dep_info` is marked packed despite containing pointers/work_struct-like adjacent state in the parent structure, so layout changes should be made carefully.

## Test signals
Compile all users of the header and run ABI tests for vendor subcommands, frame-size bounds, and state initialization paths in DEP/SE/vendor modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/st21nfca/st21nfca.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/st21nfca/vendor_cmds.c -->
# sources/distributed-fs/ceph-client/drivers/nfc/st21nfca/vendor_cmds.c

## Purpose
`vendor_cmds.c` exposes ST21NFCA proprietary HCI commands through the NFC vendor command interface, including factory mode, pipe clearing, device-management data operations, firmware load/reset, parameter readback, field generation, and loopback.

## Important APIs, types, and functions
- `st21nfca_vendor_cmds_init()` initializes loopback completion state and registers commands with `nfc_hci_set_vendor_cmds()`.
- Factory mode toggles `ST21NFCA_FACTORY_MODE` in `hdev->quirks`.
- HCI DM handlers proxy PUTDATA, UPDATE_AID, GETINFO, GETDATA, LOAD, RESET, and FIELD_GENERATOR to `ST21NFCA_DEVICE_MGNT_GATE`.
- `st21nfca_hci_get_param()` reads an arbitrary gate/parameter pair supplied by userspace.
- `st21nfca_hci_loopback_event_received()` captures loopback response data; `st21nfca_hci_loopback()` sends a POST_DATA event and waits for completion before replying.

## Control flow
Userspace calls an ST OUI vendor subcommand. Simple commands return HCI status. Data-returning commands allocate a vendor reply skb and attach the returned payload as `NFC_ATTR_VENDOR_DATA`. Reset sends an async device-management reset, then restarts the NFC LLC. Loopback reinitializes completion, sends a loopback event, waits for an HCI event to fill `vendor_info.rx_skb`, validates length, and replies with the echoed bytes.

## State and persistence
State is runtime-only: factory-mode quirk, loopback completion, and captured loopback skb. No persistent storage is used.

## Dependencies and integration points
The file depends on generic netlink/NFC vendor command APIs, NFC HCI command/event APIs, and NFC LLC stop/start. It is initialized from `core.c` after HCI registration.

## Risks
Userspace payload validation is minimal for most HCI DM commands. Loopback waits interruptibly without a timeout, so a lost event can block the caller until interrupted. Reset restarts LLC after sending an async reset, which depends on firmware timing. Reply allocation failures must free returned HCI skbs correctly, which the code generally does.

## Test signals
Test all vendor subcommands, invalid lengths, factory-mode effect on SE discovery, GETINFO/GETDATA reply payloads, reset with LLC restart failure, loopback success/mismatch/no-event interruption, and repeated loopback cleanup of `rx_skb`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/st21nfca/vendor_cmds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/st95hf/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/nfc/st95hf/Kconfig

## Purpose
This Kconfig entry enables the ST95HF NFC transceiver driver.

## Important symbol
- `NFC_ST95HF` is a user-visible tristate titled "ST95HF NFC Transceiver driver" and depends on `SPI && NFC_DIGITAL`.

## Control flow and integration
The option builds a driver that communicates with the transceiver over SPI and registers with the NFC digital core, as described by the help text and Makefile.

## State, dependencies, and risks
Kconfig state is compile-time only. Dependency on `NFC_DIGITAL` identifies this as a digital-core driver, not NCI/HCI. Missing SPI or digital NFC support hides the option.

## Test signals
Configuration tests should verify visibility with SPI/NFC_DIGITAL enabled, pruning when either is disabled, and module/built-in builds of the corresponding Makefile objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/st95hf/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/st95hf/Makefile -->
# sources/distributed-fs/ceph-client/drivers/nfc/st95hf/Makefile

## Purpose
This Makefile maps `CONFIG_NFC_ST95HF` to the ST95HF transceiver driver objects.

## Important build objects
- `obj-$(CONFIG_NFC_ST95HF) += st95hf.o` emits the driver when enabled.
- `st95hf-objs := spi.o core.o` combines SPI transport and digital-core logic into one module/object.

## Control flow and integration
Unlike the ST_NCI and ST21NFCA families in this subset, ST95HF does not split a shared core and physical module here; SPI and core are linked into the same `st95hf` object.

## State, dependencies, and risks
There is no runtime state in the Makefile. Build correctness depends on `spi.o` and `core.o` sharing internal symbols cleanly under one module.

## Test signals
Build `CONFIG_NFC_ST95HF=y` and `m`, run modpost, and verify the linked module includes both SPI and core code paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nfc/st95hf/Makefile -->
