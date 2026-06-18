# sources/distributed-fs/ceph-client/scripts/dtc/libfdt/fdt_overlay.c

Purpose: implements device-tree overlay application: target resolution, phandle rebasing, external fixup resolution, conflict prevention, overlay merge, and symbol update.

Important APIs/functions: public `fdt_overlay_target_offset()` resolves fragment targets by `target` phandle or `target-path`. Public `fdt_overlay_apply()` performs the full pipeline. Private helpers adjust overlay phandles (`overlay_adjust_local_phandles`), rewrite local references from `/__local_fixups__`, resolve `/__fixups__` through base `/__symbols__`, prevent overwriting base phandles, recursively merge `__overlay__` content, and update base `__symbols__` paths for subsequent overlays.

Control flow/state: `fdt_overlay_apply()` first probes both blobs, finds base max phandle as `delta`, mutates the overlay in place, mutates the base during merge/symbol update, and invalidates the overlay magic on both success and error; on error it also invalidates base magic because partial mutation may have occurred.

Dependencies/integration: uses almost every libfdt traversal and mutation primitive: `fdt_for_each_subnode`, property iterators, `fdt_getprop*`, `fdt_setprop*`, `fdt_add_subnode`, `fdt_path_offset`, phandle helpers, and unaligned `fdt32_ld/st`.

Risks: overlay application is intentionally non-atomic. Malformed fixup strings, invalid offsets, missing symbols, phandle overflow, and insufficient base slack can corrupt working copies. `fdto` must be disposable after calling.

Test signals: phandle and target-path fragments, local fixups, external fixups via symbols, missing symbols, phandle collisions, symbol propagation, nested overlay nodes, root-target paths, malformed fixup properties, and error-time magic invalidation.
