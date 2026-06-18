# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/external_aborts.c

Purpose: this arm64 KVM selftest validates userspace injection and delivery of synchronous external aborts and SError exceptions, including MMIO aborts, ESR_EL2.ISV=0 NISV behavior, stage-1 page-table-walk aborts, EASE routing, RAS ESR payloads, and EL2 AMO behavior.

Important APIs and functions: VM setup helper `vm_create_with_dabt_handler()` installs data-abort handlers and maps an MMIO address. Injection helpers `vcpu_inject_sea()` and `vcpu_inject_serror()` write `struct kvm_vcpu_events`. Test cases include `test_mmio_abort()`, `test_mmio_nisv()`, `test_mmio_nisv_abort()`, `test_serror_masked()`, `test_serror()`, `test_s1ptw_abort()`, `test_serror_emulated()`, `test_mmio_ease()`, and `test_serror_amo()`.

Control flow: `main()` runs each case sequentially and gates the AMO/EL2 case on `test_supports_el2()`. MMIO cases run the guest until a KVM exit or `KVM_RUN` failure, inject an abort/event, then expect the guest handler to finish. SError cases inject pending SError before or after guest sync and validate masking/unmasking paths. S1PTW mutates a PTE to an invalid PA to force an external abort during page-table walk.

State and persistence: global `expected_abort_pc` lets guest handlers verify the precise faulting instruction. Events are held only in KVM vCPU event state. No durable state is stored.

Dependencies and integration points: depends on arm64 exception vectors, KVM vCPU events UAPI, `KVM_CAP_ARM_NISV_TO_USER`, `KVM_EXIT_ARM_NISV`, MMIO exits, RAS ID fields, SCTLR2 EASE support, and optional EL2 support.

Risks: feature availability controls some paths; unsupported DF2/EASE is skipped locally. The test edits guest page tables and relies on exact ESR/FSC semantics. NISV behavior intentionally expects an `ENOSYS` KVM_RUN failure without the capability.

Test signals: assertions check exit reasons, MMIO/NISV addresses, ESR exception classes, FSC values, SError ISS payloads under RAS, pending ISR bits, and clean `GUEST_DONE` after injected exceptions.
