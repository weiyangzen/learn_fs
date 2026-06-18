# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/xilinx/xlnx-zynqmp-clk.h

## Purpose
This binding header defines clock IDs for the Xilinx ZynqMP firmware clock interface.

## APIs, Types, And Constants
It exports numeric IDs from `IOPLL` 0 through `LPD_WDT` 112. The constants cover PLLs, PLL routing and mux nodes, CPU clocks, debug clocks, display/audio clocks, DMA, DDR, SATA, PCIe, GPU, USB, R5, CSU, GEM TX/RX/reference clocks, QSPI, SDIO, UART, SPI, NAND, I2C, CAN, PL fabric clocks, watchdog, and miscellaneous firmware-managed clocks.

## Control Flow And State
There is no executable flow. DTS clock specifiers use these IDs, and firmware-backed clock drivers map them to runtime operations. The IDs persist in DTBs as ABI data.

## Dependencies And Integration
The header has no includes. It integrates with ZynqMP DTS files and the ZynqMP firmware clock provider.

## Risks And Test Signals
The major risk is ABI breakage if IDs diverge from firmware definitions or driver tables. Tests are DTB compilation, clock provider probe, and peripheral probe success for consumers using these clock IDs.
