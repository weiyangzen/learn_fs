<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_cls_redirect_subprogs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_cls_redirect_subprogs.c

Purpose: Build wrapper that enables subprogram mode for `test_cls_redirect.c`.

Important APIs/types/functions: Defines `SUBPROGS` and includes the full classifier source.

Control flow: The included classifier marks many helpers `__noinline`, so parsing/classification/forwarding crosses BPF subprogram calls.

State and persistence: State remains the classifier `metrics_map` and packet mutations.

Dependencies and integration: Depends on the shared classifier and verifier support for subprogram packet pointer tracking.

Risks: Pointer bounds and packet data refinements must survive call boundaries.

Test signals: Tests expect same behavior as `test_cls_redirect.c` with successful subprogram verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_cls_redirect_subprogs.c -->
