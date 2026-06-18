# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/flds_emulation.h

Purpose: Provides a shared helper for tests that intentionally force KVM emulation failure on the unsupported `flds [eax]` instruction and then validate userspace-visible failure metadata.

Important APIs/types/functions: `FLDS_MEM_EAX` defines the raw opcode bytes `0xd9 0x00`; `flds(u64 address)` emits the instruction with the target address in EAX; `handle_flds_emulation_failure_exit()` validates `KVM_EXIT_INTERNAL_ERROR`, `KVM_INTERNAL_ERROR_EMULATION`, instruction-byte flags, opcode bytes, and advances guest RIP by two bytes.

Control flow: A test calls `flds()` on an address that forces KVM emulation, then invokes `handle_flds_emulation_failure_exit()` after `KVM_RUN` exits. The helper checks the emulation failure payload and rewrites RIP to resume after the failed instruction.

State and persistence behavior: The helper only mutates the vCPU RIP via `KVM_GET_REGS`/`KVM_SET_REGS`. It has no standalone state or persistence.

Dependencies and integration points: Integrates with `struct kvm_run.emulation_failure`, KVM internal-error ABI, and tests such as `exit_on_emulation_failure_test.c`.

Risks and maintenance notes: It assumes `flds [eax]` remains unsupported by the KVM emulator. If support is added, tests using this helper will no longer get the expected failure. Opcode-size assumptions must remain aligned with the emitted instruction.

Test signals: In downstream tests, successful helper validation means KVM reported exact failing instruction bytes and userspace can recover by advancing RIP. Failure indicates missing or malformed emulation-failure metadata.
