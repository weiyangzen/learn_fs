# Research: subset-b-004781

Work item `subset-b-004781` covers the Atmel AT76 USB mac80211 driver and selected Broadcom b43 build, bus, debugfs, DMA, LED, and G-PHY local-oscillator files under `sources/distributed-fs/ceph-client/drivers/net/wireless/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/atmel/at76c50x-usb.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/atmel/at76c50x-usb.c

## Purpose
This file implements the USB mac80211 driver for Atmel AT76C503/AT76C505-family 802.11b adapters. It binds many USB VID/PID pairs to a board type, loads board-specific binary firmware, initializes the USB device, exposes a `struct ieee80211_hw`, and translates mac80211 operations into Atmel USB vendor/class control requests and bulk URBs.

## Important APIs, Types, And Functions
The driver registers `at76_driver` with `usb_register()` in `at76_mod_init()` and unregisters it in `at76_mod_exit()`. `dev_table` maps USB IDs to `enum board_type` values stored in `driver_info`. Firmware is represented by `struct fwentry firmwares[]`, protected by `fw_mutex`, and requested through `request_firmware()`.

Firmware and startup paths are centered on `at76_load_firmware()`, `at76_load_internal_fw()`, `at76_usbdfu_download()`, `at76_load_external_fw()`, `at76_get_op_mode()`, `at76_get_hw_config()`, and `at76_startup_device()`. Device control uses `at76_set_card_command()`, `at76_wait_completion()`, `at76_set_mib()`, and helper setters for radio, power management, preamble, fragmentation, RTS, autorate fallback, and WEP.

mac80211 integration is via `at76_ops`: `tx`, `start`, `stop`, `add_interface`, `remove_interface`, `config`, `bss_info_changed`, `configure_filter`, `hw_scan`, and `set_key`. USB data flow uses `at76_alloc_urbs()`, `at76_submit_rx_urb()`, `at76_rx_callback()`, `at76_rx_tasklet()`, `at76_mac80211_tx()`, and `at76_mac80211_tx_callback()`.

## Control Flow
Probe starts by loading and parsing firmware, reading the current operation mode, optionally downloading the DFU internal firmware and returning for re-enumeration, then optionally downloading external firmware. Once firmware is ready, the driver allocates a mac80211 hardware object, stores it with `usb_set_intfdata()`, copies firmware and board metadata, allocates URBs, reads hardware config for MAC and regulatory domain, configures default channel/rate/WEP/scan/radio state, and registers the hardware with mac80211.

Starting the interface submits the RX URB, sends `CMD_STARTUP`, enables radio, pushes MIB settings, and starts monitor-mode passive scanning until association. Scanning sends `CMD_SCAN`, marks `priv->scanning`, stops queues, and polls completion through delayed work. When scan completes it optionally rejoins the cached BSSID, clears scan state, notifies mac80211, and wakes queues.

Transmit accepts one outstanding bulk TX URB. It handles a join workaround by intercepting authentication frames and queuing `CMD_JOIN` before transmitting. Otherwise it stops queues, fills an Atmel TX header with length, rate, and padding, submits the bulk URB, and reports completion with `ieee80211_tx_status_irqsafe()`. Receive uses one bulk RX URB at a time; the completion schedules a tasklet, the tasklet validates URB status, strips the Atmel RX header, builds `ieee80211_rx_status`, guesses frequency during hardware scan from beacon/probe response DS parameters, passes the skb to mac80211, and resubmits another RX URB.

Disconnect clears interface data, marks the device unplugged, kills tasklet/URBs, unregisters mac80211 if needed, frees buffers and skb state, deletes the LED trigger timer, and frees the hardware object.

## State And Persistence
Persistent runtime state lives in `struct at76_priv`: USB device, TX/RX URBs, `rx_skb`, `tx_skb`, bulk buffer, mutex, work items, tasklet, WEP keys, channel, BSSID/ESSID, scan flags, power management, regulatory domain, firmware version, radio/promisc state, and registration flags. Firmware blobs are cached in static `firmwares[]` until module exit. Hardware settings persist inside the device firmware through MIB writes and card commands, not on disk. TX LED activity is tracked by global `tx_activity` and `ledtrig_tx_timer`.

## Dependencies And Integration Points
The file depends on Linux USB core, firmware loader, LED triggers, skbuff APIs, cfg80211/mac80211, WEP cipher constants, and kernel workqueue/tasklet/timer primitives. It consumes protocol layouts from `at76c50x-usb.h`. It integrates with userspace through firmware files named by `MODULE_FIRMWARE()`, mac80211/cfg80211 wireless interfaces, USB hotplug matching, and optional kernel log debugging controlled by the `debug` module parameter.

## Risks
The code trusts firmware offsets and lengths after only basic size and board-type checks; CRC is explicitly not checked. The RX path uses a single skb/URB and must handle unplug, URB cancellation, and resubmission carefully. `at76_mac80211_start()` returns 0 even if startup commands fail after RX submission, so hardware-start errors may be hidden from mac80211. `at76_mac80211_tx()` does not free or status the skb if `usb_submit_urb()` fails after assigning `priv->tx_skb`, which is a potential leak/stall path. Promiscuous state is intentionally racy because `configure_filter` must be atomic. The scan poll path has a FIXME for missing maximum scan completion time. WEP is the only hardware key path; other ciphers return `-EOPNOTSUPP`.

## Test Signals
Useful validation signals are successful firmware request/download, USB re-enumeration after internal firmware, `ieee80211_register_hw()` success, correct MAC/regdomain logs, RX/TX through mac80211, scan completion events, association after auth-frame join workaround, WEP set/unset behavior, clean disconnect during active URBs, and module unload releasing firmware and LED trigger. Fault tests should cover missing firmware, wrong board type in firmware, USB control timeouts, `usb_submit_urb()` failures, unplug during scan/TX/RX, and unsupported cipher setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/atmel/at76c50x-usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/atmel/at76c50x-usb.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/atmel/at76c50x-usb.h

## Purpose
This header defines the on-device command protocol, MIB layouts, firmware header format, board identifiers, and private driver state for `at76c50x-usb.c`. It is the contract between the driver and AT76 firmware/USB control messages.

## Important APIs, Types, And Functions
`enum board_type` identifies supported AT76 board/Radio combinations. Command/status constants define `CMD_STARTUP`, `CMD_SCAN`, `CMD_JOIN`, radio commands, MIB commands, and completion states such as `CMD_STATUS_COMPLETE` and `CMD_STATUS_IN_PROGRESS`. Operation-mode constants classify devices with flash, without flash, DFU mode, and hardware-config mode.

Packed hardware/firmware structures include `union at76_hwcfg`, `struct at76_card_config`, `struct at76_command`, `struct at76_rx_buffer`, `struct at76_tx_buffer`, scan/join/IBSS request structures, MIB records (`mib_local`, `mib_mac`, `mib_mac_mgmt`, `mib_mac_wep`, `mib_phy`, `mib_fw_version`, `mib_mdomain`), `struct set_mib_buffer`, `struct at76_fw_header`, `struct reg_domain`, and `struct fwentry`. `struct at76_priv` is the primary runtime state container.

## Control Flow
The header has no executable flow, but its layout dictates flow in the C file: probe selects a `board_type`, requests the matching `fwentry`, parses `at76_fw_header`, gets one of the hardware-config variants, sends `at76_card_config` with `CMD_STARTUP`, uses `set_mib_buffer` for MIB updates, submits/receives `at76_tx_buffer` and `at76_rx_buffer` over bulk pipes, and tracks all state in `at76_priv`.

## State And Persistence
`struct at76_priv` stores all live driver state: USB pipes and URBs, RX/TX skbs, work items, tasklet, WEP key material, channel/BSSID/ESSID, radio/promisc/scan state, power mode, regulatory domain, MAC address, firmware version, and mac80211 registration flag. `struct fwentry` stores firmware blob ownership and parsed internal/external firmware pointers. All protocol structures are packed because they are sent to or read from device firmware.

## Dependencies And Integration Points
The header assumes kernel networking and mac80211 types such as `ETH_ALEN`, `IW_ESSID_MAX_SIZE`, `IEEE80211_MAX_FRAG_THRESHOLD`, `IEEE80211_COUNTRY_STRING_LEN`, `struct usb_device`, `struct urb`, `struct ieee80211_hw`, `struct sk_buff`, work structs, tasklets, and mutexes. It is private to the Atmel USB driver rather than a public subsystem header.

## Risks
Because the structures are device ABI, field order, size, endianness, and packing are high risk. Several fields are marked reserved or unknown, so changes can break old firmware. `struct at76_priv` includes a legacy `netdev_registered` bit even though the driver uses mac80211 registration, suggesting historical drift. WEP key storage is fixed-size and must only be written with validated key lengths. `set_mib_buffer` multiplexes byte, word, address, and WEP payloads and requires correct `type`, `size`, and `index`.

## Test Signals
Compile-time size/layout warnings, successful USB startup, MIB get/set operations, valid RX/TX header parsing, firmware-version reporting, and WEP key programming exercise this header. Regression tests should emphasize endian-sensitive fields, packed layout compatibility, and each board-type hardware-config variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/atmel/at76c50x-usb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/Kconfig

## Purpose
This Kconfig file creates the `WLAN_VENDOR_BROADCOM` menu gate for Broadcom wireless drivers and sources the Broadcom wireless subdriver configuration files.

## Important APIs, Types, And Functions
The central symbol is `config WLAN_VENDOR_BROADCOM`, a bool defaulting to `y`. When enabled, it includes `b43/Kconfig`, `b43legacy/Kconfig`, and `brcm80211/Kconfig`.

## Control Flow
Kconfig evaluation first presents the vendor menu. If the symbol is disabled, all nested Broadcom driver prompts are skipped. If enabled, Kconfig continues into the b43, b43legacy, and brcm80211 option sets.

## State And Persistence
The only persisted state is the kernel configuration symbol in `.config`. It does not build code directly; it controls visibility of child options.

## Dependencies And Integration Points
This file is included by the higher-level wireless Kconfig hierarchy. It integrates the b43 soft-MAC driver, legacy b43 driver, and Broadcom brcm80211 drivers into the vendor organization used by Linux wireless configuration.

## Risks
The main risk is menu reachability: disabling this symbol hides all child Broadcom wireless options even though it has no direct build output. Source paths must remain correct as subdriver directories move.

## Test Signals
`make menuconfig` or `scripts/kconfig/conf` should show Broadcom options only when `WLAN_VENDOR_BROADCOM=y`, and downstream symbols should remain selectable under the vendor gate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/Makefile

## Purpose
This Makefile connects selected Broadcom wireless Kconfig symbols to their driver subdirectories.

## Important APIs, Types, And Functions
It adds `b43/` for `CONFIG_B43`, `b43legacy/` for `CONFIG_B43LEGACY`, and `brcm80211/` for either `CONFIG_BRCMFMAC` or `CONFIG_BRCMSMAC`.

## Control Flow
During kbuild traversal, each `obj-$(CONFIG_...) += dir/` line conditionally descends into a subdirectory if the corresponding symbol is built in or modular.

## State And Persistence
The file has no runtime state. Build state is the selected `.config` values and generated object lists.

## Dependencies And Integration Points
It is consumed by the kernel kbuild system from the parent wireless Makefile. It must stay consistent with symbols declared in the Broadcom Kconfig subtree.

## Risks
Incorrect symbol-to-directory mapping would silently omit a driver or build the wrong directory. The two brcm80211 symbols intentionally share one directory, so refactors must preserve that aggregation.

## Test Signals
Builds with `CONFIG_B43`, `CONFIG_B43LEGACY`, `CONFIG_BRCMFMAC`, and `CONFIG_BRCMSMAC` as `y`/`m` should descend into the expected subdirectories and produce the corresponding modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/Kconfig

## Purpose
This Kconfig file defines the Broadcom b43 soft-MAC driver and its bus, PHY, LED, HWRNG, SDIO, and debug options.

## Important APIs, Types, And Functions
`config B43` is the main tristate and depends on `(BCMA_POSSIBLE || SSB_POSSIBLE) && MAC80211 && HAS_DMA`; it selects `FW_LOADER` and `CORDIC`, and selects BCMA/SSB through internal bus symbols. The bus choice selects `B43_BCMA`, `B43_SSB`, or both. Additional options autoselect SSB PCI host and PCICORE support when possible. Feature symbols include `B43_SDIO`, `B43_BCMA_PIO`, `B43_PIO`, `B43_PHY_G`, `B43_PHY_N`, `B43_PHY_LP`, `B43_PHY_HT`, broken `B43_PHY_LCN`/`B43_PHY_AC`, `B43_LEDS`, `B43_HWRNG`, and `B43_DEBUG`.

## Control Flow
Kconfig first enables the main driver, then requires a supported bus selection. PHY and auxiliary options become visible or default-enabled according to bus and subsystem availability. Debugfs support is compiled only when `B43_DEBUG=y`.

## State And Persistence
The symbols persist in the kernel `.config` and drive compilation in `b43/Makefile`. Runtime b43 behavior changes materially based on these symbols: bus abstraction availability, PHY code inclusion, PIO fallback, SDIO support, LED class integration, HWRNG registration, and debugfs code.

## Dependencies And Integration Points
The file integrates b43 with mac80211, BCMA, SSB, SDIO host support, LED class/mac80211 LED triggers, HW random core, firmware loader, and Kconfig's `BROKEN` gate for unsupported PHYs. It also documents that proprietary V4 firmware must be installed separately using b43-fwcutter.

## Risks
Wrong dependencies can create build failures or unusable configurations, especially around bus glue and optional PHY files. Defaulting many PHYs to `y` broadens build coverage but increases maintenance surface. The LCN and AC PHYs are intentionally gated by `BROKEN` because enabling them is documented to crash the driver.

## Test Signals
Kconfig tests should cover BCMA-only, SSB-only, combined bus, SDIO, LEDs, HWRNG, and debug combinations. Build tests should ensure each enabled PHY has matching objects and that disabled debug/LED options use the stub paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/Makefile

## Purpose
This Makefile assembles the `b43.o` composite module from mandatory driver objects and optional objects selected by Kconfig.

## Important APIs, Types, And Functions
Mandatory objects include `main.o`, `bus.o`, `phy_common.o`, `sysfs.o`, `xmit.o`, `dma.o`, `pio.o`, `rfkill.o`, and `ppr.o`. Optional groups add G-PHY support (`phy_g.o tables.o lo.o wa.o`), N-PHY tables/radios/PHY, LP-PHY, HT-PHY, LCN, AC, LEDs, SDIO, and debugfs. `obj-$(CONFIG_B43) += b43.o` exposes the composite target.

## Control Flow
kbuild expands `b43-y` and `b43-$(CONFIG_...)` lists according to `.config`, compiles selected objects, links them into `b43.o`, and then either links it built-in or emits `b43.ko`.

## State And Persistence
No runtime state exists here. Build composition is derived entirely from selected Kconfig symbols.

## Dependencies And Integration Points
The object list must match declarations in `b43/Kconfig` and source-level references. For example, `lo.o` is included only with `CONFIG_B43_PHY_G`, while `debugfs.o` is included only with `CONFIG_B43_DEBUG`.

## Risks
Missing an object in a feature group causes unresolved symbols; including it without dependencies can compile unsupported code. Feature grouping is important because many source files assume specific PHY or subsystem structures exist.

## Test Signals
Compile matrix tests for each PHY/debug/LED/SDIO option should produce either no unresolved symbols or expected stubs. `nm`/modpost output can confirm optional objects are present only when selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/b43.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/b43.h

## Purpose
`b43.h` is the main private header for the Broadcom b43 driver. It defines register maps, shared-memory offsets, host flags, IRQ bits, firmware metadata, DMA/PIO top-level containers, key/QoS/statistics structures, and the central `b43_wldev` and `b43_wl` runtime objects.

## Important APIs, Types, And Functions
The file defines extensive MMIO constants for DMA, PIO, MAC, PHY, radio, GPIO, TSF, WEP, IFS, RNG, and TX FIFO registers. Shared-memory constants cover firmware metadata, host flags, channel state, power-control values, crypto tables, WME/QoS, beacon/probe templates, and rate maps. Firmware structures include `struct b43_fw_header`, `struct b43_iv`, `struct b43_request_fw_context`, `struct b43_firmware_file`, and `struct b43_firmware`.

`struct b43_wldev` represents one 802.11 core and holds bus device, mac80211 owner, firmware, PHY, DMA/PIO engines, IRQ state, periodic/restart work, key table, stats, debug state, and initialization status. `struct b43_wl` represents the wireless hardware/mac80211 instance across cores and stores the current device, mutex/spinlock, interface state, queues, beacon state, QoS parameters, work items, LEDs, and optional HWRNG state.

Inline wrappers (`b43_read16`, `b43_write16`, `b43_read32`, `b43_write32`, `b43_block_read`, `b43_block_write`, `b43_device_enable`, `b43_bus_powerup`, queue stop/wake helpers) route core code through `struct b43_bus_dev` operations.

## Control Flow
Most b43 source files include this header and operate on `b43_wldev` under `wl->mutex` for high-level operations and `hardirq_lock` for IRQ mask state. Data paths choose DMA or PIO via `b43_using_pio_transfers()`. Bus calls are abstracted so the same core code can run on SSB or BCMA. The `b43_status()`/`b43_set_status()` helpers define the device lifecycle states from uninitialized to initialized to started.

## State And Persistence
The header declares the in-memory state model. There is no disk persistence. Hardware and firmware state persists only in device registers, shared memory, and firmware RAM. `b43_wl` is mac80211-facing state; `b43_wldev` is core-specific hardware state. The firmware cache in `b43_firmware` stores loaded blobs and parsed revision/format/opensource flags.

## Dependencies And Integration Points
It depends on kernel spinlocks, interrupts, completions, HWRNG, BCMA, SSB, and mac80211. It includes b43 component headers for debugfs, LEDs, rfkill, bus, LO calibration, and common PHY definitions. Register definitions are consumed by DMA, PIO, xmit, PHY, rfkill, LED, debugfs, firmware, and main control code.

## Risks
Because this file centralizes hardware ABI constants, incorrect register bits or shared-memory offsets can break unrelated subsystems. The inline accessors rely on a correctly initialized `b43_bus_dev` vtable. `b43_wldev` uses a union for DMA/PIO engines, so `__using_pio_transfers` must be correct before accessing either side. Queue helpers collapse non-QoS traffic to queue 0, which must match mac80211 queue state. Status updates rely on atomic write plus memory barrier ordering.

## Test Signals
Compile coverage across BCMA/SSB, DMA/PIO, debug/LED/HWRNG, and PHY combinations is the main structural signal. Runtime signals include correct register access through both bus types, orderly status transitions, queue stop/wake behavior, firmware metadata parsing, and absence of union misuse when switching between DMA and PIO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/b43.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/bus.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/bus.c

## Purpose
This file implements b43's bus abstraction layer, adapting BCMA and SSB devices into a common `struct b43_bus_dev` used by the rest of the driver.

## Important APIs, Types, And Functions
For BCMA, it defines wrappers around `bcma_core_is_enabled()`, `bcma_core_enable()`, `bcma_core_disable()`, `bcma_read16/32()`, `bcma_write16/32()`, and block I/O. `b43_bus_dev_bcma_init()` allocates and populates a bus device from `struct bcma_device`. For SSB, equivalent wrappers call `ssb_bus_may_powerdown()`, `ssb_bus_powerup()`, `ssb_device_is_enabled()`, `ssb_device_enable()`, `ssb_device_disable()`, `ssb_read/write`, and block I/O; `b43_bus_dev_ssb_init()` builds from `struct ssb_device`. `b43_bus_get_wldev()` and `b43_bus_set_wldev()` bridge bus drvdata to b43 core state.

## Control Flow
The probe path for a BCMA or SSB core calls the matching initializer. That initializer allocates `b43_bus_dev`, sets bus type and native device pointer, installs vtable functions, copies device/dma/irq metadata, board/chip/core IDs, and points to the bus SPROM. Core b43 code then uses inline wrappers from `b43.h`, which dispatch through these function pointers.

## State And Persistence
The file allocates one `b43_bus_dev` per core and stores static metadata copied from bus structures. Runtime state is the vtable and pointers back to BCMA/SSB objects. No persistent state is written.

## Dependencies And Integration Points
It depends on BCMA and SSB APIs selected by Kconfig. It also has a BCM47XX BCMA-specific write-flush workaround for BCM4716 PCI-hosted BCMA devices. It integrates with drvdata storage on native bus devices so later callbacks can recover the `b43_wldev`.

## Risks
Wrong metadata copying can affect DMA device selection, IRQ handling, board quirks, and PHY behavior. BCMA powerdown/powerup wrappers currently return 0 with commented calls, so BCMA power-management semantics are intentionally incomplete or delegated elsewhere. The `flush_writes` quirk is platform-specific and must be narrowly applied.

## Test Signals
BCMA and SSB probe should populate identical core fields for the same hardware class, register access should work through b43 inline wrappers, drvdata get/set should round-trip, and BCM47XX BCMA devices should perform write flushing when required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/bus.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/bus.h

## Purpose
This header declares the common bus-device interface that lets b43 core code operate on either BCMA or SSB hardware.

## Important APIs, Types, And Functions
`enum b43_bus_type` is compiled with BCMA and/or SSB variants. `struct b43_bus_dev` stores the native bus pointer, vtable callbacks for power, enable/disable, MMIO and block I/O, flush-write flag, Linux device and DMA device pointers, IRQ, board/chip/core IDs, and SPROM pointer. Inline helpers identify host type: `b43_bus_host_is_pcmcia()`, `b43_bus_host_is_pci()`, and `b43_bus_host_is_sdio()`. Initializers and drvdata helpers are declared for bus-specific code.

## Control Flow
Bus-specific probe code creates this object, then the rest of b43 dereferences only this common interface. Host-type helpers branch on bus type and native host/bus type fields.

## State And Persistence
`b43_bus_dev` is runtime metadata only. It persists for the lifetime of a b43 core and is freed by bus/core teardown outside this header.

## Dependencies And Integration Points
The header depends on BCMA and SSB types being available through b43 includes and Kconfig. Its fields are consumed by DMA, PHY, SPROM quirk logic, LED logic, and core device setup.

## Risks
Conditional enum contents mean code must not assume numeric bus type values across configurations. The shared `union` requires callers to check `bus_type` before accessing `bdev` or `sdev`. Incorrect `dma_dev` or `bus_sprom` pointers cascade into DMA mapping failures or board-quirk mistakes.

## Test Signals
Build tests with BCMA-only, SSB-only, and combined configs should compile all host helpers. Runtime tests should verify PCI/PCMCIA/SDIO host detection, MMIO read/write through the vtable, and stable board/chip/core metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/bus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/debugfs.c

## Purpose
This file implements b43's optional debugfs interface for direct MMIO/SHM inspection, controlled MMIO/SHM writes, TX status logging, manual controller restart, LO calibration inspection, and dynamic debug toggles.

## Important APIs, Types, And Functions
`b43_debugfs_init()` creates the root debugfs directory and `b43_debugfs_exit()` removes it. `b43_debugfs_add_device()` allocates a `b43_dfsentry`, TX status ring log, per-device directory, debugfs files, and dynamic debug bools. `b43_debugfs_remove_device()` tears them down. `b43_debugfs_log_txstat()` appends TX status reports to a circular log.

File handlers include `shm16read`, `shm16write`, `shm32read`, `shm32write`, `mmio16read`, `mmio16write`, `mmio32read`, `mmio32write`, `txstat`, `restart`, and `loctls`. Generic `b43_debugfs_read()` and `b43_debugfs_write()` route through a custom `b43_debugfs_fops` structure stored as debugfs aux data.

## Control Flow
Read/write calls recover `b43_wldev` from `file->private_data`, lock `dev->wl->mutex`, reject uninitialized devices, allocate/copy buffers, invoke the per-file handler, and then release the mutex. Read output is cached in `struct b43_dfs_file` until the user drains it. Address-setting write files store the next read address in `dev->dfsentry`; subsequent read files perform the actual hardware access.

## State And Persistence
Debugfs state lives in `struct b43_dfsentry`: cached read buffers, next MMIO/SHM addresses, dynamic debug flags, and TX status circular log. It is runtime-only and disappears on device removal/module unload. Dynamic debug flags can raise `b43_modparam_verbose` for more logging.

## Dependencies And Integration Points
The file depends on debugfs, file operations, user-copy helpers, b43 MMIO/SHM helpers, TX status structures, controller restart, and G-PHY LO data. It is compiled only with `CONFIG_B43_DEBUG`.

## Risks
This exposes raw hardware reads/writes to privileged debugfs users, so invalid writes can disrupt hardware. Address validation limits MMIO to below `0xF00`, checks alignment, and validates SHM routing/address, but semantic safety is still caller responsibility. Read buffering uses a 16 KiB allocation per file read and must be freed when consumed. `debugfs_remove(e->subdir)` removes only the subtree reference; teardown depends on debugfs lifetime rules.

## Test Signals
With `CONFIG_B43_DEBUG=y`, debugfs should create per-wiphy files, reject invalid addresses/alignment, read/write MMIO and SHM, log recent TX statuses, restart on writing `1` to `restart`, print LO data only for G-PHY, and cleanly remove files on device detach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/debugfs.h

## Purpose
This header declares b43 debugfs state and APIs when `CONFIG_B43_DEBUG` is enabled, and no-op stubs when debug support is disabled.

## Important APIs, Types, And Functions
`enum b43_dyndbg` lists runtime dynamic debug features for transmit power, DMA overflow/verbosity, periodic work, LO, firmware, keys, and verbose stats. Under debug config, `struct b43_txstatus_log`, `struct b43_dfs_file`, and `struct b43_dfsentry` define per-device debugfs state. Public functions are `b43_debug()`, `b43_debugfs_init()`, `b43_debugfs_exit()`, `b43_debugfs_add_device()`, `b43_debugfs_remove_device()`, and `b43_debugfs_log_txstat()`.

## Control Flow
Callers can use `b43_debug(dev, feature)` regardless of config. With debug disabled it returns false and all debugfs lifecycle/logging functions are inline no-ops. With debug enabled, calls are implemented by `debugfs.c`.

## State And Persistence
Debug-enabled builds store per-device debugfs directory pointers, cached file buffers, next raw access addresses, dynamic debug flags, and a TX status log. Disabled builds define no state beyond an empty interface.

## Dependencies And Integration Points
The header bridges b43 core, DMA, LO, and debugfs implementation code. It also lets other files compile without `#ifdef CONFIG_B43_DEBUG` around every debugfs call.

## Risks
The enabled/disabled ABI must stay source-compatible. Any new debugfs file in `debugfs.c` needs a matching `b43_dfsentry` field if it uses the generic cache helper. Dynamic debug enum order indexes a fixed bool array, so insertions affect saved mental mappings but not persistent ABI.

## Test Signals
Builds with and without `CONFIG_B43_DEBUG` should both compile. Disabled builds should have no debugfs side effects; enabled builds should allocate/free `b43_dfsentry` and log TX statuses safely.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/dma.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/dma.c

## Purpose
This file implements b43 DMA ring allocation, DMA engine setup/reset, TX descriptor submission, TX status cleanup, RX buffer recycling, RX overflow recovery, and direct FIFO RX toggling.

## Important APIs, Types, And Functions
It defines 32-bit and 64-bit DMA operation tables (`dma32_ops`, `dma64_ops`) for descriptor lookup/fill, TX index poking, suspend/resume, and RX index get/set. Ring setup and teardown use `b43_setup_dmaring()`, `alloc_ringmemory()`, `dmacontroller_setup()`, `b43_destroy_dmaring()`, and `b43_dma_free()`. Public entry points are `b43_dma_init()`, `b43_dma_tx()`, `b43_dma_handle_txstatus()`, `b43_dma_rx()`, `b43_dma_handle_rx_overflow()`, `b43_dma_tx_suspend()`, `b43_dma_tx_resume()`, and `b43_dma_direct_fifo_rx()`.

## Control Flow
Initialization detects engine type (`30`, `32`, or `64` bit), sets DMA mask/coherent mask, computes bus translation bits, picks parity behavior, creates five TX rings plus one RX ring, allocates coherent descriptor memory, initializes controllers, and pre-populates RX descriptors with mapped skbs. TX selects the multicast ring for after-DTIM frames or maps mac80211 queue priority to AC rings, checks free slots, generates a firmware TX header with a cookie, maps header and payload into two descriptors, writes multicast cookie when needed, memory-bars, and pokes the TX index.

TX completion parses the cookie back to ring and slot, verifies in-order status, can skip one missed header/data pair, restarts open-source firmware on larger ordering failures, unmaps header/payload DMA mappings, frees bounce buffers, fills mac80211 TX status, returns the skb, updates ring slot counts, wakes stopped queues, and schedules `tx_work`. RX polls from `ring->current_slot` to the hardware current slot, syncs the mapped skb for CPU, validates firmware length and poison marker, replaces the descriptor with a fresh buffer, unmaps the completed skb, strips the firmware frame offset, and passes it to `b43_rx()`. Overflow handling backs the hardware RX index up one slot to make all descriptors appear free again.

## State And Persistence
`struct b43_dmaring` tracks descriptor memory, metadata array, DMA base, slot count, used/current slots, frame offset, RX buffer size, controller index/base, type, stopped flag, queue priority, and debug statistics. Descriptor metadata stores skb, DMA address, and whether a descriptor is the last fragment. No disk persistence exists; hardware state is programmed into DMA controller registers.

## Dependencies And Integration Points
The file depends on Linux DMA mapping APIs, mac80211 skb/status APIs, b43 bus MMIO access, `xmit.c` helpers for TX header/status, `main.c` helpers for RX, restart, and power saving, and debugfs dynamic flags. It supports both SSB and BCMA DMA translation paths.

## Risks
This is a high-risk data path. Ring slot accounting must remain exact because each TX frame consumes two slots. DMA mapping failures trigger GFP_DMA bounce-buffer fallbacks; cleanup must unmap and free both header and payload correctly. RX poisoning detects untouched buffers, but length races require polling and fallback recycling. Out-of-order TX statuses can leak/stall rings unless recovery works. Queue wake logic appears inverted: if `tx_queue_stopped[prio]` is true, the code clears the flag but does not call `b43_wake_queue()`, while the else branch wakes when the flag was false. Any change here needs hardware/mac80211 queue testing. Ring initialization has a suspicious loop writing `ring->meta->skb` repeatedly rather than `ring->meta[i].skb`, which may leave most metadata unpoisoned.

## Test Signals
Important tests include DMA mask negotiation on 30/32/64-bit hardware, TX/RX traffic under each AC queue, multicast after-DTIM handling, ring-full queue stopping and waking, TX status cookie parsing, bounce-buffer paths with constrained DMA masks, RX poisoned-buffer drops, RX oversized-frame drops, overflow recovery, suspend/resume ordering, direct FIFO RX toggling from PIO code, and clean teardown after partial initialization failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/dma.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/dma.h

## Purpose
This header defines b43 DMA register constants, descriptor layouts, ring structures, operation vectors, and public DMA APIs.

## Important APIs, Types, And Functions
It defines DMA IRQ bits, 32-bit and 64-bit controller register offsets and bit masks, descriptor formats (`b43_dmadesc32`, `b43_dmadesc64`, `b43_dmadesc_generic`), ring memory sizes, RX frame offsets/buffer sizes, ring slot counts, pointer poison helpers, `struct b43_dmadesc_meta`, `struct b43_dma_ops`, `enum b43_dmatype`, `enum b43_addrtype`, and `struct b43_dmaring`. Inline `b43_dma_read()` and `b43_dma_write()` access controller registers relative to a ring MMIO base.

Public prototypes cover DMA init/free, TX suspend/resume, TX submit, TX status handling, RX overflow, RX polling, and direct FIFO RX mode.

## Control Flow
The implementation fills `b43_dmaring` with either 32-bit or 64-bit ops and uses register constants to program controllers and descriptors. The public API is called by b43 main/xmit/interrupt code depending on whether DMA transfers are active.

## State And Persistence
`struct b43_dmaring` is the key state object. It owns coherent descriptor memory, optional TX header cache, DMA address, slot counters, controller metadata, stopped state, queue priority, debug counters, and flexible descriptor metadata. State is runtime-only and synchronized through caller context and hardware interrupts.

## Dependencies And Integration Points
The header includes `b43.h`, so it has access to `struct b43_wldev`, bus MMIO wrappers, and mac80211 state. It is used by `dma.c`, debugfs TX status inspection, and interrupt/data path code.

## Risks
Descriptor bit definitions must match hardware exactly. `B43_TXRING_SLOTS` must stay divisible by the number of slots used per TX frame. RX buffer sizes depend on firmware header format and must remain large enough for max frames plus firmware offset. The poison pointer intentionally equals `ERR_PTR(-ENOMEM)` and should never be confused with a valid skb pointer.

## Test Signals
Compile checks catch descriptor struct use, but runtime validation requires successful DMA initialization, descriptor programming, TX/RX traffic, ring wraparound, debug statistics, and teardown without DMA API warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/leds.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/leds.c

## Purpose
This file maps b43 board/SPROM LED behavior descriptions to Linux LED class devices and mac80211 LED triggers, then drives GPIO bits to reflect radio, TX, RX, and association LED state.

## Important APIs, Types, And Functions
Low-level helpers `b43_led_turn_on()` and `b43_led_turn_off()` update `B43_MMIO_GPIO_CONTROL` respecting active-low wiring. `b43_led_update()` computes desired hardware state from LED trigger brightness plus radio enable state. `b43_leds_work()` applies pending state under `wl->mutex`. `b43_led_brightness_set()` is the LED subsystem callback. Registration flow uses `b43_register_led()`, `b43_unregister_led()`, `b43_map_led()`, and `b43_led_get_sprominfo()`. Public lifecycle functions are `b43_leds_register()`, `b43_leds_init()`, `b43_leds_stop()`, `b43_leds_exit()`, and `b43_leds_unregister()`.

## Control Flow
At registration time, the driver reads SPROM GPIO LED behavior bytes or falls back to hardcoded defaults when all bytes are `0xff`. Behavior codes are mapped to TX/RX, radio, or association LED class devices with default mac80211 triggers. Brightness changes from LED triggers atomically update requested state and queue work. The work item locks the driver, checks that a current started device exists, and updates each registered LED. Init synchronizes radio LED state with hardware rfkill/radio state, resets activity LEDs, and applies static on/off behaviors to unmapped LEDs.

## State And Persistence
LED runtime state is in `struct b43_leds` under `struct b43_wl`: four `struct b43_led` objects, a stop flag, and one work item. Each LED stores LED class device, GPIO index, active-low flag, name, requested brightness, and last hardware state. SPROM behavior is read from hardware configuration and not modified.

## Dependencies And Integration Points
The file depends on b43 MMIO access, rfkill/radio helpers, SPROM board data, LED classdev APIs, mac80211 LED trigger name helpers, and the driver's workqueue via `ieee80211_queue_work()`.

## Risks
SPROM fallback mappings are board-specific and can produce wrong LED behavior on unknown boards. Multiple behavior codes can map to the same LED object; duplicate registration returns `-EEXIST`. Brightness state is intentionally read racily and repaired by subsequent work. `b43_leds_exit()` turns off LEDs by index even if not registered, relying on indexes being initialized or harmless. Work must be stopped before unregistering LEDs to avoid use-after-free.

## Test Signals
Validation should check LED registration names/triggers, TX/RX/radio/assoc trigger behavior, active-low GPIO polarity, SPROM fallback paths, rfkill/radio-off forcing LEDs off, stop/unregister races, and no work execution after device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/leds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/leds.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/leds.h

## Purpose
This header declares b43 LED state structures, SPROM behavior constants, and LED lifecycle APIs, with no-op stubs when LED support is disabled.

## Important APIs, Types, And Functions
With `CONFIG_B43_LEDS`, it defines `struct b43_led`, `struct b43_leds`, `B43_MAX_NR_LEDS`, behavior masks, active-low mask, and `enum b43_led_behaviour`. It declares register/init/exit/stop/unregister functions. Without LED support, `struct b43_leds` is empty and lifecycle functions compile to no-ops.

## Control Flow
Driver code can always call LED lifecycle functions. Kconfig decides whether they manipulate LED class devices or disappear at compile time.

## State And Persistence
Enabled builds store four logical LEDs and one work item in `struct b43_wl`. Disabled builds store no LED state. There is no persistence outside hardware GPIO state and LED subsystem registration.

## Dependencies And Integration Points
The enabled path depends on Linux LED class and workqueue types. Behavior values are interpreted from SPROM GPIO configuration by `leds.c`.

## Risks
The enum includes a `B43_LED_WEIRD` FIXME behavior, reflecting incomplete semantic knowledge. Header stubs must stay compatible with call sites. LED name length is fixed at 31 characters plus terminator, so name generation must fit.

## Test Signals
Builds with and without `CONFIG_B43_LEDS` should compile and run. Enabled runtime tests should show registered LED class devices; disabled builds should have no LED class side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/leds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/lo.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/lo.c

## Purpose
This file implements G-PHY local oscillator calibration and adjustment for b43, including feedthrough measurement, TX bias/magnification measurement, per-attenuation calibration caching, hardware power-control DC lookup-table updates, periodic maintenance, and cleanup.

## Important APIs, Types, And Functions
Core helpers include `b43_find_lo_calib()`, `b43_lo_write()`, `lo_measure_feedthrough()`, `lo_txctl_register_table()`, `lo_measure_txctl_values()`, `lo_read_power_vector()`, `lo_measure_gain_values()`, `lo_measure_setup()`, `lo_measure_restore()`, `lo_probe_possible_loctls()`, `lo_probe_loctls_statemachine()`, `b43_calibrate_lo_setting()`, and `b43_get_calib_lo_settings()`.

Public functions are `b43_gphy_dc_lt_init()`, `b43_lo_g_adjust()`, `b43_lo_g_adjust_to()`, `b43_lo_g_maintenance_work()`, `b43_lo_g_cleanup()`, and `b43_lo_g_init()`.

## Control Flow
Calibration suspends the MAC, saves a large set of core/PHY/radio registers, sets up loopback/feedthrough measurement conditions, measures or refreshes TX control values when expired, computes gain settings from RF/baseband attenuation and loopback properties, probes I/Q LO control pairs with a small state machine looking for lower feedthrough, restores registers/channel, reenables the MAC, and returns a `b43_lo_calib` record. Adjustment looks up or creates a calibration for current or requested attenuation settings and writes the LO control pair to `B43_PHY_LO_CTL`.

Hardware power-control devices read a power vector from shared memory, clear it on-device, calibrate affected RF/BB table entries, update the cached DC lookup table, and write it back to PHY table registers. Periodic maintenance refreshes power-vector/DC table state for hardware power control, or expires and recalibrates cached list entries for software power control.

## State And Persistence
LO state is stored in `struct b43_txpower_lo_control`: RF/BB attenuation lists, cached DC lookup table, calibration list, timestamps for power-vector and TX-control measurements, current TX bias/magnification, and saved power vector. Calibration entries store attenuation keys, I/Q control values, timestamp, and list node. State is runtime-only; hardware receives current LO control and DC table values.

## Dependencies And Integration Points
This file depends on G-PHY structures and helpers from `phy_g.h`, common b43 MAC suspend/enable and dummy-transmission helpers, radio/PHY read/write/mask helpers, SPROM board flags, shared memory access, and debugfs dynamic LO logging. It is built only with `CONFIG_B43_PHY_G`.

## Risks
The calibration sequence is register-heavy and hardware-specific; missing a restore can leave radio/PHY state corrupted. It intentionally switches to channel 6 during measurement and must restore the old channel. The probing loops use feedthrough thresholds and magic values derived from hardware behavior. Memory allocation failure during calibration prevents adjustment. `b43_gphy_dc_lt_init()` assumes RF/BB list product fits the power-vector/table layout and warns if it exceeds 64. Because calibration can sleep/reschedule, callers must use suitable contexts.

## Test Signals
Useful signals include stable association and TX power on G-PHY devices, successful LO debugfs output, no stuck MAC after calibration, correct channel restoration, bounded calibration list growth/expiry, hardware power-control DC table updates after power vector changes, and no warnings from invalid I/Q ranges or table-size assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/lo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/lo.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/lo.h

## Purpose
This header declares G-PHY local oscillator control types, calibration-cache state, expiration constants, and public LO calibration APIs.

## Important APIs, Types, And Functions
`struct b43_loctl` stores signed I/Q control values. `struct b43_lo_calib` keys a calibrated LO control pair by baseband and RF attenuation values and includes a jiffies timestamp. `struct b43_txpower_lo_control` stores attenuation lists, 32-word DC lookup table cache, calibration list, measurement timestamps, TX bias/magnification, and power vector. Public functions adjust LO, adjust to explicit attenuation values, initialize/update DC lookup tables, run maintenance, clean up, and initialize LO state.

## Control Flow
G-PHY code allocates/fills `b43_txpower_lo_control`, calls init for hardware power-control setup, calls adjust during attenuation/power changes, calls maintenance periodically, and calls cleanup on teardown.

## State And Persistence
All state is runtime-only and attached to the G-PHY object. Expiration constants define when calibration entries, power vectors, and TX-control measurements are stale.

## Dependencies And Integration Points
The header includes `phy_g.h` for RF/baseband attenuation structures. It is used by `b43.h`, `lo.c`, PHY code, and debugfs LO inspection.

## Risks
I/Q values outside expected range are caught in debug writes but still depend on correct calibration. Expiration constants are tied to a 15-second maintenance cadence and subtract slack; changing periodic scheduling requires revisiting them. `B43_DC_LT_SIZE` must match hardware table assumptions.

## Test Signals
Builds with `CONFIG_B43_PHY_G` should compile all LO callers. Runtime test signals include LO adjustment on channel/power changes, periodic maintenance refreshing stale calibrations, and cleanup freeing all calibration list entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/lo.h -->
