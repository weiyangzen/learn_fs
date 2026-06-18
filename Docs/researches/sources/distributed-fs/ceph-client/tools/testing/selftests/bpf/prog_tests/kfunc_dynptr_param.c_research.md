
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/kfunc_dynptr_param.c

## Purpose

`kfunc_dynptr_param.c` validates kfuncs that accept dynptr parameters, especially PKCS#7 signature verification behavior with NULL dynptr data.

## Important APIs, Types, and Functions

The test uses `test_kfunc_dynptr_param.skel.h`, a libbpf print callback to detect missing `bpf_verify_pkcs7_signature` kfunc, `bpf_program__attach()`, `bpf_prog_get_next_id()` as a trigger, and `RUN_TESTS` for paired verifier cases.

## Control Flow and Data Flow

`has_pkcs7_kfunc_support()` opens/loads once with a temporary print callback and skips if the extern kfunc is missing. Each runtime subtest loads the skeleton, sets current PID, attaches the selected program, calls `bpf_prog_get_next_id()` to trigger, destroys the link, and checks `skel->bss->err` against the expected runtime error.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is BSS `pid` and `err`, plus transient link state. Dependencies include kernel/module BTF exposing PKCS#7 kfuncs, dynptr support, and libbpf extern resolution. Integration is kfunc dynptr parameter validation and runtime error reporting. Risks are feature skips on kernels without the kfunc and log-format matching in the print callback. Test signals are skip when unsupported, expected `-EBADMSG` for `dynptr_data_null`, and passing verifier cases from `RUN_TESTS`.
