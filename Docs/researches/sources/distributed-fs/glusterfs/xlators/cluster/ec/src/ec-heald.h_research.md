# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-heald.h

## Purpose
Declares the EC self-heal daemon interface used outside `ec-heald.c`: management operation dispatch, daemon lifecycle, and index-healer wakeup after replacement or new dirty-index work.

## Important APIs, types, and functions
`ec_xl_op(xlator_t *this, dict_t *input, dict_t *output)` handles SHD management requests such as full and index heals. `ec_selfheal_daemon_init(xlator_t *this)` allocates and initializes per-brick healer objects. `ec_shd_index_healer_wake(ec_t *ec)` wakes index healer threads for currently up bricks. `ec_selfheal_daemon_fini(xlator_t *this)` tears down SHD healer objects.

## Control flow
The EC translator initializes SHD structures during xlator startup, accepts management operations through `ec_xl_op()`, wakes index workers when dirty index processing should resume, and finalizes worker synchronization objects on shutdown when running as self-heald.

## State and persistence behavior
The header does not define state directly, but its functions operate on `ec_t`, `ec_self_heald_t`, and `struct subvol_healer` state declared in `ec-types.h`. Persistence is indirect through the daemon's heal operations and index purges.

## Dependencies and integration points
Includes `ec-types.h`, Gluster dictionaries, globals, and `xlator_t`. It is included by `ec-heal.c` for `ec_shd_index_healer_wake()` after replace-brick heal, by `ec-heald.c` for its own public definitions, and by EC translator setup/management code for lifecycle and `xl-op` routing.

## Risks and test signals
The surface is small, but ABI/API drift between this header and `ec-heald.c` would break SHD startup or management heal commands. Tests should confirm startup/fini calls are guarded by SHD mode, `ec_xl_op()` recognizes expected management operation dictionaries, and replace-brick paths can call the wake function without circular initialization problems.
