# sources/distributed-fs/ceph-client/tools/arch/x86/include/uapi/asm/svm.h

## Purpose
Defines AMD SVM exit codes and printable mappings used by KVM, tracing, and user-space tooling.

## APIs, Types, and Functions
Exports `SVM_EXIT_*` constants for CR/DR accesses, exceptions, interrupts, instruction intercepts, nested page faults, AVIC events, VMGEXIT, software exits, and invalid guest state. It also defines SEV-ES/SNP software VMGEXIT event IDs, `SVM_VMGEXIT_TERM_REASON()`, and `SVM_EXIT_REASONS`, a macro list mapping exit codes to names.

## Control Flow, State, and Persistence
There is no runtime code. The macro list is expanded by consumers into switch tables or arrays for decoding exit reason values.

## Dependencies and Integration
Uses exception vector macros such as `DE_VECTOR` from the broader x86 UAPI/KVM context. Integrated with KVM SVM run/trace paths and tools that display exit reasons.

## Risks and Test Signals
Risks include stale numeric values, missing new VMGEXIT events, and name-list omissions that make diagnostics less useful. Test signals are KVM SVM trace output, nested/SEV-ES/SNP selftests that hit VMGEXIT paths, and table-generation compile tests.
