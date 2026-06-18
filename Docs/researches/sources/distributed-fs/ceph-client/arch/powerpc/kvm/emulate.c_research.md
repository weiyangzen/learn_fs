
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/emulate.c

## Purpose
Implements generic PowerPC instruction emulation used by KVM when a guest traps on privileged or special instructions. It handles decrementer programming, common SPR reads/writes, traps, KVM software breakpoints, and dispatches unknown core-specific instructions to the active backend.

## Important APIs, Types, And Functions
Exports `kvmppc_emulate_instruction()`. Other important functions are `kvmppc_emulate_dec()`, `kvmppc_get_dec()`, `kvmppc_emulate_mtspr()`, and `kvmppc_emulate_mfspr()`. It uses `enum emulation_result`, `ppc_inst_t`, disassembly helpers such as `get_op()`, `get_xop()`, `get_rs()`, `get_rt()`, and `get_sprn()`, and backend callbacks `emulate_mtspr`, `emulate_mfspr`, and `emulate_op`.

## Control Flow
`kvmppc_emulate_instruction()` fetches the trapped instruction with `kvmppc_get_last_inst()`, decodes primary opcode and extended opcode, and first handles generic traps, `mfspr`, `mtspr`, `tlbsync`, and the KVM software breakpoint opcode. SPR emulation reads/writes SRR, PVR, PIR, timebase/decrementer, and SPRG registers locally; unrecognized SPRs are delegated to backend ops. If generic decoding fails, the backend `emulate_op` gets a final chance. Successful emulation advances PC by 4.

## State And Persistence
Touches vCPU architectural state: GPRs, PC, SRR, SPRGs, decrementer values, hrtimer state, `last_exit_type`, and debug exit fields. `kvmppc_emulate_dec()` stores `dec`, starts/cancels the decrementer hrtimer, and records the timebase at programming time. No global persistent state is created.

## Dependencies And Integration Points
Depends on KVM host structures, PowerPC disassembly/opcode helpers, timebase conversion, Book3S/BookE exception queue helpers, `timing.h`, and tracepoint `kvm_ppc_instr`. It is called from backend run loops after instruction-related exits.

## Risks
The emulator only covers a small generic subset; unsupported instructions become backend responsibilities or inject errors. PC advancement is fixed at 4 and the source comment notes prefixed instructions would need `ppc_inst_len()`. Decrementer behavior differs between BookE and Book3S, and wrong interrupt dequeue/requeue behavior can cause timer loss or storms.

## Test Signals
Tracepoint `kvm_ppc_instr` shows decoded emulation results. Useful tests include guests executing SPR accesses, decrementer programming, trap instructions, KVM breakpoints producing `KVM_EXIT_DEBUG`, and backend-specific fallback instructions.
