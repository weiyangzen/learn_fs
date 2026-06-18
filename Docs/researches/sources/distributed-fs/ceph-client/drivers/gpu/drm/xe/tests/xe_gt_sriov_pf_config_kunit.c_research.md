# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/tests/xe_gt_sriov_pf_config_kunit.c

## Purpose

`xe_gt_sriov_pf_config_kunit.c` tests SR-IOV PF fair resource partitioning for GuC contexts, doorbells, GGTT, and local memory across 1 to 63 VFs.

## Important APIs, Types, and Functions

- Setup helpers: `pf_set_admin_mode`, `pf_set_usable_vram`, `num_vfs_gen_param`, and `pf_gt_config_test_init`.
- Fair-share tests: `fair_contexts_1vf`, `fair_contexts`, `fair_doorbells_1vf`, `fair_doorbells`, `fair_ggtt_1vf`, `fair_ggtt`, `fair_vram_1vf`, `fair_vram_1vf_admin_only`, and `fair_vram`.
- Parameter data: `TEST_MAX_VFS`, `TEST_VRAM`, and `vram_sizes`.
- Suite: `pf_gt_config_suite`.

## Control Flow

The init path creates a fake BMG SR-IOV PF device, attaches fake VRAM, installs LMTT ops, sets total/driver VF limits, disables admin-only mode, and calls `xe_sriov_init`. Parameterized tests toggle admin-only mode and VF counts, then assert fair-share functions return aligned, power-of-two, capacity-respecting values with specific thresholds.

## State and Persistence Behavior

The tests mutate fake device SR-IOV PF fields, admin-only state, VRAM usable size, tile VRAM pointers, and LMTT ops. No live hardware state is touched.

## Dependencies and Integration Points

It depends on KUnit static/fake device helpers, `xe_sriov_init`, PF profile functions (`pf_profile_fair_ctxs`, `pf_profile_fair_dbs`, `pf_profile_fair_ggtt`, `pf_profile_fair_lmem`), GuC ID/doorbell limits, LMTT ops, and VRAM region helpers.

## Risks and Edge Cases

- Threshold expectations encode policy; intentional resource policy changes require updating tests.
- `TEST_VRAM` is chosen to work on 32-bit but may not represent all real device sizes.
- The fake device must remain close enough to real PF initialization for profile results to be meaningful.

## Test Signals

Passing tests indicate fair shares remain aligned, power-of-two, and within available contexts/doorbells/GGTT/VRAM. Admin-only single-VF cases verify reserved PF resources are accounted differently.
