# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/exit_on_emulation_failure_test.c

Purpose: Verifies that an unsupported emulated instruction exits to userspace with `KVM_EXIT_INTERNAL_ERROR` and an emulation-failure payload when `KVM_CAP_EXIT_ON_EMULATION_FAILURE` behavior is exercised.

Important APIs/types/functions: `guest_code()` executes `flds()` against an MMIO address; `main()` creates an MMIO-backed hole and uses `handle_flds_emulation_failure_exit()` from `flds_emulation.h` to validate the exit. The file depends directly on the shared `flds` failure helper.

Control flow: The guest attempts `flds [eax]` using an address that forces KVM instruction emulation. Since the emulator is known not to support this instruction, the vCPU exits to userspace. The host checks internal-error subtype, instruction bytes, instruction size, advances RIP, and can continue or finish the test.

State and persistence behavior: No durable state. The only mutation is host-side RIP advancement after the expected emulation failure.

Dependencies and integration points: Depends on KVM instruction emulator failure reporting, MMIO-triggered emulation, and the `flds_emulation.h` helper's exact opcode expectations.

Risks and maintenance notes: If KVM learns to emulate `flds`, this test must choose a different unsupported instruction or update expectations. Payload layout and instruction-byte flags are ABI-sensitive.

Test signals: Passing means KVM exits to userspace with complete emulation-failure metadata instead of silently failing or injecting an unexpected guest exception. Failures point to emulator reporting or exit-on-failure regressions.
