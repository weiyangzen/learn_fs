# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bad_struct_ops.c

Purpose: negative tests for struct_ops program loading and log diagnostics.

Important APIs/types/functions: uses `bad_struct_ops.skel.h`, `bad_struct_ops2.skel.h`, `start_libbpf_log_capture`, and `stop_libbpf_log_capture`. `invalid_prog_reuse` checks invalid reuse of a struct_ops program pointer; `unused_program` checks that an unreferenced struct_ops program still autoloads and fails load.

Control flow: each subtest opens a skeleton, starts libbpf log capture, attempts load expecting error, stops capture, and asserts a diagnostic substring is present. The unused-program test also asserts `foo` has autoload enabled before loading.

State and persistence behavior: only temporary skeletons and captured log buffers are allocated. Logs are freed and skeletons destroyed after each subtest.

Dependencies and integration points: libbpf logging capture helpers, generated skeletons, and a kernel/testmod environment that validates struct_ops.

Risks: substring assertions are sensitive to libbpf/kernel diagnostic wording. Missing log capture leaves limited context. These are intentionally negative load tests.

Test signals: failed skeleton load plus expected log substrings for invalid program reuse and failed unreferenced program load.
