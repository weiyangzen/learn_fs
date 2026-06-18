# sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/efa_common_defs.h

Provides common EFA definition helpers: spec version constants, bitfield access macros, and the shared low/high 32-bit memory-address structure.

The key APIs are `EFA_GET(ptr, mask)`, `EFA_SET(ptr, mask, value)`, `EFA_COMMON_SPEC_VERSION_MAJOR`, `EFA_COMMON_SPEC_VERSION_MINOR`, and `struct efa_common_mem_addr`. The macros use Linux `FIELD_GET` and `FIELD_PREP` with EFA's convention that a logical field name maps to a `_MASK` symbol.

There is no standalone control flow. The macros are expanded in command construction, completion parsing, host-info setup, and register or descriptor interpretation. The file owns no state; callers mutate descriptor words in place or embed the common memory-address struct in firmware-visible commands.

Dependencies are limited to `<linux/bitfield.h>`, but the integration surface is broad because generated admin and IO definitions depend on this convention. Risks include passing the wrong field width, using a missing or stale mask, or relying on `EFA_SET` to clear unrelated bits. Test signals are build failures for missing masks and runtime correctness of decoded capabilities, host-info fields, and multi-flag command descriptors.
