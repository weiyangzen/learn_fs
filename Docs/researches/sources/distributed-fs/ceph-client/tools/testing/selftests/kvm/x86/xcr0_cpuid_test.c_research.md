<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/xcr0_cpuid_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/xcr0_cpuid_test.c

## Purpose
This test validates that KVM exposes a sane guest XCR0/CPUID xfeature model. It checks architectural dependencies among XSAVE features and rejects enabling unsupported XCR0 bits.

## Important APIs, Types, and Functions
Important macros are `ASSERT_XFEATURE_DEPENDENCIES` and `ASSERT_ALL_OR_NONE_XFEATURE`. `guest_code()` uses `set_cr4(OSXSAVE)`, `xgetbv(0)`, `this_cpu_supported_xcr0()`, `xsetbv_safe()`, feature masks for FP/SSE/YMM/MPX/AVX512/AMX, and guest assertions.

## Control Flow, State, and Persistence
`main()` requires XSAVE, creates one vCPU, and runs until `GUEST_DONE`. The guest enables OSXSAVE, compares initial XCR0 against supported XCR0, validates dependency/all-or-none rules, successfully sets XCR0 to FP-only and then all supported bits, and iterates all unsupported bit positions expecting #GP if any unsupported bit is added. State is guest CR4.OSXSAVE, XCR0, and CPUID-derived supported xfeature mask.

## Dependencies and Integration Points
It integrates with KVM CPUID xfeature enumeration, XSETBV emulation/hardware execution, CR4.OSXSAVE handling, and XSAVE feature masks.

## Risks and Test Signals
Risks include advertising incoherent xfeature sets, initializing XCR0 to a value unusable by the guest, or allowing unsupported bits. Signals are guest dependency assertions, successful supported `XSETBV`, and `#GP` for every unsupported bit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/xcr0_cpuid_test.c -->
