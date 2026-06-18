# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/btf_module.c

## Purpose
This small test verifies loading BTF for the selftest kernel module `bpf_testmod` and finding a known exported symbol in that module BTF.

## APIs, Types, and Functions
It uses `btf__load_vmlinux_btf`, `btf__load_module_btf`, `btf__find_by_name`, `btf__free`, and the global selftest environment flag `env.has_testmod`.

## Control Flow
`test_btf_module` skips when the test module is unavailable. Otherwise it loads vmlinux BTF, loads module BTF with vmlinux as the base, searches for `bpf_testmod_test_read`, asserts a positive type ID, and frees both BTF objects.

## State, Dependencies, and Integration
No persistent state is created. The test depends on the selftest module being loaded or discoverable, sysfs kernel/module BTF support, and valid vmlinux base BTF.

## Risks and Test Signals
The only success signal is a positive symbol type ID. Failures point to missing test module setup, module BTF load regressions, or symbol name drift in `bpf_testmod`.
