# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fdi_regs.h

Purpose: defines MMIO registers and bitfields for FDI PLL, TX control, RX control, RX misc, TU size, and RX interrupt status/mask registers.

Important APIs/types/functions: includes `FDI_PLL_BIOS_*`, `FDI_PLL_FREQ_CTL`, `FDI_TX_CTL()`, `FDI_RX_CTL()`, `FDI_RX_MISC()`, `FDI_RX_TUSIZE1/2()`, `FDI_RX_IIR()`, `FDI_RX_IMR()`, and bitfields for enable, link-training patterns, voltage/pre-emphasis presets, port width, PLL enable, enhanced framing, composite sync, auto training, PCDCLK, BPC, lane powerdown, delay, and lock/error interrupts.

Control flow: no executable code. `intel_fdi.c` uses these definitions to compute PLL frequency, train links, poll bit/symbol lock, control RX/TX/PLL state, and report errors.

State and persistence: the header has no software state; it maps hardware register state retained by the display engine/PCH.

Dependencies and integration: depends on `intel_display_reg_defs.h`. The bit encodings are coupled to platform branches for ILK, SNB, IVB, CPT/PCH, and Haswell FDI-over-DDI paths.

Risks: FDI bit definitions include generation-specific encodings, especially IVB training bits and CPT RX patterns. Mixing them can train the wrong pattern or leave PLLs enabled. Register offsets are pipe-indexed and must match fixed pipe/PCH transcoder mappings.

Test signals: MMIO trace FDI training on supported hardware, verify lock bits and error bits are interpreted correctly, and compile state checker/enable paths for ILK/SNB/IVB/HSW.
