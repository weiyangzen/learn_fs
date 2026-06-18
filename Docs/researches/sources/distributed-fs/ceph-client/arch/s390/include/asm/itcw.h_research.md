# sources/distributed-fs/ceph-client/arch/s390/include/asm/itcw.h

Purpose: This header declares helpers for incrementally constructing FCX transport command words and associated DCW/TIDAW data.

Important APIs/types/functions: `ITCW_OP_READ`, `ITCW_OP_WRITE`, opaque `struct itcw`, `itcw_get_tcw()`, `itcw_calc_size()`, `itcw_init()`, `itcw_add_dcw()`, `itcw_add_tidaw()`, `itcw_set_data()`, and `itcw_finalize()` are the public API.

Control flow: A caller calculates buffer size, initializes an ITCW builder for read or write, adds device command words and transport indirect data address words, optionally assigns data, then finalizes the TCW before issuing channel I/O.

State and persistence: State is the caller-provided ITCW buffer containing a TCW and appended DCW/TIDAW structures. The header itself owns no memory.

Dependencies and integration points: It depends on `asm/fcx.h` layouts and integrates with channel subsystem drivers using FCX and TCW-based I/O.

Risks and test signals: Builder bounds and finalization order must match hardware layout. Tests should cover calculated sizes, maximum TIDAW counts, read/write operations, malformed command rejection, and real FCX-capable device I/O.
