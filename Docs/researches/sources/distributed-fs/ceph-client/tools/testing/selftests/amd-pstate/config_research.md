# sources/distributed-fs/ceph-client/tools/testing/selftests/amd-pstate/config

Purpose: kselftest kernel config fragment for AMD P-state unit testing.

Important APIs/types/functions: sets `CONFIG_X86_AMD_PSTATE_UT=m`.

Control flow: no runtime flow.

State and persistence: declarative build configuration.

Dependencies/integration: used by kselftest/config tooling to request the test module.

Risks and test signals: if the kernel is not built with this module, `basic.sh` skips.
