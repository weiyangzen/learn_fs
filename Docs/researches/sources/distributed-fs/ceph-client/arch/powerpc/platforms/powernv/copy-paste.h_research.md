
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/copy-paste.h

Purpose: exposes inline wrappers for PowerPC VAS copy/paste instructions used by PowerNV accelerator code.

Important APIs: `vas_copy(void *crb, int offset)` emits the `copy` instruction using the command/request block pointer and offset. `vas_paste(void *paste_address, int offset)` emits the `paste` instruction, reads CR0 through `mfocrf`, and returns the condition-code bits after masking out summary overflow.

Control flow and state: both helpers are single inline assembly operations with `memory` clobbers. `vas_paste()` returns hardware status encoded in CR0; no memory or global state is maintained by the wrapper itself.

Dependencies and integration points: depends on opcode macros from `asm/ppc-opcode.h` and CR field constants from `asm/reg.h`. Included by PowerNV VAS code that submits accelerator requests.

Risks: register constraints and CR0 handling must match instruction semantics exactly. Callers must provide valid MMIO/architected addresses and interpret nonzero paste status correctly. The helpers provide no retry, ordering beyond the assembly memory clobber, or validation.

Test signals: successful VAS accelerator submission paths, paste error handling, compiler build coverage across supported PowerPC toolchains, and hardware tests that verify CR0 status propagation.
