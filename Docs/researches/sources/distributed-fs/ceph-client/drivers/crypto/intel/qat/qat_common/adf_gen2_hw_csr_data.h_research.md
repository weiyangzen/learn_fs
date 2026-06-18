## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen2_hw_csr_data.h

Purpose: Defines the Gen2 ring CSR address map and macro-level register accessors used by Gen2 CSR ops.

Important APIs/types: Provides constants for ring config, base, head, tail, empty status, interrupt flag/source/coalescing registers, bundle size, arbiter slot spacing, and `WRITE_CSR_RING_SRV_ARB_EN()`. `BUILD_RING_BASE_ADDR()` converts DMA address plus ring-size encoding into hardware base format. Declares `adf_gen2_init_hw_csr_ops()`.

Control flow/state: Header macros directly read/write MMIO through `ADF_CSR_RD/WR`; no state is stored. The `WRITE_CSR_RING_BASE` macro splits lower and upper 32-bit base registers.

Dependencies/integration: Consumed by the Gen2 CSR ops implementation and generic ring/transport code through initialized ops.

Risks and test signals: Risks are incorrect bundle stride, split-base programming, and interrupt source mask values. Hardware smoke tests should validate ring producer/consumer movement, coalesced interrupts, empty-status reporting, and service arbitration under load.
