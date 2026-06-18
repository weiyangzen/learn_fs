<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/strobemeta_nounroll2.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/strobemeta_nounroll2.c

Purpose: Second non-unrolled strobemeta build with larger map count to extend bounded-loop stress coverage.

Important APIs/types/functions: Sets 2 ints, 25 strings, 30 maps, 20 entries, `NO_UNROLL`, and includes `strobemeta.h`.

Control flow: Same header control flow as the first no-unroll variant, but with a larger outer map loop.

State and persistence: No unique persistence; all runtime data remains in `strobemeta_cfgs`, stack maps, sample heap, and perf events.

Dependencies and integration: Depends on common strobemeta code and verifier bounded-loop support.

Risks: Higher map count increases payload-capacity and loop-state pressure.

Test signals: Verifier load success and absence of payload-bound failures distinguish this variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/strobemeta_nounroll2.c -->
