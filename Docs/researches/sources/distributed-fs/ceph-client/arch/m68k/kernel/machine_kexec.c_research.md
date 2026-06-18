# sources/distributed-fs/ceph-client/arch/m68k/kernel/machine_kexec.c

## Purpose

`machine_kexec.c` implements the m68k architecture handoff for `kexec`, copying a small physical relocation stub into the control page, disabling interruptions, flushing caches, and jumping to the relocation code with enough CPU/MMU state to disable the old address space and start the new kernel.

## Important APIs, Types, and Functions

The standard architecture hooks are `machine_kexec_prepare()`, `machine_kexec_cleanup()`, `machine_shutdown()`, `machine_crash_shutdown()`, and `machine_kexec()`. `relocate_kernel_t` is the no-return function type matching `relocate_new_kernel` from `relocate_kernel.S`.

## Control Flow

Prepare, cleanup, shutdown, and crash shutdown are no-ops. The real path in `machine_kexec()` gets the virtual address of `image->control_code_page`, copies `relocate_new_kernel` through `relocate_new_kernel_size`, disables local interrupts, logs `image->start`, flushes all caches, combines `m68k_cputype` and `m68k_mmutype` into `cpu_mmu_flags`, and calls the control-page stub with the relocation list head, entry point, and CPU/MMU flags.

## State and Persistence Behavior

The function mutates the control code page contents and CPU interrupt/cache state. It does not persist kernel data structures because control should never return. The flags passed to the stub encode current hardware features so the assembly can safely disable MMU/cache state.

## Dependencies and Integration Points

It depends on `relocate_kernel.S`, `<linux/kexec.h>` image layout, `page_address()`, `__flush_cache_all()`, and setup globals `m68k_cputype`/`m68k_mmutype`. It integrates with generic kexec core through the architecture hook names.

## Risks and Edge Cases

The relocation stub must fit in the control code page and must be cache coherent after the copy. If the CPU/MMU flag packing drifts from `relocate_kernel.S` expectations, the stub may take the wrong MMU-disable path. The no-op crash shutdown means platform devices are not quiesced here; crash-kexec depends on earlier generic and platform behavior.

## Test Signals

`kexec -l` followed by `kexec -e` should reach the new kernel entry on 030/040/060-capable configurations. Instrumentation should show the copied stub size below one page, interrupts disabled before jump, and no stale instruction cache execution.
