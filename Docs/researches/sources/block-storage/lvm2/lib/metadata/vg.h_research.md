# File Research: sources/block-storage/lvm2/lib/metadata/vg.h

This header defines the `struct volume_group` data model and public VG helper prototypes.

Key definitions:
- `alloc_policy_t` enum for allocation policy: invalid, contiguous, cling, internal cling-by-tags, normal, anywhere, inherit.
- Persistent reservation flags: `VG_PR_REQUIRE`, `VG_PR_AUTOSTART`, `VG_PR_PTPL`.
- `MAX_EXTENT_COUNT` as `UINT32_MAX`.

`struct volume_group` contains:
- Command/context pointers, memory pool, format instance, cache info, sequence number, status flags, write/backup state.
- Committed and precommitted metadata copies.
- Allocation policy, profile, status bits, radix trees for LV/PV name and UUID lookup.
- Identity fields: VG id, name, old name, system id, lock type/args.
- Extent accounting, max LV/PV, PV/LV/historical LV/tag lists.
- Removed LV/PV tracking lists, metadata area copy target, persistent reservation state.
- Special LVs: pool metadata spare and sanlock LV.
- Message and lockd-free LV lists.

Public API:
- VG allocation/free, string duplication, accessors, setters, sizing, metadata area metrics, attribute/tag/UUID formatting, visible LV and snapshot counts, and backup trigger.

Dependencies:
- `lib/id/id.h`, `libdevmapper`, `cmd_context`, `format_instance`, and `logical_volume`.

Risks:
- Many list/radix members are maintained by separate metadata subsystems; callers must preserve invariants when adding/removing LVs or PVs.
- Comments make clear that `vg_committed == NULL` implies committed copy, but non-NULL equality is not guaranteed.
