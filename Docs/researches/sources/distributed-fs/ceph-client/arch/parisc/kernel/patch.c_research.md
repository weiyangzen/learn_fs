# sources/distributed-fs/ceph-client/arch/parisc/kernel/patch.c

Purpose: provides PA-RISC runtime text patching for kernel and module code, including strict RWX environments where direct writes to text mappings are not allowed.

Important types and functions are `struct patch`, `patch_lock`, `patch_map`, `patch_unmap`, `__patch_text_multiple`, `__patch_text`, `patch_text_stop_machine`, `patch_text`, and `patch_text_multiple`. The public wrappers run through `stop_machine_cpuslocked`; the double-underscore variants perform the actual patching and are marked `__kprobes` so they can be used safely around probing infrastructure.

Control flow first flushes dcache and icache aliases for the target range and flushes the kernel TLB range. `patch_map` decides whether the target is module or core kernel text and whether strict module/kernel RWX requires a writable fixmap alias. It maps the backing page into `FIX_TEXT_POKE0`, acquires `patch_lock` with IRQ save, and returns the writable address. `__patch_text_multiple` copies 32-bit instructions, remapping if the sequence crosses a page boundary, then flushes the modified alias range and TLB before unmapping and releasing the lock.

State is transient: fixmap slot contents, IRQ flags, cache/TLB state, and patched text bytes. Persistent behavior is the modified instruction stream. Dependencies include `core_kernel_text`, `vmalloc_to_page`, `virt_to_page`, fixmap APIs, cache/TLB flush assembly from `pacache.S`, and generic `stop_machine`.

Risks include partial patching if callers pass lengths not divisible by four, stale instruction cache if flush order changes, page-boundary remap mistakes, deadlock if called outside the expected CPU-locking context, and strict RWX differences between modules and core text. Test signals include alternatives/livepatch/ftrace/kprobe text modifications, SMP stop-machine stress, strict kernel/module RWX builds, and execution of newly patched instructions without illegal-instruction or stale-code behavior.
