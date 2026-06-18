# subset-b-004305 Research Report

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/arcnet/com20020.c -->
# sources/distributed-fs/ceph-client/drivers/net/arcnet/com20020.c

## Purpose
`com20020.c` is the shared ARCnet COM20020 chipset core. It provides the hardware callback implementation consumed by the generic ARCnet core and by bus-specific wrappers such as ISA, PCI, and PCMCIA. The file probes/checks COM20020 register behavior, copies packet data through the indexed I/O memory window, sets node identity and timing registers, registers the `net_device`, and exports the core helpers when bus drivers are modular.

## Important APIs, Types, and Functions
- `com20020_check(struct net_device *dev)` resets and validates a candidate COM20020 device by programming setup/config subregisters, checking status bits, clearing reset/config flags, and verifying the ARCnet `TESTvalue` signature in buffer memory.
- `com20020_found(struct net_device *dev, int shared)` installs `arcnet_local.hw` callbacks, configures setup and node registers, requests the IRQ, and calls `register_netdev()`.
- `com20020_netdev_ops` binds the device to `arcnet_open`, `arcnet_close`, `arcnet_send_packet`, `arcnet_timeout`, address setting, and multicast/promiscuous mode handling.
- `com20020_copy_to_card()` and `com20020_copy_from_card()` select a 512-byte ARCnet buffer plus offset through `COM20020_REG_W_ADDR_HI/LO` and transfer bytes with `arcnet_outsb()`/`arcnet_insb()`.
- `com20020_reset()`, `com20020_command()`, `com20020_status()`, `com20020_setmask()`, and `com20020_close()` form the hardware operations called by the generic ARCnet driver.

## Control Flow
Bus code allocates an ARCnet device, fills module or platform parameters in `arcnet_local`, then calls `com20020_check()`. The check path resets the chip, derives `lp->setup`, `lp->setup2`, and `lp->config`, writes the node subregister with a temporary ID, clears reset/config flags, and reads the signature byte from buffer zero. After detection, `com20020_found()` installs callbacks, resolves the station ID if missing, rewrites setup registers, requests the interrupt, and registers the netdev. Opening the netdev sets `TXENcfg` before delegating to `arcnet_open()`. Closing and the hardware close callback clear `TXENcfg`.

At runtime the ARCnet core drives the callback table. TX/RX data movement is done by address-window programming and byte stream I/O. Status combines normal status and diagnostic status into a single integer, allowing the common layer to see `NEWNXTIDflag` and normal ARCnet flags. Promiscuous mode toggles `PROMISCset` in `SUB_SETUP1`; multicast filtering is noted as best-effort and effectively degrades to promiscuous support.

## State and Persistence
The driver keeps hardware programming state in `struct arcnet_local`: `setup`, `setup2`, `config`, timing/backplane fields, `card_flags`, and callback pointers. Persistent kernel-visible state is the registered `net_device`, IRQ ownership, and hardware node ID in COM20020 subregisters. There is no disk persistence. Device state is restored on reset/open by rewriting config/setup registers.

## Dependencies and Integration Points
The file depends on `arcdevice.h` for ARCnet core structures, constants, logging, protocol TX/RX helpers, and interrupt handling, and on `com20020.h` for register definitions. It integrates with the Linux netdev API through `net_device_ops`, with interrupt handling through `request_irq(..., arcnet_interrupt, ...)`, and with bus-specific COM20020 modules via exported symbols.

## Risks
The clock-rate log index is explicitly marked fragile and could index incorrectly if setup values are unexpected. Probing is hardware-timing-sensitive (`udelay`, `mdelay`) and can disrupt the ARCnet token by causing reconfiguration. Multicast filtering is incomplete. Reset validation relies on a single signature byte, and register access ordering is critical because the COM20020 memory window is stateful.

## Test Signals
Useful signals include successful `com20020_check()` status transitions, signature byte validation, IRQ request success, `register_netdev()` success, open/close toggling TX enable, packet movement through `copy_to_card`/`copy_from_card`, correct node ID programming via `ndo_set_mac_address`, and promiscuous flag updates reflected in received traffic. Hardware tests should cover normal and 10 Mbit-capable cards, backplane mode, shared IRQ mode, and reset recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/arcnet/com20020.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/arcnet/com20020.h -->
# sources/distributed-fs/ceph-client/drivers/net/arcnet/com20020.h

## Purpose
`com20020.h` is the COM20020 support interface shared by the chipset core and COM20020 bus drivers. It declares the exported core entry points, defines PCI helper structures used by COM20020 PCI variants, names the COM20020 register layout and bit fields, and provides the inline subaddress selector needed for extended COM20020 registers.

## Important APIs, Types, and Functions
- `com20020_check()`, `com20020_found()`, and `com20020_netdev_ops` are the bus-driver interface to the core implementation.
- `struct com20020_pci_channel_map`, `struct com20020_pci_card_info`, `struct com20020_priv`, and `struct com20020_dev` describe multi-channel PCI cards, LED offsets, per-card private data, and per-netdev LED/device state.
- Register macros map the low I/O region: interrupt mask/status at 0, command/diagnostic status at 1, address registers at 2/3, memory data at 4, subaddress at 5, config at 6, and indexed extra register at 7.
- Bit macros define address-window read mode, diagnostic flags, config reset/TX enable/timeout fields, setup flags such as `PROMISCset`, `P1MODE`, and `SLOWARB`, and subregister IDs.
- `com20020_set_subaddress(struct arcnet_local *lp, int ioaddr, int val)` selects either the low config-encoded subregisters or the extended `COM20020_REG_W_SUBADR` register.

## Control Flow
Bus drivers include this header, allocate or discover a COM20020-backed `net_device`, then call the declared core functions. The inline subaddress helper is used whenever code wants to address COM20020 extra registers. For subaddresses below 4 it mutates the low two bits of `lp->config` and writes `COM20020_REG_W_CONFIG`; for subaddresses 4 and above it writes the dedicated subaddress register. That split is central to COM20020 and COM20022 setup behavior.

## State and Persistence
The header itself has no storage except types. It defines how runtime state is organized: PCI card metadata, LED class devices, misc BAR addresses, list nodes, netdev references, and the `arcnet_local.config` value that is updated by the subaddress helper. No persistent state exists outside live kernel structures and hardware registers.

## Dependencies and Integration Points
It depends on `linux/leds.h` for LED class devices and expects `struct net_device` and `struct arcnet_local` definitions from including translation units. It is an integration point between `com20020.c`, COM20020 PCI/ISA/PCMCIA wrappers, ARCnet core callbacks, and optional LED support for PCI cards.

## Risks
`com20020_set_subaddress()` mutates `lp->config`, so callers must treat config as cached hardware state and avoid racing config writes. The register constants encode hardware layout directly; incorrect use can select the wrong subregister and corrupt node/setup configuration. PCI helper structs assume `PLX_PCI_MAX_CARDS == 2`, so card definitions outside that shape require changes.

## Test Signals
Compile coverage should verify all bus drivers agree on the declarations. Runtime tests should exercise subaddress writes for both low and extended registers, ensure config bits survive subaddress changes, and validate PCI card metadata consumers for multi-channel cards and LED registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/arcnet/com20020.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/arcnet/com20020_cs.c -->
# sources/distributed-fs/ceph-client/drivers/net/arcnet/com20020_cs.c

## Purpose
`com20020_cs.c` is the PCMCIA/Card Services wrapper for COM20020 ARCnet adapters. It allocates the ARCnet netdev, applies module parameters, claims PCMCIA I/O and IRQ resources, enables the device, delegates chipset validation/registration to `com20020_check()` and `com20020_found()`, and handles suspend/resume/removal.

## Important APIs, Types, and Functions
- Module parameters `node`, `timeout`, `backplane`, `clockp`, and `clockm` seed `arcnet_local` defaults before hardware detection.
- `com20020_probe(struct pcmcia_device *p_dev)` allocates `struct com20020_dev` and `alloc_arcdev("")`, initializes ARCnet parameters, sets resource flags, and calls `com20020_config()`.
- `com20020_config()` requests an I/O window, records `dev->base_addr` and `dev->irq`, enables the PCMCIA function, runs chipset check, sets card name/flags, and calls `com20020_found()`.
- `com20020_detach()` unregisters the netdev, frees the separately requested IRQ, disables the PCMCIA device, and frees allocations.
- `com20020_suspend()`/`com20020_resume()` detach or re-reset open devices around power events.
- `com20020_cs_driver` binds probe/remove/suspend/resume to PCMCIA IDs for Contemporary Controls and SoHard cards.

## Control Flow
On PCMCIA match, probe allocates the wrapper and netdev, configures `arcnet_local` from module parameters, sets the desired 8-bit I/O resource width and IRQ enable flag, and enters configuration. Configuration either uses a supplied resource start or scans `0x100..0x3f0` in 16-byte steps with `pcmcia_request_io()`. It then stores the assigned port, validates an IRQ is present, enables the device, and performs COM20020 signature/status checks. If successful it marks the card as 10 Mbit-capable, attaches the device to the PCMCIA device for sysfs lifetime, and lets the core register the netdev. Any failure drops through `com20020_release()`.

Removal reverses the flow: unregister netdev, free the IRQ because the core requested it outside card services, disable the PCMCIA function, then free the ARCnet device and wrapper. Resume pulses the reset bit in `COM20020_REG_W_CONFIG` for open links but otherwise leaves full reinitialization to the networking path.

## State and Persistence
State lives in `p_dev->priv` (`struct com20020_dev`), the allocated `net_device`, `arcnet_local` parameter fields, PCMCIA resource descriptors, and chip registers. The driver has no persistent storage. Suspend state is minimal; resume reasserts hardware reset using cached `lp->config`.

## Dependencies and Integration Points
The file depends on PCMCIA core headers (`pcmcia/cistpl.h`, `pcmcia/ds.h`), ARCnet allocation/helpers from `arcdevice.h`, and COM20020 core functions/registers from `com20020.h`. It integrates with the `module_pcmcia_driver()` mechanism and with the common ARCnet interrupt/netdev path through `com20020_found()`.

## Risks
The I/O scan is legacy ISA-style and assumes 16-byte spacing. `com20020_detach()` assumes `link->priv` and `info->dev` are valid after successful probe. IRQ lifetime is split between this wrapper and COM20020 core, so failure paths must remain aligned with whether `com20020_found()` requested the IRQ. Resume performs a lightweight reset only; unusual cards may require full setup replay.

## Test Signals
Relevant tests are PCMCIA ID matching, resource assignment with fixed and scanned I/O ports, failure cleanup at each allocation/configuration step, successful COM20020 check/found registration, suspend/resume with an open interface, and card removal while down and while previously opened. Hardware smoke tests should confirm the station ID, IRQ, and 10 Mbit setup logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/arcnet/com20020_cs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/arcnet/com9026.h -->
# sources/distributed-fs/ceph-client/drivers/net/arcnet/com9026.h

## Purpose
`com9026.h` is a compact register-definition header for COM9026/COM90xx ARCnet controllers. It gives the legacy COM90xx memory-mapped and I/O-mapped drivers symbolic names for the controller's status, command, config, reset, station ID, and buffer-address/data ports.

## Important APIs, Types, and Functions
The header declares no functions or data structures. Its API is the set of register offset macros:
- `COM9026_REG_W_INTMASK` / `COM9026_REG_R_STATUS` at offset 0.
- `COM9026_REG_W_COMMAND` and `COM9026_REG_R_STATION` at offset 1, depending on access path/context.
- `COM9026_REG_RW_CONFIG` at offset 2.
- `COM9026_REG_R_RESET` at offset 8, where a read triggers reset.
- `COM9026_REG_RW_MEMDATA` at offset 12 and address low/high registers at 14/15 for I/O-mapped buffer access.

## Control Flow
COM90xx drivers include this header and use the offsets in their probe, reset, status, interrupt-mask, and buffer-copy routines. The memory-mapped driver also reads the station ID and signature through mapped memory using these offsets. The I/O-mapped driver programs address registers and streams bytes through the data register.

## State and Persistence
There is no software state in the header. The macros describe volatile hardware state exposed through I/O ports or shared memory. Persistence is limited to the hardware registers and controller buffer memory.

## Dependencies and Integration Points
This header is consumed by `com90xx.c` and `com90io.c`, and indirectly aligns those drivers with ARCnet constants from `arcdevice.h` such as command bits, status flags, and buffer-size assumptions.

## Risks
Because offsets are bare hardware ABI, any wrong constant can cause destructive I/O. `COM9026_REG_W_COMMAND` and `COM9026_REG_R_STATION` sharing offset 1 is context-sensitive and easy to misuse. The reset register's read side effect must be respected by probes and diagnostics.

## Test Signals
The main validation signal is successful COM90xx/COM90io probe and reset on real hardware or an emulator. Tests should confirm status reads, reset side effects, station ID reads, config writes, and memory data transfers through the defined offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/arcnet/com9026.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/arcnet/com90io.c -->
# sources/distributed-fs/ceph-client/drivers/net/arcnet/com90io.c

## Purpose
`com90io.c` supports legacy COM90xx ARCnet cards whose packet buffers are accessed through I/O-mapped address/data registers rather than directly mapped shared memory. It requires an I/O base address, optionally auto-detects IRQ, validates the card signature, registers a single ARCnet netdev, and implements ARCnet hardware callbacks using programmed I/O.

## Important APIs, Types, and Functions
- `com90io_probe()` validates a specified I/O address, resets the device, checks status flags and signature byte, configures I/O-mapped 8-bit mode, and probes IRQ when none is supplied.
- `com90io_found()` requests the IRQ and I/O region for runtime, installs `arcnet_local.hw` callbacks, reads the station ID, and registers the netdev.
- `get_buffer_byte()`, `get_whole_buffer()`, and `put_whole_buffer()` implement indexed access through COM9026 address and memory-data registers.
- `com90io_reset()`, `com90io_command()`, `com90io_status()`, `com90io_setmask()`, `com90io_copy_to_card()`, and `com90io_copy_from_card()` are the callback table used by the ARCnet core.
- Module parameters `io`, `irq`, and `device` and non-module `com90io=` setup configure the single supported device.

## Control Flow
Initialization allocates an ARCnet device, applies module parameters, normalizes IRQ 2 to 9, and calls the probe. Probe refuses autoprobe without an I/O address, claims the I/O region temporarily, checks for empty status `0xff`, resets by reading `COM9026_REG_R_RESET`, waits, validates post-reset flags, clears reset/config flags, writes I/O-map config, and verifies `TESTvalue` at buffer offset zero. If no IRQ is set, it enables the `NORXflag` interrupt under `probe_irq_on/off()` to discover the line. It then releases the temporary region and calls `com90io_found()`.

Runtime copy callbacks compute `bufnum * 512 + offset`, program high/low address registers with `AUTOINCflag`, and transfer bytes through `COM9026_REG_RW_MEMDATA`. Exit unregisters the netdev, clears `IOMAPflag` to leave the card in memory-mapped mode for old drivers, frees IRQ and region, and frees the ARCnet device.

## State and Persistence
The module stores one global `my_dev`. Runtime state includes `dev->base_addr`, `dev->irq`, `lp->config`, and the registered netdev. Hardware state includes COM9026 config, status, reset, interrupt mask, and buffer address pointer. There is no persistent storage.

## Dependencies and Integration Points
The driver depends on `arcdevice.h` for ARCnet core callbacks and flags and `com9026.h` for register offsets. It integrates with module parameters, legacy boot setup, Linux resource management (`request_region`, `request_irq`), and the generic ARCnet interrupt and TX/RX path.

## Risks
The driver explicitly cannot autoprobe I/O-mapped cards without a base address. Auto-IRQ probing can fail or be unsafe on some systems. Indexed I/O access is stateful, so concurrent unexpected access would corrupt transfer offsets, though the ARCnet core normally serializes hardware operations. The exit path assumes `my_dev` exists after successful init.

## Test Signals
Test evidence includes correct rejection of missing/empty I/O addresses, status and signature validation, IRQ autoprobe or configured IRQ operation, station ID read from buffer byte 1, successful netdev registration, TX/RX data copied through I/O ports, reset recovery, and cleanup restoring memory-mapped mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/arcnet/com90io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/arcnet/com90xx.c -->
# sources/distributed-fs/ceph-client/drivers/net/arcnet/com90xx.c

## Purpose
`com90xx.c` is the normal shared-memory COM90xx ARCnet chipset driver. It can scan legacy I/O ports and shared memory windows, match a reset controller to its buffer memory, detect memory mirrors, register ARCnet devices, and implement the ARCnet hardware callbacks using `memcpy_toio()`/`memcpy_fromio()` over mapped card memory.

## Important APIs, Types, and Functions
- `com90xx_probe()` performs the five-stage legacy probe across possible I/O ports and shared memory addresses.
- `check_mirror()` tests whether adjacent shared-memory windows mirror the same card buffer.
- `com90xx_found()` allocates and initializes a netdev for a matched port/IRQ/shared-memory tuple, reserves the full mirrored memory range, maps it, reads station ID, installs callbacks, and registers the device.
- `com90xx_reset()`, `com90xx_command()`, `com90xx_status()`, `com90xx_setmask()`, `com90xx_copy_to_card()`, and `com90xx_copy_from_card()` are the ARCnet hardware callback set.
- Global `cards[16]` and `numcards` track registered devices for module exit.

## Control Flow
Probe builds candidate port and shared-memory lists from module parameters or defaults (`0x200..0x3f0` ports and `0xA0000..0xFF800` memory in 2 KiB steps). Stage 1 filters reserved or empty ports and resets plausible controllers. Stage 2 waits for reset completion. Stage 3 maps candidate memory windows, checks the ARCnet signature, verifies writability, and marks mirrors by overwriting the signature. Stage 5 validates controller status, clears reset/config flags, optionally probes IRQ, resets the controller again, and finds which shared-memory window regained the signature. A successful pair is passed to `com90xx_found()`.

`com90xx_found()` allocates a device, determines the real mirrored memory range by walking backward and forward with `check_mirror()`, reserves and maps that entire range, requests IRQ, fills the ARCnet callback table, reads the station ID, registers the netdev, and stores it in `cards`. Runtime packet transfers directly copy to/from `lp->mem_start + bufnum * 512 + offset`. Exit iterates registered cards, unregistering netdevs, freeing IRQs, unmapping memory, releasing I/O and memory regions, and freeing devices.

## State and Persistence
Runtime state is tracked in `cards[]`, `numcards`, `dev->base_addr`, `dev->irq`, `dev->mem_start/end`, and `arcnet_local.mem_start`. Hardware state includes reset/config/status registers and shared packet memory. No disk persistence exists. The probe mutates candidate shared memory and later restores `TESTvalue` for leftover windows.

## Dependencies and Integration Points
The file depends on `arcdevice.h`, `com9026.h`, Linux resource APIs, I/O mapping APIs, module parameters, boot setup parsing, and the generic ARCnet core. It is the memory-mapped counterpart to `com90io.c`.

## Risks
Legacy probing touches broad low-memory ranges and I/O ports, so false positives or platform conflicts are possible despite resource checks. The probe logs one `arc_cont()` line using `*p` in the match print path where the loop variable is not the matched pointer, which is suspicious for diagnostics. Mirror detection depends on `TESTvalue` behavior and can mis-size unusual cards. `cards[16]` bounds the number of registered cards.

## Test Signals
Important signals are each probe stage pruning expected candidates, successful status/reset clearing, IRQ detection, correct shared-memory pairing, mirror range sizing, station ID read, netdev registration, packet transfer by mapped memory, and clean multi-card module exit. Tests should include parameter-specified and scanned configurations, no-card systems, mirrored-memory cards, and reset failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/arcnet/com90xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/arcnet/rfc1051.c -->
# sources/distributed-fs/ceph-client/drivers/net/arcnet/rfc1051.c

## Purpose
`rfc1051.c` implements ARCnet RFC1051 "simple standard" encapsulation for IP and ARP. It registers an `ArcProto` with the ARCnet core, translates between ARCnet protocol IDs and Ethernet protocol numbers, builds ARCnet soft headers, receives unsplit packets, and prepares packets for transmission in COM90xx/COM20020 buffers.

## Important APIs, Types, and Functions
- `rfc1051_proto` advertises suffix `s`, MTU `XMTU - RFC1051_HDR_SIZE`, IP capability, and callbacks for receive, header build, and TX preparation.
- `arcnet_rfc1051_init()` maps `ARC_P_IP_RFC1051` and `ARC_P_ARP_RFC1051` to this protocol and optionally becomes the broadcast protocol.
- `type_trans()` pulls ARCnet/RFC1051 headers from an skb and returns `ETH_P_IP` or `ETH_P_ARP`.
- `rx()` allocates an skb, copies already-read header data plus remaining card bytes, sets protocol, and submits via `netif_rx()`.
- `build_header()` pushes ARCnet hard/soft headers and chooses RFC1051 protocol IDs.
- `prepare_tx()` calculates ARCnet buffer offsets, writes hard and soft headers/data to the card, and records `lp->lastload_dest`.

## Control Flow
On module load, protocol map entries for RFC1051 IP and ARP point at `rfc1051_proto`; unload unregisters it. For RX, the ARCnet core supplies a partial packet header and buffer number. The driver computes the payload offset from packet length (`512 - length` for long frames, `256 - length` for short frames), allocates an skb sized for the ARCnet header plus payload, copies the cached header, fetches any remaining payload from the card via `lp->hw.copy_from_card()`, translates the protocol, and hands the skb to the network stack.

For TX, upper layers call `build_header()` to prepend the ARCnet header and RFC1051 proto byte. `prepare_tx()` removes the hard-header size from the length, clamps unexpected oversized frames to `XMTU`, selects the short/long/exception offset encoding, writes the hard header at buffer offset 0, writes the soft header and payload at the selected offset, and returns complete.

## State and Persistence
The module keeps no per-flow state and does not fragment/reassemble. It updates netdev stats on unsupported protocols or allocation failure and writes `lp->lastload_dest` for common ARCnet transmit tracking. Persistence is only the registered protocol map while the module is loaded.

## Dependencies and Integration Points
It depends on ARCnet core globals (`arc_proto_map`, `arc_bcast_proto`, `arc_proto_default`), `struct ArcProto`, `struct archdr`, hardware copy callbacks, skb APIs, and Linux protocol constants. It is a protocol-layer module above the hardware drivers in this work item.

## Risks
Only IP and ARP are supported; other protocols increment RX/TX errors. No split-packet support exists, so MTU is lower than RFC1201. The `IFF_LOOPBACK`/`IFF_NOARP` path broadcasts rather than deriving destination from IP, and a FIXME notes incomplete RFC1051 no-ARP behavior. RX trusts length and header shape supplied by the ARCnet core.

## Test Signals
Tests should verify module registration/unregistration, protocol translation for IP/ARP, rejection of unsupported protocols, correct skb `pkt_type` for broadcast/promiscuous other-host traffic, short and long frame offset encoding, card copy offsets, and successful ping/ARP exchange using RFC1051 encapsulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/arcnet/rfc1051.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/arcnet/rfc1201.c -->
# sources/distributed-fs/ceph-client/drivers/net/arcnet/rfc1201.c

## Purpose
`rfc1201.c` implements the standard ARCnet RFC1201 encapsulation. Compared with RFC1051 it supports more protocol IDs, a 1500-byte MTU, exception packets, and split-packet transmit/reassembly. It registers an `ArcProto` with callbacks for header construction, receive, initial TX preparation, and continued segmented TX.

## Important APIs, Types, and Functions
- `rfc1201_proto` advertises suffix `a`, MTU 1500, IP capability, and callbacks `rx`, `build_header`, `prepare_tx`, and `continue_tx`.
- `arcnet_rfc1201_init()` maps IP, IPv6, ARP, RARP, IPX, and Novell echo ARCnet protocol IDs to this protocol.
- `type_trans()` maps ARCnet RFC1201 proto IDs to Linux Ethernet protocol IDs and sets broadcast/other-host packet type.
- `rx()` handles unsplit packets, exception packets, split-packet start/continuation/completion, ARP source correction, duplicate/out-of-order handling, and skb delivery.
- `load_pkt()`, `prepare_tx()`, and `continue_tx()` write unsplit or segmented packets into ARCnet card buffers.

## Control Flow
Receive begins by deriving the card-buffer payload offset from length. Exception packets (`split_flag == 0xff`) skip a 4-byte compatibility prefix and reload the soft header. Unsplit packets abort any in-progress assembly from the same source, allocate an skb, copy remaining payload, repair DOS-originated ARP sender hardware address when zero, translate protocol, and deliver. Split packets are tracked per source station in `lp->rfc1201.incoming[saddr]`. A first segment allocates a large skb for up to 16 segments and stores sequence/count metadata. Later segments must match the expected sequence and segment number; duplicates are ignored, out-of-order packets abort assembly, and the final segment clears state and delivers the assembled skb.

Transmit first builds an ARCnet/RFC1201 header with an incrementing sequence. `prepare_tx()` sends packets up to `XMTU` immediately through `load_pkt()`. Larger packets initialize `lp->outgoing` with data length, segment count, and segment number and return 0 so the ARCnet core calls `continue_tx()` for each segment. `continue_tx()` positions a new soft header before each chunk, sets first/continuation split flags, writes the segment through `load_pkt()`, and reports completion after the last segment.

## State and Persistence
State lives in `arcnet_local.rfc1201.sequence`, `incoming[station]` reassembly slots, `aborted_seq`, and the common `lp->outgoing` transmit continuation state. The module updates netdev stats for malformed, unsupported, duplicate, missing, length, and allocation failure cases. No disk persistence exists.

## Dependencies and Integration Points
The module depends on ARCnet core protocol maps, hardware copy callbacks, skb allocation and delivery, and Linux protocol constants. It integrates tightly with the generic ARCnet TX scheduler because split transmit requires `prepare_tx()` to return incomplete and `continue_tx()` to be called with subsequent hardware buffers.

## Risks
Split reassembly is stateful and sensitive to sequence ordering, duplicates, and memory pressure. The maximum of 16 segments protects allocation but drops larger advertised assemblies. Some error counters use CRC/frame/missed categories for protocol-level anomalies, which can complicate diagnostics. ARP source repair is legacy compatibility behavior that mutates received packets.

## Test Signals
Test coverage should include module protocol registration, IPv4/IPv6/ARP/RARP/IPX translation, unsplit RX/TX, exception-packet handling, split transmit across multiple buffers, split receive completion, duplicate continuation, out-of-order abort, sequence mismatch, ARP sender repair, allocation failure counters, and broadcast/promiscuous packet-type handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/arcnet/rfc1201.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/bareudp.c -->
# sources/distributed-fs/ceph-client/drivers/net/bareudp.c

## Purpose
`bareudp.c` implements the BareUDP virtual tunnel netdevice. BareUDP encapsulates payloads such as MPLS, NSH, IP, or other configured ethertypes directly in UDP without an inner Ethernet header. The driver is controlled through rtnetlink, keeps per-netns device lists, creates one UDP tunnel socket per opened device, decapsulates received UDP packets into the configured protocol, and transmits packets using metadata supplied by the tunnel infrastructure.

## Important APIs, Types, and Functions
- `struct bareudp_net` stores the per-network-namespace device list.
- `struct bareudp_conf` captures netlink configuration: destination UDP port, ethertype, source-port minimum, and multiprotocol mode.
- `struct bareudp_dev` is the netdev private state: netns, netdev, ethertype, port, source port range, multiprotocol flag, RCU-protected socket, list node, and GRO cells.
- `bareudp_udp_encap_recv()` is the UDP tunnel receive callback.
- `bareudp_xmit()`, `bareudp_xmit_skb()`, and `bareudp6_xmit_skb()` implement IPv4/IPv6 transmit encapsulation from `skb_tunnel_info()`.
- `bareudp_fill_metadata_dst()` resolves route/source-port metadata for collect-metadata users.
- `bareudp_newlink()`, `bareudp_dellink()`, `bareudp_fill_info()`, and `bareudp_link_ops` expose rtnetlink creation, deletion, and introspection.
- `bareudp_net_ops` registers per-netns initialization and cleanup.

## Control Flow
Module init registers pernet state first, then rtnl link ops. Creating a link validates required netlink attributes (`PORT`, `ETHERTYPE`), rejects unsupported multiprotocol combinations, prevents duplicate ports in the same netns, registers the netdevice, and links it into the namespace list. Opening the device creates an IPv6 UDP socket when IPv6 is available, otherwise IPv4, enables UDP GSO, installs UDP tunnel callbacks, and stores the socket via RCU. Stopping clears the socket pointer, waits for network readers with `synchronize_net()`, and releases the UDP tunnel socket.

Receive starts in the UDP encap callback. It identifies outer address family, determines the inner protocol from configured ethertype plus optional multiprotocol inference (IPv4/IPv6 payload version or MPLS unicast/multicast based on outer destination), pulls the UDP header using `iptunnel_pull_header()`, attaches tunnel metadata, resets skb headers, validates inner network header availability, decapsulates ECN, and submits the skb through `gro_cells_receive()`. Transmit requires a valid configured inner protocol and `IP_TUNNEL_INFO_TX` metadata. The IPv4/IPv6 transmit helpers choose a UDP source port, resolve a route, check PMTU, scrub cross-netns packets, ensure headroom, handle offloads, and emit through `udp_tunnel_xmit_skb()` or `udp_tunnel6_xmit_skb()`.

## State and Persistence
Persistent runtime state is per-netns only: the list of devices and each device's config. Socket state exists only while the netdev is open and is protected by RCU. GRO cell state is initialized in `ndo_init` and destroyed in `ndo_uninit`. Stats are per-CPU device stats plus explicit error counters. There is no disk persistence.

## Dependencies and Integration Points
BareUDP depends on rtnetlink, pernet operations, UDP tunnel helpers, IP tunnel metadata, route lookup, ECN helpers, GRO cells, skb offload handling, and optional IPv6. User space integrates through `ip link add type bareudp ...` using `IFLA_BAREUDP_*` attributes. Datapath integration expects collect-metadata tunnel users to attach `struct ip_tunnel_info`.

## Risks
Transmit drops packets without tunnel metadata, with protocols outside configured/multiprotocol rules, or when the socket has not been opened. Multiprotocol MPLS receive infers unicast/multicast from the outer destination address, so policy errors can drop traffic. The duplicate-port check only compares ports, not ethertype, making port exclusive per netns. ECN errors may be logged unless the module parameter disables them. Correct RCU socket lifetime is critical around stop/uninit.

## Test Signals
Tests should verify netlink validation, duplicate port rejection, multiprotocol mode constraints, IPv4 and IPv6 socket creation, open/stop socket lifetime, receive decapsulation for configured ethertypes, IP multiprotocol IPv4/IPv6 detection, MPLS unicast/multicast behavior, ECN error accounting/logging, GRO delivery stats, metadata route filling, IPv4/IPv6 transmit encapsulation, PMTU behavior, and namespace cleanup deleting all devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/bareudp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/bonding/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/bonding/Makefile

## Purpose
The bonding `Makefile` defines how the Ethernet bonding driver is built. It composes the `bonding.o` module from the core, mode-specific, sysfs, debugfs, netlink, and option source files, and conditionally includes procfs support.

## Important APIs, Types, and Functions
There are no C APIs in this file. The important build variables are:
- `obj-$(CONFIG_BONDING) += bonding.o`, which enables the module/object when bonding is configured.
- `bonding-objs := ...`, listing mandatory component objects including `bond_main.o`, `bond_3ad.o`, `bond_alb.o`, sysfs, debugfs, netlink, and options.
- `proc-$(CONFIG_PROC_FS) += bond_procfs.o` and `bonding-objs += $(proc-y)`, which include procfs support only when configured.

## Control Flow
Kbuild evaluates `CONFIG_BONDING`; if enabled, it links `bonding.o` from the listed objects. `CONFIG_PROC_FS` controls whether `bond_procfs.o` joins that link. This directly determines whether the files researched here (`bond_3ad.c`, `bond_alb.c`, `bond_debugfs.c`) are part of the bonding object.

## State and Persistence
The file has no runtime state. Its persistent effect is build composition: changing object membership changes which features and symbols exist in the built kernel/module.

## Dependencies and Integration Points
The Makefile integrates with Linux Kbuild and the Kconfig symbols `CONFIG_BONDING` and `CONFIG_PROC_FS`. It relies on each listed object sharing internal bonding headers and symbols.

## Risks
Omitting a mode object would silently remove required mode functionality or cause unresolved references from `bond_main.o`/options/netlink. Adding conditional objects incorrectly can break built-in versus module builds. The debugfs object is always listed, but its C file compiles no-op functions when debugfs/netns constraints are not met.

## Test Signals
Build tests should cover `CONFIG_BONDING=m`, `CONFIG_BONDING=y`, and disabled bonding, with `CONFIG_PROC_FS` both enabled and disabled. Link success and expected symbols/modes in the resulting module are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/bonding/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/bonding/bond_3ad.c -->
# sources/distributed-fs/ceph-client/drivers/net/bonding/bond_3ad.c

## Purpose
`bond_3ad.c` implements IEEE 802.3ad/LACP mode for the bonding driver. It maintains actor/partner port state, sends and receives LACPDU and marker frames, groups ports into aggregators, selects the active aggregator according to policy, drives the LACP receive/periodic/mux/transmit/churn state machines, reacts to link and speed changes, manages carrier state, and exposes LACP statistics.

## Important APIs, Types, and Functions
- State-machine helpers include `ad_rx_machine()`, `ad_periodic_machine()`, `ad_mux_machine()`, `ad_tx_machine()`, `ad_churn_machine()`, `ad_port_selection_logic()`, and `ad_agg_selection_logic()`.
- Packet functions `ad_lacpdu_send()`, `ad_marker_send()`, `bond_3ad_lacpdu_recv()`, and `bond_3ad_rx_indication()` implement LACP/marker frame I/O.
- Aggregator and port lifecycle functions include `bond_3ad_initialize()`, `bond_3ad_bind_slave()`, `bond_3ad_unbind_slave()`, `ad_initialize_port()`, `ad_initialize_agg()`, and `ad_clear_agg()`.
- Change handlers include `bond_3ad_adapter_speed_duplex_changed()`, `bond_3ad_handle_link_change()`, `bond_3ad_update_ad_actor_settings()`, `bond_3ad_update_lacp_rate()`, and `bond_3ad_update_lacp_active()`.
- Status/stat APIs include `bond_3ad_set_carrier()`, `bond_3ad_get_active_agg_info()`, `bond_3ad_stats_size()`, and `bond_3ad_stats_fill()`.

## Control Flow
Bond initialization records actor system priority/MAC and starts an aggregator selection timer. When a slave is bound, its port is initialized with actor state, keys derived from user key, speed, and duplex, then disabled until state machines enable it. The delayed work handler `bond_3ad_state_machine_handler()` runs every `ad_delta_in_ticks`, advances the aggregator selection timer, optionally selects the active aggregator, then for each slave runs RX timeout processing, periodic LACP scheduling, port selection, mux transitions, LACP transmit, and churn detection. If mux or aggregator selection changed usable slaves, it rearms slave-array work and may notify RTNL.

Receive paths consume only LACP destination multicast frames with protocol `PKT_TYPE_LACPDU`. LACPDU payloads enter `ad_rx_machine()` under `mode_lock`; marker frames are answered or counted. The RX machine records partner state, detects loopback, manages current/expired/defaulted states, and updates `AD_PORT_MATCHED`, `AD_PORT_SELECTED`, and synchronization. The mux machine transitions ports between detached, waiting, attached, collecting, distributing, and collecting/distributing states, setting bonding slave active/inactive flags. Aggregator selection chooses a best active LAG based on individual/partner status and `ad_select` policy (`stable`, `bandwidth`, `count`, or `prio`).

## State and Persistence
State is stored in `BOND_AD_INFO(bond)` and `SLAVE_AD_INFO(slave)`: system identity, aggregator identifiers, timers, stats, per-port state bits, actor/partner params, selected aggregator pointer, LACPDU template, churn counters, and active flags. Timers are software counters in delayed work ticks. There is no disk persistence; state is rebuilt from bond parameters and slave link characteristics.

## Dependencies and Integration Points
The file depends on bonding internals (`struct bonding`, `struct slave`, mode locks, slave-array updates, carrier helpers), `net/bond_3ad.h` protocol structures, netdev/skb APIs, ethtool speed/duplex values, RCU iteration over slaves, RTNL notifications, and netlink stat filling. It integrates with `bond_main.c` receive handling, mode initialization, link monitoring, sysfs/netlink option updates, and transmit eligibility through slave flags.

## Risks
The implementation is concurrency-sensitive: delayed work, receive handler, link changes, and unbind paths coordinate with `mode_lock`, RCU, and RTNL. Aggregator selection assumes it is called with the first aggregator; a FIXME documents that this API shape is fragile. Incorrect speed/duplex reporting can alter actor keys and restart LACP. Loopback detection disables useful partner updates by returning early. Marker response support is intentionally minimal. Carrier depends on active aggregator and `min_links`, so stale aggregator state can affect link reporting.

## Test Signals
Strong tests include LACPDU TX/RX counters, loopback frame rejection, marker response behavior, aggregator formation with matching actor/partner keys, active aggregator selection under all `ad_select` policies, `min_links` carrier behavior, link up/down and speed/duplex transitions, lacp rate/active option updates, slave bind/unbind while traffic is running, churn counters after synchronization failure, netlink stats encoding, and switch interoperability with active and passive LACP peers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/bonding/bond_3ad.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/bonding/bond_alb.c -->
# sources/distributed-fs/ceph-client/drivers/net/bonding/bond_alb.c

## Purpose
`bond_alb.c` implements bonding transmit load balancing (TLB) and adaptive load balancing (ALB, which adds receive load balancing through ARP manipulation). It assigns transmit flows to slaves, tracks per-slave load, periodically rebalances, manages per-slave MAC addresses, sends learning packets to update switches, rewrites ARP sender MACs for receive balancing, and maintains receive-client hash tables for ALB mode.

## Important APIs, Types, and Functions
- TLB functions include `tlb_initialize()`, `tlb_deinitialize()`, `tlb_choose_channel()`, `tlb_get_least_loaded_slave()`, and `tlb_clear_slave()`.
- RLB functions include `rlb_initialize()`, `rlb_deinitialize()`, `rlb_arp_recv()`, `rlb_arp_xmit()`, `rlb_choose_channel()`, `rlb_update_rx_clients()`, `rlb_rebalance()`, and hash-table list helpers.
- MAC/learning helpers include `alb_send_learning_packets()`, `alb_set_slave_mac_addr()`, `alb_swap_mac_addr()`, `alb_fasten_mac_swap()`, `alb_handle_addr_collision_on_attach()`, and `alb_change_hw_addr_on_detach()`.
- Exported bonding hooks include `bond_alb_initialize()`, `bond_alb_deinitialize()`, `bond_tlb_xmit()`, `bond_alb_xmit()`, `bond_alb_monitor()`, `bond_alb_init_slave()`, `bond_alb_deinit_slave()`, `bond_alb_handle_link_change()`, `bond_alb_handle_active_change()`, `bond_alb_set_mac_address()`, and `bond_alb_clear_vlan()`.

## Control Flow
Initialization allocates the TLB transmit hash table and, for ALB, the RLB receive hash table and ARP receive probe. Transmit selection first excludes broadcast/multicast and special IPv6 neighbor-discovery cases. TLB chooses a slave by `bond_xmit_hash()` and either dynamic load buckets or the prebuilt usable-slave array. ALB adds protocol-specific logic: IPv4/IPv6 unicast traffic is hashed by destination address, while ARP replies/requests may select a receive slave and rewrite ARP source MAC to that slave's address. `bond_do_alb_xmit()` falls back to the current active slave for unbalanced traffic and rewrites Ethernet source MAC when sending on non-active slaves.

RLB tracks clients by destination IP hash and maintains secondary source-IP lists to purge stale entries when another host starts using an IP. ARP replies create or update client assignments; monitor work sends ARP replies to tell clients which slave MAC to use. Periodic monitor work also sends switch learning packets for slaves and upper VLAN/macvlan devices, clears TLB bucket load histories on rebalance intervals, manages temporary promiscuity for disabled slave MAC teaching, runs requested RLB rebalance, and drains delayed client updates/retries.

MAC lifecycle is central. In ALB/RLB, slaves need distinct receive MACs while the current active slave owns the bond MAC. Active-slave changes may swap MAC addresses, clear affected TLB buckets, send learning packets, and schedule RLB client updates. Slave attach handles address collisions before insertion; detach repairs permanent-address ownership. TLB mode uses a lighter software `dev_addr` strategy because receive balancing is not active.

## State and Persistence
State lives in `bond->alb_info`, `SLAVE_TLB_INFO(slave)`, the TLB hash table, and the RLB hash table. Important fields include per-bucket assigned slave, load history, bytes, per-slave bucket list head/load, RLB client IP/MAC/vlan/slave assignments, used/source linked-list indexes, update flags, retry/delay counters, selected RLB receive slave, learning-packet counters, and temporary promiscuity state. There is no disk persistence; state is rebuilt on bond/slave initialization and continuously refreshed by monitor work.

## Dependencies and Integration Points
The file depends on bonding internals, `net/bond_alb.h` structures/constants, ARP creation/transmit helpers, VLAN tagging APIs, IPv6 neighbor discovery parsing, netdev upper-device walking, RTNL for MAC/promiscuity changes, RCU slave iteration, and the bonding workqueue. It integrates with `bond_main.c` mode transmit hooks, link-change hooks, active-slave selection, receive probe dispatch, sysfs/netlink TLB dynamic load option, and debugfs RLB hash inspection.

## Risks
ALB requires lower drivers to support MAC address changes while open; failure returns `-EOPNOTSUPP`. Receive balancing depends on ARP behavior and does not cover non-ARP neighbor discovery in the same way, so IPv6 handling mainly avoids unsafe balancing for ND/DAD. Hash collisions can move older RLB clients back to the primary. Locking is subtle because some helpers require RTNL with no mode lock, while hash-table operations use `mode_lock` with softirqs disabled. Temporary promiscuity cleanup uses `rtnl_trylock()` and can be delayed. Incorrect MAC swaps can disrupt traffic until learning packets/ARP updates converge.

## Test Signals
Tests should cover TLB dynamic and non-dynamic transmit selection, load rebalance counters, multicast/broadcast exclusion, IPv6 ND/DAD exclusion, ALB ARP reply/request rewriting, RLB client hash insertion/update/purge, VLAN-tagged client updates, switch learning packets for bond/VLAN/macvlan uppers, MAC collision handling on attach, MAC repair on detach, active-slave MAC swaps, link down/up clearing and rebalance, promiscuity timeout cleanup, and operation when slave MAC changes fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/bonding/bond_alb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/bonding/bond_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/bonding/bond_debugfs.c

## Purpose
`bond_debugfs.c` provides optional debugfs visibility for bonding, specifically the ALB receive-load-balancing hash table. When debugfs is enabled and network namespaces are not enabled, it creates `/sys/kernel/debug/bonding/<bond>/rlb_hash_table`; otherwise it compiles stub functions so the rest of bonding can call debug hooks unconditionally.

## Important APIs, Types, and Functions
- `bond_debug_rlb_hash_show()` is a seq_file show callback that prints source IP, destination IP, destination MAC, and assigned slave device for each used RLB hash entry.
- `DEFINE_SHOW_ATTRIBUTE(bond_debug_rlb_hash)` builds the file operations.
- `bond_debug_register()`, `bond_debug_unregister()`, and `bond_debug_reregister()` manage per-bond debugfs directories and files.
- `bond_create_debugfs()` and `bond_destroy_debugfs()` manage the top-level `bonding` debugfs directory.
- The `#else` branch defines no-op versions of all public functions when unsupported.

## Control Flow
At bonding module initialization, `bond_create_debugfs()` creates the root directory. Each bond calls register to create a directory named after the bond netdev and a read-only `rlb_hash_table` file. Reading that file checks the bond is in ALB mode, locks `bond->mode_lock`, walks `bond_info->rx_hashtbl_used_head` through `used_next`, and prints assigned client entries. Rename calls attempt `debugfs_change_name()` and fall back to unregistering the old directory on failure. Module cleanup recursively removes the root.

## State and Persistence
The file owns `bonding_debug_root` and each bond stores `bond->debug_dir`. The displayed RLB state is owned by `bond_alb.c`; debugfs only reads it under lock. There is no persistent storage, and debugfs entries disappear on unregister/module exit.

## Dependencies and Integration Points
It depends on `CONFIG_DEBUG_FS`, absence of `CONFIG_NET_NS` for real debugfs support, bonding internals, `bond_alb.h` RLB structures, `seq_file`, and debugfs APIs. It integrates with bonding lifecycle hooks in the main driver.

## Risks
Debugfs is unavailable when network namespaces are enabled, so tooling must tolerate stubs. `debugfs_create_*` failures are not fatal and are only partially reported. The file exposes IPv4 RLB state only; it does not summarize TLB or 802.3ad state. Readers hold `mode_lock` while formatting the table, so very large tables can extend lock hold time.

## Test Signals
Tests should verify root and per-bond directory creation, readable `rlb_hash_table` in ALB mode, empty output in non-ALB modes, correct formatting for assigned and `(none)` clients, safe unregister/reregister, cleanup on module exit, and successful builds with debugfs disabled or netns enabled using the stub functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/bonding/bond_debugfs.c -->
