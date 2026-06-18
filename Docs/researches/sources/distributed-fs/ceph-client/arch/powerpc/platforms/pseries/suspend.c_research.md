# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/suspend.c

Purpose: Exposes pSeries partition hibernation/suspend-to-memory coordination through `/sys/power/hibernate` and platform suspend ops.

Important APIs/types/functions: Defines `pseries_suspend_begin()`, `pseries_suspend_enter()`, sysfs `store_hibernate()`/`show_hibernate()`, `suspend_subsys`, `pseries_suspend_ops`, sysfs registration helper, and `pseries_suspend_init()`.

Control flow: Init on LPAR creates a custom `power` bus root with a `hibernate` attribute and installs suspend ops. Writing a stream id requires `CAP_SYS_ADMIN`, polls `H_VASI_STATE` until firmware reports suspending rather than enabled, invokes `pm_suspend(PM_SUSPEND_MEM)`, and on success runs `post_mobility_fixup()`. Enter calls `rtas_ibm_suspend_me()`.

State and persistence: Keeps a static device for the suspend sysfs bus. Hibernation stream state lives in firmware and post-resume device-tree fixups update runtime state.

Dependencies and integration points: Depends on PAPR VASI hcall, RTAS suspend-me, generic PM suspend core, pseries mobility fixups, firmware LPAR feature detection, and capability checks.

Risks: The sysfs bus name overlaps conceptually with generic power sysfs. `simple_strtoul()` parsing accepts trailing junk. Polling `-EAGAIN` sleeps indefinitely until firmware changes state. Correct post-mobility fixup is essential after resume.

Test signals: Sysfs hibernate read/write permissions, valid/invalid stream ids, VASI enabled/suspending/error states, suspend/resume on LPAR, post-mobility device-tree update, and non-LPAR init no-op.

Source read size: 190 lines, 4407 bytes.
