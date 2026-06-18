# sources/distributed-fs/ceph-client/include/dt-bindings/clock/sophgo,sg2042-clkgen.h

## Purpose
`sophgo,sg2042-clkgen.h` defines IDs for the Sophgo SG2042 clock generator block.

## Important APIs, types, and functions
The exported namespace is organized by function: `DIV_*` divider IDs, `GATE_*` gate IDs, and `MUX_*` mux IDs. Divider clocks cover MPLL/FPLL-derived CPU, DDR, A53, UART, LPC, EFUSE, Ethernet TX/PTP, GMAC, SD, TPU, PCIe, video, and timer-related paths. Gates cover the corresponding derived clocks and DDR/RP/AXI outputs. Mux IDs select DDR01, DDR23, RP CPU normal, and AXI DDR sources.

## Control flow
Device-tree clock cells reference these IDs under the SG2042 clkgen provider. Runtime control is in the Sophgo clock driver, which interprets whether an ID names a divider, gate, or mux.

## State and persistence
The header has no state. Clock generator registers hold selected parents, divisors, and gate state. IDs are stable ABI for DTBs.

## Dependencies and integration points
It integrates with SG2042 DTS, Sophgo clkgen driver data, CPU/DDR interconnect clocks, Ethernet, UART, SD, PCIe, TPU, video, timer, EFUSE, and LPC-style peripheral consumers.

## Risks and test signals
Risks include confusing divider/gate/mux IDs for the same signal, breaking DDR or CPU parent selection, and renumbering a dense ABI. Test signals include clock provider registration, DDR stability, CPU/interconnect rate checks, Ethernet/PTP behavior, PCIe/SD/UART operation, and debugfs verification that mux/divider/gate chains align.
