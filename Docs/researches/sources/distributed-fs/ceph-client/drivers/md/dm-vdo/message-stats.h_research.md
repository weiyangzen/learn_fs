# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/message-stats.h

## Purpose
`message-stats.h` declares the public VDO status/config serialization functions.

## Important APIs, Types, and Functions
It declares `vdo_write_config(struct vdo *vdo, char **buf, unsigned int *maxlen)` and `vdo_write_stats(struct vdo *vdo, char *buf, unsigned int maxlen)`.

## Control Flow
The header defines no logic. Status paths call these functions with a VDO instance and output buffer to produce current config or stats text.

## State and Persistence Behavior
No state is declared. Output is transient and derived from live VDO state.

## Dependencies and Integration Points
It includes `types.h` for `struct vdo` visibility. It is used by device-mapper target/status code.

## Risks and Edge Cases
Callers must pass valid buffers and lengths; `vdo_write_config()` mutates the buffer pointer and length by reference, while `vdo_write_stats()` takes them by value.

## Test Signals
Compile coverage in status code and runtime status/config output validation are the main signals.
