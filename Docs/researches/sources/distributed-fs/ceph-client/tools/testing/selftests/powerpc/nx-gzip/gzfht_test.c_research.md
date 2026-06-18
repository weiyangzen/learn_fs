<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/gzfht_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/gzfht_test.c

Purpose: Sample NX gzip compressor using fixed Huffman blocks. It compresses a file to `<name>.nx.gz` through the NX accelerator and emits a simple gzip wrapper.

Important APIs and types: Important routines are `compress_fht_sample`, `gzip_header_blank`, `append_sync_flush`, `set_bfinal`, `compress_file`, and `main`. Uses CPB/CRB/DDE macros and `nxu_submit_job`.

Control flow: `compress_file()` reads the full input, chooses chunk size from NX sysfs capability or a fallback, writes a gzip header, submits fixed-Huffman compression jobs chunk by chunk, handles page-fault condition code retries, inserts sync flush blocks between chunks, carries CRC state, appends trailer CRC/ISIZE, and writes the output file.

State and persistence: State includes allocated input/output buffers, CRB/CPB command block, CRC, source/target totals, chunk size, and fault retry counter. It creates `<input>.nx.gz`.

Dependencies and integration points: Depends on `utils.h` for file/sysfs helpers, `nxu.h`/`nx.h`, `gzip_vas.c`, and NX gzip VAS device support.

Risks: Output buffer sizing and fixed-Huffman-only behavior make it a sample rather than full gzip implementation. Hardware condition codes and sysfs caps are platform-specific.

Test signals: Pass means the accelerator can compress random files and the paired `gunz_test` can decompress and validate them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/gzfht_test.c -->
