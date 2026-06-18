# subset-b-004678 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ieee802154/ca8210.c -->
# sources/distributed-fs/ceph-client/drivers/net/ieee802154/ca8210.c

## Purpose
`ca8210.c` is a SoftMAC IEEE 802.15.4 SPI driver for Cascoda CA-8210 radios. It registers an `ieee802154_hw`, translates mac802154 operations into Cascoda SAP commands, handles SPI upstream/downstream exchange, optionally exposes a debugfs test interface, and manages device reset, IRQ, GPIO, and external-clock setup from devicetree.

## Important APIs, types, and functions
Key state lives in `struct ca8210_priv`, with the SPI device, `ieee802154_hw`, workqueues, current TX skb, synchronous command response pointer, completions, retry count, promiscuous flag, and optional `struct ca8210_test`. `struct mac_message` models the over-SPI command payloads. Important paths include `ca8210_spi_transfer()`, `ca8210_spi_exchange()`, `ca8210_rx_done()`, `ca8210_net_rx()`, `ca8210_skb_tx()`, `ca8210_skb_rx()`, and the `ca8210_phy_ops` callbacks.

## Control flow
Probe allocates the hw/private object, initializes completions and workqueues, sets debugfs if configured, obtains platform data, initializes reset/IRQ GPIOs, hard-resets the chip, applies TDME register initialization, optionally enables/registers an exported fixed clock, then calls `ieee802154_register_hw()`. TX builds an MCPS-DATA request from the skb header, starts async SPI, and completes only after `SPI_MCPS_DATA_CONFIRM`. RX comes through the IRQ-triggered dummy SPI read, `ca8210_rx_done()`, and `ca8210_skb_rx()`.

## State and persistence
Runtime state is in RAM only: completions synchronize SPI and synchronous SAP commands, `last_dsn` suppresses duplicate received frames, `nextmsduhandle` tracks async TX confirms, and debugfs buffers upstream messages in a kfifo. No persistent storage is written.

## Dependencies and integration points
The file depends on SPI, GPIO descriptors, debugfs, kfifo, workqueues, clk provider APIs, mac802154/cfg802154, and devicetree properties such as reset/irq GPIOs and optional external clock settings. The debugfs path can pass raw Cascoda API commands to userspace.

## Risks and test signals
High-risk areas are async/sync SPI races around `sync_command_response`, retry handling that can call remove after repeated NACKs, skb lifetime during async TX, len-field validation in RX/debugfs, and probe error cleanup after partial initialization. Test signals include module probe/remove on real or emulated SPI, reset wakeup timeout behavior, mac802154 TX confirm/error paths, duplicate DSN RX suppression, promiscuous mode RX framing, debugfs read/write/ioctl behavior, and external-clock enable/disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ieee802154/ca8210.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ieee802154/cc2520.c -->
# sources/distributed-fs/ceph-client/drivers/net/ieee802154/cc2520.c

## Purpose
`cc2520.c` is a SPI mac802154 driver for the TI CC2520 2.4 GHz IEEE 802.15.4 transceiver, with optional CC2591 amplifier support. It configures radio registers, handles FIFO-based TX/RX, exposes mac802154 operations, and wires FIFOP/SFD GPIO interrupts into packet receive and transmit completion.

## Important APIs, types, and functions
`struct cc2520_private` stores SPI, hw, a shared command buffer protected by `buffer_mutex`, TX synchronization flags, amplifier mode, FIFO GPIO, IRQ work, and `tx_complete`. Low-level helpers include `cc2520_cmd_strobe()`, `cc2520_get_status()`, register/RAM read/write helpers, `cc2520_write_txfifo()`, and `cc2520_read_rxfifo()`. The mac802154 ops are `cc2520_start()`, `cc2520_stop()`, `cc2520_tx()`, `cc2520_rx()`, ED/channel/filter/txpower/promiscuous setters.

## Control flow
Probe allocates private state, reads the `amplified` property, requests FIFO/CCA/FIFOP/SFD/reset/vreg GPIOs, powers and resets the chip, runs `cc2520_hw_init()`, registers FIFOP and SFD IRQs, and registers an `ieee802154_hw`. TX flushes the TX FIFO, writes the length and payload, checks underflow, marks `is_tx`, strobes `STXONCCA`, then waits for SFD ISR completion. FIFOP ISR schedules work that reads an RX frame and flushes RXFIFO twice.

## State and persistence
The driver has no persistent state. Runtime state includes the shared SPI buffer, `is_tx`, `promiscuous`, completion state, and programmed hardware filter/RAM registers for PAN, short, and extended addresses.

## Dependencies and integration points
It integrates with SPI, GPIO descriptors, IRQ/workqueue APIs, CRC-CCITT for promiscuous TX FCS generation, mac802154, and cfg802154. Device tree/firmware properties supply GPIOs and optional amplifier mode.

## Risks and test signals
Important risks are synchronous wait interruption/deadlock if SFD completion is missed, RX length handling after corrupted frames, shared buffer use across work and mac802154 calls, missing error propagation in some filter writes, and different behavior when AUTOCRC is disabled in promiscuous mode. Tests should cover probe GPIO failures, amplified and non-amplified register initialization, TX underflow handling, SFD completion, FIFOP RX path, CRC_OK filtering, promiscuous TX/RX, address filter writes, and channel/txpower validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ieee802154/cc2520.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ieee802154/fakelb.c -->
# sources/distributed-fs/ceph-client/drivers/net/ieee802154/fakelb.c

## Purpose
`fakelb.c` implements a deprecated in-kernel IEEE 802.15.4 loopback simulator. It creates a configurable number of fake mac802154 PHYs and forwards transmitted frames to other running fake PHYs on the same page/channel.

## Important APIs, types, and functions
`struct fakelb_phy` holds an `ieee802154_hw`, current page/channel, suspended state, and list nodes for all PHYs and currently-ifup PHYs. The mac802154 operations are `fakelb_hw_xmit()`, `fakelb_hw_ed()`, `fakelb_hw_channel()`, `fakelb_hw_start()`, `fakelb_hw_stop()`, and a no-op promiscuous setter. Module setup is handled by `fakelb_init_module()`, `fakelb_probe()`, `fakelb_add_one()`, and teardown by `fakelb_remove()`/`fakelb_del()`.

## Control flow
Module init registers a platform device and platform driver. Probe creates `numlbs` fake radios, initializes broad channel support across many 802.15.4 pages, registers each hw, and links it into `fakelb_phys`. Start adds a PHY to the ifup list; stop removes it. Transmit walks the ifup list under a read lock, clones the skb for every peer with matching page/channel, injects clones with `ieee802154_rx_irqsafe()`, then completes the original transmit.

## State and persistence
State is entirely in RAM: global PHY lists, current channel/page, and suspended/ifup membership. There is no configuration persistence beyond the module parameter `numlbs`.

## Dependencies and integration points
The file integrates with platform devices, mac802154/cfg802154, netdevice/skbuff APIs, module parameters, mutexes, and rwlocks. It is functionally replaced by `mac802154_hwsim`.

## Risks and test signals
Risks include deprecated behavior diverging from real filtering, no real promiscuous semantics, global list teardown interactions while devices are up, and possible skb clone allocation failure silently dropping peer delivery. Tests should validate module load/unload, `numlbs` creation, channel isolation, start/stop list membership, multi-peer loopback delivery, and removal while interfaces are down/up.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ieee802154/fakelb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ieee802154/mac802154_hwsim.c -->
# sources/distributed-fs/ceph-client/drivers/net/ieee802154/mac802154_hwsim.c

## Purpose
`mac802154_hwsim.c` is the newer IEEE 802.15.4 software radio simulator for mac802154. It creates simulated radios, forwards frames over directed graph edges, supports configurable link LQI, and exposes a generic-netlink control API for adding/removing radios and edges.

## Important APIs, types, and functions
State is split into `struct hwsim_phy`, RCU-protected `struct hwsim_pib`, directed `struct hwsim_edge`, and RCU-protected `struct hwsim_edge_info`. mac802154 operations are `hwsim_hw_xmit()`, `hwsim_hw_receive()`, ED/channel/filter/start/stop/promiscuous setters. Netlink commands are implemented by `hwsim_new_radio_nl()`, `hwsim_del_radio_nl()`, `hwsim_get_radio_nl()`, `hwsim_dump_radio_nl()`, `hwsim_new_edge_nl()`, `hwsim_del_edge_nl()`, and `hwsim_set_edge_lqi()`.

## Control flow
Module init registers the generic-netlink family, creates a platform device, and registers the platform driver. Probe creates two initial radios and subscribes them to one another. TX reads the sender PIB under RCU, walks outgoing edges, skips suspended endpoints, matches page/channel, clones the skb, and calls `hwsim_hw_receive()` on the endpoint. Receive optionally enforces level-4 IEEE 802.15.4 frame-field filtering before injecting into mac802154.

## State and persistence
All simulator topology and radio state is volatile. Radios have monotonically assigned IDs, a current PIB, suspended flag, and edge list. PIB and edge info updates allocate replacement objects and publish them with RCU.

## Dependencies and integration points
The driver integrates mac802154/cfg802154 with generic netlink, rtnetlink context for PIB updates, RCU, platform device infrastructure, skbuff cloning, and multicast notifications on a `config` group.

## Risks and test signals
Risks include RCU/list mutation correctness, validation gaps in nested netlink attributes, typo-sensitive ABI constants from the header, frame filtering divergence from hardware, and topology cleanup when deleting radios referenced by edges. Test signals include initial two-radio connectivity, netlink add/delete/get/dump radio, edge add/delete/set-LQI, channel filtering, promiscuous vs filtered receive, multicast notifications, and repeated module unload under active topology changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ieee802154/mac802154_hwsim.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ieee802154/mac802154_hwsim.h -->
# sources/distributed-fs/ceph-client/drivers/net/ieee802154/mac802154_hwsim.h

## Purpose
`mac802154_hwsim.h` defines the user/kernel generic-netlink ABI for the mac802154 hwsim radio simulator. It is consumed by `mac802154_hwsim.c` and by userspace tools that manage simulated radios and edges.

## Important APIs, types, and functions
The header exports three enum families: `MAC802154_HWSIM_CMD_*` for radio/edge commands, `MAC802154_HWSIM_ATTR_*` for top-level radio attributes, and `MAC802154_HWSIM_EDGE_ATTR_*` for nested edge attributes. Command semantics include get/new/delete radio and get/set/new/delete edge. Attributes identify radio IDs, nested edge descriptions, edge endpoint IDs, and edge LQI.

## Control flow
There is no executable control flow in the header. At runtime, `mac802154_hwsim.c` maps these constants into generic-netlink policy tables and operation dispatch. Requests use `MAC802154_HWSIM_ATTR_RADIO_ID` plus optional nested `MAC802154_HWSIM_ATTR_RADIO_EDGE`; dumps and replies return nested `MAC802154_HWSIM_ATTR_RADIO_EDGES` entries.

## State and persistence
The header stores no state. It defines stable numeric ABI values, so changes are persistent in the compatibility sense: reordering or renaming constants can break userspace.

## Dependencies and integration points
It is a kernel-private header in the driver folder but effectively describes a netlink ABI shared with userspace. It is directly included by the hwsim implementation and indirectly tied to generic-netlink policy validation.

## Risks and test signals
The visible risk is ABI typo/constant drift: `MAC802154_HWSIM_CMD_MAX` uses `__MAC802154_HWSIM_MAX`, which does not match the declared `__MAC802154_HWSIM_CMD_MAX`. If compiled as-is in a strict path using that macro, it would fail or reference an undefined symbol. Tests should include driver compilation with warnings enabled, netlink command enumeration checks, userspace tool compatibility, and nested attribute encode/decode round trips for radio and edge state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ieee802154/mac802154_hwsim.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ieee802154/mcr20a.c -->
# sources/distributed-fs/ceph-client/drivers/net/ieee802154/mcr20a.c

## Purpose
`mcr20a.c` is a SPI mac802154 driver for NXP MCR20A 802.15.4 transceivers. It combines regmap-backed direct/indirect register access with raw async SPI packet-buffer transfers and implements channel, CCA, TX power, address filtering, RX, TX, and IRQ sequencing.

## Important APIs, types, and functions
`struct mcr20a_local` stores SPI, hw, DAR/IAR regmaps, prepared SPI messages for TX, RX, register, and IRQ status flows, plus `is_tx` and current `tx_skb`. Register policy is in `mcr20a_dar_*()` and `mcr20a_iar_*()`. Core functions include `mcr20a_xmit()`, `mcr20a_start()`, `mcr20a_stop()`, `mcr20a_set_channel()`, address/CCA/txpower/promiscuous setters, `mcr20a_irq_isr()`, and chained async completion handlers.

## Control flow
Probe resets the chip with `rst_b`, allocates hw/private data, initializes SPI message templates, creates DAR/IAR regmaps, sets phy capabilities, runs `mcr20a_phy_init()`, requests an initially disabled IRQ, and registers hw. Start enables IRQ, unmasks sequence interrupts, and starts RX. TX first forces IDLE, then IRQ sequence completion writes the packet buffer, sets TX sequence, waits for TX IRQ, completes mac802154 transmit, and restarts RX. RX IRQ reads frame length, then packet data plus LQI, strips FCS, and injects an skb.

## State and persistence
State is volatile: cached regmaps, prepared SPI message structs, current TX skb, `is_tx`, programmed address filters, and hardware sequence state. No file or firmware persistence is performed.

## Dependencies and integration points
The driver integrates with SPI, regmap, GPIO reset, IRQ trigger type, mac802154/cfg802154, skbuff, and constants from `mcr20a.h`.

## Risks and test signals
Risks are concentrated in async SPI message reuse, IRQ disable/enable ordering, `is_tx` races, RX length minus FCS underflow if invalid length handling is wrong, ignored regmap errors in filter setters, and CCA ED setters returning success for unsupported levels. Test signals include register access policy tests, probe failure unwinding, start/stop IRQ state, TX with and without ACK, RX length/LQI paths, channel PLL programming, CCA mode/threshold mapping, promiscuous filtering, and removal during idle/TX/RX.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ieee802154/mcr20a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ieee802154/mcr20a.h -->
# sources/distributed-fs/ceph-client/drivers/net/ieee802154/mcr20a.h

## Purpose
`mcr20a.h` is the register map and bitfield definition header for the NXP MCR20A transceiver driver. It names direct access registers, indirect access registers, and bit masks used by `mcr20a.c` for radio initialization, IRQ handling, filtering, CCA, power, and packet sequencing.

## Important APIs, types, and functions
The header does not define functions or structs. Its important exported symbols are `DAR_*` register addresses, `IAR_*` indirect register addresses, IRQ status bits, `DAR_PHY_CTRL*` masks, source address matching bits, RX frame filter bits, dual PAN bits, CCA control bits, pad controls, sequence manager bits, and test/DTM/TX mode flags.

## Control flow
There is no runtime control flow. The constants are consumed by `mcr20a.c` in regmap readability/writeability policies, initialization overwrite tables, TX/RX sequence management, IRQ decoding, and mac802154 configuration callbacks.

## State and persistence
No state is stored here. The definitions are a compile-time hardware contract; incorrect values persist as misprogrammed hardware registers at runtime.

## Dependencies and integration points
The file is private to the MCR20A driver and depends only on kernel bit macros being available through the including C file. It is coupled tightly to NXP datasheet semantics and to the `mcr20a.c` regmap configs.

## Risks and test signals
Primary risks are misspelled register comments, bit definition mistakes, and stale datasheet mapping. A notable typo-like risk is `IAR_ANT_AGC_CTRL_ANTX_MASK` referencing `BIT(AR_ANT_AGC_CTRL_ANTX_SHIFT)`, where the apparent `I` prefix is missing; compile coverage should catch this if the macro is used. Test signals include allmodconfig/build coverage, register read/write smoke tests on hardware, static checks for unused or malformed bit macros, and cross-checking each writable/readable register list against this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ieee802154/mcr20a.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ieee802154/mrf24j40.c -->
# sources/distributed-fs/ceph-client/drivers/net/ieee802154/mrf24j40.c

## Purpose
`mrf24j40.c` is a SPI mac802154 driver for Microchip MRF24J40, MRF24J40MA, and MRF24J40MC 802.15.4 transceivers. It handles short and long register spaces, TX/RX FIFO access, IRQ status processing, and mac802154 callbacks for channel, filtering, CSMA, CCA, TX power, and promiscuous mode.

## Important APIs, types, and functions
`struct mrf24j40` contains SPI, hw, short/long regmaps, prepared async SPI messages for TX, post-TX trigger, RX length/buffer reads, IRQ status reads, and the current TX skb. Register policies are in `mrf24j40_short_reg_*()` and `mrf24j40_long_reg_*()`, with a custom long-register regmap bus. Key functions are `mrf24j40_tx()`, `write_tx_buf_complete()`, RX handlers, `mrf24j40_intstat_complete()`, `mrf24j40_hw_init()`, and `mrf24j40_phy_setup()`.

## Control flow
Probe allocates hw/private state, configures capabilities, prepares SPI messages, initializes regmaps, validates SPI clock, initializes hardware, sets phy defaults, requests IRQ, and registers hw. TX writes the normal TX FIFO then asynchronously writes `TXNCON` to trigger transmit with security/ACK flags derived from the skb frame control. IRQ completion re-enables IRQs, ignores security decryption events, completes TX on `TXNIF`, and starts RX handling on `RXIF`. RX temporarily sets `RXDECINV`, reads length and payload/LQI/RSSI, unlocks RX, and injects the skb.

## State and persistence
All state is volatile. Hardware register settings carry current channel, addresses, PAN coordinator mode, CCA thresholds, and power; driver state tracks prepared SPI buffers and the in-flight TX skb.

## Dependencies and integration points
It integrates with SPI, regmap, IRQ trigger type, mac802154/cfg802154, IEEE 802.15.4 frame helpers, and module/of/spi device ID tables. MRF24J40MC-specific amplifier setup is selected through device ID data.

## Risks and test signals
Risks include async message lifetime during removal, RX buffer length copying into stack/local buffers, edge-triggered IRQ race warnings, unimplemented ED returning zero, silent partial TX FIFO truncation, and module variant mismatches between OF data and SPI ID data. Tests should cover probe for all three variants, max SPI frequency rejection, TX ACK/security flag propagation, TX complete, RX lock/read/unlock, channel RF reset delay, filter writes, CSMA/CCA/ED threshold mapping, promiscuous mode, and IRQ polarity behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ieee802154/mrf24j40.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ifb.c -->
# sources/distributed-fs/ceph-client/drivers/net/ifb.c

## Purpose
`ifb.c` implements the Intermediate Functional Block netdevice. IFB provides a redirect target for tc actions, allowing ingress traffic to be queued and shaped by egress qdisc machinery and allowing per-device qdisc/policy sharing.

## Important APIs, types, and functions
`struct ifb_q_private` is per-TX-queue state with receive/transmit skb queues, tasklet, queue index, and u64 stats. `struct ifb_dev_private` points to the per-queue array. Key functions are `ifb_xmit()`, `ifb_ri_tasklet()`, `ifb_stats64()`, ethtool stats helpers, `ifb_dev_init()`, `ifb_dev_free()`, `ifb_setup()`, and rtnl link registration via `ifb_link_ops`.

## Control flow
Module init registers the rtnl link kind and creates legacy `ifb%d` devices according to `numifbs`. `ifb_xmit()` accepts only redirected packets with a valid ingress interface index, updates RX queue stats, enqueues to the queue-private receive queue, possibly stops the TX queue, and schedules the tasklet. The tasklet moves queued packets to a transmit queue under netdev queue lock, clears redirect/classify/netfilter-egress loop markers, restores the original device from `skb_iif`, updates TX stats, and reinjects via `dev_queue_xmit()` or `netif_receive_skb()`.

## State and persistence
State is volatile per netdevice and per queue: skb queues, tasklet pending flag, stats, drops, and queue stopped state. Configuration persistence is handled externally by rtnetlink userspace, not by this driver.

## Dependencies and integration points
IFB integrates with netdevice core, rtnl link ops, ethtool stats, qdisc/tc redirect actions, netfilter egress skip markers, skb metadata, and network namespaces for original-device lookup.

## Risks and test signals
Risks include queue/tasklet races, redirect loops if skip flags regress, drops when original ifindex disappears, queue wake/stop threshold correctness, stats consistency under 32-bit readers, and behavior with ingress vs egress redirected skbs. Tests should cover `ip link add type ifb`, module legacy creation, tc mirred ingress shaping, multi-queue stats, queue limit backpressure, original device removal, netns isolation, close/open queue transitions, and ethtool stat names/values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ifb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/Kconfig

## Purpose
`ipa/Kconfig` defines the build-time configuration symbol for the Qualcomm IPA network driver. It presents `CONFIG_QCOM_IPA` as a tristate option and records the platform, subsystem, and helper dependencies required to build the driver.

## Important APIs, types, and functions
There are no C APIs or functions. The important interface is the `config QCOM_IPA` symbol. It depends on networking, Qualcomm SMEM, Qualcomm architecture or compile-test, interconnect support, compatible remoteproc/common and AOSS QMP settings, and selects the MDT loader, SCM, and QMI helper libraries.

## Control flow
Kconfig resolution determines whether `drivers/net/ipa/Makefile` contributes `ipa.o` to the build. The help text constrains expected use to Qualcomm IPA hardware and notes that the selection type must match `QCOM_Q6V5_COMMON`.

## State and persistence
Kconfig state persists only in the kernel build configuration. It determines compilation and module/built-in linkage, not runtime driver data.

## Dependencies and integration points
The symbol gates all IPA source under the folder and ties the network driver to Qualcomm firmware loading, secure monitor calls, QMI messaging, remoteproc, AOSS QMP, and interconnect infrastructure.

## Risks and test signals
Risks include dependency mismatches where IPA is built without compatible remoteproc/Q6 support, unmet selected helpers in unusual compile-test configurations, and user confusion around built-in vs module linkage matching `QCOM_Q6V5_COMMON`. Test signals include `olddefconfig` dependency resolution, `COMPILE_TEST` builds on non-QCOM architectures, module and built-in build combinations, and runtime probe on supported Qualcomm SoCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/Makefile

## Purpose
`ipa/Makefile` defines the object composition for the Qualcomm IPA driver. It builds the core IPA object from common driver sources plus versioned IPA, GSI, and SoC data objects.

## Important APIs, types, and functions
The important build variables are `IPA_REG_VERSIONS`, `GSI_REG_VERSIONS`, and `IPA_DATA_VERSIONS`, which expand into `reg/ipa_reg-v%.o`, `reg/gsi_reg-v%.o`, and `data/ipa_data-v%.o`. `obj-$(CONFIG_QCOM_IPA) += ipa.o` ties the composite object to Kconfig.

## Control flow
When `CONFIG_QCOM_IPA` is enabled, Kbuild creates `ipa.o` from core objects such as `ipa_main.o`, `ipa_power.o`, `gsi.o`, endpoint/command/modem/QMI/sysfs code, all listed IPA register descriptions, all listed GSI register descriptions, and all listed IPA data descriptions.

## State and persistence
There is no runtime state. The file is build metadata; its persistent effect is which version tables and support modules are linked into the IPA driver.

## Dependencies and integration points
The Makefile integrates Kconfig with the source layout under `drivers/net/ipa`, including `reg/` and `data/` generated/static version files. It must remain synchronized with version enums and lookup code in the core driver.

## Risks and test signals
Risks include adding a new version file without updating the corresponding version list, listing data without matching runtime selection logic, or removing a core object needed by module init/probe. Test signals include incremental and clean builds for `CONFIG_QCOM_IPA=m/y`, link checks for every versioned object, and probe tests for SoCs matching each `ipa_data-v*.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/data/ipa_data-v3.1.c -->
# sources/distributed-fs/ceph-client/drivers/net/ipa/data/ipa_data-v3.1.c

## Purpose
`ipa_data-v3.1.c` is the static SoC data description for Qualcomm IPA hardware version 3.1. It defines endpoint/GSI channel topology, resource group limits, IPA-local memory layout, QSB parameters, interconnect bandwidths, and power data used by the generic IPA driver.

## Important APIs, types, and functions
The file exports `const struct ipa_data ipa_data_v3_1`. Supporting static data includes `ipa_qsb_data`, `ipa_gsi_endpoint_data`, `ipa_resource_src`, `ipa_resource_dst`, `ipa_resource_data`, `ipa_mem_local_data`, `ipa_mem_data`, `ipa_interconnect_data`, and `ipa_power_data`. Local enums define IPA v3.1 source/destination resource types and group IDs.

## Control flow
There is no executable algorithm. Runtime IPA selection code uses `ipa_data_v3_1` to size and program endpoints, configure resources, map IPA-resident memory regions, request interconnect bandwidth, set core clock rate, and apply a backward-compatibility flag. Endpoint entries describe AP command, LAN RX, AP modem TX/RX, and modem-owned endpoints with GSI EE/channel/endpoint IDs and endpoint configuration such as aggregation, QMAP, checksum, DMA mode, status, and filter support.

## State and persistence
All data is compile-time constant. At runtime it becomes the authoritative configuration for IPA v3.1 hardware but is not modified or persisted by this file.

## Dependencies and integration points
The file depends on IPA core headers for endpoint IDs, memory IDs, sequence types, resource structures, version IDs, and compatibility flags. It is linked through the IPA Makefile and selected by core version matching.

## Risks and test signals
Risks are incorrect table constants: endpoint IDs, channel/event ring sizes, resource min/max limits, memory offsets/canaries, IMEM/SMEM sizes, interconnect names, or clock rate errors can break modem/AP data path setup. Test signals include build-time structure initialization checks, IPA v3.1 probe on target SoCs, endpoint bring-up, AP/modem traffic, QMAP/checksum/status behavior, resource programming validation, memory canary checks, and interconnect/clock vote verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipa/data/ipa_data-v3.1.c -->
