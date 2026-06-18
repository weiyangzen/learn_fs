# File Research: sources/block-storage/lvm2/lib/lvmpolld/lvmpolld-client.h

Purpose: declares the lvmpolld client API and provides no-op fallbacks when LVM is built without `LVMPOLLD_SUPPORT`.

Read coverage: complete file read, 52 lines.

Key contents:
- Defines the default daemon socket path as `DEFAULT_RUN_DIR "/lvmpolld.socket"`.
- Forward-declares `cmd_context`, `poll_operation_id`, and `daemon_parms`.
- Declares connection, enablement, socket override, poll initialization, and progress request functions.
- Provides macro stubs returning false/no-op behavior when lvmpolld support is not compiled in.

Dependencies:
- Includes `libdaemon/client/daemon-client.h` only under `LVMPOLLD_SUPPORT`.
- Consumed by polling command paths that can transparently fall back to foreground polling.

Risk and edge cases:
- Callers must not assume lvmpolld is available: the header intentionally compiles all calls to no-ops in unsupported builds.
- `lvmpolld_poll_init()` and `lvmpolld_request_info()` return `0` in unsupported builds, so higher-level polling paths must handle fallback behavior.
