# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/get-reg-list.c

Purpose: this arm64 KVM selftest detects regressions in `KVM_GET_REG_LIST` by comparing vCPU register lists against blessed register sets across feature configurations such as base FP/SIMD, PMU, SVE, pointer authentication, EL2, and EL2 E2H0.

Important APIs and data: `struct feature_id_reg` maps optional registers to feature ID fields. Helper callbacks `filter_reg()`, `check_supported_reg()`, `check_reject_set()`, `finalize_vcpu()`, and `print_reg()` are consumed by common register-list test infrastructure. Register arrays include `base_regs`, `pmu_regs`, `vregs`, `sve_regs`, `pauth_addr_regs`, `pauth_generic_regs`, `el2_regs`, and `el2_e2h0_regs`. `vcpu_configs[]` enumerates all tested sublist combinations.

Control flow: common KVM selftest code creates vCPUs using each `vcpu_reg_list` configuration, enables requested features/capabilities, finalizes when needed, gets the actual reg list, filters host-dependent DEMUX registers, omits unsupported feature-gated registers, compares against expected arrays, and uses `print_reg()` to format unexpected/missing register IDs for updating the blessed lists.

State and persistence: the file holds static expected-register arrays and configuration descriptors. Runtime state is limited to a VM/vCPU per configuration. No files are written by the test, although printed output is designed to help maintainers update source arrays.

Dependencies and integration points: depends on arm64 KVM one-reg/list UAPI, feature capability constants, sysreg encoding macros, SVE/PAuth/PMU/EL2 capabilities, and common register-list harness declarations from KVM selftests. It encodes ABI expectations that must remain stable for old kernels.

Risks: blessed lists are large and must be carefully updated when the ABI intentionally grows. Some registers are feature-gated by ID registers rather than just KVM capabilities, so `feat_id_regs` must stay current. Duplicate or missing feature mappings can cause false positives. DEMUX registers are filtered because they vary with host cache topology.

Test signals: mismatched register lists, unexpected set rejection errno, unsupported optional register exposure, or unrecognized register ID formatting failures indicate regressions. Passing across all configurations indicates the arm64 reg-list ABI remains compatible.
