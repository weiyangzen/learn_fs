
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/kfunc_call.c

## Purpose

`kfunc_call.c` validates kernel function call support from BPF across tc and syscall program types, including success cases, verifier failure cases, runtime failure cases, light skeletons, subprograms, and destructive kfunc capability gating.

## Important APIs, Types, and Functions

It uses `kfunc_call_fail.skel.h`, `kfunc_call_test.skel.h`, `kfunc_call_test.lskel.h`, subprog skeletons, destructive skeletons, `cap_helpers.h`, `bpf_prog_test_run_opts()`, verifier log buffers through `bpf_object_open_opts`, and tables of `kfunc_test_params`.

## Control Flow and Data Flow

For each table case, success paths load normal and light skeletons, select the named program, run with tc packet data or syscall context, and compare retval. Failure paths enable one failing program, capture verifier logs, either expect load failure or runtime `bpf_prog_test_run_opts()` error, and assert the expected diagnostic substring. Additional subtests exercise subprogram variants and destructive kfunc loading under capability constraints.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is verifier log text, program retvals, and skeleton BSS where applicable. Dependencies include kernel BTF kfunc definitions, syscall and tc test-run support, capabilities for destructive calls, and light skeleton ABI. Integration is verifier kfunc type checking, memory acquisition/release rules, nullable context handling, and runtime syscall kfunc behavior. Risks are verifier log wording drift, missing kfuncs on older kernels, and capability-dependent skips/failures. Test signals are exact retvals for success cases, expected `-EINVAL` runtime failures, verifier load rejection for bad memory/type cases, and log substrings matching the table.
