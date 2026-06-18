# File Research: sources/block-storage/lvm2/lib/properties/prop_common.c

This file implements generic property get/set dispatch.

Main APIs:
- `prop_not_implemented_get()`, `prop_not_implemented_set()` log `ENOSYS`.
- `prop_get_property()`.
- `prop_set_property()`.

Behavior:
- Both dispatchers linearly scan a sentinel-terminated `struct lvm_property_type` array by `id`.
- `prop_get_property()` validates requested type mask, copies the descriptor to the caller’s `prop`, then invokes the property getter.
- `prop_set_property()` validates existence, settable flag, and type mask, copies string or integer value from caller prop into descriptor, then invokes setter.

Dependencies:
- `prop_common.h`, logging with errno.

Risks:
- Property arrays must be sentinel-terminated with `id[0] == 0`.
- Setter copies only string/integer union members; signed integer fields depend on compatible representation/usage.
