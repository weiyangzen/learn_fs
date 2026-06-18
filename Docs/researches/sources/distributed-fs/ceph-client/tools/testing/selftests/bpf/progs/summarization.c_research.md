<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/summarization.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/summarization.c

Purpose: Verifier summarization test object for packet-data mutation and sleepable-state summaries across optional tc and uprobe programs.

Important APIs/types/functions: Defines helpers `changes_pkt_data`, `does_not_change_pkt_data`, sleep helpers, and main programs in `?tc` and `?uprobe.s` sections.

Control flow: Main programs call subprograms that either mutate packet data or may sleep, allowing verifier summary propagation to be observed.

State and persistence: No persistent maps; state is verifier metadata and return values.

Dependencies and integration: Depends on optional section annotations and verifier function-summary logic.

Risks: Incorrect summaries can allow invalid packet access after mutation or reject safe programs.

Test signals: Expected signals are section-specific verifier accept/reject outcomes from selftest annotations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/summarization.c -->
