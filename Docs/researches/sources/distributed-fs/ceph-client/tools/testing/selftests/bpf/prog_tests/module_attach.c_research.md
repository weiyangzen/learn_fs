<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/module_attach.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/module_attach.c

Purpose: tests BPF attachment to functions and writable tracepoints in `bpf_testmod`, including read-only, writable, and detach behavior.

Important APIs and functions: `trigger_module_test_writable()` opens/writes/reads the module sysfs test file. `test_module_attach_prog()` selects skeleton programs by name, attaches, triggers module behavior with requested read/write sizes, and verifies BSS counters. `test_module_attach_writable()` covers writable cases. `test_module_attach_detach()` validates that destroying/detaching a link stops future hits. `test_module_attach()` iterates read and detach program-name arrays.

Control flow: per-program subtests load `test_module_attach`, attach the selected program, trigger module IO, assert outputs, then destroy. Detach tests perform a trigger before and after link destruction.

State and persistence: state is module test sysfs I/O and skeleton BSS counters. BPF links are temporary; module itself is an external prerequisite.

Dependencies and integration: depends on `bpf_testmod`, `test_module_attach.skel.h`, `testing_helpers.h`, sysfs test files, and fentry/fexit/raw tracepoint support as defined by the fixture.

Risks and test signals: correct counter increments and no increments after detach are signals. Risks include missing/unloaded test module, changed sysfs interface, and target symbol renames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/module_attach.c -->
