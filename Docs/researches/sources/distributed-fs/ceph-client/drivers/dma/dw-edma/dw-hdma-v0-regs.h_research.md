## sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-hdma-v0-regs.h

Purpose: Packed MMIO and linked-list definitions for native HDMA v0 hardware.

Important APIs/types/functions: defines channel count, enable, interrupt mask/enable bits, link-list enable, consumer cycle bits, doorbell start bit, and channel status mask. Structures include `dw_hdma_v0_ch_regs`, `dw_hdma_v0_ch`, `dw_hdma_v0_regs`, `dw_hdma_v0_lli`, and `dw_hdma_v0_llp`.

Control flow: no executable logic; consumed by the HDMA core and debugfs code for register offsets and LLI layout.

State and persistence: represents live hardware register state and hardware-fetched LL entries. Packed layout is part of the device programming ABI.

Dependencies and integration: includes DMAengine headers and is private to the HDMA v0 implementation.

Risks and test signals: incorrect offsets or bit definitions can break start, stop, abort, MSI, LL mode, or non-LL mode. Test with debugfs offset inspection, successful HDMA transfers, stop/abort interrupts, and comparison against vendor register documentation.
