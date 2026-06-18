# subset-b-005855 Research

Grouped source research for Linux kernel include headers in the Ceph client source tree, covering VFS/file descriptor helpers, file locking and attributes, fbdev, BPF/filter interfaces, firmware loader and platform firmware IPC contracts, and small platform data headers. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/f75375s.h -->
# sources/distributed-fs/ceph-client/include/linux/f75375s.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/f75375s.h` defines platform data for the Fintek F75375S hardware monitor/fan controller. The source was read as a complete 21-line file for this report.

## Important APIs, Types, and Functions

The only exported type is `struct f75375s_platform_data`, with two-element `pwm` and `pwm_enable` arrays. There are no functions or runtime helpers.

## Control Flow

There is no executable control flow. Board or platform setup code fills this structure before the hwmon driver probes the chip.

## State and Persistence Behavior

The header describes initial fan PWM state only. Persistence is owned by the board data provider and the F75375S driver/hardware registers.

## Dependencies and Integration Points

The file depends on kernel integer types being available through include context. It integrates with the F75375S hwmon driver and platform-device registration on systems without BIOS fan initialization.

## Risks and Edge Cases

The fixed array size assumes exactly two PWM channels. Incorrect board data can leave fans disabled or at unsafe duty cycles.

## Test Signals

Build coverage for the F75375S driver, platform data probe tests, and boot-time validation that both PWM channels are initialized as intended on affected boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/f75375s.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/falloc.h -->
# sources/distributed-fs/ceph-client/include/linux/falloc.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/falloc.h` defines kernel-side fallocate and legacy XFS-compatible space reservation ioctl contracts. The source was read as a complete 63-line file for this report.

## Important APIs, Types, and Functions

Important exports are `struct space_resv`, `FS_IOC_RESVSP`, `FS_IOC_UNRESVSP`, `FS_IOC_RESVSP64`, `FS_IOC_UNRESVSP64`, `FS_IOC_ZERO_RANGE`, and `FALLOC_FL_MODE_MASK`. On `CONFIG_X86_64`, it also defines packed `struct space_resv_32` and matching 32-bit compat ioctl numbers.

## Control Flow

There is no local execution. VFS and filesystem ioctl/fallocate paths validate user mode bits against `FALLOC_FL_MODE_MASK`, translate ioctl payloads into ranges, and dispatch to filesystem allocation, punch, zero, collapse, insert, unshare, or write-zeroes implementations.

## State and Persistence Behavior

The header describes file extent state changes but stores no data. Actual persistence is in filesystem allocation metadata and file size/extent maps.

## Dependencies and Integration Points

It includes `uapi/linux/falloc.h` for user-visible flags and uses ioctl encoding macros. Integration points are VFS fallocate, filesystem-specific space management, compat ioctl handling on x86_64, and userspace tools using legacy XFS reservation ioctls.

## Risks and Edge Cases

Only one fallocate mode may be set at a time, with separate flags such as keep-size layered on top. Compat packing is ABI-sensitive, and range operations can interact badly with sparse files, reflinks, inline data, quotas, and distributed filesystem metadata consistency.

## Test Signals

Fallocate ioctl tests across native and compat ABIs, xfstests for punch/zero/collapse/insert/unshare/write-zeroes, quota and ENOSPC tests, and CephFS client tests for extent/state propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/falloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fanotify.h -->
# sources/distributed-fs/ceph-client/include/linux/fanotify.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/fanotify.h` centralizes kernel fanotify flag masks, permission classes, event groupings, and response validation masks. The source was read as a complete 150-line file for this report.

## Important APIs, Types, and Functions

The file exports macros such as `FAN_GROUP_FLAG`, `FANOTIFY_ADMIN_INIT_FLAGS`, `FANOTIFY_USER_INIT_FLAGS`, `FANOTIFY_MARK_FLAGS`, `FANOTIFY_PATH_EVENTS`, `FANOTIFY_DIRENT_EVENTS`, `FANOTIFY_PERM_EVENTS`, `FANOTIFY_EVENTS`, `FANOTIFY_OUTGOING_EVENTS`, `ALL_FANOTIFY_EVENT_BITS`, and `FANOTIFY_RESPONSE_VALID_MASK`. It also defines internal `FANOTIFY_UNPRIV`.

## Control Flow

There is no local function flow. Fanotify init, mark, event-generation, and permission-response paths use these masks to reject invalid userspace flags, split inode/path/error/mount event classes, and verify permission responses.

## State and Persistence Behavior

The header stores no state. Runtime state lives in fsnotify/fanotify groups, marks, queues, and permission event objects.

## Dependencies and Integration Points

It depends on `linux/sysctl.h` and `uapi/linux/fanotify.h`. It integrates with fsnotify, fanotify syscalls, capability checks for `CAP_SYS_ADMIN`, mount and inode watches, and file-handle/fd/pidfd reporting.

## Risks and Edge Cases

The masks intentionally avoid extending old UAPI aggregate constants. Privilege mistakes can expose file descriptors, pidfds, permission events, or unlimited queues to unprivileged users. Event classification must preserve directory-only and data-type restrictions.

## Test Signals

fanotify syscall selftests for privileged/unprivileged init, mark validation, permission response validation, mount and dirent events, pidfd/file-handle reporting, and queue overflow behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fanotify.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fault-inject-usercopy.h -->
# sources/distributed-fs/ceph-client/include/linux/fault-inject-usercopy.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/fault-inject-usercopy.h` exposes a tiny wrapper for injecting failures into user memory copy paths. The source was read as a complete 22-line file for this report.

## Important APIs, Types, and Functions

The main API is `should_fail_usercopy()`. With `CONFIG_FAULT_INJECTION_USERCOPY` it is an external function; otherwise it is a static inline returning `false`.

## Control Flow

Callers in usercopy paths invoke `should_fail_usercopy()` before or during copy operations. Disabled builds compile the branch away to a constant no-fail result.

## State and Persistence Behavior

The header owns no state. Fault policy is owned by the fault injection subsystem when enabled.

## Dependencies and Integration Points

It includes `linux/types.h` and integrates with hardened/usercopy and fault-injection debug/config control points.

## Risks and Edge Cases

Enabled tests must avoid leaking synthetic failures into production configurations. Disabled stubs should keep call sites buildable without altering behavior.

## Test Signals

Fault-injection KUnit or selftests that force usercopy failures, plus allnoconfig/tinyconfig builds verifying the stub path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fault-inject-usercopy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fault-inject.h -->
# sources/distributed-fs/ceph-client/include/linux/fault-inject.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/fault-inject.h` declares the generic kernel fault injection policy structure and helper APIs. The source was read as a complete 134-line file for this report.

## Important APIs, Types, and Functions

Key exports are `enum fault_flags`, `struct fault_attr`, `FAULT_ATTR_INITIALIZER`, `DECLARE_FAULT_ATTR`, `setup_fault_attr`, `should_fail_ex`, `should_fail`, `fault_create_debugfs_attr`, `struct fault_config`, `fault_config_init`, `should_fail_alloc_page`, and `should_failslab`. Disabled configs provide empty structs and no-fail stubs.

## Control Flow

Consumers initialize a `fault_attr`, optionally expose it through debugfs/configfs, then call `should_fail()` or a specialized helper at allocation or operation points. The implementation evaluates probability, interval, count/times, stack/task filters, address ranges, size/space, verbosity, and rate limiting.

## State and Persistence Behavior

State is in `fault_attr`: counters, atomics, rate-limit state, filters, and debugfs dentries. There is no file-backed persistence beyond runtime debugfs/configfs settings.

## Dependencies and Integration Points

The enabled path depends on `atomic`, `configfs`, and `ratelimit`. Integration points include page allocation failure, slab allocation failure, usercopy failure, debugfs/configfs test controls, and subsystem-specific injected error paths.

## Risks and Edge Cases

Fault attributes are global or subsystem-owned mutable test state. Wrong default return semantics matter: the disabled `setup_fault_attr()` comment notes `0` means error for `__setup()` handlers. Tests must account for ratelimits, intervals, and task/stack filters.

## Test Signals

Fault-injection selftests, allocation failure paths, debugfs/configfs attribute creation tests, and disabled-config build coverage for all stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fault-inject.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fb.h -->
# sources/distributed-fs/ceph-client/include/linux/fb.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/fb.h` is the main kernel framebuffer device interface header. It defines monitor metadata, user cursor/image structs, `fb_info`, driver operations, helper operations for I/O/system/DMA memory, deferred I/O wrappers, mode database helpers, color map helpers, and fbdev logging. The source was read as a complete 908-line file for this report.

## Important APIs, Types, and Functions

Important types include `struct fb_chroma`, `struct fb_monspecs`, `struct fb_cmap_user`, `struct fb_image_user`, `struct fb_cursor_user`, `struct fb_event`, `struct fb_blit_caps`, `struct fb_pixmap`, `struct fb_deferred_io`, `struct fb_ops`, tileblit structs, `struct fb_info`, `struct fb_videomode`, `struct dmt_videomode`, and `struct fb_modelist`. Important APIs include notifier helpers, `register_framebuffer`, `unregister_framebuffer`, `devm_register_framebuffer`, `fb_set_var`, `fb_pan_display`, `fb_blank`, `framebuffer_alloc`, `framebuffer_release`, EDID/mode helpers, cmap helpers, deferred I/O helpers, and default ops macros such as `FB_DEFAULT_IOMEM_OPS`, `FB_DEFAULT_DEFERRED_OPS`, and generated deferred ops macros.

## Control Flow

Framebuffer drivers populate `fb_info` and `fb_ops`, register the framebuffer, and then fbmem/fbcon/ioctl/mmap paths call the operation table for open, read/write, mode validation, set_par, pan, blank, drawing, cursor, ioctl, mmap, and destroy. Deferred I/O wrappers call base read/write/draw operations and then mark damaged ranges or areas. Mode helpers parse EDID, validate timings, and convert between `fb_var_screeninfo` and `fb_videomode`.

## State and Persistence Behavior

`fb_info` holds current variable/fixed screen state, monitor specs, pixmaps, color map, modelist, current mode, blank state, backlight/LCD associations, deferred I/O state, screen memory pointers, pseudo palette, suspend state, and driver private data. Persistence is device/runtime state; framebuffer contents may live in VRAM, system RAM, or DMA memory.

## Dependencies and Integration Points

The header depends on UAPI fb structures, mutexes, refcounts, workqueues, and architecture video helpers. It integrates with fbmem, fbcon, backlight, LCD, device tree video modes, I2C DDC, sysfs/device registration, mmap, deferred I/O, and DRM compatibility paths that expose fbdev.

## Risks and Edge Cases

`fb_ops` locking expectations are strict: most callbacks require the console semaphore while debug hooks must be lock-free. Endianness math (`fb_be_math`) affects pixel packing. `FBINFO_HIDE_SMEM_START` protects modern drivers from userspace sharing buffers behind the kernel. Deferred I/O must accurately mark damage. `fb_info` memory and device lifetime must match registration/unregistration.

## Test Signals

fbdev driver build tests, framebuffer registration/unregistration smoke tests, fbcon switching, `FBIOGET/PUT_*` ioctl tests, mmap/read/write tests for I/O and system memory helpers, deferred I/O damage tests, EDID/mode parsing tests, endian pixel rendering tests, and suspend/resume/blank/backlight tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fbcon.h -->
# sources/distributed-fs/ceph-client/include/linux/fbcon.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/fbcon.h` declares the framebuffer console integration hooks used by fbdev registration, mode changes, blanking, suspend/resume, and console-to-fb mappings. The source was read as a complete 55-line file for this report.

## Important APIs, Types, and Functions

Key functions are `fb_console_init`, `fb_console_exit`, `fbcon_fb_registered`, `fbcon_fb_unregistered`, `fbcon_fb_unbind`, `fbcon_suspended`, `fbcon_resumed`, `fbcon_mode_deleted`, `fbcon_delete_modelist`, `fbcon_new_modelist`, `fbcon_get_requirement`, `fbcon_fb_blanked`, `fbcon_modechange_possible`, `fbcon_update_vcs`, `fbcon_remap_all`, and console mapping ioctls. Disabled `CONFIG_FRAMEBUFFER_CONSOLE` builds provide no-op or zero-return inline stubs.

## Control Flow

fbdev core calls these hooks as framebuffers appear, disappear, change modes, blank, or suspend. fbcon then updates virtual consoles, font/blit requirements, and console mappings.

## State and Persistence Behavior

The header owns no state. fbcon state lives in console, vc, and framebuffer console internals.

## Dependencies and Integration Points

It forward-declares fb structures and depends on compiler attributes. It integrates the fbdev core with the virtual terminal console layer.

## Risks and Edge Cases

Disabled stubs make framebuffer devices usable without console support but can hide fbcon-specific regressions. Mode deletion and remapping must avoid stale modelist or console mappings.

## Test Signals

Builds with and without `CONFIG_FRAMEBUFFER_CONSOLE`, framebuffer registration tests, VT switch/remap ioctl tests, suspend/resume and blanking tests, and mode deletion tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fbcon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fcdevice.h -->
# sources/distributed-fs/ceph-client/include/linux/fcdevice.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/fcdevice.h` declares the Fibre Channel netdevice allocation helper. The source was read as a complete 28-line file for this report.

## Important APIs, Types, and Functions

It includes `linux/if_fc.h` and declares `alloc_fcdev(int sizeof_priv)` for kernel builds.

## Control Flow

There is no local flow. Fibre Channel network drivers call `alloc_fcdev()` to allocate a `net_device` with FC-specific setup and private data.

## State and Persistence Behavior

No state is owned here. State lives in allocated `net_device` instances and driver private areas.

## Dependencies and Integration Points

It integrates with the networking core, `struct net_device`, and Fibre Channel link-layer definitions from `if_fc.h`.

## Risks and Edge Cases

The header is legacy and narrowly scoped; risks are mostly build/API drift with netdevice allocation and FC header definitions.

## Test Signals

Build coverage of FC network drivers and probe/remove tests that allocate and free FC netdevices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fcdevice.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fcntl.h -->
# sources/distributed-fs/ceph-client/include/linux/fcntl.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/fcntl.h` provides kernel-side validation masks and lock-command classification helpers for open/openat2/fcntl handling. The source was read as a complete 48-line file for this report.

## Important APIs, Types, and Functions

Key macros are `VALID_OPEN_FLAGS`, `VALID_RESOLVE_FLAGS`, `OPEN_HOW_SIZE_VER0`, `OPEN_HOW_SIZE_LATEST`, `force_o_largefile`, `IS_GETLK32`, `IS_SETLK32`, `IS_SETLKW32`, `IS_GETLK64`, `IS_SETLK64`, `IS_SETLKW64`, and aggregate `IS_GETLK`, `IS_SETLK`, `IS_SETLKW`.

## Control Flow

Open and openat2 syscall code validates userspace flags against these masks, applies large-file defaults, and dispatches fcntl lock commands through 32-bit or native command paths based on word size.

## State and Persistence Behavior

No state is stored in this header. It affects validation before file objects, dentries, and locks are created or modified.

## Dependencies and Integration Points

It includes `linux/stat.h` and UAPI fcntl definitions. It integrates with VFS open path resolution, openat2 ABI sizing, file locking, and compat handling.

## Risks and Edge Cases

Adding flags without updating masks rejects valid userspace requests; overly broad masks can bypass intended path-resolution restrictions. Lock command mapping differs between 32-bit and 64-bit builds.

## Test Signals

open/openat2 selftests for flag validation, path resolution constraints, 32-bit compat fcntl lock tests, and large-file behavior tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fcntl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fd.h -->
# sources/distributed-fs/ceph-client/include/linux/fd.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/fd.h` wraps floppy UAPI definitions and adds a compat ioctl payload for 32-bit userspace. The source was read as a complete 25-line file for this report.

## Important APIs, Types, and Functions

It includes `uapi/linux/fd.h`. Under `CONFIG_COMPAT`, it defines `struct compat_floppy_struct` and `FDGETPRM32`.

## Control Flow

There is no local flow. Floppy ioctl handling uses the compat structure to translate `FDGETPRM` for 32-bit callers.

## State and Persistence Behavior

No state is owned by the header. Runtime state lives in floppy drive geometry and driver data.

## Dependencies and Integration Points

It integrates with the floppy block driver, ioctl layer, and compat subsystem.

## Risks and Edge Cases

Compat pointer and integer width mismatches can corrupt geometry reporting. The `name` field uses a compat userspace address.

## Test Signals

Compat ioctl build coverage and floppy ioctl translation tests where hardware or emulation is available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fddidevice.h -->
# sources/distributed-fs/ceph-client/include/linux/fddidevice.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/fddidevice.h` declares FDDI network device helpers. The source was read as a complete 28-line file for this report.

## Important APIs, Types, and Functions

It includes `linux/if_fddi.h` and declares `fddi_type_trans(struct sk_buff *, struct net_device *)` and `alloc_fddidev(int sizeof_priv)` for kernel builds.

## Control Flow

FDDI drivers allocate devices with `alloc_fddidev()` and pass received packets through `fddi_type_trans()` to classify the packet protocol for the network stack.

## State and Persistence Behavior

No state is owned here. State lives in `net_device`, skb metadata, and driver private data.

## Dependencies and Integration Points

It integrates with networking core, skbuff receive paths, and FDDI link-layer definitions.

## Risks and Edge Cases

Legacy protocol support can be build-fragile. Receive classification must handle malformed FDDI frames without corrupting skb protocol state.

## Test Signals

Build coverage for FDDI drivers, packet receive classification tests, and netdevice allocation/free smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fddidevice.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fdtable.h -->
# sources/distributed-fs/ceph-client/include/linux/fdtable.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/fdtable.h` defines internal file descriptor table structures and lookup helpers. The source was read as a complete 118-line file for this report.

## Important APIs, Types, and Functions

Important exports are `NR_OPEN_DEFAULT`, `struct fdtable`, `struct files_struct`, `rcu_dereference_check_fdtable`, `files_fdtable`, `files_lookup_fd_raw`, `files_lookup_fd_locked`, `close_on_exec`, `put_files_struct`, `unshare_files`, `struct fd_range`, `dup_fd`, `do_close_on_exec`, `iterate_fd`, `close_fd`, `file_close_fd`, and `files_cachep`.

## Control Flow

VFS fd operations use `files_struct` as the per-task descriptor table. Lookups read the RCU-protected `fdtable`, use `array_index_mask_nospec()` to guard bounds/speculation, and return masked file pointers. Writers hold `file_lock`, resize tables, set close-on-exec/open/full bitmaps, and duplicate or close descriptor ranges.

## State and Persistence Behavior

`files_struct` persists while shared by tasks through an atomic count. It stores the active fdtable pointer, inline default arrays, descriptor bitmaps, `next_fd`, resize state, lock, and wait queue. State is process runtime state, not file-backed.

## Dependencies and Integration Points

It depends on RCU, spinlocks, nospec helpers, fs types, and atomics. It integrates with fork/clone/unshare, exec close-on-exec, file lookup, close, descriptor iteration, and VFS file lifetime.

## Risks and Edge Cases

RCU and locking rules are strict. Out-of-range fd access must remain speculation-safe. Resize and shared `files_struct` operations can race with lookups if callers do not hold RCU or `file_lock` as required.

## Test Signals

fdtable stress tests with concurrent open/close/dup/exec/fork, KCSAN/lockdep coverage, close-on-exec tests, and Spectre/nospec regression tests for fd lookups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fdtable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fec.h -->
# sources/distributed-fs/ceph-client/include/linux/fec.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/fec.h` defines platform data for Freescale/NXP FEC Ethernet controllers. The source was read as a complete 22-line file for this report.

## Important APIs, Types, and Functions

The only exported type is `struct fec_platform_data` with `phy_interface_t phy`, `mac[ETH_ALEN]`, and an optional `sleep_mode_enable` callback.

## Control Flow

Platform or board code provides this data to the FEC driver. The driver consumes PHY mode, MAC address, and optional sleep-mode callback during probe, suspend, or low-power transitions.

## State and Persistence Behavior

No state is owned here. The platform data carries boot-time configuration; MAC persistence is outside the header, typically firmware, device tree, NVMEM, or board data.

## Dependencies and Integration Points

It includes `linux/phy.h` and integrates with the FEC Ethernet driver, PHY subsystem, netdevice registration, and platform power management.

## Risks and Edge Cases

Invalid PHY interface or MAC address can prevent network bring-up. Sleep callback polarity must match board wiring.

## Test Signals

FEC driver probe tests, PHY mode validation, MAC address source tests, and suspend/resume tests exercising `sleep_mode_enable`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fiemap.h -->
# sources/distributed-fs/ceph-client/include/linux/fiemap.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/fiemap.h` declares the kernel-side FIEMAP extent reporting interface used by filesystems. The source was read as a complete 27-line file for this report.

## Important APIs, Types, and Functions

It defines `struct fiemap_extent_info` and declares `fiemap_prep()` and `fiemap_fill_next_extent()`.

## Control Flow

Filesystem fiemap implementations prepare a user request with `fiemap_prep()`, iterate filesystem extents, and call `fiemap_fill_next_extent()` for each logical/physical/length/flag tuple until the user buffer is full or extents are exhausted.

## State and Persistence Behavior

`fiemap_extent_info` tracks request flags, number of extents mapped, max extents, and the userspace destination pointer. It is per-ioctl transient state.

## Dependencies and Integration Points

It includes UAPI FIEMAP definitions and `linux/fs.h`. It integrates with VFS ioctl handling and filesystem extent maps, including distributed filesystems such as CephFS when they expose extent layout.

## Risks and Edge Cases

Userspace pointer handling and extent count limits are sensitive. Filesystems must set accurate flags for unwritten, shared, delayed, encoded, or last extents and validate unsupported flags.

## Test Signals

FIEMAP xfstests for sparse, unwritten, shared/reflinked, inline, encrypted/compressed, and distributed file extents; ioctl fault-injection for userspace copy errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fiemap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/file.h -->
# sources/distributed-fs/ceph-client/include/linux/file.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/file.h` declares VFS file allocation, descriptor acquisition, descriptor installation, and cleanup-helper APIs. The source was read as a complete 255-line file for this report.

## Important APIs, Types, and Functions

Important exports include `fput`, `alloc_file_pseudo`, `alloc_file_pseudo_noaccount`, `alloc_file_clone`, `struct fd`, `FDPUT_FPUT`, `FDPUT_POS_UNLOCK`, `fd_file`, `fd_empty`, `EMPTY_FD`, `BORROWED_FD`, `CLONED_FD`, `fdput`, `fget`, `fget_raw`, `fget_task`, `fget_task_next`, `fdget`, `fdget_raw`, `fdget_pos`, `fdput_pos`, cleanup classes `fd`, `fd_raw`, and `fd_pos`, `f_dupfd`, `replace_fd`, close-on-exec helpers, unused-fd helpers, `take_fd`, `fd_install`, `receive_fd`, `receive_fd_replace`, delayed fput helpers, `struct fd_prepare`, `FD_PREPARE`, `fd_publish`, and `FD_ADD`.

## Control Flow

Callers acquire `struct file` references through fget/fdget helpers, use `fd_file()` to access the pointer, and release via `fdput()` or `fdput_pos()` depending on whether the low-bit flags request `fput()` and/or position unlock. Allocation flows reserve an fd, allocate or receive a file, install with `fd_install()`, and publish/take ownership. `fd_prepare` and cleanup classes make error paths automatically release partially acquired fds/files.

## State and Persistence Behavior

The header does not own storage, but its `struct fd` encodes file pointer plus flags in low pointer bits. Descriptor state lives in `files_struct`; file state lives in `struct file`; delayed fput state is handled by VFS.

## Dependencies and Integration Points

It depends on cleanup helpers, errno, error pointers, and VFS types. It integrates with fdtable internals, open/receive-fd paths, SCM_RIGHTS, pseudo files, mount/dentry/inode file creation, close-on-exec, and positional file locking.

## Risks and Edge Cases

Low-bit pointer tagging requires `struct file` alignment. Forgetting `fdput_pos()` after `fdget_pos()` can leave position locks held. Publishing must transfer ownership exactly once; failure paths must not leak unused fds or double `fput()` files.

## Test Signals

Open/close/dup/SCM_RIGHTS tests, fd leak tests under fault injection, lockdep for `f_pos` locking, cleanup-class build tests, and stress tests around `FD_ADD` and `fd_prepare` failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/file.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/file_ref.h -->
# sources/distributed-fs/ceph-client/include/linux/file_ref.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/file_ref.h` implements a file-specific reference counter designed for `SLAB_TYPESAFE_BY_RCU` file objects. The source was read as a complete 218-line file for this report.

## Important APIs, Types, and Functions

Key exports are `FILE_REF_ONEREF`, `FILE_REF_MAXREF`, `FILE_REF_SATURATED`, `FILE_REF_RELEASED`, `FILE_REF_DEAD`, `FILE_REF_NOREF`, `file_ref_t`, `file_ref_init`, `__file_ref_put`, `file_ref_get`, `file_ref_inc`, `file_ref_put`, `file_ref_put_close`, `file_ref_read`, and `__file_ref_read_raw`.

## Control Flow

`file_ref_init()` stores count minus one. `file_ref_get()` unconditionally increments with full ordering and succeeds only if the resulting value is not in a negative/dead zone. `file_ref_inc()` is for callers already holding a ref and warns on released refs. `file_ref_put()` disables preemption, decrements, and falls into `__file_ref_put()` when the result enters saturation/dead handling. `file_ref_put_close()` optimizes the common last-reference close by CASing one-ref directly to dead.

## State and Persistence Behavior

The counter stores valid, saturation, released/dead, and no-ref zones in an atomic long-sized field. It is in-memory lifetime state for `struct file`, not persistent storage.

## Dependencies and Integration Points

It depends on atomics, preemption guards, and integer types. It integrates with the VFS file cache and RCU-safe file object reuse.

## Risks and Edge Cases

The design intentionally avoids trying to repair negative/dead counts after failed gets because the file may already have been recycled. Preemption disabling in `file_ref_put()` protects against slab-page freeing races. Incorrect callers can resurrect, leak, or prematurely free files.

## Test Signals

Refcount stress tests with concurrent get/put/close, KCSAN and KASAN under file-table churn, SLAB_TYPESAFE_BY_RCU reuse tests, saturation tests, and warnings from `file_ref_inc()` misuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/file_ref.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fileattr.h -->
# sources/distributed-fs/ceph-client/include/linux/fileattr.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/fileattr.h` provides the merged VFS representation for legacy `FS_IOC_GETFLAGS/SETFLAGS` and XFS-style `FS_IOC_FSGETXATTR/FSSETXATTR` file attributes. The source was read as a complete 83-line file for this report.

## Important APIs, Types, and Functions

Important masks are `FS_COMMON_FL`, `FS_XFLAG_COMMON`, `FS_XFLAG_RDONLY_MASK`, `FS_XFLAG_VALUES_MASK`, `FS_XFLAG_DIRONLY_MASK`, `FS_XFLAG_MISC_MASK`, and `FS_XFLAGS_MASK`. The central type is `struct file_kattr`. APIs include `copy_fsxattr_to_user`, `fileattr_fill_xflags`, `fileattr_fill_flags`, `fileattr_has_fsx`, `vfs_fileattr_get`, `vfs_fileattr_set`, `ioctl_getflags`, `ioctl_setflags`, `ioctl_fsgetxattr`, and `ioctl_fssetxattr`.

## Control Flow

Filesystem ioctl paths fill a `file_kattr` from either flags or fsxattrs, VFS validates and maps common bits, then get/set helpers call filesystem fileattr methods. `fileattr_has_fsx()` detects attributes that cannot be represented in simple flags.

## State and Persistence Behavior

`file_kattr` is transient request state. Persistent effects are filesystem inode flags, project IDs, extent size hints, CoW extent size hints, and read-only flags such as verity.

## Dependencies and Integration Points

It integrates with VFS ioctl handling, idmapped mounts, inode attribute mutation, ext-family flags, XFS-style fsxattrs, project quotas, DAX, verity, and filesystem-specific fileattr implementations.

## Risks and Edge Cases

Some xflags are read-only or directory-only; mapping them incorrectly can expose unsupported persistence changes. Overlap between flags and xflags must remain consistent. Idmapped mount permission checks affect set operations.

## Test Signals

xfstests for chattr/lsattr, project quota inheritance, DAX/verity flags, idmapped mount permission behavior, unsupported flag rejection, and fsxattr copy_to_user fault handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fileattr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/filelock.h -->
# sources/distributed-fs/ceph-client/include/linux/filelock.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/filelock.h` defines VFS file lock, flock, lease, delegation, and lock-manager interfaces. It includes a Ceph-specific private lock union member. The source was read as a complete 596-line file for this report.

## Important APIs, Types, and Functions

Important flags include `FL_POSIX`, `FL_FLOCK`, `FL_DELEG`, `FL_LEASE`, `FL_CLOSE`, `FL_SLEEP`, `FL_OFDLCK`, `FL_LAYOUT`, and `FILE_LOCK_DEFERRED`. Key types are `struct file_lock_operations`, `struct lock_manager_operations`, `struct lease_manager_operations`, `struct lock_manager`, `struct file_lock_core`, `struct file_lock`, `struct file_lease`, `struct file_lock_context`, and `struct delegated_inode`. APIs include fcntl lock/lease/delegation helpers, `locks_start_grace`, `locks_end_grace`, `locks_in_grace`, `opens_in_grace`, lock classification helpers, lock allocation/copy/free/remove/test functions, `posix_lock_file`, `vfs_lock_file`, `vfs_cancel_lock`, lease break/set/modify helpers, `show_fd_locks`, `locks_inode_context`, `break_lease`, `break_deleg`, `try_break_deleg`, `break_deleg_wait`, and `break_layout`.

## Control Flow

fcntl and flock syscalls build `file_lock` requests, test conflicts, enqueue blocking locks, wake waiters, or dispatch to filesystem/lock-manager callbacks. Lease/delegation paths check inode lock contexts, use memory barriers around lockless lease-list tests, and call `__break_lease()` for blocking or nonblocking break flows. Disabled `CONFIG_FILE_LOCKING` builds return errors or no-op fallbacks.

## State and Persistence Behavior

`file_lock_context` hangs off inodes and stores flock, POSIX, and lease lists under a spinlock. Each lock tracks owner, type, range, pid, file, waitqueue, blocker, blocked requests, global-list linkage, and filesystem-private state. The union includes NFS/NFSv4, AFS, and Ceph `struct inode *` private state.

## Dependencies and Integration Points

It includes `linux/fs.h` and `linux/nfs_fs_i.h`. Integration points include VFS fcntl/flock, NFS/NLM/NFSv4 lock managers, AFS, Ceph, pNFS layouts, leases/delegations, proc lock display, inode operation flags, and network namespace grace periods.

## Risks and Edge Cases

Lock objects can be requests or granted locks, but never both. List ordering by owner/range matters for POSIX semantics. Lockless lease checks require the paired acquire/release barriers. Ceph lock private state must remain compatible with generic copy/release flows.

## Test Signals

POSIX and OFD lock tests, flock tests, lease/delegation break tests, network lock manager grace-period tests, CephFS lock recovery tests, `/proc/locks` tests, lockdep/KCSAN, and disabled-config build tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/filelock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/filter.h -->
# sources/distributed-fs/ceph-client/include/linux/filter.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/filter.h` is a major kernel BPF/socket-filter interface header. It defines eBPF register aliases, instruction constructors, classic BPF conversion helpers, BPF runtime/JIT allocation and kallsyms interfaces, socket filter attachment APIs, SKB/XDP context helpers, redirect state, and SK_LOOKUP execution helpers. The source was read as a complete 1886-line file for this report.

## Important APIs, Types, and Functions

Important macros include BPF register aliases, internal opcodes such as `BPF_TAIL_CALL`, `BPF_PROBE_MEM*`, `BPF_NOSPEC`, instruction builders such as `BPF_ALU64_REG`, `BPF_MOV64_IMM`, `BPF_LD_IMM64`, `BPF_LDX_MEM`, `BPF_STX_MEM`, `BPF_ATOMIC_OP`, `BPF_JMP_*`, `BPF_CALL_REL`, `BPF_EMIT_CALL`, `BPF_CALL_KFUNC`, `BPF_EXIT_INSN`, BPF helper declaration macros `BPF_CALL_0` through `BPF_CALL_5`, and context-range macros. Important types include `struct compat_sock_fprog`, `struct sock_fprog_kern`, `struct bpf_binary_header`, `struct bpf_prog_stats`, `struct sk_filter`, `struct bpf_redirect_info`, `struct bpf_net_context`, `struct bpf_sock_addr_kern`, `struct bpf_sock_ops_kern`, `struct bpf_sysctl_kern`, `struct bpf_sockopt_kern`, and `struct bpf_sk_lookup_kern`. Key APIs include `bpf_prog_run`, `bpf_prog_run_pin_on_cpu`, `bpf_compute_data_pointers`, `bpf_prog_run_save_cb`, `sk_filter`, BPF program allocation/free/create/destroy APIs, socket attach/detach APIs, JIT runtime helpers, XDP redirect helpers, SK_LOOKUP runners, and packet load/store helpers.

## Control Flow

BPF programs are created from classic or eBPF instructions, verified/selected for interpreter or JIT runtime, optionally made read-only/executable, then run through dispatcher functions with migration constraints and optional stats accounting. SKB execution saves or clears `skb->cb` as needed, computes `data_meta` and `data_end`, and restores prior control-buffer state. XDP and redirect helpers store per-task redirect state in `current->bpf_net_context`, then flush devmap/cpumap/xskmap lists in matching CPU context. SK_LOOKUP macros iterate program arrays under RCU and aggregate selected sockets/drop decisions.

## State and Persistence Behavior

State includes refcounted `sk_filter` objects, `bpf_prog` memory and stats, JIT binary headers, per-task `bpf_net_context`, per-packet skb control-buffer overlays, redirect metadata, and socket lookup context. JIT code may be exposed through kallsyms depending on hardening and sysctl state.

## Dependencies and Integration Points

The header depends on BPF UAPI, networking/skbuff, workqueues, scheduler clocks, set_memory, kallsyms, VLAN, sockptr, u64 stats, and qdisc internals. It integrates with socket filters, seccomp/classic BPF conversion, verifier, BPF syscall, BPF JIT back ends, netfilter BTF access, tc, XDP, reuseport, cgroup sockopt/sysctl hooks, and inet/IPv6 socket lookup.

## Risks and Edge Cases

This header sits on hot and security-sensitive paths. Risks include instruction encoding drift, verifier/JIT disagreement, missing zero-extension or speculation barriers, unsafe skb cb leakage to unprivileged programs, per-task redirect state not initialized before use, JIT hardening/kallsyms exposure mistakes, and CPU-context mismatches between redirect and flush.

## Test Signals

BPF selftests for instruction encoding, verifier/JIT parity, socket filters, reuseport, SK_LOOKUP, cgroup sockopt/sysctl, XDP redirects, JIT hardening/kallsyms sysctls, classic-to-eBPF migration, skb cb access, packet load/store helpers, and CONFIG_BPF_JIT/CONFIG_BPF_SYSCALL disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/filter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/find.h -->
# sources/distributed-fs/ceph-client/include/linux/find.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/find.h` provides bitmap bit-search helpers and iteration macros used throughout the kernel. It is intentionally included through `linux/bitmap.h`. The source was read as a complete 695-line file for this report.

## Important APIs, Types, and Functions

Important functions/macros include `_find_next_bit`, `_find_next_and_bit`, `_find_next_andnot_bit`, `_find_next_or_bit`, `_find_next_zero_bit`, `_find_first_bit`, `__find_nth_bit`, `__find_nth_and_bit`, `__find_nth_and_andnot_bit`, `_find_first_and_bit`, `_find_first_andnot_bit`, `_find_first_and_and_bit`, `_find_first_zero_bit`, `_find_last_bit`, endian-specific `_find_*_le`, `find_random_bit`, inline `find_next_bit`, `find_next_and_bit`, `find_next_andnot_bit`, `find_next_or_bit`, `find_next_zero_bit`, `find_first_bit`, `find_nth_bit`, `find_nth_and_bit`, `find_first_andnot_bit`, `find_last_bit`, wrap helpers, `find_next_clump8`, and iteration macros such as `for_each_set_bit`, `for_each_clear_bit`, bitrange iterators, and clump iterators.

## Control Flow

Callers search bitmaps for set, clear, combined, excluded, or nth bits. For compile-time small bitmaps, inline paths mask a single word and use `__ffs`, `ffz`, `__fls`, or `fns`; larger cases call architecture/generic implementations. Wrap helpers search from an offset and wrap to the beginning. Iteration macros repeatedly call the find helpers and increment past found bits/ranges.

## State and Persistence Behavior

No state is owned by the header. It operates over caller-owned bitmap memory.

## Dependencies and Integration Points

It depends on bitops, endian definitions, and bitmap inclusion discipline. It is used by cpumasks, nodemasks, allocation bitmaps, fd bitmaps, page/block allocators, scheduler masks, and many driver resource maps.

## Risks and Edge Cases

Size and offset bounds are critical: helpers return `size` when not found. Small-constant masks must avoid invalid shifts. Big-endian little-endian bitmap helpers swab word values. Iteration macros assign inside loop conditions and require caller variables with appropriate unsigned types.

## Test Signals

lib/bitmap tests, bitops tests on 32-bit/64-bit and big/little-endian targets, randomized bitmap search comparisons, boundary tests for size 0/1/BITS_PER_LONG, and wrap/clump iteration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/find.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fips.h -->
# sources/distributed-fs/ceph-client/include/linux/fips.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/fips.h` declares the kernel FIPS mode flag and helper. The source was read as a complete 18-line file for this report.

## Important APIs, Types, and Functions

It declares external `fips_enabled` and inline `fips_fail_notify()` returning `fips_enabled`.

## Control Flow

Cryptographic or compliance-sensitive code can call `fips_fail_notify()` to determine whether a failure should trigger FIPS-mode behavior. Actual notification/control is elsewhere.

## State and Persistence Behavior

The only referenced state is global `fips_enabled`, typically initialized from boot/config policy. The header does not store or persist it.

## Dependencies and Integration Points

It integrates with crypto, integrity, and boot parameter code that gates behavior in FIPS mode.

## Risks and Edge Cases

The helper currently mirrors `fips_enabled`; callers expecting richer notification semantics must rely on external implementation/policy.

## Test Signals

FIPS boot parameter tests, crypto selftest failure behavior, and build coverage for code paths using `fips_fail_notify()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fips.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firewire.h -->
# sources/distributed-fs/ceph-client/include/linux/firewire.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/firewire.h` defines the Linux FireWire core interface, including CSR constants, card/device/unit structures, transactions, address handlers, descriptors, and isochronous transfer contexts. The source was read as a complete 625-line file for this report.

## Important APIs, Types, and Functions

Important exports include CSR register/key constants, `struct fw_csr_iterator`, `fw_csr_iterator_init`, `fw_csr_iterator_next`, `fw_csr_string`, `fw_bus_type`, `struct fw_card`, `fw_card_get`, `fw_card_put`, `fw_card_read_cycle_time`, `struct fw_attribute_group`, device quirks/state enums, `struct fw_device`, `struct fw_unit`, `struct fw_driver`, transaction callback types, `struct fw_packet`, `struct fw_transaction`, `struct fw_address_handler`, `struct fw_address_region`, address-handler APIs, `fw_send_response`, `fw_send_request`, `fw_send_request_with_tstamp`, `fw_cancel_transaction`, `fw_run_transaction`, descriptor APIs, `struct fw_iso_packet`, `struct fw_iso_buffer`, `struct fw_iso_context`, iso context create/queue/start/stop/destroy APIs, and `fw_iso_resource_manage`.

## Control Flow

FireWire cards register core state and workqueues. Devices and units are discovered from CSR config ROMs; drivers probe `fw_unit` instances. Outbound transactions are built as `fw_transaction`/`fw_packet`, sent through the card driver, and completed through callbacks, sometimes synchronously for local/error cases. Inbound address handlers run in RCU read-side context and must respond. Isochronous contexts queue packet descriptors and DMA buffers, then schedule work to flush completions.

## State and Persistence Behavior

State includes card generation/node IDs, transaction label allocation, split timeout tracking, bus manager work, topology and speed maps, device state/config ROMs, unit directories, pending transactions/timers, address handler refs, and DMA-mapped iso buffers. This is runtime bus state reset by topology changes.

## Dependencies and Integration Points

The header depends on device model, DMA mapping, krefs, workqueues, timers, completions, sysfs, atomics, and byte order helpers. It integrates with FireWire host controller drivers, device/unit drivers, sysfs, CSR/config ROM parsing, asynchronous request/response transactions, and isochronous audio/video streaming.

## Risks and Edge Cases

Generation must be read before node ID to avoid sending to stale nodes after bus reset. Address callbacks run in RCU context and cannot sleep or recursively initiate outbound requests. Iso DMA buffers are not normally kernel-mapped. Transaction callbacks may run in current or workqueue context.

## Test Signals

FireWire bus reset/device discovery tests, config ROM parsing tests, async transaction timeout/cancel tests, generation/node-id race tests, address handler response tests, and isochronous transmit/receive DMA tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firewire.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware-map.h -->
# sources/distributed-fs/ceph-client/include/linux/firmware-map.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/firmware-map.h` declares firmware memory map add/remove helpers, with stubs when firmware memmap support is disabled. The source was read as a complete 40-line file for this report.

## Important APIs, Types, and Functions

The exported APIs are `firmware_map_add_early`, `firmware_map_add_hotplug`, and `firmware_map_remove`. Disabled `CONFIG_FIRMWARE_MEMMAP` builds return success without recording anything.

## Control Flow

Architecture/platform code reports firmware memory regions early or during hotplug; removal unregisters matching ranges. Disabled builds compile these operations to no-ops.

## State and Persistence Behavior

The header owns no state. Enabled implementations maintain a firmware memory-map registry, generally exposed through sysfs.

## Dependencies and Integration Points

It includes `linux/list.h` and integrates with firmware/e820/platform memory discovery, memory hotplug, and firmware memmap sysfs.

## Risks and Edge Cases

No-op stubs return success, so callers cannot infer whether a region is actually visible in firmware memmap. Range/type matching must be exact for removal.

## Test Signals

Boot-time firmware memmap tests, hotplug add/remove tests, sysfs visibility tests, and disabled-config build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware-map.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware.h -->
# sources/distributed-fs/ceph-client/include/linux/firmware.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/firmware.h` declares the kernel firmware loader API and firmware upload interface. The source was read as a complete 216-line file for this report.

## Important APIs, Types, and Functions

Key definitions include `FW_ACTION_NOUEVENT`, `FW_ACTION_UEVENT`, `struct firmware`, `enum fw_upload_err`, `struct fw_upload`, `struct fw_upload_ops`, `firmware_request_builtin`, `request_firmware`, `firmware_request_nowait_nowarn`, `firmware_request_nowarn`, `firmware_request_platform`, `request_firmware_nowait`, `request_firmware_direct`, `request_firmware_into_buf`, `request_partial_firmware_into_buf`, `release_firmware`, `firmware_upload_register`, `firmware_upload_unregister`, `firmware_request_cache`, and cleanup helper `DEFINE_FREE(firmware, ...)`.

## Control Flow

Drivers request firmware synchronously, asynchronously, directly, from platform fallback, into provided buffers, or by partial reads. Successful requests return a `struct firmware` that must be released. Firmware upload users register device-specific prepare/write/poll/cancel/cleanup ops; the firmware loader calls them to push update data to hardware and report upload errors.

## State and Persistence Behavior

`struct firmware` carries size/data plus private loader state. Upload state is in `struct fw_upload` and driver-private handles. Firmware data is transient kernel memory; actual persistent update effects are device-specific flash or secure storage.

## Dependencies and Integration Points

It depends on kernel types, compiler attributes, cleanup helpers, and GFP flags. It integrates with the firmware loader, module/device model, sysfs fallback/uevent policy, built-in firmware, platform firmware, and device firmware update flows.

## Risks and Edge Cases

Availability depends on `CONFIG_FW_LOADER` reachability; disabled stubs return `-EINVAL`. Async callbacks must handle lifetime of context and firmware. Upload cancel runs from a different kernel thread, so driver ops must be race-safe. Buffer and partial requests require size/offset validation.

## Test Signals

Firmware loader selftests, built-in/direct/nowait/platform request tests, missing firmware error paths, release/cleanup-class tests, firmware upload sysfs tests, cancellation/race tests, and disabled-config build tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/broadcom/tee_bnxt_fw.h -->
# sources/distributed-fs/ceph-client/include/linux/firmware/broadcom/tee_bnxt_fw.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/firmware/broadcom/tee_bnxt_fw.h` declares Broadcom BNXT firmware operations mediated through a Trusted Execution Environment. The source was read as a complete 14-line file for this report.

## Important APIs, Types, and Functions

The APIs are `tee_bnxt_fw_load()` and `tee_bnxt_copy_coredump(void *buf, u32 offset, u32 size)`.

## Control Flow

BNXT driver code can request secure firmware loading through TEE and copy coredump ranges from secure/firmware-owned storage into a caller buffer.

## State and Persistence Behavior

The header owns no state. Firmware and coredump state are managed by the BNXT driver, TEE client, and device/secure firmware.

## Dependencies and Integration Points

It depends on `linux/types.h` and integrates with Broadcom network firmware loading, TEE infrastructure, and coredump retrieval paths.

## Risks and Edge Cases

Coredump offset/size validation and secure memory access are critical. Loading failures may depend on TEE availability and firmware policy.

## Test Signals

BNXT firmware load tests with and without TEE, coredump range tests, secure firmware error injection, and build coverage for BNXT TEE integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/broadcom/tee_bnxt_fw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/cirrus/cs_dsp.h -->
# sources/distributed-fs/ceph-client/include/linux/firmware/cirrus/cs_dsp.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/firmware/cirrus/cs_dsp.h` declares the Cirrus Logic DSP firmware support API for ADSP1/ADSP2/Halo cores, including DSP memory regions, coefficient controls, lifecycle management, raw data access, write sequences, and packed DSP chunk helpers. The source was read as a complete 360-line file for this report.

## Important APIs, Types, and Functions

Important definitions include region masks, 24-bit DSP word constants, acked-control timeout limits, write-sequence opcodes, `struct cs_dsp_region`, `struct cs_dsp_alg_region`, `struct cs_dsp_coeff_ctl`, `struct cs_dsp`, `struct cs_dsp_client_ops`, init/power/run/stop/remove APIs, clock/bus-error/watchdog APIs, debugfs APIs, coefficient read/write APIs, raw data read/write APIs, algorithm lookup, `struct cs_dsp_wseq`, write-sequence APIs, `struct cs_dsp_chunk`, chunk inline helpers, chunk read/write/flush APIs, and `cs_dsp_hibernate`.

## Control Flow

Client drivers initialize a `cs_dsp`, load WMFW and coefficient firmware through power-up APIs, create coefficient controls, run the core with pre/post client callbacks under `pwr_lock`, access controls and DSP memory, and stop/power down/remove the DSP. Write sequences record register operations for DSP-controlled replay. Chunk helpers pack/unpack non-byte-aligned DSP words.

## State and Persistence Behavior

`struct cs_dsp` stores device/regmap pointers, firmware identity, memory map, algorithm regions, boot/running/hibernating flags, control list, power lock, region locking, and debugfs filenames. Coefficient controls cache values and enabled/set flags. Persistence beyond runtime is firmware/device-specific.

## Dependencies and Integration Points

It depends on bits, device model, firmware loader, lists, and regmap. It integrates with audio codec/amplifier drivers, WMFW format definitions, coefficient binary loading, debugfs, regmap-backed hardware access, and client lifecycle callbacks.

## Risks and Edge Cases

Control callbacks run under `pwr_lock`, so callbacks must avoid deadlocks. DSP word packing is 24-bit and easy to mis-size. Acked controls have polling/timeout behavior. Firmware/control ABI drift can break coefficient parsing or raw memory access.

## Test Signals

Cirrus DSP KUnit tests, WMFW/bin parsing tests, coefficient read/write/acked-control timeout tests, power-up/down/run/stop sequencing tests, regmap fault injection, chunk pack/unpack tests, and debugfs lifecycle tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/cirrus/cs_dsp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/cirrus/cs_dsp_test_utils.h -->
# sources/distributed-fs/ceph-client/include/linux/firmware/cirrus/cs_dsp_test_utils.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/firmware/cirrus/cs_dsp_test_utils.h` declares KUnit support utilities for testing Cirrus DSP firmware loading, memory maps, regmap behavior, and mock WMFW/bin builders. The source was read as a complete 163-line file for this report.

## Important APIs, Types, and Functions

Important types include `struct cs_dsp_test`, `struct cs_dsp_mock_alg_def`, `struct cs_dsp_mock_coeff_def`, `struct cs_dsp_mock_xm_header`, opaque WMFW/bin builders, mock region arrays, mock region-size arrays, regmap helpers, XM header helpers, packed/unpacked memory conversion helpers, mock firmware builders for bin and WMFW blocks, and firmware getters.

## Control Flow

Tests initialize mock DSP/regmap state, build XM headers or WMFW/bin firmware blobs, add algorithm/coefficient/data/patch/info/name blocks, feed generated `struct firmware` objects to cs_dsp code, and inspect regmap dirtiness or dropped ranges.

## State and Persistence Behavior

`struct cs_dsp_test` carries KUnit, DSP, local private state, and a bus-write observation flag. Builders own temporary blob state until returned as firmware objects. No persistent state exists.

## Dependencies and Integration Points

It depends on regmap and WMFW format structures. It integrates with KUnit tests for `cs_dsp`, mock regmaps, and firmware loader-style in-memory blobs.

## Risks and Edge Cases

Mock format helpers must mirror real WMFW/bin ABI closely or tests can pass invalid assumptions. Packed/unpacked memory conversions are especially error-prone for 24-bit DSP words and optional ZM memory.

## Test Signals

The header itself is test support; signals are KUnit suites that build mock firmware, exercise missing/dirty regmap ranges, verify algorithm base calculations, and compare generated blobs with parser expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/cirrus/cs_dsp_test_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/cirrus/wmfw.h -->
# sources/distributed-fs/ceph-client/include/linux/firmware/cirrus/wmfw.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/firmware/cirrus/wmfw.h` defines the packed on-disk/in-memory structures and constants for Wolfson/Cirrus WMFW firmware and coefficient files. The source was read as a complete 208-line file for this report.

## Important APIs, Types, and Functions

Important constants include max name/description lengths, coefficient flags/types, core identifiers `WMFW_ADSP1`, `WMFW_ADSP2`, `WMFW_HALO`, region types, and memory type constants. Packed structs include `wmfw_header`, `wmfw_footer`, size records, `wmfw_region`, ID headers for ADSP1/ADSP2/Halo, algorithm headers, algorithm data, coefficient data, `wmfw_coeff_hdr`, and `wmfw_coeff_item`.

## Control Flow

There is no executable code. Firmware parsers read these packed records from firmware bytes, validate magic/length/version/core fields, discover memory regions and algorithms, and create coefficient controls.

## State and Persistence Behavior

These are firmware file ABI structures. Persistent state is the firmware/coefficient blob supplied by userspace, built-in firmware, or tests.

## Dependencies and Integration Points

It depends on kernel integer endian types and integrates with `cs_dsp`, mock firmware builders, firmware loader APIs, and Cirrus DSP client drivers.

## Risks and Edge Cases

All structures are packed and endian-specific, so alignment or field-size changes are ABI breaks. Variable-length `data[]` records need strict length validation to avoid overreads. Long memory type encodings and packed Halo regions must match parser assumptions.

## Test Signals

Parser tests for each WMFW format version/core, malformed length/magic/endian tests, coefficient control flag/type tests, and round-trip tests with `cs_dsp_test_utils` builders.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/cirrus/wmfw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/imx/dsp.h -->
# sources/distributed-fs/ceph-client/include/linux/firmware/imx/dsp.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/firmware/imx/dsp.h` declares the NXP i.MX DSP mailbox IPC interface. The source was read as a complete 71-line file for this report.

## Important APIs, Types, and Functions

Important exports are `DSP_MU_CHAN_NUM`, `struct imx_dsp_chan`, `struct imx_dsp_ops`, `struct imx_dsp_ipc`, `imx_dsp_set_data`, `imx_dsp_get_data`, `imx_dsp_ring_doorbell`, `imx_dsp_request_channel`, and `imx_dsp_free_channel`. Disabled `CONFIG_IMX_DSP` builds return `-ENOTSUPP`, `ERR_PTR(-EOPNOTSUPP)`, or no-op.

## Control Flow

Client drivers set private data, request mailbox channels, ring doorbells to notify DSP firmware, and receive reply/request callbacks through `imx_dsp_ops`.

## State and Persistence Behavior

`struct imx_dsp_ipc` stores four host/DSP channels, the device, callback ops, and private data. Runtime state is mailbox and firmware communication state only.

## Dependencies and Integration Points

It depends on device, types, and mailbox client APIs. It integrates with i.MX DSP firmware, MU/mailbox hardware, audio/remoteproc-style clients, and platform drivers.

## Risks and Edge Cases

Channel index validation is critical. Disabled stubs return two different unsupported errno values. Callback concurrency depends on mailbox context.

## Test Signals

i.MX DSP driver probe tests, mailbox loopback tests, invalid channel tests, callback ordering tests, and disabled-config build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/imx/dsp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/imx/ipc.h -->
# sources/distributed-fs/ceph-client/include/linux/firmware/imx/ipc.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/firmware/imx/ipc.h` defines the i.MX System Controller Firmware RPC message header and IPC accessors. The source was read as a complete 71-line file for this report.

## Important APIs, Types, and Functions

Important definitions are `IMX_SC_RPC_VERSION`, `IMX_SC_RPC_MAX_MSG`, opaque `struct imx_sc_ipc`, `enum imx_sc_rpc_svc`, `struct imx_sc_rpc_msg`, `imx_scu_call_rpc`, and `imx_scu_get_handle`. Disabled `CONFIG_IMX_SCU` builds return `-ENOTSUPP`.

## Control Flow

SCFW service shims build RPC messages with version/size/service/function fields, call `imx_scu_call_rpc()`, and optionally wait for a response. Clients can obtain the default SCU IPC handle with `imx_scu_get_handle()`.

## State and Persistence Behavior

The header owns no state. IPC state is held by the SCU driver and firmware channel; RPC messages are transient stack/buffer data.

## Dependencies and Integration Points

It integrates with i.MX SCU firmware, mailbox/IPI transport, PM/RM/MISC/IRQ service headers, and platform drivers needing SCFW services.

## Risks and Edge Cases

`IMX_SC_RPC_MAX_MSG` constrains message size. `have_resp` controls synchronous response handling. Service/function IDs must match firmware ABI.

## Test Signals

SCU RPC tests with response/no-response calls, service shim tests, firmware timeout/error injection, and disabled-config build tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/imx/ipc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/imx/s4.h -->
# sources/distributed-fs/ceph-client/include/linux/firmware/imx/s4.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/firmware/imx/s4.h` declares the minimal i.MX S4 IPC RPC message format. The source was read as a complete 20-line file for this report.

## Important APIs, Types, and Functions

It forward-declares `struct imx_s4_ipc` and defines packed `struct imx_s4_rpc_msg` with `ver`, `size`, `cmd`, and `tag`.

## Control Flow

There is no local flow. S4 IPC clients format command messages using this header before sending them to firmware transport code.

## State and Persistence Behavior

Only transient RPC message bytes are described. Persistent firmware state is outside the header.

## Dependencies and Integration Points

It integrates with NXP i.MX S4 firmware IPC clients and mailbox/firmware transport code.

## Risks and Edge Cases

The struct is packed firmware ABI; field order/size changes break communication. Callers must validate command tags and response matching externally.

## Test Signals

S4 IPC message layout tests, firmware command round-trips, and compile-time packed-size assertions in users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/imx/s4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/imx/sci.h -->
# sources/distributed-fs/ceph-client/include/linux/firmware/imx/sci.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/firmware/imx/sci.h` aggregates i.MX System Controller Interface service headers and declares SCU IRQ/SOC initialization helpers. The source was read as a complete 57-line file for this report.

## Important APIs, Types, and Functions

It includes SCU IPC plus MISC, PM, and RM service headers. APIs include `imx_scu_enable_general_irq_channel`, notifier register/unregister, `imx_scu_irq_group_enable`, `imx_scu_irq_get_status`, and `imx_scu_soc_init`, with `-EOPNOTSUPP` stubs when `CONFIG_IMX_SCU` is disabled.

## Control Flow

Platform code initializes SCU SOC support, enables a general IRQ channel, registers notifiers, enables IRQ groups, and queries group status through firmware-backed calls.

## State and Persistence Behavior

No state is owned here. IRQ channels, notifier lists, and SOC data are owned by the SCU implementation and firmware.

## Dependencies and Integration Points

It integrates with i.MX SCU firmware, notifier chains, IRQ service groups, SOC initialization, and included PM/RM/MISC services.

## Risks and Edge Cases

The mutual includes between `sci.h` and service headers rely on include guards. Disabled stubs uniformly return unsupported, so clients must handle absent SCU hardware.

## Test Signals

SCU IRQ notifier tests, group enable/status tests, SOC init tests, and disabled-config build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/imx/sci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/imx/sm.h -->
# sources/distributed-fs/ceph-client/include/linux/firmware/imx/sm.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/firmware/imx/sm.h` declares NXP i.MX SCMI extension helpers for miscellaneous controls, CPU control, and logical machine management. The source was read as a complete 99-line file for this report.

## Important APIs, Types, and Functions

It defines SCMI control IDs for i.MX95/i.MX94 audio/wake controls and `SCMI_IMX952_CTRL_BYPASS_AUDMIX`. APIs include `scmi_imx_misc_ctrl_get/set`, `scmi_imx_cpu_start`, `scmi_imx_cpu_started`, `scmi_imx_cpu_reset_vector_set`, `enum scmi_imx_lmm_op`, LMM operation flags, `scmi_imx_lmm_operation`, `scmi_imx_lmm_info`, and `scmi_imx_lmm_reset_vector_set`. Disabled driver configs return `-EOPNOTSUPP`.

## Control Flow

Clients call SCMI extension helpers to query/set SoC controls, start/stop CPUs, program CPU reset vectors, boot/power/shutdown logical machine managers, query LMM info, and set LMM reset vectors.

## State and Persistence Behavior

The header owns no state. Runtime and persistent effects are mediated by SCMI firmware and platform power/control domains.

## Dependencies and Integration Points

It depends on bitfield, errno, SCMI i.MX protocol definitions, and types. It integrates with SCMI transport, NXP SoC control drivers, CPU hotplug/boot flows, and virtualization/partition management.

## Risks and Edge Cases

SCMI IDs are firmware ABI. Disabled helpers fail at runtime; clients must degrade cleanly. Reset-vector programming carries boot/security risk if arguments are wrong.

## Test Signals

SCMI protocol mock tests, CPU start/reset-vector tests, LMM operation tests, unsupported-driver tests, and firmware error-path tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/imx/sm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/imx/svc/misc.h -->
# sources/distributed-fs/ceph-client/include/linux/firmware/imx/svc/misc.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/firmware/imx/svc/misc.h` defines i.MX SCU miscellaneous service function IDs and control APIs. The source was read as a complete 77-line file for this report.

## Important APIs, Types, and Functions

It defines `enum imx_misc_func` for set/get control, DMA groups, SECO image/auth, debug output, waveform capture, build info, unique ID, boot status/done, OTP fuse access, temperature, boot device, and button status. APIs are `imx_sc_misc_set_control`, `imx_sc_misc_get_control`, and `imx_sc_pm_cpu_start`, with unsupported stubs when SCU is disabled.

## Control Flow

Clients build MISC RPCs through these helpers to set/get resource controls or start a CPU with a physical address. The helpers call into the SCU IPC layer.

## State and Persistence Behavior

No state is owned here. Effects may be persistent or hardware-visible depending on the specific SCFW control, such as OTP, boot status, or CPU start.

## Dependencies and Integration Points

It includes `sci.h` and integrates with i.MX SCFW MISC service, SECO/security firmware, CPU boot, and platform control drivers.

## Risks and Edge Cases

Function IDs are firmware ABI. Some operations are security-sensitive or one-time-programming related. Disabled `imx_sc_rm_is_resource_owned`-style assumptions do not apply here; callers receive unsupported errors.

## Test Signals

SCU MISC RPC tests, control get/set tests, CPU start tests, firmware error injection, and disabled-config build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/imx/svc/misc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/imx/svc/pm.h -->
# sources/distributed-fs/ceph-client/include/linux/firmware/imx/svc/pm.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/firmware/imx/svc/pm.h` defines i.MX SCU Power Management service function IDs and constants. The source was read as a complete 85-line file for this report.

## Important APIs, Types, and Functions

It defines `enum imx_sc_pm_func` for system/partition/resource power modes, low-power requests, CPU resume address, clock rate/enable/parent, reset, boot/reboot, and CPU start. It also defines clock selector constants, power mode constants, and clock-parent constants.

## Control Flow

There are no functions in this header. SCU PM service shims use these function IDs and constants when building PM RPC messages to firmware.

## State and Persistence Behavior

The header owns no state. Firmware applies power, clock, reset, and boot state changes.

## Dependencies and Integration Points

It includes `sci.h` and integrates with i.MX SCFW PM service, clock drivers, power domain drivers, CPU boot/resume, and reset/reboot paths.

## Risks and Edge Cases

ID mismatches can power off or clock the wrong resource. Some clock constants intentionally alias per-resource meanings. Firmware policy may reject operations despite valid IDs.

## Test Signals

SCU PM RPC encoding tests, clock/power-domain integration tests, suspend/resume tests, reset/reboot tests, and firmware rejection-path tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/imx/svc/pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/imx/svc/rm.h -->
# sources/distributed-fs/ceph-client/include/linux/firmware/imx/svc/rm.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/firmware/imx/svc/rm.h` defines i.MX SCU Resource Management service function IDs and resource-owner helper APIs. The source was read as a complete 74-line file for this report.

## Important APIs, Types, and Functions

`enum imx_sc_rm_func` covers partition allocation/free/static/lock, DID queries, parent/assign/move operations, master/peripheral permissions, resource ownership, memory-region allocation/fragment/split/assign/permissions, pad assignment, and dumps. APIs are `imx_sc_rm_is_resource_owned` and `imx_sc_rm_get_resource_owner`; disabled builds return `true` for ownership and `-EOPNOTSUPP` for owner query.

## Control Flow

SCU RM clients use these IDs in RPC messages and call ownership helpers before touching resources. Disabled builds optimistically treat resources as owned to avoid blocking non-SCU platforms.

## State and Persistence Behavior

No state is owned here. Resource partitioning and ownership are maintained by SCFW.

## Dependencies and Integration Points

It includes `sci.h` and integrates with i.MX SCFW RM service, partitioning, device ownership, memory-region permissions, pad control, and platform drivers.

## Risks and Edge Cases

Ownership stubs returning `true` are convenient but can hide missing SCU checks if used on wrong platforms. RM operations are security/isolation-sensitive. Resource IDs and partition IDs are firmware ABI.

## Test Signals

SCU RM ownership tests, partition/resource assignment tests, disabled-config behavior tests, and firmware rejection/error-path tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/imx/svc/rm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/intel/stratix10-smc.h -->
# sources/distributed-fs/ceph-client/include/linux/firmware/intel/stratix10-smc.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/firmware/intel/stratix10-smc.h` defines Intel/Altera Stratix 10 secure monitor call IDs, call encodings, register protocols, and status codes for communicating from EL1 service drivers to EL3 secure firmware. The source was read as a complete 734-line file for this report.

## Important APIs, Types, and Functions

Important macros include `INTEL_SIP_SMC_STD_CALL_VAL`, `INTEL_SIP_SMC_FAST_CALL_VAL`, `INTEL_SIP_SMC_ASYNC_VAL`, status codes, FPGA configuration calls, protected register read/write/update calls, RSU status/update/notify/retry/DCMF calls, ECC DBE notification, service-completed polling, firmware/SVC version calls, mailbox send command, FPGA Crypto Service calls, HWMON temperature/voltage calls, and async poll/RSU async call IDs.

## Control Flow

Service-layer clients choose a FAST call for atomic/synchronous requests or STD/async calls for preemptible longer operations. The caller passes function ID in `a0` and request arguments in `a1` onward, often physical addresses rather than virtual pointers. Some async operations return busy/accepted and require `INTEL_SIP_SMC_SERVICE_COMPLETED` or async poll to retrieve completion data.

## State and Persistence Behavior

The header owns no state. State lives in secure firmware, reserved physical buffers, FPGA configuration state, RSU boot metadata, mailbox transaction IDs, FCS output buffers, and HWMON readings.

## Dependencies and Integration Points

It depends on ARM SMCCC encoding and bit operations. It integrates with Stratix10 service layer, FPGA manager, RSU driver, mailbox command transport, FCS/security services, HWMON, and out-of-tree secure firmware ABI.

## Risks and Edge Cases

The header is shared with secure firmware and is ABI-critical. Physical address arguments must point to DMA-safe/shared buffers. Async/busy status handling must not reuse buffers early. A malformed function ID or wrong FAST/STD mode can fail across firmware versions.

## Test Signals

SMC ABI compile-time value tests, service-layer mocked SMCCC tests, FPGA reconfiguration success/busy/error tests, RSU status/update tests, FCS buffer tests, HWMON read tests, and firmware-version compatibility tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/intel/stratix10-smc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/intel/stratix10-svc-client.h -->
# sources/distributed-fs/ceph-client/include/linux/firmware/intel/stratix10-svc-client.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/firmware/intel/stratix10-svc-client.h` declares the client-facing Stratix 10 service layer API for FPGA configuration, RSU, FCS, HWMON, mailbox commands, and asynchronous transactions. The source was read as a complete 392-line file for this report.

## Important APIs, Types, and Functions

Important definitions include service client names, service status codes, timeout constants, `enum stratix10_svc_command_code`, `struct stratix10_svc_client_msg`, `struct stratix10_svc_command_config_type`, `struct stratix10_svc_cb_data`, `struct stratix10_svc_client`, opaque `struct stratix10_svc_chan`, channel request/free APIs, memory allocate/free APIs, `stratix10_svc_send`, `stratix10_svc_done`, `async_callback_t`, and async add/remove/send/poll/done APIs.

## Control Flow

Clients request a named channel, allocate service-layer memory if needed, fill `stratix10_svc_client_msg`, send commands, receive completion callbacks with status and completed buffer addresses, then call `stratix10_svc_done()` or async done to release transaction resources. Async clients can register a unique client ID, send messages with a handler, poll completion, and remove transactions.

## State and Persistence Behavior

Channel and async transaction state are owned by the service layer. Client messages carry payload pointers, output pointers, lengths, command codes, and register-style arguments. Hardware/firmware state changes persist according to FPGA/RSU/FCS/HWMON operation semantics.

## Dependencies and Integration Points

It integrates with Stratix10 secure monitor calls, FPGA manager, RSU, FCS, HWMON, device model, mailbox buffers, and service-layer worker/callback infrastructure.

## Risks and Edge Cases

Timeout constants differ by client class. Clients must free service memory and channels, call done after completion/error, and handle busy/no-support/invalid-param statuses. Async handler lifetime and callback arguments must be protected from use-after-free.

## Test Signals

Service-layer client mock tests, FPGA reconfiguration buffer flow tests, RSU/FCS/HWMON command tests, timeout tests, async send/poll/done lifecycle tests, and channel allocation failure tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/intel/stratix10-svc-client.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/mediatek/mtk-adsp-ipc.h -->
# sources/distributed-fs/ceph-client/include/linux/firmware/mediatek/mtk-adsp-ipc.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/firmware/mediatek/mtk-adsp-ipc.h` declares MediaTek ADSP mailbox IPC structures and send API. The source was read as a complete 59-line file for this report.

## Important APIs, Types, and Functions

Important exports are request/response channel and opcode constants, mailbox enum values, opaque `struct mtk_adsp_ipc`, `struct mtk_adsp_ipc_ops`, `struct mtk_adsp_chan`, `struct mtk_adsp_ipc`, data accessors `mtk_adsp_ipc_set_data/get_data`, and `mtk_adsp_ipc_send`.

## Control Flow

Clients register reply/request callbacks, store private data, and call `mtk_adsp_ipc_send()` on a channel index with request/response opcode. Mailbox callbacks deliver firmware replies or requests into the provided ops.

## State and Persistence Behavior

`struct mtk_adsp_ipc` stores two mailbox channels, device pointer, ops, and private data. State is runtime IPC/mailbox state only.

## Dependencies and Integration Points

It depends on device, types, mailbox controller, and mailbox client APIs. It integrates with MediaTek ADSP firmware, audio DSP clients, and mailbox transport drivers.

## Risks and Edge Cases

Channel/opcode mismatches can deadlock request/response flows. Callback context and mailbox ownership must be handled by clients. There are no disabled stubs, so callers require the implementation to be linked.

## Test Signals

MediaTek ADSP IPC probe tests, mailbox loopback tests, invalid channel/opcode tests, callback ordering tests, and compile/link coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/mediatek/mtk-adsp-ipc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/meson/meson_sm.h -->
# sources/distributed-fs/ceph-client/include/linux/firmware/meson/meson_sm.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/firmware/meson/meson_sm.h` declares the Amlogic Meson secure monitor firmware call interface. The source was read as a complete 31-line file for this report.

## Important APIs, Types, and Functions

It defines command indexes for efuse read/write, chip ID, and A1 power-controller set/get. APIs include `meson_sm_call`, `meson_sm_call_write`, `meson_sm_call_read`, and `meson_sm_get`.

## Control Flow

Clients obtain a firmware handle from a device-tree firmware node, then invoke simple calls or buffer read/write calls with a command index and five 32-bit arguments.

## State and Persistence Behavior

The header owns no state. Secure monitor firmware owns command execution and persistent effects such as efuse writes or power-controller settings.

## Dependencies and Integration Points

It integrates with device tree firmware nodes, ARM secure monitor calls, Meson efuse/chip ID/power drivers, and platform firmware infrastructure.

## Risks and Edge Cases

Efuse write operations can be irreversible. Buffer size and command index validation are important. Secure monitor availability depends on platform firmware.

## Test Signals

Meson secure monitor probe tests, chip ID read tests, efuse read/write policy tests, power-controller call tests, and firmware-node lookup failure tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/firmware/meson/meson_sm.h -->
