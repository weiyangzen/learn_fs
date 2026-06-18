## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_gen4_hw_csr_data.h

Purpose: Defines the Gen4 ring CSR layout and low-level register access macros.

Important APIs/types: Provides offsets for ring config/base/head/tail, multiple status registers, interrupt enable/flag/source/coalescing, exception status/interrupt enable, ring service arbiter, address offset, and bundle size. `BUILD_RING_BASE_ADDR()` preserves hardware-required alignment. `read_base()` handles non-contiguous LBASE/UBASE reads. Declares `adf_gen4_init_hw_csr_ops()`.

Control flow/state: Macros operate directly on MMIO addresses and do not store state. The base read/write helpers split or combine 64-bit DMA addresses.

Dependencies/integration: Consumed by `adf_gen4_hw_csr_data.c`, transport ring setup, bank reset/drain paths, and debug/status flows through `adf_hw_csr_ops`.

Risks and test signals: Risks include wrong address offset, incorrect 64-bit base handling, and interrupt/coalescing mask drift. Hardware tests should check ring traffic, interrupt source selection, base readback, and exception status paths.
