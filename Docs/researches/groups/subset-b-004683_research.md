# subset-b-004683 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mctp/mctp-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/net/mctp/mctp-i2c.c

Purpose: implements the DMTF MCTP SMBus/I2C transport binding as ARPHRD_MCTP netdevices. It creates one netdev per eligible I2C adapter and, for mux trees, shares one slave `i2c_client` on the root adapter across child bus netdevices selected by the `mctp-controller` property.

Important APIs/types/functions: `struct mctp_i2c_client` owns the hardware slave client, local link address, selected receive device, and child device list. `struct mctp_i2c_dev` owns the netdev, adapter reference, RX buffer/completion, TX kthread, skb queue, bus lock counters, and `allow_rx`. Key functions are `mctp_i2c_new_client`, `mctp_i2c_slave_cb`, `mctp_i2c_recv`, `mctp_i2c_header_create`, `mctp_i2c_xmit`, `mctp_i2c_tx_thread`, `mctp_i2c_release_flow`, `mctp_i2c_add_netdev`, adapter notifiers, and module init/exit.

Control flow: probe registers an I2C slave callback, then scans existing adapters. Adapter add/delete notifications create or remove netdevs. RX accumulates bytes from I2C slave events, validates command, length and PEC, strips the I2C header, fills `mctp_skb_cb` with the source slave address, and calls `netif_rx`. TX builds an SMBus packet header via `header_ops`, queues skb work, computes PEC, sends with `__i2c_transfer`, and updates stats.

State and persistence: runtime-only state is held in kernel objects, lists, refcounts, skb queues, kthreads, completions, and I2C bus locks. MCTP flow extensions drive `dev_flow_state`; active flows keep the I2C segment locked until `release_flow` queues an unlock marker. No persistent storage exists.

Dependencies/integration: depends on I2C slave support, optional I2C mux root discovery, OF `mctp-i2c-controller` / `mctp-controller`, netdev/MCTP core registration via `mctp_register_netdev`, and SMBus PEC helpers. It integrates tightly with MCTP flow lifecycle to preserve request/response bus ownership.

Risks and test signals: main risks are lock/refcount imbalance, RX racing unregister, malformed byte counts or PECs, mux selection mistakes, and TX queue backpressure. Useful tests include I2C mux add/remove, flow release under error, malformed frame rejection, netdev unregister while RX is in progress, and hardware or emulated PEC interoperability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mctp/mctp-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mctp/mctp-i3c.c -->
# sources/distributed-fs/ceph-client/drivers/net/mctp/mctp-i3c.c

Purpose: implements the DMTF MCTP I3C transport binding. It creates one MCTP netdev per I3C bus whose current master has the `mctp-controller` property, and attaches matching I3C devices with DCR class `I3C_DCR_MCTP`.

Important APIs/types/functions: `struct mctp_i3c_bus` owns the netdev, TX thread, one-slot TX state, local provisioned ID, bus pointer, and device list. `struct mctp_i3c_device` stores the I3C device, IBI setup, dynamic address, read/write limits, provisioned ID, and a mutex. Key functions are `mctp_i3c_bus_add`, `mctp_i3c_add_device`, `mctp_i3c_setup`, `mctp_i3c_ibi_handler`, `mctp_i3c_read`, `mctp_i3c_header_create`, `mctp_i3c_xmit`, and the I3C bus notifier.

Control flow: module init registers the I3C bus notifier, scans existing buses, then registers the I3C device driver. A bus add creates a netdev and TX thread. Device probe finds the owning bus, requests/enables IBI, and records endpoint limits. RX is IBI-driven: the handler filters the mandatory data byte when present and performs a private read transfer. TX looks up the destination provisioned ID from an internal header, appends PEC, and sends a private SDR write transfer.

State and persistence: all state is volatile. `busdevs_lock` protects the global bus list and per-bus device lists. Device mutexes serialize IBI RX, TX, and removal. A single pending TX skb is protected by `tx_lock`; the netdev queue is stopped until the TX thread consumes it.

Dependencies/integration: depends on I3C master/device APIs, OF property discovery on the master node, MCTP netdev registration, 48-bit provisioned IDs as link-layer addresses, and SMBus PEC calculation with I3C dynamic address bytes.

Risks and test signals: risks include unsupported IBI controllers, stale device lookup after endpoint removal, one-slot TX backpressure, max write/read length mismatches, and bus notifier ordering. Tests should cover bus add/remove races, IBI payload filtering, PEC rejection, endpoint `mwl` drops, and probe behavior without `mctp-controller`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mctp/mctp-i3c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mctp/mctp-serial.c -->
# sources/distributed-fs/ceph-client/drivers/net/mctp/mctp-serial.c

Purpose: implements DSP0253 MCTP over serial as the `N_MCTP` TTY line discipline. Opening the line discipline creates an MCTP netdev over the attached tty; closing unregisters it.

Important APIs/types/functions: `struct mctp_serial` holds the tty, netdev, IDA index, spinlock, TX work item, TX/RX state machines, FCS values, lengths, positions, and fixed buffers. Key functions are `next_chunk_len`, `mctp_serial_tx_work`, `mctp_serial_tx`, `mctp_serial_tty_receive_buf`, `mctp_serial_push_header`, `mctp_serial_push`, `mctp_serial_rx`, `mctp_serial_open`, and `mctp_serial_close`.

Control flow: TX copies the skb into a bounded buffer, stops the netdev queue, and schedules work. The worker writes the frame delimiter, version, length, escaped payload bytes, FCS, and trailing delimiter, handling partial tty writes and write wakeups. RX consumes bytes from `receive_buf`, runs a framing/escape state machine, validates version and CRC-CCITT FCS, and injects a packet with no link-layer address.

State and persistence: state is per-tty and runtime-only. The IDA allocates stable instance numbers while devices are open. A spinlock protects RX and TX state machines. `TTY_DO_WRITE_WAKEUP` and workqueue scheduling preserve progress across partial writes but no data persists after close.

Dependencies/integration: depends on TTY line discipline registration, CAP_NET_ADMIN for opening, MCTP netdev core, CRC-CCITT helpers, and normal netdevice queueing. It uses a fixed serial MTU of 68 bytes and ARPHRD_MCTP with no hardware header.

Risks and test signals: risks include malformed frames leaving the RX state machine stuck until a delimiter, partial write handling, concurrent tty close versus TX work, and fixed buffer length assumptions. Built-in KUnit coverage exercises `next_chunk_len`; further tests should cover escaping, CRC failure, line discipline permissions, close during TX, and netdev stats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mctp/mctp-serial.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mctp/mctp-usb.c -->
# sources/distributed-fs/ceph-client/drivers/net/mctp/mctp-usb.c

Purpose: implements DMTF DSP0283 MCTP-over-USB as a USB class driver that registers an ARPHRD_MCTP netdev for matching MCTP USB interfaces.

Important APIs/types/functions: `struct mctp_usb` stores the USB device/interface, endpoint addresses, netdev, one TX URB, one RX URB, stopped flag, and delayed RX retry work. Key functions are `mctp_usb_probe`, `mctp_usb_start_xmit`, `mctp_usb_out_complete`, `mctp_usb_rx_queue`, `mctp_usb_in_complete`, `mctp_usb_open`, `mctp_usb_stop`, and `mctp_usb_disconnect`.

Control flow: probe finds bulk IN/OUT endpoints, allocates netdev and URBs, initializes retry work, and registers the MCTP netdev. Opening starts TX and queues the first RX URB. TX prepends `struct mctp_usb_hdr`, stops the queue, submits the bulk OUT URB, and wakes the queue on successful completion. RX completion validates one or more DMTF packets in the USB transfer, clones/trims skbs for packed frames, injects MCTP packets, and requeues RX.

State and persistence: state is runtime-only in URBs, skbs, delayed work, and the stopped flag. Stop kills both URBs and cancels retry work; disconnect unregisters and frees objects. Per-CPU dynamic stats are enabled.

Dependencies/integration: depends on USB class matching via `USB_INTERFACE_INFO(USB_CLASS_MCTP, 0, 1)`, Linux USB bulk URBs, MCTP netdev registration with `MCTP_PHYS_BINDING_USB`, and `linux/usb/mctp-usb.h` constants.

Risks and test signals: risks include packed-frame parsing bugs, RX retry after stop/disconnect, TX queue stuck after URB errors, and header length truncation because packet length is stored in `u8`. Tests should cover short/invalid IDs, multiple packets per transfer, open/stop cycles, allocation failure retry, and unplug during active URBs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mctp/mctp-usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio.c

Purpose: provides generic exported helper routines for MDIO-compatible transceivers, especially Clause 45 probing, link status, auto-negotiation reporting, and ioctl mediation for drivers using `struct mdio_if_info`.

Important APIs/types/functions: exported symbols are `mdio45_probe`, `mdio_set_flag`, `mdio45_links_ok`, `mdio45_nway_restart`, `mdio45_ethtool_ksettings_get_npage`, and `mdio_mii_ioctl`. The helper uses `mdio_if_info` callbacks `mdio_read`/`mdio_write`, `prtad`, `mmds`, and `mode_support`.

Control flow: `mdio45_probe` scans MMDs 1-5, checks `STAT2`, reads device bitmaps, and records address/MMD presence. `mdio45_links_ok` clears latched bits then validates `STAT1` and fault state across MMDs. Ethtool reporting derives port type, supported/advertised modes, AN state, partner modes, speed, duplex, and 10GBASE-T MDI-X. `mdio_mii_ioctl` validates Clause 22/45 addressing or emulates common MII registers over Clause 45.

State and persistence: no owned persistent state; helpers update caller-owned `mdio_if_info` fields and ioctl/ethtool output structures. Hardware register changes occur only through callback writes such as flag setting and AN restart.

Dependencies/integration: depends on `linux/mdio.h`, ethtool legacy-link-mode conversion, MII ioctl data, and driver-supplied MDIO callbacks. It is a library module for Ethernet drivers rather than an MDIO bus controller.

Risks and test signals: risks include incomplete decoding for nonstandard next pages, negative MDIO reads being treated as bitfields in some paths, C22 emulation limits, and incorrect speed/duplex if hardware reports uncommon modes. Tests should mock read/write callbacks for C45 probe, link-fault latching, ioctl validation, and ethtool mode conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/Kconfig

Purpose: defines the build-time configuration surface for MDIO helper modules, MDIO controller drivers, MDIO-over-transport libraries, and MDIO bus multiplexers under `PHYLIB`.

Important APIs/types/functions: Kconfig symbols include helper accessors `FWNODE_MDIO`, `OF_MDIO`, `ACPI_MDIO`; bus controllers such as `MDIO_AIROHA`, `MDIO_ASPEED`, `MDIO_BCM_IPROC`, `MDIO_IPQ4019`, `MDIO_REALTEK_RTL9300`; library symbols `MDIO_BITBANG`, `MDIO_I2C`, `MDIO_REGMAP`, `MDIO_CAVIUM`; and mux symbols `MDIO_BUS_MUX*`.

Control flow: the file gates all definitions under `if PHYLIB`. Several symbols are silent libraries selected by concrete drivers (`MDIO_CAVIUM`, `MDIO_BUS_MUX`), while others are user-visible tristate choices. Dependencies express architecture, OF/ACPI, HAS_IOMEM, COMMON_CLK, PCI, USB, GPIOLIB, REGMAP, and MUX subsystem requirements.

State and persistence: Kconfig state persists in kernel build configuration. Selected symbols determine which object files are built and which helper APIs are available to other drivers.

Dependencies/integration: integrates with `drivers/net/mdio/Makefile`, phylib, OpenFirmware/ACPI discovery layers, and platform-specific SoC options. Defaults are conservative except for architecture defaults such as Broadcom iProc and Meson mux modules.

Risks and test signals: risks are missing `select` dependencies for helper libraries, overbroad `COMPILE_TEST`, link failures from silent symbols, and configuration combinations that compile a driver without required firmware APIs. Test signals are `allmodconfig`, `allyesconfig`, architecture defconfigs, and randconfig coverage for each dependency branch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/Makefile

Purpose: maps MDIO Kconfig symbols to kernel objects so helper modules, controller drivers, and mux drivers are built when selected.

Important APIs/types/functions: uses standard `obj-$(CONFIG_...) += file.o` entries. It includes firmware helpers (`acpi_mdio.o`, `fwnode_mdio.o`, `of_mdio.o`), controller drivers, library helpers (`mdio-bitbang.o`, `mdio-cavium.o`, `mdio-i2c.o`, `mdio-regmap.o`), and mux drivers.

Control flow: Kbuild includes each object based on resolved tristate state. Silent helper symbols are still built when selected by concrete drivers. The ordering places helper accessors first, individual controllers next, and mux core/drivers last.

State and persistence: no runtime state; this file affects build artifacts and module composition.

Dependencies/integration: depends on the Kconfig file for symbol availability and on source files exporting symbols used by other modules. Mux-specific object mappings must stay aligned with `select MDIO_BUS_MUX` relationships.

Risks and test signals: risks are stale object entries for renamed source files, omitted objects for Kconfig symbols, or building helper libraries in the wrong module linkage mode. Build tests with `allmodconfig`, targeted module builds, and `make M=drivers/net/mdio` catch most issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/acpi_mdio.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/acpi_mdio.c

Purpose: registers an MDIO bus from ACPI firmware descriptions and instantiates PHY devices from ACPI child nodes.

Important APIs/types/functions: exports `__acpi_mdiobus_register(struct mii_bus *mdio, struct fwnode_handle *fwnode, struct module *owner)`. It uses `acpi_get_local_address`, `ACPI_COMPANION_SET`, `__mdiobus_register`, and `fwnode_mdiobus_register_phy`.

Control flow: the helper masks all PHY addresses to prevent auto-probing, registers the mii_bus, associates the ACPI companion with the bus device, iterates child fwnodes, extracts each local address, filters invalid addresses, and delegates PHY creation/registration to the fwnode helper. Missing devices are logged but do not abort the whole bus registration.

State and persistence: state is in caller-owned `mii_bus`, ACPI companion references, and registered PHY devices. No driver-private persistent storage exists.

Dependencies/integration: depends on ACPI, fwnode MDIO helpers, phylib, and bus owner module registration. It is a firmware accessor library, not a platform driver.

Risks and test signals: risks include incomplete ACPI address data, silently skipped invalid children, and partial bus population after child registration failures. Tests should exercise ACPI child parsing, address bounds, deferred PHY errors, and bus registration/unregistration with ACPI companions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/acpi_mdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/fwnode_mdio.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/fwnode_mdio.c

Purpose: provides firmware-node-neutral helpers to create and register PHY devices on MDIO buses from OF or ACPI child nodes, including optional PSE and timestamping integration.

Important APIs/types/functions: exports `fwnode_mdiobus_phy_device_register` and `fwnode_mdiobus_register_phy`. Internal helpers are `fwnode_find_pse_control` and `fwnode_find_mii_timestamper`.

Control flow: PHY registration reads IRQs with defer-state fallback, handles `broken-turn-around`, attaches the fwnode to the PHY device, and calls `phy_device_register`. Higher-level registration discovers a timestamper, detects C45 compatibility or explicit PHY IDs, obtains/creates a `phy_device`, handles ACPI and OF registration paths, binds optional PSE control, and assigns timestamping when available.

State and persistence: state lives in registered `phy_device` instances: IRQ, fwnode reference, `psec`, `mii_ts`, and bus masks. Error paths remove/free PHYs and unregister timestampers.

Dependencies/integration: depends on phylib, generic firmware nodes, OF helpers for timestampers and PSE, ACPI checks, IRQ firmware lookup, and PHY device lifecycle APIs.

Risks and test signals: risks include leaked fwnode/timestamper references on error, wrong C45 detection, IRQ probe deferral behavior, and optional PSE errors after PHY registration. Tests should cover ACPI and OF paths, explicit PHY IDs, missing IRQ providers, PSE/timestamper defer/fail cases, and `broken-turn-around` masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/fwnode_mdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-airoha.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-airoha.c

Purpose: platform MDIO controller driver for the Airoha AN7583 SoC, supporting Clause 22 and Clause 45 transactions through a syscon regmap register.

Important APIs/types/functions: `struct airoha_mdio_data` stores base register offset, parent regmap, clock, and reset control. Read/write callbacks are `airoha_mdio_read`, `airoha_mdio_write`, `airoha_mdio_cl45_read`, and `airoha_mdio_cl45_write`; probe is `airoha_mdio_probe`.

Control flow: probe reads the MMIO offset from `reg`, obtains the parent syscon regmap, enables clock/reset, programs optional `clock-frequency`, fills `mii_bus` callbacks, and registers with `devm_of_mdiobus_register`. Transactions compose AN7583 command fields, write the busy bit, poll for completion, and read/write data. Clause 45 reads/writes issue an address phase before data phase.

State and persistence: runtime state is in `mii_bus->priv`, clock/reset hardware state, and SoC MDIO register fields. A read-specific reset workaround clears stale data caused by a documented hardware bug.

Dependencies/integration: depends on OF MDIO, regmap/syscon, clocks, resets, and phylib. Compatible string is `airoha,an7583-mdio`.

Risks and test signals: risks include reset side effects on concurrent users, wrong `reg` offset, unsupported clock rates, and timeout handling. Tests should cover C22/C45 address/data phases, absent PHY stale-data workaround, clock-frequency programming, and registration cleanup on errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-airoha.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-aspeed.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-aspeed.c

Purpose: MDIO bus controller for the independent ASPEED AST2600 MDIO block, exposing Clause 22 and Clause 45 callbacks to phylib.

Important APIs/types/functions: `struct aspeed_mdio` stores MMIO base and optional reset. `aspeed_mdio_op` emits a hardware operation; `aspeed_mdio_get_data` reads completed data; C22/C45 callbacks and `aspeed_mdio_probe/remove` implement bus lifecycle.

Control flow: probe allocates a devm mii_bus, maps registers, obtains optional shared reset, deasserts reset, installs read/write callbacks, and registers via `of_mdiobus_register`. Operations encode start type, op code, PHY address, register/devad, and write data into `ASPEED_MDIO_CTRL`, issue a dummy read to avoid stale read-after-write state, poll `FIRE` clear, and for reads poll `DATA_IDLE` before returning data.

State and persistence: runtime-only state is MMIO registers, reset line state, and registered bus. Remove asserts reset and unregisters the bus.

Dependencies/integration: depends on OF MDIO, HAS_IOMEM, reset controller, iopoll, and phylib. Compatible string is `aspeed,ast2600-mdio`.

Risks and test signals: risks include timeout tuning, stale-data workaround regressions, reset sharing side effects, and C45 address phase mistakes. Test signals include register-level emulation, reset probe/remove, C22 and C45 reads/writes, and failed `of_mdiobus_register` cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-aspeed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-bcm-iproc.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-bcm-iproc.c

Purpose: Broadcom iProc Clause 22 MDIO bus controller driver.

Important APIs/types/functions: `struct iproc_mdio_priv` stores the mii_bus and MMIO base. Core functions are `iproc_mdio_wait_for_idle`, `iproc_mdio_config_clk`, `iproc_mdio_read`, `iproc_mdio_write`, `iproc_mdio_probe`, `iproc_mdio_remove`, and resume clock restore.

Control flow: probe allocates private state and a bus, maps registers, assigns C22 callbacks, configures MDC divisor/preamble, registers with OF MDIO, and stores platform data. Reads/writes wait for idle, write an encoded MII data command with start, opcode, PHY, register, TA, and data fields, wait again, and return data or status. Resume reprograms clock configuration.

State and persistence: state is volatile in hardware registers and allocated bus/private structures. Remove unregisters and frees the bus.

Dependencies/integration: depends on Broadcom iProc architecture or compile test, OF MDIO, HAS_IOMEM, platform bus, and phylib.

Risks and test signals: risks include one-second busy-loop timeout, no Clause 45 support, clock divisor assumptions, and bus ID collisions for platform IDs. Tests should cover busy timeout, resume register restore, read/write encoding, and OF child PHY registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-bcm-iproc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-bcm-unimac.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-bcm-unimac.c

Purpose: Broadcom UniMAC MDIO bus controller for GENET MACs and Broadcom switch blocks, supporting Clause 22 transactions with optional platform-data wait callbacks.

Important APIs/types/functions: `struct unimac_mdio_priv` holds mii_bus, base, wait function/data, optional clock, and requested bus frequency. Key callbacks are `unimac_mdio_read`, `unimac_mdio_write`, `unimac_mdio_reset`, `unimac_mdio_clk_set`, probe/remove, and resume.

Control flow: probe maps an integrated register range, chooses platform-data or default polling behavior, obtains optional clock, sets bus callbacks, programs optional clock-frequency, and registers via OF MDIO. Each transaction enables the clock, writes command fields, starts hardware, waits, handles read-fail/turnaround masking, and disables the clock. Reset performs dummy BMSR reads on visible PHYs to work around integrated PHY first-transaction failures.

State and persistence: runtime state is the bus object, clock enable state, register configuration, and PHY ignore-turnaround masks inherited from OF. No storage persists beyond driver lifetime.

Dependencies/integration: depends on Broadcom platform data (`mdio-bcm-unimac.h`), clocks, OF MDIO, phylib, and endian-aware MMIO access for MIPS big-endian systems.

Risks and test signals: risks include clock-frequency divisor overflow, platform-data wait callbacks, read-fail handling with broken TA devices, and reset scans touching unintended PHYs. Tests should include platform and OF modes, clock gating, dummy-read workaround, suspend/resume, and broken TA masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-bcm-unimac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-bitbang.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-bitbang.c

Purpose: implements MDIO Clause 22 and Clause 45 protocol bit-banging over controller-specific pin operations.

Important APIs/types/functions: exported APIs are `mdiobb_read_c22`, `mdiobb_write_c22`, `mdiobb_read_c45`, `mdiobb_write_c45`, `alloc_mdio_bitbang`, and `free_mdio_bitbang`. It depends on `struct mdiobb_ctrl` and `struct mdiobb_ops` for MDC/MDIO direction, data set, and data get callbacks.

Control flow: helper routines send bits and numbers with timing delays, emit preamble/start/opcode/PHY/register fields, perform Clause 45 address phases, handle turnaround, and read/write 16-bit payloads. Allocation creates a `mii_bus`, pins callbacks to the exporting module, installs C22/C45 read/write callbacks, and initializes default C22 opcodes unless overridden.

State and persistence: state is owned by the embedding controller in `mdiobb_ctrl`; the library only allocates/frees an mii_bus and holds a module reference on ops owner. No hardware state is stored here.

Dependencies/integration: used by GPIO and other low-level drivers that can drive MDIO pins. It integrates with phylib through standard mii_bus callbacks and supports `phy_ignore_ta_mask`.

Risks and test signals: risks include timing margins on slow GPIO providers, sleeping GPIO callbacks under bus locks, turnaround handling returning `0xffff`, and module owner reference imbalance. Tests should cover C22/C45 waveforms, overridden C22 opcodes, broken TA masks, and alloc/free module references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-bitbang.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-cavium.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-cavium.c

Purpose: common MDIO transaction implementation for Cavium OCTEON and Thunder MDIO bus drivers.

Important APIs/types/functions: exports `cavium_mdiobus_read_c22`, `cavium_mdiobus_write_c22`, `cavium_mdiobus_read_c45`, and `cavium_mdiobus_write_c45`. Internal helpers are `cavium_mdiobus_set_mode` and `cavium_mdiobus_c45_addr`.

Control flow: transactions switch hardware mode between C22/C45 as needed, program write data or address phase, write SMI command fields, poll pending bits with bounded delays, and return data or `-EIO`. Clause 45 reads/writes first issue a C45 address command, then read or write data using the appropriate operation code.

State and persistence: state is held in the caller's `struct cavium_mdiobus`, especially MMIO base and current mode. Register state is hardware-resident and volatile.

Dependencies/integration: depends on `mdio-cavium.h` register/bitfield definitions and 64-bit MMIO accessors. Platform frontends such as `mdio-octeon.c` assign these callbacks to mii_bus.

Risks and test signals: risks include mode switch races if callers bypass mii_bus locking, timeout calibration, endian/bitfield layout, and C45 command field correctness. Tests should use register mocks or hardware diagnostics for C22/C45 reads/writes, invalid read data, pending timeout, and mode transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-cavium.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-cavium.h -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-cavium.h

Purpose: shared register layout, data structures, accessors, and function declarations for Cavium MDIO implementations.

Important APIs/types/functions: defines `enum cavium_mdiobus_mode`, SMI register offsets (`SMI_CMD`, `SMI_WR_DAT`, `SMI_RD_DAT`, `SMI_CLK`, `SMI_EN`), endian-aware bitfield macro `OCT_MDIO_BITFIELD_FIELD`, unions for hardware register layouts, `struct cavium_mdiobus`, `oct_mdio_readq/writeq`, and common callback prototypes.

Control flow: no active control flow, but the type layouts are consumed by common and frontend drivers to program SMI command, clock/mode, enable, read-data, and write-data registers. Accessor selection uses OCTEON CSR functions on OCTEON SoCs and generic `readq/writeq` elsewhere.

State and persistence: `struct cavium_mdiobus` carries runtime state for one hardware bus: the mii_bus pointer, MMIO base, and cached mode. Unions model hardware register state.

Dependencies/integration: integrates `mdio-cavium.c`, `mdio-octeon.c`, and Thunder frontend code. Depends on architecture bitfield endianness and optional `CONFIG_CAVIUM_OCTEON_SOC`.

Risks and test signals: risks include bitfield packing mismatch, 64-bit MMIO ordering, and stale prototypes when common callbacks change. Build coverage across big/little-endian and OCTEON/non-OCTEON configs is critical.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-cavium.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-gpio.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-gpio.c

Purpose: generic GPIO-backed MDIO bus driver built on the bitbang MDIO library.

Important APIs/types/functions: `struct mdio_gpio_info` embeds `mdiobb_ctrl` and GPIO descriptors for MDC, MDIO, and optional separate MDO. GPIO-backed `mdiobb_ops` callbacks are `mdio_dir`, `mdio_get`, `mdio_set`, and `mdc_set`. Lifecycle is in `mdio_gpio_probe/remove`.

Control flow: probe allocates state, requests GPIOs by index, derives bus ID from OF alias or platform ID, calls `alloc_mdio_bitbang`, assigns name/parent/id, optionally overrides opcodes for `microchip,mdio-smi0`, and registers the bus with OF MDIO. Remove unregisters and frees the bitbang bus.

State and persistence: runtime state consists of GPIO descriptors, mii_bus, and bitbang control. GPIO values and direction change during transactions; no persistent storage exists.

Dependencies/integration: depends on GPIOLIB, MDIO_BITBANG, OF MDIO, platform bus, and phylib. Compatible strings are `virtual,mdio-gpio` and `microchip,mdio-smi0`.

Risks and test signals: risks include sleeping GPIO access under timing-sensitive bitbang paths, optional MDO semantics, alias collisions, and opcode override regressions. Tests should cover two-wire and three-wire GPIO layouts, OF registration, Microchip SMI0 opcodes, and removal cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-hisi-femac.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-hisi-femac.c

Purpose: Hisilicon Fast Ethernet MAC MDIO controller driver exposing Clause 22 read/write callbacks.

Important APIs/types/functions: `struct hisi_femac_mdio_data` stores clock and MMIO base. Core routines are `hisi_femac_mdio_wait_ready`, `hisi_femac_mdio_read`, `hisi_femac_mdio_write`, probe, and remove.

Control flow: probe allocates mii_bus/private data, maps registers, gets/enables the clock, assigns read/write callbacks, registers with OF MDIO, and stores the bus. Reads wait for `MDIO_RW_FINISH`, write PHY/register fields, wait again, then read `MDIO_RO_DATA`. Writes wait, write command/data fields with `MDIO_WRITE`, then wait for completion.

State and persistence: runtime state is the enabled clock, MMIO registers, and bus private data. Remove unregisters bus, disables clock, and frees bus.

Dependencies/integration: depends on HAS_IOMEM, OF MDIO, clock framework, platform bus, and phylib. Compatible string is `hisilicon,hisi-femac-mdio`.

Risks and test signals: risks include clock lifecycle leaks on registration failure, timeout values, no Clause 45 support, and register field width assumptions. Tests should cover wait timeout, read/write command encoding, clock error paths, and OF PHY registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-hisi-femac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-i2c.c

Purpose: library that exposes PHYs reachable over I2C, commonly inside SFP modules, as an MDIO `mii_bus`.

Important APIs/types/functions: exported `mdio_i2c_alloc` creates a bus over an `i2c_adapter` for `enum mdio_i2c_proto`. Helpers implement default C22/C45 I2C transfers, SMBus-byte fallback, RollBall SFP page/password protocol, and functionality checks.

Control flow: default transfers map MDIO PHY IDs to I2C addresses `phy_id + 0x40`, excluding SFP EEPROM addresses 0x50/0x51. C45 uses one address/write pointer phase then read/write data. SMBus fallback reads/writes high and low bytes under an I2C segment lock. RollBall initializes a password, page-switches to page 3 around each transaction, writes command/data registers, polls for completion, and restores the original page.

State and persistence: the returned bus stores the adapter in `priv`; persistent module state is absent. RollBall temporarily changes SFP page state but restores it under lock.

Dependencies/integration: depends on I2C/SMBus APIs, SFP constants, phylib, and callers that register/free the returned bus. It is library-mode Kconfig, not a standalone device driver.

Risks and test signals: risks include collisions with SFP EEPROM pages, page-restore failures after I2C errors, long RollBall polling delays, SMBus fallback endianness, and unsupported I2C functionality. Tests should mock adapters for default, SMBus-only, and RollBall protocols, including error paths and reserved address filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-ipq4019.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-ipq4019.c

Purpose: Qualcomm IPQ4019/IPQ50xx/IPQ60xx/IPQ807x MDIO controller driver supporting Clause 22 and Clause 45.

Important APIs/types/functions: `struct ipq4019_mdio_data` stores MMIO base, optional ethernet LDO-ready register, optional MDIO AHB clock, and selected MDC rate. Core callbacks are `ipq4019_mdio_read_c22`, `ipq4019_mdio_write_c22`, `ipq4019_mdio_read_c45`, `ipq4019_mdio_write_c45`, `ipq_mdio_reset`, and `ipq4019_mdio_set_div`.

Control flow: probe maps registers, obtains optional clock, selects/programs MDC divider, maps optional LDO resource, assigns C22/C45 callbacks and reset, and registers with OF MDIO. Reset can mark Ethernet LDO ready, set/enable the MDIO clock, delay, and restore divider. Transactions poll busy, switch C22/C45 mode, write address/data registers, start access commands, and poll completion.

State and persistence: runtime state is MMIO mode/divider, clock enable/rate, optional LDO bit, and bus data. Remove unregisters the bus; devm handles allocations.

Dependencies/integration: depends on COMMON_CLK, OF MDIO, HAS_IOMEM, platform bus, and phylib. Compatible strings include `qcom,ipq4019-mdio` and `qcom,ipq5018-mdio`.

Risks and test signals: risks include divider exact-match validation, clock optionality in reset, C45 mode left enabled/disabled between operations, and LDO timing. Tests should cover divider selection from DT/default, C22/C45 sequences, busy timeouts, optional resource paths, and reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-ipq4019.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-ipq8064.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-ipq8064.c

Purpose: Qualcomm IPQ8064 Clause 22 MDIO interface driver using a regmap over NSS GMAC registers.

Important APIs/types/functions: `struct ipq8064_mdio` stores the regmap. Key routines are `ipq8064_mdio_wait_busy`, `ipq8064_mdio_read`, `ipq8064_mdio_write`, `ipq8064_mdio_probe`, and remove.

Control flow: probe maps the DT resource manually, allocates a devm mii_bus, initializes an MMIO regmap with locking disabled, assigns read/write callbacks, registers with OF MDIO, and stores the bus. Reads/writes program address/data registers with a fixed clock range, sleep briefly, and poll busy clear. Writes to register 31 delay longer to avoid subsequent bad reads.

State and persistence: runtime state is regmap/MMIO register state and bus private data. No persistent storage exists.

Dependencies/integration: depends on MFD_SYSCON/regmap-style MMIO, OF MDIO, platform bus, and phylib. Compatible string is `qcom,ipq8064-mdio`.

Risks and test signals: risks include disabled regmap locking relying on mii_bus serialization, fixed clock range, manual resource mapping, and the special register-31 delay. Tests should cover timeout, regmap failure paths, read/write command fields, and OF PHY discovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-ipq8064.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-moxart.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-moxart.c

Purpose: MOXA ART Ethernet MDIO controller driver for RTL8201CP-style PHY access.

Important APIs/types/functions: `struct moxart_mdio_data` stores MMIO base. Core routines are `moxart_mdio_read`, `moxart_mdio_write`, `moxart_mdio_reset`, probe, and remove.

Control flow: read/write callbacks encode PHY/register fields and MIIRD/MIIWR bits, poll auto-clearing control bits up to five 10 ms iterations, and return data/status. Reset scans all PHY addresses, reads BMCR, and writes BMCR_RESET for responsive devices. Probe allocates bus/private data, sets PHY_MAC_INTERRUPT placeholders for all addresses, maps registers, registers with OF MDIO, and stores bus.

State and persistence: volatile state is MMIO control/data registers and mii_bus data. Reset temporarily changes PHY BMCR reset bits. Remove unregisters and frees bus.

Dependencies/integration: depends on ARCH_MOXART or compile test, OF MDIO, platform MMIO, and phylib.

Risks and test signals: risks include broad reset scanning, fixed polling duration, PHY interrupt comments not matching OF behavior, and no Clause 45 support. Tests should include timeouts, BMCR reset behavior, OF child registration, and invalid MMIO resource errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-moxart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mscc-miim.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mscc-miim.c

Purpose: Microsemi/Microchip MIIM controller driver and setup helper for Ocelot/LAN966x switch MDIO blocks.

Important APIs/types/functions: `struct mscc_miim_dev` stores regmaps, status offset, optional PHY reset regmap/info, clock, bus frequency, and read-error policy. Exports `mscc_miim_setup`. Core callbacks are `mscc_miim_read`, `mscc_miim_write`, `mscc_miim_reset`, `mscc_miim_clk_set`, probe, and remove.

Control flow: reads wait for no pending command, issue a read command, wait for not busy, read data, and optionally treat hardware error bits as `-EIO`. Writes wait pending then issue a write command. Reset toggles SoC-specific PHY reset bits and delays 500 ms. Probe resets switch, creates regmaps from resources, calls setup, obtains optional PHY regmap/match data/clock, programs prescaler from `clock-frequency`, registers with OF MDIO, and stores bus.

State and persistence: runtime state is regmap-backed registers, optional clock enable, reset bits, and bus private data. No storage persists after unload.

Dependencies/integration: depends on REGMAP_MMIO, Ocelot MFD helpers, reset/clock frameworks, OF MDIO, and phylib. `mscc_miim_setup` lets other drivers reuse the MIIM callbacks with existing regmaps.

Risks and test signals: risks include high-resolution-timer fallback behavior, optional read-error ignore policy, prescaler bounds, long reset delay, and regmap creation failures. Tests should cover exported setup, register errors, clock-frequency validation, reset variants, and read error bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mscc-miim.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mux-bcm-iproc.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mux-bcm-iproc.c

Purpose: Broadcom iProc MDIO mux controller that provides a parent MDIO bus and child mux buses for internal/external selections.

Important APIs/types/functions: `struct iproc_mdiomux_desc` stores mux handle, base, device, mii_bus, and core clock. Core functions are `mdio_mux_iproc_config`, `start_miim_ops`, C22/C45 callbacks, `mdio_mux_iproc_switch_fn`, probe/remove, and PM suspend/resume.

Control flow: probe maps registers, handles legacy unaligned base resources, obtains/enables optional core clock, registers a parent mii_bus with C22/C45 callbacks, initializes child buses via `mdio_mux_init`, then configures scan/clock registers. Switch function encodes desired child as internal/external and bus ID. Transactions reset/clear ctrl, wait stat done state transitions, program param/address/control registers, and return read data or status.

State and persistence: runtime state includes current mux child in mdio-mux core, clock enable, hardware rate/selection registers, and mii_bus objects. PM disables/re-enables clock and reconfigures registers.

Dependencies/integration: depends on `MDIO_BUS_MUX`, OF MDIO, clocks, iopoll, platform MMIO, and phylib. Compatible string is `brcm,mdio-mux-iproc`.

Risks and test signals: risks include resource alignment compatibility, param register bit accumulation, PM restore, clock rate assumptions, and child bus registration failure cleanup. Tests should cover C22/C45 transactions, internal/external child switching, suspend/resume, and malformed child `reg` values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mux-bcm-iproc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mux-bcm6368.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mux-bcm6368.c

Purpose: Broadcom BCM6368 MDIO mux controller for selecting internal versus external PHY buses.

Important APIs/types/functions: `struct bcm6368_mdiomux_desc` stores mux handle, base, device, parent mii_bus, and `ext_phy` selection. Core functions are `bcm6368_mdiomux_read`, `bcm6368_mdiomux_write`, `bcm6368_mdiomux_switch_fn`, probe, and remove.

Control flow: probe maps the integrated register region, allocates/registers a parent mii_bus, masks PHYs from parent auto-scan, then calls `mdio_mux_init` to create child buses. The switch function updates `ext_phy`; subsequent reads/writes include or omit `MDIOC_EXT_MASK`, write command registers, delay 50 us, and read/write data.

State and persistence: runtime state is the `ext_phy` flag, mux child state in mdio-mux core, MMIO registers, and bus objects. No persistent storage exists.

Dependencies/integration: depends on OF MDIO, BMIPS/compile-test config, mdio-mux core, platform bus, and phylib. Compatible string is `brcm,bcm6368-mdio-mux`.

Risks and test signals: risks include no busy/status polling, raw MMIO ordering, child `reg` values treated directly as boolean external selection, and parent phy mask assumptions. Tests should cover internal/external child reads/writes, mux init failure cleanup, and timing on real hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mux-bcm6368.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mux-gpio.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mux-gpio.c

Purpose: generic GPIO-controlled MDIO mux driver that selects child buses by driving a GPIO array.

Important APIs/types/functions: `struct mdio_mux_gpio_state` stores GPIO descriptors and mux handle. Core functions are `mdio_mux_gpio_switch_fn`, probe, and remove.

Control flow: probe obtains a GPIO descriptor array as outputs, allocates state, and calls `mdio_mux_init` with no explicit parent bus, so the core locates `mdio-parent-bus`. The switch function compares current/desired child values, places `desired_child` into a bitmap, and calls `gpiod_multi_set_value_cansleep`.

State and persistence: runtime state is GPIO output levels, mux handle, and mdio-mux child bus state. No persistent storage exists.

Dependencies/integration: depends on OF_GPIO, OF MDIO, mdio-mux core, GPIO consumer API, and platform bus. Supports `mdio-mux-gpio` and legacy `cavium,mdio-mux-sn74cbtlv3253`.

Risks and test signals: risks include child values wider than available GPIOs, bitmap sizing by `desired_child` type, sleeping GPIO operations under MDIO mux lock, and missing parent bus defer. Tests should cover multi-bit selections, repeated same-child no-op, missing GPIOs, and parent bus deferral.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mux-gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mux-meson-g12a.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mux-meson-g12a.c

Purpose: Amlogic G12A MDIO mux/glue driver selecting external MDIO or an internal Ethernet PHY and registering the internal EPHY PLL with the common clock framework.

Important APIs/types/functions: `struct g12a_mdio_mux` stores registers, mux handle, and PLL clock. `struct g12a_ephy_pll` implements `clk_hw`. Key functions are PLL ops, `g12a_enable_internal_mdio`, `g12a_enable_external_mdio`, `g12a_mdio_switch_fn`, `g12a_ephy_glue_clk_register`, probe, and remove.

Control flow: probe maps registers, enables peripheral clock, registers input mux and EPHY PLL clocks, and initializes mdio-mux children. Switching to internal enables/locks PLL, programs PHY identity/control/source registers, and waits for power-up. Switching external clears mux/source and disables PLL when enabled.

State and persistence: runtime state is register programming for PLL and PHY control, clock enable state, and mdio-mux child selection. No persistent storage exists.

Dependencies/integration: depends on COMMON_CLK, OF MDIO, HAS_IOMEM, mdio-mux core, and platform bus. Compatible string is `amlogic,g12a-mdio-mux`.

Risks and test signals: risks include PLL lock timeout, `__clk_is_enabled` usage, hard-coded PLL/PHY magic values, child ID assumptions 0/1, and cleanup with PLL enabled. Tests should cover clock registration, internal/external switching, invalid child IDs, and remove after internal selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mux-meson-g12a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mux-meson-gxl.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mux-meson-gxl.c

Purpose: Amlogic GXL MDIO mux/glue driver selecting between external MDIO and an internal Ethernet PHY.

Important APIs/types/functions: `struct gxl_mdio_mux` stores registers and mux handle. Core functions are `gxl_enable_internal_mdio`, `gxl_enable_external_mdio`, `gxl_mdio_switch_fn`, probe, and remove.

Control flow: probe maps registers, enables the `ref` clock, and calls `mdio_mux_init`. Switching internal programs PHY config, reset signal, PHY ID expected by the Meson GXL PHY driver, enables PHY, and delays for power-up. Switching external resets the mux/control register to external path.

State and persistence: state is hardware register selection, internal PHY enable/reset state, reference clock enable, and mdio-mux child state. No persistent storage exists.

Dependencies/integration: depends on OF MDIO, HAS_IOMEM, COMMON_CLK, mdio-mux core, and the matching Meson GXL PHY driver identity. Compatible string is `amlogic,gxl-mdio-mux`.

Risks and test signals: risks include hard-coded internal PHY address/ID coupling, missing external cleanup beyond register zeroing, delay sensitivity, and invalid child IDs. Tests should cover child IDs 0/1, ref clock failures, repeated switching, and PHY driver match after internal enable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mux-meson-gxl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mux-mmioreg.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mux-mmioreg.c

Purpose: simple memory-mapped register MDIO mux driver, typically for FPGA or glue registers.

Important APIs/types/functions: `struct mdio_mux_mmioreg_state` stores mux handle, physical address, register size, and mask. Key functions are `mdio_mux_mmioreg_switch_fn`, probe, and remove.

Control flow: probe obtains the MMIO resource, validates register width is 8/16/32 bits, reads `mux-mask`, verifies child `reg` values do not set unmasked bits, and calls `mdio_mux_init`. The switch function maps the register on each switch, reads current value, replaces masked bits with desired child, writes if changed, and unmaps.

State and persistence: hardware mux bits persist in the device register while powered. Driver state is the resource metadata and mux handle.

Dependencies/integration: depends on OF MDIO, HAS_IOMEM, mdio-mux core, platform bus, and phylib.

Risks and test signals: risks include repeated ioremap per switch, mask validation edge cases, concurrent external register modification, and only 8/16/32-bit width support. Tests should cover each register width, bad masks, child reg validation, same-child no-op, and parent bus deferral.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mux-mmioreg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mux-multiplexer.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mux-multiplexer.c

Purpose: MDIO mux driver using the generic kernel mux consumer subsystem for child selection.

Important APIs/types/functions: `struct mdio_mux_multiplexer_state` stores a `mux_control`, whether a deselect is needed, and mux handle. Core routines are `mdio_mux_multiplexer_switch_fn`, probe, and remove.

Control flow: probe obtains the mux control, stores state, and initializes mdio-mux children. The switch function no-ops when already selected, otherwise deselects the previous mux state when required, selects the desired child through `mux_control_select`, and records whether a later deselect is needed. Remove uninitializes child buses and deselects if selected.

State and persistence: runtime state is the mux subsystem's selected state, `do_deselect`, and child bus registrations.

Dependencies/integration: depends on OF MDIO, mdio-mux core, `MULTIPLEXER`, mux consumer API, and platform bus. Compatible string is `mdio-mux-multiplexer`.

Risks and test signals: risks include deselect/select ordering, mux provider failures while under MDIO locks, stale `do_deselect`, and parent-bus deferral. Tests should cover failed deselect/select, repeated same child, remove after selection, and mux provider probe deferral.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mux-multiplexer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mux.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mux.c

Purpose: core framework for MDIO bus multiplexers. It creates child mii_bus instances that switch a shared parent bus before forwarding MDIO operations.

Important APIs/types/functions: exports `mdio_mux_init` and `mdio_mux_uninit`. Internal types are `struct mdio_mux_parent_bus` and `struct mdio_mux_child_bus`; forwarding callbacks include C22/C45 read/write variants.

Control flow: `mdio_mux_init` locates the parent bus via `mdio-parent-bus` or uses a supplied bus, allocates parent state, iterates child nodes, reads each child `reg`, allocates a child bus, installs only the callbacks supported by the parent, registers it with OF MDIO, and returns a mux handle. Child operations lock the parent bus `mdio_lock` with mux nesting, call the driver switch function if needed, update current child, and forward to the parent callback. Uninit unregisters/frees child buses and releases the parent device.

State and persistence: runtime state tracks current child, parent ID counter, parent device reference, child bus list, and driver-provided switch data. No persistent storage exists.

Dependencies/integration: used by GPIO, MMIO, Broadcom, Amlogic, and generic mux drivers. Depends on OF MDIO, phylib, mii_bus locking, and driver-specific switch functions.

Risks and test signals: risks include child registration partial failures, parent reference leaks, `parent_count` global uniqueness only per boot, switch failure leaving current child stale, and callback absence. Tests should cover parent deferral, mixed C22/C45 parents, failed child registration, nested lock behavior, and uninit cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mvusb.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mvusb.c

Purpose: USB-to-MDIO adapter driver for Marvell Link Street development-board adapters.

Important APIs/types/functions: `struct mvusb_mdio` stores the USB device, mii_bus, and small command buffer. Key functions are `mvusb_mdio_read`, `mvusb_mdio_write`, probe, and disconnect. USB ID is vendor `0x1286`, product `0x1fa4`.

Control flow: probe allocates a devm mii_bus/private object, initializes reversed command preamble words, assigns C22 read/write callbacks, stores USB interface data, and registers with OF MDIO. Read writes a command to bulk OUT endpoint 2 then reads a 16-bit value from bulk IN endpoint 6. Write sends preamble/address/value over bulk OUT endpoint 2. Disconnect unregisters the bus.

State and persistence: runtime state is the USB device pointer and command buffer; no persistent storage exists.

Dependencies/integration: depends on USB core, OF MDIO, phylib, and hardware-specific bulk endpoint protocol.

Risks and test signals: risks include undocumented USB command format, fixed endpoints/timeouts, no Clause 45 support, and disconnect during transfers. Tests require the adapter or USB emulation to validate read/write commands, timeout handling, and unplug cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mvusb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-octeon.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-octeon.c

Purpose: platform frontend for Cavium OCTEON MDIO buses using the common Cavium callbacks.

Important APIs/types/functions: probe/remove allocate and manage `struct cavium_mdiobus`; callbacks are imported from `mdio-cavium.c`. Hardware enable is controlled through `union cvmx_smix_en` and `SMI_EN`.

Control flow: probe allocates a devm mii_bus with Cavium private state, maps SMI registers, enables the SMI block, sets bus name/id/parent and C22/C45 callbacks, stores platform data, and registers with OF MDIO. On registration failure or remove it disables SMI and unregisters the bus.

State and persistence: runtime state is the enabled SMI hardware bit, register base, cached mode in common code, and registered bus. No persistent storage exists.

Dependencies/integration: depends on OF MDIO, HAS_IOMEM, `MDIO_CAVIUM`, OCTEON-compatible DT node `cavium,octeon-3860-mdio`, and phylib.

Risks and test signals: risks include enabling hardware before registration failure, pointer-form bus IDs, C22/C45 common-code behavior, and 64-bit accessor correctness. Tests should cover probe failure cleanup, remove disable, C22/C45 transactions, and OF PHY child discovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-octeon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-pic64hpsc.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-pic64hpsc.c

Purpose: Microchip PIC64-HPSC/HX Clause 22 MDIO controller driver.

Important APIs/types/functions: `struct pic64hpsc_mdio_dev` stores MMIO base. Core functions are `pic64hpsc_mdio_wait_trigger`, `pic64hpsc_mdio_c22_read`, `pic64hpsc_mdio_c22_write`, and probe.

Control flow: probe maps registers, obtains/enables the clock, reads optional `clock-frequency` defaulting to 2.5 MHz, computes/publishes the prescaler, assigns C22 callbacks, and registers with `devm_of_mdiobus_register`. Reads wait for idle, program frame config with trigger/read/PHY/register/SOF, wait, validate READOK unless ignored by `phy_ignore_ta_mask`, and return data. Writes wait, program write-data register, then trigger a write frame.

State and persistence: runtime state is prescaler and frame registers plus bus private data. No persistent storage exists.

Dependencies/integration: depends on ARCH_MICROCHIP or compile test, OF MDIO, HAS_IOMEM, clock framework, and phylib. Compatible string is `microchip,pic64hpsc-mdio`.

Risks and test signals: risks include prescaler range validation, READOK interpretation, write completion not re-polled after trigger, and no Clause 45 support. Tests should cover clock-frequency bounds, read timeout, ignored TA mask, and OF registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-pic64hpsc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-realtek-rtl9300.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-realtek-rtl9300.c

Purpose: MDIO controller for Realtek RTL9300-family switch SoCs where MDIO access is abstracted through switch port polling hardware.

Important APIs/types/functions: `struct rtl9300_mdio_priv` stores regmap, HW mutex, valid port bitmap, per-port SMI bus/address maps, C45 mode per SMI bus, and bus pointers. `struct rtl9300_mdio_chan` binds a child mii_bus to one SMI bus. Key functions are C22/C45 read/write callbacks, `rtl9300_mdiobus_map_ports`, `rtl9300_mdiobus_probe_one`, `rtl9300_mdiobus_init`, and probe.

Control flow: probe obtains parent syscon regmap, maps switch `ethernet-ports` to MDIO bus/address using `phy-handle`, creates one mii_bus per child MDIO node, detects whether each SMI bus must operate in C45 mode, then programs port address, polling selection, and global interface mode registers. Access callbacks map PHY address to switch port, lock hardware, program control/data registers, wait for command clear, and return data or fail status.

State and persistence: runtime state includes port maps, bus C45 mode, regmap hardware configuration, and mutex-protected access. The programmed switch registers persist until reset or reconfiguration.

Dependencies/integration: depends on Realtek RTL platform, MFD syscon, OF/fwnode graph properties, phylib, and switch-port DT layout.

Risks and test signals: risks include incorrect port-to-PHY mapping, no mixed C22/C45 on the same SMI bus, tight polling timeouts, and hardware access shared with switch subsystems. Tests should cover DT mapping validation, duplicate/illegal ports, C22/C45 buses, fail bit handling, and concurrent reads/writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-realtek-rtl9300.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-regmap.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-regmap.c

Purpose: library that exposes a regmap-backed, nontraditional MDIO device as a virtual Clause 22 mii_bus.

Important APIs/types/functions: `struct mdio_regmap_priv` stores regmap and the one valid PHY address. Exported `devm_mdio_regmap_register` consumes `struct mdio_regmap_config` and returns the registered mii_bus. Callbacks are `mdio_regmap_read_c22` and `mdio_regmap_write_c22`.

Control flow: registration validates `config->parent`, allocates a devm mii_bus under the parent, stores regmap/address, assigns name/id/parent and callbacks, sets `phy_mask` for optional autoscan of the valid address only or no autoscan, and calls `devm_mdiobus_register`. Reads/writes reject all addresses except `valid_addr`, then map MDIO register numbers directly to regmap offsets.

State and persistence: runtime state is the regmap pointer, valid address, bus object, and underlying register contents. No independent persistent storage exists.

Dependencies/integration: depends on REGMAP, phylib, MDIO consumers that build the config, and optional OF MDIO users. It is library-style and exports GPL symbol.

Risks and test signals: risks include direct register-number-to-regmap-offset assumptions, only Clause 22 support, autoscan mask mistakes, and parent/dev mismatch in devm allocation. Tests should cover invalid address rejection, autoscan masks, read/write error propagation, and registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-regmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-sun4i.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-sun4i.c

Purpose: Allwinner sun4i EMAC MDIO controller driver.

Important APIs/types/functions: `struct sun4i_mdio_data` stores MMIO base and optional PHY regulator. Core callbacks are `sun4i_mdio_read`, `sun4i_mdio_write`, probe, and remove.

Control flow: probe allocates mii_bus/private data, maps registers, obtains/enables optional `phy` regulator, assigns callbacks, registers with OF MDIO, and stores the bus. Reads and writes program PHY/register address, set MCMD to start, poll MIND busy with a 100 ms jiffies timeout and 1 ms sleep, clear MCMD, then read MRDD or write MWTD.

State and persistence: runtime state is MMIO register values, optional regulator enable state, and bus private data. Remove unregisters, disables regulator, and frees bus.

Dependencies/integration: depends on ARCH_SUNXI or compile test, OF MDIO, regulator framework, platform MMIO, and phylib. Compatible strings include `allwinner,sun4i-a10-mdio` and deprecated `allwinner,sun4i-mdio`.

Risks and test signals: risks include regulator optional/defer handling, polling while sleeping, read/write command ordering, and no Clause 45 support. Tests should cover regulator paths, timeout, OF registration, remove cleanup, and deprecated compatible coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-sun4i.c -->
