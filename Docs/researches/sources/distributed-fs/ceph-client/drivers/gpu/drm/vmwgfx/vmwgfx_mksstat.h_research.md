# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_mksstat.h

Purpose: Defines optional kernel-side mksGuestStat counter support. When `CONFIG_DRM_VMWGFX_MKSSTATS` is enabled, it exposes counter IDs, page-layout helpers, and timing macros used to record nested self/total cycle counts into shared mksGuestStat pages.

Important APIs/types/functions: `mksstat_kern_stats_t` currently enumerates `MKSSTAT_KERN_EXECBUF` and `MKSSTAT_KERN_COTABLE_RESIZE`, with `MKSSTAT_KERN_COUNT` as the sentinel. `vmw_mksstat_get_kern_pstat()`, `_pinfo()`, and `_pstrs()` compute offsets from the descriptor base page to stat, info, and string pages. `struct mksstat_timer_t` stores the previous top timer, TSC start, and per-pid slot. `MKS_STAT_TIME_DECL`, `MKS_STAT_TIME_PUSH`, and `MKS_STAT_TIME_POP` wrap measured regions.

Control flow: The declaration macro samples `rdtsc()` and obtains a slot from `vmw_mksstat_get_kern_slot(current->pid, dev_priv)`. Push records the current top timer and installs the new counter. Pop reserves the slot by atomically replacing the pid with `MKSSTAT_PID_RESERVED`, restores the top timer, updates count/self/total cycles, subtracts nested elapsed time from the parent self counter, and releases the slot back to the pid.

State and persistence: Per-process stat state lives in arrays on `dev_priv` (`mksstat_kern_pids`, `mksstat_kern_top_timer`, `mksstat_kern_pages`). The backing pages are registered with the hypervisor by code in `vmwgfx_msg.c`. With the config disabled, all macros compile to no-ops.

Dependencies and integration points: Requires page-size layout constants, `rdtsc`, current task pid, atomic64 counters, and MKSGuestStat structures from device headers. Risks include TSC availability/ordering assumptions, strict enum ordering matching page initialization, slot contention returning a negative slot and silently disabling timing, and macro dependence on a visible `dev_priv` variable. Test signals include config-enabled builds, nested timer accounting, concurrent process slots, cleanup/reset paths, and disabled-config compilation.
