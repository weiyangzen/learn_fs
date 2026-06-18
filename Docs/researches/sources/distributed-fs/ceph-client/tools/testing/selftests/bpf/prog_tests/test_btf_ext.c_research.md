# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_btf_ext.c

Purpose: `test_btf_ext.c` verifies that libbpf exposes BTF.ext line and function info for a loaded BPF program exactly as the kernel reports it through `bpf_prog_get_info_by_fd()`.

Important APIs/types/functions: `subtest_line_func_info()` opens and loads `test_btf_ext.skel.h`, obtains fd for `skel->progs.global_func`, queries kernel `bpf_prog_info` line info into a local `bpf_line_info` array, gets libbpf's `bpf_program__line_info()` and count, then repeats the process for `bpf_func_info` with `bpf_program__func_info()` and count. `ASSERT_MEMEQ()` compares libbpf arrays to kernel-returned arrays. `test_btf_ext()` runs the `line_func_info` subtest.

Control flow: the subtest first retrieves line-info records by setting `info.line_info`, `info.nr_line_info`, and record size before calling `bpf_prog_get_info_by_fd()`. It then reads libbpf's parsed line-info pointer/count. It resets `info`, retrieves function-info records similarly, reads libbpf's parsed function-info pointer/count, validates pointers/counts, and compares memory for both record sets. Skeleton destruction releases the program.

State and persistence: state is read-only BTF.ext metadata associated with the loaded BPF object and local stack buffers for kernel info. No persistent files are written.

Dependencies: depends on generated `test_btf_ext.skel.h`, libbpf support for retaining BTF.ext line/function info, kernel support for returning line and function info via `BPF_OBJ_GET_INFO_BY_FD`, and `btf_helpers.h`/test assertions.

Integration points: this is a metadata consistency test between libbpf's view of the BPF object and the kernel's view after load. It protects tooling that relies on libbpf line/function metadata matching kernel program info.

Risks: local arrays are fixed at 128 entries, so a future BPF object with more records would need a larger buffer or dynamic sizing. The variable names `libbbpf_*_cnt` include a typo but are local and harmless. The test assumes record ordering and bytes are identical between libbpf metadata and kernel-returned info.

Test signals: success is signaled by skeleton load, successful kernel line-info and func-info queries, non-null libbpf line/function info pointers, matching record counts, and byte-for-byte equality of all reported records.
