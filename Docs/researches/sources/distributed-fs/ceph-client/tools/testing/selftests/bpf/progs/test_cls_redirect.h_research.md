<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_cls_redirect.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_cls_redirect.h

Purpose: Shared header defining GRE/GUE encapsulation structures and constants used by classifier redirect tests.

Important APIs/types/functions: Defines `gre_base_hdr`, `guehdr`, `unigue`, and related packed header layouts.

Control flow: No executable flow; it supplies exact on-wire layout for encapsulation code.

State and persistence: No persistent state.

Dependencies and integration: Included by normal and dynptr classifier implementations.

Risks: Packed layout or bitfield/endian mistakes would produce invalid packets.

Test signals: Compile-time structure size/layout and packet output comparisons are test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_cls_redirect.h -->
