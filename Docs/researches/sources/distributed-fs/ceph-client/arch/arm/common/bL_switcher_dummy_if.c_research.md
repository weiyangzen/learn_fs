<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/bL_switcher_dummy_if.c -->
# sources/distributed-fs/ceph-client/arch/arm/common/bL_switcher_dummy_if.c

## Purpose
Debug-only misc-device user interface for triggering big.LITTLE switch requests from userspace.

## Important APIs/types/functions
- `bL_switcher_write()` parses three-byte input `<cpu>,<cluster>`.
- Misc device: `/dev/b.L_switcher` with dynamic minor and `.write` handler.
- Calls `bL_switch_request(cpu, cluster)`.

## Control flow
Userspace writes at least three bytes. The driver copies the first three bytes, validates digit-comma-cluster format, converts one decimal CPU digit and cluster digit, then delegates to the switcher core.

## State and persistence behavior
No persistent state beyond misc-device registration. It causes state changes in `bL_switcher.c` by enqueueing switch requests.

## Dependencies and integration points
Depends on miscdevice, uaccess, module registration, and the exported big.LITTLE switcher API.

## Risks and edge cases
Only single-digit CPU IDs and cluster `0` or `1` are accepted. Input beyond three bytes is ignored. This is intentionally a debugging interface, so exposing it in production can let privileged users trigger disruptive CPU migration paths.

## Test signals
Build with `CONFIG_BL_SWITCHER_DUMMY_IF`, confirm `/dev/b.L_switcher` exists, write values like `0,1`, and verify switcher trace events or callback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/bL_switcher_dummy_if.c -->
