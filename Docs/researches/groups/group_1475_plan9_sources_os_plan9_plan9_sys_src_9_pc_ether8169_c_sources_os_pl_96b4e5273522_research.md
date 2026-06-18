# Group Research: group_1475_plan9_sources_os_plan9_plan9_sys_src_9_pc_ether8169_c_sources_os_pl_96b4e5273522

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/plan9`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/ether8169.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/ether8169.c

## Role

Plan 9 PCI Ethernet driver for Realtek RTL8110S/8169S/8168/810x-family controllers. It binds as `rtl8169` and implements device discovery, reset, MII link handling, descriptor-ring RX/TX, multicast filtering, statistics, and shutdown.

## Main Interfaces

- Registers card type with `ether8169link()` via `addethercard("rtl8169", rtl8169pnp)`.
- Exposes generic Ethernet callbacks: `attach`, `transmit`, `interrupt`, `ifstat`, `promiscuous`, `multicast`, and `shutdown`.
- Uses `ethermii.h` for PHY access through `rtl8169miimir`, `rtl8169miimiw`, `rtl8169mii`, and `miistatus`.

## Data Structures

- `D`: 16-byte TX/RX DMA descriptor with control, VLAN, and 64-bit address split fields.
- `Dtcc`: hardware tally counter dump area.
- `Ctlr`: per-device PCI/MMIO state, descriptor rings, buffer arrays, MII state, interrupt mask, statistics, and watermarks.

## Important Behavior

- Scans PCI Ethernet devices and accepts selected Realtek IDs plus one Corega alias.
- Uses I/O-port CSR access rather than memory-mapped access.
- Reads MAC address from `Idr0` unless user supplied an address.
- Allocates 32 TX descriptors, 256 RX descriptors, and a tally-counter block on first attach.
- RX path accepts only single-descriptor packets with `Fs|Ls` and no receive-summary error; CRC is stripped by subtracting four bytes.
- TX path reclaims completed descriptors, queues packets from `edev->oq`, and pokes `Tppoll`.
- Multicast uses Ethernet CRC hash into Realtek multicast registers, with PCIe variants requiring reversed hash-register byte order.
- Hardware-specific setup branches on `macv` and `pciv`, including several undocumented “magic” register writes.

## Dependencies And Assumptions

- Depends on Plan 9 kernel networking (`etherif.h`, `netif.h`) and MII support (`ethermii.h`).
- Assumes 32-bit PCI DMA addresses by writing high descriptor address words as zero.
- Assumes Realtek PHY address `1`.
- Some variants are explicitly untested or rely on vendor-driver-derived constants.

## Notable Risks

- RX fragment handling drops packets that span multiple descriptors; oversized packets are expected to be filtered or counted.
- `rtl8169attach()` calls `miistatus(ctlr->mii)` even though `rtl8169mii()` can fail, so nil MII handling depends on external behavior.
- Hardware-version handling is conservative; unknown `macv` rejects the device.
- Transmit interrupt masking leaves normal TX interrupts mostly off and relies on transmit calls/selected errors for cleanup.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/ether8169.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/ether82543gc.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/ether82543gc.c

## Role

Plan 9 driver for Intel RS-82543GC Gigabit Ethernet, specifically older Intel PRO/1000 server adapters. It registers as `82543GC`.

## Main Interfaces

- `ether82543gclink()` registers `gc82543pnp`.
- Provides Ethernet callbacks for attach, transmit, interrupt, ifstat, shutdown, control, promiscuous, and multicast.
- `gc82543ctl()` supports `auto on/off` and `clear stats`.

## Data Structures

- `Rdesc` and `Tdesc`: Intel legacy receive/transmit descriptors.
- `Ctlr`: MMIO register mapping, EEPROM image, descriptor rings, private RX block-pool selector, statistics, flow-control config, and multicast table shadow.
- Global free lists split short and jumbo receive buffers, though normal operation uses short buffers.

## Important Behavior

- Maps BAR0 with `vmap` and reads registers through volatile memory access.
- Reads AT93C46-style EEPROM by bit-banging `Eecd`; validates checksum `0xBABA`.
- Resets device, reloads EEPROM defaults, configures flow control and TBI autonegotiation.
- Initializes receive address registers, clears 4096-bit multicast table, and sets up RX/TX descriptor rings.
- Uses a watchdog kproc to periodically check link and replenish RX descriptors.
- RX uses a private block pool and hands completed good packets to `etheriq`.
- TX sends only when link is up and not paused; completed descriptors free their blocks.
- Multicast hashes directly from address bytes into the Intel MTA.

## Dependencies And Assumptions

- Assumes little-endian descriptor/register layout, as noted by the file header.
- No generic `ethermii.h` integration; this driver is mostly TBI/autoneg-oriented.
- Device selection accepts only Intel 82543GC fiber ID while explicitly skipping older or copper variants.

## Notable Risks

- Several comments mark tuning and GMII/MII support as incomplete.
- `gc82543recv()` drops non-EOP or errored packets without detailed error accounting.
- The RX free-block pool is global, so multiple devices share allocator state.
- Busy-wait loops during detach/reset have no scheduling backoff.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/ether82543gc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/ether82557.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/ether82557.c

## Role

Plan 9 driver for Intel 82557/82558/82559 and related 82562/PRO/100 Fast Ethernet controllers. It registers as `i82557`.

## Main Interfaces

- `ether82557link()` registers `reset`.
- Supplies generic Ethernet attach, transmit, interrupt, ifstat, shutdown, promiscuous, and multicast callbacks.
- Uses internal `command()` helper for 8255x CU/RU command register sequencing.

## Data Structures

- `Rfd`: receive frame descriptor with embedded packet buffer.
- `Cb`: command block ring used for transmit, configure, individual-address setup, multicast setup, and NOP workarounds.
- `Ctlr`: I/O-port state, EEPROM, MII lock, receive-frame ring, command-block queue, configuration bytes, and statistical dump buffer.

## Important Behavior

- Scans supported Intel PCI IDs, wakes devices from PCI power management, and uses I/O BAR1.
- Reads variable-size serial EEPROM through `hy93c46r`; checksum expected to sum to `0xBABA`.
- Uses the 8255x command unit and receive unit, not simple modern descriptor rings.
- Builds an RFD ring with a suspended sentinel buffer to avoid hardware prefetch issues.
- TX queues transmit/configuration/address commands into a circular command-block ring and resumes the CU.
- RX copies small packets into new blocks and can swap in a replacement RFD block for larger packets.
- PHY support uses MDI register reads/writes, PHY scan fallback, and several DP83840/82555 workarounds.
- Multicast setup is incomplete; adding multicast currently enables a broader receive mode through configuration.

## Dependencies And Assumptions

- Depends on Plan 9 PCI, I/O port, queue, and Ethernet infrastructure.
- Assumes the chip can be reset without restoring PCI config beyond the power-management wake path.
- Uses device revision and EEPROM fields to infer PHY behavior.

## Notable Risks

- `ifstat()` waits for dump completion with a tight spin on `ctlr->dump[16]`.
- Multicast support is effectively coarse and may enable promiscuous/multicast-all behavior.
- Several chip/hub workarounds are static because dynamic autonegotiation monitoring is not implemented.
- The watchdog periodically injects multicast-setup action for a receiver lockup erratum.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/ether82557.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/ether82563.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/ether82563.c

## Role

Plan 9 driver for Intel PCIe gigabit controllers, including 82563, 82566/7, 82571/2/3/4/5/6/7/9. It registers multiple model names plus `igbepcie`.

## Main Interfaces

- `ether82563link()` registers model-specific PNP functions and a catch-all `igbepcie`.
- Ethernet callbacks: attach, transmit, interrupt, ifstat, ctl, promiscuous, multicast, shutdown.
- Control messages support runtime RX interrupt timer tuning: `rdtr` and `radv`.

## Data Structures

- `Rd` and `Td`: Intel receive/transmit descriptors.
- `Flash`: helper for flash-backed NVM reads on integrated controller variants.
- `Ctlr`: MMIO state, controller type, EEPROM/NVM image, receive address, descriptor rings, worker rendezvous points, interrupt masks, block pool accounting, flow control, statistics, and watermarks.

## Important Behavior

- Scans many Intel PCI IDs and maps BAR0 registers.
- Resets device, reads EEPROM either via `Eerd` or ICH flash descriptor path, validates checksum, and programs receive address registers.
- Uses one global RX block pool, with per-controller allocation count.
- Attach starts three kernel processes: link monitor, receive processor, and transmit processor.
- Interrupt handler masks causes and wakes the relevant process rather than doing all work inline.
- RX process replenishes descriptors, handles checksum flags when enabled, and queues good packets to `etheriq`.
- TX path reclaims completed descriptors and fills the ring from `edev->oq`.
- Link process reads PHY status, tracks speed counts, and restarts autonegotiation for selected PHY fault bits.
- Multicast hashes into MTA and intentionally never clears bits because hash collisions are not reference-counted.

## Dependencies And Assumptions

- Depends on MMIO CSR access, Plan 9 kprocs/rendezvous, PCI, and Ethernet queue/block APIs.
- Assumes 32-bit DMA by writing high address registers as zero.
- Disables RX checksum offload in initialization because comments identify boot-time problems on at least one controller.
- Jumbo receive sizes are deliberately disabled by forcing `rbsz = ETHERMAXTU`.

## Notable Risks

- Global `nrbfull` and RX block pool are shared across controllers.
- Some conditional logic looks suspect: `if(ctlr->type != i82575 || ctlr->type == i82576)` is true for nearly all types.
- Link/PHY support is controller-family-specific and comments doubt 82575 PHY correctness.
- Flash/NVM and reset paths contain long busy waits and panic on stuck EEPROM/flash reads.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/ether82563.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/ether82598.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/ether82598.c

## Role

Plan 9 PCIe 10Gb Ethernet driver for Intel 82598 and 82599 controllers. It registers as `i82598` and `i10gbe`.

## Main Interfaces

- `ether82598link()` registers `pnp`.
- Ethernet callbacks include attach, detach/shutdown, transmit, interrupt, ifstat, ctl, multicast, and promiscuous.
- `ctl()` currently rejects all commands with `Ebadarg`.

## Data Structures

- `Rd` and `Td`: 10Gb receive and transmit descriptors.
- `Stat`: register/name table for hardware counters.
- `Ctlr`: PCI device, MMIO and MSI-X mappings, RX/TX rings, receive block pool counters, worker rendezvous state, receive address, multicast table, stats, speed counters, and watermarks.

## Important Behavior

- Scans Intel 82598/82599 PCI IDs, maps register BAR and MSI-X BAR, but does not use MSI-X table support.
- Resets device, reads NVM with a section-aware checksum check, and loads receive address.
- Starts link, RX, and TX kernel processes on attach.
- RX/TX workers are woken by interrupt bits and replenish/clean descriptor rings outside interrupt context.
- Disables jumbo mode and IP payload checksum offload due to hardware/errata concerns.
- Programs queue/vector mapping with simple queue 0 RX/TX interrupt causes.
- Multicast hashes into MTA and does not clear bits on remove, matching collision-safe behavior.
- Supports both 82598 and 82599 register differences for RX address, reset cleanup, RX DMA, and TX DMA enable.

## Dependencies And Assumptions

- Uses Plan 9 PCI/MMIO mapping, block pools, kprocs, queues, and Ethernet API.
- Assumes 32-bit DMA address use in descriptor base and packet addresses.
- Bounds controller table to four controllers.
- Treats max MTU as `ETHERMAXTU`.

## Notable Risks

- `eeread()` can spin indefinitely until `EEdone`.
- `freemem()` is not called on normal detach; comments mark memory cleanup TODO.
- RX path does not inspect descriptor error bits before queuing packets.
- MSI-X BAR is mapped but unused.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/ether82598.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/ether83815.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/ether83815.c

## Role

Plan 9 driver for National Semiconductor DP83815 and SiS 900-family 10/100 Ethernet controllers. It registers as `83815`.

## Main Interfaces

- `ether83815link()` registers `reset`.
- Ethernet callbacks: attach, transmit, interrupt, ifstat, promiscuous, multicast, shutdown.
- Multicast callback is a no-op because all multicast is already accepted.

## Data Structures

- `Des`: DP83815 transmit/receive descriptor with next pointer, command/status, buffer address, and block pointer.
- `Ctlr`: PCI/I/O-port state, SROM data and MAC address, duplex/speed state, RX/TX rings, extensive RX/TX/system counters, and silicon revision.

## Important Behavior

- Scans PCI network devices for National DP83815 and SiS900.
- Uses I/O-port registers and allocates shared descriptor storage for TX and RX rings.
- Reads MAC address differently for National SROM, Soekris-style variants, SiS SROM, and SiS 630 CMOS-backed address storage.
- Performs soft reset, PHY reset, recommended DSP/config register programming, and autonegotiation.
- RX interrupt loop consumes descriptors owned by software, checks status bits, queues good packets, and replaces receive buffers.
- TX path queues blocks into descriptors and prompts the transmitter; interrupt path reclaims completed descriptors.
- Promiscuous mode toggles accept-all-unicast in receive filter control.
- Media override parsing accepts common 10/100 and full-duplex option strings.

## Dependencies And Assumptions

- Uses Plan 9 PCI, I/O, block, and Ethernet interfaces.
- Assumes internal PHY support; external PHY support is listed as future work.
- Uses `ether->mbps = media(ether)` after autonegotiation.

## Notable Risks

- Some MAC address extraction logic is highly hardware-specific and bit-order-sensitive.
- RX replacement allocation failure leaves descriptor buffer handling degraded.
- Link-change handling only updates link state on PHY interrupt and does not reconfigure all media parameters.
- Full-duplex and threshold behavior are partly option/autonegotiation driven and marked incomplete in comments.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/ether83815.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/ether8390.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/ether8390.c

## Role

Shared Plan 9 support code for National Semiconductor DP8390 and compatible Ethernet NIC cores, used by board-specific NE2000/SMC-style drivers.

## Main Interfaces

- Exports `dp8390reset`, `dp8390read`, `dp8390getea`, and `dp8390setea`.
- Installs generic Ethernet callbacks during `dp8390reset`: attach, transmit, interrupt, shutdown, promiscuous, multicast.
- Relies on board-specific `Dp8390` fields and low-level access helpers from `ether8390.h`.

## Data Structures

- `Hdr`: DP8390 receive-ring packet header.
- Uses `Dp8390` from `ether8390.h` for port/data width, shared-memory mode, ring page numbers, multicast shadow, and transmit state.

## Important Behavior

- Implements DP8390 remote DMA reads/writes through register setup plus data-port transfer.
- Supports both shared-memory cards and remote-DMA I/O cards.
- Handles optional dummy remote-read sequence for boards that require it before writes.
- Initializes the receive ring using page pointers `pstart`, `pstop`, `nxtpkt`, and `Bnry`.
- RX path reads ring headers, validates next-page and length, handles wraparound, copies packets into Plan 9 blocks, and advances boundary.
- TX path pads short packets, writes them to card memory, starts transmission, and tracks `txbusy`.
- Interrupt path handles receive, transmit complete/error, counter overflow, and overflow recovery using the datasheet-prescribed sequence.
- Multicast uses `ethercrc`, a 64-bit hash table, and reference counts for filter bits.

## Dependencies And Assumptions

- Depends on `ether8390.h` macros/functions: `regr`, `regw`, `rdread`, and `rdwrite`.
- Assumes board driver has set ring memory layout, transfer width, and data port correctly before `dp8390reset`.
- Maximum accepted RX packet is `sizeof(Etherpkt)`.

## Notable Risks

- Remote DMA waits use spin timeouts and may silently proceed after timeout in some paths.
- Ring corruption causes full ring reinitialization and packet loss.
- Only one transmit packet is active at a time.
- Header comments and behavior assume old DP8390 clone quirks, so board setup is critical.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/ether8390.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/ether8390.h -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/ether8390.h

## Role

Header and x86-specific access layer for DP8390-compatible Ethernet drivers. It defines the shared controller state used by `ether8390.c` and board-specific drivers.

## Main Interfaces

- Defines `Dp8390`.
- Declares:
  - `dp8390reset(Ether*)`
  - `dp8390read(Dp8390*, void*, ulong, ulong)`
  - `dp8390getea(Ether*, uchar*)`
  - `dp8390setea(Ether*)`
- Defines register access macros `regr` and `regw`.
- Defines static data-port transfer helpers `rdread` and `rdwrite`.

## Data Structures

- `Dp8390` embeds a `Lock` and stores:
  - I/O register and data-port addresses.
  - Transfer width and shared-memory/dummy-read flags.
  - Receive and transmit page layout.
  - Transmit busy flag.
  - Multicast address-register shadow and 64 hash-bit reference counts.

## Important Behavior

- `rdread` and `rdwrite` select byte or word I/O transfer routines based on `ctlr->width`.
- Unsupported transfer widths panic.
- `Dp8390BufSz` defines the NIC page size as 256 bytes.

## Dependencies And Assumptions

- Assumes x86 I/O-port primitives `inb`, `outb`, `insb`, `outsb`, `inss`, and `outss`.
- Intended to be included after Plan 9 kernel and Ethernet definitions.
- Functions are static in the header because they are architecture/translation-unit local helpers.

## Notable Risks

- Header contains executable static functions, so changes affect every including board driver.
- Width must be initialized before any shared DP8390 code calls data-port helpers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/ether8390.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/etherdp83820.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/etherdp83820.c

## Role

Plan 9 driver for National Semiconductor DP83820 10/100/1000 Ethernet controller. It registers as `DP83820`.

## Main Interfaces

- `etherdp83820link()` registers `dp83820pnp`.
- Ethernet callbacks: attach, transmit, interrupt, ifstat, promiscuous, multicast, shutdown.
- MII access is exposed through `dp83820miimir` and `dp83820miimiw`.

## Data Structures

- `Desc`: 64-bit-aligned TX/RX descriptor with link pointer, buffer pointer, command/status, extended status, and block pointer.
- `Ctlr`: MMIO state, EEPROM, config shadow, MII pointer, descriptor rings, global RX block pool use, MIB counters, and TX/RX error counters.

## Important Behavior

- Scans PCI Ethernet devices for DP83820 ID, maps BAR1 MMIO, and enables bus mastering.
- Resets controller, reads ATC93C46-style EEPROM, checks byte checksum, and derives MAC address from EEPROM words.
- Uses bit-banged MII management through `Mear`; attaches generic Plan 9 MII support unless TBI mode is enabled.
- Allocates RX/TX descriptor memory and a private receive block pool on first attach.
- RX descriptors are circular through hardware `link` fields; received good packets are queued and descriptors are replenished.
- TX path reclaims completed descriptors, counts descriptor error bits, queues packets, and restarts transmitter.
- Interrupt path handles RX, TX, MIB counter service, PHY changes, and TX underrun threshold adjustment.
- Receive filter accepts perfect-match, broadcast, and all multicast by default.

## Dependencies And Assumptions

- Depends on `ethermii.h` and Plan 9 PCI/MMIO/Ethernet APIs.
- File header states little-endian and 32-bit host assumptions.
- Uses global `dp83820rbpool` for receive block recycling.

## Notable Risks

- `dp83820ifstat()` assigns `edev` counters using `Mibd + offset` as an array index, which appears inconsistent with `ctlr->mibd[Nmibd]`.
- Promiscuous and multicast callbacks are effectively no-ops because filter defaults are broad.
- Reset contains disabled configuration code and prints diagnostic PCI/config values unconditionally.
- Several waits spin until reset/MII operations complete.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/etherdp83820.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/etherec2t.c -->
# File Research: sources/os/plan9/plan9/sys/src/9/pc/etherec2t.c

## Role

Plan 9 PCMCIA wrapper driver for NE2000-like Ethernet cards, including Linksys, Accton, Netgear, SMC, and related cards. It uses the shared DP8390 core from `ether8390.c`.

## Main Interfaces

- `etherec2tlink()` registers `addethercard("EC2T", reset)`.
- `reset()` probes/configures a matching PCMCIA card and then delegates common NIC setup to `dp8390reset` and `dp8390setea`.

## Data Structures

- `Ec2t`: PCMCIA product-name matcher plus flag indicating whether MAC address/checksum are read from I/O space.
- `ec2tpcmcia[]`: supported card name table.
- Uses `Dp8390` from `ether8390.h`.

## Important Behavior

- Supplies default port `0x300`, IRQ `9`, memory offset `0x4000`, and size `16 KiB` when not configured.
- Allocates the I/O range and finds a matching PCMCIA special entry, with optional `id=` override and `iochecksum` option.
- Initializes `Dp8390` for 16-bit I/O, no shared memory, data port at base + `0x10`.
- Computes transmit and receive page layout from `ether->mem`, `ether->size`, and `Dp8390BufSz`.
- Resets board by reading and writing the reset port.
- Validates card identity either by I/O-space checksum or by reading PROM marker bytes through DP8390 remote DMA.
- Loads MAC address from PROM/I/O bytes unless user supplied one, then writes it to the DP8390 core.

## Dependencies And Assumptions

- Depends on PCMCIA helper `pcmspecial`, `pcmspecialclose`, and the shared DP8390 implementation.
- Assumes NE2000-compatible register layout with data port offset `0x10` and reset port offset `0x1F`.
- Assumes 16-bit transfers.

## Notable Risks

- If `malloc(sizeof(Dp8390))` succeeds but later validation fails, cleanup frees controller memory but does not clear `ether->ctlr`.
- Probe identity relies on product strings and weak PROM/checksum signatures.
- Default I/O/IRQ settings may conflict unless overridden by configuration.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/9/pc/etherec2t.c -->