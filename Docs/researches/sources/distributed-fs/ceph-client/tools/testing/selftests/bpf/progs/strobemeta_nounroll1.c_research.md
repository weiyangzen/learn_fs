<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/strobemeta_nounroll1.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/strobemeta_nounroll1.c

Purpose: Builds strobemeta with non-unrolled loops and moderate map count to test verifier handling without forced loop unrolling.

Important APIs/types/functions: Defines `STROBE_MAX_INTS=2`, `STROBE_MAX_STRS=25`, `STROBE_MAX_MAPS=13`, `STROBE_MAX_MAP_ENTRIES=20`, `NO_UNROLL`, then includes `strobemeta.h`.

Control flow: The included `read_strobe_meta` uses pragma no-unroll loops for ints, strings, maps, and per-map entries.

State and persistence: Uses the common strobemeta BPF maps and perf output; no local state beyond compile-time bounds.

Dependencies and integration: Depends on bounded-loop verifier support and the shared header.

Risks: Verifier loop bound inference and payload bounds must survive without unrolling.

Test signals: Load success and correct sample metadata for the 13-map configuration are the primary test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/strobemeta_nounroll1.c -->
