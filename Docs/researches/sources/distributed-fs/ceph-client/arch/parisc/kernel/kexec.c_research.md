# sources/distributed-fs/ceph-client/arch/parisc/kernel/kexec.c

## Purpose

`kexec.c` implements the PA-RISC machine-dependent kexec handoff. It stops secondary CPUs, maps the relocation code, copies the relocation stub, passes architecture-specific boot parameters, flushes caches/TLBs, disables interrupts, and jumps to the new kernel.

## Important APIs, Types, And Functions

External relocation symbols are `relocate_new_kernel()`, `relocate_new_kernel_size`, and offsets for initrd, cmdline, and free-memory fields. `machine_shutdown()` stops SMP CPUs. `machine_kexec()` performs the final handoff. `machine_kexec_prepare()` logs image metadata through `kexec_image_info()`. Cleanup and crash-shutdown hooks are present but empty.

## Control Flow

`machine_shutdown()` sends stop requests to secondary CPUs and waits until only one CPU remains online. `machine_kexec()` maps the image control code page at `FIX_TEXT_KEXEC`, flushes caches, prepares either a direct function pointer or a 64-bit function descriptor pointing at the fixed mapping, copies the relocation code into that mapping, writes command line, initrd, and free-memory values into relocation-code data slots, flushes caches and TLBs again, disables local IRQs, and calls the relocation stub with the page-masked image head, image start, and physical control page.

`machine_kexec_prepare()` currently only emits debug information for the image and segments.

## State And Persistence Behavior

The file mutates fixmap state, writes into the control code page, stops CPUs, flushes caches and TLBs, disables local interrupts, and transfers execution. It does not persist state across the new kernel except through the relocation stub arguments and patched relocation-code data slots.

## Dependencies And Integration Points

It depends on generic kexec `struct kimage`, PA-RISC fixmap definitions, cache/TLB flushing, function descriptor semantics, `PAGE0->mem_free`, SMP stop handling, and the assembly relocation routine.

## Risks

The relocation code must fit and be executable at `FIX_TEXT_KEXEC`. Offsets into the relocation code must match the assembly layout exactly. Secondary CPUs must be stopped before the handoff to avoid memory corruption. Incorrect function descriptor setup on 64-bit will branch to the wrong address. Cache/TLB flush ordering is critical before executing freshly copied code.

## Test Signals

Signals include successful `kexec -l` and `kexec -e`, correct cmdline/initrd visibility in the second kernel, no secondary CPU activity during handoff, debug segment logs when enabled, and successful operation on 32-bit and 64-bit builds.
