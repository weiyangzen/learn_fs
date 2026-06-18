# sources/distributed-fs/ceph-client/include/linux/blk-cgroup.h

## Purpose
`blk-cgroup.h` declares the common block I/O controller cgroup interface used to associate bios with block cgroups, throttle current tasks, observe congestion, and carry Fibre Channel application identifiers.

## Important APIs, Types, And Functions
With `CONFIG_BLK_CGROUP`, the header exposes `blkcg_root_css`, `blkcg_schedule_throttle()`, `blkcg_maybe_throttle_current()`, `blk_cgroup_congested()`, `blkcg_pin_online()`, `blkcg_unpin_online()`, `blkcg_get_cgwb_list()`, and `bio_blkcg_css()`. Without cgroup block support, it provides inert fallbacks: root CSS is an `ERR_PTR(-EINVAL)`, throttling is a no-op, congestion is false, and `bio_blkcg_css()` returns `NULL`.

The Fibre Channel app-id helpers `blkcg_set_fc_appid()` and `blkcg_get_fc_appid()` are declared outside the config block. `FC_APPID_LEN` defines the maximum application identifier storage length.

## Control Flow And State
The header itself owns no state; all state lives in cgroup subsystem state, bios, request queues, and block-cgroup internals. The config-gated wrappers make caller code compile regardless of kernel configuration while preserving behavior only when the block cgroup controller exists. Pin/unpin calls imply lifetime protection for online cgroups; throttle calls integrate with scheduling and memdelay behavior.

## Dependencies And Integration Points
It depends on `linux/types.h` and forward declarations for `bio`, `cgroup_subsys_state`, and `gendisk`. `blk_types.h` stores per-bio cgroup data under `CONFIG_BLK_CGROUP`, and `request_queue` stores policy bitmaps and root block groups. The app-id functions integrate with FC storage paths and cgroup identity.

## Risks And Test Signals
Risks include forgetting that cgroup helpers may be compiled out, using `blkcg_root_css` without checking the error pointer in non-cgroup builds, and mishandling cgroup lifetime around online pinning. Test signals include builds with and without `CONFIG_BLK_CGROUP`, throttling behavior under cgroup I/O limits, bio-to-cgroup attribution, and app-id length validation.
