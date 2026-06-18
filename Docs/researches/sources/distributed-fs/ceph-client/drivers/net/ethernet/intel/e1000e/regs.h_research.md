# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/e1000e/regs.h

## Purpose
`regs.h` defines e1000e memory-mapped register offsets and indexed-register macros. It is the low-level address map used by the driver for MAC control, descriptor rings, interrupts, statistics, flow control, wake/manageability, RSS, and PTP timestamping.

## Important APIs, types, and functions
The file contains macros rather than functions. Important groups include device control/status (`E1000_CTRL`, `E1000_STATUS`, `E1000_CTRL_EXT`), MDIO/PHY (`E1000_MDIC`, `E1000_PHY_CTRL`, `E1000_KMRNCTRLSTA`), RX/TX queue register macros (`E1000_RDBAL`, `E1000_RDLEN`, `E1000_TDBAL`, `E1000_TXDCTL`, etc.), interrupt registers, hardware statistics counters, receive address/VLAN/multicast tables, manageability registers, RSS tables, and PTP registers (`E1000_TSYNCRXCTL`, `E1000_TSYNCTXCTL`, `E1000_SYSTIM*`, `E1000_TIMINCA`, cross timestamp registers).

## Control flow
No runtime control flow exists here. The indexed queue macros encode hardware layout differences between the first four queues and later queues. Callers use these offsets through e1000e register access macros such as `er32` and `ew32`.

## State and persistence behavior
The definitions address persistent device MMIO state. Some counters are read-to-clear, some registers are write-only or read-only, and some control bits alter persistent hardware behavior across reset or power states. Comments identify access direction for many registers but enforcement is in the call sites.

## Dependencies and integration points
Every e1000e module that touches hardware registers depends on this address map. The PTP code uses the timestamp offsets, PHY code uses MDIC/Kumeran/manageability-related registers, ring setup uses queue macros, and stats/ethtool code use counter offsets.

## Risks
Incorrect offsets are high-impact because reads and writes may still hit valid MMIO locations with unrelated side effects. Queue macros must match hardware generation layout. Read-to-clear counters and timestamp latches require call-site care; using them for flushes or debug dumps can destroy state.

## Test signals
Signals include successful device probe, queue bring-up, interrupt delivery, stats accuracy, PTP operation, wake/manageability behavior, RSS programming, and absence of MMIO faults or unexpected counter resets during ethtool register dumps.
