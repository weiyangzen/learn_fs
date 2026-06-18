# sources/distributed-fs/ceph-client/drivers/staging/media/deprecated/atmel/atmel-isc-regs.h

## Purpose
This header defines the ISC/XISC register map, bit fields, masks, and SoC-specific register offsets used by the deprecated Atmel media drivers. It is the low-level hardware programming contract for control, front-end cropping, clocking, interrupts, image pipeline modules, histogram, DMA, and version registers.

## Important Constants
The file defines control registers `ISC_CTRLEN`, `ISC_CTRLDIS`, and `ISC_CTRLSR` with capture/profile/histogram bits; PFE config registers and polarity/CCIR/MIPI/BPS fields; clock enable/disable/status/config registers; interrupt enable/disable/mask/status and `ISC_INT_DDONE`/`ISC_INT_HISDONE`; DPC, WB, CFA, CC, GAM, VHXS, CSC, CBC, SUB422, SUB420, RLP, HIS, DMA, VERSION, and histogram entry registers.

SoC offset constants distinguish SAMA5D2 and SAMA7G5 layouts for CSC, CBC, subsampling, RLP, histogram, DMA, version, and histogram entries. RLP and DMA constants encode packing modes, YUV byte orders, planar/packed DMA modes, burst sizes, and DMA view modes.

## Control Flow and State
This header has no executable control flow. It structures all register writes and regmap field allocations done in `atmel-isc-base.c`, `atmel-isc-clk.c`, and the SoC-specific files. State exists in hardware registers addressed by these constants.

## Dependencies and Integration Points
It depends on Linux bit operations and is included by every Atmel ISC source file in this subset. SoC drivers combine these constants with per-device offsets stored in `struct isc_reg_offsets`.

## Risks and Test Signals
Risks include incorrect masks/shifts causing register corruption, SoC offset mismatches, typo-prone BPS constants, and assumptions that SAMA5D2 and SAMA7G5 register layouts differ only by provided offsets. Test signals are successful capture across formats, clock configuration, interrupt delivery, histogram reads, register trace inspection, and comparing register writes against SoC datasheets.
