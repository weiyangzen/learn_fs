<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/strobemeta_bpf_loop.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/strobemeta_bpf_loop.c

Purpose: Builds the Strobelight metadata program with `USE_BPF_LOOP`, 2 ints, 25 strings, 100 maps, and 20 map entries to exercise helper-driven bounded iteration.

Important APIs/types/functions: Provides only preprocessor constants and includes `strobemeta.h`; the exported BPF maps/programs come from the header, especially `read_var_callback` and `on_event`.

Control flow: The included header routes int, string, and map scans through three `bpf_loop` calls with a shared callback context and payload offset.

State and persistence: State is the common strobemeta maps; this wrapper changes only compile-time loop strategy and capacities.

Dependencies and integration: Depends on kernels/verifier support for `bpf_loop` and the common strobemeta header.

Risks: Large map-slot count stresses callback precision, `payload_off` tracking, and `bpf_loop` return-count validation.

Test signals: Expected signal is successful load and metadata extraction with high map capacity; verifier failures around imprecise scalar offsets are regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/strobemeta_bpf_loop.c -->
