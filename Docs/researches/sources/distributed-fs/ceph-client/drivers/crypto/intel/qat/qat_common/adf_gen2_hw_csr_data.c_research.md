## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen2_hw_csr_data.c

Purpose: Provides Gen2 implementations of the generic `adf_hw_csr_ops` ring CSR access table.

Important APIs/functions: `adf_gen2_init_hw_csr_ops()` assigns function pointers for ring base-address construction, ring head/tail reads and writes, empty status reads, ring config/base writes, interrupt flag/source/coalescing control, and ring service arbiter enable writes. The individual static functions are thin wrappers around macros in `adf_gen2_hw_csr_data.h`.

Control flow and state: No persistent state is owned. The function pointer table is populated during hardware-data initialization and later used by transport/ring code against mapped ETR CSR bases.

Dependencies/integration: Depends on `adf_hw_csr_ops`, QAT CSR read/write helpers, and the Gen2 CSR layout macros. It integrates with generic transport code through the ops table instead of exposing Gen2 offsets directly.

Risks and test signals: The wrappers are simple but sensitive to offset math and address packing. Test signals include ring setup success, correct DMA base programming for 64-bit addresses, interrupt coalescing behavior, and no regressions in service arbiter programming.
