<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/ucna_injection_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/ucna_injection_test.c

## Purpose
This test verifies userspace injection of UnCorrectable No Action required machine-check errors through KVM MCE APIs. It checks both CMCI interrupt delivery and recording of UCNA data in machine-check bank registers.

## Important APIs, Types, and Functions
Key functions are `ucna_injection_guest_code()`, `guest_cmci_handler()`, `inject_ucna()`, `run_ucna_injection()`, `test_ucna_injection()`, `setup_mce_cap()`, `create_vcpu_with_mce_cap()`, and `run_vcpu_expect_gp()`. It uses `KVM_X86_GET_MCE_CAP_SUPPORTED`, `KVM_X86_SETUP_MCE`, `KVM_X86_SET_MCE`, `struct kvm_x86_mce`, MCE MSRs, xAPIC CMCI vector programming, and APIC default GPA mapping.

## Control Flow, State, and Persistence
The host creates three vCPUs: one with CMCI support for the main injection flow, one without CMCI support, and one for reserved-bit validation. The main guest enables xAPIC, programs LVTCMCI, enables per-bank CMCI, syncs for a first UCNA injection, records the bank address, disables CMCI, syncs for a second UCNA, and records again. The host injects two MCEs and verifies only the first caused a CMCI interrupt while both updated bank address registers. The other guests intentionally write invalid/unsupported MCI_CTL2 bits and should #GP.

## Dependencies and Integration Points
This integrates with KVM MCE setup, machine-check bank MSRs, CMCI delivery through LAPIC, xAPIC mapping, guest exception handlers, and host MCE capability filtering.

## Risks and Test Signals
Risks include incorrect MCG capability masking, signaling UCNA despite CMCI disabled, missing register recording, and reserved-bit validation failures. Signals are one CMCI interrupt, matching first/second UCNA addresses, and expected guest #GP syncs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/ucna_injection_test.c -->
