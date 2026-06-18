## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/edac.h

Purpose: provides the PowerPC EDAC atomic memory scrub primitive.

Important APIs/types/functions: `edac_atomic_scrub(void *va, u32 size)` iterates over 32-bit words and performs a load-reserve/store-conditional writeback of the same value followed by `isync`.

Control flow: for each word in the requested range, the helper loops on `lwarx/stwcx.` until the conditional store succeeds. This forces a read/write cycle without changing data.

State and persistence: mutates memory by writing the original value back, allowing ECC hardware to detect and correct errors. No separate kernel state is held.

Dependencies and integration: used by generic EDAC software scrubbing. Relies on PowerPC reservation semantics and memory clobbers for interrupt/DMA/SMP safety.

Risks and test signals: only full 32-bit words are scrubbed; callers must pass appropriate size/alignment. Reservation loops on faulty memory can be costly. Test signals include EDAC scrub tests, injected ECC correctable errors, SMP/DMA concurrent access, and alignment boundary cases.
