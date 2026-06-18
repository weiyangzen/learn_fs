# File Research: sources/block-storage/lvm2/lib/lvmpolld/lvmpolld-client.c

Purpose: implements the client-side connection to `lvmpolld`, allowing LVM commands to delegate long-running polling operations such as pvmove, mirror conversion, and snapshot/thin merge monitoring to the daemon.

Read coverage: complete file read, 364 lines.

Key responsibilities:
- Maintains process-global lvmpolld enablement, socket path, connected state, and `daemon_handle`.
- Opens the daemon using `LVMPOLLD_SOCKET`, protocol name, and protocol version, warning and falling back to local polling if connection fails.
- Builds and sends poll initialization requests for pvmove, conversion, classic snapshot merge, and thin snapshot merge.
- Builds and sends progress requests by LV UUID, optionally including abort requests, `LVM_SYSTEM_DIR`, and devicesfile/system context.
- Interprets daemon responses for in-progress, finished, not-found, invalid, failed, signal termination, and child command return codes.
- Maps LVM2 and lvmpolld-specific return codes to user-facing errors and points users to daemon logs.

Important entry points:
- `lvmpolld_set_active()`, `lvmpolld_set_socket()`, `lvmpolld_use()`, `lvmpolld_disconnect()`.
- `lvmpolld_poll_init()` starts a daemon-tracked operation.
- `lvmpolld_request_info()` checks completion and success/failure of a daemon-tracked operation.

Dependencies:
- Uses libdaemon client I/O, `lvmpolld-protocol.h`, exported metadata LV type flags, `polldaemon.h`, command context, and LVM command return codes.
- Depends on `daemon_request_extend()`, `daemon_send()`, and `daemon_reply_*()` parsing.

Risk and edge cases:
- `lvmpolld_use()` requires both global enablement and a configured socket path; disabled or missing socket returns local polling.
- Requests are keyed by LV UUID and require VG/LV names for logging and daemon parameters.
- The interval string buffer is intentionally small but checked for truncation.
- Error handling must destroy both requests and replies on every path.
- Finished daemon operations can fail either by signal or by LVM child command return code, and both cases are surfaced differently.
