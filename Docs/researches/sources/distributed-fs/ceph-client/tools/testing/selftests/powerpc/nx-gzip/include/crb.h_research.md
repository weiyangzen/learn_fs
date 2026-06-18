<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/include/crb.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/include/crb.h

Purpose: Defines generic NX coprocessor request/status/descriptor block layouts and constants. It is a lower-level hardware-format header used by the gzip sample code.

Important APIs and types: Declares `struct coprocessor_completion_block`, `struct coprocessor_status_block`, `struct data_descriptor_entry`, and `struct coprocessor_request_block`; defines CCB/CSB/DDE/CRB sizes, alignments, masks, completion codes, and field access macros.

Control flow: No executable flow. Callers populate DDEs and CRBs, submit to NX, then decode CSB completion codes and processed-byte counts using these definitions.

State and persistence: No software persistence. Structures are shared memory contracts with the accelerator and kernel driver.

Dependencies and integration points: Included by `gunz_test.c` and related NX code; depends on endian helpers and `nx.h`.

Risks: The structs are hardware ABI. Padding, endianness, alignment, and bit masks are all correctness-critical.

Test signals: Successful NX jobs and sensible CSB condition codes validate the header definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/nx-gzip/include/crb.h -->
