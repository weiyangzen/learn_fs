# subset-b-005394 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/pcihost_wrapper.c -->
# sources/distributed-fs/ceph-client/drivers/ssb/pcihost_wrapper.c

Purpose: wraps a PCI device that exposes a Sonics Silicon Backplane into an `ssb_bus`, so SSB core drivers can bind below an ordinary `pci_driver`.

Important APIs/types/functions: `ssb_pcihost_register()` is the exported entry point. It installs `ssb_pcihost_probe()` and `ssb_pcihost_remove()` into the caller's `struct pci_driver`, optionally attaches `ssb_pcihost_pm_ops`, then calls `pci_register_driver()`. Probe allocates `struct ssb_bus`, enables the PCI function, requests BAR regions, sets bus mastering, disables the Broadcom retry timeout register field, and calls `ssb_bus_pcibus_register()`. Suspend/resume call `ssb_bus_suspend()`/`ssb_bus_resume()` around PCI save/disable/sleep and restore/enable sequencing.

Control flow: PCI matching enters probe, SSB enumeration and child-device registration happen in the SSB core, and remove unwinds in reverse order through `ssb_bus_unregister()`, region release, device disable, and `kfree()`.

State and persistence: state is runtime only: the allocated `ssb_bus` is stored as PCI driver data and freed on removal. PCI config state is saved across sleep but no durable data is written.

Dependencies and integration: depends on PCI core, PM sleep, and the SSB PCI bus registration path. The caller supplies IDs/name while this wrapper supplies common host behavior.

Risks: failure unwinds must stay paired with each probe step. PM resume re-enables PCI before SSB resume; failures can leave children unavailable. The retry-timeout config write is device-specific and should be limited to hardware where it is valid.

Test signals: bind/unbind a Broadcom SSB PCI device, confirm child cores enumerate, suspend/resume with wake-capable child devices, and inject failures for enable, region request, and SSB registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/pcihost_wrapper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/pcmcia.c -->
# sources/distributed-fs/ceph-client/drivers/ssb/pcmcia.c

Purpose: implements PCMCIA host-bus access for SSB devices, including core/segment window switching, byte/word/dword and optional block I/O operations, CIS-based invariant extraction, SPROM sysfs access, and PCMCIA hardware setup.

Important APIs/types/functions: `ssb_pcmcia_ops` provides `struct ssb_bus_ops`; `ssb_pcmcia_switch_coreidx()` programs address-window config registers; `ssb_pcmcia_switch_segment()` selects the 0/1 memory segment; `ssb_pcmcia_get_invariants()` parses CISTPL tuples into `ssb_init_invariants`; `ssb_pcmcia_init()`, `ssb_pcmcia_exit()`, and `ssb_pcmcia_hardware_setup()` handle setup and teardown. SPROM support is built from `ssb_pcmcia_sprom_read_all()`, `ssb_pcmcia_sprom_write_all()`, and sysfs `ssb_sprom` show/store callbacks.

Control flow: every MMIO access takes `bus->bar_lock`, selects the requested core and segment, then reads or writes `bus->mmio`. SPROM sysfs calls the common SSB SPROM attribute helpers, which lock `sprom_mutex`, optionally freeze devices, and call the PCMCIA read/write callbacks. Invariant collection first reads the LAN MAC tuple, then vendor-specific tuples for board, PA, country, antenna, flags, and LEDs.

State and persistence: `bus->mapped_device`, `mapped_pcmcia_seg`, `sprom_size`, and `sprom_mutex` are runtime state. SPROM writes persist on card EEPROM and are explicitly user-visible/high-risk.

Dependencies and integration: uses Linux PCMCIA config/CIS APIs, GPIO-free raw MMIO, SSB core freeze/thaw, and common SPROM helpers in `sprom.c`.

Risks: core switching is retry-based and returns all-ones on failed reads, which can mask hardware faults. `ssb_pcmcia_sprom_check_crc()` is a TODO returning success, so sysfs writes rely on upper-layer formatting but not CRC validation here. SPROM writes are slow and destructive if interrupted. Tuple size checks protect parsing but unknown card tuple variants can fail discovery.

Test signals: exercise 8/16/32-bit reads and writes across both segments, scan multiple cores, read the sysfs SPROM hex dump, attempt invalid SPROM stores, parse cards with missing/short tuples, and resume after PCMCIA COR reinitialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/pcmcia.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/scan.c -->
# sources/distributed-fs/ceph-client/drivers/ssb/scan.c

Purpose: discovers SSB cores on native, PCI, PCMCIA, and SDIO host buses and initializes the bus chip identity and per-core `struct ssb_device` table.

Important APIs/types/functions: `ssb_core_name()` maps core IDs to readable names. `ssb_bus_scan()` is the main scanner. `scan_read32()` and `scan_switchcore()` abstract host-bus-specific reads and core switching. `ssb_ioremap()` and `ssb_iounmap()` map/unmap host address space. Fallback helpers `pcidev_to_chipid()` and `chipid_to_nrcores()` handle older chips without usable ChipCommon core count.

Control flow: scan maps host I/O, switches to core 0, reads `SSB_IDHIGH`, detects ChipCommon when present, populates chip ID/revision/package/capabilities, computes core count, remaps full native SSB space when needed, then iterates every core. It fills each `struct ssb_device`, records special core pointers for ChipCommon, EXTIF, MIPS, and PCI/PCIe, filters unsupported duplicate 802.11 cores, ignores dangling Ethernet cores on wireless PCI devices, and adjusts `bus->nr_devices`.

State and persistence: runtime bus state includes `mmio`, chip metadata, `nr_devices`, `devices[]`, and subsystem core pointers. No durable state is written.

Dependencies and integration: calls PCI, PCMCIA, and SDIO switching helpers and uses SSB register definitions. Later SSB driver registration and core initialization consume the populated device table.

Risks: fallback chip/core tables must cover legacy IDs or scanning degrades to one core. Duplicate-core filtering is policy-sensitive and can hide functional cores. Host-specific reads use different address math, so segment/window bugs can corrupt enumeration.

Test signals: scan PCI, PCMCIA, SDIO, and native SSB hosts; verify chip metadata, core count, duplicate 802.11 handling, PCI-vs-PCIe core filtering, and clean unmap on mid-scan errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/scan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/sdio.c -->
# sources/distributed-fs/ceph-client/drivers/ssb/sdio.c

Purpose: implements SDIO host-bus access for SSB devices, including SDIO backplane window programming, register/block I/O, CIS tuple invariant extraction, and SDIO bus initialization.

Important APIs/types/functions: `ssb_sdio_ops` supplies SSB bus operations. `ssb_sdio_set_sbaddr_window()` programs SBADDR low/mid/high registers. `ssb_sdio_scan_read32()` and `ssb_sdio_scan_switch_coreidx()` support enumeration. Runtime accessors `ssb_sdio_read8/16/32()`, `ssb_sdio_write8/16/32()`, and optional block read/write helpers claim the SDIO host, switch core, translate offsets, and use SDIO I/O APIs. `ssb_sdio_get_invariants()` parses SDIO tuples into board/SPROM data.

Control flow: enumeration sets the address window to each core base and reads ID registers. Runtime access claims the host, ensures `bus->sdio_sbaddr` matches the target core, combines the lower backplane address with the selected window, sets the 32-bit access flag when needed, performs SDIO I/O, logs errors, and releases the host. A read-after-write quirk can force a dummy read after 32-bit writes.

State and persistence: runtime state is `bus->sdio_sbaddr`, `mapped_device`, parsed SPROM fields, and optional quirk flags. No persistent storage is modified.

Dependencies and integration: depends on MMC/SDIO function APIs, SSB scan and main bus code, tuple data exposed by the SDIO core, and Broadcom SDIO address-window conventions.

Risks: all register access depends on correct host-claiming and address-window cache coherency. Bad tuple sizes fail invariant extraction. Block I/O must preserve alignment expectations for 16/32-bit widths. The 32-bit access flag and read-after-write quirk are hardware-sensitive.

Test signals: enumerate SDIO SSB devices, read/write 8/16/32-bit registers, exercise block transfers, trigger SDIO errors, verify tuple-derived MAC/board fields, and test hardware requiring the read-after-write quirk.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/sdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/sprom.c -->
# sources/distributed-fs/ceph-client/drivers/ssb/sprom.c

Purpose: provides common SSB SPROM helpers shared by host-specific SPROM sysfs implementations and architecture fallback providers.

Important APIs/types/functions: `ssb_attr_sprom_show()` reads a host SPROM image and formats it as a hex string. `ssb_attr_sprom_store()` parses a hex string, checks CRC through the host callback, freezes SSB devices, writes the image, thaws devices, and returns a sysfs byte count or error. `ssb_arch_register_fallback_sprom()` installs one fallback callback, `ssb_fill_sprom_with_fallback()` invokes it, and `ssb_is_sprom_available()` checks ChipCommon SPROM capability for newer PCI chips. Internal `sprom2hex()` and `hex2sprom()` do endian-aware conversion.

Control flow: show allocates a word buffer, locks `sprom_mutex` interruptibly, reads through the supplied callback, unlocks, formats, and frees. Store allocates, parses exact-length hex after stripping trailing whitespace, invokes the host CRC check, locks, freezes devices, writes through the supplied callback, thaws, unlocks, and frees.

State and persistence: local global state is only the fallback callback pointer. Store may persist data through the host-specific SPROM writer; this file coordinates locking and device freeze but does not access hardware directly.

Dependencies and integration: used by PCMCIA/PCI SPROM attributes and platform architecture code. Depends on SSB freeze/thaw and host callbacks for actual read/write/CRC behavior.

Risks: fallback registration is not locked and only prevents a second callback by plain pointer check. Store return precedence can expose write errors before thaw errors. Correctness relies on host callbacks validating CRC and write semantics; PCMCIA currently passes a stub CRC checker.

Test signals: sysfs SPROM read formatting, exact-length and malformed writes, interrupted mutex acquisition, freeze/write/thaw error paths, fallback duplicate registration, and ChipCommon rev >=31 SPROM capability detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/sprom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/ssb_private.h -->
# sources/distributed-fs/ceph-client/drivers/ssb/ssb_private.h

Purpose: is the private cross-file declaration hub for the SSB subsystem. It exposes host-bus operations, scan/SPROM helpers, core helpers, optional subsystem hooks, and configuration-dependent stubs to keep callers buildable when features are disabled.

Important APIs/types/functions: declarations cover PCI, PCMCIA, SDIO, SoC host, scan, SPROM, core bus lookup, freeze/thaw, B43 PCI bridge, PMU clocks, watchdog hooks, serial/parallel flash, EXTIF, embedded watchdog, and GPIO initialization. `struct ssb_freeze_context` tracks frozen devices for SPROM writes.

Control flow: there is no executable flow except inline stubs. Compile-time `CONFIG_*` gates decide whether a symbol is externally resolved or becomes a no-op/constant-return inline helper.

State and persistence: no state is owned here. It defines the shape of transient freeze context and references subsystem runtime state owned by other files.

Dependencies and integration: includes public `linux/ssb/ssb.h`, types, and BCM47xx watchdog definitions. It is included by SSB implementation files to avoid exposing internals through public headers.

Risks: stub behavior matters: disabled host helpers often return success or zero, so callers must be behind matching bustype/config checks. Prototype drift between this header and implementations is compile-time visible. Returning `-ENOTSUPP` for disabled GPIO differs from no-op success stubs.

Test signals: build SSB with PCI, PCMCIA, SDIO, GPIO, SFLASH, EXTIF, MIPS, and embedded options both enabled and disabled; verify no unresolved symbols and expected stub behavior in disabled configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ssb/ssb_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/staging/Kconfig

Purpose: defines the top-level `STAGING` Kconfig menu and sources all staging driver submenus in this kernel tree.

Important APIs/types/functions: `menuconfig STAGING` is a bool gate with a warning help text about driver quality, kernel taint, and unstable userspace interfaces. Inside `if STAGING`, it sources RTL8723BS, Octeon, IIO, SM750FB, NVEC, media, FBTFT, MOST, Greybus, VC04 services, axis-fifo, and vme_user Kconfig files.

Control flow: Kconfig visibility flows from `STAGING`; none of the sourced staging symbols are reachable unless `STAGING=y`.

State and persistence: configuration state is stored in kernel build `.config`, not runtime state.

Dependencies and integration: integrates staging subdirectories into the kernel configuration graph and pairs with `drivers/staging/Makefile` for build inclusion.

Risks: ordering can affect menu presentation and dependency diagnostics. Missing or renamed sourced files break configuration. Enabling staging intentionally exposes less mature drivers and can taint support status.

Test signals: run `make menuconfig`/`olddefconfig` with `STAGING=y` and `n`, verify all sourced paths exist, and check that disabling `STAGING` hides FBTFT and axis-fifo options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/Makefile -->
# sources/distributed-fs/ceph-client/drivers/staging/Makefile

Purpose: connects selected staging Kconfig symbols to subdirectory builds.

Important APIs/types/functions: `obj-y += media/` always descends into media staging, while other entries are conditional on symbols such as `CONFIG_FB_TFT`, `CONFIG_XIL_AXIS_FIFO`, `CONFIG_GREYBUS`, and `CONFIG_BCM2835_VCHIQ`.

Control flow: kbuild evaluates `obj-*` variables and descends into enabled subdirectories during kernel or module builds.

State and persistence: no runtime state; build outputs depend on `.config`.

Dependencies and integration: pairs with top-level staging Kconfig and each subdirectory Makefile. It integrates FBTFT and axis-fifo into the build when their symbols are selected.

Risks: symbol/path mismatch silently omits drivers or breaks builds. The unconditional `media/` descent relies on that subdirectory handling its own inner config filtering.

Test signals: compile with each staging symbol enabled as built-in and module, especially `CONFIG_FB_TFT=m` and `CONFIG_XIL_AXIS_FIFO=m`, and verify expected objects are produced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/axis-fifo/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/staging/axis-fifo/Kconfig

Purpose: declares the staging Kconfig option for the Xilinx AXI-Stream FIFO memory-mapped character driver.

Important APIs/types/functions: `config XIL_AXIS_FIFO` is a tristate option named `Xilinx AXI-Stream FIFO IP core driver`; it depends on `OF && HAS_IOMEM`.

Control flow: when selected, kbuild can compile `axis-fifo.o` from the matching Makefile.

State and persistence: stores only build configuration.

Dependencies and integration: depends on Device Tree probing and MMIO support because the driver is a platform driver using OF properties and mapped registers.

Risks: no explicit dependency on `MISC_DEVICES`, `DEBUG_FS`, or `POLL`-related facilities is needed because those are core APIs, but the driver's runtime ABI is a staging misc device and may change.

Test signals: Kconfig visibility on OF and non-OF builds, module/built-in builds, and compile with `COMPILE_TEST` style architectures that satisfy `HAS_IOMEM`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/axis-fifo/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/axis-fifo/Makefile -->
# sources/distributed-fs/ceph-client/drivers/staging/axis-fifo/Makefile

Purpose: builds the Xilinx AXI-Stream FIFO staging driver object when enabled.

Important APIs/types/functions: `obj-$(CONFIG_XIL_AXIS_FIFO) += axis-fifo.o`.

Control flow: kbuild includes the object for built-in or module output based on the tristate symbol.

State and persistence: no runtime state.

Dependencies and integration: tied directly to `axis-fifo/Kconfig` and the top-level staging Makefile.

Risks: any source rename or Kconfig symbol rename must be reflected here or the driver will not build.

Test signals: build with `CONFIG_XIL_AXIS_FIFO=y` and `m` and verify `axis-fifo.o`/module output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/axis-fifo/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/axis-fifo/axis-fifo.c -->
# sources/distributed-fs/ceph-client/drivers/staging/axis-fifo/axis-fifo.c

Purpose: implements a platform/misc character driver for Xilinx AXI-Stream FIFO IP. It exposes packet-oriented FIFO reads and writes to userspace, interrupt-driven blocking semantics, polling, and a small debugfs register view.

Important APIs/types/functions: `struct axis_fifo` stores MMIO base, FIFO depths/capability flags, wait queues, locks, misc device, and debugfs dentry. File operations are `axis_fifo_open()`, `axis_fifo_read()`, `axis_fifo_write()`, and `axis_fifo_poll()`. Probe/remove are `axis_fifo_probe()` and `axis_fifo_remove()`. `axis_fifo_irq()` handles receive/transmit/error interrupts. `axis_fifo_parse_dt()` requires 32-bit RX/TX data widths and reads FIFO depth and use flags.

Control flow: probe allocates state, maps MMIO, parses OF properties, resets/enables interrupts, requests IRQ, allocates an ID, registers `/dev/axis_fifoN`, and creates debugfs. Reads lock the RX path, wait for receive occupancy unless nonblocking, read packet length, validate user buffer and word alignment, drain data words through a small stack buffer, and flush on errors. Writes validate word-aligned packet length and FIFO depth, wait for vacancy, copy userspace data with `vmemdup_user()`, write data words, then write transmit length. IRQ wakes read/write wait queues and logs FIFO protocol errors.

State and persistence: all state is volatile hardware/device state. FIFO contents are consumed by reads/writes. No persistent storage exists.

Dependencies and integration: depends on platform/OF, MMIO, IRQ, miscdevice, debugfs, poll, wait queues, mutexes, and Xilinx register semantics.

Risks: userspace ABI is packet-oriented and rejects partial buffers. `axis_fifo_read()` flushes unread packet data on several errors, causing data loss by design. Debugfs exposes live registers without locking. Removal does not explicitly reset hardware after deregistration. Correctness depends on Device Tree properties matching generated IP.

Test signals: blocking and nonblocking read/write, poll readiness, packet sizes at zero, unaligned, exact FIFO limit and over-limit, RX packet larger than user buffer, IRQ wakeups, error interrupts, debugfs `regs`, and OF probe failures for non-32-bit widths or missing properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/axis-fifo/axis-fifo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/Kconfig

Purpose: declares the FBTFT staging subsystem and all small SPI TFT/OLED/LCD controller driver options.

Important APIs/types/functions: `menuconfig FB_TFT` is a tristate requiring `FB`, `SPI`, `BACKLIGHT_CLASS_DEVICE`, and `GPIOLIB || COMPILE_TEST`; it selects `FB_BACKLIGHT` and `FB_SYSMEM_HELPERS_DEFERRED`. Child tristates enable individual panel/controller drivers such as AGM1264K-FL, HX/ILI/SSD/ST/UC controllers, RA8875, and tinylcd.

Control flow: when `FB_TFT` is enabled, its child symbols become visible and the matching Makefile entries compile core and panel modules.

State and persistence: configuration only; runtime state belongs to the selected driver modules.

Dependencies and integration: connects staging FBTFT to framebuffer, SPI, GPIO, and backlight kernel subsystems.

Risks: child options generally do not repeat dependencies, so the top-level gate must remain accurate. Help text is terse and does not encode panel bus-width constraints.

Test signals: Kconfig with missing SPI/FB/backlight/GPIO dependencies, all drivers as modules, and `COMPILE_TEST` coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/Makefile -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/Makefile

Purpose: builds the FBTFT core library and selected panel/controller modules.

Important APIs/types/functions: `obj-$(CONFIG_FB_TFT) += fbtft.o` combines `fbtft-core.o`, `fbtft-sysfs.o`, `fbtft-bus.o`, and `fbtft-io.o`; subsequent `obj-$(CONFIG_FB_TFT_*)` entries build individual `fb_*.o` drivers.

Control flow: kbuild produces the shared core when the top-level symbol is enabled and adds per-panel objects according to child symbols.

State and persistence: build-only state.

Dependencies and integration: tied to `fbtft/Kconfig` and the source files in this directory.

Risks: `fb_ssd1325.o` is keyed by `CONFIG_FB_TFT_SSD1305` rather than a visible `CONFIG_FB_TFT_SSD1325` symbol in this snapshot, so SSD1325 build selection appears coupled to SSD1305. Any symbol/file mismatch breaks module availability.

Test signals: build each FBTFT option individually, verify module names, and specifically check whether `fb_ssd1325.o` is built when expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_agm1264k-fl.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_agm1264k-fl.c

Purpose: drives an AGM1264K-FL 128x64 monochrome module made from two KS0108-compatible halves over GPIO parallel lines.

Important APIs/types/functions: `init_display()`, `verify_gpios()`, `request_gpios_match()`, custom `write_reg8_bus8()`, `set_addr_win()`, `write_vmem()`, and GPIO bit-banged `write()` override standard FBTFT paths. It defines gamma and Floyd-Steinberg style diffusion tables for RGB565-to-1bpp conversion.

Control flow: init resets both controller halves and enables display/page/start-line registers. GPIO matching maps `wr`, `cs0`, `cs1`, and `rw`; `write_vmem()` converts framebuffer RGB565 to grayscale, applies gamma and dithering, splits updates across left/right chips, selects command/data mode with RS, and bit-bangs bytes over db0-db7.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: requires many GPIOs and has no hardware read/status wait. A file-static `addr_win` is shared across instances. Per-update allocation and full conversion are costly; dithering/window calculations must avoid crossing the two chip halves incorrectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_agm1264k-fl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_bd663474.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_bd663474.c

Purpose: initializes and drives a 240x320 BD663474/uPD-style 16-bit register LCD controller.

Important APIs/types/functions: `init_display()` programs oscillator, power, display, GRAM, grayscale, and RAM-access registers. `set_addr_win()` writes GRAM cursor registers for four rotations. `set_var()` updates entry mode `0x003`.

Control flow: probe registration supplies a 16-bit register-width FBTFT display. Runtime updates set the GRAM start address according to rotation, issue register `0x202`, and the FBTFT core streams pixel data.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: controller naming/description says uPD161704 despite BD663474 driver name. Rotation code sets only cursor, not full GRAM window bounds. No gamma sysfs hook despite grayscale register initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_bd663474.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_hx8340bn.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_hx8340bn.c

Purpose: supports HX8340BN 176x220 16-bit color LCDs, including 9-bit SPI or emulated 9-bit transfer via FBTFT.

Important APIs/types/functions: `init_display()` sends extended-command, sleep-out, oscillator, power, drive, pixel-format, and display-on commands. `set_var()` writes MIPI MADCTL rotation/BGR. `set_gamma()` masks and writes GC0 gamma tables. Module parameter `emulate` exists to force emulation.

Control flow: after reset, initialization enables the extended command set, wakes the panel, configures power/drive/pixel format, then turns display on. FBTFT handles address windows while this driver handles rotation and gamma.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: the `emulate` parameter is declared here but actual 9-bit emulation depends on FBTFT core behavior. Gamma curve selection only customizes GC0; nonzero GC selection exits early.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_hx8340bn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_hx8347d.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_hx8347d.c

Purpose: supports HX8347D 320x240 LCD controllers with custom power, address-window, rotation, and gamma programming.

Important APIs/types/functions: `init_display()`, `set_addr_win()`, `set_var()`, and `set_gamma()` are the key hooks. Gamma uses two 14-value curves and masks per register width.

Control flow: reset is followed by drive-strength, power, oscillator, pixel-format, and display-on commands. Address windows program x/y start/end registers then issue GRAM write register `0x22`; rotation uses register `0x16`.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: gamma all-zero input is treated as skip, so a user cannot intentionally write all-zero gamma. Window setup assumes controller coordinates match the configured 320x240 geometry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_hx8347d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_hx8353d.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_hx8353d.c

Purpose: supports 128x160 HX8353D LCD controllers using MIPI-style command registers and a single custom gamma curve.

Important APIs/types/functions: `init_display()` enables extended commands, power/VCOM/pixel format, sleep-out/display-on, and LUT programming. `set_var()` writes MADCTL rotation/BGR. `set_gamma()` writes register `0xE0` with 19 values.

Control flow: initialization resets, waits, configures panel power and RGB LUT, then enables normal display. Rotation updates only MADCTL; FBTFT core performs memory writes.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: gamma values are not masked before register writes, unlike many sibling drivers. Fixed 128x160 geometry may not cover panel variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_hx8353d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_hx8357d.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_hx8357d.c

Purpose: supports HX8357D 320x480 LCDs with an Adafruit-derived initialization sequence.

Important APIs/types/functions: `init_display()` uses command constants from `fb_hx8357d.h`; `set_var()` computes HX8357D MADCTL bits. Display metadata exposes two 14-value gamma curves but this file has no runtime `set_gamma()` hook.

Control flow: reset and soft reset are followed by extended command unlock, RGB/COM/oscillator/panel/power/timing/gamma constants, pixel format, TE configuration, sleep-out, and display-on. Rotation writes MIPI address mode.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: BGR logic is inverted-looking: `par->bgr ? RGB : BGR`, so panel color validation is important. Static gamma in init cannot be changed through FBTFT gamma hook.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_hx8357d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_hx8357d.h -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_hx8357d.h

Purpose: contains HX8357B/HX8357D command constants, geometry constants, and RGB565 color definitions used by the HX8357D FBTFT driver.

Important APIs/types/functions: defines command IDs such as `HX8357D_SETC`, `HX8357_SETRGB`, `HX8357D_SETCOM`, `HX8357_SETPWR1`, `HX8357D_SETSTBA`, `HX8357D_SETCYC`, and `HX8357D_SETGAMMA`.

Control flow: no executable code; inclusion lets `fb_hx8357d.c` use named constants instead of literal command bytes.

State and persistence: no state.

Dependencies and integration: private to the HX8357D driver but based on an Adafruit header with MIT license text.

Risks: contains constants for both B and D variants; using the wrong variant command in driver code can silently misconfigure hardware. Color constants are unused by the driver.

Test signals: compile the HX8357D driver and compare command values with the target controller datasheet.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_hx8357d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ili9163.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ili9163.c

Purpose: supports 128x128 ILI9163 LCD modules, including offsets for panel variants whose controller memory is 128x160.

Important APIs/types/functions: `init_display()`, `set_addr_win()`, `set_var()`, and optional `gamma_adj()` under `GAMMA_ADJ` configure the panel. Constants describe ILI9163C power/frame/gamma commands.

Control flow: initialization resets, exits sleep, sets RGB565, gamma curve, normal mode, power/VCOM/frame controls, column/page ranges, display on, and memory-write mode. Address windows add `__OFFSET` for selected rotations and issue memory-write start.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: compile-time `RED`/`GAMMA_ADJ` switches mean behavior changes at build time rather than runtime. Default branch mutates `var.rotate` if unsupported. The color-space comment and BGR bit use must be validated on real red/black modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ili9163.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ili9320.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ili9320.c

Purpose: supports ILI9320 240x320 16-bit-register LCDs and warns if the read device code is unexpected.

Important APIs/types/functions: `read_devicecode()` uses the FBTFT read op. `init_display()` programs the application-note power/display/GRAM sequence. `set_addr_win()`, `set_var()`, and `set_gamma()` handle cursor, rotation, BGR, and two 10-value gamma curves.

Control flow: after reset it reads register 0, initializes power and GRAM bounds, turns the display on, then later FBTFT updates set GRAM address and stream pixels through register `0x22`.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: requires a working read operation for meaningful ID warning; write-only configurations will likely read zero. Gamma masking protects bit width, but coordinate code assumes 240x320 geometry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ili9320.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ili9325.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ili9325.c

Purpose: supports ILI9325 240x320 LCDs with module parameters for power/voltage tuning.

Important APIs/types/functions: `bt`, `vc`, `vrh`, `vdv`, and `vcm` module parameters are masked in `init_display()`. `set_addr_win()`, `set_var()`, and `set_gamma()` mirror the ILI9320-style GRAM path.

Control flow: initialization writes internal timing, power sequencing with delays, GRAM area, gate scan, panel controls, and display-on. Runtime rotation changes entry mode and cursor addressing.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: power parameters can produce unsupported panel voltages if changed poorly; the source documents one safe 3.3V configuration but does not validate electrical limits. Gamma register mappings are manual and error-prone.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ili9325.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ili9340.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ili9340.c

Purpose: supports ILI9340 240x320 LCDs with an Adafruit 2.2-inch style initialization sequence.

Important APIs/types/functions: `init_display()` writes power, VCOM, pixel format, frame-rate, display function, gamma, sleep-out, and display-on commands. `set_var()` writes MADCTL rotation/BGR.

Control flow: reset is followed by vendor command unlock/configuration and MIPI DCS commands. Address-window and memory writes are left to FBTFT core defaults.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: no runtime gamma hook despite fixed gamma writes in init. Rotation mapping differs from ILI9341 and must be validated with panel orientation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ili9340.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ili9341.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ili9341.c

Purpose: supports ILI9341 LCD panels over SPI, using FBTFT's SPI-specific registration macro and gamma sysfs support.

Important APIs/types/functions: `init_display()` sends MI0283QT-9A startup commands. `set_var()` writes MADCTL bits. `set_gamma()` writes positive/negative 15-value gamma tables. Display metadata sets `txbuflen` to 4 pages.

Control flow: probe registers an SPI/platform-compatible driver. Initialization soft-resets, powers/configures display, exits sleep, then display-on. Rotation and gamma are applied through FBTFT operations.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: the header comments mention 9-bit SPI emulation, but the file does not expose a local emulate parameter. Gamma values are not masked here, so invalid sysfs gamma may reach hardware registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ili9341.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ili9481.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ili9481.c

Purpose: supports ILI9481 320x480 LCDs using an FBTFT `init_sequence` array instead of a custom init function.

Important APIs/types/functions: `default_init_sequence` encodes sleep-out, power, VCOM, panel, frame/inversion, pixel format, gamma, and display-on commands. `set_var()` writes MIPI address mode with H/V flip and row/column exchange bits.

Control flow: the FBTFT core interprets the init sequence markers, delays, and commands. Runtime rotation only updates MADCTL.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: init sequence is fixed for one panel family. The HFLIP/VFLIP constants are low-bit values that differ from many MADCTL definitions, so orientation must be verified.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ili9481.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ili9486.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ili9486.c

Purpose: supports ILI9486 320x480 LCDs with a PiScreen-matching init sequence.

Important APIs/types/functions: `default_init_sequence` configures interface mode, sleep, RGB565 pixel format, power/VCOM, positive/negative/digital gamma, and display-on. `set_var()` writes rotation-specific address mode values.

Control flow: FBTFT core runs the sequence; this driver then handles rotation updates and relies on common memory-window writes.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: the sequence contains two sleep-out commands and fixed gamma values. No gamma hook exists for calibration. Unsupported rotation default silently does nothing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ili9486.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_pcd8544.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_pcd8544.c

Purpose: drives PCD8544/Nokia 5110-style 84x48 monochrome LCDs from an RGB565 framebuffer.

Important APIs/types/functions: `init_display()` configures extended/basic instruction modes, temperature coefficient `tc`, bias `bs`, and display mode. `set_addr_win()`, `write_vmem()`, and `set_gamma()` implement addressing, RGB565-to-1bpp packing, and contrast.

Control flow: full updates reset X/Y RAM address, pack each vertical 8-pixel bank from framebuffer into bytes, set DC high, and write 504 bytes. Gamma writes Vop contrast in extended mode.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: any nonzero RGB565 pixel becomes on, so grayscale/color information is discarded. `set_addr_win()` ignores requested region and full-frame write_vmem is expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_pcd8544.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ra8875.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ra8875.c

Purpose: supports RA8875 medium-size LCD controllers with custom SPI command framing and multiple panel timing presets.

Important APIs/types/functions: `write_spi()` forces register writes at 1 MHz. `init_display()` selects timing for 320x240, 480x272, 640x480, or 800x480. `set_addr_win()`, custom `write_reg8_bus8()`, and `write_vmem16_bus8()` implement RA8875 framing and pixel streaming.

Control flow: init checks framebuffer resolution, writes PLL, interface, pixel clock, horizontal/vertical timing, PWM, and display-on registers. Register writes send command prefix `0x80` then data prefix `0x00`; pixel writes prepend data prefix and stream big-endian RGB565.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: unsupported resolutions fail initialization. `set_addr_win()` writes end coordinates as `xs + xe`/`ys + ye`, which deserves hardware validation because many APIs pass absolute `xe/ye`. Register write temporarily rewrites `par->fbtftops.write`, which is fragile if reentered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ra8875.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_s6d02a1.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_s6d02a1.c

Purpose: supports S6D02A1 128x160 LCDs through a long fixed vendor initialization sequence.

Important APIs/types/functions: `default_init_sequence` contains unlock, gamma/power, staged sleep-out power-up, address mode, tear, pixel format, gamma curve, display-on, and memory-write commands. `set_var()` writes MIPI address mode.

Control flow: FBTFT core executes the sequence with embedded delays; runtime rotation writes MADCTL bits and common FBTFT paths handle pixel transfer.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: large magic init table is hard to audit and panel-specific. No gamma hook exists despite gamma-like table values in the sequence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_s6d02a1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_s6d1121.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_s6d1121.c

Purpose: supports Samsung S6D1121 240x320 16-bit-register LCD controllers.

Important APIs/types/functions: `init_display()` writes a Lib_UTFT-derived sequence. `set_addr_win()`, `set_var()`, and `set_gamma()` manage GRAM cursor, rotation, BGR, and two 14-value gamma curves.

Control flow: after reset, init configures power, panel, display, and GRAM-write mode. Runtime updates choose GRAM address based on rotation and issue register `0x22` before pixel streaming.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: one gamma assignment appears to use `CURVE(0, 3)` in both registers `0x0031` and `0x0032`, which may be intentional or a copy error. Register sequences are panel-specific and lack ID checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_s6d1121.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_seps525.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_seps525.c

Purpose: drives a 160x128 SEPS525 OLED controller such as Newhaven NHD-1.69 modules.

Important APIs/types/functions: `init_display()` programs oscillator, current/precharge, display mode, RGB interface, memory write mode, duty, display-on, and soft reset. `set_addr_win()` sets pointer/window registers. `set_var()` supports only 0 and 180 degree rotation and BGR swap.

Control flow: init resets and configures OLED current and memory mode, then enters data-access port. Address updates set optional window bounds and current X/Y pointer. Unsupported 90/270 rotation returns `-EINVAL`.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: `seps525_use_window` is compile-time zero, so window bounds are not currently used. Only two rotations work. OLED current constants are fixed and may not suit all panels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_seps525.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_sh1106.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_sh1106.c

Purpose: supports SH1106 128x64 OLEDs with monochrome framebuffer packing and contrast control.

Important APIs/types/functions: `init_display()` validates x/y size and forbids rotation, then writes SSD1306-like display configuration. `write_vmem()` packs RGB565 pixels into page bytes with a column offset of 2. `write_register()` keeps DC low for all command bytes. `blank()` and `set_gamma()` control display on/off and contrast.

Control flow: initialization rejects invalid geometry, resets, configures multiplex/COM/segment/precharge/VCOM, and turns display on. Updates compute affected pages from offset/len, set page/column, pack bits, and write data with DC high.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: rotation is unsupported. SH1106 RAM is wider than visible columns, hence fixed offset 2; wrong modules may need a different offset. Any nonzero pixel becomes lit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_sh1106.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ssd1289.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ssd1289.c

Purpose: supports SSD1289 240x320 16-bit-register LCD controllers.

Important APIs/types/functions: `reg11` module parameter seeds display-control register `0x11`. `init_display()`, `set_addr_win()`, `set_var()`, and `set_gamma()` configure controller registers, cursor, rotation, and two 10-value gamma curves.

Control flow: init writes the ITDB02-derived register sequence and enters RAM data write. `set_var()` avoids touching register `0x11` if the init hook has been replaced by platform data, preventing override of custom init.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: module parameter `reg11` can alter scan/color behavior. No device ID read. Rotation depends on register `0x11` bits matching the panel wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ssd1289.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ssd1305.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ssd1305.c

Purpose: supports SSD1305 OLED controllers with monochrome packing and contrast-as-gamma.

Important APIs/types/functions: `init_display()` configures display clock, multiplex, charge pump, addressing, COM pins, precharge, normal display, and display on. `set_addr_win()`, `write_vmem()`, `blank()`, and `set_gamma()` implement page addressing, RGB565-to-1bpp conversion, display on/off, and contrast.

Control flow: init sets a default contrast in `par->gamma.curves[0]` under lock when unset. Updates pack the whole framebuffer in vertical byte order and write it with DC high.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: write_reg caveat requires command/value pairs as separate calls because DC must stay low. Rotation only affects segment/COM choices in init/addressing. Any nonzero pixel is on.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ssd1305.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ssd1306.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ssd1306.c

Purpose: supports SSD1306 OLED controllers, including 128x64/128x48/other-height variants and a special 64x48 address window.

Important APIs/types/functions: `init_display()`, `set_addr_win_64x48()`, `set_addr_win()`, `write_vmem()`, `blank()`, and `set_gamma()` configure OLED mode and pack framebuffer data.

Control flow: init sets contrast default, clock, multiplex based on yres, charge pump, vertical addressing, remap/COM, precharge/VCOM, normal mode, and display-on. Updates pack RGB565 nonzero pixels into page bytes and write xres*yres/8 bytes.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: does not reject unsupported rotations; remap is fixed. 64x48 panels need special column/page commands. Contrast values are accepted after masking only.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ssd1306.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ssd1325.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ssd1325.c

Purpose: supports SSD1325 128x64 4-bit grayscale OLEDs by converting RGB565 framebuffer data into packed grayscale nibbles.

Important APIs/types/functions: `rgb565_to_g16()`, `init_display()`, `set_addr_win()`, `write_vmem()`, `blank()`, and `set_gamma()` are key. Gamma represents a 15-entry grayscale lookup table.

Control flow: init writes clock/display/addressing/window commands and display-on. Updates iterate columns in pairs, convert two RGB565 pixels to 4-bit grayscale, pack them into one byte, set DC high, and write the whole buffer.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: Kconfig/Makefile selection appears tied to SSD1305 in this snapshot. `set_gamma()` validates all 15 entries but writes only the first 8 values to register `0xB8`, which may be incomplete or controller-specific.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ssd1325.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ssd1331.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ssd1331.c

Purpose: supports SSD1331 96x64 color OLEDs with a custom command/data register writer and 63-entry grayscale gamma table.

Important APIs/types/functions: `init_display()` configures remap/color depth, address offsets, precharge, contrast, and display-on. `write_reg8_bus8()` sends the first byte as command then remaining bytes as data. `set_gamma()` accumulates 63 relative gamma entries into SSD1331 lookup values. `blank()` toggles display.

Control flow: initialization sets orientation partly from `rotate == 180`, then FBTFT updates use column/row address commands. Gamma validation enforces monotonically increasing accumulated values <=180.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: rotation handling in init only distinguishes 180 from others; no `set_var()` hook for runtime rotation. Gamma write is very long and easy to break if `gamma_len` changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ssd1331.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ssd1351.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ssd1351.c

Purpose: supports SSD1351 128x128 color OLEDs with optional onboard backlight controlled through controller GPIO.

Important APIs/types/functions: `init_display()` conditionally installs `register_onboard_backlight()`, unlocks commands, initializes OLED power/timing/contrast, and displays on. `set_addr_win()`, `set_var()`, `set_gamma()`, `blank()`, and backlight ops handle runtime behavior.

Control flow: if platform data requests `FBTFT_ONBOARD_BACKLIGHT`, the driver registers a raw backlight whose update writes SSD1351 GPIO register `0xB5`. Rotation writes remap register `0xA0`; gamma accumulates 63 values and writes lookup table `0xB8`.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: backlight registration uses the framebuffer device string and must unregister through FBTFT. Gamma validation rejects small increments and accumulated >180. `set_var()` skips when custom init replaces this file's init hook.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ssd1351.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_st7735r.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_st7735r.c

Purpose: supports ST7735R 128x160 LCDs with an FBTFT init sequence and gamma sysfs hook.

Important APIs/types/functions: `default_init_sequence` covers reset, sleep-out, frame-rate, inversion, power, pixel format, display-on, and normal mode. `set_var()` writes MADCTL rotation/BGR. `set_gamma()` writes positive/negative 16-value gamma curves masked to 6 bits.

Control flow: FBTFT executes the sequence and delays. Runtime rotation/gamma are applied by hooks; memory writes use common MIPI/FBD address paths.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: default init sequence is for one ST7735R panel class; offsets for common tab-color modules are not represented here. Gamma values are masked rather than rejected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_st7735r.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_st7789v.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_st7789v.c

Purpose: supports ST7789V LCD controllers and optionally synchronizes framebuffer writes to a panel tearing-effect GPIO interrupt.

Important APIs/types/functions: `init_tearing_effect_line()` requests optional `te` GPIO and IRQ, `panel_te_handler()` completes a global completion, `init_display()` programs ST7789V power/porch/gamma-related defaults, `write_vmem()` waits for TE before dispatching to buswidth-specific FBTFT writers, `set_var()`, `set_gamma()`, and `blank()` handle runtime settings.

Control flow: init resets, sets up TE IRQ if present, exits sleep, sets RGB565, writes porch/gate/VRH/VCOM/power, enables TE output if IRQ exists, turns display on, and optionally enters invert mode. Every update enables the TE IRQ, waits up to 33 ms, disables it, then writes through the selected bus helper.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: static global `panel_te` and `irq_te` are not per-device, limiting multi-panel safety. Timeout logs but still writes. Optional TE GPIO lifetime is devm IRQ-managed after dropping the descriptor. Unsupported buswidth logs and returns success-like zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_st7789v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_tinylcd.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_tinylcd.c

Purpose: implements a custom 320x480 tinylcd.com panel initialization and rotation mapping.

Important APIs/types/functions: `init_display()` writes a vendor command sequence including power, frame, display function, gamma-like commands, RGB565 pixel format, sleep-out, and display-on. `set_var()` writes rotation-specific display function and address mode values.

Control flow: after reset the driver programs fixed panel registers, sleeps 250 ms after exit-sleep, and enables display. Runtime rotation rewrites registers `0xB6` and MADCTL.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: panel-specific magic values and no gamma hook. Module aliases are SPI-only beyond FBTFT registration compatible string; platform alias is absent compared with many siblings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_tinylcd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_tls8204.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_tls8204.c

Purpose: drives TLS8204 monochrome 84x48 LCDs from an RGB565 framebuffer, similar to PCD8544 but with TLS8204 addressing.

Important APIs/types/functions: `init_display()` configures extended mode, bias `bs`, display line address, and normal display. `set_addr_win()`, `write_vmem()`, and `set_gamma()` manage addressing, page-row packing, and contrast.

Control flow: updates iterate six 8-pixel rows, set page/column before each row because controller memory is larger than visible LCD, pack pixels MSB-first, set DC high, and write one row at a time.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: only contrast/bias are tunable. Nonzero pixels become on. Full-row writes ignore partial update regions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_tls8204.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_uc1611.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_uc1611.c

Purpose: supports UltraChip UC1611 240x160 4-bit grayscale LCDs with 8 bpp framebuffer semantics and packed 4-bit controller transfers.

Important APIs/types/functions: `init_display()` toggles SPI CS polarity and sets bias ratio/gain/pot/temp/load/pump module-parameter controls. `set_var()` configures framebuffer grayscale fields and RAM/LCD mapping for rotations. `write_vmem()` packs two 4-bit grayscale pixels per byte for 8-bit bus or tagged 9-bit words for 9-bit bus. `blank()` controls display enable.

Control flow: init changes SPI mode, soft-resets, configures LCD voltage and grayscale mode, then enables display. Writes compute dirty y range, align page pairs for non-rotated modes, pack pixels according to rotation and bus width, set DC or 9-bit data bit, and call the bus write op.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: mutating `par->spi->mode` by XOR can be surprising if called more than once. `txbuflen=-1` relies on FBTFT dynamic buffer sizing. Packing differs by rotation and bus width, making off-by-one and odd-length dirty region bugs likely.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_uc1611.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_uc1701.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_uc1701.c

Purpose: supports UC1701 102x64 monochrome LCD controllers.

Important APIs/types/functions: `init_display()` performs soft reset and writes start line, orientation, pixel mode, bias, power, voltage, volume, advanced program control, and display enable. `set_addr_win()` resets page/column. `write_vmem()` packs each 8-pixel page from RGB565 into bytes and writes per page.

Control flow: full updates loop over `PAGES`, generate one page buffer, issue page/column commands, set DC high, write WIDTH bytes, and set DC low afterward.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: defined address shift constants are unused, so top/bottom view column offsets may be incomplete. `set_addr_win()` ignores xs/ys/xe/ye. No contrast/gamma hook despite volume-mode initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_uc1701.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_upd161704.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_upd161704.c

Purpose: supports NEC uPD161704 240x320 16-bit-register LCD controllers.

Important APIs/types/functions: `init_display()` writes a Lib_UTFT-derived oscillator, y-setting, power, window, display-area, gate-scan, color, RAM-control, and display-on sequence. `set_addr_win()` sets GRAM cursor for rotations and issues register `0x0e`. `set_var()` adjusts display/RAM control registers for rotation.

Control flow: after reset, the controller is powered and windowed to full 240x320. Runtime address-window calls set the cursor from rotation and common FBTFT code streams pixels.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: many microsecond delays and magic power constants are panel-specific. No gamma hook or ID check. The display-on register writes `0x0000`, which should be confirmed against the controller datasheet.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_upd161704.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fbtft-bus.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fbtft-bus.c

Purpose: provides exported shared FBTFT bus helpers for writing controller registers and framebuffer memory over 8-, 9-, and 16-bit buses.

Important APIs/types/functions: macro `define_fbtft_write_reg()` generates and exports `fbtft_write_reg8_bus8()`, `fbtft_write_reg16_bus8()`, and `fbtft_write_reg16_bus16()`. `fbtft_write_reg8_bus9()` handles 9-bit command/data SPI, including 8-bit SPI emulation padding. Video-memory helpers are `fbtft_write_vmem16_bus8()`, `fbtft_write_vmem16_bus9()`, `fbtft_write_vmem8_bus8()` (stub), and `fbtft_write_vmem16_bus16()`.

Control flow: register helpers optionally log arguments, prepend `par->startbyte`, write the first argument with DC low as command, then write remaining arguments with DC high as data. Video-memory helpers set DC high and chunk framebuffer bytes through `par->txbuf` for endian conversion or 9-bit tagging. Non-buffered 16-over-8 writes fall back to raw `fbtftops.write()`.

State and persistence: no persistent state. It reads `struct fbtft_par` fields such as `buf`, `txbuf`, `startbyte`, `gpio.dc`, SPI bits-per-word, and framebuffer memory.

Dependencies and integration: exported to panel modules and used by FBTFT core defaults. Depends on GPIO descriptor DC control, SPI settings, endian helpers, and `fbtft_write_buf_dc()`.

Risks: the generated register helper's data write length multiplies by `sizeof(data_type) + offset`, which is subtle when `startbyte` is present. `fbtft_write_reg8_bus9()` pads when emulating 9-bit over 8-bit SPI and assumes zero is a no-op. `fbtft_write_vmem8_bus8()` is unimplemented and returns `-1`. All helpers assume valid buffers sized by the core.

Test signals: bus traces for command/data DC transitions, startbyte panels, 9-bit native and emulated SPI, endian correctness for RGB565, chunking across small tx buffers, null txbuf path, and callers accidentally selecting the unimplemented 8-bit vmem helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fbtft-bus.c -->
