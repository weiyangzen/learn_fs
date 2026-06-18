# sources/distributed-fs/ceph-client/kernel/kexec_core.c

## Purpose
`kexec_core.c` implements the common in-kernel machinery behind kexec image staging and execution. It validates user- or file-mode segment layouts, allocates control/source pages, builds the self-contained indirection list consumed by architecture `machine_kexec()`, owns the global loaded reboot/crash images, exposes kexec status in sysfs, and provides sysctls that can permanently disable or count-limit kexec loads.

## Important APIs, Types, And Functions
Key exported/shared state is `atomic_t __kexec_lock`, `bool kexec_in_progress`, `bool kexec_file_dbg_print`, `struct kimage *kexec_image`, and `struct kimage *kexec_crash_image`. `do_kimage_alloc_init()` initializes `struct kimage` bookkeeping lists and crash hotplug fields. `sanity_check_segment_list()` enforces page alignment, non-overlap, size limits, crash-reserved-range containment, and memory acceptance. `kimage_alloc_control_pages()`, `kimage_alloc_page()`, `kimage_load_segment()`, `kimage_map_segment()`, and `kimage_free()` are the main image lifecycle helpers. `kexec_load_permitted()` gates loads by `CAP_SYS_BOOT`, `kexec_load_disabled`, and per-type load limits. `kernel_kexec()` executes the loaded image.

## Control Flow
Allocation starts with `do_kimage_alloc_init()`, segment validation, control-page allocation, then per-segment copying through `kimage_load_normal_segment()` or `kimage_load_crash_segment()`. Normal images build an indirection list of `IND_DESTINATION`, `IND_SOURCE`, `IND_INDIRECTION`, and `IND_DONE` entries so the relocation stub can copy pages at reboot time. Crash images copy directly into reserved crash memory. `kernel_kexec()` takes the NMI-safe lock, validates `kexec_image`, calls liveupdate and either the hibernation-like preserve-context path or normal reboot shutdown path, dumps kmsg, and transfers to `machine_kexec()`.

## State And Persistence
Loaded images persist in global pointers until exchanged or freed; page lists in each `kimage` track control, destination, unusable, and CMA-backed pages. Sysctls under `kernel/` hold process lifetime state: `kexec_load_disabled` is one-way to disabled, while `kexec_load_limit_panic` and `kexec_load_limit_reboot` decrement on successful permission checks. Sysfs under `/sys/kernel/kexec` reports `loaded`, crash status, crash size, CMA ranges, and crash elfcore header size when configured.

## Dependencies And Integration Points
The file depends on architecture hooks for allocation, preparation, cache flushing, shutdown, and execution (`arch_kexec_*`, `machine_kexec_*`). It integrates with crash dump reservation, CMA, syscore/PM/freezer/CPU hotplug, vmcoreinfo, liveupdate, sysctl, and `/sys/kernel` via `kernel_kobj`.

## Risks And Edge Cases
The core risks are memory corruption during page relocation, invalid crash-kernel destinations, overflow in segment math, and stale architecture cleanup if `kimage_free()` misses a path. The custom source/destination allocator can become O(N^2), and CMA segments bypass the normal indirection mapping. `kernel_kexec()` must preserve lock release and device resume paths after preserve-context failures.

## Test Signals
Useful signals include successful and failing `kexec_load`/`kexec_file_load` cases, segment overlap/alignment/oversize rejection, crash-kernel loads constrained to `crashk_res`, sysctl count-limit behavior, sysfs `loaded`/`crash_loaded` values, CMA segment loading, and architecture kexec selftests that verify control page allocation and final transfer.
