<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/pe_preserve_elems.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/pe_preserve_elems.c

Purpose: verifies `BPF_F_PRESERVE_ELEMS` behavior for perf-event arrays or related map types, ensuring elements survive expected close/update paths.

Important APIs and functions: `test_one_map()` accepts a map/program pair and validates preservation semantics by updating the map, running the program, and checking element state. `test_pe_preserve_elems()` loads `test_pe_preserve_elems` and applies the helper to fixture maps.

Control flow: open/load skeleton, for each map/program scenario update elements, trigger program execution, check preserved entries, and cleanup.

State and persistence: map element contents are the tested transient state. Skeleton destruction releases maps.

Dependencies and integration: depends on `test_pe_preserve_elems.skel.h`, map flags, and BPF program execution helpers.

Risks and test signals: preserved element values after program/map operations are signals. Risks include map flag support changes and fixture map-type behavior differences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/pe_preserve_elems.c -->
