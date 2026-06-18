# sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/trace.h

Purpose: Declares UCSI trace events for command execution, PPM reset, connector status snapshots, port registration, and altmode registration.

Important APIs/types/functions: external format helpers `ucsi_cmd_str` and `ucsi_recipient_str` are declared here. Event classes include `ucsi_log_command`, `ucsi_log_connector_status`, and `ucsi_log_register_altmode`; concrete events include `ucsi_run_command`, `ucsi_reset_ppm`, `ucsi_connector_change`, `ucsi_register_port`, and `ucsi_register_altmode`.

Control flow and state: generated tracepoints copy command return codes, connector status fields via `UCSI_CONSTAT`, and altmode SVID/mode/VDO into trace entries. No persistent driver state is modified.

Persistence behavior: none; trace buffers are external to the driver.

Dependencies/integration points: includes Type-C altmode definitions and relies on `ucsi.h` being included before field helper use through `trace.c`. Uses standard kernel trace include macros with `TRACE_INCLUDE_PATH .` and `TRACE_INCLUDE_FILE trace`.

Risks: trace status decoding reads version-gated bitfields, so invalid or uninitialized connector status may produce warnings or zeros. Trace declarations are sensitive to include order and generated-code conventions.

Test signals: compile with `CONFIG_TRACING`; enable tracepoints during UCSI init, command failures, connector hotplug, and altmode discovery; confirm connector numbers, change masks, RDO, BC status, and altmode SVIDs are meaningful.
