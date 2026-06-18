<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/smsc/smc91x.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/smsc/smc91x.h

## Purpose
`smc91x.h` is the hardware abstraction and register-definition header for the SMSC/SMC 91C9x/91C1xx Ethernet family used by the `smc91x` driver. It does not register a netdev by itself; instead it gives the C driver portable macros for banked register selection, FIFO data movement, MMU packet allocation, MII bit access, multicast table writes, platform quirks, and private driver state.

## Important APIs, Types, and Functions
The central type is `struct smc_local`, which holds deferred TX state, tasklet/work items, optional power/reset GPIOs, chip revision, cached TX/RX/RPC/CTL modes, MII state, locks, optional PXA DMA state, MMIO bases, data-CS aliasing, bus shift/alignment quirks, and platform data. Important access macros include `SMC_inb/inw/inl`, `SMC_outb/outw/outl`, `SMC_ins*`, `SMC_outs*`, `SMC_SELECT_BANK`, `SMC_GET_*`, `SMC_SET_*`, `SMC_PUSH_DATA`, and `SMC_PULL_DATA`. Register groups cover bank 0 TX/RX/EPH/RPC, bank 1 address/config/control, bank 2 MMU/FIFO/pointer/interrupts, bank 3 multicast/MII/revision, bank 7 external registers, and SMC91C96 attribute-space ECOR/ECSR.

## Control Flow
The runtime driver selects a bank, uses the generated register offsets, and transfers packets through the device data register. TX flow allocates packet memory through `MMU_CMD`, selects packet numbers with `PN_REG`, writes packet headers and payload via `SMC_PUT_PKT_HDR` and `SMC_PUSH_DATA`, then enqueues the frame. RX flow reads the FIFO, pointer, packet header, and payload via `SMC_GET_PKT_HDR` and `SMC_PULL_DATA`, then releases packet memory through MMU commands. Interrupt handling relies on `SMC_GET_INT`, `SMC_ACK_INT`, and `SMC_SET_INT_MASK`; MII accesses are bit-level through `MII_REG`.

## State and Persistence Behavior
The header defines volatile hardware state: selected bank, interrupt masks, packet memory pages, PHY mode, MAC address registers, multicast hash table, and power/reset pins. Persistent state may be affected indirectly by EEPROM reload/store control bits, but this file only defines the bits. Cached driver state lives in `struct smc_local`, especially pending TX skb, work state, MII, cached mode registers, and platform access flags.

## Dependencies and Integration Points
It depends on `linux/smc91x.h`, DMA engine APIs, MII/netdevice types, and arch-specific I/O primitives. ARM, Atari, ColdFire, default MMIO, PXA DMA, data-CS, endian, and alignment paths are integrated by preprocessor selection. The header assumes the including C file provides names such as `lp`, `ioaddr`, `dev`, `CARDNAME`, and `SMC_DEBUG`.

## Risks
Risks are macro side effects, hidden dependencies on local variable names, bank-selection mistakes, non-atomic 8/16-bit fallback accesses, write alignment workarounds, and platform-specific DMA/cache ordering. Changing register constants or access macros can silently break old boards. `BUG()` stubs catch impossible bus-width paths but turn misconfiguration into hard failures.

## Test Signals
Useful signals are successful probe on 8/16/32-bit buses, correct bank debug checks under `SMC_DEBUG`, TX/RX with odd and aligned packet buffers, multicast/promiscuous mode updates, MII link negotiation, PXA DMA and non-DMA RX, netpoll if enabled, and EEPROM reload/store paths on hardware that supports them. Build coverage should include ARM/PXA, ColdFire big-endian 16-bit, and generic MMIO configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/smsc/smc91x.h -->
