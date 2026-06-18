# sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/debugfs.c

Purpose: Exposes a debugfs interface under the USB debug root for issuing selected raw UCSI commands and reading command responses plus UCSI 2.1 current/voltage telemetry.

Important APIs/types/functions: `ucsi_cmd` validates command opcodes and calls `ucsi_send_command`; `ucsi_resp_show` prints the stored 128-bit response; `ucsi_peak_curr_show`, `ucsi_avg_curr_show`, and `ucsi_vbus_volt_show` expose connector telemetry; `ucsi_debugfs_register/unregister/init/exit` manage dentries and `struct ucsi_debugfs_entry`.

Control flow and state: module init creates the top-level `ucsi` debugfs directory. Each registered UCSI instance allocates a debugfs entry and creates `command`, `response`, `peak_current`, `avg_current`, and `vbus_voltage`. Writing a command clears prior response/status, routes set-like commands without response storage and get-like commands into `debugfs->response`.

Persistence behavior: only last command response and status are cached in memory for each UCSI instance. Debugfs files disappear on unregister or module exit.

Dependencies/integration points: depends on `CONFIG_DEBUG_FS`, `usb_debug_root`, UCSI core command encoding, and cached connector telemetry maintained in `ucsi_handle_connector_change`.

Risks: raw command injection can perturb live Type-C policy and should be treated as a diagnostic-only interface. The telemetry helpers read `ucsi->connector` without selecting a connector index, so they effectively expose connector 1. Response storage is only 128 bits, which may be smaller than some modern UCSI payloads.

Test signals: debugfs directory/file creation, accepted/rejected opcodes, response formatting, error propagation through `status`, cleanup on `ucsi_destroy`, and telemetry changes after UCSI 2.1 power-reading-ready connector updates.
