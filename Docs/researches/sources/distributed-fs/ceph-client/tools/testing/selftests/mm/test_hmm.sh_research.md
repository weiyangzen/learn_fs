# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/test_hmm.sh

Purpose: wrapper script for HMM selftests that loads the `test_hmm` kernel module, runs `hmm-tests`, and unloads the module.

Important APIs and functions: `check_test_requirements()` enforces root, `modprobe`, and `CONFIG_TEST_HMM=m`; `load_driver()` optionally passes `spm_addr_dev0` and `spm_addr_dev1`; `run_smoke()` runs the only supported test mode; `usage()` documents invocations.

Control flow and state: after requirements pass, `run_test()` accepts only `smoke` with optional SPM addresses. It loads the module, invokes the sibling `hmm-tests` binary, unloads the module, and exits 0. External state is transient module load state.

Dependencies and risks: depends on root, module tools, `test_hmm` module, and compiled `hmm-tests`. The script does not explicitly propagate `hmm-tests` failure status because it ends with `exit 0`, so failures may only be visible in output.
