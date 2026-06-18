<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_ptr.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_ptr.c

Purpose: validates BPF-side access to map metadata/pointers using a light skeleton fixture.

Important APIs and functions: `test_map_ptr()` opens `map_ptr_kern.lskel.h`, sets ringbuf `max_entries` to page size before load, loads, stores `page_size` in BSS, and runs `cg_skb` with `bpf_prog_test_run_opts()`.

Control flow: open, configure map, load, set BSS, run program on `pkt_v4`, expect successful syscall and nonzero retval, destroy.

State and persistence: state is a ring buffer map and BSS page-size value inside the skeleton. It is destroyed at cleanup.

Dependencies and integration: depends on light skeleton support, `map_ptr_kern.lskel.h`, packet fixtures, and ringbuf map creation.

Risks and test signals: nonzero program retval after successful test-run means the BPF program observed expected map properties. Risks are page-size assumptions and light-skeleton API changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/map_ptr.c -->
