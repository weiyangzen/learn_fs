# sources/distributed-fs/ceph-client/drivers/s390/cio/idset.c

Purpose: implements a bitmap-backed set of subchannel IDs used by CSS/CIO scanning logic.

Important APIs/types/functions: `struct idset` stores SSID and ID dimensions plus a flexible bitmap. Public functions allocate/free sets, fill them, add/delete/check subchannel IDs, delete subsequent IDs in an SSID range, test emptiness, and OR one set into another.

Control flow: `idset_sch_new()` sizes the set from global `max_ssid` and `__MAX_SUBCHANNEL`. Operations map `(ssid, sch_no)` to `ssid * num_id + id` and then use bitmap primitives. `idset_sch_del_subseq()` clears from a given subchannel number to the end of that SSID.

State and persistence behavior: state is heap/vmalloc bitmap memory only. The set persists until `idset_free()` and has no locking of its own, so callers own synchronization.

Dependencies and integration points: depends on `css.h` for `max_ssid`, `asm/schid.h` for `struct subchannel_id`, and Linux bitmap/vmalloc helpers. It is a local utility for channel-subsystem evaluation.

Risks and test signals: callers must not pass out-of-range SSIDs or subchannel numbers. `idset_add_set()` only ORs the minimum shared bit length, so differently sized sets truncate to the smaller dimension. Tests should cover allocation sizing, fill/empty, add/delete/contains across multiple SSIDs, subsequence clearing, and OR of mismatched dimensions.
