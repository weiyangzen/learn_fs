# sources/distributed-fs/ceph-client/net/batman-adv/bat_v.h

## Purpose
`bat_v.h` declares BATMAN V lifecycle hooks and provides no-op stubs when `CONFIG_BATMAN_ADV_BATMAN_V` is disabled.

## Important APIs
- Enabled builds declare `batadv_v_init`, `batadv_v_hardif_init`, `batadv_v_mesh_init`, and `batadv_v_mesh_free`.
- Disabled builds inline all four functions as harmless no-ops or success returns.

## Control Flow and Integration
Always-built core code can call BATMAN V setup functions unconditionally. Kconfig and Makefile decide whether real implementations from `bat_v.c` are linked or the inline stubs are used.

## State and Persistence
No header-local state. The stubs ensure no BATMAN V state is initialized when the feature is disabled.

## Risks and Test Signals
Risks are mismatches between conditional declarations and Makefile object inclusion. Test signals include builds with `CONFIG_BATMAN_ADV_BATMAN_V=y` and `n`, and runtime confirmation that `BATMAN_V` is absent from routing algorithm dumps when disabled.
