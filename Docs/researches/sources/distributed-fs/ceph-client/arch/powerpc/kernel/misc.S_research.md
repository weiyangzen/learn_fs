
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/misc.S

Purpose: common low-level PowerPC assembly helpers shared across 32-bit and 64-bit builds for early relocation math, nonlocal jump state save/restore, and current stack-frame inspection.

Important APIs/types/functions: `reloc_offset`; `add_reloc_offset`; `setjmp`; `longjmp`; `current_stack_frame`; exported `current_stack_frame`; `_ASM_NOKPROBE_SYMBOL` annotations for relocation helpers.

Control flow: `reloc_offset` returns zero via the fall-through into `add_reloc_offset`, while `add_reloc_offset(x)` uses a link-register branch trick to compare the current executing address against a linked address constant and add that runtime relocation delta to the input. `setjmp` saves LR, SP, TOC/r2, CR, and callee-saved GPRs into the caller-supplied buffer and returns 0. `longjmp` restores that state, sets LR, and returns the supplied nonzero value or 1 if the supplied value is zero. `current_stack_frame` loads the caller's backchain from the current stack pointer.

State and persistence: all state is caller-provided memory for jump buffers or CPU registers; no kernel global state is retained.

Dependencies and integration: used by early boot/relocation and exception-like control transfers before normal C runtime assumptions fully apply. Depends on ABI register layout, `SZL`, and offsets selected by 32-bit versus 64-bit configuration.

Risks: jump buffer layout must match callers and architecture width; restoring stale r2/TOC or CR can corrupt subsequent C execution; relocation helper must remain unprobeable because it is used in delicate early contexts.

Test signals: boot relocatable kernels, run paths using kernel `setjmp/longjmp`, inspect stack unwinding users of `current_stack_frame`, and build PPC32/PPC64 variants.
