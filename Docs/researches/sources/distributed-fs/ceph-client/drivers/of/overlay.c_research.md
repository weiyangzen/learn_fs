# sources/distributed-fs/ceph-client/drivers/of/overlay.c

## Purpose
Implements Linux Open Firmware device-tree overlay application and removal. It accepts an overlay FDT, unflattens it into a detached overlay tree, resolves phandles, converts fragments into an `of_changeset`, applies the changeset to the live tree, and later reverts overlays in topmost order.

## Important APIs, types, and functions
- Public API: `of_overlay_fdt_apply()`, `of_overlay_remove()`, `of_overlay_remove_all()`, `of_overlay_notifier_register()`, `of_overlay_notifier_unregister()`, `of_overlay_mutex_lock()`, and `of_overlay_mutex_unlock()`.
- Core state type: `struct overlay_changeset`, carrying the overlay id, IDR/list membership, backing FDT memory, unflattened overlay root, notifier state, fragment table, symbols flag, and embedded `struct of_changeset`.
- Overlay model helpers: `struct fragment` maps a fragment `__overlay__` node to a live target; `struct target` tracks whether recursion is operating in the live tree or in newly attached overlay nodes.
- Build path: `init_overlay_changeset()`, `find_target()`, `build_changeset()`, `build_changeset_next_level()`, `add_changeset_node()`, and `add_changeset_property()`.
- Removal path: `overlay_removal_is_ok()`, `node_overlaps_later_cs()`, and `find_node()`.

## Control flow
`of_overlay_fdt_apply()` validates FDT header and size, allocates an overlay changeset, assigns an ID, links it into global state, copies and aligns the FDT, unflattens it, then calls `of_overlay_apply()` while holding overlay and OF mutexes. `of_overlay_apply()` resolves phandles, initializes fragments, sends pre-apply notifications, builds the changeset, applies entries, sends changeset entry notifications, and sends post-apply notifications.

## State and persistence behavior
State is kernel memory only: `ovcs_idr`, `ovcs_list`, `devicetree_state_flags`, the copied FDT, the unflattened overlay memory, and the embedded changeset. Sticky corruption flags refuse later operations after uncertain rollback state. Overlay IDs persist until removed.

## Dependencies and integration points
Depends on libfdt, OF dynamic changesets, `of_resolve_phandles()`, notifier chains, `idr`, global `of_mutex`, and OF reconfiguration consumers such as platform population.

## Risks and edge cases
Partial apply/revert can make tree state uncertain; notifiers must not retain overlay pointers beyond allowed windows; duplicate entries are rejected; overlapping overlays must be removed topmost first; updating live properties outside overlay-created nodes warns about leaks.

## Test signals
Covered by `unittest.c` overlay cases and `overlay_test.c` KUnit tests for apply, platform-device creation, cleanup, duplicate errors, bad fixups, notifier errors, and topmost removal.
