# sources/distributed-fs/ceph-client/include/dt-bindings/clock/tenstorrent,atlantis-prcm-rcpu.h

## Purpose
Defines clock and reset IDs for the Tenstorrent Atlantis PRCM RCPU block. It supplies DT-facing identifiers for root/divided RCPU clocks, peripheral clocks, interconnect clocks, and reset lines.

## Important APIs, Types, and Constants
The file exports `CLK_*` IDs, including `CLK_RCPU_PLL`, `CLK_RCPU_ROOT`, divided RCPU clocks, RTC, DMA, AXI/APB fabric, UART, SPI, GPIO, CAN, and I2S clocks. It also exports `RST_*` reset IDs ending with `RST_I2S1` 31. There are no structs or helper macros.

## Control Flow and State
No executable control flow. Runtime state belongs to the PRCM clock/reset provider and reset controller; DT consumers only pass these integer IDs.

## Dependencies and Integration Points
Self-contained and guarded by `_DT_BINDINGS_ATLANTIS_PRCM_RCPU_H`. It integrates with clock-controller and reset-controller nodes for Atlantis RCPU peripherals and bus fabric.

## Risks and Test Signals
Clock and reset namespaces are both present, so consumers must use the right property and provider. Renumbering can bind devices to wrong resets or clocks. Test signals include DTS build, schema checks for PRCM nodes, and boot/probe coverage for UART, SPI, GPIO, CAN, I2S, and DMA.
