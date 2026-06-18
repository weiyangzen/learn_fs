# subset-b-003971 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/cyapa_gen3.c -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/cyapa_gen3.c

## Purpose

`cyapa_gen3.c` implements the Gen3 Cypress APA I2C/SMBus touchpad backend behind the common `cyapa_dev_ops` interface. It covers legacy register-map access, device-state detection, bootloader entry/exit, firmware validation and flashing, calibration/baseline sysfs handlers, power-mode transitions, IRQ filtering, and multitouch input reporting.

## Important APIs, Types, and Functions

Key device wire types are `struct cyapa_touch`, `struct cyapa_reg_data`, and `struct gen3_write_block_cmd`. Bus access is normalized through `cyapa_read_byte`, `cyapa_write_byte`, `cyapa_read_block`, `cyapa_i2c_reg_read_block`, and `cyapa_smbus_read_block`. Firmware update is split across `cyapa_gen3_check_fw`, `cyapa_gen3_bl_enter`, `cyapa_gen3_bl_activate`, `cyapa_gen3_write_fw_block`, `cyapa_gen3_do_fw_update`, `cyapa_gen3_bl_deactivate`, and `cyapa_gen3_bl_exit`. Runtime behavior is exposed through `cyapa_gen3_do_operational_check`, `cyapa_gen3_set_power_mode`, `cyapa_gen3_do_calibrate`, `cyapa_gen3_show_baseline`, `cyapa_gen3_irq_handler`, and the exported `cyapa_gen3_ops` table.

## Control Flow

State parsing inspects bootloader status bytes or operational status/data-valid bits to set `cyapa->gen` and `cyapa->state`. Operational check exits bootloader if needed, sets full-active power before querying product data, and rejects non-Gen3 or non-`CYTRA` devices. Firmware update verifies an exact 30,848-byte image and two checksums, writes all data blocks first, then header/checksum blocks, with each 64-byte flash block wrapped in a security-key command and polled until the bootloader is no longer busy. IRQ handling reads one complete `cyapa_reg_data`, validates status/data bits, then reports slots, pressure, and mechanical buttons.

## State and Persistence Behavior

Runtime state is stored in the shared `struct cyapa`: state, generation, firmware version, product ID, dimensions, button capability, max pressure, operational flag, and input device pointer. Firmware persists on the touchpad flash only through the bootloader update path. Power state is written into the device register and delayed according to the previous scan rate; during runtime PM, the handler opportunistically drains/report polls to avoid losing touch state while the command settles.

## Dependencies and Integration Points

This file depends on Linux I2C/SMBus helpers, input MT helpers, unaligned endian helpers, `cyapa.h` constants/helpers, and the common cyapa core that calls `cyapa_dev_ops`. It integrates with sysfs attributes supplied by the core, the firmware loader, and the Linux input subsystem.

## Risks and Edge Cases

SMBus block reads loop by 32-byte chunks and trust the encoded command class; wrong lengths become `-EIO`. Touch IDs are converted to slots by `id - 1` without a local range check. The firmware checksum error for image data logs "header checksum", which can mislead diagnostics. Bootloader timing uses long sleeps and fixed retry windows, so marginal hardware can produce `-EAGAIN` despite being recoverable. Proximity and some bootloader hooks are stubs returning unsupported/success by design.

## Test Signals

Useful coverage includes I2C and SMBus read/write paths, state parsing for OP/BL idle/active/busy/watchdog cases, firmware-size and checksum rejection, block-write timeout/error injection, bootloader enter/exit recovery, calibration timeout, baseline read, power-mode no-op and PM-poll paths, invalid packet rejection, slot/button reporting, and `cyapa_gen3_ops` signature/build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/cyapa_gen3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/cyapa_gen5.c -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/cyapa_gen5.c

## Purpose

`cyapa_gen5.c` implements the Cypress PIP transport and Gen5 device operations for cyapa touchpads. It provides shared PIP command serialization used by Gen5 and Gen6, PIP state detection, bootloader firmware update, power management, calibration, baseline diagnostics, proximity control, IRQ command response handling, and touch/button/proximity report decoding.

## Important APIs, Types, and Functions

Important packet structures include `cyapa_pip_touch_record`, `cyapa_pip_report_data`, `cyapa_tsg_bin_image_*`, `pip_bl_cmd_head`, `pip_app_cmd_head`, and parameter/retrieve command payloads. Public helpers used by Gen6 include `cyapa_pip_cmd_state_initialize`, `cyapa_i2c_pip_read`, `cyapa_i2c_pip_write`, `cyapa_empty_pip_output_data`, `cyapa_i2c_pip_cmd_irq_sync`, PIP response sorters, `cyapa_pip_bl_enter`, `cyapa_pip_bl_exit`, `cyapa_pip_check_fw`, `cyapa_pip_do_fw_update`, `cyapa_pip_deep_sleep`, `cyapa_pip_set_proximity`, `cyapa_pip_suspend_scanning`, `cyapa_pip_resume_scanning`, `cyapa_pip_do_calibrate`, `cyapa_pip_irq_cmd_handler`, and `cyapa_pip_irq_handler`. `cyapa_gen5_ops` binds these to the common driver.

## Control Flow

Initialization sets completions, command mutexes, PM-stage locks, response sort callbacks, and cached power/sleep state. Every PIP command takes `cmd_lock`, records the expected command code, optionally drains stale output data, writes an output report, then waits by IRQ completion or polling until the sorter finds the matching response. State parsing classifies idle buffers, HID descriptors, report descriptors, command responses, or touch/button reports into Gen5 app/bootloader states and always drains unread content afterward. Firmware update validates TSG image header/family/platform metadata, app-integrity CRC, row alignment, and app CRC; it initiates bootload with metadata, writes each row except the final integrity row, and validates bootloader acknowledgements. Runtime IRQs first give pending commands a chance to consume responses, then normal reports are parsed into MT slots, buttons, proximity distance, or runtime wake events.

## State and Persistence Behavior

Persistent driver state lives in `cyapa->cmd_states.pip`, cached device power/sleep values, product information, electrode geometry, platform version, origin flags, and input device state. Firmware writes persist in device flash through PIP bootloader commands. Baseline/IDAC scanning temporarily suspends scanning and resumes it even on most error paths.

## Dependencies and Integration Points

The code depends on Linux I2C master send/recv, completions, mutexes, atomics, PM runtime, CRC-ITU-T, input MT, and shared PIP constants/macros from `cyapa.h`. Gen6 directly reuses many non-static helpers from this file.

## Risks and Edge Cases

Command response matching depends on the global `in_progress_cmd`; malformed or interleaved responses must be drained carefully. `cyapa_empty_pip_output_data` has fixed report/empty-count limits and can return `-EINVAL` after draining unrelated reports. Baseline and panel-scan routines perform many command transactions while scanning is suspended, so resume failure masks or combines with the original error. Several response paths validate headers but trust payload offsets after minimum-length checks. Firmware parsing assumes the final flash record is row `0x01ff`.

## Test Signals

Tests should cover command serialization, IRQ and polling response paths, fallback polling after IRQ timeout, stale touch reports during commands, state parsing for HID/report/command data, bootloader enter/exit, TSG firmware validation failures, row-write errors, power transitions including deep sleep and button-only, proximity unsupported timeout mapping, calibration suspend/resume ordering, baseline data retrieval, touch liftoff and origin inversion, wake events, and invalid report lengths/IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/cyapa_gen5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/cyapa_gen6.c -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/cyapa_gen6.c

## Purpose

`cyapa_gen6.c` adds Gen6-specific behavior on top of the shared Gen5 PIP command engine. It identifies Gen5 versus Gen6 PIP devices, reads Gen6-specific system information, implements Gen6 power/IRQ interval controls, wraps proximity changes with command-IRQ masking, exposes Gen6 baseline diagnostics, and registers `cyapa_gen6_ops`.

## Important APIs, Types, and Functions

Local wire structures are `pip_app_cmd_head`, `pip_app_resp_head`, `pip_fixed_info`, and the local interval-setting command. `cyapa_pip_state_parse` is the shared PIP generation detector. Gen6-specific helpers include `cyapa_get_pip_fixed_info`, `cyapa_gen6_read_sys_info`, `cyapa_gen6_bl_read_app_info`, `cyapa_gen6_config_dev_irq`, `cyapa_gen6_set_proximity`, `cyapa_gen6_change_power_state`, `cyapa_gen6_set_interval_setting`, `cyapa_gen6_get_interval_setting`, `cyapa_gen6_deep_sleep`, `cyapa_gen6_set_power_mode`, `cyapa_pip_retrieve_data_structure`, `cyapa_gen6_show_baseline`, and `cyapa_gen6_operational_check`.

## Control Flow

State parsing wakes from deep sleep, drains queued data, reads the HID descriptor, determines app versus bootloader mode, then reads fixed silicon/family identifiers either from bootloader info or app system info. Family `0x9B` with silicon-high `0x0B` maps to Gen6; family `0x91` with silicon-high `0x02` maps to Gen5. Operational check exits bootloader if possible, forces full-active power, enables proximity, reads system info, and validates the `CYTRA` product prefix. Power changes disable command IRQs around disruptive transitions, wake from deep sleep with a ping plus deep-sleep command, use Gen6 active/button-only/LP1/LP2 modes, and update cached low-power intervals as needed.

## State and Persistence Behavior

Gen6 stores geometry, firmware, platform, product ID, origin flags, button capability, Rx electrode count, aligned Rx count, cached PIP power/sleep state, and `gen6_interval_setting` in `struct cyapa`. Firmware persistence is delegated to the shared PIP bootloader helpers. Baseline diagnostics suspend scanning, retrieve RX attenuator/IDAC and attenuator trim structures, then resume scanning and clear the sysfs buffer on failure.

## Dependencies and Integration Points

This file depends heavily on non-static helpers from `cyapa_gen5.c`, including PIP command execution, response sorting, firmware validation/update, deep sleep, proximity, scan suspend/resume, calibration, and IRQ processing. It integrates with the same cyapa core `cyapa_dev_ops` table and Linux I2C/input infrastructure.

## Risks and Edge Cases

`cyapa_pip_state_parse` returns success even when fixed info does not match Gen5 or Gen6, leaving `state` as no-device for the caller to interpret. IRQ enable/disable errors are often ignored around proximity/power operations. Gen6 interval updates choose LP2 once LP1 is occupied, so later distinct sleep times overwrite LP2. The retrieve-data helper has a fixed response buffer sized for `GEN6_MAX_RX_NUM + 10`; larger firmware data structures return `-ENOBUFS` only if the response itself fit.

## Test Signals

Coverage should include Gen5/Gen6 detection in app and bootloader modes, fixed-info read failures, deep-sleep wake ping behavior, command IRQ mask/unmask sequencing, active/button-only/off/LP1/LP2 transitions, interval cache synchronization, proximity error propagation, bootloader app-info fallback, system-info offset parsing and validation, baseline retrieve-data success and `-ENOBUFS`, resume-after-baseline failure, and reuse of shared PIP firmware/calibration/IRQ handlers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/cyapa_gen6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/cypress_ps2.c -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/cypress_ps2.c

## Purpose

`cypress_ps2.c` implements support for Cypress PS/2 trackpads in the psmouse stack. It detects Cypress hardware, sends Cypress extension commands, queries firmware and optional geometry metrics, switches the device into absolute pressure mode, configures Linux input capabilities, parses variable-length absolute packets, reports semi-multitouch events, and handles reconnect/disconnect/rate callbacks.

## Important APIs, Types, and Functions

The psmouse entry points are `cypress_detect` and `cypress_init`. Command transport is handled by `cypress_ps2_sendbyte`, `cypress_ps2_ext_cmd`, `cypress_verify_cmd_state`, and `cypress_send_ext_cmd`. Hardware setup uses `cypress_read_fw_version`, `cypress_read_tp_metrics`, `cypress_query_hardware`, `cypress_set_absolute_mode`, `cypress_reset`, and `cypress_set_input_params`. Packet flow uses `cypress_get_finger_count`, `cypress_parse_packet`, `cypress_process_packet`, `cypress_validate_byte`, and `cypress_protocol_handler`. Lifecycle callbacks are `cypress_set_rate`, `cypress_disconnect`, and `cypress_reconnect`.

## Control Flow

Detection sends the encoded read-ID command and requires Cypress signature bytes `0x33 0xCC`. Initialization allocates `struct cytp_data`, resets the device, queries firmware/metrics, enters absolute-with-pressure mode, configures input ABS/MT/key capabilities, and installs psmouse callbacks. The protocol handler dynamically adjusts expected packet size based on the first byte and pressure mode, then processes a full packet. Packet parsing extracts one or two coordinate contacts, maps high-bit finger-count encodings including horizontal-scroll overloads for four/five-finger signals, suppresses left click on multifinger tap packets, and reports two semi-MT slots with button state.

## State and Persistence Behavior

All state is volatile in `struct cytp_data`: firmware version, packet size, mode bits, dimensions, pressure range, resolution, and metrics-support flag. Hardware mode persists only until reset or reconnect. `psmouse->private`, callback pointers, packet size, model, and rate fields bind this state into the psmouse core.

## Dependencies and Integration Points

The driver integrates with serio/libps2/psmouse, Linux input MT, and constants/types from `cypress_ps2.h`. It uses `ps2_command`, `ps2_sendbyte`, `psmouse_reset`, and psmouse protocol-handler callbacks rather than I2C.

## Risks and Edge Cases

Firmware version 11 and newer disable TP metrics because known devices return bogus data, leaving hardcoded default dimensions. `cypress_process_packet` ignores its `zero_pkt` argument; leave events are instead represented by zero contacts through normal reporting. Packet validation only inspects the first byte after mode is set, so malformed trailing bytes can still reach parsing. The code supports at most two actual coordinate slots while reporting higher finger counts through pointer emulation/tool count. Reconnect restores absolute mode but does not re-query geometry.

## Test Signals

Tests should cover detect success/failure signatures, extension-command retry/recovery, metrics-supported and default paths, invalid geometry rejection, absolute-mode setup, input capability setup, first-byte validation, dynamic 4/5/7/8-byte packet sizing, one/two/four/five-finger count decoding, tap suppression of button clicks, semi-MT slot assignment, reconnect failure and success, disconnect reset/free, and rate changes around the 80 Hz threshold.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/cypress_ps2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/cypress_ps2.h -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/cypress_ps2.h

## Purpose

`cypress_ps2.h` is the protocol definition and private-state header for the Cypress PS/2 trackpad driver. It defines Cypress extension-command encoding, mode/status bits, packet bitfields, default geometry, MT limits, report/private-data structures, and the psmouse-visible detect/init prototypes.

## Important APIs, Types, and Functions

The command macros `ENCODE_CMD`, `DECODE_CMD_AA/BB/CC/DD`, and `CYTP_CMD_*` describe how four two-bit nibbles are sent through PS/2 extension commands. Mode flags include absolute-with-pressure, absolute-without-pressure, Cypress relative, standard relative, high-rate, and report-mode bits. Packet and response masks describe button bits, absolute scroll/tap bits, status response bits, and TP metrics flags. `struct cytp_contact`, `struct cytp_report_data`, and `struct cytp_data` are consumed by `cypress_ps2.c`. Public prototypes are `cypress_detect` and `cypress_init`.

## Control Flow

The header itself has no executable control flow, but it defines the encoding used by `cypress_send_ext_cmd`: each Cypress command is decomposed into DD, CC, BB, and AA nibbles and sent as PS/2 set-resolution extension bytes before a get-info command reads the response. Packet constants drive `cypress_validate_byte` and `cypress_parse_packet`.

## State and Persistence Behavior

`struct cytp_data` is the persistent per-device runtime cache held in `psmouse->private`. It stores firmware version, current packet size, Cypress mode bits, pressure/dimension/resolution values, and whether TP metrics are supported. `struct cytp_report_data` is transient parsed packet state for the current input report.

## Dependencies and Integration Points

The header includes `psmouse.h` for `struct psmouse` and is private to the psmouse Cypress implementation. Its constants are tightly coupled to the packet parser, input setup, and command transport in `cypress_ps2.c`.

## Risks and Edge Cases

The misspelled `FW_VERSION_MASX` and `CYTP_CMD_PALM_GEMMETRY_MASK` names are ABI-internal but can trip search/readability. Defaults are based on specific Dell XPS dimensions and become the fallback for devices without trustworthy metrics. `CYTP_MAX_MT_SLOTS` is two even though tool-count constants represent up to five fingers, so consumers must treat this as semi-MT.

## Test Signals

Build coverage should catch macro/prototype drift with `cypress_ps2.c`. Behavioral tests should validate command encode/decode round trips, mode-bit combinations, packet bit masks used by finger/button parsing, default dimension constants, and structure layout expectations for two contact slots and cached device parameters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/cypress_ps2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/elan_i2c.h -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/elan_i2c.h

## Purpose

`elan_i2c.h` is the shared contract between the Elan touchpad core and its I2C/SMBus transport backends. It defines report IDs/layout offsets, common mode bits, firmware-update constants, product IDs, the IAP mode enum, the transport operation table, and extern declarations for the two backend implementations.

## Important APIs, Types, and Functions

Important constants include `ETP_ENABLE_ABS`, `ETP_ENABLE_CALIBRATE`, report IDs `ETP_REPORT_ID`, `ETP_REPORT_ID2`, `ETP_TP_REPORT_ID`, `ETP_TP_REPORT_ID2`, report offsets, `ETP_MAX_REPORT_LEN`, `ETP_MAX_FINGERS`, firmware page sizes, firmware signature size, and product IDs used for quirks. `enum tp_mode` distinguishes `IAP_MODE` and `MAIN_MODE`. `struct elan_transport_ops` is the central ABI between core and transports, covering initialization, sleep/power/mode control, calibration, baseline, version/product/checksum/geometry queries, IAP reset/update, report feature discovery, report reads, pressure adjustment, and pattern query.

## Control Flow

The header has no runtime control flow. At probe time, `elan_i2c_core.c` selects either `elan_i2c_ops` or `elan_smbus_ops`, then drives all device operations through this table. The report ID/offset constants are used in IRQ decoding for touchpad, high-precision touchpad, and optional trackpoint packets.

## State and Persistence Behavior

This file defines no storage, but it determines how state is represented by the core: report geometry, firmware metadata, calibration state, IAP mode, and firmware page/update parameters. The firmware constants also define the expected naming and signature contract for persistent device firmware updates.

## Dependencies and Integration Points

It depends on Linux integer types and forward-declares `struct i2c_client` and `struct completion`. It is included by `elan_i2c_core.c`, `elan_i2c_i2c.c`, and `elan_i2c_smbus.c`, making operation-table compatibility the main integration point.

## Risks and Edge Cases

Any signature change in `struct elan_transport_ops` must be implemented by both transports. Shared report offsets must remain valid for both full I2C and SMBus packet layouts; SMBus fakes the same offsets by reading into an offset buffer. Product IDs in this header feed quirks in the core, so missing IDs can affect resume behavior and firmware handling.

## Test Signals

Build tests should cover both `CONFIG_MOUSE_ELAN_I2C_I2C` and `CONFIG_MOUSE_ELAN_I2C_SMBUS`. Runtime tests should verify all ops are populated, report IDs dispatch correctly, firmware page-size constants match selected IC/IAP versions, firmware names include product IDs, and property/quirk handling recognizes the listed product IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/elan_i2c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/elan_i2c_core.c -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/elan_i2c_core.c

## Purpose

`elan_i2c_core.c` is the transport-independent Elan I2C/SMBus touchpad driver. It selects a backend, powers and initializes the device, queries firmware and geometry, exposes sysfs firmware/calibration/baseline controls, registers input devices, decodes IRQ reports for touchpad and optional trackpoint data, and implements suspend/resume with regulator and wakeup handling.

## Important APIs, Types, and Functions

`struct elan_tp_data` is the central per-device state. Probe and lifecycle functions include `elan_probe`, `elan_suspend`, `elan_resume`, and `elan_disable_regulator`. Initialization/query helpers include `elan_initialize`, `elan_query_product`, `elan_query_device_info`, `elan_query_device_parameters`, `elan_get_fwinfo`, and `elan_i2c_lookup_quirks`. Firmware update is handled by `elan_sysfs_update_fw`, `elan_update_firmware`, `__elan_update_firmware`, and `elan_write_fw_block`. Sysfs calibration/baseline flows use `elan_calibrate`, `calibrate_store`, `elan_acquire_baseline`, `acquire_store`, `min_show`, and `max_show`. IRQ reporting uses `elan_isr`, `elan_report_absolute`, `elan_report_contact`, and `elan_report_trackpoint`.

## Control Flow

Probe chooses native I2C if available, otherwise SMBus, allocates state, enables `vcc`, verifies the address, initializes absolute mode, queries firmware/info/geometry, sets up input devices, requests a threaded IRQ, and registers input nodes. IRQ handling completes firmware update waits when `in_fw_update` is true; otherwise it reads a transport report and dispatches by report ID. Firmware update disables IRQs, enters IAP mode, writes all pages after the boot area with per-page checksums, waits for reset, verifies IAP checksum, and reinitializes. Suspend serializes against sysfs, disables IRQ, sleeps or powers off depending on wake capability, and may disable the regulator; resume re-enables power, initializes with optional quick-wakeup quirk, then reenables IRQ.

## State and Persistence Behavior

Driver state includes queried product/firmware/checksum/IAP metadata, geometry/resolution, report features/length, pressure adjustment, mode bits, baseline cache, clickpad/middle-button flags, quirks, regulator pointer, sysfs mutex, and firmware-update completion flag. Firmware update changes persistent device flash. Baseline values persist only in memory after `baseline/acquire` and are invalidated before each acquire.

## Dependencies and Integration Points

The core integrates Linux I2C driver registration, ACPI/OF matching, firmware loader, regulator framework, PM wake IRQ/events, input MT, sysfs device groups, and transport ops from `elan_i2c.h`. Device properties can override max coordinates, physical size, trace counts, clickpad, middle button, and trackpoint presence.

## Risks and Edge Cases

Firmware update assumes the signature address derived from IC/IAP metadata is within the firmware blob before dereferencing. Geometry calculations divide by trace counts or millimeter values returned by firmware/properties. Suspend keeps IRQ disabled until resume even if initialization later fails. Trackpoint reports can arrive without a registered trackpoint device and only warn once. Baseline/calibration disable IRQs and rely on transport mode restoration on all error paths.

## Test Signals

Coverage should include I2C versus SMBus selection, regulator failure paths, device-property overrides, quirk lookup, firmware metadata for every IC type, firmware signature mismatch, update success/failure with checksum mismatch, sysfs read/write locking, calibration timeout, baseline not-ready and acquire paths, touch/high-precision/trackpoint IRQ reports, optional middle/clickpad/trackpoint properties, suspend as wake source versus powered-off, resume quick-wakeup, and both ACPI/OF/module match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/elan_i2c_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/elan_i2c_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/elan_i2c_i2c.c

## Purpose

`elan_i2c_i2c.c` is the native I2C transport backend for the Elan touchpad core. It implements register-command reads/writes, reset and descriptor reads, sleep/power/mode control, calibration and baseline queries, firmware/product/geometry queries, IAP firmware update operations, report feature selection, and full report reads for `elan_i2c_ops`.

## Important APIs, Types, and Functions

Low-level helpers are `elan_i2c_read_block`, `elan_i2c_read_cmd`, and `elan_i2c_write_cmd`. Initialization/control helpers include `elan_i2c_initialize`, `elan_i2c_sleep_control`, `elan_i2c_power_control`, `elan_i2c_set_mode`, `elan_i2c_calibrate`, and `elan_i2c_calibrate_result`. Query helpers include `elan_i2c_get_pattern`, `elan_i2c_get_version`, `elan_i2c_get_sm_version`, `elan_i2c_get_product_id`, `elan_i2c_get_checksum`, `elan_i2c_get_max`, `elan_i2c_get_resolution`, `elan_i2c_get_num_traces`, and `elan_i2c_get_pressure_adjustment`. IAP update helpers include `elan_i2c_iap_get_mode`, `elan_i2c_iap_reset`, `elan_i2c_prepare_fw_update`, `elan_i2c_write_fw_block`, and `elan_i2c_finish_fw_update`.

## Control Flow

Native I2C reads send a little-endian 16-bit register address followed by a read message. Initialization issues reset through the standard command register, consumes reset acknowledgement, then reads device and report descriptors. Firmware update checks/enters IAP mode, sets flash keys, optionally configures IAP page type for newer ICs, writes pages with register prefix plus checksum, polls IAP status bits, resets the device, waits on the IRQ completion, and drains the final interrupt signal. Normal report reads use `i2c_master_recv` for the report length selected from pattern.

## State and Persistence Behavior

The transport stores no private state; all persistent state is in core `elan_tp_data` and on the device. It changes hardware mode, power state, IAP page type, and flash contents through register writes. Pattern handling affects how firmware/IAP versions and report lengths are interpreted by the core.

## Dependencies and Integration Points

It depends on Linux I2C transfer APIs, unaligned endian helpers, completions supplied by the core, and constants/ops from `elan_i2c.h`. It is selected only when the adapter supports `I2C_FUNC_I2C`.

## Risks and Edge Cases

Several read helpers allocate 3-byte buffers for 2-byte reads, so callers must continue to interpret only the intended bytes. `elan_i2c_finish_fw_update` enables IRQ while the core-level update path is otherwise operating under disabled IRQ assumptions, so ordering with the completion is critical. Firmware signature bounds are checked in the core, not here. Pattern-specific version and IC-type parsing has separate old/new paths that can regress older firmware. Power control read-modify-write depends on the current register being readable while suspended.

## Test Signals

Tests should cover two-message I2C read errors, short transfers, reset descriptor sequence, old/new pattern parsing, IAP mode detection, IAP reset and password verification, 64/128/512-byte page programming, IAP status error bits, firmware reset completion timeout, report length selection for high-precision reports, pressure adjustment bit parsing, baseline/calibration commands, and integration with the core firmware update and IRQ completion paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/elan_i2c_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/elan_i2c_smbus.c -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/elan_i2c_smbus.c

## Purpose

`elan_i2c_smbus.c` is the SMBus transport backend for the Elan touchpad core. It implements the same `elan_transport_ops` contract as the native I2C backend using SMBus byte/block commands, including hello-packet initialization, mode/calibration/baseline/version/geometry queries, IAP firmware update preparation and page writes, packet reads, and SMBus-specific report feature selection.

## Important APIs, Types, and Functions

Core entry points are the functions installed into `elan_smbus_ops`: `elan_smbus_initialize`, `elan_smbus_sleep_control`, `elan_smbus_power_control`, `elan_smbus_set_mode`, `elan_smbus_calibrate`, `elan_smbus_calibrate_result`, `elan_smbus_get_baseline_data`, version/product/checksum/geometry helpers, `elan_smbus_iap_get_mode`, `elan_smbus_iap_reset`, `elan_smbus_prepare_fw_update`, `elan_smbus_write_fw_block`, `elan_smbus_finish_fw_update`, `elan_smbus_get_report_features`, `elan_smbus_get_report`, and `elan_smbus_get_pattern`.

## Control Flow

Initialization reads a five-byte hello packet of all `0x55` values and sends the enable-touchpad byte. Mode and calibration are written as small command blocks to `ETP_SMBUS_IAP_CMD`. Query helpers read block data from command IDs and decode big-endian or packed fields into core state. Firmware update enters IAP from main mode by setting the flash key, writing and verifying the SMBus IAP password, waiting for mode switch, setting the flash key again, and resetting. Each firmware page is split into two SMBus block writes because SMBus blocks are limited to 32 bytes, then IAP status bits are checked. Report reads place block data at offset 2 so the resulting buffer matches the shared report ID offsets expected by the core.

## State and Persistence Behavior

The backend stores no transport-private state. It mutates device mode, sleep state, IAP mode, and flash contents. `power_control`, `finish_fw_update`, and `get_pattern` are no-ops or fixed-value implementations because the SMBus protocol path does not expose the corresponding native I2C behavior.

## Dependencies and Integration Points

It depends on SMBus byte/block/I2C-block functionality selected in `elan_probe`, constants from `elan_i2c.h`, and Linux I2C SMBus helpers. Its buffer layout is intentionally coupled to the core ISR offsets.

## Risks and Edge Cases

SMBus page writes split by `fw_page_size / 2`; this only works for page sizes that fit the two-block protocol and may not support newer larger page modes. `elan_smbus_get_checksum` appears to choose the firmware checksum command when `iap` is true and IAP checksum when false, the reverse of the naming pattern used by I2C, so update verification should be treated carefully. `sleep_control(false)` and `power_control` are no-ops, which shifts wake behavior to initialization/enabling. Report length can shrink for `ETP_TP_REPORT_ID2` after reading the report ID.

## Test Signals

Tests should cover hello-packet validation, enable command errors, all block query length checks, packed range/resolution/trace decoding, calibration result copy bounds, IAP password write/read verification, main-to-IAP transition, page split writes and IAP error bits, checksum-command behavior, report offset compatibility with the core, trackpoint short-report handling, fixed pattern zero behavior, and parity with native I2C ops required by `struct elan_transport_ops`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/elan_i2c_smbus.c -->
