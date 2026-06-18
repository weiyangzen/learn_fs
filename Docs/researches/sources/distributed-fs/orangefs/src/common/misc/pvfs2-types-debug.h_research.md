# sources/distributed-fs/orangefs/src/common/misc/pvfs2-types-debug.h

Purpose: Provides inline debugging helpers for printing OrangeFS object attribute types and attrmask contents through the gossip logging subsystem.

Important APIs and functions: `PINT_attr_dump_object_type` logs the decoded `PVFS_object_type` when `PVFS_ATTR_COMMON_TYPE` is set. `PINT_attrmask_print` logs each recognized `PVFS_ATTR_*` bit in a `uint32_t` object-attribute mask.

Control flow: Both functions are `static inline` and execute only logging calls. The object-type helper switches over known values from `PVFS_TYPE_NONE` through `PVFS_TYPE_INTERNAL`; the attrmask helper checks each supported bit independently so composite masks print one line per bit.

State and persistence: Stateless. Output goes to gossip debug sinks selected elsewhere; no data is persisted by this header.

Dependencies and integration points: Includes `gossip.h` and `pvfs2-types.h`. Used by getattr/setattr and utility code when diagnosing mask conversion or server-returned attributes.

Risks: Unknown object types are silently ignored. Labels contain minor spelling/name drift for symlink and distributed-directory mask strings, which can affect log-based diagnostics. As inline header code, any change recompiles many dependent modules.

Test signals: Log masks with no bits, every individual bit, all bits, unknown future bits, and every object type including invalid values. Verify expected strings under enabled and disabled gossip masks.
