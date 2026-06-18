# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/fpga_defs.h

## Purpose
`fpga_defs.h` defines register offsets and bitfields for FPGA-based Chelsio cxgb hardware paths, including FPGA-level interrupt routing, TP/MC3/GMAC interrupt registers, MI0 MDIO access, and a compact GMAC register map. It is a hardware definition header, not executable code.

## Important APIs, Types, and Functions
The file exports no functions or structures. Important constants include FPGA PCIX version/status addresses and master interrupt bits for SGE, TP, MC3, GMAC, and PCIX; TP interrupt cause/enable addresses; MC3 and GMAC interrupt address groups; MI0 clock/CSR/address/data registers and bitfield helpers; GMAC station address, control, inter-frame spacing, jumbo length, link delay, pause, multicast filter, random backoff, and TX FIFO threshold registers. `MAC_REG_ADDR(idx, reg)` and derived `MAC_REG_*` macros compute per-port GMAC register offsets.

## Control Flow
There is no direct control flow. Runtime code uses these constants to configure FPGA variants, access MI0 MDIO state, manipulate GMAC control bits, and service FPGA interrupt causes. The macros follow the same shift/mask/value/getter convention as `regs.h`, so callers assemble register values with `V_*` and test fields with `G_*`/`F_*`.

## State and Persistence
All state represented by this file is hardware state in FPGA registers: interrupt masks/causes, MI0 operation status, GMAC enable/loopback/speed/pause/promiscuous/multicast/jumbo settings, and per-port MAC address/filter registers. The header owns no driver memory and persists nothing outside the device.

## Dependencies and Integration Points
This header is a legacy FPGA companion to the ASIC register map in `regs.h`. It integrates with lower-level board initialization, MDIO, and GMAC code that must support FPGA hardware revisions. The constants overlap conceptually with `gmac.h` operation callbacks but sit at the register-access layer.

## Risks
Risk is primarily register-map drift or mixing FPGA and ASIC paths. Applying these offsets to an ASIC BAR or using ASIC constants against an FPGA target could corrupt unrelated registers. The generic macro names for GMAC control bits also require discipline to avoid collision or confusion with similarly named `regs.h` fields. MI0 busy/poll bits need correct polling by callers; the header does not enforce timing.

## Test Signals
Signals include successful FPGA board probe, readable FPGA version/status registers, working MI0 MDIO reads/writes, GMAC enable/disable and loopback behavior, per-port MAC address programming, multicast/promiscuous/jumbo configuration, and correct FPGA master interrupt cause/enable handling for SGE, TP, MC3, GMAC, and PCIX events.
