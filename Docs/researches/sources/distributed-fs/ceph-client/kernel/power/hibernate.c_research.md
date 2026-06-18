# sources/distributed-fs/ceph-client/kernel/power/hibernate.c

## Purpose
Implements the kernel hibernation coordinator: validating whether hibernation is available, creating a suspend-to-disk image, writing it through the swsusp backend, powering the machine down, and restoring a saved image during boot or explicit resume. It is the policy/control layer above `snapshot.c` memory-image construction and `swap.c` image storage.

## Important APIs, Types, and Functions
Global state includes `swsusp_resume_device`, `swsusp_resume_block`, `in_suspend`, `hib_comp_algo`, `freezer_test_done`, `hibernation_mode`, `hibernation_ops`, and `hibernate_atomic`. `hibernate_acquire()`/`hibernate_release()` serialize hibernation and `/dev/snapshot` ownership. `hibernation_available()` gates hibernation on command-line disablement, lockdown, secretmem, and CXL memory state.

Primary entry points are `hibernate()`, `software_resume()`, `hibernation_snapshot()`, `hibernation_restore()`, `hibernation_platform_enter()`, `hibernation_set_ops()`, `pm_hibernation_mode_is_suspend()`, `system_entering_hibernation()`, and exported `hibernate_quiet_exec()`. Sysfs handlers implement `/sys/power/disk`, `resume`, `resume_offset`, `image_size`, and `reserved_size`; boot parameters include `resume=`, `resume_offset=`, `hibernate=`, `noresume`, `resumewait`, `resumedelay=`, and `nohibernate`. The `compressor` module parameter selects LZO or LZ4, validated through the crypto acomp API.

## Control Flow
`hibernate()` first checks availability and compression support, locks `system_transition_mutex` via `lock_system_sleep()`, acquires the hibernation token, prepares the console, calls robust PM notifiers, syncs filesystems, optionally freezes filesystems, freezes user tasks, locks device hotplug, creates memory bitmaps, and calls `hibernation_snapshot()`.

`hibernation_snapshot()` begins platform mode if requested, preallocates image memory, freezes kernel threads, prepares devices, reclaims shmem pages, suspends consoles, restricts GFP I/O and filesystem allocation flags, suspends devices, and then calls `create_image()`. `create_image()` runs late/noirq device freeze, platform pre-snapshot, CPU disable, IRQ disable, syscore suspend, processor-state save, and `swsusp_arch_suspend()`. After the architecture snapshot returns, it resumes syscore, IRQs, CPUs, platform, and devices with `PMSG_THAW`, `PMSG_RECOVER`, or `PMSG_RESTORE` depending on whether execution is still in the image kernel or has returned after restore.

If `in_suspend` remains true, `hibernate()` builds swsusp flags for platform mode, no-compress mode, CRC/compression algorithm, writes the image with `swsusp_write()`, and either performs `test_resume` or calls `power_down()`. `power_down()` enters suspend mode, platform hibernation, poweroff, reboot, or halt based on `/sys/power/disk`; it restores the swap signature through `swsusp_unmark()` only when a wakeup event rolls back the transition.

Resume is handled by late initcall `software_resume_initcall()`: it resolves the resume device, calls `swsusp_check()`, validates compression support from header flags, freezes processes and kernel threads, reads the image via `load_image_and_restore()`, and jumps into the restored kernel through `hibernation_restore()` and `resume_target_kernel()`. Restore uses DPM quiesce callbacks, platform pre-restore, CPU disable, syscore suspend, highmem restore, and `swsusp_arch_resume()`.

## State and Persistence
Persistent user-visible state is held in sysfs tunables and boot parameters. Persistent on-disk state is delegated to `swap.c`, but this file chooses flags encoded in the image header. `hibernate_atomic` prevents concurrent hibernation or snapshot-device access. `in_suspend` is `__nosavedata` and distinguishes the image kernel after snapshot creation from execution after a successful restore. `entering_platform_hibernation` tells platform code and poweroff paths that firmware hibernation is underway. `hibernation_mode` persists until changed through `/sys/power/disk`.

## Dependencies and Integration Points
The file integrates with DPM (`dpm_prepare`, `dpm_suspend`, `dpm_suspend_end`, resume phases), freezer/OOM/usermode-helper code, filesystem freeze/thaw, console suspend, CPU hotplug, syscore ops, architecture swsusp hooks, PM notifiers, crypto compression, block-device lookup, security lockdown, secretmem/CXL guards, wakeup-event accounting, and platform hibernation ops. It is invoked from `/sys/power/state`, `/sys/power/disk`, boot resume initcalls, `/dev/snapshot`, and exported PM APIs.

## Risks
The highest risks are ordering regressions across freezer, device, CPU, IRQ, and syscore phases; missing cleanup on error paths; image/swap signature corruption if `power_down()` returns unexpectedly; races with wakeup events; compression algorithm/header mismatches; holding `system_transition_mutex` around paths that may wait for device discovery; and platform callbacks that do not implement the full required hibernation contract. Resume is especially sensitive because a partially restored image can leave devices, highmem, or filesystems inconsistent.

## Test Signals
Exercise `/sys/power/state` with `disk`, `/sys/power/disk` modes `shutdown`, `reboot`, `platform`, `suspend`, and `test_resume`; boot with `resume=`, `resume_offset=`, `resumewait`, `resumedelay=`, `hibernate=noresume`, `hibernate=nocompress`, and `nohibernate`; validate LZO/LZ4 compressor selection; run PM test levels through `/sys/power/pm_test`; inject DPM, freezer, swap, and wakeup-count failures; verify lockdown/secretmem/CXL disable paths; and confirm resume leaves swap signatures, suspend statistics, notifier events, and filesystem state consistent.
