# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/system_local.c

## Purpose
Defines the concrete AtomISP MMIO/base-address map for all hardware blocks enumerated in `system_global.h`.

## Important APIs, Types, and Functions
Exports constant `hrt_address` arrays for ISP control/DMEM/BAMEM, SP control/DMEM, MMUs, DMA and ISYS2401 DMA, IRQ blocks, GDCs, FIFO monitor, GP device, GP timer, GPIO, timed controller, input formatters, input system, RX, IBUF controllers, ISYS IRQs, CSI RX FE/BE controllers, pixel generators, and stream2MMIO controllers.

## Control Flow
No logic; low-level accessors index these arrays by enum id to compute register addresses.

## State and Persistence Behavior
All data is read-only static address mapping.

## Dependencies and Integration Points
Includes `system_local.h`, which provides `hrt_address` and id counts. Integrates with hardware register drivers and SP/ISP control code.

## Risks
Address constants must match silicon. Enum count mismatches can cause build errors or out-of-bounds use in callers. The single `GP_TIMER_BASE` reflects interleaved timer registers, so consumers must not assume per-timer bases.

## Test Signals
Hardware bring-up should validate DEBI/MMIO access, SP/ISP DMEM/control reads, input formatter programming, and ISP2401 CSI/stream2MMIO register operations at these bases.
