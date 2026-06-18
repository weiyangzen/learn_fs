# sources/distributed-fs/ceph-client/kernel/kexec_file.c

## Purpose
`kexec_file.c` implements the `kexec_file_load` syscall path where the kernel, not userspace, reads and interprets the kernel/initrd/cmdline files. It probes architecture file loaders, verifies signatures when configured, constructs kexec segments, locates memory holes, loads purgatory, stores SHA-256 digests for purgatory verification, and atomically installs or unloads default/crash images.

## Important APIs, Types, And Functions
Loader-facing APIs include `kexec_image_probe_default()`, `kexec_image_post_load_cleanup_default()`, `kexec_add_buffer()`, `kexec_locate_mem_hole()`, `kexec_load_purgatory()`, `kexec_purgatory_get_symbol_addr()`, and `kexec_purgatory_get_set_symbol()`. The syscall is `SYSCALL_DEFINE5(kexec_file_load, ...)`. Internal helpers read files with `kernel_read_file_from_fd()`, validate signatures through loader `verify_sig`, prepare segments, and clean temporary `kernel_buf`, `initrd_buf`, `cmdline_buf`, purgatory buffers, and IMA buffers.

## Control Flow
The syscall checks `kexec_load_permitted()`, validates flags, takes `kexec_trylock()`, chooses `kexec_image` or `kexec_crash_image`, handles unload by exchange, and otherwise allocates a file-mode `kimage`. Preparation reads kernel/initrd, probes the arch loader, optionally verifies signatures and lockdown policy, copies a NUL-terminated command line, adds IMA/KHO buffers, and calls the loader. After segment sanity checks, it allocates control and swap pages, calls `machine_kexec_prepare()`, copies vmcoreinfo for crash images, calculates digests, loads every segment, terminates the indirection list, runs post-load hooks, cleans temporary buffers, and exchanges the global image pointer.

## State And Persistence
File contents are transient until converted into `image->segment[]` and segment source pages. Installed images persist in the global kexec pointers. `segment_cma[]` records contiguous CMA allocations for zero-copy placement. Purgatory state lives in `image->purgatory_info` until copied and later cleaned. Signature enforcement is held in static `sig_enforce`, which can be forced on by `set_kexec_sig_enforced()`.

## Dependencies And Integration Points
The file depends on architecture loaders (`kexec_file_loaders`, `arch_kexec_kernel_image_probe()`, `arch_kexec_locate_mem_hole()`, relocation hooks), IMA, lockdown, PE signature verification, KHO handover, crash hotplug, memblock or system RAM walkers, DMA CMA, SHA-256 crypto, and purgatory ELF symbols. It also relies on core functions from `kexec_core.c`.

## Risks And Edge Cases
Major risks include accepting unsigned images under lockdown policy, placing segments over each other or over excluded architecture ranges, stale crash memory protection, CMA overlap, purgatory relocation errors, digest omissions, and cleanup leaks on late errors. The memory-hole search must handle top-down/bottom-up alignment, driver-managed RAM, crash ranges, KHO-only scratch memory, and `CONFIG_ARCH_KEEP_MEMBLOCK` differences.

## Test Signals
Signals include syscall flag validation, unload behavior, permission/limit checks, signature enforced/permissive paths, initrd omission, bad command-line NUL termination, memory-hole placement under overlap/excluded ranges, CMA success/fallback, purgatory symbol set/get, digest verification, crash-image protection toggles, and IMA/KHO segment inclusion.
