## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_hw_csr_data.c

Purpose: Provides Gen4 implementations of generic ring CSR operations, including expanded status and interrupt controls not present in Gen2.

Important APIs/functions: `adf_gen4_init_hw_csr_ops()` populates function pointers for base address encoding, head/tail access, status reads (`stat`, `uo`, `e`, `ne`, `nf`, `f`, `c`, exception), exception interrupt enable access, ring config/base read/write, interrupt enable/flag/source/coalescing access, service arbiter enable, and `get_int_col_ctl_enable_mask()`.

Control flow and state: No state is stored here. The generic transport code calls through `adf_hw_csr_ops` with an ETR CSR base; this file's wrappers delegate to Gen4 offset macros.

Dependencies/integration: Depends on `adf_gen4_hw_csr_data.h`, the generic CSR ops type, and MMIO access macros. It is installed during Gen4 hardware initialization.

Risks and test signals: The larger Gen4 ring window includes `ADF_RING_CSR_ADDR_OFFSET` and 0x2000 bundle stride, so any mismatch breaks all ring operations. Tests should validate ring base readback, exception interrupt enable programming, interrupt coalescing, and service arbiter behavior for multiple banks.
