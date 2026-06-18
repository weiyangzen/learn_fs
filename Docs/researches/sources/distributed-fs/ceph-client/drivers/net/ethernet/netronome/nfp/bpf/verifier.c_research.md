<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/bpf/verifier.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/bpf/verifier.c

## Purpose
This file implements NFP-specific BPF verifier hooks. It rejects programs the NFP JIT/firmware cannot support, records verifier-derived metadata needed by translation, validates helper calls and pointer usage, tracks map-value access semantics for endian-safe atomics, computes subprogram stack usage, and mirrors verifier optimizations into JIT metadata.

## Important APIs, Types, And Functions
- Verifier hooks: `nfp_verify_insn()` runs per instruction, and `nfp_bpf_finalize()` runs after kernel verifier completion.
- Metadata navigation: `nfp_bpf_goto_meta()` efficiently moves through the metadata list by instruction index.
- Helper checks: `nfp_bpf_check_helper_call()`, `nfp_record_adjust_head()`, `nfp_bpf_stack_arg_ok()`, and `nfp_bpf_map_call_ok()`.
- Pointer and memory checks: `nfp_bpf_check_ptr()`, `nfp_bpf_check_store()`, `nfp_bpf_check_atomic()`, `nfp_bpf_check_stack_access()`, and `nfp_bpf_map_mark_used()`.
- ALU constraints: `nfp_bpf_check_alu()` records operand ranges and rejects unsupported multiplication/division ranges.
- Finalization/optimization hooks: `nfp_assign_subprog_idx_and_regs()`, `nfp_bpf_get_stack_usage()`, `nfp_bpf_insn_flag_zext()`, `nfp_bpf_opt_replace_insn()`, and `nfp_bpf_opt_remove_insns()`.

## Control Flow
For each verifier instruction callback, the driver locates the matching `nfp_insn_meta`, checks opcode support with the JIT callback table, rejects extended register numbers, and dispatches by instruction class. Helper calls are gated by firmware capability and argument shape. Loads/stores/atomics validate pointer types and record pointer state for translation. ALU operations store min/max source and destination ranges so the JIT can choose multiplication/division/shift sequences.

Finalize allocates subprogram metadata, assigns subprogram indexes and callee-save needs, imports kernel stack depths, accounts for return address and saved R6-R9 registers, computes max call-chain stack usage, verifies firmware stack limit, and copies zero-extension flags from verifier aux data. Replacement/removal hooks allow only verifier optimizations that the JIT can mirror, such as conditional jump hard-wiring and instruction removal flags.

## State And Persistence
The file mutates only per-program and per-map runtime metadata: instruction flags, pointer states, helper argument snapshots, ALU ranges, map use-map words, `adjust_head_location`, subprogram stack info, and computed `stack_size`. No hardware or disk state is changed directly.

## Dependencies And Integration Points
It depends on the Linux BPF verifier environment, verifier register/stack state, TC/XDP constants, NFP firmware capability state, BPF map offload state from `offload.c`, and the JIT metadata/layout in `main.h`. Its results are consumed directly by `jit.c`.

## Risks And Edge Cases
- The JIT trusts verifier metadata; accepting an unsupported pointer type, variable stack offset, unsupported helper argument, or unsafe map use can lead to bad firmware code generation.
- `nfp_bpf_map_update_value_ok()` depends on stack argument checks running first and on kernel stack-state semantics for zero initialization.
- Atomic map counters cannot be safely used after non-zero host-endian initialization; the code rejects those conflicts but only at tracked word granularity.
- Event output supports only `BPF_F_CURRENT_CPU` and warns that return codes/loss/reordering differ for offload.
- Subprogram stack walking assumes kernel verifier has prevented recursion and that recorded pseudo-call destinations are correct.
- `nfp_assign_subprog_idx_and_regs()` return value is ignored in finalize, so inconsistency would need later failures or logs to surface.

## Test Signals
Run BPF verifier/offload tests for unsupported opcodes, helper gating, adjust_head/tail capabilities, map helper stack arguments, event_output restrictions, pointer type changes across paths, stack access alignment/variable offsets, ALU64 multiplication/division range rejection, map atomic conflicts, subprogram stack accounting, verifier instruction replacement/removal, and JIT translation of finalized metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/bpf/verifier.c -->
