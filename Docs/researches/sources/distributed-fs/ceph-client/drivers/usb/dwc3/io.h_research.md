# sources/distributed-fs/ceph-client/drivers/usb/dwc3/io.h

Purpose: provides DWC3 register read/write helpers that compensate for the driver's MMIO mapping starting at the global register window while callers use Synopsys-documented xHCI-relative offsets.

Important APIs/functions: `dwc3_readl(struct dwc3 *dwc, u32 offset)` and `dwc3_writel(struct dwc3 *dwc, u32 offset, u32 value)`.

Control flow: both helpers derive `base` from `dwc->regs`, access `base + offset - DWC3_GLOBALS_REGS_START`, then emit tracepoints using a documentation-style base address (`base - DWC3_GLOBALS_REGS_START`) and the original offset.

State and persistence: no independent state. Reads and writes directly affect memory-mapped DWC3 hardware registers and trace output.

Dependencies and integration: includes Linux IO primitives, trace support, debug helpers, and core register constants. Nearly every DWC3 core, gadget, host-adjacent, and PHY helper depends on these accessors for consistent offset handling and traceability.

Risks: callers must pass offsets in the expected DWC3 register namespace; passing already-adjusted offsets would access the wrong register. Tracepoints expose all register access and can be high volume. No barriers beyond `readl`/`writel` semantics are added here, so call sites still need explicit ordering around DMA-visible structures.

Test signals: successful register access during probe, trace events with expected addresses, and absence of faults from invalid MMIO offsets. Low-level failures usually manifest as probe timeouts, command timeouts, or incorrect hardware capability reads.
