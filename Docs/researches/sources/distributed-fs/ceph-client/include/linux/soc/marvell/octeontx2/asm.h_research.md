# sources/distributed-fs/ceph-client/include/linux/soc/marvell/octeontx2/asm.h

Purpose: This Marvell OcteonTX2 header provides architecture-level assembly helper definitions for SoC-specific low-level code.

Important APIs/types/functions: On ARM64 it defines `otx2_lmt_flush(ioaddr)` using `ldeor`, `cn10k_lmt_flush(val, addr)` using `steorl`, and `otx2_atomic64_fetch_add(incr, ptr)` using `ldadda`. Non-ARM64 builds provide compile-safe fallbacks.

Control flow: Packet/CPT enqueue paths perform LMT stores, then call the flush macro to force the hardware-visible operation with the required release/atomic semantics. Atomic add returns the previous 64-bit value.

State and persistence: State is in memory and coprocessor-facing LMTST side effects. The helpers impose ordering but do not store software state.

Dependencies and integration: Depends on ARM64 LSE instruction availability when compiled for ARM64. Integrates with OcteonTX2/CN10K NIX packet send and CPT instruction enqueue paths.

Risks and test signals: Ordering bugs here can drop descriptors or enqueue stale data. Test ARM64 and non-ARM64 builds, NIX/CPT enqueue stress, memory-ordering validation, and toolchain support for the embedded `.cpu generic+lse` assembly.
