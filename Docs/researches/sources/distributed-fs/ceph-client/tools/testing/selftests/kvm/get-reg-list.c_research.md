<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/get-reg-list.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/get-reg-list.c

Purpose: this architecture-shared test detects regressions in `KVM_GET_REG_LIST` by comparing the current register list for each vCPU configuration against architecture-supplied blessed lists. Missing blessed registers are failures; new registers are reported for maintainers to add to the baseline.

Important APIs, types, and functions: external `vcpu_configs[]` entries provide named register sublists, capability requirements, rejected-set and skipped-set lists. Weak hooks `check_supported_reg()`, `filter_reg()`, `print_reg()`, `check_reject_set()`, and `finalize_vcpu()` allow architecture-specific behavior. On arm64, `prepare_vcpu_init()` applies feature bits before `aarch64_vcpu_setup()`. `run_test()` gets `vcpu_get_reg_list()`, builds the blessed array, tests get/writeback or expected set rejection for present blessed registers, counts new/missing registers, and reports pass/fail.

Control flow: `main()` parses optional `--config=`, `--list`, and `--list-filtered`. Listing modes require a single config. For each selected configuration, it forks a child to isolate skips/failures, runs `run_test()`, and treats non-skip nonzero exit as failure. In normal mode, it prints candidate additions for new regs and missing-reg diagnostics for regressions.

State, persistence, and dependencies: state is process-local allocated register arrays and transient barebones VMs/vCPUs. Dependencies include architecture-specific `processor.h` definitions that supply `vcpu_reg_list` data, KVM one-reg ioctls, fork/wait, and kselftest assertion helpers. It writes no files; `--list` output can be captured manually to update blessed lists elsewhere.

Risks and edge cases: new registers are tolerated but surfaced; missing supported registers are failures because they can break migration from older to newer kernels. Some registers are advertised but must reject set or be skipped for set. The test writes back exactly the value read to avoid inventing unsupported register values. Filtered regs do not count as new.

Test signals: per-config `PASS`, counts of blessed/current/filtered registers when differences exist, printed new-register snippets, missing-register diagnostics, and aggregate child exit status from `main()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/get-reg-list.c -->
