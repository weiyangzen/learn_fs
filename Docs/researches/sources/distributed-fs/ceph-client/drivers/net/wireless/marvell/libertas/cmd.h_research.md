## sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/cmd.h

Purpose: this header defines the command control node and prototypes/macros for Libertas firmware command submission and response/event processing.

Important types and APIs: `struct cmd_ctrl_node` holds list linkage, result, callback and argument, command buffer pointer, and a wait queue flag for synchronous commands. `lbs_cmd()` wraps `__lbs_cmd()` while preserving the caller's original response buffer size; `lbs_cmd_with_response()` uses `lbs_cmd_copyback()`. Prototypes cover async and sync command submission, buffer allocation/free, command execution/completion, response processing, event processing, and specific command helpers for channel, power save, host sleep, radio, MAC control, SNMP, monitor mode, RSSI, 11d, register access, and hardware spec.

Control flow and integration: most driver code includes this header to send firmware commands without knowing queue internals. `cmdresp.c` uses the response/event declarations; cfg/debugfs/ethtool use specific helper prototypes.

State and persistence: the header defines no storage, but `cmd_ctrl_node` instances are allocated by `cmd.c` and stored in `lbs_private`. Callback and wait queue fields determine whether command state is recycled immediately or after synchronous waiters inspect results.

Risks and tests: the `lbs_cmd()` macro temporarily overwrites `hdr.size` with `sizeof(*cmd)` while passing the original expected copyback size; misuse with non-standard command buffers can copy too much or too little. Test signals are compile coverage across all callers and command/response size sanity under firmware interactions.
