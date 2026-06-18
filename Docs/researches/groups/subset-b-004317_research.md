# subset-b-004317 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/xilinx_can.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/xilinx_can.c

Purpose: implements the SocketCAN network driver for Xilinx AXI CAN, Zynq CANPS, AXI CANFD 1.0, and AXI CANFD 2.0 platform devices. It binds OF compatibles to per-IP capability data, maps controller registers, configures clocks/reset/runtime PM, registers a `struct net_device` via `alloc_candev()`/`register_candev()`, and translates between Xilinx message RAM/FIFO formats and Linux CAN/CAN-FD sk_buffs.

Important APIs, types, and functions:
- `enum xcan_reg` and the `XCAN_*` masks describe the controller register map, classic CAN FIFO offsets, CAN-FD message RAM offsets, interrupt bits, bit timing fields, ECC counters, and RX FIFO status fields.
- `struct xcan_devtype_data` captures variant-specific behavior: IP type, flags such as `XCAN_FLAG_TX_MAILBOXES`, `XCAN_FLAG_RX_FIFO_MULTI`, `XCAN_FLAG_CANFD_2`, bit timing constants, bus clock name, and BTR field shifts.
- `struct xcan_priv` embeds `struct can_priv`, TX ring counters (`tx_head`, `tx_tail`, `tx_max`), a `spinlock_t tx_lock`, NAPI, endian-specific register accessors, clocks, optional transceiver PHY, reset control, variant metadata, and u64 ECC statistics.
- `xcan_write_reg_le/be()` and `xcan_read_reg_le/be()` abstract MMIO endianness; probe starts little-endian and switches to big-endian if the status register does not match config-mode expectations.
- `set_reset_mode()`, `xcan_set_bittiming()`, `xcan_chip_start()`, and `xcan_chip_stop()` are the controller mode and timing core.
- `xcan_start_xmit_fifo()`, `xcan_start_xmit_mailbox()`, `xcan_write_frame()`, and `xcan_tx_interrupt()` implement TX for FIFO and mailbox hardware.
- `xcan_rx_fifo_get_next_frame()`, `xcan_rx_poll()`, `xcan_rx()`, and `xcanfd_rx()` implement NAPI receive for classic and CAN-FD frames.
- `xcan_err_interrupt()`, `xcan_state_interrupt()`, `xcan_current_error_state()`, `xcan_set_error_state()`, and `xcan_update_error_state_after_rxtx()` drive CAN error state, bus-off, error frame reporting, and ECC ethtool counters.
- Netdev, ethtool, and PM integration is through `xcan_netdev_ops`, `xcan_ethtool_ops`, `xcan_dev_pm_ops`, `xcan_probe()`, and `xcan_remove()`.

Control flow:
- Probe maps the single MMIO resource, reads `tx-fifo-depth` or `tx-mailbox-count` plus `rx-fifo-depth`, allocates a CAN netdev sized for the usable echo queue, gets optional reset/PHY and mandatory clocks, enables runtime PM, detects register endianness, installs NAPI with RX FIFO depth as weight, registers the CAN device, initializes CANFD2 acceptance filter registers, and resets ECC counters when enabled.
- Open powers the transceiver, resumes runtime PM, requests IRQ, forces config mode, opens the CAN device, starts the chip, enables NAPI, and starts the netdev queue. Close reverses that path: stop queue, disable NAPI, reset/stop hardware, free IRQ, close CAN core, runtime suspend, and power off the transceiver.
- Chip start always resets to config mode, programs arbitration and optional data-phase bit timing, enables interrupts including error/state/RX/TX and optional ECC/RXMNF, enables loopback if requested, enables one extended filter on cores that otherwise drop all RX traffic, starts the controller, and marks CAN state active.
- TX validates the skb through `can_dev_dropped_skb()`, then either writes a FIFO frame or a single mailbox frame. FIFO mode can use at most two outstanding frames when TXFEMP exists; mailbox mode intentionally serializes to one frame because hardware transmits by CAN ID priority rather than submission order.
- RX interrupt handling masks the RX interrupt and schedules NAPI. NAPI drains frames until empty or quota, decodes classic or CAN-FD frame formats, advances the CANFD read index or clears RXNEMP, updates error state after successful RX, and re-enables RX interrupt when polling completes.
- IRQ handling also processes sleep/wake, TXOK, bus/error/RX overflow/arbitration lost/RXMNF/ECC conditions. Error handling clears status, updates SocketCAN stats, creates CAN error skbs when needed, resets the controller into config mode on bus-off, and accounts ECC counters with `u64_stats_sync`.
- Suspend stops a running netdev and delegates to runtime PM; resume restores clocks and restarts hardware/queue if the device was running.

State and persistence behavior: Runtime state is in `xcan_priv` and the CAN core, not persisted across reboot. `tx_head`/`tx_tail` track echo slots and are reset by hardware reset. `priv->can.state` tracks active, sleeping, warning/passive, bus-off, or stopped. ECC counters are cumulative per driver lifetime and exported through ethtool using `u64_stats_t`; hardware ECC counters are reset after reads during interrupt handling. Bit timing, ctrlmode, data bit timing, TDC settings, and CAN-FD support are owned by SocketCAN state and programmed into hardware at start/resume. Runtime PM controls clock state between opens and helper reads such as `xcan_get_berr_counter()`.

Dependencies and integration points: The driver depends on Linux platform/OF, SocketCAN (`linux/can/dev.h`, CAN bit timing and error helpers), netdev/NAPI, ethtool, runtime PM, reset framework, clocks, optional PHY transceiver, MMIO accessors, interrupts, and u64 stats synchronization. Device-tree bindings must provide the compatible, MMIO/IRQ, `can_clk`, variant bus clock (`pclk` or `s_axi_aclk`), TX depth property, RX FIFO depth, and optional `xlnx,has-ecc`. Integration with userspace is standard CAN netdev operations, ethtool stats, and SocketCAN error frames.

Risks and edge cases:
- Endianness detection relies on the status register returning exactly config-mode mask under little-endian access; unusual reset states could mis-detect.
- FIFO TX completion cannot know exact completed frame count from TXOK alone; the driver limits depth to two and uses TXFEMP, but this is still synchronization-sensitive.
- CANFD mailbox hardware sends by CAN ID priority, so the driver serializes to preserve FIFO ordering; increasing parallelism would change ordering semantics.
- RXFD decoding writes data in four-byte chunks and depends on aligned sk_buff data access patterns used elsewhere in CAN drivers.
- ECC interrupt handling accepts a small race between reading and resetting saturated hardware counters.
- `xcan_open()` error paths call `pm_runtime_put()` after failed `pm_runtime_get_sync()` without `pm_runtime_put_noidle()`, matching common kernel patterns but worth testing under runtime-PM failure injection.
- Missing DT depth properties are fatal; mailbox-mode RX is explicitly unsupported despite the error string mentioning mailbox mode.
- Bus-off leaves hardware in config mode and relies on CAN restart logic through `do_set_mode`.

Test signals:
- Boot/probe tests for each compatible, both endian modes, mandatory DT property validation, clock/reset/runtime PM failures, and optional transceiver/ECC paths.
- CAN loopback and real-bus tests for classic CAN, extended IDs, RTR frames, CAN FD, BRS, TDC auto reporting, and data lengths across DLC boundaries.
- TX stress with FIFO depth >2, TXFEMP/TXOK races, mailbox ordering with competing CAN IDs, and echo skb accounting.
- RX NAPI quota tests for static FIFO and CANFD multi-buffer FIFO, including overflow and RXMNF interrupts.
- Error injection for ACK/bit/stuff/form/CRC, arbitration lost, warning/passive recovery after RX/TX, bus-off and restart.
- Suspend/resume and runtime PM open/close cycles with active traffic.
- Ettool ECC counter reads under repeated ECC interrupts and 32-bit/64-bit builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/xilinx_can.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/Kconfig

Purpose: defines the top-level Kconfig menu for Distributed Switch Architecture switch drivers under `drivers/net/dsa`. It gates the menu on `NET_DSA`, sources vendor submenus, and declares selectable tristate symbols for standalone DSA switch drivers and transport frontends.

Important APIs, types, and functions: This is Kconfig metadata rather than C code. Key symbols include `NET_DSA_BCM_SF2`, `NET_DSA_LOOP`, `NET_DSA_MT7530`, `NET_DSA_MT7530_MDIO`, `NET_DSA_MT7530_MMIO`, `NET_DSA_MV88E6060`, `NET_DSA_RZN1_A5PSW`, `NET_DSA_KS8995`, `NET_DSA_SMSC_LAN9303`, `NET_DSA_SMSC_LAN9303_I2C`, `NET_DSA_SMSC_LAN9303_MDIO`, `NET_DSA_VITESSE_VSC73XX`, `NET_DSA_VITESSE_VSC73XX_SPI`, `NET_DSA_VITESSE_VSC73XX_PLATFORM`, and `NET_DSA_YT921X`. It also includes nested vendor Kconfig files for b53, Hirschmann, Lantiq, Microchip, Marvell mv88e6xxx, MaxLinear, Ocelot, Qualcomm, SJA1105, XRS700x, and Realtek.

Control flow: Kconfig processing enters the `Distributed Switch Architecture drivers` menu only when `NET_DSA` is available. Each symbol contributes dependencies and selected helper modules. For example Broadcom SF2 selects Broadcom tagging and PHY helpers plus `B53`; MT7530 core implies its MDIO/MMIO frontends; LAN9303 frontends select the shared core and regmap transport; VSC73xx frontends select the shared Vitesse core.

State and persistence behavior: The file persists build-time configuration only. Choices become `.config` symbols that drive compilation and module availability; it has no runtime state. `select` and `imply` statements can force helper objects into a build and therefore affect kernel image/module contents.

Dependencies and integration points: It integrates with the kernel Kconfig language, DSA tag protocol symbols, bus frameworks (`SPI`, `I2C`, MMIO via `HAS_IOMEM`), architecture predicates, PHY/PCS helpers, VLAN helpers, and subordinate vendor directories. The `source "drivers/net/dsa/b53/Kconfig"` line is the direct integration point for the B53 files in this work item.

Risks and edge cases:
- `select` bypasses dependency prompts of selected symbols, so selected helpers must remain safe under the selecting driver's dependencies.
- Split core/front-end symbols, such as MT7530 and LAN9303, need Makefile wiring to match Kconfig or builds can miss transport objects.
- Architecture defaults (`default ARCH_*`) influence distro kernels and can unexpectedly enable code when `NET_DSA` is on.
- Any missing sourced Kconfig path breaks menu generation.

Test signals:
- `make olddefconfig`, `make menuconfig`, and `scripts/kconfig/conf` parsing over several architectures.
- Build combinations with each tristate as built-in, module, and disabled.
- Compile-test combinations for `SPI`, `I2C`, `HAS_IOMEM`, `OF`, and DSA tag symbols.
- Verify each enabled symbol has matching `obj-$(CONFIG_...)` wiring in `drivers/net/dsa/Makefile` or subdirectory Makefiles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/Makefile

Purpose: maps top-level DSA Kconfig symbols to object files and always descends into vendor subdirectories that contain their own Kconfig-controlled objects.

Important APIs, types, and functions: This is Kbuild metadata. It builds single objects such as `dsa_loop.o`, `ks8995.o`, `mt7530.o`, `mv88e6060.o`, and `yt921x.o`; compound object `bcm-sf2.o` is composed from `bcm_sf2.o bcm_sf2_cfp.o`; shared-core/front-end families use separate objects such as `lan9303-core.o`, `lan9303_i2c.o`, `lan9303_mdio.o`, `vitesse-vsc73xx-core.o`, `vitesse-vsc73xx-platform.o`, and `vitesse-vsc73xx-spi.o`.

Control flow: During Kbuild, `obj-$(CONFIG_SYMBOL)` appends objects when symbols are `y` or `m`. `obj-y += b53/` and the other vendor directory entries cause Kbuild to visit those subdirectories; their internal Makefiles decide actual object emission based on configuration.

State and persistence behavior: There is no runtime state. Build outputs are generated according to `.config`, with modules or built-ins selected by tristate values. The order provides deterministic traversal but should not encode runtime ordering.

Dependencies and integration points: It integrates with the kernel Kbuild system, the top-level DSA Kconfig symbols, and subdirectory Makefiles. The B53 integration is delegated to `drivers/net/dsa/b53/Makefile`, while Broadcom SF2 links against B53 symbols selected by Kconfig.

Risks and edge cases:
- Mismatch between Kconfig symbols and object names results in enabled drivers not compiling or stale objects building.
- Always descending into subdirectories is normal, but each subdirectory must gate objects correctly to avoid unconfigured code.
- Compound objects need all constituent filenames maintained when source files are renamed.

Test signals:
- `make M=drivers/net/dsa` with representative configs.
- `make W=1` and allmodconfig/allnoconfig coverage to catch missing symbol/object wiring.
- Confirm each Kconfig entry that declares code has corresponding Makefile output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/b53/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/b53/Kconfig

Purpose: declares the Broadcom B53 managed switch DSA driver family and its transport-specific frontends. The `B53` menuconfig enables the common switch core; separate symbols enable SPI, MDIO, MMAP, SRAB, and SerDes support.

Important APIs, types, and functions: This is Kconfig metadata. `B53` is tristate, depends on `NET_DSA`, and selects all supported Broadcom DSA tag protocols (`NONE`, `BRCM`, `BRCM_LEGACY`, `BRCM_LEGACY_FCS`, `BRCM_PREPEND`). `B53_SPI_DRIVER` depends on `B53 && SPI`; `B53_MDIO_DRIVER` depends on `B53`; `B53_MMAP_DRIVER` depends on `B53 && HAS_IOMEM` and defaults on BCM63xx/BMIPS platforms; `B53_SRAB_DRIVER` depends on `B53 && HAS_IOMEM` and has the common optional-SerDes dependency idiom `B53_SERDES || !B53_SERDES`; `B53_SERDES` depends on `B53` and defaults on Northstar Plus platforms.

Control flow: Kconfig exposes B53 common support first, then transport choices. Selecting a transport enables the matching Kbuild object in `b53/Makefile`. `B53_SERDES` is independently selectable and can be used by the SRAB transport when SGMII lanes are present.

State and persistence behavior: Build-time only. The selected symbols determine which transport modules exist and which SerDes code is linked. Runtime transport detection is handled in the C probe functions, not here.

Dependencies and integration points: Integrates with DSA core, Broadcom tag protocol implementations, SPI, MDIO, MMIO/platform drivers, and architecture defaults. It is sourced from the top-level DSA Kconfig and consumed by the B53 Makefile.

Risks and edge cases:
- Because `B53` selects several tag protocols, tag implementations must remain compatible as built-in or module dependencies for all B53 transports.
- `B53_MDIO_DRIVER` has no explicit `MDIO` dependency because MDIO support is normally core networking infrastructure; build coverage should confirm this remains valid.
- The SRAB optional dependency must avoid link failures when SerDes is disabled while still allowing SRAB-only builds.

Test signals:
- Kconfig builds for B53 common only, each transport individually, all transports as modules, and SRAB with/without SerDes.
- Architecture configs where defaults apply (`BCM63XX`, `BMIPS_GENERIC`, `ARCH_BCM_IPROC`, `ARCH_BCM_NSP`).
- Module dependency inspection for selected DSA tag protocols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/b53/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/b53/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/b53/Makefile

Purpose: connects B53 Kconfig symbols to the common core and transport-specific object files.

Important APIs, types, and functions: This is Kbuild metadata. `CONFIG_B53` builds `b53_common.o`; `CONFIG_B53_SPI_DRIVER` builds `b53_spi.o`; `CONFIG_B53_MDIO_DRIVER` builds `b53_mdio.o`; `CONFIG_B53_MMAP_DRIVER` builds `b53_mmap.o`; `CONFIG_B53_SRAB_DRIVER` builds `b53_srab.o`; `CONFIG_B53_SERDES` builds `b53_serdes.o`.

Control flow: Kbuild evaluates each `obj-$(CONFIG_...)` line and includes the object in the built-in image or module set based on tristate value. Transport objects call exported symbols from `b53_common.o`, and SRAB can call exported SerDes helpers when enabled.

State and persistence behavior: Build artifacts only; no runtime state.

Dependencies and integration points: Integrates with the B53 Kconfig file and with the common/transport source files in the same directory. It relies on Kconfig to prevent illegal combinations, for example SPI transport without SPI support.

Risks and edge cases:
- If a transport is built as a module while common support is unavailable or not exported correctly, link/load errors occur.
- Optional SerDes references in SRAB must remain guarded by `IS_ENABLED(CONFIG_B53_SERDES)` to match this Makefile split.
- New B53 transport files require both Kconfig and Makefile updates.

Test signals:
- `make M=drivers/net/dsa/b53` for each symbol as `m` and built-in configs.
- Link checks for SRAB with `B53_SERDES=n`, `m`, and `y`.
- `modinfo`/`nm` checks for exported common symbols used by transport modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/b53/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/b53/b53_common.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/b53/b53_common.c

Purpose: provides the transport-independent Broadcom B53 DSA switch core. It implements chip detection and initialization, DSA switch callbacks, VLAN and bridge handling, ARL/FDB/MDB programming, port enable/disable, phylink integration, Broadcom tag setup, stats/devlink resources, mirroring, EEE, MTU, ageing time, and allocation/registration helpers exported to B53 transport drivers and Broadcom SF2 users.

Important APIs, types, and functions:
- `struct b53_mib_desc` and the `b53_mibs*` tables describe per-chip MIB counter layouts for ethtool stats.
- `b53_switch_alloc()`, `b53_switch_detect()`, and `b53_switch_register()` are the main transport-facing entry points. Transports allocate a `b53_device` with bus-specific `b53_io_ops`, optionally set platform data, then register with DSA.
- `b53_switch_ops` wires DSA callbacks for tag protocol, setup/teardown, ethtool stats, PHY access, phylink, port setup/enable/disable, EEE, bridge flags, VLANs, FDB/MDB, mirroring, and MTU.
- `b53_phylink_mac_ops` handles fixed/PHY/802.3z link state programming through `b53_force_link()`, `b53_force_port_config()`, RGMII adjustment helpers, and optional SerDes callbacks.
- VLAN helpers `b53_enable_vlan()`, `b53_configure_vlan()`, `b53_vlan_add()`, and `b53_vlan_del()` program chip-specific VLAN table formats and maintain `dev->vlans[]` plus per-port PVID state.
- ARL helpers `b53_arl_op()`, `b53_fdb_add()`, `b53_fdb_del()`, `b53_fdb_dump()`, `b53_mdb_add()`, and `b53_mdb_del()` operate the address resolution table through chip-specific `b53_arl_ops`.
- Bridge helpers `b53_br_join()`, `b53_br_leave()`, `b53_br_set_stp_state()`, `b53_br_flags_pre()`, and `b53_br_flags()` update port VLAN masks, EAP behavior, STP state, learning, flood masks, and isolation.
- `b53_switch_chips[]` is the core chip capability table: VLAN count, enabled-port mask, IMP/CPU port, VTA register set, ARL geometry, duplex and jumbo registers, and ARL ops.

Control flow:
- A transport calls `b53_switch_alloc()` to allocate `struct dsa_switch` and `struct b53_device`, install common DSA/phylink operations, initialize mutexes, and default VLAN behavior.
- `b53_switch_register()` copies platform chip ID/ports if supplied, otherwise detects the chip by reading management ID registers and legacy 5325/5365 VLAN/PHY clues. It then calls `b53_switch_init()` to load chip table data, allocate runtime `ports` and `vlans` arrays, configure optional reset GPIO, and register the switch with DSA.
- DSA `.setup` calls `b53_setup()`: sets DSA VLAN/PVID behavior, ageing bounds, resets switch and local caches, creates default VLAN membership, resets MIB counters, applies config with forwarding temporarily disabled, enables CPU ports, disables other ports until DSA enables them, and registers devlink VLAN resources.
- Port enable powers optional PHYs/IRQs through transport ops, clears RX/TX disable, restores bridge PVLAN mask and CPU port membership, and restores EEE. Port disable sets RX/TX disable and calls optional PHY/IRQ disable hooks.
- VLAN filtering changes set `dev->vlan_filtering` and re-run `b53_apply_config()`. VLAN add/delete update cached membership/untag/PVID state immediately, but only program hardware table entries and fast-age affected VLANs when filtering is enabled.
- FDB/MDB operations lock `arl_mutex`, load MAC/VID index registers, issue read/write ARL operations, select existing or free bins, and write static unicast or multicast port-bitmask entries.
- FDB dump starts ARL search and iterates bounded by ARL size, using family-specific search result decoders and callback filtering by port.
- Phylink config adjusts RGMII/MII quirks during fixed mode, forces link/speed/duplex/flow-control for fixed and some PHY modes, and delegates 802.3z/SGMII link control to transport SerDes ops where available.

State and persistence behavior: The driver keeps soft state in `struct b53_device`: chip identity, register offsets, port masks, IMP port, tag protocol, enabled VLAN/filtering flags, VLAN cache, per-port PVID/bridge mask/EEE state, SerDes lane cache, mutexes, and ARL ops. This state is reconstructed at probe and reset; it is not persistent. Hardware state is programmed into switch registers and may be lost on reset/suspend, so `b53_configure_vlan()` is designed to replay cached VLAN entries after reconfiguration. Devlink resource occupancy is computed live from the VLAN cache. MIB counters are hardware counters read under `stats_mutex` and reset during setup.

Dependencies and integration points: The core depends on DSA, phylink, switchdev bridge/VLAN/FDB/MDB objects, devlink resources through DSA helpers, PHYLIB for PHY stats and MII access, netdev ethtool stats, Broadcom tag protocol implementations, B53 register definitions, and transport-provided `b53_io_ops`. Transport modules call exported common symbols; Broadcom SF2 also selects/reuses B53 support. Hardware register differences are centralized in `b53_switch_chips[]`, `b53_arl_ops_*`, and chip-family predicate helpers from `b53_priv.h`.

Risks and edge cases:
- Many register formats vary subtly across 5325/5365/5389/539x/531x5/63xx/58xx/SF2 families; wrong chip ID or table entry metadata can corrupt VLAN or ARL programming.
- VLAN state is cached even when filtering is disabled; transitions must correctly replay membership and PVIDs or bridge isolation/flooding can break.
- CPU port/tag protocol selection has hardware constraints for ports 5, 7, and 8; unsupported stacked tag protocols fall back to `DSA_TAG_PROTO_NONE`, changing VLAN tagging assumptions.
- ARL searches and writes are timeout-based and bounded; full ARL bins return `-ENOSPC` for additions but deletions of missing entries are tolerated.
- `b53_br_leave()` updates `dev->ports[port].vlan_ctl_mask` inside a loop over remote ports, which is subtle and should be regression-tested for bridge membership correctness.
- Some paths intentionally skip behavior on older chips (`is5325()`), so feature coverage is uneven.
- RGMII delay programming is chip-specific and has comments documenting swapped BCM53125 clock controls; DT interface mode errors can manifest as link failures.
- `b53_mirror_del()` clears `reg &= ~mirror->to_local_port`, which treats a port number as a bitmask; tests should verify this is intended with the surrounding mirror API.

Test signals:
- Probe/register tests for each chip table entry via MDIO/SPI/MMAP/SRAB fixtures or emulation, including legacy 5325/5365 detection.
- DSA bridge tests for join/leave, STP states, learning/flood/isolation flags, fast ageing, multiple bridges with global VLAN filtering constraints.
- VLAN add/delete/filtering toggle tests including PVID changes, CPU-port tagging, default VLAN behavior, VLAN 0, out-of-range VIDs, and 7278 port 7 restrictions.
- FDB/MDB add/delete/dump tests across unicast/multicast, VLAN-aware and VLAN-unaware modes, full ARL bins, and chip-family ARL encodings.
- Phylink tests for fixed, PHY, RGMII variants, 802.3z/SGMII, SerDes-enabled SRAB, and CPU port flow control on BCM5301x.
- Ettool stats, PHY stats, EEE enable/restore, MTU jumbo toggling, ageing time units, mirroring, and devlink VLAN resource occupancy.
- Reset/resume-style reconfiguration tests to verify cached VLAN/port state is replayed after hardware reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/b53/b53_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/b53/b53_mdio.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/b53/b53_mdio.c

Purpose: implements the B53 transport driver for switches managed through Broadcom pseudo-PHY MDIO registers. It provides `b53_io_ops` read/write methods, probes MDIO devices by OUI/compatible/address, and registers the common B53 DSA switch core.

Important APIs, types, and functions:
- `REG_MII_PAGE`, `REG_MII_ADDR`, and `REG_MII_DATA0..3` define the pseudo-PHY indirect access window at `BRCM_PSEUDO_PHY_ADDR`.
- `b53_mdio_op()` sets the switch page, writes the target register/opcode, and polls completion bits.
- `b53_mdio_read8/16/32/48/64()` and `b53_mdio_write8/16/32/48/64()` marshal switch registers through 16-bit MDIO data registers.
- `b53_mdio_phy_read16()` and `b53_mdio_phy_write16()` expose direct PHY MDIO access to the common DSA core.
- `b53_mdio_probe()`, `b53_mdio_remove()`, and `b53_mdio_shutdown()` manage the MDIO driver lifecycle.
- `b53_of_match[]` lists supported Broadcom compatible strings for MDIO-connected B53 switches.

Control flow:
- Probe refuses non-management MDIO addresses except address zero so generic PHY drivers can bind normal PHYs.
- It reads PHY ID registers from address 0, validates against known Broadcom OUIs, and defers on BCM7445D0 until the correct SF2 user MII bus appears.
- It allocates a B53 switch with `b53_mdio_ops`, forces `current_page` to `0xff` to guarantee the first page write, records the MDIO bus, stores driver data, and calls `b53_switch_register()`.
- Each switch register access goes through `b53_mdio_op()`. Page changes are cached in `dev->current_page`; after setting address/opcode the code polls up to five times for READ/WRITE bits to clear.
- Multiword reads assemble little-endian 16-bit data words from high word down to low; writes emit low word first then trigger the operation.

State and persistence behavior: Runtime state is minimal: `dev->current_page` caches the selected pseudo-PHY page, `dev->priv` and `dev->bus` point at the MDIO bus, and the common B53 core owns switch state. No persistent state exists. Shutdown calls `b53_switch_shutdown()` and clears driver data.

Dependencies and integration points: Depends on MDIO/PHY APIs (`mdio_device`, `mii_bus`, `mdiobus_*_nested`), Broadcom PHY constants, OF matching, RTNL-safe nested MDIO access, and the common B53 exported allocation/register/remove/shutdown functions. Integrates with DSA through the common core after successful probe.

Risks and edge cases:
- MDIO operations assume completion within five 10-100 us polls; slow or wedged hardware returns `-EIO`.
- Page caching must be invalidated after hardware reset; common reset paths set `current_page = 0xff`.
- `b53_mdio_phy_read16()` does not check negative `mdiobus_read_nested()` errors before storing in `u16`, so error propagation for PHY reads is weak.
- The probe OUI filter may reject future Broadcom variants unless updated.
- BCM7445D0 bus-name matching is platform-specific and can defer indefinitely if bus names change.

Test signals:
- Probe on supported compatibles and OUIs, unsupported OUI rejection, pseudo-PHY vs normal PHY address behavior.
- Register read/write width tests for 8/16/32/48/64-bit values and page changes.
- Timeout injection for stuck MDIO operation bits.
- Reset path tests verifying first access reprograms page.
- DSA registration/open/remove/shutdown cycles on MDIO-attached hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/b53/b53_mdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/b53/b53_mmap.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/b53/b53_mmap.c

Purpose: implements the B53 platform/MMIO transport for memory-mapped Broadcom switch register blocks, primarily BCM63xx integrated switches. It supplies direct MMIO `b53_io_ops`, parses OF/platform data, manages SoC EPHY/GPHY power bits through syscon regmap, and registers the common B53 switch core.

Important APIs, types, and functions:
- `struct b53_phy_info` describes SoC-specific EPHY/GPHY control bit layouts.
- `struct b53_mmap_priv` stores the switch MMIO base, optional GPIO/syscon regmap, selected PHY info, and runtime `phys_enabled` mask.
- `b53_mmap_read8/16/32/48/64()` and `b53_mmap_write8/16/32/48/64()` perform direct register access at `(page << 8) + reg`, honoring optional big-endian platform data and checking alignment.
- `b53_mmap_phy_enable()` and `b53_mmap_phy_disable()` toggle BCM63xx EPHY/GPHY low-power/bias bits when `brcm,gpio-ctrl` is present.
- `b53_mmap_probe_of()` maps resources, allocates `b53_platform_data`, reads chip ID from match data, detects big endian, and builds enabled-port mask from child `ports`.
- `b53_mmap_probe()`, `b53_mmap_remove()`, and `b53_mmap_shutdown()` implement platform lifecycle.

Control flow:
- Probe obtains platform data from board code or constructs it from OF. OF probing requires the MMIO resource and a `ports` child with `reg` properties to populate enabled ports.
- It allocates private transport data, records the register base, optionally looks up `brcm,gpio-ctrl`, selects PHY power metadata by chip ID, allocates a B53 device with MMIO ops, attaches platform data, and calls `b53_switch_register()`.
- MMIO read/write paths use direct `readb/readw/readl` or big-endian `ioread16be/ioread32be`. 48-bit accesses split into 16+32 or 32+16 depending on register alignment.
- PHY enable/disable updates SoC control bits and `phys_enabled` so shared EPHY bias is only powered down when no relevant EPHY ports remain active.

State and persistence behavior: Transport state is in `b53_mmap_priv`: mapped registers, syscon regmap, PHY metadata, and a live PHY-enabled bitmask. Platform data stores chip ID, enabled ports, register base, and endian mode. This state is runtime-only; hardware registers and PHY power bits are reprogrammed during probe/port enable.

Dependencies and integration points: Uses platform devices, OF, MMIO helpers, MFD syscon/regmap, platform data `<linux/platform_data/b53.h>`, and common B53 exported helpers. Integrates with DSA via `b53_switch_register()` and with common port enable/disable through `phy_enable`/`phy_disable` callbacks.

Risks and edge cases:
- OF probe fails without `ports`, so bindings must describe ports even if chip defaults exist.
- Direct MMIO alignment warnings return `-EINVAL` for unaligned 16/32/64-bit accesses; common register definitions must match hardware alignment.
- Big-endian mode is controlled by a DT boolean and affects multiword reads/writes; incorrect binding breaks register interpretation.
- PHY power control silently does nothing when `brcm,gpio-ctrl` lookup fails, which may be valid for some platforms but can hide missing bindings.
- EPHY bias tracking depends on `phys_enabled` matching successful regmap writes; failed writes prevent mask updates but callers do not receive errors because callbacks return void.

Test signals:
- Probe with platform data and OF data for each compatible, including enabled-port parsing and missing `ports` failure.
- Big-endian and little-endian register access tests for all widths, especially 48-bit odd/even alignment cases.
- PHY power sequencing tests on BCM6318/6368/63268 with multiple ports enabled/disabled.
- DSA port enable/disable cycles verifying EPHY/GPHY low-power bits.
- Remove/shutdown tests ensuring DSA unregister/shutdown paths run.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/b53/b53_mmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/b53/b53_priv.h -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/b53/b53_priv.h

Purpose: declares private data structures, chip predicates, transport operation vectors, ARL conversion helpers, and exported common-core prototypes for the B53 DSA switch family.

Important APIs, types, and functions:
- `struct b53_io_ops` is the core transport abstraction: register read/write widths, optional PHY read/write, IRQ enable/disable, PHY power hooks, phylink capability/PCS hooks, and SerDes link callbacks.
- `struct b53_arl_ops` abstracts chip-family ARL entry read/write/search decoding.
- `struct b53_device` is the central common-core state object containing the `dsa_switch`, platform data, mutexes, ops, chip metadata, register offsets, port masks, current page, bus/priv pointers, VLAN/port runtime caches, and SerDes PCS structures.
- `struct b53_port`, `struct b53_vlan`, `struct b53_pcs`, and `struct b53_arl_entry` model per-port EEE/PVID, VLAN table entries, phylink PCS lanes, and ARL entries.
- Chip ID constants and inline predicates (`is5325()`, `is63xx()`, `is5301x()`, `is58xx()`, etc.) centralize family checks used by common and transport code.
- `b53_build_op()` generates locked inline wrappers `b53_read*()` and `b53_write*()` around transport ops using `dev->reg_mutex`.
- ARL conversion helpers translate between packed hardware MAC/VID/fwd registers and `struct b53_arl_entry` for normal, 5325/5365, 5389, and 63xx search formats.
- Exported prototypes cover switch allocation/register/detect and DSA callback helpers reused by other Broadcom drivers.

Control flow: Transport drivers include this header, implement `b53_io_ops`, and call `b53_switch_alloc()`/`b53_switch_register()`. Common code uses the locked read/write wrappers to serialize register accesses, then dispatches chip-specific ARL encoding through `dev->arl_ops`. DSA callbacks declared here are implemented in `b53_common.c` and exported for transport/SF2 integration.

State and persistence behavior: The header defines runtime state layout but stores no state itself. `struct b53_device` fields are initialized at allocation, detection, chip initialization, and setup, then mutated by DSA events. `current_page` caches bus page selection for paged transports. VLAN and port arrays persist for the device lifetime and are used to replay hardware configuration.

Dependencies and integration points: Includes kernel mutex, phylink, etherdevice, and DSA headers plus `b53_regs.h`. Optional BCM47xx reset GPIO discovery integrates with NVRAM/board APIs under `CONFIG_BCM47XX`. Transport modules, common core, and SerDes code share this contract.

Risks and edge cases:
- The read/write wrappers assume every populated `b53_io_ops` callback exists for widths used by common code.
- `reg_mutex` serializes switch register operations but not higher-level ARL/VLAN semantics; common code uses additional mutexes where needed.
- Chip predicate coverage must match chip IDs in `b53_common.c`; adding variants in one place but not the other causes wrong feature branches.
- ARL bit packing has special CPU port remapping for BCM5325 and multicast handling; incorrect helpers corrupt FDB/MDB entries.
- `b53_for_each_port()` iterates over `B53_N_PORTS` rather than `dev->num_ports`, relying on `enabled_ports`.

Test signals:
- Build coverage for all transports and `CONFIG_BCM47XX` on/off.
- Unit-style tests or hardware tests for ARL encode/decode helpers across unicast, multicast, VID, static/age/valid flags, and BCM5325 CPU port remapping.
- Lockdep coverage for nested register access paths and ARL/stat mutexes.
- Probe tests verifying all `struct b53_device` chip metadata fields are initialized before use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/b53/b53_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/b53/b53_regs.h -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/b53/b53_regs.h

Purpose: provides register page offsets, register offsets, bit masks, shifts, and table-format definitions for Broadcom B53 switch cores. It is the shared hardware contract used by the common core, transports, and SerDes code.

Important APIs, types, and functions: This header contains macros only. Major groups include management/control/status pages, port MII pages, MIB pages, QoS/PVLAN/VLAN/jumbo/EEE/CFP pages, port control/STP bits, switch mode and forwarding bits, IMP override and GMII/RGMII override bits, reset/fast-age controls, link/speed/duplex summaries, global management and Broadcom header controls, aging time, mirroring registers, device/revision IDs, VLAN table access registers for standard/5397-98/63xx/5325/5365 variants, ARL table and search formats, 802.1X drop controls, port VLAN masks, VLAN control registers, jumbo frame settings, EAP mode fields, EEE timer/status registers, and CFP control.

Control flow: There is no executable flow. C code uses these definitions to compute the correct `(page, reg)` pair and bit encodings for register reads/writes. Chip-family branches in `b53_common.c` select alternate offsets such as `B53_VT_ACCESS_9798`, `B53_VT_ACCESS_63XX`, `B53_VLAN_CTRL4_25`, or `B53_JUMBO_MAX_SIZE_63XX`.

State and persistence behavior: No software state. The macros describe hardware state fields that persist in switch registers until reset or reprogramming.

Dependencies and integration points: Depends on kernel bit helper macros (`BIT`, `BIT_ULL`, `GENMASK`, `GENMASK_ULL`) via includers. It is included by `b53_priv.h`, `b53_common.c`, and SerDes/common code. It must remain synchronized with Broadcom switch datasheets and binding-supported chip variants.

Risks and edge cases:
- Several register layouts differ by chip family; using a standard macro on a 5325/5365/63xx/5397-98 path can program the wrong register.
- Multiword fields such as ARL MAC/VID, 48-bit counters, and jumbo/VLAN entries depend on transport endianness and width handling.
- One macro appears suspicious: `VTA_VID_HIGH_MASK_25` references `VTA_VID_HIGH_S_25E`, which is not defined in the visible file; if used, it would fail compilation. It may be dead code, but it is a risk signal.
- Comments document hardware quirks, such as swapped BCM53125 clock controls elsewhere; register definitions alone do not enforce safe usage.

Test signals:
- Compile all B53 variants to catch undefined/unused macro issues under different preprocessor paths.
- Hardware register read/write smoke tests for VLAN, ARL, jumbo, mirroring, EEE, and RGMII controls on representative chip families.
- Static analysis for unused or misspelled macros, especially variant-only fields.
- Regression tests around any macro changes because they can silently affect multiple transports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/b53/b53_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/b53/b53_serdes.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/b53/b53_serdes.c

Purpose: implements Northstar Plus B53 SerDes/SGMII PHY logic and phylink PCS integration. It provides lane selection, SerDes register access through the B53 register interface, PCS operations, link power control, capability reporting, PCS selection, and SerDes initialization.

Important APIs, types, and functions:
- `pcs_to_b53_pcs()` converts phylink PCS pointers back to `struct b53_pcs`.
- `b53_serdes_write_blk()`/`b53_serdes_read_blk()` select SerDes blocks and access block registers.
- `b53_serdes_set_lane()` caches and programs the active lane.
- `b53_serdes_config()`, `b53_serdes_an_restart()`, and `b53_serdes_get_state()` implement `struct phylink_pcs_ops`.
- `b53_serdes_link_set()` powers the SerDes BMCR up/down for 802.3z/SGMII link changes.
- `b53_serdes_phylink_get_caps()` advertises lane-dependent 2500BASE-X, 1000BASE-X, SGMII, and MAC speed capabilities.
- `b53_serdes_phylink_mac_select_pcs()` returns the initialized PCS for 802.3z/SGMII interfaces.
- `b53_serdes_init()` validates SerDes ID/PHY ID registers and initializes `dev->pcs[lane]`.

Control flow:
- SRAB or another transport maps a port to a lane through `b53_serdes_map_lane()`.
- Initialization reads SerDes ID0 and MII PHY IDs; zero or all-ones ID is treated as uninitialized hardware and returns `-ENODEV`.
- The selected lane's `struct b53_pcs` is populated with the common device pointer, lane number, and PCS ops.
- During phylink validation/capability discovery, lane 0 gets 2500BASE-X plus 1000BASE-X/SGMII, while lane 1 gets 1000BASE-X/SGMII.
- PCS config toggles fiber mode for 1000BASE-X; an restart sets `BMCR_ANRESTART`; state reading maps digital status speed/duplex/link/pause and BMSR autoneg-complete to `phylink_link_state`.
- Link set toggles `BMCR_PDOWN` when phylink asks an 802.3z/SGMII link up or down.

State and persistence behavior: `dev->serdes_lane` caches currently selected SerDes lane to avoid redundant lane writes. `dev->pcs[]` stores initialized PCS objects for the device lifetime. Hardware state lives in SerDes block registers and BMCR; it is not persisted across reset and must be reinitialized by transport setup.

Dependencies and integration points: Depends on B53 register wrappers, `b53_serdes.h` register definitions, Linux PHY constants, phylink PCS APIs, and DSA transport code that supplies `serdes_map_lane`. Exported symbols are consumed by SRAB when `CONFIG_B53_SERDES` is enabled.

Risks and edge cases:
- Lane selection warns if lane >1 and only supports `B53_N_PCS` lanes.
- `b53_serdes_config()` only toggles 1000BASE-X fiber mode; other interface-specific configuration is minimal.
- Capability assumptions are based on observed lane behavior and may not cover future SoCs.
- If mux configuration maps SGMII but SerDes ID registers are not initialized, SRAB logs/continues without PCS for that port.
- Register access depends on the underlying B53 transport being usable before switch registration completes.

Test signals:
- SRAB probe on SGMII and non-SGMII mux modes for ports 4/5.
- Phylink validation and link-up/down for SGMII, 1000BASE-X, and 2500BASE-X on lane 0.
- Autoneg restart and state reporting with pause/speed/duplex changes.
- Reset/reprobe cycles verifying `dev->serdes_lane` and `dev->pcs[]` reinitialize.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/b53/b53_serdes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/b53/b53_serdes.h -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/b53/b53_serdes.h

Purpose: declares Northstar Plus B53 SerDes register definitions and helper prototypes for optional SerDes/phylink PCS support.

Important APIs, types, and functions:
- Macros define the non-standard SerDes page, lane selector, block-address register, SerDes ID registers, MII register mapping, digital control/status registers, digital control bits, status speed/duplex/link/pause/error fields, and block offsets.
- `b53_serdes_map_lane()` is an inline wrapper that returns `B53_INVALID_LANE` when the transport does not implement lane mapping.
- Prototypes expose `b53_serdes_link_set()`, `b53_serdes_phylink_mac_select_pcs()`, `b53_serdes_phylink_get_caps()`, and `b53_serdes_init()`.
- When `CONFIG_B53_SERDES` is disabled, `b53_serdes_init()` compiles as an inline `-ENODEV` stub.

Control flow: Transport code includes this header and calls `b53_serdes_init()` after determining mux/lane configuration. Common phylink callbacks can call the exported helpers through transport ops. The compile-time stub lets SRAB code handle disabled SerDes without link errors.

State and persistence behavior: No state is stored in the header. It defines register fields used to manipulate hardware state and function contracts that operate on `struct b53_device`/`struct b53_pcs`.

Dependencies and integration points: Depends on Linux PHY/types headers and declarations from `b53_priv.h` through includer order. Integrates optional `CONFIG_B53_SERDES` with SRAB and common phylink support.

Risks and edge cases:
- The header uses `struct b53_device` through inline/prototypes without declaring it locally; it relies on include order from files that include `b53_priv.h` first.
- Register bit definitions are specific to Northstar Plus SerDes and should not be reused blindly for other SerDes blocks.
- The disabled-config stub returns `-ENODEV`; callers must treat this as optional, as SRAB does.

Test signals:
- Build SRAB/common code with `B53_SERDES=y`, `m`, and `n`.
- Compile-check include order in any new caller.
- Hardware tests validating each status/control bit against observed SGMII/1000BASE-X/2500BASE-X behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/b53/b53_serdes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/b53/b53_spi.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/b53/b53_spi.c

Purpose: implements the B53 transport driver for SPI-managed Broadcom switches. It supplies SPI-backed register read/write operations and registers the common B53 DSA core from an SPI device.

Important APIs, types, and functions:
- SPI protocol macros define data/status/page-select registers and command bits such as `B53_SPI_CMD_SPIF`, `B53_SPI_CMD_RACK`, read/write, normal, and fast modes.
- `b53_spi_read_reg()`, `b53_spi_clear_status()`, `b53_spi_set_page()`, `b53_prepare_reg_access()`, and `b53_spi_prepare_reg_read()` implement the controller command sequence and polling.
- `b53_spi_read8/16/32/48/64()` and `b53_spi_write8/16/32/48/64()` implement `b53_io_ops`, using little-endian register payload layout and unaligned helpers for writes.
- `b53_spi_probe()`, `b53_spi_remove()`, and `b53_spi_shutdown()` implement SPI driver lifecycle.
- OF and SPI ID tables list supported B53 switch models.

Control flow:
- Probe allocates a B53 device with SPI ops, copies optional platform data, registers the common switch, and stores driver data.
- Every register access clears pending SPI status by waiting for `SPIF` to clear, selects the target page, then issues a read or write command.
- Reads trigger an initial register read command, poll for `RACK`, then read data from `B53_SPI_DATA`.
- Writes compose a command/register/value buffer and send it directly; 48-bit writes use an 8-byte value buffer but transmit only 6 payload bytes.

State and persistence behavior: Transport state is the `spi_device` stored in `dev->priv`; common B53 state is owned by `b53_device`. No persistent state. Shutdown calls common switch shutdown and clears SPI driver data.

Dependencies and integration points: Depends on Linux SPI APIs, unaligned little-endian helpers, optional B53 platform data, OF/SPI device tables, and the common B53 exported helpers. Integrates with DSA through `b53_switch_register()`.

Risks and edge cases:
- SPI status and RACK polling are limited to ten 1 ms delays; slow hardware returns `-EIO`.
- All payloads are treated as little-endian; hardware variants requiring other ordering would need a new path.
- No PHY read/write callbacks are provided, so common PHY access falls back to switch MII-page register access.
- Probe does not call `spi_set_drvdata()` if common registration fails; that is fine, but remove must tolerate absent data.
- `B53_SPI_CMD_FAST` is defined but unused.

Test signals:
- SPI probe/remove/shutdown on each compatible/ID.
- Register width read/write tests, especially 48-bit truncation and 64-bit payloads.
- Status/RACK timeout injection.
- DSA setup and traffic tests over SPI-managed switches.
- Platform data and OF match coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/b53/b53_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/b53/b53_srab.c -->
# sources/distributed-fs/ceph-client/drivers/net/dsa/b53/b53_srab.c

Purpose: implements the B53 transport driver for Broadcom Switch Register Access Bridge (SRAB) MMIO blocks, common on BCM5301x/iProc/Northstar-style SoCs. It supplies SRAB-backed register access, optional per-port link interrupts, port mux/SerDes discovery, phylink capability hooks, and platform lifecycle glue for the common B53 DSA core.

Important APIs, types, and functions:
- SRAB register macros define command/status, write/read data, control/status, interrupt, and port mux registers.
- `struct b53_srab_port_priv` stores per-port IRQ, enabled flag, back pointer, port number, and detected PHY interface mode.
- `struct b53_srab_priv` stores SRAB register base, optional mux config base, and per-port interrupt/mode state.
- `b53_srab_request_grant()`, `b53_srab_release_grant()`, and `b53_srab_op()` implement SRAB bus arbitration and command polling.
- `b53_srab_read8/16/32/48/64()` and `b53_srab_write8/16/32/48/64()` implement register access ops.
- `b53_srab_port_isr()` and `b53_srab_port_thread()` acknowledge per-port interrupts and notify DSA phylink on SGMII link changes.
- `b53_srab_irq_enable()`/`b53_srab_irq_disable()` are optional transport IRQ hooks used by common port enable/disable.
- `b53_srab_phylink_get_caps()` reports capabilities from mux mode and optional SerDes.
- `b53_srab_mux_init()` reads port 5/4 mux settings, sets PHY interface mode, and initializes SerDes for SGMII.
- `b53_srab_probe()`, `b53_srab_remove()`, and `b53_srab_shutdown()` implement platform lifecycle.

Control flow:
- Probe matches OF data to optional platform chip ID, allocates private data, maps SRAB registers, allocates a B53 device with SRAB ops, attaches platform data if present, stores platform driver data, prepares IRQ metadata, initializes mux/SerDes, and registers the common switch.
- Each switch register read/write requests SRAB grant by setting `RCAREQ` and polling `RCAGNT`, performs a command with page/register/op bits and polls `GORDYN` completion, accesses read/write data registers, and releases the grant.
- IRQ preparation clears pending interrupt bits, looks up optional named IRQs `link_state_pN` for ports except 6, records port metadata, and enables host interrupt delivery.
- Common `b53_enable_port()` calls SRAB `irq_enable` when present; the threaded IRQ path acknowledges the port interrupt and calls `b53_port_event()` for SGMII ports so phylink sees link changes.
- Mux init maps resource 1 when supported, reads port 5 then port 4 mux registers, maps values to SGMII/MII/GMII/RGMII/INTERNAL/NA, initializes SerDes for SGMII ports, and logs detected modes.

State and persistence behavior: Runtime transport state includes SRAB register mappings, mux mapping, per-port IRQ enabled status, detected interface modes, and common B53 state. Hardware SRAB grants and interrupts are transient. Remove disables host interrupts and unregisters DSA. Shutdown calls common DSA shutdown and clears driver data.

Dependencies and integration points: Depends on platform devices, OF matching, MMIO, interrupts/threaded IRQs, optional B53 SerDes helpers, phylink interface mode APIs, and common B53 exported functions. Integrates with DSA through common registration and with phylink through capability/PCS/link-event hooks.

Risks and edge cases:
- `b53_srab_request_grant()` loops 20 times but checks `WARN_ON(i == 5)`, which appears inconsistent; a failure after 20 polls may not be detected as intended.
- Optional per-port IRQ absence is represented by `-ENXIO` and ignored, so link changes may rely on polling/other mechanisms.
- Port 6 is skipped explicitly; assumptions must match hardware variants.
- SerDes lane mapping only supports SGMII on port 5 -> lane 0 and port 4 -> lane 1.
- Resource 1 mux mapping is skipped for non-BCM58xx platform data; missing mux resource silently disables mode discovery.
- Every register operation requests/releases SRAB grant; performance and deadlock behavior depend on hardware grant reliability.

Test signals:
- Probe on each compatible with and without platform data `.data` chip IDs.
- SRAB read/write width tests and timeout injection for grant and command completion.
- IRQ enable/disable and threaded link-state interrupt tests for SGMII ports.
- Mux mode tests for SGMII, MII, GMII, RGMII, internal, invalid modes, and missing mux resource.
- SerDes-enabled and SerDes-disabled builds/runtime behavior.
- Remove/shutdown tests confirming host interrupts are disabled and DSA unregister/shutdown runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/dsa/b53/b53_srab.c -->
