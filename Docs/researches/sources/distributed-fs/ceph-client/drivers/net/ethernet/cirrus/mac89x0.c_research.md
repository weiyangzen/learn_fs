<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cirrus/mac89x0.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cirrus/mac89x0.c

## Purpose

`mac89x0.c` is a Macintosh-specific CS89x0 Ethernet driver for Dayna-style CS8900 cards in classic NuBus slot space. It strips the generic driver down to TP-only, hardwired slot/IRQ behavior and shared-memory packet access suitable for these Macintosh cards.

## Important APIs, Types, and Functions

Private `struct net_local` stores message level, chip type/revision, TX command, RX mode/config, and underrun count. Register helpers are split between ISA-like access (`readreg_io`, `writereg_io`) and shared-memory packet-page access (`readreg`, `writereg`), all using NuBus word access with byte swapping.

Core functions are `mac89x0_device_probe`, `net_open`, `net_send_packet`, `net_interrupt`, `net_rx`, `net_close`, `net_get_stats`, `set_multicast_list`, `set_mac_address`, and `mac89x0_device_remove`. The driver registers as a platform driver named `mac89x0`.

## Control Flow

Probe allocates a netdev, assumes slot `0xE`, refuses to bind if a real NuBus function resource exists in that slot, probes the pseudo-ISA address at offset `DEFAULTIOBASE`, validates the CS89x0 signature, enables shared memory with `MEMORY_ON`, reads chip revision and EEPROM MAC address, computes `SLOT2IRQ(slot)`, installs netdev ops, and registers the device.

Open disables interrupts, requests the slot IRQ, writes the chip IRQ selector, programs the MAC address, enables serial RX/TX, accepts directed/broadcast/error-free frames, enables RX/TX/buffer events, re-enables interrupts, and starts the queue. TX disables local IRQs around writing command/length and copying the frame into shared memory, then waits for TX completion interrupt to wake the queue. Interrupt flow mirrors the generic CS89x0 ISQ drain: RX, TX completion/errors, buffer-ready/underrun, missed RX, and collision events.

## State and Persistence Behavior

The driver keeps only volatile netdev-private state. EEPROM is required for the MAC address and is not modified. Hardware state is reprogrammed on each open. Statistics live in `dev->stats` and are supplemented from packet-page miss/collision counters.

## Dependencies and Integration Points

The file depends on classic Macintosh/NuBus APIs (`nubus_slot_addr`, `for_each_func_rsrc`, `hwreg_present`, `SLOT2IRQ`) and shared CS89x0 constants from `cs89x0.h`. It integrates with the normal netdev layer but not phylib or NAPI.

## Risks and Edge Cases

The probe is deliberately hard-coded to slot E, so multi-slot support is absent. Lack of a real NuBus ROM requires ISA-like probing, raising false-positive/false-negative risks. TX uses `local_irq_save` instead of a device spinlock and performs MMIO memory copies directly. The RX path uses `alloc_skb(length, GFP_ATOMIC)` without the 2-byte alignment reserve used in the generic driver. Removal assumes a registered netdev exists.

## Test Signals

Validate slot-E detection with and without a real NuBus card, EEPROM-present behavior, open/close, TX completion wakeups, TX underrun fallback, RX copy path, multicast/promiscuous changes, statistics reads, and module unload cleanup on supported Macintosh hardware or emulator coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cirrus/mac89x0.c -->
