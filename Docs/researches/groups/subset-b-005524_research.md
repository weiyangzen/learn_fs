# subset-b-005524 Research

Grouped source research for selected legacy MUSB glue/DMA drivers and USB PHY drivers under `sources/distributed-fs/ceph-client/drivers/usb`. Each section is marker-delimited for source-tree-aligned reconciliation.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/tusb6010.c -->
# sources/distributed-fs/ceph-client/drivers/usb/musb/tusb6010.c

## Purpose

`tusb6010.c` is the MUSB platform glue for the TI TUSB6010 USB 2.0 OTG dual-role controller when connected through the parallel NOR-style host interface. It adapts the generic MUSB core to TUSB6010 register layout, byte-access limitations, FIFO access rules, power/clock/idle behavior, OTG/VBUS state changes, platform GPIO power sequencing, and child `musb-hdrc` platform-device registration.

## Important APIs, Types, and Functions

`struct tusb6010_glue` stores parent device, child MUSB platform device, optional generic PHY device pointer, and power/interrupt GPIO descriptors. `tusb_ops` is the integration surface for MUSB core: custom register accessors, FIFO offsets/access, DMA hooks, enable/disable, mode, idle, VBUS status, and VBUS control.

Hardware helpers include `tusb_get_revision()`, `tusb_print_revision()`, `tusb_wbus_quirk()`, `tusb_readb()`, `tusb_writeb()`, `tusb_read_fifo()`, `tusb_write_fifo()`, `tusb_set_clock_source()`, `tusb_allow_idle()`, `tusb_musb_set_mode()`, `tusb_musb_set_vbus()`, and `tusb_musb_vbus_status()`. Lifecycle functions are `tusb_probe()`, `tusb_remove()`, `tusb_musb_init()`, `tusb_musb_start()`, `tusb_musb_exit()`, `tusb_musb_enable()`, and `tusb_musb_disable()`.

## Control Flow

Probe obtains `enable` and `int` GPIOs, installs `tusb_ops` into caller-provided MUSB platform data, registers a generic USB PHY provider, and creates a `musb-hdrc` child with the two memory resources plus an IRQ derived from the interrupt GPIO. During MUSB init, the driver gets a USB2 PHY, records async/sync DMA physical windows from resources, ioremaps the sync window, shifts `musb->mregs` by `TUSB_BASE_OFFSET`, powers the chip through the enable GPIO, waits for the INT pin to assert readiness, validates the product-test reset value, reads silicon revision, configures VLYNQ/NOR interrupt mode, PHY clock, PRCM management, CPU bus signals, PHY ID pullup, and installs the TUSB interrupt handler.

The IRQ path masks TUSB interrupts, reads `TUSB_INT_SRC`, handles wakeup and silicon errata, synthesizes OTG state changes not reported by the Mentor core, clears DMA status while leaving transfer completion to `tusb6010_omap.c`, maps TUSB USB-IP endpoint interrupt bits into `musb->int_tx` and `musb->int_rx`, calls `musb_interrupt()`, clears non-reserved interrupt bits, schedules or cancels idle, and restores the mask. Idle is timer-driven through `musb_do_idle()` and `tusb_musb_try_idle()`.

## State and Persistence Behavior

State is volatile kernel and hardware register state. `struct musb` holds the active OTG state, revision, IO bases, DMA windows, timers, and PHY pointer; `struct tusb6010_glue` owns parent/child platform linkage and GPIOs. Hardware state persists in TUSB registers while the chip is powered: PRCM clock source, wake masks, VBUS/session timers, PHY controls, DMA request configuration, CPU interface pullups, and interrupt masks.

The file also uses two risky file-scope state holders: `the_musb`, used by the PHY `set_power` callback, and static saved PHY control values in `tusb_wbus_quirk()`. Those assume a single active controller instance or serialized use.

## Dependencies and Integration Points

The driver depends on Linux platform devices, GPIO descriptors, generic USB PHY registration, MUSB core platform ops, IRQ type control, timers, DMA resource layout, and TUSB register definitions from `tusb6010.h`. It integrates with `tusb6010_omap.c` when `CONFIG_USB_TUSB_OMAP_DMA` is enabled and exposes a child device consumed by the generic `musb-hdrc` core.

## Risks and Test Signals

Main risks are hardware-ordering regressions, singleton assumptions, IRQ mask/clear handling around reserved bits, and silicon errata workarounds. `usb_phy_generic_unregister(glue->phy)` is called even though this source never stores the return from `usb_phy_generic_register()` in `glue->phy`, which is a lifetime bug signal. FIFO code must preserve 16/32-bit access constraints on buses without byte cycles. Tests should cover probe with GPIO power sequencing, revision detection, host/peripheral/OTG modes, VBUS transitions, wake from idle, TUSB rev 3.0 WBUS quirk, endpoint interrupts, short FIFO transfers, DMA-enabled builds, and remove after failed or partial probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/tusb6010.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/tusb6010.h -->
# sources/distributed-fs/ceph-client/drivers/usb/musb/tusb6010.h

## Purpose

`tusb6010.h` is the private register map for the TUSB6010 MUSB glue and OMAP DMA support. It defines the controller's memory layout, system/PHY/PRCM/interrupt/GPIO/DMA register offsets, bit masks, field macros, FIFO address calculation, and silicon revision constants.

## Important APIs, Types, and Functions

This header has no functions or types. Important constants include `TUSB_BASE_OFFSET`, `TUSB_FIFO_BASE`, `TUSB_SYS_REG_BASE`, `TUSB_DEV_CONF`, `TUSB_PHY_OTG_CTRL`, `TUSB_DEV_OTG_STAT`, `TUSB_DEV_OTG_TIMER`, `TUSB_PRCM_*`, `TUSB_INT_*`, `TUSB_USBIP_INT_*`, `TUSB_DMA_*`, `TUSB_GPIO_*`, `TUSB_EP_*`, `TUSB_WAIT_COUNT`, `TUSB_SCRATCH_PAD`, `TUSB_PROD_TEST_RESET`, `TUSB_DIDR1_*`, and revision tags `TUSB_REV_10` through `TUSB_REV_31`.

## Control Flow

Runtime flow is implemented by C files using these constants. `tusb6010.c` programs PRCM, wake, PHY, VBUS, FIFO, and interrupt registers; `tusb6010_omap.c` programs DMA request routing and endpoint transfer-size registers. Field macros such as `TUSB_DEV_OTG_TIMER_VAL()`, `TUSB_PRCM_MNGMT_*`, `TUSB_DMA_REQ_CONF_*`, and `TUSB_EP_CONFIG_XFR_SIZE()` encode values before MMIO writes.

## State and Persistence Behavior

The header names hardware state rather than owning state. Register writes affect chip-local power, wake, OTG, endpoint, FIFO, interrupt, and DMA behavior until reset or power removal. Reserved-bit masks encode persistence rules: callers must avoid writing ones into reserved status/mask fields when clearing or masking interrupts.

## Dependencies and Integration Points

The definitions are tightly coupled to TUSB6010 hardware documentation and to MUSB platform glue. They assume a 32-bit system/control register block, 32-bit FIFO windows, and a Mentor core offset at `0x400`.

## Risks and Test Signals

The risk is silent hardware misprogramming from incorrect masks or offsets. Tests are mostly indirect: successful TUSB probe, revision logging, interrupt delivery, DMA request mapping, FIFO transfer correctness, and suspend/resume/idle wake behavior. Any edits should be validated against the data sheet and with register readback on real hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/tusb6010.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/tusb6010_omap.c -->
# sources/distributed-fs/ceph-client/drivers/usb/musb/tusb6010_omap.c

## Purpose

`tusb6010_omap.c` implements the MUSB DMA-controller adapter for TUSB6010 on OMAP systems. It maps MUSB endpoint DMA requests to Linux DMAEngine channels named `dmareq0` through `dmareq4`, programs TUSB endpoint transfer-size registers, and handles TUSB-specific errata around DMA alignment, transfer-size corruption, shared request lines, and short-packet completion.

## Important APIs, Types, and Functions

`struct tusb_dma_data` binds a TUSB DMA request number to a DMAEngine channel. `struct tusb_omap_dma_ch` is per-active-MUSB-DMA-channel state: endpoint, direction, DMA request data, address, packet size, transfer length, and completed length. `struct tusb_omap_dma` owns the MUSB `dma_controller`, TUSB base, request pool, and multichannel flag.

The MUSB-facing callbacks are `tusb_omap_dma_allocate()`, `tusb_omap_dma_release()`, `tusb_omap_dma_program()`, `tusb_omap_dma_abort()`, `tusb_dma_controller_create()`, and `tusb_dma_controller_destroy()`. Internal helpers manage request mapping: `tusb_omap_use_shared_dmareq()`, `tusb_omap_free_shared_dmareq()`, `tusb_omap_dma_allocate_dmareq()`, `tusb_omap_dma_free_dmareq()`, and `tusb_omap_dma_cb()`.

## Control Flow

Controller creation masks TUSB DMA interrupts, clears endpoint mapping, configures burst/request timing, allocates up to five generic `struct dma_channel` wrappers, requests one DMAEngine channel in single-channel mode or all request channels in multichannel mode, and returns a populated `dma_controller`. Channel allocation rejects endpoint zero, chooses an unused wrapper, records endpoint/direction, and either maps a dedicated request line for TUSB rev 3+ or uses request 0 dynamically.

Programming rejects odd addresses, transfers smaller than 32 bytes, transfers larger than one packet, and addresses that would use the corrupt async DMA path. It also refuses if the previous endpoint transfer-size register is nonzero. On success it maps CPU memory, configures DMAEngine for sync or async FIFO physical address and bus width, prepares a single slave transfer, programs MUSB TX/RX CSR DMA bits, writes packet-size and transfer-size registers, and issues pending DMA. Callback computes actual length from TUSB remaining count, works around corrupted remaining values, copies final 1-31 bytes by PIO, frees shared DMA request state, marks the channel free, calls `musb_dma_completion()`, and manually terminates short TX packets with `TXPKTRDY`.

## State and Persistence Behavior

State lives in allocated controller/channel objects and in static `dma_channel_pool[MAX_DMAREQ]`, making the implementation effectively singleton-oriented. Hardware state persists in `TUSB_DMA_EP_MAP`, endpoint transfer-size registers, DMA request configuration, and MUSB endpoint CSR bits until cleared or overwritten.

## Dependencies and Integration Points

The file depends on MUSB DMA controller APIs, DMAEngine slave configuration, TUSB register definitions, TUSB MUSB glue-provided endpoint FIFO addresses, and platform DMA channel naming. It is selected through `tusb_ops` in `tusb6010.c`.

## Risks and Test Signals

Risk areas include singleton static channel pool, partial cleanup paths, DMA map return values not checked, use of `phys_to_virt()` on DMA addresses, shared request release mismatch, and several hardware errata assumptions. Tests should exercise endpoint allocation/release, rev 2 shared request use, rev 3 multichannel use, aligned and unaligned buffers, rejected small/large transfers, short TX packet termination, RX tail PIO copy, abort while busy, DMAEngine request failures, and controller destroy after partial allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/tusb6010_omap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/ux500.c -->
# sources/distributed-fs/ceph-client/drivers/usb/musb/ux500.c

## Purpose

`ux500.c` is the ST-Ericsson Ux500 MUSB platform glue. It creates a `musb-hdrc` child device, supplies Ux500-specific MUSB platform operations, wires USB PHY notifications into MUSB OTG/VBUS state, manages the platform clock, and provides suspend/resume integration.

## Important APIs, Types, and Functions

`ux500_musb_hdrc_config` declares a 16-endpoint dynamic-FIFO multipoint MUSB instance. `struct ux500_glue` stores parent device, child MUSB platform device, and clock. Important callbacks are `ux500_musb_set_vbus()`, `musb_otg_notifications()`, `ux500_musb_interrupt()`, `ux500_musb_init()`, and `ux500_musb_exit()`. `ux500_ops` binds quirks, optional UX500 DMA callbacks, FIFO mode, init/exit, and VBUS control.

## Control Flow

Probe accepts platform data or builds it from DT `dr_mode`, allocates a child `musb-hdrc`, gets and enables the parent clock, copies resources and platform data into the child, and registers it. MUSB init gets the USB2 PHY, registers a notifier, and installs the Ux500 interrupt handler. PHY notifications for ID grounding, VBUS connect, and disconnect call into `ux500_musb_set_vbus()` or update OTG state.

The IRQ handler reads MUSB USB/TX/RX interrupt status under `musb->lock` and delegates to `musb_interrupt()` when any status is pending. VBUS control sets or clears `MUSB_DEVCTL_SESSION`, switches MUSB host/device mode, waits for A-device configuration in one path, and delays after VBUS-off to allow discharge.

## State and Persistence Behavior

Persistent runtime state is in `struct ux500_glue`, `struct musb`, the USB PHY notifier registration, and the enabled platform clock. Hardware state includes MUSB `DEVCTL`, endpoint interrupt registers, and host/device mode bits. No file-backed state exists.

## Dependencies and Integration Points

The file depends on platform devices, clocks, OF `dr_mode`, MUSB core, `linux/usb/musb-ux500.h` notification event constants, and optional `ux500_dma.c` support when `CONFIG_USB_UX500_DMA` is enabled. It integrates with AB8500-style PHY drivers via USB PHY notifier events.

## Risks and Test Signals

Risks include VBUS/off timing assumptions, busy-wait timeout behavior, notifier lifecycle on init failure, and DT mode parsing that leaves mode unchanged for unknown strings. Tests should cover DT and platform-data probe, clock enable failure, PHY probe deferral, notifier events for ID/VBUS/none, host/peripheral mode transitions, suspend/resume clock and PHY suspend ordering, and remove after child registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/ux500.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/ux500_dma.c -->
# sources/distributed-fs/ceph-client/drivers/usb/musb/ux500_dma.c

## Purpose

`ux500_dma.c` implements a DMAEngine-backed MUSB DMA controller for Ux500 platforms. It preallocates fixed RX/TX DMA channels associated with MUSB endpoint pairs and exposes MUSB DMA callbacks for allocation, compatibility testing, programming, abort, create, and destroy.

## Important APIs, Types, and Functions

`struct ux500_dma_channel` wraps a MUSB `dma_channel`, DMAEngine channel, endpoint pointer, transfer length, cookie, logical channel number, direction, and allocation flag. `struct ux500_dma_controller` owns RX and TX channel arrays plus the MUSB private pointer and physical register base.

Key functions are `ux500_dma_controller_create()`, `ux500_dma_controller_destroy()`, `ux500_dma_controller_start()`, `ux500_dma_controller_stop()`, `ux500_dma_channel_allocate()`, `ux500_dma_channel_release()`, `ux500_dma_channel_program()`, `ux500_dma_channel_abort()`, `ux500_dma_is_compatible()`, `ux500_configure_channel()`, and `ux500_dma_callback()`.

## Control Flow

Creation allocates the controller, records the MUSB physical base resource, installs MUSB DMA callbacks, and requests DMAEngine channels. Requesting first tries named channels such as `iep_1_9` or `oep_1_9`, then falls back to board-data DMA filters and parameter arrays. Allocation maps endpoint number to one of eight RX or TX channels, enforcing one user per direction/channel. Programming marks the channel busy, builds a one-entry scatterlist from the DMA address, configures the DMA slave endpoint FIFO address, chooses 1-byte or 4-byte bus width by transfer alignment, prepares a slave SG descriptor with callback, submits, and issues pending.

Completion runs under `musb->lock`, records actual length, marks status free, and calls `musb_dma_completion()`. Abort clears MUSB TX/RX DMA CSR bits, terminates the DMAEngine channel, and marks the channel free. Destroy releases all DMAEngine channels and frees controller memory.

## State and Persistence Behavior

State is per-controller memory plus external DMAEngine channel state. `cur_len`, `cookie`, `status`, and `is_allocated` are active-transfer state. Hardware-visible state includes DMA controller descriptors and MUSB endpoint CSR DMA bits. No persistent storage exists.

## Dependencies and Integration Points

The file depends on DMAEngine slave APIs, MUSB DMA controller interfaces, Ux500 MUSB platform data, named DMA channels, endpoint FIFO offset callbacks, and Linux DMA mapping helpers. It is wired from `ux500_ops`.

## Risks and Test Signals

Risks include use of `pfn_to_page(PFN_DOWN(dma_addr))` on DMA addresses, no explicit `dmaengine_submit()` error check, named/fallback channel mismatch, endpoint 8/16 pairing assumptions, and compatibility restrictions that may force PIO for unaligned or short transfers. Tests should cover all endpoint-to-channel mappings, repeated allocate/release, named-channel and filter fallback paths, unaligned rejection, TX/RX program/complete, abort while busy, DMA request failure cleanup, and removal after partially allocated channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/musb/ux500_dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/usb/phy/Kconfig

## Purpose

`drivers/usb/phy/Kconfig` declares build-time configuration for legacy USB PHY and transceiver drivers. It provides the `USB_PHY` umbrella symbol and feature symbols for AB8500, Freescale OTG, Keystone, NOP/generic, AM335x, TWL6030, GPIO VBUS, OMAP OTG, Tahvo, ISP1301, MXS, Tegra, ULPI, and ULPI viewport support.

## Important APIs, Types, and Functions

This is a Kconfig file, so the API surface is configuration symbols. Important symbols in this subset include `USB_PHY`, `AB8500_USB`, `FSL_USB2_OTG`, `KEYSTONE_USB_PHY`, `NOP_USB_XCEIV`, `AM335X_CONTROL_USB`, `AM335X_PHY_USB`, `USB_GPIO_VBUS`, `OMAP_OTG`, `TAHVO_USB`, `TAHVO_USB_HOST_BY_DEFAULT`, `USB_ISP1301`, and `USB_MXS_PHY`.

## Control Flow

There is no runtime flow. Kconfig dependency resolution controls which source files compile. Many PHY drivers `select USB_PHY`; AM335x PHY selects its control module and `USB_COMMON`; several entries guard built-in/module combinations with `depends on USB_GADGET || !USB_GADGET` to avoid a built-in PHY depending on modular gadget code.

## State and Persistence Behavior

The file persists only kernel build configuration choices. Runtime behavior is indirect: selected symbols decide which modules exist and which platform/OF devices can bind.

## Dependencies and Integration Points

It integrates with the USB PHY Makefile and architecture/platform symbols such as `AB8500_CORE`, `USB_EHCI_FSL`, `USB_FSL_USB2`, `USB_OTG_FSM`, `ARCH_KEYSTONE`, `ARM`, `TWL4030_CORE`, `OMAP_USB2`, `ARCH_OMAP_OTG`, `MFD_RETU`, `I2C`, `ARCH_MXC`, `ARCH_MXS`, and `ARCH_TEGRA`.

## Risks and Test Signals

Risks include impossible built-in/module combinations, missing selects for helper code, and stale dependencies preventing compile-test coverage. Build matrix tests should cover all listed symbols as built-in and module where legal, with `COMPILE_TEST` for cross-platform drivers and `USB_GADGET=m` cases for dependency guards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/Makefile -->
# sources/distributed-fs/ceph-client/drivers/usb/phy/Makefile

## Purpose

`drivers/usb/phy/Makefile` maps USB PHY Kconfig symbols to object files. It controls which legacy PHY drivers and shared helpers are built into the kernel or emitted as modules.

## Important APIs, Types, and Functions

The important outputs are object mappings: `phy.o` for `CONFIG_USB_PHY`, `of.o` for `CONFIG_OF`, and driver objects for `CONFIG_AB8500_USB`, `CONFIG_FSL_USB2_OTG`, `CONFIG_NOP_USB_XCEIV`, `CONFIG_TAHVO_USB`, `CONFIG_AM335X_CONTROL_USB`, `CONFIG_AM335X_PHY_USB`, `CONFIG_OMAP_OTG`, `CONFIG_TWL6030_USB`, `CONFIG_USB_TEGRA_PHY`, `CONFIG_USB_GPIO_VBUS`, `CONFIG_USB_ISP1301`, `CONFIG_USB_MXS_PHY`, `CONFIG_USB_ULPI`, `CONFIG_USB_ULPI_VIEWPORT`, and `CONFIG_KEYSTONE_USB_PHY`.

## Control Flow

There is no runtime flow. Kbuild expands `obj-$(CONFIG_...)` entries according to configuration values and links the corresponding object into built-in archives or modules.

## State and Persistence Behavior

The Makefile persists build structure only. Runtime state is created by the drivers it includes.

## Dependencies and Integration Points

It integrates directly with `Kconfig` symbols and the Linux Kbuild system. It also reflects helper dependencies: OF helper code builds whenever `CONFIG_OF` is enabled, while `phy.o` builds only under `USB_PHY`.

## Risks and Test Signals

Risks are stale symbol/object names, missing objects for enabled symbols, and object ordering regressions if helper providers are needed by built-in consumers. Test signals are allmodconfig/allnoconfig/allyesconfig builds and targeted builds for each PHY symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/of.c -->
# sources/distributed-fs/ceph-client/drivers/usb/phy/of.c

## Purpose

`of.c` provides a small Device Tree helper for legacy USB PHY users. It parses a node's `phy_type` string and returns the corresponding `enum usb_phy_interface`.

## Important APIs, Types, and Functions

The exported API is `of_usb_get_phy_mode(struct device_node *np)`. It maps `""`, `utmi`, `utmi_wide`, `ulpi`, `serial`, and `hsic` through the `usbphy_modes[]` table to values of `enum usb_phy_interface`.

## Control Flow

The function reads `phy_type` with `of_property_read_string()`. Missing or invalid strings return `USBPHY_INTERFACE_MODE_UNKNOWN`; a matching table entry returns its index.

## State and Persistence Behavior

There is no runtime state beyond the static string table. The parsed value is a transient interpretation of Device Tree data.

## Dependencies and Integration Points

The file depends on OF APIs and `linux/usb/of.h`/`linux/usb/otg.h` enum definitions. Controller and PHY drivers use it to translate firmware description into register programming choices.

## Risks and Test Signals

Risks are binding-string drift and the legacy `phy_type` property differing from newer PHY bindings. Tests should pass nodes with missing, known, and unknown `phy_type` values and verify callers handle `UNKNOWN` gracefully.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/of.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-ab8500-usb.c -->
# sources/distributed-fs/ceph-client/drivers/usb/phy/phy-ab8500-usb.c

## Purpose

`phy-ab8500-usb.c` is the USB transceiver driver for ST-Ericsson AB8500/AB8505 PMIC-family chips. It detects USB link-status changes, classifies cable/charger/ACA states, powers host or peripheral PHY modes, notifies Ux500 MUSB glue through USB PHY notifiers, manages regulators/clock/pinctrl, applies PMIC PHY tuning and watchdog workarounds, and registers a legacy `usb_phy`.

## Important APIs, Types, and Functions

`struct ab8500_usb` stores `struct usb_phy`, PMIC pointer, current mode, VBUS draw, delayed PHY-disable work, system clock, three regulators, saved voltage, previous link status, pinctrl handles, charger-detection flag, and behavior flags. Link status enums model AB8500 and AB8505 register encodings; `enum ab8500_usb_mode` tracks idle, peripheral, host, dedicated charger, and UART states.

Key functions include regulator helpers, `ab8500_usb_phy_enable()`, `ab8500_usb_phy_disable()`, AB8500/AB8505 link-status update functions, `abx500_usb_link_status_update()`, IRQ handlers for link status and disconnect, `ab8500_usb_set_host()`, `ab8500_usb_set_peripheral()`, `ab8500_usb_restart_phy()`, tuning helpers, `ab8500_usb_probe()`, and `ab8500_usb_remove()`.

## Control Flow

Probe rejects old AB8500 revisions, allocates PHY/OTG structures, sets flags based on chip family, obtains regulators and sysclk, requests link/status/disconnect IRQs, registers the USB2 PHY, applies tuning for newer AB8500/AB8505, runs watchdog and PHY restart sequences, then reads initial link status. Link-status IRQ reads a PMIC line-status register and dispatches to the family-specific decoder. USB host/peripheral links enable the corresponding PHY, call `UX500_MUSB_PREPARE`, and send `UX500_MUSB_ID` or `UX500_MUSB_VBUS`; charger states send charger notifications and USB charger events; idle/disconnect states reset mode and VBUS draw.

Disconnect IRQ disables host/peripheral/UART PHY paths, sends notifier cleanup for peripheral mode, handles AB8500 v2.0 dedicated-charger workaround, and returns idle. `set_host` and `set_peripheral` only update pointers directly; when called with NULL from contexts that may be atomic they schedule delayed work to disable PHY safely.

## State and Persistence Behavior

Runtime state is held in `struct ab8500_usb` and PMIC registers. Persistent hardware effects include regulator voltage/load changes, PMIC PHY control bits, PHY tuning registers, pinctrl state, watchdog control register toggles, and link-status/charger detection behavior. No filesystem persistence exists.

## Dependencies and Integration Points

The file depends on ABx500 MFD register APIs, AB8500 chip-id helpers, regulators, clocks, pinctrl, threaded IRQs, USB PHY/OTG core, and Ux500 MUSB notifier event constants. It is a key provider for `ux500.c` OTG notifications.

## Risks and Test Signals

Risks include duplicated `if (ab->mode == USB_IDLE)` text in the AB8505 peripheral path, a duplicated `return irq;` line in IRQ setup, races between IRQs and scheduled disable work, regulator-voltage restoration when USB is not sole consumer, and correct handling of spurious link statuses. Tests should cover AB8500 and AB8505 cable matrix, ACA RID A/B/C, charger detection, boot-with-cable, disconnect in host/peripheral/UART/charger modes, NULL host/gadget callbacks, regulator failures, tuning failures, and remove while work is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-ab8500-usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-am335x-control.c -->
# sources/distributed-fs/ceph-client/drivers/usb/phy/phy-am335x-control.c

## Purpose

`phy-am335x-control.c` is the AM335x USB control-module companion driver. It owns the shared control registers used by AM335x USB PHY instances and exports a `struct phy_control` callback table so per-PHY drivers can power PHY 0/1 and configure wakeup bits.

## Important APIs, Types, and Functions

`struct am335x_control_usb` stores device, PHY control register base, wakeup register base, spinlock, and embedded `struct phy_control`. Internal callbacks are `am335x_phy_power()` and `am335x_phy_wkup()`. Exported lookup API is `am335x_get_phy_control(struct device *dev)`.

## Control Flow

Probe matches `ti,am335x-usb-ctrl-module`, maps named resources `phy_ctrl` and `wakeup`, initializes the spinlock, copies the static callback table, and stores drvdata. `am335x_get_phy_control()` parses the caller's `ti,ctrl_mod` phandle, finds the matching platform device bound to this driver, retrieves drvdata, drops references, and returns the callback table. Power operations select register offsets for ID 0 or 1, clear or set PHY power-down bits, and configure VBUS/session comparator bits based on host vs non-host mode. Wake operations update PHY wake-enable bits under spinlock.

## State and Persistence Behavior

State persists in mapped control-module registers: power-down bits, OTG VBUS detect/session-end enable bits, and wake-enable bits. Kernel state is the single control object plus exported callback pointers.

## Dependencies and Integration Points

The file depends on OF phandles, platform bus lookup, MMIO, spinlocks, and the header `phy-am335x-control.h`. It is consumed by `phy-am335x.c`.

## Risks and Test Signals

Risks include cross-device lifetime of returned callback pointers, no NULL checks in inline wrappers, invalid PHY IDs producing only `WARN_ON`, and mixed locked/unlocked register updates. Tests should cover phandle absence/defer, both PHY IDs, host/peripheral power-on bit patterns, wake enable/disable, invalid IDs, and probe resource failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-am335x-control.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-am335x-control.h -->
# sources/distributed-fs/ceph-client/drivers/usb/phy/phy-am335x-control.h

## Purpose

`phy-am335x-control.h` declares the callback contract between the AM335x USB PHY driver and the AM335x control-module driver.

## Important APIs, Types, and Functions

`struct phy_control` contains two callbacks: `phy_power()` and `phy_wkup()`. Inline wrappers `phy_ctrl_power()` and `phy_ctrl_wkup()` invoke those callbacks. `am335x_get_phy_control()` returns a callback table for a device's `ti,ctrl_mod` phandle.

## Control Flow

The header has no independent execution. `phy-am335x.c` calls `am335x_get_phy_control()` during probe and later invokes the inline wrappers in init/shutdown and PM paths.

## State and Persistence Behavior

The header owns no state. The callback implementation changes AM335x control-module hardware state.

## Dependencies and Integration Points

It depends on `enum usb_dr_mode`, `struct device`, integer types, and bool definitions through includers. It is private to the AM335x PHY/control split.

## Risks and Test Signals

The wrappers assume a non-NULL `phy_control` and non-NULL callbacks. Compile coverage plus AM335x probe-defer and PM tests are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-am335x-control.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-am335x.c -->
# sources/distributed-fs/ceph-client/drivers/usb/phy/phy-am335x.c

## Purpose

`phy-am335x.c` provides a USB2 PHY driver for AM335x SoCs by combining the generic NOP USB PHY framework with AM335x-specific control-module power and wake callbacks.

## Important APIs, Types, and Functions

`struct am335x_phy` embeds `struct usb_phy_generic`, a `struct phy_control *`, PHY ID, and USB data-role mode. Important callbacks are `am335x_init()`, `am335x_shutdown()`, `am335x_phy_suspend()`, and `am335x_phy_resume()`. Lifecycle functions are `am335x_phy_probe()` and `am335x_phy_remove()`.

## Control Flow

Probe allocates state, retrieves control callbacks through `am335x_get_phy_control()`, reads the DT alias ID `phyN`, derives role mode via `of_usb_get_dr_mode_by_phy()`, creates a generic PHY, overrides its init/shutdown callbacks, disables wakeup by default to avoid immediate DS0 wake, powers the PHY down, and registers it with `usb_add_phy_dev()`. Init powers the PHY on through the control module; shutdown powers it off. Suspend optionally enables PHY wakeup if userspace allowed device wake, then powers off; resume powers on and disables wakeup again.

## State and Persistence Behavior

Runtime state is per-platform-device. Hardware state is owned by the control-module registers reached through callbacks. Wakeup policy persists in the device power-management flags while the device exists.

## Dependencies and Integration Points

The driver depends on OF aliases and role parsing, `phy-am335x-control`, generic USB PHY helper code, platform PM, and the legacy USB PHY registry. It is selected with `AM335X_PHY_USB`.

## Risks and Test Signals

Risks include alias absence, control driver probe ordering, role-mode propagation, and wakeup policy mismatch between standby and DS0. Tests should cover PHY0/PHY1 aliases, missing `ti,ctrl_mod`, host/peripheral/OTG modes, init/shutdown sequencing, suspend/resume with wakeup enabled and disabled, and removal while registered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-am335x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-fsl-usb.c -->
# sources/distributed-fs/ceph-client/drivers/usb/phy/phy-fsl-usb.c

## Purpose

`phy-fsl-usb.c` is the Freescale USB2 OTG transceiver driver. It implements a legacy USB OTG finite-state-machine backend for Freescale dual-role controller registers, manages SRP/HNP signaling, ID-change interrupts, OTG timers, VBUS drive/charge/discharge, and start/stop handoff to host and gadget drivers.

## Important APIs, Types, and Functions

Global objects include `usb_dr_regs`, `fsl_otg_dev`, `srp_wait_done`, OTG FSM timers, driver timers, and `active_timers`. Hardware actions are `fsl_otg_chrg_vbus()`, `fsl_otg_dischrg_vbus()`, `fsl_otg_drv_vbus()`, `fsl_otg_loc_conn()`, `fsl_otg_loc_sof()`, `fsl_otg_start_pulse()`, and `write_ulpi()`.

OTG operation callbacks are collected in `fsl_otg_ops`. Host/gadget integration uses `fsl_otg_set_host()`, `fsl_otg_set_peripheral()`, `fsl_otg_start_host()`, `fsl_otg_start_gadget()`, `fsl_otg_start_srp()`, and `fsl_otg_start_hnp()`. Lifecycle and interrupt functions are `fsl_otg_conf()`, `usb_otg_start()`, `fsl_otg_probe()`, `fsl_otg_remove()`, and `fsl_otg_isr()`.

## Control Flow

Probe requires platform data, allocates the global OTG object and `usb_otg`, initializes timers and FSM ops, registers the USB2 PHY, maps the dual-role controller MMIO resource, runs board `init`, selects endian accessors on PPC, requests a shared IRQ, stops and resets the controller, programs idle USB mode and PHY interface type, enables system-interface output if present, clears/sets OTGSC bits, records initial ID state, and enables ID interrupts.

ID interrupts update FSM `id`, `default_a`, host/gadget role metadata, and either schedule delayed switch-to-gadget or immediately stop gadget, drive VBUS, and start host. SRP starts with data-line pulsing followed by VBUS pulsing, discharge, and wait timers. Host and gadget start/stop call PM suspend/resume methods on registered host/gadget parent devices.

## State and Persistence Behavior

This driver is heavily global and effectively single-instance. FSM inputs, timers, active timer list, role flags, host-working state, mapped MMIO, and PHY registration persist until remove. Hardware state persists in USBCMD, USBMODE, PORTSC, OTGSC, ULPI viewport, and optional system-interface control registers.

## Dependencies and Integration Points

It depends on `linux/usb/otg-fsm.h`, Freescale platform data, host and gadget driver PM callbacks, shared controller resources, IRQs, timers, workqueues, and the register map in `phy-fsl-usb.h`.

## Risks and Test Signals

This source tree shows strong bug signals: duplicated braces near `fsl_otg_get_timer()`, timer switch cases returning `a_wait_vrise_tmr` for many timer IDs, duplicated `.drv_vbus` initializer, pointer debug casts through `int`, busy-wait reset loops without timeout, global singleton state, and cleanup paths that free global objects on some start failures. Tests should include build/static analysis, single and repeated probe/remove, ID cable switching, SRP/HNP flows, host/gadget registration/unregistration, big/little-endian MMIO, IRQ sharing, board init/exit failures, and timer add/delete behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-fsl-usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-fsl-usb.h -->
# sources/distributed-fs/ceph-client/drivers/usb/phy/phy-fsl-usb.h

## Purpose

`phy-fsl-usb.h` defines the Freescale USB dual-role controller register map, OTGSC/PORTSC/USBCMD bitfields, OTG timing constants, software timer structure, controller MMIO layout, and `struct fsl_otg` state used by `phy-fsl-usb.c`.

## Important APIs, Types, and Functions

Important macros cover USBCMD, USBSTS, USBINTR, DEVICEADDR, PORTSC, OTGSC, USBMODE, control register fields, OTG interrupt status/enable masks, and OTG timing constants such as `TA_WAIT_VRISE`, `TA_WAIT_BCON`, `TB_DATA_PLS`, and `TB_SRP_FAIL`. `struct usb_dr_mmap` models the memory-mapped dual-role controller. `struct fsl_otg_timer` and `otg_timer_initializer()` model software timers. `struct fsl_otg` embeds `struct usb_phy`, `struct otg_fsm`, MMIO pointer, delayed work, host-working flag, and IRQ. Public declarations are `fsl_otg_add_timer()`, `fsl_otg_del_timer()`, and `fsl_otg_pulse_vbus()`.

## Control Flow

The C file uses these definitions to reset and program the controller, mask write-one-to-clear bits, configure PHY interface type, manipulate VBUS/SRP/HNP signals, and run OTG FSM timers. `struct usb_dr_mmap` lets code address operational registers by field name.

## State and Persistence Behavior

The header defines both volatile kernel state (`struct fsl_otg`, `struct fsl_otg_timer`) and hardware register state. Register writes affect controller role, port power, OTG signaling, interrupt enable/status, and PHY interface configuration.

## Dependencies and Integration Points

It depends on Linux OTG FSM and USB OTG headers. It is private to the Freescale OTG transceiver driver and platform data using Freescale USB2 controller conventions.

## Risks and Test Signals

The risk is bitfield misuse in mixed host/device/OTG register spaces. Write-one-to-clear masks are especially important for PORTSC/OTGSC. Header changes should be validated by build coverage, register-offset audits, and role-transition tests on Freescale dual-role hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-fsl-usb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-generic.c -->
# sources/distributed-fs/ceph-client/drivers/usb/phy/phy-generic.c

## Purpose

`phy-generic.c` implements the generic "NOP" USB transceiver. It provides a minimal legacy `usb_phy` for boards where PHY hardware is autonomous or controlled only by a clock, reset GPIO, VCC regulator, optional VBUS regulator, and optional VBUS-detect GPIO.

## Important APIs, Types, and Functions

Exported helpers are `usb_phy_generic_register()`, `usb_phy_generic_unregister()`, `usb_gen_phy_init()`, `usb_gen_phy_shutdown()`, and `usb_phy_gen_create_phy()`. OTG operations include `nop_set_suspend()`, `nop_set_vbus()`, `nop_set_peripheral()`, and `nop_set_host()`. The platform driver uses `usb_phy_generic_probe()` and `usb_phy_generic_remove()`.

## Control Flow

`usb_phy_gen_create_phy()` reads optional `clock-frequency`, reset GPIO, VBUS-detect GPIO, `main_clk`, `vcc`, and exclusive `vbus` regulator; allocates `usb_otg`; and initializes generic PHY/OTG callbacks. Probe optionally requests threaded VBUS GPIO IRQ, initializes OTG state from GPIO, sets init/shutdown callbacks, registers the PHY, stores drvdata, and marks wakeup capability from `wakeup-source`.

Init enables VCC and clock and toggles reset. Shutdown asserts reset, disables clock, and disables VCC. VBUS IRQ updates `last_event`, OTG state, and notifiers when VBUS changes. `set_vbus` controls the VBUS regulator for host power when present.

## State and Persistence Behavior

State is `struct usb_phy_generic`: clock, regulators, GPIOs, VBUS state, VBUS regulator enabled flag, and current draw. Hardware state is limited to reset GPIO level, regulator enable/load, clock enable, and VBUS event state.

## Dependencies and Integration Points

It depends on platform devices, device properties, GPIO descriptors, clocks, regulator framework, IRQs, and legacy USB PHY/OTG registration. Other drivers, such as Keystone and AM335x, reuse `usb_phy_gen_create_phy()`.

## Risks and Test Signals

Risks include regulator enable/disable imbalance on error paths, VBUS IRQ before gadget registration, optional-resource error handling, and wakeup interaction with suspend regulator control. Tests should cover no-resource NOP PHY, reset timing, clock-frequency setting, VCC failure, VBUS GPIO rising/falling, vbus regulator set_vbus, host/gadget registration, wakeup-source property, and removal with VBUS regulator enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-generic.h -->
# sources/distributed-fs/ceph-client/drivers/usb/phy/phy-generic.h

## Purpose

`phy-generic.h` declares the private state and helper APIs for the generic NOP USB PHY.

## Important APIs, Types, and Functions

`struct usb_phy_generic` embeds `struct usb_phy` and stores device, clock, VCC regulator, reset GPIO, VBUS-detect GPIO, VBUS regulator, VBUS regulator enabled flag, current draw, and VBUS state. Declared helper APIs are `usb_gen_phy_init()`, `usb_gen_phy_shutdown()`, and `usb_phy_gen_create_phy()`.

## Control Flow

The header has no execution path. `phy-generic.c`, `phy-am335x.c`, and `phy-keystone.c` populate this structure and install optional platform-specific init/shutdown callbacks.

## State and Persistence Behavior

The structure is per-device runtime state. Its fields mirror hardware controls that persist only while the PHY device is active.

## Dependencies and Integration Points

It depends on `linux/usb/usb_phy_generic.h`, GPIO descriptors, and regulators. It is a local helper boundary for legacy USB PHY implementations.

## Risks and Test Signals

Risks are lifecycle misuse by derived drivers, especially overriding callbacks without preserving generic resources. Compile coverage and probe/remove tests for generic, AM335x, and Keystone PHYs are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-generic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-gpio-vbus-usb.c -->
# sources/distributed-fs/ceph-client/drivers/usb/phy/phy-gpio-vbus-usb.c

## Purpose

`phy-gpio-vbus-usb.c` implements a peripheral-only USB PHY that detects VBUS with a GPIO, optionally controls a data-line pullup GPIO, and optionally limits VBUS current through a regulator. It is intended for internal-transceiver B-device controllers without role switching.

## Important APIs, Types, and Functions

`struct gpio_vbus_data` stores VBUS and pullup GPIOs, `struct usb_phy`, regulator, delayed work, cached VBUS state, IRQ, and current draw. Important functions are `gpio_vbus_probe()`, `gpio_vbus_remove()`, `gpio_vbus_irq()`, `gpio_vbus_work()`, `gpio_vbus_set_peripheral()`, `gpio_vbus_set_power()`, `gpio_vbus_set_suspend()`, and PM suspend/resume hooks.

## Control Flow

Probe allocates state and `usb_otg`, gets required `vbus` GPIO, obtains IRQ from platform resource or GPIO, gets optional `pullup` GPIO, requests an edge IRQ, initializes delayed work, gets optional `vbus_draw` regulator, and registers the USB2 PHY. IRQ schedules 100 ms delayed work when a gadget is registered. Work debounces VBUS, updates OTG state and `last_event`, calls `usb_gadget_vbus_connect()` or disconnect, sets default 100 mA draw on connect, toggles optional pullup, sends notifiers, and updates USB PHY event.

`set_peripheral()` binds/unbinds the gadget and forces initial state sampling by calling the IRQ handler. `set_power()` updates current draw only in B-peripheral state; suspend drops draw to zero and restore uses cached current.

## State and Persistence Behavior

Runtime state is in `gpio_vbus_data`; hardware state is GPIO levels and regulator current/enable state. There is no persistent storage.

## Dependencies and Integration Points

The file depends on GPIO descriptors, IRQs, delayed work, regulator framework, USB gadget VBUS helpers, and legacy USB PHY/OTG notifiers. It matches DT compatible `gpio-usb-b-connector`.

## Risks and Test Signals

Risks include edge-trigger bounce, work running during gadget unregister, regulator current-limit failures ignored after logging, sysfs notification name mismatch risk around `vbus_state` in nearby code patterns, and assumption that pullup control belongs in this PHY. Tests should cover VBUS connect/disconnect debounce, gadget bind/unbind with VBUS already high, optional pullup absent/present, regulator absent/failing, suspend/resume IRQ wake, and remove with pending work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-gpio-vbus-usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-isp1301.c -->
# sources/distributed-fs/ceph-client/drivers/usb/phy/phy-isp1301.c

## Purpose

`phy-isp1301.c` is an I2C driver for the NXP ISP1301 USB transceiver. It initializes the transceiver into USB mode, configures pull-downs and interrupt masks, drives VBUS, registers a legacy USB2 PHY, and exports a helper for other code to get the underlying I2C client.

## Important APIs, Types, and Functions

`struct isp1301` stores `struct usb_phy`, mutex, and I2C client. Important helpers are `isp1301_write()`, `isp1301_clear()`, `isp1301_phy_init()`, `isp1301_phy_set_vbus()`, `isp1301_probe()`, `isp1301_remove()`, and exported `isp1301_get_client()`.

## Control Flow

Probe allocates state, initializes the PHY callbacks and label, sets client data, registers the PHY, and stores a singleton fallback client. PHY init clears UART mode, sets mode-control bits, configures OTG control pull-downs, clears pull-ups, and masks all interrupts. `set_vbus` sets or clears `OTG1_VBUS_DRV`. `isp1301_get_client()` first looks up a DT-referenced I2C node, then falls back to the singleton non-DT client with a device reference.

## State and Persistence Behavior

State is the I2C client plus PHY registration. Hardware register writes persist inside the ISP1301 until reset or later configuration. The file-scope fallback client is singleton state.

## Dependencies and Integration Points

It depends on I2C SMBus byte writes, ISP1301 register definitions, OF I2C lookup, and legacy USB PHY registration. Other platform glue can call `isp1301_get_client()`.

## Risks and Test Signals

Risks include ignoring `usb_add_phy_dev()` return, singleton fallback limiting non-DT multi-device systems, unused mutex around I2C access, and no error propagation from init register writes. Tests should cover I2C probe/remove, DT lookup reference handling, non-DT singleton lookup, init register sequence failure injection, VBUS drive toggling, and multiple-device behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-isp1301.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-keystone.c -->
# sources/distributed-fs/ceph-client/drivers/usb/phy/phy-keystone.c

## Purpose

`phy-keystone.c` is a small TI Keystone USB PHY driver layered on the generic NOP PHY helper. Its Keystone-specific behavior is enabling or disabling the SuperSpeed PHY reference clock bit in a PHY control register.

## Important APIs, Types, and Functions

`struct keystone_usbphy` embeds `struct usb_phy_generic` and stores an MMIO `phy_ctrl` base. Important functions are `keystone_usbphy_init()`, `keystone_usbphy_shutdown()`, `keystone_usbphy_probe()`, and `keystone_usbphy_remove()`.

## Control Flow

Probe maps the first MMIO resource, creates a generic PHY, overrides init/shutdown callbacks, stores drvdata, and registers the PHY. Init sets `PHY_REF_SSP_EN` in `USB_PHY_CTL_CLOCK`; shutdown clears it. Remove unregisters the PHY.

## State and Persistence Behavior

Runtime state is per-device. Hardware state is the PHY clock control bit plus any generic PHY resources configured by `usb_phy_gen_create_phy()`.

## Dependencies and Integration Points

The driver depends on OF compatible `ti,keystone-usbphy`, MMIO, generic NOP PHY helpers, and the legacy USB PHY registry. Kconfig depends on `NOP_USB_XCEIV`.

## Risks and Test Signals

Risks include register bit assumptions and generic-resource lifecycle interactions. Tests should cover probe resource failure, generic helper failure, init/shutdown bit readback, remove after registration, and DWC3/Keystone controller integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-keystone.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-mv-usb.h -->
# sources/distributed-fs/ceph-client/drivers/usb/phy/phy-mv-usb.h

## Purpose

`phy-mv-usb.h` is the private register and state header for Marvell/PXA-style OTG controller support. It defines command and OTGSC bits, OTG timing constants, software FSM state, MMIO register layout, and per-device runtime state.

## Important APIs, Types, and Functions

Important definitions include `USBCMD_RUN_STOP`, `USBCMD_CTRL_RESET`, `OTGSC_CTRL_*`, `OTGSC_STS_*`, `OTGSC_INTSTS_*`, `OTGSC_INTR_*`, timing constants `T_A_WAIT_*` and `T_B_*`, `enum otg_function`, `enum mv_otg_timer`, `struct mv_otg_ctrl`, `struct mv_otg_regs`, and `struct mv_otg`.

## Control Flow

The header has no execution path. Implementation code uses `struct mv_otg_regs` to access operational registers, `struct mv_otg_ctrl` to carry OTG FSM inputs and timeout flags, and `struct mv_otg` to coordinate PHY registration, IRQ handling, delayed work, workqueue, platform data, clocks, and active/clock-gating state.

## State and Persistence Behavior

`struct mv_otg_ctrl` is volatile FSM state. `struct mv_otg_regs` names hardware state for run/reset, port and OTG signaling, endpoint status, mux control, and interrupt bits. `struct mv_otg` persists for one probed controller instance.

## Dependencies and Integration Points

It depends on Linux types, timers, workqueues, clocks, platform data, and USB PHY definitions through includers. It is intended for Marvell OTG controller code sharing the ChipIdea/EHCI-style register layout.

## Risks and Test Signals

Risks are incorrect OTGSC write-one-to-clear behavior, timer-unit confusion, and mismatch between `VUSBHS_MAX_PORTS` layout and actual hardware. Tests should validate role switching, ID/VBUS interrupts, timer expiry, reset/run-stop programming, and register offsets against hardware documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-mv-usb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-mxs-usb.c -->
# sources/distributed-fs/ceph-client/drivers/usb/phy/phy-mxs-usb.c

## Purpose

`phy-mxs-usb.c` is the Freescale/NXP MXS/i.MX USB PHY driver. It powers and resets USB PHY blocks, handles SoC-specific errata, controls clocks/regulators/PLL, tunes TX calibration from DT, manages wakeup and suspend behavior, detects charger type through anatop registers, and registers a legacy USB2 PHY.

## Important APIs, Types, and Functions

`struct mxs_phy_data` stores SoC quirk flags; `struct mxs_phy` stores the USB PHY, clock, SoC data, anatop/SIM regmaps, port ID, TX calibration mask/value, and 3.0 V regulator. Important functions include `mxs_phy_init()`, `mxs_phy_shutdown()`, `mxs_phy_suspend()`, `mxs_phy_set_wakeup()`, `mxs_phy_on_connect()`, `mxs_phy_on_disconnect()`, charger detection helpers, `mxs_phy_probe()`, `mxs_phy_remove()`, and system PM helpers.

## Control Flow

Probe maps the PHY resource, gets the clock, optional anatop and SIM syscon regmaps, parses TX calibration properties, reads `usbphy` alias as port ID, fills legacy PHY callbacks, gets SoC match data and optional `phy-3p0` regulator, sets wakeup capability, and registers the PHY. Init delays for clock switching, enables the clock, optionally powers i.MX7ULP PLL, resets the PHY block, enables regulator, powers up, sets auto clock/power bits, applies IP fixes and charger-detect disable, and writes TX calibration. Shutdown clears wake/auto bits, powers down, gates clock, disables PLL/regulator, and disables the clock.

Suspend powers down most PHY circuits and gates the clock, with a low-speed/VBUS exception and PHY2 hardware-clock-control exception. Resume re-enables clock, ungates, and powers up. Wakeup toggles PHY wake bits and may force line disconnect through anatop loopback registers. Charger detection performs data-contact, primary, and secondary detection sequences.

## State and Persistence Behavior

State is per-device plus hardware registers in PHY, anatop, SIM, regulator, and clock frameworks. TX calibration derived from DT persists in PHY TX register after init. Wakeup, disconnect-line, PLL, and charger-detect states persist until changed.

## Dependencies and Integration Points

The driver depends on STMP reset helpers, platform MMIO, clocks, syscon/regmap, OF match data and aliases, regulators, USB PHY callbacks, and i.MX/MXS analog register conventions.

## Risks and Test Signals

This source tree has visible textual defects: duplicated `void __iomem *base;` in probe and an extra comment terminator in charger-disable code, both strong build-failure signals. Functional risks include quirk flag mismatch, port ID errors, anatop absent paths, charger-detect timing, and clock gating around wake. Tests should include build/static analysis, every compatible string, optional anatop/SIM/regulator paths, TX calibration bounds, init/shutdown, suspend/resume low-speed and high-speed devices, wakeup enable/disable, connect/disconnect notifications, charger SDP/CDP/DCP detection, and probe failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-mxs-usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-omap-otg.c -->
# sources/distributed-fs/ceph-client/drivers/usb/phy/phy-omap-otg.c

## Purpose

`phy-omap-otg.c` drives the OMAP1 USB OTG controller output bits based on extcon ID and VBUS state. It bridges external connector notifications into the legacy OMAP OTG control register so host/peripheral mode signaling is visible to the controller.

## Important APIs, Types, and Functions

`struct otg_device` stores MMIO base, cached ID/VBUS booleans, extcon pointer, and notifier blocks. Important functions are `omap_otg_ctrl()`, `omap_otg_set_mode()`, `omap_otg_id_notifier()`, `omap_otg_vbus_notifier()`, and `omap_otg_probe()`.

## Control Flow

Probe requires platform data naming an extcon device, maps the OTG resource, registers notifiers for `EXTCON_USB_HOST` and `EXTCON_USB`, reads initial states, writes the corresponding OTG output bits, logs revision and state, and stores drvdata. ID and VBUS notifiers update cached state and call `omap_otg_set_mode()`, which programs B-session-valid, A-session-valid, or B-session-end bits depending on ID/VBUS combination.

## State and Persistence Behavior

Runtime state is the cached ID/VBUS values and notifier registrations. Hardware state persists in `OMAP_OTG_CTRL` output bits until overwritten.

## Dependencies and Integration Points

The file depends on OMAP1 platform data, extcon, MMIO, and platform devices. It is selected by `OMAP_OTG` and integrates with board-level connector detection.

## Risks and Test Signals

Risks include ambiguous extcon boolean polarity, missing state for some ID/VBUS combinations, no remove callback beyond devm cleanup, and platform-data-only binding. Tests should cover extcon absent/deferred, initial host/peripheral/no-cable states, ID/VBUS notification ordering, register bit readback, and controller behavior during cable changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-omap-otg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-tahvo.c -->
# sources/distributed-fs/ceph-client/drivers/usb/phy/phy-tahvo.c

## Purpose

`phy-tahvo.c` is the Tahvo USB transceiver driver used by Nokia/Retu-Tahvo platforms. It registers a legacy USB PHY, exposes host/peripheral mode control through sysfs, reports VBUS through sysfs and extcon, controls Tahvo USB registers, and connects/disconnects gadget or host state on VBUS changes.

## Important APIs, Types, and Functions

`struct tahvo_usb` stores platform device, USB PHY, VBUS state, mutex, interface clock, IRQ, selected mode, and extcon device. Important functions are `check_vbus_state()`, `tahvo_usb_become_host()`, `tahvo_usb_stop_host()`, `tahvo_usb_become_peripheral()`, `tahvo_usb_stop_peripheral()`, `tahvo_usb_power_off()`, `tahvo_usb_set_suspend()`, `tahvo_usb_set_host()`, `tahvo_usb_set_peripheral()`, `tahvo_usb_vbus_interrupt()`, sysfs `otg_mode` handlers, `tahvo_usb_probe()`, and `tahvo_usb_remove()`.

## Control Flow

Probe allocates state and `usb_otg`, selects default mode from Kconfig, enables the optional interface clock, reads initial VBUS, registers extcon cables, powers the transceiver off, initializes PHY/OTG callbacks, registers the USB2 PHY, stores drvdata, and requests a threaded VBUS IRQ. Host/peripheral set callbacks bind or unbind host/gadget and power the transceiver according to the selected sysfs mode. `otg_mode_store()` switches mode, stopping the previous role and either powering into the new role if a host/gadget is present or powering off. VBUS IRQ serializes through a mutex and updates gadget connection, OTG state, USB PHY events, extcon state, and sysfs notification.

## State and Persistence Behavior

Runtime state is in `tahvo_usb`, extcon, PHY/OTG pointers, and selected mode. Hardware state persists in Tahvo `USBR` register bits controlling host/peripheral switches, suspend, regulator output, and mode. The selected mode is not file-backed; it resets on driver reload.

## Dependencies and Integration Points

The driver depends on Retu MFD register access, extcon provider APIs, legacy USB PHY/OTG, USB gadget VBUS helpers, platform IRQs, sysfs device groups, and an optional `usb_l4_ick` clock.

## Risks and Test Signals

Risks include sysfs `vbus_show()` notifying `"vbus_state"` while the attribute is named `vbus`, `clk_enable()` without prepare, missing error check for `usb_add_phy()` paths beyond return, and races among sysfs mode changes, IRQ, and host/gadget callbacks mitigated only by `serialize`. Tests should cover default host/peripheral builds, sysfs mode changes with and without host/gadget, VBUS IRQ connect/disconnect, extcon state updates, suspend bit toggling, clock absent/present, remove with IRQ active, and sysfs notification behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-tahvo.c -->
