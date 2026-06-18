# subset-b-005507 Research

Grouped source research for Xilinx USB gadget UDC helpers, USB gadget string descriptor helpers, and USB host/EHCI configuration, platform glue, debug, hub, memory, and core lifecycle code. Each source file section is marker-delimited for deterministic reconciliation into the mapped source-tree-aligned reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/udc-xilinx.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/udc-xilinx.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/udc-xilinx.c` implements the Xilinx USB2 device controller as a Linux USB gadget UDC. It registers a platform driver for `xlnx,usb2-device-4.00.a`, exposes `usb_gadget_ops` and `usb_ep_ops`, manages endpoint zero Chapter 9 traffic, queues gadget requests on up to eight endpoints, and drives the controller register block with little- or big-endian accessors detected at probe time. The source was read as a complete 2266-line file.

## Important APIs, Types, and Functions

Core types are `struct xusb_udc`, `struct xusb_ep`, and `struct xusb_req`. `xusb_udc` owns the `usb_gadget`, endpoint array, bound gadget driver, cached setup packet, dummy status request, MMIO base, spinlock, optional DMA flag, clock, and endian-specific read/write callbacks. `xusb_ep` wraps `struct usb_ep`, queue state, descriptor, endpoint DPRAM address, endpoint number, ping-pong buffer state, and direction/type flags.

Important entry points include endpoint ops `xudc_ep_enable()`, `xudc_ep_disable()`, `xudc_ep_queue()`, `xudc_ep_dequeue()`, `xudc_ep_set_halt()`, request allocation/free, and EP0-specific queue/enable stubs. Gadget ops are `xudc_get_frame()`, `xudc_wakeup()`, `xudc_pullup()`, `xudc_start()`, and `xudc_stop()`. Interrupt and protocol handling is split across `xudc_irq()`, `xudc_startup_handler()`, `xudc_ctrl_ep_handler()`, `xudc_nonctrl_ep_handler()`, `xudc_handle_setup()`, `xudc_ep0_in()`, and `xudc_ep0_out()`. Data movement uses `xudc_eptxrx()`, `xudc_read_fifo()`, `xudc_write_fifo()`, and optional DMA helpers `xudc_start_dma()`, `xudc_dma_send()`, and `xudc_dma_receive()`.

## Control Flow

Probe allocates the UDC and a reusable status request, maps MMIO, requests the IRQ, detects optional built-in DMA from `xlnx,has-builtin-dma`, enables `s_axi_aclk` if present, probes register endianness through the test-mode register, initializes endpoints, registers the gadget with `usb_add_gadget_udc()`, and enables global/event/buffer interrupts. Binding a gadget driver calls `xudc_start()`, which stores the driver, sets gadget speed to the driver's max, enables EP0 with a control descriptor, resets address, and clears remote wakeup.

For non-control endpoints, `queue()` maps DMA if needed, attempts immediate service if the endpoint queue is empty, and otherwise appends the request. IN transfers fill DPRAM or DMA into the next free ping-pong buffer, program count registers, and set `XUSB_BUFFREADY_OFFSET`. OUT transfers consume hardware buffer counts, copy or DMA into the request buffer, detect short packets or full request completion, and complete via `xudc_done()`. Interrupt completion clears per-buffer ready flags and re-enters the per-endpoint read/write path for the queue head.

EP0 receives setup packets through `xudc_ctrl_ep_handler()`. The UDC handles standard GET_STATUS, SET_ADDRESS, SET/CLEAR_FEATURE locally, including remote wakeup, test mode, endpoint halt, and deferred address/test-mode application after status stage. Other setup requests are passed to the gadget driver's `setup()` callback outside the spinlock. Reset, suspend, resume, and disconnect events are handled in `xudc_startup_handler()`, which updates speed/state, nukes queues on reset, clears stalls, re-enables selected event interrupts, and calls gadget suspend/resume/disconnect callbacks outside the lock.

## State and Persistence Behavior

The driver has no file-backed persistence. Runtime state is in MMIO registers, endpoint queue lists, per-endpoint ping-pong flags, request `actual/status`, `usb_state`, `remote_wkp`, and EP0 setup phase variables `setupseqtx/setupseqrx`. DMA mappings are per-request and unmapped on completion for nonzero endpoints. System sleep clears/sets the USB ready bit and gates the optional clock, while register contents are otherwise expected to be maintained or reset by the controller/hardware lifecycle.

## Dependencies and Integration Points

The file depends on Linux platform devices, OF matching, clocks, IRQs, DMA mapping, `linux/usb/gadget.h`, and USB Chapter 9 definitions. It integrates upward with composite or function gadget drivers through `usb_add_gadget_udc()` and gadget callbacks, and downward with the Xilinx controller register/DPRAM layout. Device tree integration is the compatible string plus optional `s_axi_aclk` and `xlnx,has-builtin-dma` properties.

## Risks and Edge Cases

The code relies on correct ping-pong buffer bookkeeping; mismatched `curbufnum`, `buffer0ready`, and `buffer1ready` can stall endpoints or overwrite data. DMA uses controller DPRAM addresses derived from MMIO pointers and `virt_to_phys()`, so platform DMA address assumptions are sensitive. Several callbacks deliberately drop and reacquire the spinlock around gadget driver calls; queue state must remain valid across re-entry. EP0 local handling must preserve Chapter 9 sequencing, especially SET_ADDRESS, test mode, zero-length status stages, and setup request cancellation. Endianness detection writes the test-mode register and assumes the attempted big-endian write/read is harmless. Suspend/resume is shallow and does not reconstruct all endpoint registers after full power loss.

## Test Signals

Useful signals include successful bind/unbind of standard gadget functions, enumeration at full and high speed, control request coverage for GET_STATUS/SET_ADDRESS/SET_FEATURE/CLEAR_FEATURE/test mode, remote wakeup behavior, halt/clear-halt with pending requests and busy buffers, IN/OUT bulk and interrupt transfers crossing max-packet boundaries, short packet and overflow handling, DMA and PIO transfer modes, reset/suspend/resume/disconnect interrupt paths, endian variants, and probe/remove with absent/present clock and DMA device-tree properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/udc-xilinx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/usbstring.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/usbstring.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/gadget/usbstring.c` provides shared USB gadget helpers for building string descriptors and validating USB language IDs. Gadget drivers use it when answering GET_DESCRIPTOR requests for string descriptor zero and string IDs in a language-specific table. The source was read as a complete 91-line file.

## Important APIs, Types, and Functions

The exported APIs are `usb_gadget_get_string()` and `usb_validate_langid()`. `usb_gadget_get_string()` consumes a `struct usb_gadget_strings` table and a string ID, emits a USB string descriptor into a caller-supplied `u8` buffer, and converts UTF-8 strings to UTF-16LE using `utf8s_to_utf16s()`. `usb_validate_langid()` checks the primary and sublanguage fields in a USB language identifier.

## Control Flow

ID zero is handled specially: the function emits the four-byte language descriptor containing `table->language`. Nonzero IDs are found by linear scan through `table->strings` until a matching `struct usb_string.id` or terminating null string. Missing IDs return `-EINVAL`. Found strings are length-capped to `USB_MAX_STRING_LEN`, converted to UTF-16LE at `buf[2]`, then descriptor length and type are written at bytes zero and one. Language validation rejects reserved primary-language ranges and zero sublanguage values.

## State and Persistence Behavior

The file owns no persistent state. It reads immutable caller-provided string tables and writes only the output descriptor buffer for the current request.

## Dependencies and Integration Points

It depends on kernel NLS conversion helpers, USB Chapter 9 descriptor constants, and `linux/usb/gadget.h` table types. The symbols are exported GPL for gadget drivers and composite functions that implement EP0 string descriptor handling.

## Risks and Edge Cases

The output buffer must be at least 256 bytes and 16-bit aligned as documented; the helper casts `&buf[2]` to `wchar_t *`. Invalid UTF-8 conversion is normalized to `-EINVAL`, which normally stalls the control request. The function trusts `table` and `table->strings` to be valid. `strlen()` plus `USB_MAX_STRING_LEN` caps source bytes, not user-visible characters, before conversion.

## Test Signals

Tests should cover descriptor zero, known and unknown string IDs, maximum-length strings, multi-byte UTF-8 conversion, invalid UTF-8, multiple language tables in gadget setup code, valid common language IDs such as `0x0409`, and rejected primary/sublanguage combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/usbstring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/usb/host/Kconfig

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/host/Kconfig` defines the kernel configuration surface for USB host-controller drivers. It gates xHCI, EHCI, OHCI, UHCI, platform-specific glue, SPI/PCMCIA/SoC controllers, debug/test features, and virtualized Xen USB host support. The source was read as a complete 728-line file.

## Important APIs, Types, and Functions

This is Kconfig metadata rather than C code. Important symbols include `USB_XHCI_HCD`, `USB_XHCI_PLATFORM`, `USB_XHCI_*` SoC options, `USB_EHCI_HCD`, `USB_EHCI_ROOT_HUB_TT`, `USB_EHCI_TT_NEWSCHED`, `USB_EHCI_FSL`, `USB_EHCI_EXYNOS`, `USB_EHCI_HCD_AT91`, `USB_EHCI_HCD_PLATFORM`, `USB_BRCMSTB`, `USB_OHCI_HCD`, `USB_UHCI_HCD`, `USB_HCD_BCMA`, `USB_HCD_SSB`, `USB_HCD_TEST_MODE`, and individual non-EHCI host controllers. Dependencies and selects encode architecture, bus, PHY, DMA, I/O-memory, and companion-controller relationships.

## Control Flow

Menu flow is declarative. Top-level options expose host-controller families. Nested `if USB_XHCI_HCD`, `if USB_EHCI_HCD`, and `if USB_OHCI_HCD` blocks reveal family-specific platform drivers only when the family core is enabled. `select` statements pull in required common platform HCDs, root-hub TT support, generic PHY, firmware loader, or companion-controller glue. Deprecated symbols remain as compatibility prompts and redirect users to replacement drivers.

## State and Persistence Behavior

Kconfig selections persist in `.config` and determine which objects are compiled, built as modules, or omitted. No runtime state is stored here, but bad dependency/select relationships can create invalid builds or missing runtime drivers.

## Dependencies and Integration Points

The file integrates with `drivers/usb/host/Makefile`, architecture symbols, bus support (`USB_PCI`, `BCMA`, `SSB`, `SPI`, `PCMCIA`, `XEN`), PHY/reset frameworks, and common USB core options. It also documents module names and user-facing hardware support descriptions.

## Risks and Edge Cases

Incorrect dependencies can expose drivers on architectures without required MMIO/DMA/IOPORT/PHY support. Missing `select` links can build platform wrappers without their generic HCD backend. Overly broad `default y` values can unexpectedly increase kernel footprint on matching SoCs. Deprecated entries must continue to avoid selecting removed code. Typos in help text mention OCHI instead of OHCI in BCMA/SSB descriptions but do not affect builds.

## Test Signals

Validation should include `allmodconfig`, `allyesconfig`, `randconfig`, and architecture-focused configs for ARM, MIPS, PowerPC, SPARC/LEON, x86 PCI, and COMPILE_TEST. Confirm that enabled Kconfig symbols produce the expected Makefile objects and module names, and that deprecated options do not reference removed object files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/Makefile -->
# sources/distributed-fs/ceph-client/drivers/usb/host/Makefile

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/host/Makefile` maps USB host-controller Kconfig symbols to built objects and composite module object lists. It is the build-side companion for the host `Kconfig`. The source was read as a complete 90-line file.

## Important APIs, Types, and Functions

Key composite object lists are `fhci-y`, `xhci-hcd-y`, `xhci-mtk-hcd-y`, `xhci-plat-hcd-y`, and `xhci-rcar-hcd-y`. Important object mappings include `obj-$(CONFIG_USB_EHCI_HCD) += ehci-hcd.o`, EHCI platform drivers such as `ehci-pci.o`, `ehci-platform.o`, `ehci-exynos.o`, `ehci-atmel.o`, `ehci-brcm.o`, Freescale `fsl-mph-dr-of.o` plus `ehci-fsl.o`, OHCI/UHCI/FHCI/xHCI families, BCMA/SSB bridge drivers, and smaller host controllers such as `max3421-hcd.o` and `xen-hcd.o`.

## Control Flow

Kbuild expands object lists according to the final `.config`. Some modules are composite, for example `xhci-hcd.o` is built from xHCI core, ring, hub, debug, trace, optional debug capability, debugfs, and sideband pieces. Platform wrappers are added only when their config symbol is enabled. Freescale EHCI pulls in both common Freescale DR glue and the EHCI-specific object.

## State and Persistence Behavior

The file has no runtime state. Its output is the compiled object/module graph, which persists as build artifacts and determines driver registration availability.

## Dependencies and Integration Points

It integrates with Kconfig symbols, generated trace include paths through `CFLAGS_xhci-trace.o := -I$(src)`, and Linux Kbuild composite-object conventions. Every source file in this work item except `Kconfig` itself is either directly mapped here or included into `ehci-hcd.c`.

## Risks and Edge Cases

Kconfig/Makefile drift can silently omit a driver or build an object without its required core. Optional fragments guarded by `ifneq ($(CONFIG_*),)` must match bool/tristate expectations. Composite xHCI additions can change module dependencies and link order. Freescale double mapping is intentional; removing one object can break OF/platform data setup.

## Test Signals

Build `drivers/usb/host/` under representative configs and confirm expected `.o` and `.ko` outputs. Use `make M=drivers/usb/host` with EHCI, OHCI, xHCI, BCMA, SSB, Freescale, Exynos, Atmel, Broadcom STB, and debugfs/test-mode permutations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/bcma-hcd.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/bcma-hcd.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/host/bcma-hcd.c` is Broadcom BCMA bus glue for USB host cores. It initializes Broadcom USB20/USB30 cores, applies chip-specific register sequences, controls optional VCC GPIO, and creates child platform devices for generic EHCI/OHCI or OF-populated child controllers. The source was read as a complete 499-line file.

## Important APIs, Types, and Functions

`struct bcma_hcd_device` stores the BCMA core, created EHCI/OHCI platform devices, and optional VCC GPIO. Key helpers are `bcma_wait_bits()`, `bcma_hcd_4716wa()`, `bcma_hcd_init_chip_mips()`, `bcma_hcd_usb20_old_arm_init()`, `bcma_hcd_usb20_ns_init()`, `bcma_hcd_usb20_ns_init_hc()`, `bcma_hcd_usb30_init()`, `bcma_hcd_create_pdev()`, and `bcma_hci_platform_power_gpio()`. Driver entry points are `bcma_hcd_probe()`, `bcma_hcd_remove()`, `bcma_hcd_shutdown()`, and optional PM `bcma_hcd_suspend()/resume()`.

## Control Flow

Probe allocates per-core state, requests optional `"vcc"` GPIO high, and dispatches by BCMA core ID. Old USB20 host cores use either MIPS initialization that enables/reset cores and creates `ohci-platform`/`ehci-platform` devices, or ARM initialization that sequences PMU PLL/PHY registers and populates OF children. Northstar USB20 enables the core, applies host-controller threshold/break-transfer tuning on specific chips, and populates OF children. Northstar USB30 enables the core and populates OF children. Remove unregisters created child platform devices and disables the core; shutdown and PM additionally toggle VCC low/high.

## State and Persistence Behavior

Runtime state is per-core and devm-managed. Persistent effects are BCMA core enable/disable state, Broadcom PHY/PLL/control registers, child platform devices registered into the device model, and GPIO output level. No file-backed state is used.

## Dependencies and Integration Points

The driver depends on the BCMA bus API, Broadcom chip IDs, optional MIPS/ARM code paths, GPIO descriptors, platform device registration, OF child population, and generic `ehci-platform`/`ohci-platform` pdata. Kconfig selects generic platform HCD support when the corresponding EHCI/OHCI core is enabled.

## Risks and Edge Cases

The initialization sequences use hard-coded Broadcom registers and timing delays; applying the wrong path to a chip revision can leave PHYs or PLLs unusable. MIPS-specific 4716 workaround depends on CPU clock thresholds. Child platform devices share the BCMA IRQ and fixed resource windows, so address/IRQ errors surface later in the generic HCD. ARM old-core init requires PMU discovery. PM resume only re-enables the core/GPIO and does not replay all USB20 register tuning.

## Test Signals

Test on BCMA USB20 old MIPS, old ARM, Northstar USB20, and Northstar USB30 systems. Check child HCD creation/removal, VCC GPIO polarity, suspend/resume/shutdown power behavior, DMA mask setup, OF child population, controller enumeration, and logs for timeout messages from PLL/MDIO waits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/bcma-hcd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-atmel.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-atmel.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/host/ehci-atmel.c` is the Atmel/AT91 platform wrapper for the common EHCI host controller core. It wires clocks, MMIO, IRQ, HSIC mode setup, suspend/resume, and platform-driver registration around `ehci_init_driver()`. The source was read as a complete 251-line file.

## Important APIs, Types, and Functions

`struct atmel_ehci_priv` holds interface and USB clocks plus a `clocked` flag in EHCI private storage. Important functions are `atmel_start_clock()`, `atmel_stop_clock()`, `atmel_start_ehci()`, `atmel_stop_ehci()`, `ehci_atmel_drv_probe()`, `ehci_atmel_drv_remove()`, `ehci_atmel_drv_suspend()`, and `ehci_atmel_drv_resume()`. The driver uses `ehci_atmel_drv_overrides.extra_priv_size` and registers `ehci_atmel_driver`.

## Control Flow

Module init initializes a copy of the generic EHCI `hc_driver` and registers the platform driver. Probe checks `usb_disabled()`, gets IRQ, coerces 32-bit DMA mask, creates the HCD, maps MMIO, obtains `ehci_clk` and `usb_clk`, sets `ehci->caps` to the mapped base, enables both clocks, calls `usb_add_hcd()`, enables wakeup, and, when DT PHY mode is HSIC, writes the HSIC enable bit to instruction register 8. Remove removes the HCD, releases it, and stops clocks. PM suspend calls `ehci_suspend()` then stops clocks; resume starts clocks and calls `ehci_resume()`.

## State and Persistence Behavior

State is limited to the HCD, the two clocks, and the `clocked` boolean. Hardware register state is initialized by the common EHCI setup and one optional HSIC instruction-register write. No persistent storage exists.

## Dependencies and Integration Points

The wrapper depends on platform resources, OF matching `atmel,at91sam9g45-ehci`, clock framework names `ehci_clk` and `usb_clk`, `of_usb_get_phy_mode()`, and the common EHCI core. It exposes standard USB host behavior through `usb_add_hcd()`.

## Risks and Edge Cases

Clock enable errors are not individually unwound inside `atmel_start_clock()`, so failed clock preparation could leave asymmetric state. HSIC mode is configured only after `usb_add_hcd()`, so regressions could appear if the core expects that bit earlier. Suspend/resume assumes clocks and EHCI state remain coherent across system sleep.

## Test Signals

Build with `USB_EHCI_HCD_AT91`, probe an AT91 EHCI node with both clocks, exercise HSIC and non-HSIC DT modes, run high-speed enumeration and transfers, and verify suspend/resume with wakeup-enabled root hub.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-atmel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-brcm.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-brcm.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/host/ehci-brcm.c` is the Broadcom STB EHCI platform wrapper. It provides clock/resource setup, big-endian MMIO reset handling, Broadcom instruction-register workarounds, and a hub-control override that aligns resume completion to a microframe boundary. The source was read as a complete 281-line file.

## Important APIs, Types, and Functions

`struct brcm_priv` stores the optional clock. Key functions are `ehci_brcm_wait_for_sof()`, `ehci_brcm_hub_control()`, `ehci_brcm_reset()`, `ehci_brcm_probe()`, `ehci_brcm_remove()`, `ehci_brcm_suspend()`, and `ehci_brcm_resume()`. `brcm_overrides` replaces the generic reset routine and extends private storage; probe also assigns `ehci_brcm_hc_driver.hub_control`.

## Control Flow

Probe sets a 32-bit DMA mask, gets the IRQ, creates an HCD from the Broadcom-customized EHCI driver, enables an optional clock, maps MMIO, and calls `usb_add_hcd()`. Reset marks MMIO big-endian, derives operational register base from capabilities, issues a controller reset to avoid reboot lockups, writes two Broadcom instruction registers to avoid OUT underflows, and then calls common `ehci_setup()`. Hub control intercepts `GetPortStatus` when clearing a resume bit; it disables local IRQs, waits for the next SOF and an extra delay, then delegates to `ehci_hub_control()`. Suspend delegates to `ehci_suspend()` and gates the clock; resume ungates the clock, reapplies instruction-register tuning, calls `ehci_resume()`, and resets runtime-PM bookkeeping.

## State and Persistence Behavior

Persistent runtime state is the HCD and optional clock. Hardware-visible state includes big-endian register access, instruction-register tuning, and normal EHCI schedules/root hub state. No file-backed state exists.

## Dependencies and Integration Points

The driver matches `brcm,ehci-brcm-v2` and `brcm,bcm7445-ehci`, depends on the clock framework, platform resources, and common EHCI core. It integrates with the USB hub layer through the overridden `hub_control` path.

## Risks and Edge Cases

The SOF workaround runs with local IRQs disabled and uses atomic polling; excessive delay would affect interrupt latency. The hub-control override must remain compatible with generic EHCI hub semantics. Broadcom instruction-register magic values are hardware-specific and must be restored after resume. Big-endian MMIO assumptions are central to reset correctness.

## Test Signals

Validate resume from suspended ports near microframe boundaries, reboot/shutdown without controller lockup, high-memory bus-load OUT transfers, suspend/resume clock gating, and enumeration on both compatible strings. Dynamic debug logs should show SOF workaround only on matching resume-completion cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-brcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-dbg.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-dbg.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/host/ehci-dbg.c` is included by `ehci-hcd.c` and provides EHCI dynamic-debug formatting plus optional debugfs snapshots of controller state. It is troubleshooting infrastructure for queue heads, transfer descriptors, bandwidth tables, periodic schedules, registers, and root-hub state. The source was read as a complete 1081-line file.

## Important APIs, Types, and Functions

When `CONFIG_DYNAMIC_DEBUG` is enabled, notable helpers include `dbg_hcs_params()`, `dbg_hcc_params()`, `dbg_qtd()`, `dbg_qh()`, `dbg_itd()`, `dbg_sitd()`, `dbg_status_buf()`, `dbg_intr_buf()`, `dbg_command_buf()`, `dbg_port_buf()`, `dbg_status()`, `dbg_cmd()`, and `dbg_port()`. Debugfs support uses `struct debug_buffer`, file operations for `async`, `bandwidth`, `periodic`, and `registers`, and fill functions `fill_async_buffer()`, `fill_bandwidth_buffer()`, `fill_periodic_buffer()`, and `fill_registers_buffer()`. `create_debug_files()` and `remove_debug_files()` are called from EHCI start/stop. Without dynamic debug, the file compiles to inline no-op stubs.

## Control Flow

EHCI setup and runtime code call debug formatting helpers directly for logging. On controller start, `create_debug_files()` creates a per-bus debugfs directory under the global EHCI debug root and four read-only files. Opening a debug file allocates a `debug_buffer`; the first read lazily vmallocs output space, calls the selected fill routine under a mutex, and serves data through `simple_read_from_buffer()`. Fill routines take EHCI locks while walking live schedules or reading registers, then render a bounded snapshot.

## State and Persistence Behavior

The only owned state is transient debugfs dentries and per-open `debug_buffer` allocations. Debug output is a snapshot and not persisted. It reads live EHCI schedule state, register values, bandwidth accounting, and TT lists without modifying controller behavior.

## Dependencies and Integration Points

The file depends on internal EHCI structures from `ehci.h`, debugfs, dynamic debug, USB bus/HCD conversion helpers, PCI config access for extended capability reporting, and schedule structures owned by `ehci-q.c` and `ehci-sched.c`. It is not a standalone compilation unit; it is part of `ehci-hcd.c`.

## Risks and Edge Cases

Schedule snapshots race with hardware and software changes, so output is diagnostic rather than authoritative. Buffer sizes are bounded; long periodic or TT lists can be truncated. Some helpers return zero or no-op when dynamic debug is disabled, so tests must cover both build modes. Register dumping avoids MMIO access when `HCD_HW_ACCESSIBLE` is false, which is important during suspend.

## Test Signals

Build with and without `CONFIG_DYNAMIC_DEBUG` and debugfs. On a running EHCI controller, verify `/sys/kernel/debug/usb/ehci/<bus>/{async,bandwidth,periodic,registers}` opens, reads, truncates safely, closes without leaks, and reports suspended controllers without MMIO access. Exercise active bulk, interrupt, and isochronous transfers to populate schedule dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-dbg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-exynos.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-exynos.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/host/ehci-exynos.c` is the Samsung S5P/Exynos EHCI platform wrapper. It manages Exynos USB host clock, PHYs, optional VBUS GPIO, DMA-burst tuning, legacy PHY binding quirks, and system PM around the generic EHCI core. The source was read as a complete 323-line file.

## Important APIs, Types, and Functions

`struct exynos_ehci_hcd` stores the USB host clock, saved OF node, up to three PHY handles, and a `legacy_phy` flag. Important functions are `exynos_ehci_get_phy()`, `exynos_ehci_phy_enable()`, `exynos_ehci_phy_disable()`, `exynos_setup_vbus_gpio()`, `exynos_ehci_probe()`, `exynos_ehci_remove()`, `exynos_ehci_suspend()`, and `exynos_ehci_resume()`. `exynos_overrides` extends EHCI private storage.

## Control Flow

Probe coerces a 32-bit DMA mask, requests optional `"samsung,vbus"` GPIO high, creates the HCD, obtains PHYs through modern `phys` phandles or legacy child-node bindings, enables the `usbhost` clock, maps resources, gets the IRQ, powers PHYs, sets `ehci->caps`, temporarily clears `pdev->dev.of_node` for legacy PHY children to avoid generic USB device binding conflicts, enables DMA burst in instruction register 0, and calls `usb_add_hcd()`. Remove restores the OF node, removes the HCD, powers off PHYs, and releases the HCD. PM suspend calls `ehci_suspend()`, powers off PHYs, and disables the clock; resume reverses that and reapplies DMA burst tuning before `ehci_resume()`.

## State and Persistence Behavior

Runtime state is the HCD private Exynos structure, PHY power state, optional VBUS GPIO state, clock enable state, saved OF node pointer, and hardware DMA-burst register. No file-backed state is used.

## Dependencies and Integration Points

The driver depends on platform resources, OF matching `samsung,exynos4210-ehci`, generic PHY framework, clock framework, GPIO descriptors, and the common EHCI core. It bridges both modern and legacy Exynos PHY descriptions.

## Risks and Edge Cases

`exynos_ehci_get_phy()` counts `phys` phandles without bounding `num_phys` against `PHY_NUMBER`, so malformed DT with more than three PHYs risks array overrun. Legacy OF-node clearing is a fragile integration workaround and must be restored on every failure/remove path. PHY power-on rollback must match partial successes. DMA-burst tuning must be reprogrammed after resume.

## Test Signals

Test modern and legacy DT PHY bindings, absent optional VBUS GPIO, suspend/resume, PHY power-on failure rollback, high-speed transfer throughput with DMA burst enabled, and module remove after failed and successful probes. Static analysis should flag PHY array bounds if DT input is not constrained elsewhere.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-exynos.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-fsl.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-fsl.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/host/ehci-fsl.c` is the Freescale/NXP SoC EHCI host wrapper for ARC-derived USB controllers. It consumes Freescale platform data, validates host/OTG modes, configures PHY/interface registers, handles several Freescale errata, sets cache snooping and arbitration registers, integrates optional OTG host registration, and implements SoC-specific PM restore paths. The source was read as a complete 732-line file.

## Important APIs, Types, and Functions

Important functions include `fsl_ehci_drv_probe()`, `usb_phy_clk_valid()`, `ehci_fsl_setup_phy()`, `ehci_fsl_usb_setup()`, `ehci_fsl_reinit()`, `ehci_fsl_setup()`, PM helpers `ehci_fsl_mpc512x_drv_suspend()/resume()`, `ehci_fsl_drv_suspend()/resume()/restore()`, optional OTG `ehci_start_port_reset()`, and `fsl_ehci_drv_remove()`. `struct ehci_fsl_priv` stores USB control register state across deep sleep. The driver uses `struct fsl_usb2_platform_data` extensively for mode, PHY, endian, controller version, errata flags, power budget, init/exit callbacks, and saved PM registers.

## Control Flow

Probe requires platform data and host-capable operating mode, obtains IRQ, creates the HCD under the parent device, maps registers, stores mapped registers in platform data, runs platform-specific `init()`, applies pre-reset controller enables and erratum A007792 setup, and calls `usb_add_hcd()`. In OTG mode it obtains a USB2 PHY and registers the EHCI root hub as OTG host. The EHCI reset override `ehci_fsl_setup()` sets endian flags, points EHCI caps at offset `0x100`, marks integrated root-hub TT, runs common `ehci_setup()`, applies MPC5121 SBUSCFG tuning, and then `ehci_fsl_reinit()` configures Freescale non-EHCI registers and PHYs.

`ehci_fsl_setup_phy()` programs ULPI, serial, UTMI, UTMI-wide, or dual UTMI port settings, checks PHY clock validity on supported controller versions, handles erratum A006918 by refusing initialization, and enables the USB controller bit. `ehci_fsl_usb_setup()` configures snooping, priority/age/SI control registers, root-hub TT and errata flags, and per-port PHYs for DR, OTG, or MPH host modes. PM suspend/resume uses generic EHCI port preparation for most SoCs, saves/restores `FSL_SOC_USB_CTRL` for deep sleep, and has a special MPC512x path that saves EHCI operational registers, cuts port power, restores USBMODE/SBUSCFG/registers, and resumes the root hub.

## State and Persistence Behavior

Runtime state spans HCD/EHCI state, Freescale platform data, non-EHCI SoC control registers, PHY mode selection, errata flags, OTG PHY host attachment, and PM-saved register snapshots. No file-backed persistence exists. Deep sleep can lose hardware register state; this file explicitly restores PHY/control state and marks the root hub as lost power when needed.

## Dependencies and Integration Points

The file depends on `linux/fsl_devices.h`, Freescale USB platform data, optional `CONFIG_USB_OTG`, optional `CONFIG_PPC_MPC512x`, OF compatibility checks on the parent node, the common EHCI core, and register constants from `ehci-fsl.h`. It integrates with board/platform code through `pdata->init`, `pdata->exit`, power budget, and errata fields.

## Risks and Edge Cases

Missing or wrong platform data prevents probe. PHY setup is highly version- and erratum-sensitive; incorrect flags can either refuse valid hardware or initialize unsafe hardware. Several registers are big-endian non-EHCI registers while EHCI registers follow configured endian flags; mixing accessors can break hardware. OTG error paths after `usb_add_hcd()` jump to cleanup that may not fully remove the added HCD before `usb_put_hcd()`, so host/OTG probe failures need scrutiny. PM paths differ sharply for MPC512x, deep sleep, and ordinary suspend; incomplete restore can lose root-hub or PHY state.

## Test Signals

Test DR_HOST, MPH_HOST, and DR_OTG modes with ULPI, serial, UTMI, UTMI-wide, and dual UTMI PHY settings; all Freescale errata flags; big- and little-endian MMIO/descriptor combinations; deep sleep restore; MPC5121 suspend/resume; OTG HNP start-port-reset; overcurrent port-power cycling; and high-speed/full-speed devices through integrated TT. Build coverage should include PowerPC and COMPILE_TEST-style configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-fsl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-fsl.h -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-fsl.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/host/ehci-fsl.h` defines Freescale/NXP SoC USB register offsets, bit masks, and timing constants used by `ehci-fsl.c`. The source was read as a complete 56-line file.

## Important APIs, Types, and Functions

The header has no functions or types. Important constants cover non-EHCI register offsets such as `FSL_SOC_USB_SBUSCFG`, `FSL_SOC_USB_PORTSC1/2`, `FSL_SOC_USB_USBMODE`, `FSL_SOC_USB_USBGENCTRL`, `FSL_SOC_USB_ISIPHYCTRL`, snoop/priority/SI/control registers, PHY/interface bits such as `PORT_PTS_UTMI`, `PORT_PTS_ULPI`, `PORT_PTS_SERIAL`, `PORT_PTS_PTW`, `USBMODE_CM_HOST`, `USBMODE_ES`, `CTRL_UTMI_PHY_EN`, `USB_CTRL_USB_EN`, `ULPI_PHY_CLK_SEL`, `PHY_CLK_VALID`, and `UTMI_PHY_CLK_VALID_CHK_RETRY`.

## Control Flow

There is no executable control flow. The constants parameterize probe, PHY setup, EHCI reset override, and PM restore code in `ehci-fsl.c`.

## State and Persistence Behavior

The header owns no state. Its values describe hardware-visible register state controlled by the Freescale EHCI wrapper.

## Dependencies and Integration Points

It is included by `ehci-fsl.c` and must match the Freescale SoC USB controller register map and platform data semantics from `linux/fsl_devices.h`.

## Risks and Edge Cases

Incorrect bit masks can corrupt SoC control registers, especially write-one-to-clear fields guarded by `CONTROL_REGISTER_W1C_MASK` and big-endian non-EHCI registers. The constants mix standard EHCI-adjacent port fields with Freescale-specific control registers, so changes require hardware documentation review.

## Test Signals

Compile coverage through `ehci-fsl.c`, register write/read traces on Freescale hardware, PHY-mode validation for ULPI/UTMI/serial modes, and suspend/resume register restore checks are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-fsl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-grlib.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-grlib.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/host/ehci-grlib.c` is the Aeroflex Gaisler GRLIB GRUSBHC EHCI platform driver, typically used on LEON/GRLIB SoCs. It provides a static EHCI `hc_driver`, OF resource/IRQ mapping, endian detection, and platform-driver glue. The source was read as a complete 177-line file.

## Important APIs, Types, and Functions

The central object is `ehci_grlib_hc_driver`, a full `struct hc_driver` table pointing at common EHCI callbacks such as `ehci_irq`, `ehci_setup`, `ehci_run`, `ehci_stop`, `ehci_shutdown`, `ehci_urb_enqueue()`, `ehci_hub_control()`, and PM bus callbacks. Driver entry points are `ehci_hcd_grlib_probe()` and `ehci_hcd_grlib_remove()`, with OF matches by name `GAISLER_EHCI` and `01_026`.

## Control Flow

Probe rejects disabled USB, converts OF address to a resource, forces a DMA mask pointer for `usb_create_hcd()`, creates the HCD, parses and maps IRQ, maps MMIO, sets `ehci->caps`, reads `hc_capbase`, and if the version is not the known GRUSBHC value `0x0100`, enables big-endian MMIO, descriptor, and capbase handling. It then calls `usb_add_hcd()` and enables device wakeup. Remove removes the HCD, disposes the IRQ mapping, and releases the HCD.

## State and Persistence Behavior

State is the HCD/EHCI instance, mapped IRQ, mapped MMIO, and endian flags. No persistent storage exists.

## Dependencies and Integration Points

The file depends on OF address/IRQ helpers, platform devices, and common EHCI functions supplied because it is included into `ehci-hcd.c` for SPARC LEON builds. It integrates with LEON/GRLIB device-tree style matching by OF node name.

## Risks and Edge Cases

Endian detection assumes `HCIVERSION == 0x0100` identifies one byte order and any other value means big-endian operation. IRQ mapping returns zero on failure and must be disposed on later errors. The file is conditionally included by `ehci-hcd.c`, so standalone build assumptions are invalid.

## Test Signals

Test on LEON/GRLIB hardware or emulation for both detected endian paths, OF resource/IRQ failure paths, HCD add/remove, root-hub enumeration, and wakeup-capable suspend/resume when PM is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-grlib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-hcd.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-hcd.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/host/ehci-hcd.c` is the common Linux EHCI USB 2.0 host-controller implementation. It owns the generic `hc_driver` callbacks, controller reset/start/stop/shutdown, interrupt handling, URB dispatch, endpoint teardown/reset, PM helpers, module parameters, and initialization of platform driver variants that are compiled into the core. It includes `ehci-dbg.c`, `ehci-hub.c`, `ehci-mem.c`, `ehci-q.c`, `ehci-sched.c`, timer and sysfs code. The source was read as a complete 1401-line file.

## Important APIs, Types, and Functions

Important exported or shared functions include `ehci_handshake()`, `ehci_reset()`, `ehci_setup()`, `ehci_suspend()`, `ehci_resume()`, and `ehci_init_driver()`. Core lifecycle functions are `ehci_halt()`, `tdi_reset()`, `ehci_quiesce()`, `ehci_turn_off_all_ports()`, `ehci_silence_controller()`, `ehci_shutdown()`, `ehci_stop()`, `ehci_init()`, and `ehci_run()`. Runtime callbacks include `ehci_irq()`, `ehci_work()`, `ehci_urb_enqueue()`, `ehci_urb_dequeue()`, `ehci_endpoint_disable()`, `ehci_endpoint_reset()`, `ehci_get_frame()`, and `ehci_remove_device()`. Module parameters are `log2_irq_thresh`, `park`, and `ignore_oc`.

## Control Flow

`ehci_setup()` derives operational registers from capability length, caches structural parameters, initializes memory/schedule state, halts the controller, and resets it. `ehci_init()` initializes locks, hrtimer state, lists, periodic schedule size, DMA pools, async queue head, interrupt threshold, optional park mode, per-port-change support, scatter-gather capacity, and unlink bookkeeping. `ehci_run()` programs the periodic frame list and async head, configures 64-bit segment if advertised, starts `CMD_RUN`, sets the configured flag under the port-reset rwsem, waits for hardware running state, enables interrupts, and creates debugfs/sysfs files.

At runtime, URB enqueue builds qTD/QH transactions for control/bulk/interrupt, schedules interrupt QHs, or submits high-speed/full-speed isochronous transfers through ITD/SITD paths. The IRQ handler acknowledges status, handles normal/error completions by running `ehci_work()`, completes IAA unlink cycles, starts remote-wakeup port resume timers, polls root hub status for port changes, and handles fatal/controller-dead cases by stopping schedules and disabling interrupts. Stop/shutdown quiesce schedules, power off ports, clear configured flag, cancel timers, remove diagnostics, free ITDs, and clean DMA memory.

## State and Persistence Behavior

EHCI state is in `struct ehci_hcd`: command shadow, root-hub state, async/periodic schedules, DMA pools, timers, unlink lists, bandwidth tables, TT list, port bitmaps, reset timers, flags for hardware quirks, and debug/sysfs state. Hardware-visible state includes operational registers, frame list base, async head, configured flag, interrupt enables, port status, and endpoint schedule descriptors in coherent DMA memory. There is no file-backed persistence; resume can preserve hardware power or reset and mark root hub power lost.

## Dependencies and Integration Points

The file depends on the USB HCD core, PCI/platform support, DMA pools/coherent memory, debugfs, timers, OTG hooks, and `ehci.h` internal types. Platform wrappers copy `ehci_hc_driver` through `ehci_init_driver()` and override reset/port-power behavior or add private storage. It integrates with USB hub code via included `ehci-hub.c` and with transfer scheduling via included queue/scheduler code.

## Risks and Edge Cases

Controller lifecycle has many timing-sensitive handshakes; timeouts or all-ones reads indicate hardware removal or failure. The IRQ handler must avoid lost edge interrupts and controller-death races. QH unlink and completion can race with endpoint disable/dequeue and use guarded state transitions. Root-hub and companion-controller handover are sensitive to full/low-speed devices, integrated TT, and port-owner bits. Module parameters can change performance and overcurrent handling. PM resume must distinguish preserved power from hibernation/firmware takeover and can require full reset.

## Test Signals

Signals include successful high-speed enumeration, control/bulk/interrupt/isochronous URB traffic, unlink/dequeue stress, endpoint clear-halt, root-hub reset/suspend/resume, companion-controller handover for USB 1.1 devices, overcurrent handling with and without `ignore_oc`, fatal error handling, module load/unload, hibernation/system suspend, platform override behavior, and debugfs/sysfs creation/removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-hcd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-hub.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-hub.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/host/ehci-hub.c` is included by `ehci-hcd.c` and implements EHCI root-hub behavior: hub status bitmaps, hub descriptors, hub control requests, port reset/resume/suspend/power handling, companion-controller handover, wakeup flag adjustment, and bus suspend/resume. The source was read as a complete 1222-line file.

## Important APIs, Types, and Functions

Important functions include `ehci_adjust_port_wakeup_flags()` exported to platform code, `ehci_bus_suspend()`, `ehci_bus_resume()`, `ehci_get_resuming_ports()`, `set_owner()`, `check_reset_complete()`, `ehci_hub_status_data()`, `ehci_hub_descriptor()`, `ehci_hub_control()`, `ehci_relinquish_port()`, `ehci_port_handed_over()`, and `ehci_port_power()`. PM helpers include `ehci_handover_companion_ports()` and `persist_enabled_on_companion()`.

## Control Flow

The USB hub core calls `ehci_hub_status_data()` to build a change bitmap from STS_PCD/per-port-change bits, port-change bits, reset timers, suspend-change flags, and controller quirks. `ehci_hub_control()` handles standard hub requests: clearing port features, getting hub descriptors/status, getting port status with reset/resume completion, setting suspend/power/reset/test features, and erroring with `-EPIPE` for invalid requests. Reset is two-phase: SetPortFeature RESET starts the reset and sets `reset_done`; later GetPortStatus clears reset, handoffs low/full-speed ports to companions if needed, and reports change bits.

Bus suspend manually suspends each enabled port, tracks `bus_suspended` and `owned_ports`, programs wake bits, optionally enters TDI PHY low-power mode, halts the controller, cancels timers, and enables wake-capable interrupts. Bus resume reprograms frame-list and async pointers, restarts command, clears PHY low-power mode, resumes suspended ports for `USB_RESUME_TIMEOUT`, clears resume bits, hands companion-owned ports back, and re-enables interrupts.

## State and Persistence Behavior

State is stored in EHCI bitmaps and arrays such as `bus_suspended`, `owned_ports`, `suspended_ports`, `resuming_ports`, `port_c_suspend`, and `reset_done[]`, plus hardware port-status and hostpc registers. No file-backed persistence exists. Across power loss, companion ports may need reset/handover and the root hub may be marked lost power by outer PM code.

## Dependencies and Integration Points

The file depends on the USB hub core request model, EHCI register definitions, HCD timers/root-hub polling, optional OTG HNP, optional USB HCD test mode, companion controller ownership conventions, and platform quirks exposed through fields in `struct ehci_hcd`.

## Risks and Edge Cases

Port-state transitions are timing-sensitive and depend on callers issuing GetPortStatus after reset. Wakeup bits can cause false wakeups on some controllers. Companion handover must preserve persistent USB 1.1 devices but avoid delaying resume unnecessarily. Overcurrent behavior varies and may require power cycling or ignoring spurious signals. TDI PHY low-power mode requires lock drops and sleeps. Test mode deliberately halts/quiesces the controller.

## Test Signals

Test root-hub descriptor/status requests, per-port power control, reset completion, low/full-speed handoff to companions, integrated-TT ports, selective suspend/resume, remote wakeup, bus suspend/resume with persistent USB 1.1 devices, overcurrent reporting, `USB_HCD_TEST_MODE`, OTG HNP suspend clear, and controller quirks such as FSL suspend/high-speed errata and TDI PHY LPM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-hub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-mem.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-mem.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/host/ehci-mem.c` is included by `ehci-hcd.c` and owns EHCI schedule memory allocation and cleanup. It creates DMA pools for queue transfer descriptors, queue heads, high-speed isochronous descriptors, split isochronous descriptors, the coherent periodic frame list, and the software shadow table. The source was read as a complete 224-line file.

## Important APIs, Types, and Functions

Key helpers are `ehci_qtd_init()`, `ehci_qtd_alloc()`, `ehci_qtd_free()`, `ehci_qh_alloc()`, `qh_destroy()`, `ehci_mem_init()`, and `ehci_mem_cleanup()`. They allocate and initialize hardware-facing `struct ehci_qtd`, `struct ehci_qh_hw`, `struct ehci_itd`, and `struct ehci_sitd` storage with the alignment and 4 KiB boundary constraints required by EHCI hardware.

## Control Flow

`ehci_mem_init()` creates qTD and QH DMA pools, allocates the async QH and its dummy qTD, creates ITD and SITD pools, allocates the coherent periodic schedule, optionally creates a dummy QH for every periodic entry, initializes periodic entries to either the dummy QH or list-end markers, and allocates the software shadow table. Any failure jumps to cleanup and returns `-ENOMEM`. `ehci_mem_cleanup()` destroys async/dummy QHs, all DMA pools, the coherent periodic table, and the shadow table.

## State and Persistence Behavior

All state is in DMA-coherent memory, DMA pools, and kernel allocations tied to the HCD lifetime. It persists only while the EHCI controller instance is initialized. Hardware reads QHs, qTDs, ITDs, SITDs, and periodic entries directly from these allocations.

## Dependencies and Integration Points

The file depends on EHCI internal types, DMA pool APIs, coherent DMA allocation, endian conversion helpers, and `ehci_to_hcd(ehci)->self.sysdev`. Queue and scheduler files consume the allocation helpers for transfer submission.

## Risks and Edge Cases

EHCI descriptor alignment and 4 KiB crossing constraints are mandatory; changing pool sizes/alignments risks DMA hardware faults. `qh_destroy()` BUGs if a QH is still linked or has qTDs. `ehci_qh_alloc()` uses `GFP_ATOMIC` for the software QH regardless of supplied flags, which matches interrupt-context allocation expectations but can fail under pressure. Cleanup must remain in sync with every allocation added to init.

## Test Signals

Test memory-allocation failure injection at each allocation step, HCD probe/remove leak checks, DMA API debug, high-volume control/bulk/interrupt/isochronous submissions, dummy-QH periodic mode, and endpoint disable paths that destroy QHs only when unlinked and empty.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-mem.c -->
