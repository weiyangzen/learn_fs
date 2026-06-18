<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/bpf/jit.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/bpf/jit.c

## Purpose
This file is the NFP eBPF JIT compiler. It translates verified eBPF programs for TC direct-action and XDP into NFP microcode instructions, performs NFP-specific optimizations, emits helper/subprogram/stack handling, fixes branches and relocations, and produces per-vNIC relocated ustore images with ECC.

## Important APIs, Types, And Functions
- Public entry points: `nfp_bpf_jit_prepare()` records branch and subprogram metadata, `nfp_bpf_jit()` optimizes and translates a program, `nfp_bpf_supported_opcode()` exposes opcode support to the verifier, and `nfp_bpf_relo_for_vnic()` creates a relocated image for one vNIC.
- Low-level emitters: `emit_alu()`, `emit_shf()`, `emit_immed()`, `emit_cmd()`, `emit_br_relo()`, `emit_br_bit_relo()`, CSR helpers, and wrappers like `wrp_immed()`, `wrp_mov()`, and `wrp_zext()`.
- Translation callbacks: `instr_cb[256]` maps supported eBPF opcodes to callbacks for ALU64/ALU32, shifts, endian conversion, packet loads, memory loads/stores, atomics, jumps, calls, and exits.
- Memory paths: `mem_ldx()`, `mem_stx()`, `mem_op_stack()`, `data_ld_host_order*()`, `nfp_cpp_memcpy()`, and packet-cache helpers implement stack, packet, context, and map-value accesses.
- Helper/subprogram support: `adjust_head()`, `adjust_tail()`, `map_call_stack_common()`, `nfp_get_prandom_u32()`, `nfp_perf_event_output()`, `bpf_to_bpf_call()`, prologue/epilogue helpers, and callee-register save/restore routines.
- Optimization passes: `nfp_bpf_opt_reg_init()`, `nfp_bpf_opt_neg_add_sub()`, `nfp_bpf_opt_ld_mask()`, `nfp_bpf_opt_ld_shift()`, `nfp_bpf_opt_ldst_gather()`, and `nfp_bpf_opt_pkt_cache()`.

## Control Flow
Preparation walks the metadata list and records jump destinations; pseudo calls mark subprogram starts. `nfp_bpf_jit()` replaces map pseudo pointers with firmware table ids or neutral map ids, runs optimization passes, and calls `nfp_translate()`. Translation emits an intro that derives packet length, then walks instruction metadata in order, sets each instruction's output offset, emits subprogram prologues when needed, skips optimized instructions, invokes the opcode callback, emits TC/XDP outro code and optional callee-register subroutines, pads for the ustore prefetch window, and fixes relative branches.

The generated program uses pairs of NFP GPRs for 64-bit BPF registers. Stack is modeled in local memory with `stack_reg()`/LM pointer setup. Packet accesses use packet vector pointer/length with explicit bounds checks for classic loads and cached/gathered CPP reads for repeated packet loads. Map values use 40-bit addressing and atomic add commands. Helper calls are emitted as relocated branches to firmware helper addresses, with return addresses loaded through agreed registers.

Relocation is two-stage. Translation leaves `OP_RELO_TYPE` markers in branch/immediate instructions for relative branches, helper calls, normal/abort exits, next-packet target, and callee save/restore routines. `nfp_bpf_relo_for_vnic()` copies the generic image, applies the vNIC `start_off` and `tgt_done`, replaces helper relocations with parsed firmware helper addresses, clears relocation bits, and calculates ustore ECC.

## State And Persistence
The compiler mutates `struct nfp_prog`: instruction metadata flags, generated `prog`, length/allocation fields, target offsets, stack size/depth, subprogram info, map record ids, and error status. No disk state is written. Firmware-visible persistence occurs later when `offload.c` DMA-loads the relocated image and asks firmware to install it.

## Dependencies And Integration Points
The JIT depends on `nfp_asm.h` instruction encodings, NFP CSR/register conventions, BPF verifier metadata captured in `main.h`, firmware capabilities/helper addresses in `struct nfp_app_bpf`, Linux reciprocal division helpers, packet-classifier constants, and NFP netdev configuration offsets. It is invoked from BPF offload ops in `offload.c` after verifier preparation/finalization.

## Risks And Edge Cases
- Verifier hooks must reject cases the JIT cannot encode, such as unsupported pointer types, variable map offsets, non-constant divides, oversized stack, unsupported helpers, or unsafe atomics.
- Branch fixup assumes each translated block ends in an expected branch; optimized-out jump targets or unexpected delay-slot lengths produce hard translation failures.
- NFP branch delay slots and LM pointer update nops are timing-sensitive; changing emitted instruction counts can break offset assertions.
- Map-value atomics require endian-aware initialization and use-map tracking to avoid mixing host-endian values with firmware atomic counters.
- Packet-cache and load/store gather optimizations rely on pointer id/offset stability and no jumps into the middle of optimized sequences.
- `nfp_bpf_relo_for_vnic()` must clear relocation bits before ECC calculation; stale relocation markers would corrupt hardware instructions.

## Test Signals
Use verifier/JIT selftests for every supported opcode class, TC and XDP return mapping, packet bounds aborts, helper calls, adjust_head/tail success and failure, BPF-to-BPF calls with and without callee-saved registers, map lookup/update/delete and atomics, packet cache/gathered memcpy optimization cases, live reload relocation, program-size/stack-limit rejection, ustore validity/ECC checks, and hardware packet forwarding with expected TC/XDP actions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/bpf/jit.c -->
