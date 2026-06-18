# Group Research: group_13_9front_sources_os_plan9_9front_sys_src_9_pc_etheri225_c_sources_os_pl_61553f867f24

Scope: `Docs/research_subset_a.md`, source tree `sources/os/plan9/9front`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/etheri225.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/etheri225.c

Implements a Plan 9 PCI Ethernet driver for Intel i225/i226 2.5GbE controllers.

Key behavior:
- Defines Intel i225/i226 register offsets, interrupt bits, EEPROM/MDI/semaphore controls, RX/TX descriptor formats, and statistic registers.
- Discovers supported Intel PCI IDs, maps BAR0 MMIO, enables PCI bus mastering, and registers as `i225`.
- Resets the MAC, waits for EEPROM autoload, marks the driver active, disables EEE, initializes the MAC address and multicast table.
- Uses hardware semaphores and sync bits to serialize PHY/EEPROM/MDI access, then attaches a Plan 9 `Mii` bus with clause 22/45 autonegotiation.
- Allocates one 1024-entry TX ring and one 1024-entry RX ring, both with 16-byte descriptors.
- Runs separate kprocs for TX completion/fill, RX completion/refill, link status, and periodic statistics accumulation.
- Interrupt handler masks/restores interrupts, wakes link/RX/TX worker rendezvous points for link, queue 0 RX, and queue 0 TX events.
- RX path concatenates multi-descriptor packets, drops errored chains, marks checksum flags, and passes packets to `etheriq`.
- TX path dequeues from `edev->oq`, writes DMA descriptors, requests status, and frees completed blocks.
- Exposes `ifstat`, promiscuous mode, multicast hash insertion, shutdown reset, and `Ether` callbacks.

Dependencies:
- Uses Plan 9 kernel Ethernet, PCI, MII, DMA, block pool, rendezvous, and kproc APIs.
- Depends on i225/i226 MMIO register semantics and PCI write-address translation through `PCIWADDR`.

Research notes:
- Multicast removal is not implemented; `i225multicast` only sets hash bits.
- Only queue 0 is actively used even though interrupt vector setup covers four queue pairs.
- Potential controller-list issue: `i225pci` assigns `i225ctlr->link = c` rather than linking through `i225ctlrtail`, which can lose controllers after the second device.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/etheri225.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/etherigbe.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/etherigbe.c

Implements the Plan 9 Intel PRO/1000-era gigabit Ethernet driver for 82543/82544/82540/82541/82545/82546/82547-class devices.

Key behavior:
- Defines PCI IDs, MAC registers, EEPROM/flash bits, MDI access, flow control, RX/TX descriptor formats, interrupts, statistics, and chip-specific flags.
- Probes Intel gigabit Ethernet PCI devices, maps MMIO BAR0, resets the device, reads EEPROM/SPI contents, validates checksum `0xBABA`, and programs receive address slots.
- Handles 82543GC specially with GPIO-bitbanged MDIO; later chips use the MDIC register.
- Initializes PHY/MII, flow control, collision distance, speed/duplex, and autonegotiation-related settings.
- Allocates aligned RX/TX descriptor memory plus per-descriptor block arrays during attach.
- RX kproc initializes descriptors, enables RX, sleeps on RX interrupts, consumes descriptor-done packets, applies checksum flags when valid, and replenishes buffers.
- TX path frees completed descriptors, fills the TX ring from `edev->oq`, requests TX descriptor writeback when the ring is near full, and re-enables TX interrupts as needed.
- Interrupt handler masks active causes, wakes link/RX workers, directly calls transmit cleanup on TX writeback, and restores interrupt masks.
- Provides `ifstat` with hardware statistics, EEPROM dump, PHY register dump, and driver counters.
- Provides ctl command `rdtr` to tune receive delay timer.

Dependencies:
- Uses Plan 9 PCI, Ethernet, MII, block, interrupt, and command parsing APIs.
- Encodes Intel EEPROM Microwire/SPI transactions through `Eecd` bit operations.

Research notes:
- Header comments say this CAT5 path does not integrate fiber support and checksum offload is intentionally incomplete.
- RX checksum offload programming is disabled in `igberxinit` because of known hardware/driver bugs.
- Multicast filter bits are never cleared because multiple multicast addresses can hash to the same bit.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/etherigbe.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/etherm10g.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/etherm10g.c

Implements a firmware-driven Plan 9 driver for Myricom 10G PCIe Ethernet adapters.

Key behavior:
- Embeds 2K/4K Myricom firmware images and chooses firmware/alignment from PCIe lane/ECRC checks and optional `myriforce`.
- Maps adapter RAM, parses EEPROM strings for MAC address and serial number, allocates DMA-visible command, completion, stats, TX, and RX structures.
- Boots firmware by copying it into adapter RAM and submitting firmware boot commands through device command ports.
- Sends device commands for reset, interrupt queue DMA, ring offsets/sizes, coalescing, stats DMA, MTU, MAC address, flow control, promiscuous mode, and multicast join/leave.
- Uses a completion ring plus separate small and big RX rings; RX kproc replenishes both and delivers completed packets from the done ring.
- TX path segments outgoing blocks on firmware alignment boundaries, fills host TX descriptors, copies them into LANai/device memory, and frees blocks after firmware TX count advances.
- Interrupt handler wakes RX/TX workers, handles MSI versus legacy interrupt acknowledgement, checks DMA-updated stats, and updates link state.
- Exposes `ifstat` for firmware stats/ring counters and ctl commands for debug, coalescing, forced wakeups, and RX ring dump.
- Registers as `m10g` for Myricom PCI vendor IDs.

Dependencies:
- Uses Plan 9 PCI, Ether, block pool, kproc, DMA address, and command parsing APIs.
- Depends on Myricom firmware command ABI and device RAM layout.

Research notes:
- The device is treated as big-endian; helper functions pack/unpack 16/32-bit values.
- Shutdown/detach path unmaps and frees the controller and is marked/incomplete in spirit.
- Potential bug: `whichfw` uses `if(i != 4*KiB || i != 2*KiB)`, which is always true and forces 2KiB for any `myriforce` value.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/etherm10g.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/etherrt2860.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/etherrt2860.c

Implements a Plan 9 Wi-Fi/Ethernet driver for Ralink RT2860-family PCI/PCIe wireless devices, especially RT2790 and RT3090.

Key behavior:
- Defines extensive PCI, DMA, PBF, MAC, BBP, RF, EEPROM/eFUSE, security table, TXWI/RXWI, and descriptor constants.
- Maintains controller state for MAC/RF revision, RF chains, EEPROM calibration data, per-channel TX power, RSSI/LNA offsets, WCID slots, RX/TX rings, firmware image, and Wi-Fi integration.
- Reads firmware `ral-rt2860` from `/boot` or `/lib/firmware`, uploads it to MCU program RAM, and waits for MCU readiness.
- Uses MCU mailbox commands for BBP access, LEDs, RF reset, sleep/wakeup, and PCIe power-save settings.
- Reads calibration and identity data from serial EEPROM or RT3071+ eFUSE, including MAC address, RF type, chain counts, BBP/RF overrides, power tables, LNA/RSSI, LEDs, and power-save level.
- Initializes MAC defaults, BBP defaults, EEPROM BBP overrides, RF programming, RT3090 filter calibration, antenna selection, DMA rings, WCID/key tables, RX filters, protection, RTS threshold, and LEDs.
- Supports channel changes through classic RT2860 RF register programming or RT3090-style RF CSR programming.
- Integrates with `wifiattach`; `transmit` builds TXWI plus 802.11 header descriptors, assigns WCID for broadcast/BSS, queues EDCA TX, and hardcodes basic rates.
- RX interrupt path drains descriptors, handles RXWI, optional L2 padding, CRC/ICV drops, and passes frames to `wifiiq`.
- TX interrupt path frees DMA payload blocks, clears descriptors, and reads TX status FIFO.
- Promiscuous mode updates Wi-Fi RX state and hardware receive filters; multicast callback is empty.

Dependencies:
- Uses Plan 9 PCI, Ether, Wi-Fi layer (`wifi.h`), firmware file I/O, DMA, block allocation, interrupts, and kernel locking.
- Based on behavior from OpenBSD `ral(4)` per file header.

Research notes:
- Attach requires privileged firmware access via `iseve`.
- PCI probe only accepts Ralink vendor `0x1814` and devices RT2790/RT3090, despite broader constants and code paths.
- Management queue uses EDCA AC VO for RT2860C because the hardware management ring is noted as broken.
- Many 802.11 capabilities are minimal or fixed: basic rate handling is simple, multicast is unimplemented, and some calibration flags are disabled with `XXX` comments.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/etherrt2860.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/ethersmc.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/ethersmc.c

Implements PCMCIA SMC EtherEZ / SMC91cXX Ethernet support.

Key behavior:
- Defines banked SMC91cXX I/O registers, transmit/receive control bits, MMU commands, FIFO ports, interrupt flags, status bits, and statistic counters.
- Uses PCMCIA tuple `FUNCE` node-id data to read the Ethernet address when not supplied.
- Resets the chip, programs the MAC address, enables auto-release and error/counter interrupts, resets the chip MMU, and enables RX/TX on attach.
- TX path allocates chip packet memory pages through the SMC MMU, writes packet header/data through PIO, handles allocation failure by saving the block and enabling allocation interrupt, then enqueues for transmit.
- RX path reads current RX packet through the chip FIFO, checks status/error bits, allocates a Plan 9 block, handles odd-frame padding, and submits to `etheriq`.
- Interrupt handler saves/restores bank and pointer registers, masks interrupts while servicing RX, TX error, TX empty, allocation completion, RX overrun, and EPH events.
- Tracks link/carrier/collision/defer/overrun counters and exposes chip revision/statistics via `ifstat`.
- Supports promiscuous mode and all-multicast mode based on `ether->nmaddr`.

Dependencies:
- Uses Plan 9 PCMCIA helpers, I/O port allocation, Ethernet/block APIs, and interrupt registration.
- Relies on 16-bit PIO access and SMC91cXX internal MMU/FIFO semantics.

Research notes:
- This is a non-PCI DMA driver; packet movement is programmed I/O through banked registers.
- TX timeout recovery resets/re-enables the chip if a saved transmit block cannot be allocated for too long.
- Multicast filtering is coarse: it toggles all-multicast rather than maintaining a hash table.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/ethersmc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/ethervgbe.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/ethervgbe.c

Implements a Plan 9 driver for VIA Velocity VT6122 gigabit Ethernet.

Key behavior:
- Defines VIA Velocity I/O registers, command/status bits, MII registers, CAM filter registers, RX/TX descriptor formats, interrupt bits, and debug controls.
- Probes PCI class Ethernet device `0x1106:0x3119`, requires I/O BAR0 of size 256, allocates the I/O range, and registers as `vgbe`.
- Performs soft reset, EEPROM reload, MAC address read, interrupt setup, 32-bit DMA address setup, MAC start, RX/TX engine enable, and MII bus initialization.
- Allocates 256 RX and 256 TX descriptors, plants RX blocks from a `Bpool`, loads descriptor base/count/index registers, and starts RX/TX queues on attach.
- RX interrupt path scans all RX descriptors, delivers good frames minus CRC, replants descriptors, and wakes the RX queue.
- TX path finds free descriptors near the hardware TX index, dequeues from `edev->oq`, writes one-fragment TX descriptors, wakes the queue, and frees completed blocks on TX completion.
- Link status uses PHY status register to set 10/100/1000 speed and link state.
- Multicast path programs up to 32 CAM entries and CAM mask bits; promiscuous mode toggles RX control bits.
- Provides ctl commands `reset`, `dumpintr`, `dumprx`, `dumptx`, and `dumpall`, plus `ifstat` counters.

Dependencies:
- Uses Plan 9 PCI, I/O ports, Ethernet, MII, block pool, command parsing, and interrupt APIs.
- Uses little-endian identity macros, so the code assumes a little-endian host.

Research notes:
- File comments list several unfinished areas: 64/48-bit DMA, autonegotiation tuning, shutdown, jumbo frames, error reporting, and fuller promiscuous behavior.
- RX/TX descriptor scanning is simple and scans whole rings rather than maintaining software producer/consumer indices.
- Only low 32-bit DMA addresses are programmed.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/ethervgbe.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/ethervirtio.c -->
# File Research: sources/os/plan9/9front/sys/src/9/pc/ethervirtio.c

Implements a Plan 9 virtio-net driver for the legacy/transitional virtio PCI interface.

Key behavior:
- Defines legacy virtio PCI register layout, device status bits, feature bits, descriptor flags, virtqueue structs, net header, and control queue command classes.
- Probes vendor `0x1AF4` virtio-net devices with device IDs `0x1000` or `0x1041`, revision `0`, I/O BAR0, and subsystem type `1`.
- Performs legacy initialization: reset status, acknowledge driver, negotiate `Fmac`, `Fstatus`, `Fctrlvq`, and `Fctrlrx`, initialize RX/TX/control virtqueues, and publish queue PFNs.
- Allocates each virtqueue in legacy split-ring layout with descriptor, avail, and used areas aligned to 4096 bytes.
- Attach sets `Sdriverok` and starts RX/TX kprocs.
- RX kproc prebuilds descriptor pairs for virtio net header plus writable packet buffer, replenishes from a block pool, notifies the device, sleeps for used entries, and passes received packets to `etheriq`.
- TX kproc prebuilds descriptor pairs for shared header plus packet data, reads from `edev->oq`, waits for free slots, retires used descriptors, and notifies the device.
- Interrupt handler reads ISR and wakes any virtqueue with new used entries.
- Control queue helper sends class/cmd/data/ack descriptor chains for promiscuous and all-multicast control when supported.
- `ifstat` prints feature/status registers and queue counters; shutdown resets status and clears PCI bus mastering.

Dependencies:
- Uses Plan 9 PCI, I/O port, Ethernet, block pool, rendezvous, kproc, and DMA physical address APIs.
- Implements legacy virtio 1.0 split virtqueue behavior, not modern non-transitional PCI capability layout.

Research notes:
- Non-transitional virtio devices are explicitly skipped and expected to be handled by `ethervirtio10`.
- RX and TX use a single shared virtio header allocation per queue because header contents are not varied.
- Link is set optimistically to up in `reset`; `Fstatus` is only reported in `ifstat`, not used to drive link changes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/9/pc/ethervirtio.c -->