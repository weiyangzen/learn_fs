<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/gunz_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/gunz_test.c

Purpose: Sample NX hardware gzip decompressor. It parses gzip headers, streams compressed data through NX, resumes partial deflate states, and verifies trailer CRC/ISIZE.

Important APIs and types: Key helpers are FIFO macros, `nx_append_dde`, `nx_touch_pages_dde`, `nx_submit_job`, `decompress_file`, and `main`. Uses `struct nx_gzip_crb_cpb_t`, DDE lists, CPB/CSB field macros, and `nx_function_begin/end`.

Control flow: `decompress_file()` opens stdin/file input, parses gzip metadata, allocates ring buffers, alternates read/write/decompress states, builds source/target DDEs including history for resume, submits jobs, handles NX condition codes (`ERR_NX_AT_FAULT`, `ERR_NX_DATA_LENGTH`, `ERR_NX_TARGET_SPACE`, `ERR_NX_OK`), updates FIFO offsets, and verifies the gzip trailer.

State and persistence: State includes input/output FIFOs, history length, compression-ratio heuristic, CPB/CRB status, page-fault retry counts, and output file handles. It writes `<input>.nx.gunzip` for file input.

Dependencies and integration points: Depends on `nxu.h`, `nx.h`, `crb.h`, `gzip_vas.c`, POSIX files, aligned allocation, signals, and the NX gzip VAS device.

Risks: This is demonstration code, not production decompression. The state machine is complex, condition-code handling is hardware-specific, and page-fault retries assume userspace can fault pages in before NX access.

Test signals: Pass through `nx-gzip-test.sh` means hardware decompression completed and checksum/size matched for generated compressed streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/gunz_test.c -->
