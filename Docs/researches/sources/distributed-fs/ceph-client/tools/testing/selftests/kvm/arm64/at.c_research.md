# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/at.c

Purpose: this arm64 KVM selftest validates emulation of address-translation (`AT`) instructions in EL2&0 and EL1&0 translation regimes, especially access-flag behavior and slow-path emulation through invalidated stage-2 mappings.

Important APIs and functions: macros `copy_el2_to_el1()`, `__at()`, and `test_at_insn()` encode AT operations and PAR_EL1 checks. Guest functions `test_at()` and `guest_code()` execute S1E2R/W and S1E1R/W with expected fault/nonfault behavior. Host `handle_sync()` clears the stage-1 PTE access flag and reloads the page-table memslot; `run_test()` drives ucalls.

Control flow: `main()` requires `KVM_CAP_ARM_EL2`, creates an EL2-capable vCPU, finalizes vCPUs, maps `TEST_ADDR`, obtains the PTE HVA, and runs the guest. The guest disables hardware access flag, expects access-flag faults, then enables HA if supported and expects successful AT results. Before each AT instruction, the guest syncs so userspace can clear PTE_AF and reload page-table mappings.

State and persistence: `ptep_hva` points to the host mapping of the tested PTE. Guest manipulates TCR/HCR/VTCR/VTTBR and PAR_EL1. No durable state is stored.

Dependencies and integration points: depends on EL2-capable arm64 KVM, sysreg helpers, libkvm page-table introspection, `vm_mem_region_reload()`, and ucall synchronization.

Risks: the test deliberately edits page tables and stage-2 mappings. It assumes the selected test virtual/physical address mapping is safe and that reloading the page-table memslot invalidates relevant KVM state. Hardware without HAFDBS only runs the faulting half.

Test signals: guest asserts PAR fault bit, fault status code, memory attributes, shareability, and translated PA. Unexpected sync commands or guest aborts fail.
