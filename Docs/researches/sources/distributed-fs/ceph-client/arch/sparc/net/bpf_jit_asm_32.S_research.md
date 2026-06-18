# sources/distributed-fs/ceph-client/arch/sparc/net/bpf_jit_asm_32.S

Purpose: implements SPARC32 helper stubs used by the classic BPF JIT for packet data loads from linear skb data, paged skb data, and negative ancillary offsets.

Important APIs/functions: exports `bpf_jit_load_word`, `bpf_jit_load_half`, `bpf_jit_load_byte`, `bpf_jit_load_byte_msh`, and specialized positive/negative-offset variants. Slow paths call `skb_copy_bits()` or `bpf_internal_load_pointer_neg_helper()`.

Control flow: positive-offset helpers compare requested offset against skb head length and do direct loads when the bytes are linear. Unaligned word/half paths assemble values byte-by-byte. Slow paths allocate a register window, call `skb_copy_bits()`, load the scratch result, and branch to `bpf_error` on failure. Negative-offset paths reject offsets below `SKF_LL_OFF`, ask the BPF helper for a pointer, then load from it. `bpf_error` returns zero through the saved `%o7`.

State and persistence: no owned state; uses stack scratch space during slow paths and returns values in the BPF accumulator or X register.

Dependencies and integration points: called by `bpf_jit_comp_32.c` generated code. Depends on the register ABI from `bpf_jit_32.h`, skb helpers, and SPARC delay-slot/register-window conventions.

Risks: bounds checks must exactly protect direct loads. Return-through-saved-link handling must match the JIT prologue. Endianness and unaligned load assembly must match classic BPF semantics.

Test signals: JIT classic BPF packet filters reading bytes/halfwords/words at aligned, unaligned, paged, out-of-range, negative, and MSH offsets; failures should return zero.
