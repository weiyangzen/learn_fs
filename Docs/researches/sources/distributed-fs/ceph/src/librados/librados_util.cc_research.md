# sources/distributed-fs/ceph/src/librados/librados_util.cc

## Purpose
This file provides small translation helpers shared by librados public API wrappers. It maps public checksum, per-op, and operation submission flags to internal Ceph OSD flag constants.

## Important APIs, Types, and Functions
`get_checksum_op_type(rados_checksum_type_t)` maps `LIBRADOS_CHECKSUM_TYPE_XXHASH32`, `XXHASH64`, and `CRC32C` to `CEPH_OSD_CHECKSUM_OP_TYPE_*`, returning `-1` for unknown types despite the `uint8_t` return type. `get_op_flags(int)` maps `LIBRADOS_OP_FLAG_*` values such as exclusive create, failok, and fadvise hints to `CEPH_OSD_OP_FLAG_*`. `translate_flags(int)` maps C++ `librados::OPERATION_*` submission flags to `CEPH_OSD_FLAG_*`, including read balancing/localization, read-write ordering, cache/overlay/redirect controls, full handling, ordersnap, and return-vector behavior.

## Control Flow
Each function is a direct bitmask or switch translator. Unknown bit values are ignored by the two flag translators. Unknown checksum type produces the sentinel value used by callers such as `ObjectReadOperation::checksum()` and `IoCtx::checksum()`.

## State and Persistence Behavior
No state is stored. The behavior influences persistent operations indirectly because wrong mappings would change how OSDs execute writes, reads, cache hints, full-cluster policy, or checksum requests.

## Dependencies and Integration Points
The helpers depend on public librados constants, internal OSD constants, and `librados_util.h`. They are used by `librados_cxx.cc` operation builders and submit paths.

## Risks and Test Signals
The main risk is semantic drift when new public flags or checksum types are added without updating these mappings. The `uint8_t` return of `-1` should be tested because callers may pass an invalid checksum op to lower layers if they do not validate. Tests should cover each flag bit independently and combinations of flags passed through `IoCtx::operate()` and aio variants.
