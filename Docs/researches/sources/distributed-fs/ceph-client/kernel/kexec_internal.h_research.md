# sources/distributed-fs/ceph-client/kernel/kexec_internal.h

## Purpose
`kexec_internal.h` is the private boundary between the kexec core, file loader, ELF loader, purgatory support, and optional handover support. It centralizes shared prototypes and the NMI-safe kexec lock helpers.

## Important APIs, Types, And Functions
It declares `do_kimage_alloc_init()`, `sanity_check_segment_list()`, `kimage_free_page_list()`, `kimage_free()`, `kimage_load_segment()`, `kimage_terminate()`, and `kimage_is_destination_range()`. It defines `kexec_trylock()` and `kexec_unlock()` around `atomic_t __kexec_lock` using acquire/release semantics. Under `CONFIG_KEXEC_FILE`, it exposes `kimage_file_post_load_cleanup()`, `kexec_purgatory`, and `kexec_purgatory_size`. Under `CONFIG_KEXEC_HANDOVER`, it exposes `kho_locate_mem_hole()` and `kho_fill_kimage()`.

## Control Flow
The header does not execute control flow itself, but shapes all kexec paths: loaders allocate a `kimage`, validate segments, load segments, terminate the indirection page list, and free images through this interface. `kexec_trylock()` is used by load and execution paths to serialize image mutation and crash-image access.

## State And Persistence
The only state named here is `__kexec_lock`, which persists for the kernel lifetime. Inline stubs for disabled configs preserve call-site simplicity without storing state.

## Dependencies And Integration Points
The header depends on `<linux/kexec.h>` and optional `<linux/purgatory.h>`. It is included by `kexec_core.c` and `kexec_file.c`, and indirectly constrains architecture hooks that operate on `struct kimage` and `struct kexec_buf`.

## Risks And Edge Cases
Because `__crash_kexec()` may happen during NMI panic, the lock intentionally avoids sleeping locks. Any future replacement must keep NMI safety and release/acquire ordering. Config stubs must retain semantics: no file cleanup when file loading is absent and permissive no-op KHO behavior when handover is absent.

## Test Signals
Compile coverage across `CONFIG_KEXEC_FILE`, `CONFIG_KEXEC_HANDOVER`, and crash dump combinations is the primary signal. Runtime load/execution tests should show no deadlock under concurrent load/unload and panic-crash paths.
