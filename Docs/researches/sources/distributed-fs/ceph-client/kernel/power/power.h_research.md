# sources/distributed-fs/ceph-client/kernel/power/power.h

## Purpose
Defines the private interface shared by the kernel power-management implementation files. It centralizes hibernation image metadata, snapshot streaming contracts, sysfs attribute helpers, suspend/hibernate cross-file prototypes, test-level constants, and config-dependent stubs.

## Important APIs, Types, and Functions
`struct swsusp_info` is the page-aligned image header payload containing UTS data, kernel version, physical page count, CPU count, image page counts, and total image size. `struct snapshot_handle` abstracts streaming hibernation images page by page through `snapshot_read_next()` and `snapshot_write_next()`; callers use `data_of(handle)` to access the current buffer and `sync_read` to detect buffers that require synchronous reads.

Macros `power_attr()` and `power_attr_ro()` define common `/sys/power` kobj attributes. Hibernation flag definitions include `SF_PLATFORM_MODE`, `SF_NOCOMPRESS_MODE`, `SF_CRC32_MODE`, `SF_HW_SIG`, and compression algorithm selector `SF_COMPRESSION_ALG_LZ4` with dummy LZO value. PM test constants range from `TEST_NONE` through `TEST_FREEZER`.

The header declares shared variables such as `image_size`, `reserved_size`, `in_suspend`, `swsusp_resume_device`, `swsusp_resume_block`, `swsusp_header_flags`, `pm_labels`, `pm_states`, `mem_sleep_states`, `pm_test_level`, and `hib_comp_algo`. It declares cross-file entry points for memory bitmaps, hibernation preallocation, snapshot streaming, swap I/O, suspend entry, notifier chains, autosleep, wakelocks, CPU disable/enable wrappers, and DPM error recording.

## Control Flow
This file has no runtime control flow beyond small inline wrappers. It controls compile-time flow through `CONFIG_HIBERNATION`, `CONFIG_SUSPEND`, `CONFIG_PM_SLEEP`, `CONFIG_PM_AUTOSLEEP`, `CONFIG_HIGHMEM`, `CONFIG_ARCH_HIBERNATION_HEADER`, and `CONFIG_STRICT_KERNEL_RWX`. When features are disabled, callers get no-op stubs or default values to keep common code buildable.

## State and Persistence Behavior
The header itself owns no storage except through external declarations. Its definitions shape persistent hibernation image format (`struct swsusp_info` and `SF_*` flags) and user-visible sysfs ABI naming via `power_attr`. Changes to this file can affect image compatibility between the hibernating kernel and boot kernel.

## Dependencies and Integration Points
It includes suspend ioctls, UTS names, freezer, CPU, cpuidle, crypto, and compiler headers. It links `hibernate.c`, `snapshot.c`, `swap.c`, `suspend.c`, `main.c`, `user.c`, `wakelock.c`, and platform/architecture hibernation hooks. It also connects the `/dev/snapshot` UAPI to in-kernel snapshot streaming.

## Risks
Risks are ABI and contract drift: changing `struct swsusp_info`, flag semantics, snapshot streaming expectations, or config stubs can break resume, user-space suspend tools, and platform ports. The comment typo "hibernatig hernel" is harmless, but the surrounding flag documentation is important because `hibernate.c` and `swap.c` must agree exactly on compression and CRC behavior.

## Test Signals
Build matrix coverage is important: hibernation on/off, suspend on/off, highmem on/off, autosleep/wakelocks on/off, strict RWX image protection, and architecture hibernation headers. Runtime signals include successful image save/read across compression modes and `/dev/snapshot` ioctl compatibility.
