# sources/distributed-fs/ceph-client/drivers/net/wireguard/version.h

Purpose: Defines the WireGuard module version string.

Important APIs and definitions: `WIREGUARD_VERSION` is set to `"1.0.0"` and consumed by `main.c` for `MODULE_VERSION()` and load-time `pr_info()`.

Control flow: No executable flow.

State and persistence: No runtime state. The macro contributes to module metadata and logs.

Dependencies and integration points: Included by `main.c`.

Risks: Version drift can mislead userspace/log readers if code changes without updating the macro.

Test signals: Module metadata inspection and load log should report the expected version.
