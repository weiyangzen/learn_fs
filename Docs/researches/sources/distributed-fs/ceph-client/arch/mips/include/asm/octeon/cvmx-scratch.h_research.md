# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-scratch.h

Purpose: provides typed volatile accessors for OCTEON processor-local scratchpad memory.

Important APIs/types/functions: `CVMX_SCRATCH_BASE` is the negative address base for local scratch memory. Read helpers are `cvmx_scratch_read8`, `cvmx_scratch_read16`, `cvmx_scratch_read32`, and `cvmx_scratch_read64`. Write helpers are `cvmx_scratch_write8`, `cvmx_scratch_write16`, `cvmx_scratch_write32`, and `cvmx_scratch_write64`.

Control flow: each inline helper computes `CVMX_SCRATCH_BASE + address`, casts it to the corresponding volatile integer pointer with `CASTPTR`, and performs one load or store. There is no bounds checking, locking, or synchronization in the helpers.

State and persistence: scratchpad contents are per-processor, volatile runtime state. They are used for low-latency temporary storage and IOBDMA response slots; they do not persist across reset or core context assumptions.

Dependencies and integration points: depends on `CASTPTR` from `cvmx.h`. `cvmx-pow.h` uses scratch reads for asynchronous POW work responses, and other CVMX code can use scratch offsets for IOBDMA and per-core temporary values.

Risks: callers must supply valid byte offsets and natural alignment for the access width. Comments for `cvmx_scratch_write16` and `cvmx_scratch_write32` describe the wrong width, which can mislead maintainers even though the implementations are correctly typed. Scratch storage is local to a processor, so sharing assumptions across cores are invalid.

Test signals: tests are primarily compile-time and hardware/runtime checks. Useful signals include successful async IOBDMA/POW responses in scratch, no alignment exceptions, and no cross-core data-sharing assumptions in call sites.
