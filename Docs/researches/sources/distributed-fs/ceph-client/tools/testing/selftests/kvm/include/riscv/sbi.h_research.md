# Research: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/riscv/sbi.h

# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/riscv/sbi.h

Purpose: RISC-V SBI constants for KVM selftests. It records SBI version fields, standard error codes, and extension ID ranges used when testing virtual SBI exposure.

Important APIs/types/functions: `SBI_SPEC_VERSION_DEFAULT`, major/minor masks and shifts, `SBI_SUCCESS`, `SBI_ERR_*`, and experimental extension range constants.

Control flow and state: no executable control flow. Guest and host tests use these constants to interpret SBI call results and validate extension metadata.

Dependencies and integration: included by RISC-V SBI selftests and works with `riscv/processor.h` extension probing. It does not depend on common KVM helpers directly.

Risks: SBI constants must track the SBI specification version supported by KVM. Error-code mismatches would cause tests to misclassify unsupported or invalid calls.

Test signals: SBI extension and error-path tests validate these definitions by comparing guest-observed return values with expected codes.
