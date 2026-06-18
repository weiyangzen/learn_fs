# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-agl-defs.h

## Purpose
This generated-style header describes the Octeon AGL/GMX register block used by the single/low-speed Ethernet MAC path. It gives callers CSR addresses and endian-aware bitfield unions for port configuration, receive filtering, frame checks, flow control, statistics, transmit controls, interrupt reporting, and the top-level AGL port control register.

## Important APIs, Types, and Functions
The public surface is macro and union based. `CVMX_AGL_GMX_*` macros build `CVMX_ADD_IO_SEG()` CSR addresses, commonly indexed by `offset & 1` for the two AGL ports. Important register groups include global diagnostics (`BAD_REG`, `BIST`, `DRV_CTL`, `INF_MODE`), per-port mode/config (`PRTX_CFG`, `PRTX_CTL`), receive address CAM registers (`RXX_ADR_CAM0..5`, `RXX_ADR_CAM_EN`, `RXX_ADR_CTL`), receive admission and frame validation (`RXX_DECISION`, `RXX_FRM_CHK`, `RXX_FRM_CTL`, min/max/jabber/IFG/UDD skip), receive and transmit interrupts (`RXX_INT_EN`, `RXX_INT_REG`, `TX_INT_EN`, `TX_INT_REG`), receive backpressure and status (`RX_BP_*`, `RX_PRT_INFO`, `RX_TX_STATUS`), transmit timing/append/threshold/pause/statistics (`TXX_*`, `TX_*`), and source MAC/programmed pause packet registers.

## Control Flow
There is no executable control flow in this file. Driver code selects a CSR macro, reads or writes the corresponding 64-bit register, edits the matching union's `.u64` or `.s` fields, and writes it back. Hardware then controls receive filtering, frame admission, error latching, flow control, and statistic counters.

## State and Persistence Behavior
All state lives in the AGL/GMX hardware CSRs. Configuration writes persist until reset or later driver reconfiguration. Interrupt/status registers are hardware-latched, often cleared by writing status bits. Statistic CSRs accumulate packet/octet/error counters and can be affected by the stats-control fields.

## Dependencies and Integration Points
The header depends on Octeon CSR address helpers and the kernel's endian bitfield convention. It integrates with Octeon Ethernet drivers that program AGL ports, with link/PHY setup through interface mode and in-band status fields, with interrupt handlers through RX/TX interrupt enable/status unions, and with ethtool or diagnostics through statistics CSRs.

## Risks
The field layouts are hardware ABI: using the wrong port offset, wrong chip-generation interpretation, or wrong endian view can silently corrupt MAC configuration. Interrupt enable/status unions contain many specific error bits, so handlers must clear only acknowledged conditions. Statistics and flow-control fields can change link behavior immediately; misprogramming pause, backpressure, or frame-check fields can cause packet loss, bad filtering, or link stalls.

## Test Signals
Build-test Octeon Ethernet configurations that include AGL support. Runtime signals include successful link bring-up on AGL ports, correct programmed MAC filtering, expected RX/TX interrupt causes, sane ethtool counters, pause/backpressure behavior under FPA pressure, and no unexpected `BAD_REG`/BIST/error bits after initialization.
