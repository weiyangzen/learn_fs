<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/summarization_freplace.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/summarization_freplace.c

Purpose: Freplace companion to `summarization.c`, replacing summarized functions to test update of verifier summaries through freplace attachments.

Important APIs/types/functions: Defines replacement functions for packet mutation and sleep behavior in `?freplace` sections.

Control flow: Each replacement body provides a simple mutation/sleeping or non-mutating/non-sleeping behavior for the target program.

State and persistence: No BPF maps or persistent runtime state.

Dependencies and integration: Depends on freplace attachment and verifier summary recomputation.

Risks: Wrong target summary can make freplace load outcomes unsound.

Test signals: Tests attach replacements and check expected verifier compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/summarization_freplace.c -->
