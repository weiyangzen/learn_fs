# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/msg.c

Purpose: provides the SCMI message-passing transport SDU packing and unpacking operations for transports built around a contiguous message buffer rather than the shared-memory helper. It translates between `struct scmi_xfer` and the on-wire little-endian SCMI message layout.

Important APIs/types/functions: `struct scmi_msg_payld` defines the transport SDU as a 32-bit SCMI message header followed by a flexible little-endian payload array. `msg_command_size()` and `msg_response_size()` report command and response SDU lengths. `msg_tx_prepare()` writes the packed header and command payload. `msg_read_header()` extracts the SCMI header. `msg_fetch_response()` stores SCMI status and response payload into the xfer. `msg_fetch_notification()` copies notification payloads. `scmi_message_operations_get()` returns the static `scmi_message_operations` table to `driver.c`.

Control flow: a transport asks the core for these operations during SCMI driver init when message transport support is enabled. Before send, `msg_tx_prepare()` writes `pack_scmi_header(&xfer->hdr)` and copies `xfer->tx.buf` when present. On receive, the transport or core reads the header with `msg_read_header()`, then either fetches a response, where payload word zero is the SCMI status, or fetches a notification, where payload begins immediately after the header.

State and persistence behavior: this file has no persistent state and allocates no memory. It only reads from and writes to caller-owned transport buffers and xfer buffers. Response length is clamped to the smaller of the expected RX size and actual available bytes after the header/status prefix.

Dependencies and integration points: depends on `common.h` for `struct scmi_xfer`, `pack_scmi_header()`, and `struct scmi_message_operations`. It is wired into `scmi_trans_core_ops.msg` by `scmi_driver_init()` when `CONFIG_ARM_SCMI_HAVE_MSG` is enabled and is then consumed by message-based transports.

Risks and test signals: callers must provide a valid SDU buffer with enough bytes for the selected operation; short responses produce zero-length payloads after status clamping but still read status from payload word zero. Tests should verify little-endian header/status conversion, command size and response size accounting, zero-length command payloads, truncated responses, max-length notification clamping, and that notifications do not interpret the first payload word as status.
