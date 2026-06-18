# sources/distributed-fs/ceph-client/arch/s390/include/asm/idals.h

Purpose: This header implements Indirect Data Address List helpers used by s390 channel command words and QDIO-style I/O buffers when data crosses addressing boundaries.

Important APIs/types/functions: It defines IDA block sizes, `idal_is_needed()`, word-count helpers for 4K and 2K IDA lists, `idal_create_words()`, `set_normalized_cda()`, `clear_normalized_cda()`, `struct idal_buffer`, allocation/free helpers for single and array IDAL buffers, CDA setup, and user-copy helpers.

Control flow: Callers decide whether a CCW can address the buffer directly or needs an IDAL. Allocation paths build page-granular DMA64 address arrays, attach them to CCWs with `CCW_FLAG_IDA`, and teardown paths free allocated lists or page chunks. User-copy helpers walk each IDA block and copy chunk by chunk.

State and persistence: Persistent state includes allocated IDAL arrays, page chunks referenced by `struct idal_buffer`, and CCW `cda` plus `CCW_FLAG_IDA` state. The array allocator returns a NULL-terminated list of buffers for large transfers split at `CCW_MAX_BYTE_COUNT`.

Dependencies and integration points: It depends on s390 DMA address types, channel I/O `struct ccw1`, GFP allocation, uaccess copy helpers, and CCW maximum byte-count rules.

Risks and test signals: Leaks or double frees are easy if `clear_normalized_cda()`/array_free are not paired with setup. Boundary calculations must match channel hardware requirements. Tests should cover below/above-2GB buffers, multi-page transfers, partial user-copy faults, allocation failure unwinds, and channel I/O drivers using direct and IDA addressing.
