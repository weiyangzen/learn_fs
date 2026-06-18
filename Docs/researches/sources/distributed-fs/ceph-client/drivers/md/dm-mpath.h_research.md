
# sources/distributed-fs/ceph-client/drivers/md/dm-mpath.h

## Purpose
Shared private header for multipath path objects. It defines the minimal path structure visible to path selector modules and declares the callback used by hardware handler path-group initialization completion.

## Important APIs, Types, And Functions
`struct dm_path` contains a read-only `struct dm_dev *dev` and opaque `pscontext` for path-selector-private state. `dm_pg_init_complete(struct dm_path *path, unsigned int err_flags)` is declared for device-handler users that need to report path-group initialization completion.

## Control Flow
The header has no runtime flow. `dm-mpath.c` embeds `struct dm_path` in its internal `struct pgpath`, passes it to path selector callbacks, and converts back with `container_of()`. Path selectors store per-path state through `pscontext`.

## State And Persistence
Only in-memory path references are represented. There is no persistence and no ownership management in this header; target construction/destruction in `dm-mpath.c` owns device references.

## Dependencies And Integration Points
Included by `dm-path-selector.h` and path selector implementations. It bridges multipath internals and selector modules while keeping most multipath state private to `dm-mpath.c`.

## Risks
The `dev` field is documented read-only; selector modules must not drop or replace the device reference. `pscontext` lifetime must be managed consistently by selector `add_path`, `fail_path`, `reinstate_path`, and `destroy` callbacks.

## Test Signals
Compile all path selector modules against this header, validate selector private context lifetime on path add/fail/reinstate/destroy, and verify any users of `dm_pg_init_complete()` match the multipath path lifetime.
