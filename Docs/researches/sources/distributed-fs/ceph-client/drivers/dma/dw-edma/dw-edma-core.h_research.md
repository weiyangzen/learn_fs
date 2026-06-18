## sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-edma-core.h

Purpose: Shared private interface for DesignWare eDMA/HDMA common core and register-version back ends.

Important APIs/types/functions: defines direction/request/status/xfer enums, `struct dw_edma_burst`, `struct dw_edma_chunk`, `struct dw_edma_desc`, `struct dw_edma_chan`, `struct dw_edma_irq`, `struct dw_edma`, `struct dw_edma_core_ops`, transfer wrapper structs, and inline dispatch helpers such as `dw_edma_core_start()`, `dw_edma_core_handle_int()`, `dw_edma_core_ch_config()`, and `dw_edma_core_ack_emulated_irq()`.

Control flow: the common core calls inline wrappers that dereference `dw->core`, allowing eDMA v0 or HDMA v0 implementations to supply register-specific behavior without conditional logic in most of the core.

State and persistence: lays out all in-memory state. Channel state (`request`, `status`, `configured`, `non_ll`) persists only while the driver is loaded. `ll_region` and MSI messages bridge in-memory descriptor state to hardware.

Dependencies and integration: includes `linux/msi.h`, `linux/dma/edma.h`, and `virt-dma`. It is consumed by all eDMA files and is the contract bus glue indirectly depends on through `dw_edma_chip`.

Risks and test signals: changes here have high blast radius because layout and ops signatures bind all eDMA variants. Test signals include successful compilation of eDMA and HDMA back ends, correct dispatch for both map formats, and no NULL optional op dereferences except where guarded.
