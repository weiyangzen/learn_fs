# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_vdec0_brdg_ctrl_regs.h

Purpose: generated main register map for the VDEC0 bridge control block. It exports 111 `mmDCORE0_VDEC0_BRDG_CTRL_*` constants from `0x41E3100` to `0x41E3734`.

Important APIs/types/functions: macro-only API for clock/idle/graceful control, interrupt causes and masks, HBW/LBW AXI violation reporting and sticky clear, VCD/L2C/NRM/ABNRM GIC and MSI-X masks, decoder AXPROT/legal size controls, ARC message start/finish words, hardware event trace registers, decoder free-run/busy counters, stat counter enable, per-channel wait/MSI-X counters, software/APB write address/data, completion queue HBW addresses, MSI-X LBW address/data, AXI split BRESP error ID, LBW master interface monitoring, and captured last AW/AR transaction terms.

Control flow: none locally. Driver control flow programs bridge protection/interrupt/counter state, enables or masks channel flows, observes fault causes, and manages graceful stop or idle detection.

State and persistence behavior: maps persistent VDEC bridge hardware state for control, interrupt routing, fault latches, counters, and transaction capture. Some status fields are sticky until cleared through dedicated registers.

Dependencies and integration points: included by `gaudi2_regs.h`; fields decoded with `dcore0_vdec0_brdg_ctrl_masks.h`; channel transaction attributes come from the five VDEC bridge AXUSER headers. The block participates in video decode interrupt delivery and AXI fault handling.

Risks: broad operational surface. Fault mask mistakes can hide AXI violations, MSI-X address/data mistakes can misdeliver interrupts, and graceful/CGM controls can break reset or power sequencing.

Test signals: VDEC interrupt tests across VCD/L2C/NRM/ABNRM channels, AXI violation injection and sticky-clear tests, decoder busy/free-run counter readback, graceful stop/idle tests, and generated address verification.
