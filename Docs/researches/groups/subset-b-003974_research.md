# subset-b-003974 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f03.c -->
# sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f03.c

## Purpose

`rmi_f03.c` implements Synaptics RMI4 Function 03, a PS/2 pass-through function. It exposes a `SERIO_PS_PSTHRU` port so the Linux serio stack and PS/2 consumers can talk to a guest PS/2 device behind an RMI sensor. It also provides helper entry points used by GPIO button functions to overwrite and commit out-of-band trackstick button state.

## Important APIs, Types, and Functions

`struct f03_data` stores the owning `rmi_function`, allocated `serio` port, registration state, overwritten button bitmask, device count, and RX queue length. `rmi_f03_overwrite_button()` and `rmi_f03_commit_buttons()` are integration hooks for F30/F3A trackstick button emulation. `rmi_f03_pt_write()`, `rmi_f03_pt_open()`, and `rmi_f03_pt_close()` are the serio callbacks. `rmi_f03_initialize()` parses F03 query registers, while `rmi_f03_attention()` forwards RMI output-buffer bytes to `serio_interrupt()`.

## Control Flow

Probe allocates `f03_data`, reads the F03 query registers, stores it as function driver data, and defers serio registration until config. On first config, `rmi_f03_register_pt()` allocates and registers the pass-through serio port; later configs only enable the function interrupt bit. Opening the serio port drains pending output-buffer data and enables the F03 IRQ mask. Attention handling consumes transport-supplied attention data when present, otherwise reads the output buffers directly, then reports every valid byte with timeout/parity flags. Closing clears the IRQ mask, and remove unregisters the serio port.

## State and Persistence Behavior

The persistent runtime state is the devm-managed `f03_data`, the explicitly allocated serio port, and the current overwritten button bitmask. The RMI device owns the actual PS/2 TX/RX registers. IRQ enablement is tied to serio open/config state, not only probe state. Button overwrites are held in memory and emitted as `SERIO_OOB_DATA` only when committed.

## Dependencies and Integration Points

The file depends on RMI core transport helpers, the function-handler model, Linux serio, and `rmi_driver_data.attn_data`. It integrates with PS/2 consumers through `serio_register_port()`, and with F30/F3A through the exported overwrite/commit helpers declared in `rmi_driver.h`.

## Risks and Edge Cases

The query fallback for first-generation sensors hardcodes one device and queue length seven. Attention data shorter than the computed output-buffer length is ignored after warning, so packet framing from transport drivers matters. The serio port is allocated with non-devm allocation and released by `serio_unregister_port()`, so remove paths must only unregister once. OOB button commits call into the attached serio driver while RX is paused, which depends on correct serio locking behavior.

## Test Signals

Useful tests include PS/2 mouse/keyboard passthrough enumeration, writes through the serio port, open/close IRQ mask transitions, attention handling with transport-supplied and register-read data, parity/timeout flag propagation, first-generation query fallback, multiple-device warning coverage, and F30/F3A trackstick button overwrite delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f11.c -->
# sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f11.c

## Purpose

`rmi_f11.c` implements RMI4 Function 11, the legacy 2-D touch sensor function. It discovers the sensor register layout from F11 query registers, configures a shared `rmi_2d_sensor`, reads absolute or relative touch packets on attention interrupts, and reports multitouch events through the Linux input subsystem.

## Important APIs, Types, and Functions

`struct f11_2d_sensor_queries` is the parsed capability model for F11 query registers. `struct f11_2d_ctrl` stores the base control block. `struct f11_2d_data` holds pointers into the allocated packet buffer, and `struct f11_data` combines query flags, control state, IRQ masks, platform data, and the embedded `rmi_2d_sensor`. Important functions include `rmi_f11_get_query_parameters()`, `f11_2d_construct_data()`, `rmi_f11_initialize()`, `rmi_f11_finger_handler()`, `rmi_f11_attention()`, `rmi_f11_config()`, and `rmi_f11_resume()`.

## Control Flow

Probe calls `rmi_f11_initialize()`, then configures the input device through `rmi_2d_sensor_configure_input()`. Initialization reads query0, parses the variable-length per-sensor query stream, reads control registers, derives physical dimensions and max X/Y, builds packet offsets, allocates tracking/object arrays, applies platform overrides, and writes control registers back. Config toggles the absolute and relative IRQ masks separately. Attention reads either the transport-provided attention bytes or the F11 data registers, then parses finger states, absolute positions, relative deltas, optional kernel tracking, and reports an input MT frame. Resume optionally waits and issues the F11 rezero command.

## State and Persistence Behavior

The driver persists query-derived packet layout, control register shadow bytes, input tracking arrays, and IRQ masks in `f11_data`. Device state is changed by writing F11 control registers for report mode, threshold, dribble, and palm-detect settings. Runtime touch objects are ephemeral per packet. The rezero delay is persistent platform/device configuration used after resume.

## Dependencies and Integration Points

The file depends on RMI core reads/writes, OF or platform `rmi_2d_sensor_platform_data`, the shared `rmi_2d_sensor` helper layer, Linux input MT helpers, and RMI IRQ mask management. It consumes transport attention buffers through `rmi_driver_data.attn_data`.

## Risks and Edge Cases

F11 has many optional query-dependent registers, so offset accounting is the key correctness risk. Partial attention reports are processed by reducing the valid byte count, which can produce fewer fingers than expected. The code reports invalid reserved finger states but continues. The config path writes `dev_controls` to `fn->fd.query_base_addr` instead of the control base address, which is suspicious and should be regression-tested against real hardware. Gesture fields are laid out but mostly not reported. Devices with unusual optional queries may expose layout combinations this driver does not fully understand.

## Test Signals

Test signals include absolute and relative F11 devices, query combinations with gestures, touch shapes, jitter, physical properties, ACM, and info2, platform axis alignment and threshold overrides, kernel tracking on/off, reduced attention packet sizes, resume rezero behavior, IRQ mask changes, and register-write verification for control configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f11.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f12.c -->
# sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f12.c

## Purpose

`rmi_f12.c` implements RMI4 Function 12, the newer 2-D touch sensor interface. Unlike F11, F12 uses register descriptors to describe query, control, and data registers, then reports sensed objects from Data1 packets through the shared RMI 2-D sensor/input path.

## Important APIs, Types, and Functions

`enum rmi_f12_object_type` maps F12 object classifications to internal object types and MT tools. `struct f12_data` stores the embedded `rmi_2d_sensor`, platform data, register descriptors, offsets for selected Data registers, and absolute/relative IRQ masks. Important functions are `rmi_f12_read_sensor_tuning()`, `rmi_f12_process_objects()`, `rmi_f12_attention()`, `rmi_f12_write_control_regs()`, `rmi_f12_config()`, and `rmi_f12_probe()`.

## Control Flow

Probe verifies that register descriptors are present, allocates `f12_data` plus IRQ masks, reads the query/control/data descriptors, computes full data packet size, reads sensor tuning from Control8, and walks Data0 through Data15 to decide which registers are present in direct reads or HID attention reports. Data1 enables absolute reporting and sets the number of tracked objects. Tracking buffers and object arrays are allocated before `rmi_2d_sensor_configure_input()`. Config enables the absolute IRQ mask when needed, clears relative IRQs, and optionally writes the dribble bit in Control20. Attention copies transport attention bytes or reads the data registers, processes Data1 object records, and syncs the MT frame.

## State and Persistence Behavior

F12 stores descriptor-derived offsets and sizes, selected input mode, sensor dimensions, and object/tracking arrays. It persists only a small control mutation for dribble state; touch object state is rebuilt per report. `sensor->attn_size` may be smaller than full packet size when HID attention reports omit unreported descriptors.

## Dependencies and Integration Points

The file depends on RMI register descriptor helpers, RMI transport reads/writes, `rmi_2d_sensor`, Linux input MT, OF/platform sensor properties, and the shared RMI attention-data buffer. It is the main integration path for modern Synaptics RMI touchpads/touchscreens that expose Function 12.

## Risks and Edge Cases

Descriptor parsing must match the device's reported subpacket layout. `rmi_f12_process_objects()` checks available size for Data1, but uses the overall valid byte count rather than bytes remaining from `data1_offset`, which can overestimate available object bytes if preceding data is present. Relative Data9 is discovered but not reported in the attention path. The DPM resolution path divides by the read value without an explicit zero check. Dribble control assumes the enable bit is within the first three bytes of Control20.

## Test Signals

Coverage should include descriptor-present and descriptor-missing devices, HID attention versus register-read data paths, Data1 object classification for finger/stylus/palm/unclassified, truncated attention reports, Control8 tuning with DPM and pitch/receiver fallbacks, dribble on/off/default settings, and V4L/input event validation for touchscreen and touchpad platform settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f12.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f1a.c -->
# sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f1a.c

## Purpose

`rmi_f1a.c` implements RMI4 Function 1A for simple capacitive button reporting. It maps a firmware-provided button bitmask to Linux input key events using keycodes supplied through the `linux,keycodes` device property.

## Important APIs, Types, and Functions

`struct f1a_data` stores the shared input device, keymap pointer, and key count. `rmi_f1a_parse_device_properties()` reads the `linux,keycodes` property. `rmi_f1a_initialize()` registers key capabilities and installs the input keycode table. `rmi_f1a_attention()` reads the F1A data bitmask and reports each key. `rmi_f1a_config()` enables the function IRQ only when keys are configured.

## Control Flow

Probe requires the RMI core-created input device, allocates `f1a_data`, parses optional keycodes, initializes input capabilities, and stores driver data. Config sets the function IRQ mask if at least one key was configured. Attention reads one byte from the function data base address and emits `input_report_key()` for each configured key.

## State and Persistence Behavior

The keymap is devm-managed and attached to the shared input device as `input->keycode`. No hardware state is changed besides IRQ enablement. Button state is sampled on attention and not stored in the function data structure.

## Dependencies and Integration Points

The file depends on the Linux device-property API, input core, RMI reads, RMI IRQ mask management, and the shared input device in `rmi_driver_data`.

## Risks and Edge Cases

Only one byte of button state is read, so more than eight configured keycodes would not be represented correctly. If the keycode property is absent, probe succeeds with zero keys and config leaves IRQs disabled. The attention path does not call `input_sync()`, relying on surrounding RMI/input flow to sync or tolerate batched reports.

## Test Signals

Tests should cover valid, missing, empty, and malformed `linux,keycodes`; one to eight button maps; too-many key maps; IRQ enablement when `num_keys` is zero; and key press/release reporting from data-register bit changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f1a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f21.c -->
# sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f21.c

## Purpose

`rmi_f21.c` implements RMI4 Function 21 for force-click/buttonpad reporting. It reports a single force-click button as `BTN_LEFT` and marks the shared input device as a buttonpad.

## Important APIs, Types, and Functions

`struct f21_data` stores the shared input device, keycode, attention/data packet sizes and offsets, and a data buffer. `rmi_f21_initialize()` configures the input key table and `INPUT_PROP_BUTTONPAD`. `rmi_f21_probe()` derives packet sizing from function query bits. `rmi_f21_attention()` reads or consumes the button byte and reports the key.

## Control Flow

Probe requires an existing shared input device, allocates state, initializes key capabilities, then computes attention and register-read sizes from sensor count, finger-count-present, and new-report-format query bits. Config always enables the function IRQ. On attention, the handler uses transport attention data when present and advances the shared pointer, otherwise reads the full data register block. It extracts the force-click bit from the computed button offset and reports `BTN_LEFT`.

## State and Persistence Behavior

State is limited to query-derived offsets/sizes and the keycode stored in the input device. Hardware state is not modified except IRQ mask enablement. The data buffer is reused for direct register reads.

## Dependencies and Integration Points

The file integrates with RMI core reads, shared transport attention data, RMI IRQ masks, and Linux input key reporting. It also relies on the RMI core having already created `drv_data->input`.

## Risks and Edge Cases

The code tests feature bits against `fn->fd.query_base_addr` rather than a byte read from the query register, which is unusual and likely fragile unless the function descriptor has been repurposed by this source variant. Packet-size math depends on sensor and finger counts staying within fixed maxima. Attention data shorter than the computed size is ignored after a warning. No explicit `input_sync()` is issued.

## Test Signals

Useful checks include old and new report formats, devices with and without finger-count query data, transport attention and direct-read paths, press/release reporting, buttonpad property visibility, and fault injection for missing input devices or truncated attention data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f21.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f30.c -->
# sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f30.c

## Purpose

`rmi_f30.c` implements RMI4 Function 30, GPIO/LED/control support, focusing on GPIO-backed button reporting. It maps valid input GPIOs to Linux button keycodes and can route trackstick button GPIOs through F03 PS/2 out-of-band button overrides.

## Important APIs, Types, and Functions

`struct rmi_f30_ctrl_data` describes a parsed control-register block. `struct f30_data` stores query capabilities, control block layout, shadow control bytes, data bytes, keymap, shared input device, and optional F03 link. Key functions include `rmi_f30_initialize()`, `rmi_f30_set_ctrl_data()`, `rmi_f30_map_gpios()`, `rmi_f30_config()`, `rmi_f30_attention()`, and `rmi_f30_report_button()`.

## Control Flow

Probe exits early if platform GPIO data disables F30, requires the shared input device, allocates state, reads F30 queries, computes present control-register blocks, reads the control shadow, maps valid GPIO inputs to keycodes, and stores driver data. Config re-finds F03 when trackstick buttons are enabled, writes the control shadow back unless disabled, and enables or clears the IRQ mask. Attention consumes transport data or reads data registers, reports each mapped active-low GPIO button, and commits F03 OOB buttons when trackstick routing is active.

## State and Persistence Behavior

F30 persists query flags, register counts, control shadow bytes, keymap, and optional F03 linkage. The control shadow is written back on config, preserving or reapplying hardware GPIO/LED configuration. Button state is sampled per attention and not otherwise retained.

## Dependencies and Integration Points

The file depends on RMI core reads/writes, platform `gpio_data`, the shared input device, RMI IRQ masks, and F03 helper functions for trackstick passthrough. It also uses Linux input properties to mark buttonpads.

## Risks and Edge Cases

The keymap allocation uses `min(gpioled_count, TRACKSTICK_RANGE_END)` but later sets `keycodemax` to `gpioled_count` and loops to `gpioled_count`, which can index past the allocated map when more than six GPIO/LEDs exist. Control-block offset computation must match the query flags exactly. Trackstick routing only establishes if F03 is present by config time. Active-low interpretation may not match every board wiring.

## Test Signals

Tests should include GPIO-only, LED-only, combined GPIO/LED, haptic, mappable, and mechanical-button capability combinations; devices with more than six GPIOs; buttonpad and non-buttonpad mappings; trackstick-with-F03 and trackstick-without-F03 paths; control writeback failures; and attention packets from both transport and register reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f30.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f34.c -->
# sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f34.c

## Purpose

`rmi_f34.c` implements common and bootloader-v5 support for RMI4 Function 34 firmware flashing. It exposes sysfs attributes for bootloader ID, configuration ID, firmware update trigger, and update status, coordinates full device reprobe around flash mode entry, and delegates bootloader-v7-or-newer flashing to `rmi_f34v7.c`.

## Important APIs, Types, and Functions

Important functions include `rmi_f34_command()`, `rmi_f34_attention()`, `rmi_f34_write_blocks()`, `rmi_f34_flash_firmware()`, `rmi_f34_update_firmware()`, `rmi_firmware_update()`, `rmi_driver_update_fw_store()`, `rmi_f34v5_probe()`, `rmi_f34_probe()`, `rmi_f34_create_sysfs()`, and `rmi_f34_remove_sysfs()`. The file uses `struct f34_data` and v5 fields declared in `rmi_f34.h`.

## Control Flow

Probe allocates `f34_data` and selects v5 or v7 probing based on function version. The sysfs `update_fw` store callback requests a firmware file, then `rmi_firmware_update()` validates F34 availability and bootloader support. It enters flash mode, disables IRQs, frees and reprobes functions so the device is represented in bootloader mode, performs the v5 or v7 reflash, then resets/scans/reinitializes functions and re-enables the sensor. V5 flashing writes the bootloader ID when required, issues erase/write commands, and waits for completion signaled by `rmi_f34_attention()`.

## State and Persistence Behavior

`f34_data` persists bootloader/configuration IDs, update status/progress/size, command completions, and v5 geometry such as block size and block counts. During firmware update, the broader RMI function list is intentionally torn down and rebuilt. Hardware flash contents are persistent and modified by erase/write commands. Sysfs status reports percent progress or a final return code.

## Dependencies and Integration Points

The file depends on firmware loading, RMI scan/probe/init/reset helpers, RMI IRQ control, sysfs, completions, mutex guards, unaligned little-endian helpers, and the v7 helper API in `rmi_f34.h`. It integrates with the RMI core through `data->f34_container`, `bootloader_mode`, and function handler attention callbacks.

## Risks and Edge Cases

Firmware updates are high-risk because they intentionally erase persistent device flash. Correct block-size validation is essential. Failure after entering bootloader mode but before final reprobe can leave the device in an unusable state until reset or retry. Completion waits depend on F34 IRQ delivery after masks are configured. The sysfs update path is synchronous and can block for erase/write time. Reprobe failures after a successful flash still return errors to userspace.

## Test Signals

Tests should cover v5 image/config size validation, config-only and firmware-plus-config updates, unsupported bootloader versions, missing F34, firmware request failures, command timeout/error status, update status progression, IRQ disable/enable sequencing, successful post-flash reset/reprobe, and sysfs attribute creation/removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f34.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f34.h -->
# sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f34.h

## Purpose

`rmi_f34.h` is the shared Function 34 firmware-update contract for v5 and v7 bootloader code. It defines command constants, register offsets, timeouts, firmware image structures, v7 partition/container identifiers, metadata structures, and the common `struct f34_data` state passed between `rmi_f34.c` and `rmi_f34v7.c`.

## Important APIs, Types, and Functions

The header defines v5 commands such as `F34_WRITE_FW_BLOCK`, `F34_ERASE_ALL`, and `F34_ENABLE_FLASH_PROG`; v7 data offsets and logical commands; partition IDs; image container IDs; packed register/image structures including `f34v7_query_1_7`, `f34v7_data_1_5`, `partition_table`, `container_descriptor`, `image_header_10`, and `rmi_f34_firmware`; metadata containers such as `image_metadata`, `block_count`, and `physical_address`; and exported functions `rmi_f34v7_start_reflash()`, `rmi_f34v7_do_reflash()`, and `rmi_f34v7_probe()`.

## Control Flow

This file has no runtime control flow. Its structures and constants are consumed by probe, sysfs update, command, image parsing, partition-table reading, erase, read, and write routines in the F34 implementation files. Packed structures describe the bytes read from RMI registers and firmware files.

## State and Persistence Behavior

The header defines all persistent in-memory flashing state. V5 state includes block geometry, control address, command completion, and flash mutex. V7 state includes bootloader mode, command/status, block and payload geometry, partition table data, image metadata, read/config buffers, and command completion. `f34_data` additionally persists user-visible update status and IDs.

## Dependencies and Integration Points

The header depends on kernel fixed-width types, endian types, `BIT()`, RMI function declarations, and firmware structures. It is included by both F34 implementation files and bridges sysfs-triggered update logic with v7 image parsing and flashing internals.

## Risks and Edge Cases

Packed layout and little-endian fields must match Synaptics firmware formats exactly. Several v7 names intentionally preserve historical casing and command naming. Incorrect constants can erase or write the wrong partition. `CONFIG_ID_SIZE` and product ID sizes shape sysfs-visible buffers, so off-by-one errors would leak or truncate identifiers. Structure changes require coordinated updates to both v5 and v7 code.

## Test Signals

Useful checks include compile coverage of both F34 implementation files, static assertions for important image offsets and packed sizes, parsing known v5/v7 firmware images, partition ID mapping tests, and build tests on big- and little-endian architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f34.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f34v7.c -->
# sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f34v7.c

## Purpose

`rmi_f34v7.c` implements RMI4 Function 34 bootloader v7 and newer firmware flashing. It parses v10 containerized firmware images, reads the device partition table, validates image partition sizes, enters bootloader mode, erases application partitions, rewrites the partition table/config, and writes firmware, UI config, display config, and guest code blocks.

## Important APIs, Types, and Functions

Key functions include `rmi_f34v7_read_flash_status()`, `rmi_f34v7_check_command_status()`, `rmi_f34v7_write_command()`, `rmi_f34v7_write_partition_id()`, `rmi_f34v7_read_partition_table()`, `rmi_f34v7_parse_partition_table()`, `rmi_f34v7_read_queries()`, `rmi_f34v7_read_blocks()`, `rmi_f34v7_write_f34v7_blocks()`, `rmi_f34v7_write_partition_table()`, `rmi_f34v7_parse_image_header_10()`, `rmi_f34v7_parse_image_info()`, `rmi_f34v7_start_reflash()`, `rmi_f34v7_do_reflash()`, and `rmi_f34v7_probe()`.

## Control Flow

Probe reads the bootloader ID, determines the bootloader version, initializes completions, and reads v7 queries plus the current partition table. Starting a reflash parses the image and enters flash programming mode if not already in bootloader mode. The main reflash path enables F34 interrupts, refreshes bootloader version, parses image metadata, validates bootloader config size, erases application partitions, writes flash/bootloader config and partition table data, resets/scans PDT to reload the partition table, then writes firmware, UI config, optional display config, and optional guest code. Block transfers program partition ID, block number, transfer length, command, payload, then wait for idle status.

## State and Persistence Behavior

The v7 substructure of `f34_data` persists flash status, command, bootloader-mode flag, geometry, partition counts, device partition table, image metadata, read/config buffers, and progress accounting. Hardware flash partitions are persistent and are erased/reprogrammed. Completion state is reinitialized for each command, and command completion is normally driven by F34 attention.

## Dependencies and Integration Points

The file depends on RMI block reads/writes, completions, jiffies/timeouts, unaligned little-endian helpers, firmware image memory, and the common F34 sysfs/update orchestration. It also calls `rmi_scan_pdt()` during the v7 sequence after partition-table programming.

## Risks and Edge Cases

Image parsing trusts container offsets and lengths from firmware data; malformed images can point outside the firmware buffer unless higher layers guarantee validity. `rmi_f34v7_read_partition_table()` has a polling loop comparing a timeout value directly to `jiffies` rather than adding it to the current time, which can make the loop ineffective after boot. `rmi_f34v7_write_partition_id()` can leave `partition` unset if `config_area` is invalid. Progress counts blocks in some paths and bytes in v5, so user-visible percentages should be verified. Any interruption after erase can leave the device in bootloader mode.

## Test Signals

Tests should include known-good v10 images, malformed container offsets, missing flash config, unsupported header versions, each optional partition combination, bootloader entry from UI and already-bootloader modes, command timeout/status errors, block transfer chunking by payload length and page size, post-partition-table reset behavior, and full reflash recovery after injected failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f34v7.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f3a.c -->
# sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f3a.c

## Purpose

`rmi_f3a.c` implements RMI4 Function 3A GPIO button reporting. It reads GPIO existence and direction data, maps valid input GPIOs to button keycodes, reports active-low button states, and optionally routes trackstick buttons through F03 PS/2 out-of-band button emulation.

## Important APIs, Types, and Functions

`struct f3a_data` stores GPIO count, register count, data bytes, key map, shared input device, optional F03 pointer, and trackstick state. Important functions include `rmi_f3a_initialize()`, `rmi_f3a_map_gpios()`, `rmi_f3a_is_valid_button()`, `rmi_f3a_config()`, `rmi_f3a_attention()`, and `rmi_f3a_report_button()`.

## Control Flow

Probe requires the shared input device, allocates state, reads the general query byte, computes register count, reads Query1 GPIO-existence bits and Control1 direction bits, maps valid input GPIOs to `BTN_LEFT` and subsequent buttons, and stores driver data. Config optionally finds Function 03 for trackstick routing and enables the IRQ mask. Attention consumes transport attention data or reads the data registers, reports every mapped button, and commits F03 OOB button state if trackstick mode is active.

## State and Persistence Behavior

The function stores query-derived GPIO/register counts, key mapping, latest data-register bytes, and optional F03 linkage. It does not change hardware GPIO configuration. Input keymap and buttonpad property persist on the shared input device.

## Dependencies and Integration Points

The file depends on RMI reads, platform `gpio_data`, shared RMI attention data, Linux input, RMI IRQ masks, and F03 helper functions for trackstick button routing.

## Risks and Edge Cases

The keymap allocation is capped at `TRACKSTICK_RANGE_END`, while `gpio_count` and the reporting loop may be larger, creating possible out-of-bounds accesses on devices with more than six GPIOs. `rmi_f3a_report_button()` reads only `data_regs[0]`, so buttons beyond the first eight GPIOs are not decoded correctly. Trackstick F03 linkage may be absent at config time. Active-low assumptions may not fit all boards.

## Test Signals

Coverage should include different GPIO counts, GPIOs configured as outputs versus inputs, more-than-six and more-than-eight GPIO cases, buttonpad mapping, trackstick routing with and without F03, transport attention and direct-read paths, and active-low press/release event validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f3a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f54.c -->
# sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f54.c

## Purpose

`rmi_f54.c` implements RMI4 Function 54 diagnostics as a V4L2 touch video device. It exposes sensor image reports such as normalized delta images, raw capacitance, baseline, and full raw reports through videobuf2 capture/read/mmap interfaces.

## Important APIs, Types, and Functions

`enum rmi_f54_report_type` lists supported report IDs. `struct f54_data` stores sensor geometry, capabilities, report buffers, busy/completion state, delayed work, V4L2 objects, vb2 queue, and input/report map. Important functions include `is_f54_report_type_valid()`, `rmi_f54_create_input_map()`, `rmi_f54_request_report()`, `rmi_f54_get_report_size()`, `rmi_f54_buffer_queue()`, `rmi_f54_work()`, V4L2 ioctl handlers, `rmi_f54_detect()`, `rmi_f54_probe()`, and `rmi_f54_remove()`.

## Control Flow

Probe reads F54 query properties, allocates a maximum u16 report buffer, creates a workqueue, builds the V4L2 input map, selects the first valid input, registers a V4L2 device, initializes a vmalloc vb2 queue, and registers a touch video device. Config clears the F54 IRQ bit because the driver polls command completion. Queueing a vb2 buffer requests a report, waits for the delayed work to complete it, copies report data into the buffer, and marks the buffer done or error. The work item polls the command register until `GET_REPORT` clears, then reads report data from the FIFO in 32-byte chunks.

## State and Persistence Behavior

The driver persists selected report type, V4L2 input/format, report buffer, sequence number, busy flag, timeout, and workqueue. Hardware state changes include writing report type, issuing `GET_REPORT`, setting FIFO offsets, and disabling F54 interrupts. Report data persists in memory until overwritten by the next capture.

## Dependencies and Integration Points

The file depends on RMI transport reads/writes, V4L2 core, videobuf2 vmalloc memory ops, Linux media touch pixel formats, workqueues, completions, and electrode counts from F55 via `rmi_driver_data` when available.

## Risks and Edge Cases

The polling path must avoid leaving `is_busy` stuck after errors. `rmi_f54_set_input()` uses u16-sized `bytesperline` and `sizeimage` for all formats, while 8-bit reports have a smaller actual payload. Report data is read in 32-byte chunks for SMBus compatibility. Workqueue removal destroys the queue but does not explicitly cancel delayed work on the normal remove path before destroy. Concurrent V4L2 input changes and queued buffers rely on the queue lock/status mutex behavior.

## Test Signals

Tests should cover V4L2 enumeration, each supported report type, 8-bit and 16-bit payload sizes, buffer queue/read/mmap/poll paths, command timeout injection, FIFO chunk reads over SMBus, electrode count override from F55, stream stop sequence reset, remove while idle and while work is pending, and media-device userspace tools such as `v4l2-ctl`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f54.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f55.c -->
# sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f55.c

## Purpose

`rmi_f55.c` implements RMI4 Function 55 sensor-electrode assignment discovery. It reads RX/TX electrode counts and, when sensor assignment is supported, counts enabled receive/transmit electrodes so other functions can size diagnostic data correctly.

## Important APIs, Types, and Functions

`struct f55_data` stores raw query bytes and raw/configured RX/TX electrode counts. `rmi_f55_detect()` reads F55 query registers, updates `rmi_driver_data->num_rx_electrodes` and `num_tx_electrodes`, and optionally reads control assignment tables. `rmi_f55_probe()` allocates state and runs detection.

## Control Flow

Probe allocates `f55_data`, stores it on the function device, and calls detect. Detect reads three query bytes, records raw RX/TX counts, initializes configured counts, and publishes them to the RMI driver data. If the physical-characteristics byte advertises sensor assignment, it reads F55 Control1 and Control2 assignment arrays, counts entries not equal to `0xff`, and publishes those enabled counts instead.

## State and Persistence Behavior

F55 persists only discovered geometry in its own state and in shared `rmi_driver_data`. It does not modify hardware. The shared counts persist for later consumers such as F54 report sizing.

## Dependencies and Integration Points

The file depends on RMI block reads, RMI function driver data, and the shared `rmi_driver_data` geometry fields. It integrates most directly with F54 diagnostics, which consults shared electrode counts before falling back to F54 query counts.

## Risks and Edge Cases

The code assigns `cfg_num_tx_electrodes` and `drv_data->num_tx_electrodes` from `num_rx_electrodes` in the default path, which appears wrong for asymmetric sensors. Assignment-table read errors are ignored after the query succeeds, leaving default counts. Fixed `u8 buf[256]` assumes electrode counts fit in one byte-sized table.

## Test Signals

Useful checks include symmetric and asymmetric RX/TX devices, assignment-present and assignment-absent devices, assignment tables containing `0xff` holes, control-read failures, and downstream F54 report sizing with and without F55 data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_f55.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_i2c.c

## Purpose

`rmi_i2c.c` implements the I2C transport adapter for RMI4 devices. It maps RMI 16-bit register reads/writes onto I2C transfers using the RMI page-select register, handles regulators and startup delay, and registers an `rmi_transport_dev` with the RMI core.

## Important APIs, Types, and Functions

`struct rmi_i2c_xport` stores the transport, I2C client, page mutex/current page, reusable transmit buffer, regulators, and startup delay. `rmi_set_page()` writes the page-select register. `rmi_i2c_write_block()` and `rmi_i2c_read_block()` implement `rmi_transport_ops`. `rmi_i2c_probe()` powers and registers the transport, while suspend/resume hooks coordinate RMI driver suspend/resume with regulator disable/enable.

## Control Flow

Probe allocates transport state, copies platform data when present, checks I2C functionality, gets/enables `vdd` and `vio`, registers a cleanup action, reads optional `syna,startup-delay-ms`, initializes the page mutex and transport ops, forces page zero, and calls `rmi_register_transport_device()`. Reads and writes lock the page mutex, switch pages when needed, then issue native I2C transfers. System and runtime suspend call into the RMI driver then disable regulators; resume enables regulators, waits startup delay, and resumes the RMI driver.

## State and Persistence Behavior

The transport persists the current RMI page and a growable devm-managed TX buffer. Regulator enablement is runtime power state. The registered `rmi_transport_dev` persists until devm cleanup unregisters it.

## Dependencies and Integration Points

The file depends on I2C core, regulator framework, OF matching, RMI core transport registration, and PM helper macros. It supplies the `read_block` and `write_block` backend used by all RMI functions over I2C.

## Risks and Edge Cases

Every read/write depends on correct page tracking under `page_mutex`. Large writes reallocate the TX buffer and use devm allocation/free during runtime operations. Suspend warning messages say "resume" in some error paths. Runtime suspend returns zero even if `rmi_driver_suspend()` fails, after disabling regulators. Devices without both regulators must rely on regulator framework dummy supplies or fail probe.

## Test Signals

Tests should include page-crossing reads/writes, large write buffer growth, regulator failure and cleanup, startup delay behavior, system and runtime PM, OF and platform-data probe paths, I2C short transfer error handling, and full RMI enumeration over I2C.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_smbus.c -->
# sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_smbus.c

## Purpose

`rmi_smbus.c` implements the SMBus transport adapter for RMI4 touchpads, especially devices sharing PS/2 and SMBus behavior. It maps RMI register addresses to SMBus command codes through the SMBus v2 mapping table and registers the resulting transport with the RMI core.

## Important APIs, Types, and Functions

`struct mapping_table_entry` is the on-device 4-byte address/readcount/write-enable mapping entry. `struct rmi_smb_xport` stores the transport, I2C client, mapping table state, table index, and mutexes. Key functions include `rmi_smb_get_version()`, `rmi_smb_get_command_code()`, `rmi_smb_write_block()`, `rmi_smb_read_block()`, `rmi_smb_clear_state()`, `rmi_smb_enable_smbus_mode()`, `rmi_smb_reset()`, probe/remove, and PM callbacks.

## Control Flow

Probe requires platform data, SMBus block-read and host-notify functionality, and a valid IRQ. It allocates state, initializes locks, copies platform data, enables SMBus mode by reading the protocol version, then registers the transport. Reads and writes lock `page_mutex`, split transfers into up to 32-byte chunks, acquire or install a command-code mapping under `mappingtable_mutex`, then issue SMBus block transfers. Reset clears the local mapping table and re-enables SMBus mode without issuing an RMI reset command. Resume resets SMBus mapping, calls `rmi_reset()`, then resumes the RMI driver.

## State and Persistence Behavior

The transport persists a local mirror of the eight-entry SMBus mapping table and a round-robin replacement index. On reset, the mapping table is discarded. Runtime hardware state includes the device's command mapping table and SMBus mode activation.

## Dependencies and Integration Points

The file depends on I2C/SMBus APIs, platform RMI data, PM helpers, RMI transport registration, and RMI reset/suspend/resume helpers. It integrates with systems where PS/2 reset sequencing owns the physical reset and SMBus must avoid racing it.

## Risks and Edge Cases

The write loop computes `block_len` from total `len` instead of remaining `cur_len`, so final partial writes can be oversized when `len > 32` and not a multiple of 32. Read return length from `i2c_smbus_read_block_data()` is not checked against the requested length. The mapping table is only eight entries, so churn can hurt performance or expose stale mapping behavior if device writes fail. Probe cannot use firmware/OF data alone because it requires platform data.

## Test Signals

Tests should cover SMBus protocol versions 2 and 3, invalid versions, reads/writes at different RMI addresses and lengths, multi-chunk and final-partial writes, mapping-table reuse and wraparound, reset/resume clearing mappings, missing IRQ/platform data failures, and host-notify interrupt-driven RMI operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_smbus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_spi.c -->
# sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_spi.c

## Purpose

`rmi_spi.c` implements the SPI transport adapter for RMI4 devices. It converts RMI read/write requests into SPI messages, handles page selection for RMI addressing, supports optional per-byte transfer delays, and registers an RMI transport device.

## Important APIs, Types, and Functions

`enum rmi_spi_op` and `struct rmi_spi_cmd` describe SPI command variants. `struct rmi_spi_xport` stores the transport, SPI device, page state, DMA-capable TX/RX buffers, and transfer arrays. `rmi_spi_manage_pools()` sizes buffers and transfer pools. `rmi_spi_xfer()` builds and submits SPI messages. `rmi_set_page()`, `rmi_spi_write_block()`, and `rmi_spi_read_block()` implement the RMI transport. Probe and PM hooks register and suspend/resume the transport.

## Control Flow

Probe rejects half-duplex controllers, allocates state, reads OF or platform SPI timing/mode data, applies bits-per-word/mode, calls `spi_setup()`, initializes transport ops, allocates default pools, sets page zero, and registers the transport with devm cleanup. Reads and writes lock the page mutex, change pages when needed, then call `rmi_spi_xfer()` with two-byte legacy read/write commands. `rmi_spi_xfer()` allocates larger pools as needed, prepares command bytes and data bytes, optionally splits transfers into one-byte entries with configured delays, calls `spi_sync()`, and copies received data out.

## State and Persistence Behavior

The transport persists current page, reusable DMA-capable buffers, transfer arrays, and platform timing/mode settings. The RMI transport registration persists until devm cleanup. No device configuration is persistent beyond page-select state and normal RMI register operations.

## Dependencies and Integration Points

The file depends on SPI core, OF matching/properties, RMI transport registration, RMI PM helpers, and platform `rmi_device_platform_data_spi`. It provides the backend used by all RMI function drivers over SPI.

## Risks and Edge Cases

`rmi_set_page()` updates `rmi_spi->page` when `ret` is nonzero, which appears inverted and can desynchronize page tracking after failed page writes. `RMI_SPI_PAGE(addr)` masks with `0x80`, not the full high byte, so only a limited page bit is tracked. Transfer length is capped at 255 bytes; higher layers must chunk larger accesses. V2 command opcodes are enumerated but not implemented for reads. Runtime suspend returns zero even when driver suspend fails.

## Test Signals

Tests should include page switching, failed page-select writes, max-length transfers and over-limit errors, per-byte read/write delay modes, OF and platform-data probe, half-duplex rejection, system/runtime PM, SPI short/error injection, and full RMI enumeration over SPI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/rmi4/rmi_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/input/serio/Kconfig

## Purpose

`drivers/input/serio/Kconfig` defines the build-time configuration menu for the Linux serio subsystem and its controller/user drivers. It controls whether the core serio bus and individual PS/2, serial, platform, raw, and userspace serio drivers are built in, built as modules, or excluded.

## Important APIs, Types, and Functions

The main symbol is `SERIO`, a tristate defaulting to `y`. The file also defines architecture gate `ARCH_MIGHT_HAVE_PC_SERIO` and driver symbols such as `SERIO_I8042`, `SERIO_SERPORT`, `SERIO_AMBAKMI`, `SERIO_GSCPS2`, `SERIO_LIBPS2`, `SERIO_RAW`, `SERIO_ALTERA_PS2`, `SERIO_AMS_DELTA`, `SERIO_ARC_PS2`, `SERIO_APBPS2`, `SERIO_GPIO_PS2`, and `USERIO`.

## Control Flow

There is no runtime flow. Kconfig evaluates dependencies and defaults, emits selected symbols into `.config`, and Kbuild uses those symbols in the serio Makefile to include or omit object files. All individual driver choices are nested under `if SERIO`, so disabling `SERIO` removes the submenu.

## State and Persistence Behavior

The file persists build configuration state through `.config`. That state determines the available serio bus core and driver modules. It does not create runtime state.

## Dependencies and Integration Points

The symbols integrate serio with architecture support, TTY, PARPORT, AMBA, SA1111, GSC/HP300, PCI, SGI, OF, HAS_IOMEM, Hyper-V, GPIOLIB, and platform-specific machine symbols. Module names in help text match Makefile object targets.

## Risks and Edge Cases

Dependency drift can leave a driver visible without required infrastructure or hidden when compile-test coverage would be useful. Some defaults are architecture-specific and can surprise minimal configurations. Help text references older documentation paths and platform names, so user guidance can lag code movement.

## Test Signals

Build matrix checks should cover `SERIO=y/m/n`, each requested driver symbol as built-in and module where dependencies allow, dependency-disabled visibility, randconfig coverage, and Makefile object emission matching the configured symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/Makefile -->
# sources/distributed-fs/ceph-client/drivers/input/serio/Makefile

## Purpose

`drivers/input/serio/Makefile` maps Kconfig symbols to serio subsystem object files. It tells Kbuild which source files compose the core serio bus and each optional serio driver.

## Important APIs, Types, and Functions

The file uses `obj-$(CONFIG_...) += ...` entries. `CONFIG_SERIO` builds `serio.o`; individual symbols map to drivers such as `i8042.o`, `serport.o`, `ambakmi.o`, `gscps2.o`, `libps2.o`, `altera_ps2.o`, `ams_delta_serio.o`, `arc_ps2.o`, `apbps2.o`, `ps2-gpio.o`, and `userio.o`. `CONFIG_HIL_MLC` builds two objects: `hp_sdc_mlc.o` and `hil_mlc.o`.

## Control Flow

There is no runtime control flow. Kbuild evaluates each `CONFIG_*` value. Enabled built-in symbols link the objects into the kernel; module symbols build `.ko` modules; disabled symbols omit objects.

## State and Persistence Behavior

The file affects build artifacts only. It does not persist runtime driver state. The object list is persistent build metadata that must stay synchronized with Kconfig and source filenames.

## Dependencies and Integration Points

The Makefile integrates the serio directory with the kernel build system and the Kconfig symbols declared beside it. It is the link between user-visible configuration choices and compiled driver code.

## Risks and Edge Cases

Adding or renaming a driver without updating this file causes missing modules or build failures. Multi-object symbol entries such as `CONFIG_HIL_MLC` need special attention. Mismatches between Kconfig module names and Makefile targets confuse users and packaging.

## Test Signals

Tests include `make M=drivers/input/serio`, allmodconfig/allnoconfig/randconfig builds, module-name checks for each help-text module, and build failures after source renames or Kconfig symbol changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/altera_ps2.c -->
# sources/distributed-fs/ceph-client/drivers/input/serio/altera_ps2.c

## Purpose

`altera_ps2.c` implements a serio driver for the Altera University Program PS/2 controller. It exposes the memory-mapped PS/2 port as a `SERIO_8042` port for standard keyboard and mouse consumers.

## Important APIs, Types, and Functions

`struct ps2if` stores the serio port and mapped register base. `altera_ps2_rxint()` drains received bytes on interrupt. `altera_ps2_write()`, `altera_ps2_open()`, and `altera_ps2_close()` are serio callbacks. `altera_ps2_probe()` maps resources, requests IRQ, allocates/registers the serio port, and `altera_ps2_remove()` unregisters it. OF compatibles include `ALTR,ps2-1.0` and `altr,ps2-1.0`.

## Control Flow

Probe allocates private state, maps the first memory resource, gets and requests the IRQ, allocates a serio port, assigns callbacks and device metadata, registers the port, and stores driver data. Opening drains pending FIFO data by reading while status high bits indicate data, then writes to the control register to enable RX IRQs. Interrupt handling loops while data/status indicate pending RX and reports the low byte to serio. Closing disables RX IRQs.

## State and Persistence Behavior

Persistent state is the mapped register base and serio port pointer. Hardware state includes the RX interrupt enable bit in the controller control register. Received bytes are not buffered by the driver beyond the interrupt loop.

## Dependencies and Integration Points

The file depends on platform devices, devm MMIO resource mapping, IRQ handling, OF matching, and the serio core. It integrates with standard `atkbd`/`psmouse` consumers through the `SERIO_8042` port.

## Risks and Edge Cases

The status interpretation assumes upper 16 bits indicate RX data availability. Writes do not check TX readiness or errors. The open FIFO drain discards bytes without reporting flags. Serio allocation is not devm-managed but is released by `serio_unregister_port()`.

## Test Signals

Tests should cover OF and platform probe, IRQ receive, open/close interrupt enablement, write behavior under busy hardware, remove cleanup, and standard keyboard/mouse detection through serio.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/altera_ps2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/ambakmi.c -->
# sources/distributed-fs/ceph-client/drivers/input/serio/ambakmi.c

## Purpose

`ambakmi.c` implements the ARM AMBA PL050 KMI keyboard/mouse interface as a serio controller. It exposes the KMI hardware as a `SERIO_8042` port and handles clocking, IRQ-driven RX, and byte writes.

## Important APIs, Types, and Functions

`struct amba_kmi_port` stores the serio port, clock, MMIO base, IRQ, divisor, and open flag. `amba_kmi_int()` drains RX interrupts. `amba_kmi_write()`, `amba_kmi_open()`, and `amba_kmi_close()` are serio callbacks. `amba_kmi_probe()` claims AMBA resources, maps registers, gets the KMI clock, and registers the serio port. `amba_kmi_resume()` asks serio to reconnect after system resume.

## Control Flow

Probe requests AMBA regions, allocates private state and serio port, maps registers, gets `KMIREFCLK`, stores IRQ, and registers serio. Opening enables the clock, programs the clock divisor from clock rate, enables the controller, requests the shared IRQ, then enables RX interrupts. Interrupt handling reads KMIDATA while RX interrupt is asserted and reports bytes to serio. Writes busy-wait for TX empty before writing data. Close disables the controller, frees IRQ, and disables the clock.

## State and Persistence Behavior

Persistent state includes the mapped base, clock handle, IRQ, and serio port. Hardware state includes clock enablement, divisor, controller enable, and RX interrupt enable while open. Resume does not restore registers directly; it triggers serio reconnect.

## Dependencies and Integration Points

The driver depends on AMBA bus matching, PL050 register definitions, clock framework, IRQ handling, MMIO accessors, and serio core. It integrates with standard PS/2 protocol drivers via `SERIO_8042`.

## Risks and Edge Cases

Clock divisor calculation assumes a usable clock rate at or above 8 MHz. IRQ is requested on every open and freed on close, so open/close races rely on serio serialization. Write timeout returns `SERIO_TIMEOUT`, not a negative errno. Probe cleanup must release both AMBA regions and separately allocated objects.

## Test Signals

Coverage should include probe/remove, clock enable failure, IRQ request failure, receive interrupt draining, TX timeout, close cleanup, system resume reconnect, and keyboard/mouse operation on PL050 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/ambakmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/ams_delta_serio.c -->
# sources/distributed-fs/ceph-client/drivers/input/serio/ams_delta_serio.c

## Purpose

`ams_delta_serio.c` implements the Amstrad Delta/E3 mailboard keyboard serio adapter. The actual PS/2-like bit capture is done by a platform FIQ handler; this driver drains the FIQ circular buffer, validates frame/parity bits, and feeds scancodes to serio.

## Important APIs, Types, and Functions

`struct ams_delta_serio` stores the serio port, keyboard regulator, and FIQ buffer pointer. `check_data()` validates stop bit and odd parity. `ams_delta_serio_interrupt()` drains the FIQ circular buffer and reports scancodes. `ams_delta_serio_open()` and `ams_delta_serio_close()` enable/disable keyboard power. Probe is `ams_delta_serio_init()` and remove is `ams_delta_serio_exit()`.

## Control Flow

Probe allocates state, obtains the FIQ buffer from platform data, gets the `vcc` regulator, requests the platform IRQ, allocates a `SERIO_8042` port, assigns callbacks, registers it, and stores driver data. Opening enables the regulator. The IRQ handler clears the pending flag, drains words from the circular buffer using head/count metadata, validates each word, extracts the data byte, and calls `serio_interrupt()`. Closing disables the regulator, and remove unregisters the serio port.

## State and Persistence Behavior

Persistent state is the regulator, FIQ shared buffer pointer, and serio port. The circular buffer state lives in platform/FIQ memory and is mutated by both the FIQ producer and this IRQ consumer. Keyboard power state follows serio open/close.

## Dependencies and Integration Points

The file depends on Amstrad Delta FIQ platform data definitions, platform IRQs, regulator framework, and serio. It integrates with `atkbd` as a normal AT keyboard port, with userspace expected to load a custom keymap for the mailboard.

## Risks and Edge Cases

The FIQ buffer is shared memory with implicit synchronization through platform conventions. Regulator lookup converts `-ENODEV` to `-EPROBE_DEFER` to allow board constraints to settle. Bad frame/parity data is still reported with serio error flags. A missing platform buffer aborts probe.

## Test Signals

Tests should include valid scancode delivery, invalid stop bit and parity reporting, circular-buffer wraparound, regulator enable/disable, deferred regulator probing, missing platform data failure, and custom keymap operation on E3 mailboard hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/ams_delta_serio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/apbps2.c -->
# sources/distributed-fs/ceph-client/drivers/input/serio/apbps2.c

## Purpose

`apbps2.c` implements a serio driver for the GRLIB APBPS2 PS/2 controller. It exposes the big-endian MMIO APBPS2 core as a `SERIO_8042` port for keyboard or mouse devices.

## Important APIs, Types, and Functions

`struct apbps2_regs` describes the data/status/control/reload registers. `struct apbps2_priv` stores the serio port and mapped registers. `apbps2_isr()` drains received data and maps parity/frame status to serio flags. `apbps2_write()`, `apbps2_open()`, and `apbps2_close()` implement serio callbacks. `apbps2_of_probe()` maps resources, requests IRQ, reads core frequency, programs reload, and registers serio.

## Control Flow

Probe maps the MMIO resource, disables the controller, parses/maps the OF IRQ, requests it shared, reads the `freq` property, programs the reload register to `freq_hz / 10000`, allocates and registers a serio port, and stores driver data. Open clears error flags, drains stale data with a limit, and enables receiver plus receive interrupt. Interrupt handling loops while data-ready is set, reads data, clears error bits if needed, and reports the byte. Write waits for TX FIFO space, writes the byte, and enables receive/transmit controls.

## State and Persistence Behavior

Persistent state is the MMIO register mapping and serio port. Hardware state includes reload timing, control bits, FIFO contents, and status/error bits. The driver itself does not buffer data outside IRQ processing.

## Dependencies and Integration Points

The file depends on OF platform devices, big-endian MMIO accessors, IRQ mapping/request, and serio core. It integrates with standard PS/2 protocol drivers through `SERIO_8042`.

## Risks and Edge Cases

`irq_of_parse_and_map()` result is not explicitly checked before `devm_request_irq()`. Write timeout returns `-ETIMEDOUT`; open drain uses a fixed 1024-iteration limit. The OF match table uses legacy `.name` entries rather than compatible strings. Correct operation depends on the `freq` property being present and accurate.

## Test Signals

Tests should cover OF probe with valid and missing `freq`, IRQ receive with parity/frame errors, open FIFO drain, write timeout and success, reload timing, remove cleanup, and standard keyboard/mouse attach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/apbps2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/arc_ps2.c -->
# sources/distributed-fs/ceph-client/drivers/input/serio/arc_ps2.c

## Purpose

`arc_ps2.c` implements a two-port Synopsys ARC PS/2 controller as two serio `SERIO_8042` ports. It verifies the controller ID, disables interrupts during setup, reports RX bytes from both ports, and tracks basic error counters.

## Important APIs, Types, and Functions

`struct arc_ps2_port` stores per-port data/status addresses and serio port. `struct arc_ps2_data` stores both ports, base address, and interrupt/error counters. `arc_ps2_check_rx()` drains a port. `arc_ps2_interrupt()` checks both ports. `arc_ps2_write()`, `arc_ps2_open()`, and `arc_ps2_close()` implement serio callbacks. `arc_ps2_create_port()` creates each serio port, and `arc_ps2_probe()` maps/probes the controller.

## Control Flow

Probe gets the named IRQ, allocates state, maps MMIO, verifies the hardware ID, inhibits both ports, requests the IRQ, creates and registers two serio ports, and stores driver data. Opening a port enables RX interrupts in that port's status register. The shared interrupt drains each port while RX valid is set, converts frame/overflow status into serio flags, and reports bytes. Writes poll for TX not full before writing. Remove unregisters both ports and logs counters.

## State and Persistence Behavior

The driver persists per-port MMIO addresses and serio ports plus aggregate counters for total interrupts, frame errors, and buffer overflows. Hardware state is port interrupt enablement and FIFO/status contents.

## Dependencies and Integration Points

The file depends on platform devices, OF matching, MMIO accessors, IRQ handling, and serio core. It integrates with keyboard/mouse consumers through two independent serio ports.

## Risks and Edge Cases

`arc_ps2_check_rx()` maps frame errors to `SERIO_PARITY` and buffer overflow to `SERIO_FRAME`, which may be semantically surprising. The RX drain has a timeout and logs hardware-stuck errors. Writes use a short polling loop with no delay. The driver assumes exactly two ports and a fixed register layout.

## Test Signals

Useful tests include controller ID mismatch, two-port keyboard/mouse attach, shared IRQ delivery, RX frame and overflow counters, write timeout, open/close interrupt masking per port, partial port creation failure cleanup, and OF compatible matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/arc_ps2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/gscps2.c -->
# sources/distributed-fs/ceph-client/drivers/input/serio/gscps2.c

## Purpose

`gscps2.c` implements the HP GSC PS/2 keyboard/mouse controller driver for PA-RISC workstations. It registers each LASI/DINO PS/2 port as a serio `SERIO_8042` port and handles the shared-interrupt behavior of HP GSC PS/2 hardware.

## Important APIs, Types, and Functions

`struct gscps2port` stores list linkage, PA-RISC device, serio port, spinlock, MMIO base, circular buffer indices, buffered data/status entries, and port ID. Important functions include `wait_TBE()`, `gscps2_flush()`, `gscps2_writeb_output()`, `gscps2_enable()`, `gscps2_reset()`, `gscps2_read_data()`, `gscps2_report_data()`, `gscps2_interrupt()`, serio callbacks `gscps2_write/open/close()`, and PA-RISC driver probe/remove/init/exit.

## Control Flow

Probe verifies an IRQ, adjusts the HPA for DINO variants, allocates state and serio port, maps registers, resets the port, reads keyboard/mouse ID, requests the shared IRQ, validates the ID, registers the serio port, and adds the port to a global list. Opening resets and enables the port, then manually invokes the interrupt handler to flush pending data. The interrupt handler first reads data from every listed port under each port lock, then reports buffered data to serio outside the read phase; if new composite interrupt status appears during reporting, it breaks so the handler can restart. Writes wait for transmit-buffer empty, wait for receive-buffer empty, write the byte under lock, delay, then manually service incoming data.

## State and Persistence Behavior

The driver persists a global list of active PS/2 ports, per-port MMIO mappings, spinlocks, serio ports, and small circular buffers. Hardware state includes enable/reset/control bits, receive/transmit buffers, and shared composite interrupt status. Open/close toggles the controller enable bit.

## Dependencies and Integration Points

The file depends on PA-RISC device infrastructure, shared IRQs, MMIO byte access, spinlocks, delay helpers, and serio core. It integrates with standard PS/2 keyboard/mouse drivers through `SERIO_8042`.

## Risks and Edge Cases

The shared interrupt design requires reading all ports before reporting any bytes to avoid blocking writes while another port has pending data. Buffer indexing uses a 16-entry mask but `gscps2_read_data()` as shown does not advance `append`, which would prevent reporting newly read bytes unless this source variant relies on behavior not visible here; that is a high-value review point. Remove frees `ps2port` but not the separately allocated serio directly, relying on serio unregister ownership. Some memory-region release code is disabled.

## Test Signals

Tests should cover LASI keyboard and mouse ports, shared interrupt storms, write while peer port has data, timeout/parity flag reporting, open reset/enable sequencing, close disable, DINO offset builds if enabled, remove cleanup, and review or instrumentation of circular-buffer append/report behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/gscps2.c -->
