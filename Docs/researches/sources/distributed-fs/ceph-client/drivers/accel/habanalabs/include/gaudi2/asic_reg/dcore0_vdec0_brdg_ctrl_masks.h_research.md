# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_vdec0_brdg_ctrl_masks.h

Purpose: generated field shift/mask definitions for `DCORE0_VDEC0_BRDG_CTRL`. It exports 167 value masks plus associated shifts for VDEC bridge control, interrupt, AXI violation, counter, and completion/termination fields.

Important APIs/types/functions: macro-only API for CGM disable, idle mask, APB watchdog/CGM counters, graceful stop/pending, interrupt cause bits for VCD/L2C/NRM/ABNRM HBW/LBW/APB/DEC/TRC/SPI/AXI errors, HBW/LBW AXI violation causes, sticky violation clear bits, interrupt masks, GIC masks, DEC AXPROT and legal AXSIZE fields, ARC message fields, hardware event trace selection/address, free-run and busy counters, stat enable, per-channel wait/MSI-X counters, address/data fields, AXI split BRESP error, LBW master interface state, and last AW/AR transaction capture fields.

Control flow: none. External code uses masks/shifts when composing reads/writes to addresses in `dcore0_vdec0_brdg_ctrl_regs.h`.

State and persistence behavior: describes bit layout of persistent bridge control and status registers. Correct masking is required to preserve unrelated bits while acknowledging causes, clearing sticky violations, configuring counters, and masking interrupts.

Dependencies and integration points: included by `gaudi2_regs.h`; must match the main VDEC bridge register map. It complements the AXUSER channel headers for decoder and MSI-X paths.

Risks: interrupt cause and AXI violation masks are fault-reporting critical. Wrong bit masks can hide errors, clear the wrong sticky state, or report incorrect fault sources. Control fields such as graceful stop and CGM disable affect reset/power sequencing.

Test signals: interrupt cause/mask injection tests, AXI violation tests, graceful stop state tests, counter enable/readback tests, and static validation that masks do not overlap unexpectedly unless specified.
