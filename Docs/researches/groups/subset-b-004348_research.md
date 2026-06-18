# Research Report: subset-b-004348

This grouped report covers Linux Ethernet driver files under `sources/distributed-fs/ceph-client/drivers/net/ethernet/{arc,asix,atheros}`. Each section preserves the source path and is delimited for deterministic split into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/arc/emac_mdio.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/arc/emac_mdio.c

## Purpose
Implements the MDIO bus backend for the Synopsys ARC EMAC driver. It allocates and registers a `struct mii_bus`, provides PHY register read/write callbacks through ARC EMAC registers, and optionally toggles a PHY reset GPIO from device-tree properties.

## Important APIs, Types, and Functions
Key entry points are `arc_mdio_probe()` and `arc_mdio_remove()`, exported to the ARC EMAC core through `emac.h`. `arc_mdio_read()` and `arc_mdio_write()` implement `mii_bus` callbacks by programming `R_MDIO`; `arc_mdio_complete_wait()` polls `R_STATUS & MDIO_MASK` and clears completion bits; `arc_mdio_reset()` handles `phy-reset-gpios` style reset through `devm_gpiod_get_optional()`. State is held in `struct arc_emac_priv`, especially `priv->bus` and `priv->bus_data`.

## Control Flow and State
Probe allocates a bus, assigns callbacks, reads optional `phy-reset-duration`, resolves either an `mdio` child node or the EMAC node for backwards compatibility, and registers the bus with `of_mdiobus_register()`. Reads and writes synchronously issue encoded MDIO commands and wait up to about one second. Removal unregisters and frees the bus and clears `priv->bus`.

## Dependencies and Integration Points
Depends on the ARC register helpers (`arc_reg_get()`, `arc_reg_set()`), OF MDIO registration, GPIO descriptors, and PHYLIB consumers above it. Device-tree compatibility is important because old nodes without an `mdio` subnode are still accepted.

## Risks and Test Signals
Timeout handling is the primary failure mode; tests should exercise missing PHYs, slow MDIO completion, and reset GPIO polarity/timing. The reset duration clamp appears suspicious: values over 1000 ms are set to `1`, not `1000`, so board files with large values get an unexpectedly tiny reset pulse. Useful signals include successful PHY discovery, `ethtool` MII access, and no leaked bus after probe failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/arc/emac_mdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/arc/emac_rockchip.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/arc/emac_rockchip.c

## Purpose
Provides the Rockchip platform glue for the generic ARC EMAC core. It adapts SoC-specific GRF register offsets, clocks, regulator handling, and RMII speed programming before delegating the network device to `arc_emac_probe()`.

## Important APIs, Types, and Functions
`struct emac_rockchip_soc_data` describes GRF offset fields and whether a divided MAC clock is needed. `struct rockchip_priv_data` embeds `struct arc_emac_priv` and adds `regmap`, regulator, and clock handles. `emac_rockchip_probe()` is the platform probe path, `emac_rockchip_remove()` unwinds it, and `emac_rockchip_set_mac_speed()` is installed as the ARC core `set_mac_speed` callback. OF matching selects RK3036, RK3066, or RK3188 data.

## Control Flow and State
Probe allocates an Ethernet device with private Rockchip state, validates RMII-only PHY mode, resolves the GRF syscon, enables `hclk`/`macref`, optionally enables the PHY regulator, writes initial 100 Mbps RMII GRF bits, sets reference clock to 50 MHz, optionally enables `macclk` at 25 MHz, then calls `arc_emac_probe()`. Removal calls the ARC core cleanup and disables resources in reverse.

## Dependencies and Integration Points
Integrates with platform bus, OF `phy-mode`, syscon/regmap for `rockchip,grf`, Linux clock framework, regulators, and the shared ARC EMAC implementation. Runtime link speed changes are propagated from the core into GRF speed bits.

## Risks and Test Signals
Risk is concentrated in resource unwind and SoC-specific GRF bit programming. Unsupported PHY modes fail early. Tests should cover probe deferral from regulator/clock/syscon, both `need_div_macclk` paths, 10/100 speed changes, and remove after partial probe. Board-level validation should verify RMII clock rates and that GRF writes use write-mask high bits correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/arc/emac_rockchip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/asix/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/asix/Kconfig

## Purpose
Defines Kconfig entries for non-USB ASIX Ethernet drivers, currently the AX88796C SPI Fast Ethernet adapter and its optional SPI transfer compression setting.

## Important APIs, Types, and Functions
`NET_VENDOR_ASIX` gates the vendor subtree. `SPI_AX88796C` is a tristate driver option that depends on `SPI` and `GPIOLIB` and selects `PHYLIB`. `SPI_AX88796C_COMPRESSION` is a boolean default for runtime SPI compression behavior, depending on `SPI_AX88796C`.

## Control Flow and State
The file only controls build-time configuration. If the vendor option is disabled, the AX88796C prompts are hidden. Compression is compiled as a default module parameter value in `ax88796c_main.c`, then can be changed per interface through ethtool private flags when the interface is down.

## Dependencies and Integration Points
The Kconfig dependencies match the code: the driver needs SPI transport, reset GPIO, and PHYLIB for the embedded PHY. The compression option feeds `IS_ENABLED(CONFIG_SPI_AX88796C_COMPRESSION)` in the driver.

## Risks and Test Signals
Build coverage should test `m`, `y`, and disabled combinations, plus `COMPILE_TEST` only where parent menus allow it. Runtime test signals for the compression option are correct default `SPICompression` private flag state at probe and successful toggling via ethtool while the netdev is stopped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/asix/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/asix/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/asix/Makefile

## Purpose
Builds the ASIX AX88796C SPI Ethernet driver object when `CONFIG_SPI_AX88796C` is enabled.

## Important APIs, Types, and Functions
The composite object `ax88796c.o` is assembled from `ax88796c_main.o`, `ax88796c_ioctl.o`, and `ax88796c_spi.o`.

## Control Flow and State
There is no runtime control flow. The Makefile expresses module composition: main netdev/SPI driver logic, ethtool/MDIO/ioctl helpers, and low-level SPI transaction helpers are linked into one driver.

## Dependencies and Integration Points
The Makefile is selected from the parent Ethernet vendor build and relies on the Kconfig symbol. It mirrors include dependencies among the files, where `ax88796c_main.h` and `ax88796c_spi.h` expose shared structs and register definitions.

## Risks and Test Signals
The practical test is that all three objects are linked for both built-in and module builds. Omitting any object would leave unresolved symbols such as `ax88796c_ethtool_ops`, `ax88796c_mdio_read()`, or `axspi_read_reg()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/asix/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/asix/ax88796c_ioctl.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/asix/ax88796c_ioctl.c

## Purpose
Provides ethtool operations, MDIO callbacks, and MII ioctl forwarding for the ASIX AX88796C SPI Ethernet driver.

## Important APIs, Types, and Functions
Exports `const struct ethtool_ops ax88796c_ethtool_ops`, `ax88796c_mdio_read()`, `ax88796c_mdio_write()`, and `ax88796c_ioctl()`. Private ethtool flag `SPICompression` maps to `AX_CAP_COMP`. Pause configuration updates `ax88796c_device.flowctrl` and PHY asymmetric pause settings. Register dump support reads AX88796C register space while honoring `ax88796c_no_regs_mask`, then appends PHY registers.

## Control Flow and State
EtHTool getters read driver state such as `msg_enable`, `flowctrl`, and `priv_flags`. `set_pauseparam()` either delegates pause advertisement to PHY autonegotiation or directly updates `P0_MACCR` under `spi_lock`. Compression flag changes are rejected with `-EBUSY` while the netdev is running because a soft reset is needed to reprogram SPI compression. MDIO reads/writes serialize SPI access, program `P2_MDIOCR`/`P2_MDIODR`, and poll for `MDIOCR_VALID`.

## Dependencies and Integration Points
Integrates with PHYLIB (`phy_ethtool_*`, `phy_mii_ioctl()`, `phy_set_asym_pause()`), the shared SPI access macros, and netdev ethtool plumbing. Register dumps depend on masks initialized in `ax88796c_main.c`.

## Risks and Test Signals
MDIO polling uses `read_poll_timeout()` around SPI register reads; timeouts and bad SPI return values are key risks. Pause update paths should be tested with autoneg on/off and link up/down. Compression flag tests should verify `-EBUSY` while running and successful soft-reset application on next open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/asix/ax88796c_ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/asix/ax88796c_ioctl.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/asix/ax88796c_ioctl.h

## Purpose
Declares the ioctl, ethtool, and MDIO interfaces implemented by `ax88796c_ioctl.c` for use by the AX88796C main driver.

## Important APIs, Types, and Functions
The header exports `ax88796c_ethtool_ops`, `ax88796c_mdio_read()`, `ax88796c_mdio_write()`, and `ax88796c_ioctl()`. It includes `linux/ethtool.h`, `linux/mii.h`, and `linux/netdevice.h`, matching its public interfaces.

## Control Flow and State
There is no runtime control flow in the header. It establishes linkage between `ax88796c_main.c`, which assigns netdev/MDIO operation tables, and the implementation file.

## Dependencies and Integration Points
Used by `ax88796c_main.c` to populate `ndev->ethtool_ops`, `ndo_eth_ioctl`, and `mii_bus` callbacks. The function signatures are standard kernel netdev and PHYLIB contracts.

## Risks and Test Signals
Risk is low and mostly about signature drift if kernel APIs change. Build tests catch mismatches immediately. Functional tests are inherited from the implementation: ethtool stats/register access, MII ioctl behavior, and MDIO PHY discovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/asix/ax88796c_ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/asix/ax88796c_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/asix/ax88796c_main.c

## Purpose
Implements the AX88796C SPI Ethernet netdev driver: SPI device probe/remove, PHY attachment, netdev open/close, transmit and receive paths, interrupt deferral, MAC configuration, checksum offload, multicast filtering, statistics, and module registration.

## Important APIs, Types, and Functions
Core entry points are `ax88796c_probe()`, `ax88796c_remove()`, `ax88796c_open()`, `ax88796c_close()`, `ax88796c_start_xmit()`, and `ax88796c_work()`. It uses `struct ax88796c_device` from the header, `axspi_data` helpers for register access, a `mii_bus` for embedded PHY access, and `ax88796c_netdev_ops`. Helper paths include `ax88796c_soft_reset()`, `ax88796c_reload_eeprom()`, `ax88796c_load_mac_addr()`, `ax88796c_set_hw_multicast()`, `ax88796c_set_csums()`, `ax88796c_handle_link_change()`, `ax88796c_tx_fixup()`, `ax88796c_hard_xmit()`, `ax88796c_receive()`, and `ax88796c_rx_fixup()`.

## Control Flow and State
Probe allocates a devres-managed netdev, initializes per-CPU stats, mutex, MDIO bus, ethtool/netdev ops, hard-resets via GPIO, soft-resets the chip, validates revision, reloads EEPROM, loads a DT/chip/random MAC, disables power saving, connects the internal PHY, and registers the netdev. Open requests the IRQ, resets and configures MAC/SPI compression/checksum/LED/PHY polling registers, starts PHY and TX queue, and initializes the RX SPI message. IRQs are top-half minimized: the interrupt disables the IRQ, sets `EVENT_INTR`, and schedules `ax_work`. The workqueue serializes all SPI register access under `spi_lock`, handles multicast updates, drains RX interrupts, transmits queued SKBs, and re-enables IRQs. Close stops PHY/queue, clears event bits, masks interrupts, purges TX queue, resets the chip, cancels work, and frees IRQ.

## Dependencies and Integration Points
Depends on SPI core, GPIO descriptors, PHYLIB, netdev, per-CPU u64 stats, ethtool ops, and the AX88796C register/SPI helpers. Device tree supplies optional MAC address, reset GPIO, SPI IRQ, and compatible string.

## Risks and Test Signals
High-risk areas are serialized SPI access, IRQ/work race handling, TX buffer expansion, RX header validation, and reset/unwind paths. A likely logic issue exists in `ax88796c_set_mac()`: the full-duplex case sets `MACCR_SPEED_100` instead of `MACCR_DUPLEX_FULL`, which can misprogram duplex. Probe calls `ax88796c_hard_reset()` but ignores its return. Tests should cover sustained TX/RX, close while work is pending, SPI compression on/off, checksum feature toggles, PHY link changes, reset GPIO absence/failure, and ethtool register dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/asix/ax88796c_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/asix/ax88796c_main.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/asix/ax88796c_main.h

## Purpose
Defines the AX88796C driver's shared state structures, register map, bit fields, TX/RX descriptor header formats, flow-control flags, event flags, and convenience conversions used by main, ioctl, and SPI code.

## Important APIs, Types, and Functions
Important types include `struct ax88796c_device`, `struct ax88796c_pcpu_stats`, `struct skb_data`, `struct tx_pkt_info`, `struct rx_header`, and TX header substructures. Important constants define queue watermarks, register dump lengths, PHY id, multicast filter size, packet header masks, MAC/PHY/page registers, interrupt bits, checksum offload registers, SPI control bits, wake filters, and register offsets. `to_ax88796c_device()` converts a netdev private area to driver state.

## Control Flow and State
The header has no executable control flow, but it defines the state model. `ax88796c_device` persists per-interface driver state: SPI device, netdev, per-CPU stats, work item, SPI mutex, TX wait queue, MDIO bus/PHY, sequence numbers, multicast filter, link parameters, flow-control flags, compression private flags, and work event bits.

## Dependencies and Integration Points
Includes `netdevice.h`, `mii.h`, and `ax88796c_spi.h`. The register definitions are consumed by all driver components and represent the hardware ABI. The exported `ax88796c_no_regs_mask` connects main initialization with ethtool register dumping.

## Risks and Test Signals
Bitfield correctness is critical because most control paths are raw register programming. Test signals include correct TX/RX header construction, checksum offload behavior, register dump masking, and link/MAC configuration. Any kernel API changes to `netdev_priv`, per-CPU stats, or MII structures would surface through compile failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/asix/ax88796c_main.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/asix/ax88796c_spi.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/asix/ax88796c_spi.c

## Purpose
Implements low-level SPI transactions for AX88796C register access, status reads, RX queue reads, TX queue writes, and power-state wakeup.

## Important APIs, Types, and Functions
Exports fixed command buffers `ax88796c_rx_cmd_buf` and `ax88796c_tx_cmd_buf`. Functions are `axspi_wakeup()`, `axspi_read_status()`, `axspi_read_rxq()`, `axspi_write_txq()`, `axspi_read_reg()`, and `axspi_write_reg()`. They operate on `struct axspi_data`, which owns the SPI device, command buffer, RX buffer, RX transfer array, and compression flag.

## Control Flow and State
Register reads build an opcode/address/dummy-cycle command, shorten the command when compression is enabled, call `spi_write_then_read()`, convert the 16-bit result from little-endian, and return `0xffff` on SPI error. Register writes send opcode, register address, and little-endian value bytes. RX queue reads create a two-transfer SPI message: command bytes followed by RX payload. TX queue writes pass a prepared skb buffer directly to `spi_write()`.

## Dependencies and Integration Points
Used by higher-level AX88796C code through inline wrappers in `ax88796c_spi.h` and macros `AX_READ`, `AX_WRITE`, `AX_READ_STATUS`, and `AX_WAKEUP`. It depends on Linux SPI APIs and the caller to serialize transactions with `spi_lock`.

## Risks and Test Signals
Risks include stale `rx_msg` transfer list reuse if messages are not initialized at the right time, alignment/endian assumptions for `rx_buf`, and silent `0xffff` return on register read failure being indistinguishable from a legitimate value. Tests should exercise compressed and uncompressed transfers, SPI fault injection, status endian conversion, and large RX reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/asix/ax88796c_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/asix/ax88796c_spi.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/asix/ax88796c_spi.h

## Purpose
Defines the AX88796C SPI transport ABI: command opcodes, SPI state structures, status structure, function prototypes, and inline register/status/wakeup wrappers.

## Important APIs, Types, and Functions
`struct axspi_data` stores the `spi_device`, reusable RX `spi_message`, two RX transfers, command buffer, register RX buffer, and compression flag. `struct spi_status` carries a 16-bit ISR and an 8-bit status with `AX_STATUS_READY`. Public helpers are `axspi_read_rxq()`, `axspi_write_txq()`, `axspi_read_reg()`, `axspi_write_reg()`, `axspi_read_status()`, and `axspi_wakeup()`. Inline wrappers expose `AX_READ`, `AX_WRITE`, `AX_READ_STATUS`, and `AX_WAKEUP`.

## Control Flow and State
No executable logic beyond wrapper calls. The header encodes command constants such as `READ_REG`, `WRITE_REG`, `READ_RXQ`, `WRITE_TXQ`, `READ_STATUS`, and `EXIT_PWD`, which are used by the SPI implementation and TX/RX paths.

## Dependencies and Integration Points
Included by `ax88796c_main.h` and `ax88796c_spi.c`. It depends on `linux/spi/spi.h` and kernel integer types. The compression flag is set by the main driver after soft reset based on private flags and hardware `SPICR` programming.

## Risks and Test Signals
Risk is mostly ABI drift between command constants and silicon behavior. Compile tests catch function signature mismatches. Runtime tests should verify that `AX_READ`/`AX_WRITE` remain serialized by callers and that compression does not change command layout incorrectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/asix/ax88796c_spi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/Kconfig

## Purpose
Defines build options for Atheros/Qualcomm Ethernet drivers, including the platform AG71XX MAC and PCI ALX driver covered in this work item.

## Important APIs, Types, and Functions
`NET_VENDOR_ATHEROS` gates the vendor subtree and depends on `PCI || ATH79 || COMPILE_TEST`. `AG71XX` is a tristate for AR7xxx/AR9xxx built-in MACs, depends on `ATH79 || COMPILE_TEST`, selects `PHYLINK`, and implies `NET_SELFTESTS`. `ALX` is a tristate for AR816x/AR817x PCIe adapters, depends on `PCI`, and selects `CRC32` and `MDIO`. Additional ATL variants are declared but outside this source set.

## Control Flow and State
The file has build-time control only. Its symbols decide whether Makefiles descend into `ag71xx.o` or `alx/` and which networking subsystems are guaranteed available.

## Dependencies and Integration Points
Dependencies mirror implementation needs: AG71XX uses platform/OF/phylink/selftest hooks, while ALX uses PCI, MDIO ioctl plumbing, CRC multicast hashing, MSI/MSI-X, and hardware register access.

## Risks and Test Signals
Important test signals are successful allmodconfig and targeted builds with `AG71XX=m/y`, `ALX=m/y`, `NET_VENDOR_ATHEROS=n`, PCI disabled, and ATH79 disabled plus `COMPILE_TEST`. Misdeclared dependencies show up as missing symbols in these matrix builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/Makefile

## Purpose
Routes Atheros Ethernet Kconfig symbols to their driver object directories or objects.

## Important APIs, Types, and Functions
`obj-$(CONFIG_AG71XX) += ag71xx.o` builds the platform MAC driver. `obj-$(CONFIG_ALX) += alx/` descends into the ALX PCI driver subdirectory. Other ATL driver directories are also conditionally included.

## Control Flow and State
No runtime behavior. This is build-system composition only.

## Dependencies and Integration Points
Depends on Kbuild and the Kconfig symbols declared in the same folder. It integrates the local `alx/Makefile`, which combines `main.o`, `ethtool.o`, and `hw.o` into `alx.o`.

## Risks and Test Signals
Build tests should confirm that enabling only AG71XX does not build ALX and vice versa. Any object rename or missing subdirectory would fail during Kbuild.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/ag71xx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/ag71xx.c

## Purpose
Implements the Atheros/QCA AR71xx-family built-in Ethernet MAC platform driver, including OF probe, MDIO bus, phylink integration, descriptor rings, DMA, NAPI RX/TX processing, ethtool stats/selftests, interrupt handling, MTU changes, and SoC-specific configuration.

## Important APIs, Types, and Functions
Central state is `struct ag71xx`, with RX/TX `struct ag71xx_ring`, OF `struct ag71xx_dcfg`, phylink config, reset/clock resources, NAPI, restart work, and OOM timer. Probe path is `ag71xx_probe()`. Lifecycle paths are `ag71xx_open()`, `ag71xx_stop()`, `ag71xx_hw_init()`, `ag71xx_hw_enable()`, and `ag71xx_hw_disable()`. Data path functions include `ag71xx_hard_start_xmit()`, `ag71xx_tx_packets()`, `ag71xx_rx_packets()`, and `ag71xx_poll()`. MDIO is handled by `ag71xx_mdio_probe()`, `ag71xx_mdio_mii_read()`, and `ag71xx_mdio_mii_write()`. Phylink callbacks are `ag71xx_mac_config()`, `ag71xx_mac_link_down()`, and `ag71xx_mac_link_up()`.

## Control Flow and State
Probe maps MMIO, enables clocks, requests reset and IRQ resources, initializes NAPI/work/timer/ring sizes, reads MAC address and PHY mode from DT, initializes hardware, registers an MDIO bus, creates phylink, and registers the netdev. Open connects phylink, calculates RX buffer size, writes max frame length/MAC address, allocates coherent descriptor memory, enables NAPI, starts queues, and starts phylink. IRQs mask poll interrupts and schedule NAPI. NAPI cleans completed TX, consumes RX descriptors into an skb list, refills RX buffers, handles overflow, and re-enables interrupts when work is complete. Stop tears down phylink, DMA, NAPI, timer, and rings.

## Dependencies and Integration Points
Depends on platform device/OF resources, syscon/regmap indirectly through platform data patterns, reset controls, clocks, OF MDIO, PHYLINK, DMA mapping, NAPI, and net selftests. OF compatible strings select FIFO data, max frame size, descriptor length mask, and TX hang workaround behavior for AR7100/AR7240/AR9130/AR9330/AR9340/QCA9530/QCA9550/QCA9560 variants.

## Risks and Test Signals
Risk areas include DMA descriptor ownership, RX refill under memory pressure, reset timing to avoid memory corruption, AR7100 descriptor splitting, and TX hang workaround scheduling. `ag71xx_mdio_probe()` uses a `static struct mii_bus *mii_bus`, which is unusual for per-device probe and merits scrutiny for multi-instance behavior. Tests should include link mode changes through phylink, MTU updates, RX OOM recovery timer, TX timeout restart, bus-error interrupts, ethtool stats/selftest output, and probe across supported compatible strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/ag71xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/alx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/alx/Makefile

## Purpose
Builds the Qualcomm Atheros ALX PCIe Ethernet driver as a composite object.

## Important APIs, Types, and Functions
`obj-$(CONFIG_ALX) += alx.o` and `alx-objs := main.o ethtool.o hw.o` define module composition.

## Control Flow and State
No runtime control flow. The Makefile ensures that PCI/netdev orchestration (`main.o`), ethtool implementation (`ethtool.o`), and low-level hardware helpers (`hw.o`) link together.

## Dependencies and Integration Points
Selected by the parent Atheros Makefile and `CONFIG_ALX`. The object layout matches header boundaries: `alx.h` for driver state, `hw.h`/`reg.h` for hardware definitions, and the three C files for implementation.

## Risks and Test Signals
Build tests should verify that `alx.o` contains all exported symbols required across files, especially `alx_ethtool_ops` and hardware helper functions used by `main.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/alx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/alx/alx.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/alx/alx.h

## Purpose
Defines the ALX driver's private software data structures for descriptor buffers, RX/TX queues, NAPI vector binding, per-device state, quirks, and the ethtool ops export.

## Important APIs, Types, and Functions
`struct alx_buffer` stores SKB and DMA unmap metadata. `struct alx_rx_queue` owns RRD/RFD rings, DMA addresses, software buffers, and read/write indexes. `struct alx_tx_queue` owns TPD ring state and producer/consumer register offsets. `struct alx_napi` binds a NAPI instance to optional RX/TX queues and an interrupt vector. `struct alx_priv` contains the `net_device`, `struct alx_hw`, descriptor memory block, queue/NAPI counts, IRQ mask lock, ring sizes, work items, message level, stats lock, and lifecycle mutex.

## Control Flow and State
The header has no executable control flow, but it defines state that persists across PCI probe, netdev open/close, suspend/resume, and error recovery. Queue indexes and DMA metadata are the authoritative software view of hardware descriptor rings.

## Dependencies and Integration Points
Includes `hw.h`, DMA mapping, spinlocks, and Ethernet helpers. `main.c` allocates and mutates these structures; `ethtool.c` reads `alx_priv` and `alx_hw`; `hw.c` operates below `alx_hw`.

## Risks and Test Signals
Correct locking around `int_mask`, `stats`, and `mtx` is essential. Tests should stress queue allocation/free, MSI-X fallback, suspend/resume, and reset while traffic is active. Structure changes require matching updates in allocation, cleanup, and ethtool stats paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/alx/alx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/alx/ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/alx/ethtool.c

## Purpose
Implements ALX ethtool operations for link settings, pause parameters, message level, and hardware statistics exposure.

## Important APIs, Types, and Functions
Exports `const struct ethtool_ops alx_ethtool_ops`. `alx_get_link_ksettings()` reports supported/advertised modes from `alx_hw`; `alx_set_link_ksettings()` validates and applies autoneg or forced speed via `alx_setup_speed_duplex()`. `alx_get_pauseparam()` and `alx_set_pauseparam()` map ethtool pause state to `ALX_FC_*` flags and MAC/PHY reconfiguration. `alx_get_ethtool_stats()` updates hardware stats and copies `struct alx_hw_stats` in the same order as `alx_gstrings_stats`.

## Control Flow and State
Most operations lock `alx->mtx` when reading or mutating link configuration. Stats use `alx->stats_lock` because hardware counters are clear-on-read and accumulated in `hw->stats`. Pause changes may restart PHY autoneg and may immediately update MAC flow-control bits.

## Dependencies and Integration Points
Depends on ethtool legacy link-mode conversion helpers, MDIO advertisement bit definitions, `alx_hw` helpers from `hw.c`, and stats layout in `hw.h`. Netdev installs this table during PCI probe.

## Risks and Test Signals
The order of `alx_gstrings_stats` must exactly match `struct alx_hw_stats`; the `BUILD_BUG_ON` protects size but not semantic order. Link-setting validation should be tested for 10/100 forced modes, disallowed forced 1000, Fast Ethernet chip support, and pause autoneg transitions. Stats tests should verify monotonic accumulation despite clear-on-read MIB registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/alx/ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/alx/hw.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/alx/hw.c

## Purpose
Implements low-level ALX hardware access for PCIe, MAC, PHY/MDIO, ASPM, speed/duplex setup, flow control, RSS disable, basic MAC/DMA configuration, MSI-X masking, PHY identification, and MIB statistics accumulation.

## Important APIs, Types, and Functions
MDIO helpers include `alx_read_phy_reg()`, `alx_write_phy_reg()`, `alx_read_phy_ext()`, and `alx_write_phy_ext()`, all serialized by `hw->mdio_lock`. Reset/config functions include `alx_reset_pcie()`, `alx_reset_mac()`, `alx_reset_phy()`, `alx_configure_basic()`, `alx_start_mac()`, and `alx_enable_aspm()`. Link helpers include `alx_setup_speed_duplex()`, `alx_read_phy_link()`, `alx_post_phy_link()`, `alx_phy_configured()`, and `alx_clear_phy_intr()`. Address/stats helpers include `alx_get_perm_macaddr()`, `alx_set_macaddr()`, `alx_get_phy_info()`, and `alx_update_hw_stats()`.

## Control Flow and State
The hardware layer reads/writes MMIO registers through inline accessors in `hw.h`. PHY access chooses MDIO clock based on current link state and supports Clause 22 and extended MMD-like access. Probe/reset flows call PCIe reset first, decide whether PHY is already configured, optionally reset PHY, reset MAC, configure speed/duplex, load MAC address, and later configure queues/DMA via `alx_configure_basic()`. Hardware MIB counters are accumulated into `hw->stats` because reads clear the hardware counters.

## Dependencies and Integration Points
Depends on PCI config space, MMIO register definitions from `reg.h`, Linux MDIO constants, ethtool advertisement conversion, and helper fields in `struct alx_hw`. `main.c` calls these helpers under `alx->mtx` for lifecycle and link state.

## Risks and Test Signals
Risk areas include reset timing, ASPM programming, PHY workaround coverage for revisions, clear-on-read stats, and advertisement translation. `ethadv_to_hw_cfg()` appears to map advertised 1000 full to `ALX_DRV_PHY_100 | DUPLEX` rather than a 1000 field, which deserves verification against hardware definitions. Tests should cover MAC reset timeout, link transitions at 10/100/1000, wake/ASPM after suspend, MIB counter accumulation, and MDIO timeout/error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/alx/hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/alx/hw.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/alx/hw.h

## Purpose
Defines the ALX hardware-facing ABI: TX/RX descriptor formats, descriptor bitfield helpers, flow-control and sleep flags, frame-size limits, interrupt masks, hardware statistics layout, `struct alx_hw`, MMIO helpers, and prototypes for `hw.c`.

## Important APIs, Types, and Functions
Descriptor types are `struct alx_txd`, `struct alx_rfd`, and `struct alx_rrd`. `DESC_GET`, `ALX_GET_FIELD`, and `ALX_SET_FIELD` manipulate packed fields. `struct alx_hw_stats` must match ethtool stat strings. `struct alx_hw` stores PCI/MMIO handles, MAC addresses, MTU, interrupt moderation, DMA channel config, RX control image, multicast hash, link state, flow-control/advertisement config, MDIO interface, PHY ids, workaround flag, and accumulated stats. Inline accessors wrap `readl`/`writel`/`readw`/`writew`.

## Control Flow and State
No substantial executable logic beyond inline accessors and `alx_speed_to_ethadv()`. The header defines persistent hardware state that `main.c`, `ethtool.c`, and `hw.c` share.

## Dependencies and Integration Points
Includes MDIO, PCI, VLAN, and `reg.h`. It is central to all ALX files. The descriptor layout is the contract between DMA hardware and driver; the stats struct is the contract between hardware MIB reads and ethtool/netdev stats.

## Risks and Test Signals
Descriptor packing, endian conversions, and bit masks are high risk because corruption affects DMA directly. Tests should validate TSO/checksum descriptor generation, RX error decoding, MTU-derived frame sizes, interrupt mask composition, and stats ordering. Static assertions in code catch some but not all layout drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/alx/hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/alx/main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/alx/main.c

## Purpose
Implements the ALX PCIe Ethernet netdev driver: PCI probe/remove, netdev lifecycle, descriptor ring allocation, RX/TX datapath, NAPI, MSI/MSI-X/legacy interrupts, link work, reset work, MDIO ioctl bridge, suspend/resume, PCI error recovery, and module registration.

## Important APIs, Types, and Functions
Probe/remove are `alx_probe()` and `alx_remove()`. Netdev ops include `alx_open()`, `alx_stop()`, `alx_start_xmit()`, `alx_change_mtu()`, `alx_ioctl()`, `alx_get_stats64()`, and `alx_tx_timeout()`. Lifecycle helpers are `__alx_open()`, `__alx_stop()`, `alx_halt()`, `alx_activate()`, and `alx_reinit()`. Ring/data path helpers include `alx_refill_rx_ring()`, `alx_clean_rx_irq()`, `alx_clean_tx_irq()`, `alx_map_tx_skb()`, `alx_tso()`, and `alx_tx_csum()`. Interrupt paths cover MSI-X misc/ring, MSI, and legacy. Power/error paths are `alx_suspend()`, `alx_resume()`, and PCI error handlers.

## Control Flow and State
PCI probe enables the device, sets DMA mask, requests BARs, maps registers, initializes locks/state, resets PCIe/PHY/MAC, configures link advertisement, obtains MAC/PHY identity, installs netdev/ethtool ops, and registers the netdev. Open chooses MSI-X if possible or falls back to MSI/INTx, allocates NAPI contexts and coherent descriptor memory, configures hardware, requests IRQs, initializes rings, starts queues, enables interrupts, and schedules link check. RX NAPI consumes updated RRDs, validates expected RFD index/count, unmaps DMA, handles error bits, sets checksum state, and passes packets to GRO. TX maps SKB head/frags into TPDs, handles TSO and checksum offload, advances producer index, and reclaims completions from hardware consumer index. Link work reads PHY state, starts/stops MAC and queues, and reinitializes hardware after link down.

## Dependencies and Integration Points
Depends on PCI core, DMA API, NAPI, netdev multiqueue, MSI/MSI-X, MDIO ioctl emulation, ethtool ops, CRC32 multicast hashing, and low-level `hw.c` helpers. Device ids include AR8161/AR8162/AR8171/AR8172 and Killer E2200/E2400/E2500 variants with an MSI INTx-disable quirk.

## Risks and Test Signals
Risk areas include descriptor memory needing one 4 GB address window, MSI-X fallback after partial resource allocation, RX DMA address workaround near page offset `0xfc0`, reset while NAPI/IRQs are active, and clear-on-read stats. `alx_request_msix()` initializes `free_vector` to zero and frees vectors based on it during partial failure; failure-path testing is important. Tests should cover traffic under MSI-X/MSI/legacy, multiqueue TX mapping, TSO/IPv6 TSO/checksum offload, MTU changes above TSO limit, suspend/resume, PCI AER recovery, link flap, and netpoll if enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/alx/main.c -->
