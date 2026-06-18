
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/kfunc_module_order.c

## Purpose

`kfunc_module_order.c` verifies kfunc resolution when two test modules exporting relevant kfuncs are loaded in a specific order.

## Important APIs, Types, and Functions

It uses `kfunc_module_order.skel.h`, `testing_helpers.h` module load/unload helpers, and `bpf_prog_test_run_opts()` on `call_kfunc_xy` and `call_kfunc_yx`.

## Control Flow and Data Flow

The test loads `bpf_test_modorder_x.ko`, then `bpf_test_modorder_y.ko`, opens/loads the skeleton, runs both BPF programs with dummy packet data, requires zero syscall error and zero retval, destroys the skeleton, then unloads modules in reverse order.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is loaded kernel modules and transient BPF programs. Dependencies include available module files, module load permissions, kernel BTF for module kfuncs, and test-run support. Integration is module kfunc lookup ordering and ambiguity handling. Risks are cleanup if module Y load or skeleton load fails, missing modules, and permission restrictions. Test signals are successful module loads, skeleton load, and zero retvals for both call orders.
