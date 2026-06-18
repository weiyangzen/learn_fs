# sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/bcm1480_regs.h

Purpose: maps BCM1255/BCM1280/BCM1455/BCM1480 on-chip peripheral register addresses. It intentionally includes `sb1250_regs.h` and then adds or overrides the register layout that changed for the BCM1480 family.

Important APIs/types/functions: no functions or structs are defined. The exported interface is address and offset macros: `A_BCM1480_MC_*`, `A_BCM1480_L2_*`, `A_BCM1480_MAC_*`, `A_BCM1480_DUART*`, `A_BCM1480_IMR_*`, `A_BCM1480_SCD_*`, `A_BCM1480_HT_*`, `A_BCM1480_NC_*`, packet-manager/high-speed-port registers, and `A_BCM1480_PHYS_*` physical map ranges. Parameterized macros such as `A_BCM1480_MC_REGISTER(ctlid, reg)`, `A_BCM1480_IMR_REGISTER(cpu, reg)`, and mailbox helpers encode per-instance spacing.

Control flow: callers use these macros to sequence MMIO access. The file encodes routing decisions such as four memory controllers, extra MACs, two DUART blocks, 128-bit interrupt mapper registers split into non-contiguous halves, additional watchdogs/compare registers, and per-port HyperTransport/node-controller/packet-manager blocks.

State and persistence: the header itself stores no state; every address resolves to memory-mapped hardware state. Some aliases target write-only set/clear mailbox registers, status registers, or physical windows whose effects persist in the device.

Dependencies and integration: depends on `sb1250_defs.h` and `sb1250_regs.h`. It is a compatibility bridge: common SB1250 symbols remain available, while BCM1480-specific blocks use `_BCM1480_` names to avoid accidentally programming incompatible SCD/IMR/L2/MC layouts.

Risks and test signals: the primary risk is using an SB1250 `A_*` symbol for a block whose BCM1480 layout diverges, especially SCD and interrupt mapper registers. Address arithmetic should be checked for CPU, MAC, MC, PM, HT, and high-speed-port instance bounds. Test signals include build coverage for platform code using all macros, sparse/checkpatch-style detection of pointer-width truncation, and hardware smoke tests for UART, timers, interrupts, MAC DMA, and memory-controller probing.
