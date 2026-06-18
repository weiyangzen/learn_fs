<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sched_ext/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/sched_ext/config

## Purpose

Kernel config fragment for sched_ext selftests.

## Important APIs, Types, and Functions

Requests CONFIG_SCHED_CLASS_EXT, cgroups and EXT_GROUP_SCHED, BPF, BPF_SYSCALL, DEBUG_INFO, and DEBUG_INFO_BTF.

## Control Flow and Integration

Consumed by selftest config tooling so BPF struct_ops schedulers can be built and loaded.

## State and Persistence Behavior

Static metadata only.

## Dependencies and Integration Points

sched_ext, BPF syscall, BTF debug info, and cgroup scheduler support.

## Risks and Edge Cases

BTF availability and sched_ext kernel support are hard requirements; missing options turn most tests into build/load failures.

## Test Signals

Config is validated by successful sched_ext Makefile build and runner execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sched_ext/config -->
