# subset-b-005541 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/tipd/core.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/tipd/core.c

Purpose: Implements the TI TPS6598x-family USB Type-C/USB-PD controller driver over I2C, including generic TPS6598x, Apple CD321x, and TPS25750 variants. It registers Type-C ports, partners, USB role switching, power-supply status, interrupt/poll processing, alternate-mode mux state for CD321x, suspend/resume behavior, and firmware patch flows.

Important APIs/types/functions: `struct tps6598x` is the main per-controller state with regmap, mutex, Type-C objects, USB role switch, cached status registers, power supply, and variant `tipd_data`. `struct cd321x` extends it with DP/TBT/USB4 status, Type-C mux state, delayed update work, and current partner identity. `tipd_data` selects variant callbacks for IRQ handling, port registration, tracing, firmware patching, power-state switching, data-status reads, reset, and connect handling. Core helpers include `tps6598x_block_read/write`, typed read/write wrappers, `tps6598x_exec_cmd_tmo`, `tps6598x_connect`, `tps6598x_disconnect`, `tps6598x_dr_set`, `tps6598x_pr_set`, and `tps6598x_probe/remove`.

Control flow and state: probe allocates the variant-sized state, configures reset GPIO/regmap/I2C protocol, optionally switches CD321x to S0, checks controller mode, applies patches when in PTCH mode, writes interrupt masks, reads initial status, gets the connector fwnode and USB role switch, registers the power supply and Type-C port, then registers an already-connected partner. Interrupt paths read/trace event registers, clear them, refresh status/power/data caches, and update Type-C objects. CD321x uses `cd321x_queue_status` plus delayed `cd321x_update_work` to debounce state, unregister/register changed partners, set mux modes for safe USB, DP, TBT, or USB4, and switch USB roles in a controlled order.

Persistence behavior: runtime state is held only in kernel objects and cached register fields. Firmware patching reads blobs named by firmware properties and writes controller RAM/flash-like patch channels, but this file does not persist host-side state. Removal and failed probe reset controllers to discard applied patches where the variant supports reset.

Dependencies/integration points: integrates with I2C/regmap, firmware loader, device-tree/ACPI fwnodes, GPIO reset, `usb_role_switch`, Type-C class, Type-C altmode/mux APIs, power_supply, workqueues, IRQ threading, and local `tps6598x.h`/`trace.h`.

Risks: command execution busy/timeout handling is hardware-sensitive; firmware patch paths temporarily rewrite I2C client address and adapter timeout; CD321x mux state uses stack data during `typec_mux_set` and must clear it immediately; missed events can desynchronize cached `status`, `pwr_status`, and `data_status`; polling fallback depends on repeated IRQ handler execution. A visible oddity is a duplicated `tps6598x_block_read(TPS_REG_INT_EVENT1, ...)` in `tps6598x_interrupt`.

Test signals: useful signals are tracepoints for IRQ/status/power/data status, successful Type-C port/partner registration, role-swap success/failure, power_supply updates, firmware update success/errors, suspend/resume with IRQ and polling modes, hotplug/unplug, DP/TBT/USB4 mux transitions on CD321x, and probe/remove error unwinding with reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/tipd/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/tipd/tps6598x.h -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/tipd/tps6598x.h

Purpose: Defines the register bit masks, field extractors, interrupt bits, status constants, power/data status helpers, patch command layout constants, and hardware-version IDs used by the TPS6598x driver.

Important APIs/types/functions: `TPS_FIELD_GET()` wraps bitfield extraction for local masks. `TPS_STATUS_TO_UPSIDE_DOWN`, `TPS_STATUS_TO_TYPEC_PORTROLE`, `TPS_STATUS_TO_TYPEC_DATAROLE`, and `TPS_STATUS_TO_TYPEC_VCONN` translate raw status bits into Type-C booleans. `TPS_POWER_STATUS_*`, `TPS_DATA_STATUS_*`, `TPS_PD_STATUS_PORT_TYPE`, `TPS_VERSION_HW_VERSION`, and patch constants such as `TPS_PTCS_*`, `TPS_PTCD_*`, and `TPS_PTCC_*` are consumed throughout `core.c`.

Control flow and state: this header has no executable control flow or storage. It defines the interpretation layer for cached raw registers: `STATUS`, interrupt events, `POWER_STATUS`, `DATA_STATUS`, boot status, PD status, sleep config, patch-transfer responses, and hardware-version-dependent interrupt lengths.

Persistence behavior: none directly. Its patch-related constants affect how `core.c` drives firmware download/complete commands and validates device patch status.

Dependencies/integration points: depends on kernel bit helpers `<linux/bits.h>` and `<linux/bitfield.h>`. It is included by `core.c` and `trace.h`, so incorrect masks affect both behavior and diagnostics.

Risks: mask drift against vendor register definitions can create silent misreporting of port role, VCONN, power mode, DP pin assignment, USB4/TBT state, or interrupt flags. The `TPS_DATA_STATUS_TBT_CABLE_SPEED` and `TPS_DATA_STATUS_TBT_CABLE_GEN` macro definitions omit an argument in their body, so they should be reviewed before use; current code appears not to call them.

Test signals: compile coverage catches macro syntax issues only when macros are used. Runtime validation should compare trace output and Type-C class state against hardware analyzer/controller documentation for plug, power-role, data-role, DP/TBT/USB4, TPS25750 charger-detect, and patch-mode cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/tipd/tps6598x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/tipd/trace.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/tipd/trace.c

Purpose: Instantiates the TPS6598x tracepoints declared in `trace.h` by defining `CREATE_TRACE_POINTS` before including the trace header.

Important APIs/types/functions: No functions are defined directly. The important interface is the tracepoint generation side effect from `<trace/define_trace.h>` included by `trace.h`.

Control flow and state: no runtime control flow beyond module/object initialization of generated tracepoint metadata. It contributes trace events such as TPS6598x IRQ, CD321x IRQ, TPS25750 IRQ, status, power status, and data status.

Persistence behavior: none. Trace enablement and buffers are handled by the kernel tracing subsystem.

Dependencies/integration points: must be built exactly once in the driver object so tracepoint symbols are emitted. It depends on `trace.h` and the Linux tracepoint build convention.

Risks: if this file is omitted from the build when tracing is enabled, call sites in `core.c` may fail to link or tracepoints may not be available. If included more than once with `CREATE_TRACE_POINTS`, duplicate symbol errors are possible.

Test signals: build/link with tracing enabled, and verify tracefs exposes the `tps6598x` events. Runtime hotplug, power-status updates, and data-status updates should produce events when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/tipd/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/tipd/trace.h -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/tipd/trace.h

Purpose: Declares the TPS6598x tracepoint set and readable decoders for controller interrupt, status, power, and data-status bitfields, including generic TPS6598x, Apple CD321x, and TPS25750 variants.

Important APIs/types/functions: macros such as `show_irq_flags`, `show_cd321x_irq_flags`, `show_tps25750_irq_flags`, `show_status_*`, `show_power_status_*`, and `show_data_status_*` feed `TP_printk`. Trace events include `tps6598x_irq`, `cd321x_irq`, `tps25750_irq`, `tps6598x_status`, `tps25750_status`, `tps6598x_power_status`, `tps25750_power_status`, `tps6598x_data_status`, and `cd321x_data_status`.

Control flow and state: no stateful runtime logic; generated tracepoint code records event arguments from driver call sites and formats them through symbolic/flag decoders.

Persistence behavior: none. The tracing subsystem owns event enablement and buffering.

Dependencies/integration points: includes `tps6598x.h` so trace decoding uses the same masks as the driver. The header follows the kernel trace pattern with `TRACE_INCLUDE_FILE trace`, `TRACE_INCLUDE_PATH .`, and final inclusion of `<trace/define_trace.h>`.

Risks: trace formatting can become misleading if masks diverge from hardware or from `core.c` behavior. Because trace headers are sensitive to include guards and `TRACE_HEADER_MULTI_READ`, accidental restructuring can break tracepoint generation.

Test signals: compile with `CONFIG_TRACING`, enable each event under tracefs, and exercise IRQ, plug, power-status, TPS25750 charger-detect, DP, TBT, USB4, and CD321x HPD/data-status paths to confirm names and decoded fields are intelligible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/tipd/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/Kconfig

Purpose: Provides Kconfig entries for the UCSI core and platform-specific UCSI interface drivers.

Important APIs/types/functions: `TYPEC_UCSI` enables the core `typec_ucsi` module and depends on little-endian CPU plus optional USB role switch support. Child options include `UCSI_CCG`, `UCSI_ACPI`, `UCSI_STM32G0`, `UCSI_PMIC_GLINK`, `CROS_EC_UCSI`, `UCSI_LENOVO_YOGA_C630`, and `UCSI_HUAWEI_GAOKUN`.

Control flow and state: no runtime flow. Build-time selection controls which transport modules and helper integrations are compiled. `TYPEC_UCSI` selects `USB_COMMON` when debugfs is enabled.

Persistence behavior: none directly; configuration persists through kernel build configuration.

Dependencies/integration points: ties the UCSI core to ACPI, I2C, ChromeOS EC, Qualcomm PMIC GLINK, Lenovo/Huawei EC drivers, DRM bridge selections, and module naming documented in help text.

Risks: incorrect dependencies can create link failures or unusable drivers. The core excludes big-endian CPUs, which matters because UCSI command/data structures are handled as little-endian memory layouts. Optional transport entries must match Makefile object rules.

Test signals: Kconfig lint/build matrix with options as built-in and modules; randconfig coverage for optional debugfs, power_supply, DP altmode, TBT altmode, and transport drivers; menuconfig visibility checks for dependency combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/Makefile

Purpose: Defines how the UCSI core and transport modules are built.

Important APIs/types/functions: `typec_ucsi-y := ucsi.o` is the core object. Conditional additions include `debugfs.o` for `CONFIG_DEBUG_FS`, `trace.o` for `CONFIG_TRACING`, `psy.o` when `CONFIG_POWER_SUPPLY` is non-empty, `displayport.o` when `CONFIG_TYPEC_DP_ALTMODE` is enabled, and `thunderbolt.o` when `CONFIG_TYPEC_TBT_ALTMODE` is enabled. Separate module objects are listed for ACPI, CCG, STM32G0, PMIC GLINK, ChromeOS EC, Lenovo Yoga C630, and Huawei Gaokun transports.

Control flow and state: no runtime behavior. It shapes which code paths exist in the final kernel or modules and sets `CFLAGS_trace.o := -I$(src)` so generated trace headers can be found.

Persistence behavior: none beyond build outputs.

Dependencies/integration points: mirrors `Kconfig` options and the conditional declarations in `ucsi.h` for debugfs, power supply, DisplayPort, and Thunderbolt support.

Risks: mismatch between Kconfig and Makefile can create unresolved symbols or missing functionality. The `ifneq ($(CONFIG_*),)` style includes helper objects for both built-in and module states, which is intentional but should be kept consistent with header stubs.

Test signals: build with minimal `TYPEC_UCSI`, with all helpers enabled, with helpers disabled but core enabled, and with each transport as module/built-in. Trace builds should confirm include path correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/cros_ec_ucsi.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/cros_ec_ucsi.c

Purpose: Implements a UCSI transport for ChromeOS EC devices that expose a Platform Policy Manager through EC host commands and PD event notifications.

Important APIs/types/functions: `struct cros_ucsi_data` stores the EC device, UCSI core instance, notifier, work items, timeout counter, and completion/flag fields. `cros_ucsi_read`, `cros_ucsi_async_control`, and `cros_ucsi_sync_control` implement `ucsi_operations`. `cros_ucsi_event` receives ChromeOS PD notifications, `cros_ucsi_work` reads CCI and calls `ucsi_notify_common`, and `cros_ucsi_write_timeout` attempts recovery from stuck/busy PPM writes.

Control flow and state: probe finds the parent EC, creates a UCSI core instance, stores private data, registers a ChromeOS USB-PD notifier, and calls `ucsi_register`. EC `PD_EVENT_PPM` schedules work to read CCI and notify the core. `PD_EVENT_INIT` is treated like resume to re-enable PPM communication. Synchronous control delegates to `ucsi_sync_control_common` and schedules timeout recovery on `-EBUSY` or `-ETIMEDOUT`.

Persistence behavior: state is in memory only: timeout counter, pending delayed work, and UCSI core state. It does not persist commands across unload; resume and late init rebuild notification state through `ucsi_resume`.

Dependencies/integration points: integrates with `cros_ec_cmd`, ChromeOS EC platform data, `cros_usbpd_register_notify`, platform/ACPI/OF matching, UCSI core ops, Type-C mode selection for partner altmodes, and PM callbacks.

Risks: EC messages are capped at 256 bytes, so future larger UCSI payloads would need changes. Timeout recovery depends on detecting CCI busy/complete state and may leave the PPM unresponsive after five retries. Work flushing in the notifier prevents stale reads but can add latency. Parent-device discovery differs for firmware-described and subdevice cases.

Test signals: EC command success/failure logs, notifier delivery for `PD_EVENT_PPM` and `PD_EVENT_INIT`, timeout recovery logs, suspend/complete resume behavior on LPC-backed ECs, altmode mode-selection start/delete, and hotplug role/power updates through the UCSI core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/cros_ec_ucsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/debugfs.c

Purpose: Exposes a debugfs interface under the USB debug root for issuing selected raw UCSI commands and reading command responses plus UCSI 2.1 current/voltage telemetry.

Important APIs/types/functions: `ucsi_cmd` validates command opcodes and calls `ucsi_send_command`; `ucsi_resp_show` prints the stored 128-bit response; `ucsi_peak_curr_show`, `ucsi_avg_curr_show`, and `ucsi_vbus_volt_show` expose connector telemetry; `ucsi_debugfs_register/unregister/init/exit` manage dentries and `struct ucsi_debugfs_entry`.

Control flow and state: module init creates the top-level `ucsi` debugfs directory. Each registered UCSI instance allocates a debugfs entry and creates `command`, `response`, `peak_current`, `avg_current`, and `vbus_voltage`. Writing a command clears prior response/status, routes set-like commands without response storage and get-like commands into `debugfs->response`.

Persistence behavior: only last command response and status are cached in memory for each UCSI instance. Debugfs files disappear on unregister or module exit.

Dependencies/integration points: depends on `CONFIG_DEBUG_FS`, `usb_debug_root`, UCSI core command encoding, and cached connector telemetry maintained in `ucsi_handle_connector_change`.

Risks: raw command injection can perturb live Type-C policy and should be treated as a diagnostic-only interface. The telemetry helpers read `ucsi->connector` without selecting a connector index, so they effectively expose connector 1. Response storage is only 128 bits, which may be smaller than some modern UCSI payloads.

Test signals: debugfs directory/file creation, accepted/rejected opcodes, response formatting, error propagation through `status`, cleanup on `ucsi_destroy`, and telemetry changes after UCSI 2.1 power-reading-ready connector updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/displayport.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/displayport.c

Purpose: Provides DisplayPort alternate-mode support for UCSI ports, bridging Type-C altmode operations to UCSI current/new CAM commands and emulating DisplayPort VDM responses for the Type-C altmode framework.

Important APIs/types/functions: `struct ucsi_dp` stores DP altmode state, connector pointer, CAM offset, override support, VDM header/data, and work item. Main functions are `ucsi_register_displayport`, `ucsi_displayport_enter`, `ucsi_displayport_exit`, `ucsi_displayport_vdm`, `ucsi_displayport_configure`, `ucsi_displayport_status_update`, `ucsi_displayport_work`, and `ucsi_displayport_remove_partner`.

Control flow and state: registration forces conservative DP capabilities and all common pin assignments, registers a port altmode, attaches ops, and stores the CAM offset. Enter checks the active CAM and, when possible, prepares an ACK for Enter Mode while letting later Configure send `SET_NEW_CAM`. VDM handling responds to Status Update and Configure; Configure may issue UCSI `SET_NEW_CAM` with selected pins and marks the mode initialized. Work asynchronously calls `typec_altmode_vdm`.

Persistence behavior: per-altmode state is device-managed and lives for the altmode lifetime. `initialized`, DP status/config, and pending VDM fields are reset on partner removal.

Dependencies/integration points: depends on UCSI core connector locking, Type-C DP altmode APIs, USB PD VDO helpers, `typec_altmode_vdm`, and UCSI optional altmode override capability.

Risks: without firmware override support, user-initiated changes are rejected after initialization. Status Update is partly guessed because UCSI does not expose the DP Status VDO. Incorrect pin selection can misconfigure mux policy downstream. Work must be canceled on partner removal to avoid use-after-disconnect.

Test signals: DP altmode registration, enter/exit behavior with and without override, `SET_NEW_CAM` command success, generated VDM ACK/NAK behavior, active altmode updates after configure, partner removal cancellation, and DP monitor/mux behavior across reconnects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/displayport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/psy.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/psy.c

Purpose: Exposes each UCSI connector as a USB power_supply device reporting charge state, USB type, online state, voltage/current limits, instantaneous negotiated values, scope, and status.

Important APIs/types/functions: helper getters include `ucsi_psy_get_scope`, `ucsi_psy_get_status`, `ucsi_psy_get_online`, voltage/current getters, `ucsi_psy_get_usb_type`, and `ucsi_psy_get_charge_type`. Public functions are `ucsi_register_port_psy`, `ucsi_unregister_port_psy`, and `ucsi_port_psy_changed`.

Control flow and state: registration builds a name `ucsi-source-psy-<dev><connector>`, sets USB/PD/PPS supported types, and registers with `power_supply_register`. Properties are computed live from cached connector status bitmaps, `rdo`, `src_pdos`, `num_pdos`, and UCSI capability attributes.

Persistence behavior: no persistent storage. Values reflect cached UCSI connector state and are updated through `power_supply_changed` from core event paths.

Dependencies/integration points: compiled when `CONFIG_POWER_SUPPLY` is enabled. Uses USB PD PDO/RDO helpers, UCSI bitfield helpers, device `scope` property, and Type-C/UCSI power-role semantics.

Risks: PD voltage/current calculations only use fixed PDOs; PPS/APDO details are not deeply modeled despite advertising PD_PPS in usb types. If `src_pdos` are not available yet, PD values may be zero. UCSI cannot distinguish all BC charger types, so default-current fallbacks are approximate. Status depends on UCSI 2.0 sink-path status when available.

Test signals: power_supply sysfs values across disconnected, default USB, 1.5A, 3A, BC, and PD contracts; PDO refresh after `ucsi_get_src_pdos`; charge type in sink/source roles; scope override through firmware property; and unregister cleanup on driver removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/psy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/thunderbolt.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/thunderbolt.c

Purpose: Adds Thunderbolt alternate-mode control for UCSI ports that support altmode override, mapping Type-C altmode enter/exit/VDM calls to UCSI `SET_NEW_CAM` and generated Thunderbolt VDM acknowledgements.

Important APIs/types/functions: `struct ucsi_tbt` stores the connector, altmode, work item, CAM offset, and pending VDM header. Main functions are `ucsi_register_thunderbolt`, `ucsi_thunderbolt_enter`, `ucsi_thunderbolt_exit`, `ucsi_thunderbolt_vdm`, `ucsi_thunderbolt_set_altmode`, `ucsi_thunderbolt_work`, and `ucsi_thunderbolt_remove_partner`.

Control flow and state: registration always registers the port altmode, but only installs ops/private state if override is supported. Enter locks the connector, checks current CAM, sends `SET_NEW_CAM` with the requested VDO if no CAM is active, updates active altmode state, and schedules VDM ACK work. Exit sends `SET_NEW_CAM` with enter cleared. Generic incoming VDM init commands are ACKed asynchronously.

Persistence behavior: per-altmode device-managed state exists for the altmode lifetime. Pending VDM header is cleared after work runs; work is canceled on partner removal.

Dependencies/integration points: depends on Type-C Thunderbolt altmode definitions, USB PD VDO helpers, UCSI connector locking, UCSI command encoding, and Type-C altmode VDM delivery.

Risks: if override is not supported, the file registers a passive altmode without active control callbacks. Current CAM index validation must stay aligned with UCSI core altmode arrays. Generated ACKs assume firmware accepted the CAM command and do not carry additional data VDOs.

Test signals: Thunderbolt altmode registration, enter/exit with valid/invalid current CAM, `SET_NEW_CAM` command success/failure, VDM ACK emission, active altmode update, disconnect cancellation, and behavior with override disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/thunderbolt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/trace.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/trace.c

Purpose: Instantiates UCSI tracepoints and supplies string decoders for UCSI command and altmode recipient IDs.

Important APIs/types/functions: `ucsi_cmd_str` maps raw command opcodes to names for core trace output. `ucsi_recipient_str` maps UCSI altmode recipients to port/partner/plug strings. `CREATE_TRACE_POINTS` causes trace events declared in `trace.h` to be generated.

Control flow and state: no driver state. Runtime trace formatting indexes static string tables from command/recipient values. The command helper clamps unknown command IDs to index 0; recipient helper directly indexes its table.

Persistence behavior: none; trace state is owned by ftrace/tracefs.

Dependencies/integration points: includes `ucsi.h` for command constants and `trace.h` for tracepoint declarations. Built conditionally by the Makefile for `CONFIG_TRACING`.

Risks: `ucsi_recipient_str` does not bounds-check recipient values, so malformed trace calls could index outside the table. Command table coverage stops at `GET_ERROR_STATUS`; newer commands trace as unknown unless extended.

Test signals: build with tracing enabled, enable UCSI events, run core commands and altmode registration, and verify readable command/recipient names in trace output including unknown command fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/trace.h -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/trace.h

Purpose: Declares UCSI trace events for command execution, PPM reset, connector status snapshots, port registration, and altmode registration.

Important APIs/types/functions: external format helpers `ucsi_cmd_str` and `ucsi_recipient_str` are declared here. Event classes include `ucsi_log_command`, `ucsi_log_connector_status`, and `ucsi_log_register_altmode`; concrete events include `ucsi_run_command`, `ucsi_reset_ppm`, `ucsi_connector_change`, `ucsi_register_port`, and `ucsi_register_altmode`.

Control flow and state: generated tracepoints copy command return codes, connector status fields via `UCSI_CONSTAT`, and altmode SVID/mode/VDO into trace entries. No persistent driver state is modified.

Persistence behavior: none; trace buffers are external to the driver.

Dependencies/integration points: includes Type-C altmode definitions and relies on `ucsi.h` being included before field helper use through `trace.c`. Uses standard kernel trace include macros with `TRACE_INCLUDE_PATH .` and `TRACE_INCLUDE_FILE trace`.

Risks: trace status decoding reads version-gated bitfields, so invalid or uninitialized connector status may produce warnings or zeros. Trace declarations are sensitive to include order and generated-code conventions.

Test signals: compile with `CONFIG_TRACING`; enable tracepoints during UCSI init, command failures, connector hotplug, and altmode discovery; confirm connector numbers, change masks, RDO, BC status, and altmode SVIDs are meaningful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/ucsi.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/ucsi.c

Purpose: Implements the generic USB Type-C Connector System Software Interface core. It is transport-agnostic and turns UCSI commands/events into Type-C ports, partners, cables, plugs, altmodes, USB role switches, USB PD objects, power_supply updates, and debug/trace signals.

Important APIs/types/functions: exported APIs include `ucsi_create`, `ucsi_register`, `ucsi_unregister`, `ucsi_destroy`, `ucsi_send_command`, `ucsi_notify_common`, `ucsi_sync_control_common`, `ucsi_connector_change`, `ucsi_resume`, and driver-data helpers. Key internal paths are `ucsi_init`, `ucsi_reset_ppm`, `ucsi_register_port`, `ucsi_handle_connector_change`, `ucsi_register_partner`, `ucsi_unregister_partner`, `ucsi_register_altmodes`, `ucsi_pwr_opmode_change`, `ucsi_partner_change`, `ucsi_dr_swap`, and `ucsi_pr_swap`.

Control flow and state: transports create a UCSI instance with `ucsi_operations`, then `ucsi_register` reads the version and queues `ucsi_init_work`. Init resets the PPM, enables basic notifications, reads capabilities, allocates connectors, registers each Type-C port, then enables supported notifications. CCI notifications call `ucsi_notify_common`, which completes pending command/ack completions and schedules connector work. Connector work reads connector status with ACK, reacts to change bits, registers/unregisters partner/cable/plug/altmode/PD objects, updates roles/orientation/mode, and starts deferred partner tasks for PDOs, identity, cable details, connector capability, and altmode checks.

Persistence behavior: all state is in memory: `ucsi` caches version/capabilities/notification mask/flags and owns connectors; each connector caches capability/status bitmaps, role switch, partner/cable/plug, altmode arrays, PD capabilities, PDO/RDO data, telemetry, workqueue, and partner retry tasks. No disk persistence exists.

Dependencies/integration points: relies on transport ops for register/command I/O, Type-C class APIs, USB role switch, USB PD capability APIs, power_supply helper, optional DP/TBT altmode helpers, debugfs, tracing, workqueues, mutexes, completions, and version-gated UCSI bitfield macros.

Risks: command serialization depends on `ppm_lock`, completion flags, and transport correctness. Connector event coalescing uses a single `EVENT_PENDING` bit, so bad firmware notification ordering can delay or drop perceived changes. Deferred partner tasks intentionally retry busy/timeouts but need cleanup on unregister. Role-swap completions depend on connector change events arriving within 5 seconds. Error ACK semantics avoid acknowledging connector changes on command errors, which is correct but can expose firmware quirks.

Test signals: UCSI init/reset logs, trace `ucsi_run_command` and connector events, hotplug/unplug, role swaps, PD and non-PD partners, cable/plug identity, DP/TBT altmode discovery, USB4 partner flags, suspend/resume notification restoration, PPM timeout reset recovery, debugfs commands, and teardown with pending partner tasks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/ucsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/ucsi.h -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/ucsi.h

Purpose: Defines the UCSI core contract, command encodings, bitfield maps, data structures, quirks, optional helper prototypes/stubs, and connector/UCSI state used by all UCSI core and transport files.

Important APIs/types/functions: `struct ucsi_operations` is the transport interface for version/CCI/message reads and sync/async control plus optional connector/altmode hooks. `struct ucsi` stores global version, device, ops, capabilities, connectors, debugfs, init/resume work, PPM lock, notification mask, flags, completion, and quirks. `struct ucsi_connector` stores per-port Type-C objects, altmode arrays, cached bitmaps, power supply, PDO/RDO data, telemetry, PD objects, USB role switch, and identities. Macros encode UCSI commands and read version-gated fields through `UCSI_CONCAP` and `UCSI_CONSTAT`.

Control flow and state: the header does not execute flow, but it defines state ownership and invariants used by `ucsi.c`: one `ucsi` owns an array of connectors; connector cached bitmaps represent the last command responses; ops serialize PPM I/O; optional helper functions compile to stubs when dependencies are disabled.

Persistence behavior: none directly. Structures define in-memory state only.

Dependencies/integration points: includes Linux bitmap, completion, device, power_supply, Type-C, USB PD, USB role, and unaligned helpers. Optional sections integrate with `CONFIG_POWER_SUPPLY`, `CONFIG_TYPEC_DP_ALTMODE`, `CONFIG_TYPEC_TBT_ALTMODE`, and `CONFIG_DEBUG_FS`.

Risks: command and field encodings are protocol-critical; errors affect every transport. `ucsi_bitfield_read` guards minimum version but does not model removed fields. `UCSI_MAX_DATA_LENGTH` changes payload size across UCSI versions, and transports must support the core's requested length. Quirk flags alter PDO timing, partner PDO reads, and USB4/USB interpretation.

Test signals: compile matrix with optional subsystems disabled/enabled, UCSI version 1.0/1.2/2.0/2.1/3.0 behavior, command encoding tests through debugfs or trace, and connector status parsing for orientation, USB4 flags, power readings, PD revision, BC status, and change bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/ucsi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/ucsi_acpi.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/ucsi_acpi.c

Purpose: Implements the ACPI transport for UCSI devices exposed as a memory operation region plus ACPI `_DSM` read/write methods.

Important APIs/types/functions: `struct ucsi_acpi` stores device, UCSI core instance, mapped base address, quirk state, DSM GUID, and last command. Transport ops include `ucsi_acpi_read_version`, `ucsi_acpi_read_cci`, `ucsi_acpi_poll_cci`, `ucsi_acpi_read_message_in`, `ucsi_acpi_async_control`, and either `ucsi_sync_control_common` or LG Gram-specific `ucsi_gram_sync_control`. Probe/remove/resume are `ucsi_acpi_probe`, `ucsi_acpi_remove`, and `ucsi_acpi_resume`.

Control flow and state: probe defers if ACPI dependencies are unmet, maps the memory resource, parses the DSM GUID, selects quirk ops via DMI, creates/registers UCSI, installs an ACPI notify handler, and stores platform data. Reads copy from the mapped UCSI memory area, while async control writes the command to `UCSI_CONTROL`, remembers it, and evaluates the write DSM. Notifications read CCI and call `ucsi_notify_common`. Resume queues generic UCSI resume.

Persistence behavior: state is in memory plus the ACPI operation region owned by firmware. The driver does not persist host state; notification masks are restored by the UCSI core on resume.

Dependencies/integration points: ACPI platform device `PNP0CA0`, `_DSM` UUID `6f8398c2-7ca4-11e4-ad36-631042b5008f`, DMI matching for LG gram, platform memory resources, UCSI core, and ACPI notify handlers.

Risks: firmware DSM failures block reads/writes. Memory-region layout must match UCSI offsets. LG gram quirk clears a bogus power-level/PDO change event after partner source PDO reads; incorrect quirk matching would hide legitimate events or leave bogus loops. Remove unregisters/destroys before removing the notify handler, so handler ordering should be considered under concurrent ACPI notifications.

Test signals: ACPI probe on PNP0CA0, DSM read/write return status, notify-to-CCI delivery, DMI quirk behavior on affected LG systems, suspend/resume notification restoration, and hotplug/role events through the generic UCSI core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/ucsi_acpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/ucsi_ccg.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/ucsi_ccg.c

Purpose: Implements UCSI support for Cypress CCGx Type-C controllers over I2C, including HPI register access, interrupt-to-UCSI op-region caching, NVIDIA altmode quirks, runtime PM, optional firmware update from CYACD images, and sysfs-triggered flashing.

Important APIs/types/functions: `struct ucsi_ccg` stores device/client, UCSI core, firmware/version info, HPI response state, IRQ/work, locks, NVIDIA altmode mapping arrays, spin-protected op-region cache, and PM workaround work. Key functions include `ccg_read/write`, `ccg_op_region_update`, `ucsi_ccg_init`, `ucsi_ccg_sync_control`, `ccg_irq_handler`, `ccg_send_command`, firmware command helpers, `ccg_fw_update_needed`, `do_flash`, `ccg_fw_update`, `ccg_restart`, `ucsi_ccg_probe/remove`, and PM callbacks.

Control flow and state: probe initializes locks/work, reads firmware-name to select NVIDIA build quirks, starts UCSI mode in the CCG controller, reads firmware/device info, creates UCSI with `ucsi_ccg_ops`, requests IRQ, registers UCSI, and enables autosuspend. IRQ handling reads the CCG interrupt register, reads UCSI CCI, copies CCI/message-in into `op_data` before clearing interrupt, then calls `ucsi_notify_common`. Sync control serializes with `uc->lock`, handles multiple-DP CAM remapping, delegates to common UCSI sync, and post-processes GET_CURRENT_CAM, GET_ALTERNATE_MODES, and GET_CAPABILITY for NVIDIA quirks.

Persistence behavior: in-memory state includes cached op-region, firmware versions, altmode remap tables, command response flags, and runtime PM state. Firmware flashing persists to the controller: signed FW config table/signature rows and CYACD rows are written, validated, reset, and ports re-enabled.

Dependencies/integration points: I2C transfer APIs, runtime PM, firmware loader, hex parser, sysfs device attribute `do_flash`, UCSI core, Type-C DP helpers, ACPI/OF/I2C matching, threaded IRQ, and NVIDIA-specific firmware naming conventions.

Risks: firmware update is high blast-radius: bad image format, wrong vendor/build, interrupted flashing, or row-write failure can affect controller bootability. The code must hold `uc->lock` around HPI commands and `op_lock` around cached CCI/message data. Multiple-DP altmode squashing and CAM remapping are subtle and partner-pin-dependent. Runtime resume works around old NVIDIA firmware by manually invoking IRQ handling. `ccg_read/write` use runtime PM around each transfer and need correct adapter quirks handling.

Test signals: I2C read/write success under adapter max-read constraints, UCSI init/start/stop, IRQ CCI/message caching before interrupt clear, NVIDIA multi-DP altmode discovery and `SET_NEW_CAM` remap, Tegra capability masking, runtime resume workaround on old firmware, sysfs `do_flash` with signed/unsigned CYACD images, validation/reset/port re-enable after flash, and remove during pending work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/ucsi_ccg.c -->
