# subset-b-005515 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-mtk.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/xhci-mtk.c

## Purpose
Implements the MediaTek platform glue for xHCI host controllers. It powers and resets the SSUSB host block, enables MediaTek IPPC U2/U3 ports, applies SoC timing/FIFO quirks, parses Devicetree wakeup and LPM properties, creates the USB2 and optional USB3 root HCDs, and wires MediaTek bandwidth-scheduler overrides into the generic xHCI core.

## Important APIs, Types, And Functions
Driver entry points are `xhci_mtk_probe()`, `xhci_mtk_remove()`, `xhci_mtk_suspend()`, `xhci_mtk_resume()`, runtime PM callbacks, `xhci_mtk_init()`, and `xhci_mtk_exit()`. The xHCI override table installs `xhci_mtk_setup()` plus scheduler hooks `xhci_mtk_add_ep()`, `xhci_mtk_drop_ep()`, `xhci_mtk_check_bandwidth()`, and `xhci_mtk_reset_bandwidth()` from the MediaTek scheduler implementation. Hardware helpers include `xhci_mtk_ssusb_config()`, `xhci_mtk_host_enable()`, `xhci_mtk_host_disable()`, `xhci_mtk_set_frame_interval()`, `xhci_mtk_rxfifo_depth_set()`, `usb_wakeup_of_property_parse()`, and `usb_wakeup_set()`.

## Control Flow
Probe allocates `struct xhci_hcd_mtk`, gets regulators and six optional clocks, parses IRQs and DT flags, enables runtime PM, regulators, clocks, and optional reset, maps `mac` and optional `ippc` resources, creates the primary HCD, sets MTK interrupt moderation, and calls `usb_add_hcd()`. During primary setup, `xhci_mtk_ssusb_config()` resets the SSUSB IP, powers down the device side, reads U2/U3 port counts, enables non-masked host ports, and polls clock/reset status before generic xHCI setup. If dual root hubs are needed, probe creates and adds a shared HCD. Suspend stops root-hub polling, powers down ports and host IP, disables clocks, and arms syscon wake; resume reverses that and restarts polling.

## State And Persistence
All state is volatile kernel memory plus MMIO/syscon state. `struct xhci_hcd_mtk` stores the primary HCD, IPPC base, port counts and disable masks, regulators, clocks, wakeup regmap/version/base, LPM flags, and RX FIFO depth. Runtime PM state, wake IRQ configuration, root-hub polling bits, and xHCI quirk flags are re-created on probe/resume; nothing is persisted to disk.

## Dependencies And Integration Points
Depends on platform devices, Devicetree, regmap/syscon wake registers, reset, regulator and clock bulk APIs, runtime PM, wake IRQ helpers, and the generic xHCI HCD. It integrates with `xhci-mtk.h` scheduler data and the external `xhci-mtk-sch.c` implementation for periodic bandwidth accounting.

## Risks And Test Signals
Risks include incorrect IPPC port masks, clocks not stabilizing, wake syscon version mismatches, PM races around root-hub polling, regulator/clock unwind leaks, and MT8195 timing workaround regressions. Test signals include probe/remove on DT variants, USB2/USB3 enumeration with masked ports, suspend/resume and runtime autosuspend with wakeup IRQs, stream capability on non-broken controllers, isochronous scheduling, RX FIFO workaround behavior, and lockdep/PM trace coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-mtk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-mtk.h -->
# sources/distributed-fs/ceph-client/drivers/usb/host/xhci-mtk.h

## Purpose
Defines the private MediaTek xHCI host data model shared by the platform glue and the MediaTek bandwidth scheduler. It also describes the SSUSB IPPC register layout used to power and configure U2/U3 host ports.

## Important APIs, Types, And Functions
Key constants are `BULK_CLKS_NUM`, `BULK_VREGS_NUM`, `XHCI_MTK_MAX_ESIT`, `XHCI_MTK_BW_INDEX()`, and port limits `MU3C_U3_PORT_MAX` and `MU3C_U2_PORT_MAX`. Important types are `struct mu3h_sch_tt`, `struct mu3h_sch_bw_info`, `struct mu3h_sch_ep_info`, `struct mu3c_ippc_regs`, and `struct xhci_hcd_mtk`. The header exposes `hcd_to_mtk()` plus scheduler entry points `xhci_mtk_sch_init()`, `xhci_mtk_sch_exit()`, `xhci_mtk_add_ep()`, `xhci_mtk_drop_ep()`, `xhci_mtk_check_bandwidth()`, and `xhci_mtk_reset_bandwidth()`.

## Control Flow
The header has no runtime execution, but it shapes the flow used by `xhci-mtk.c` and scheduler code: platform setup fills `struct xhci_hcd_mtk`, scheduler init creates bandwidth domains, endpoint add/drop hooks allocate or release `struct mu3h_sch_ep_info`, and bandwidth check/reset hooks commit or roll back periodic endpoint reservations.

## State And Persistence
State is runtime-only. TT arrays track FS/LS split bus bandwidth, `mu3h_sch_bw_info` tracks per-microframe bandwidth domains, and `mu3h_sch_ep_info` stores per-endpoint ESIT, offsets, packet counts, CS count, burst mode, and budget table. `struct xhci_hcd_mtk` persists while the controller is bound and owns the scheduler hash/list roots and platform resources.

## Dependencies And Integration Points
Depends on Linux clock, hashtable, regulator, USB HCD, and xHCI private types. It is a private compile-time contract between the MediaTek platform driver and MediaTek scheduling code, while `hcd_to_mtk()` uses driver data installed by platform probe.

## Risks And Test Signals
Risks are layout drift with `xhci-mtk.c`, incorrect MMIO register typing/offsets, ESIT truncation over-allocating bandwidth, and flexible-array budget sizing bugs. Test signals include compile coverage with MediaTek xHCI enabled, periodic endpoint admission tests, TT split scheduling for FS/LS devices behind HS hubs, masked U2/U3 port probing, and KASAN coverage for scheduler allocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-mtk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-mvebu.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/xhci-mvebu.c

## Purpose
Provides the Marvell MVEBU xHCI MBus initialization quirk used by the platform xHCI glue. It programs USB3 address-decode windows so the host controller can access DRAM chip-select regions.

## Important APIs, Types, And Functions
The exported function is `xhci_mvebu_mbus_init_quirk(struct usb_hcd *hcd)`. The internal `xhci_mvebu_mbus_config()` clears and programs up to `USB3_MAX_WINDOWS` windows using `struct mbus_dram_target_info` and `struct mbus_dram_window`. Register helpers are `USB3_WIN_CTRL(w)` and `USB3_WIN_BASE(w)`.

## Control Flow
The platform wrapper invokes the quirk during xHCI setup for Armada compatibles. The quirk obtains IORESOURCE_MEM index 1 from the platform device, temporarily maps it with `ioremap()`, fetches DRAM target metadata from `mv_mbus_dram_info()`, clears all USB3 decode windows, writes one enabled window for each DRAM CS, then unmaps the temporary region.

## State And Persistence
No Linux object state is retained. The only lasting effect is hardware register programming in the USB3 MBus window block until reset or later reprogramming. The temporary mapping exists only during the quirk call.

## Dependencies And Integration Points
Depends on platform resources, MMIO accessors, and the MVEBU MBus library. It is connected through `xhci-plat.c` via `struct xhci_plat_priv.init_quirk` for Armada 375/380-style xHCI instances.

## Risks And Test Signals
Risks include missing resource index 1, stale or incorrect DRAM CS metadata, programming more chip selects than the hardware window count, and failures on systems with unusual memory maps. Test signals include successful Armada xHCI probe, DMA transfers to memory in each DRAM chip select, no decode errors under high I/O load, and suspend/resume behavior if the MBus registers are reset by firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-mvebu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-mvebu.h -->
# sources/distributed-fs/ceph-client/drivers/usb/host/xhci-mvebu.h

## Purpose
Declares the optional MVEBU MBus initialization hook for platform xHCI drivers and provides a no-op stub when MVEBU xHCI support is not built.

## Important APIs, Types, And Functions
The only API is `xhci_mvebu_mbus_init_quirk(struct usb_hcd *hcd)`, guarded by `IS_ENABLED(CONFIG_USB_XHCI_MVEBU)`. `struct usb_hcd` is forward-declared to avoid pulling in USB HCD headers.

## Control Flow
There is no runtime flow in the enabled declaration path. In disabled builds, callers can still invoke the inline stub and receive success, allowing generic platform glue to compile and run without special preprocessor branches.

## State And Persistence
The header exposes no state. Whether MBus hardware state is programmed depends entirely on whether the C implementation is built and selected by platform match data.

## Dependencies And Integration Points
This private header is included by `xhci-plat.c` and `xhci-mvebu.c`. It decouples Armada-specific setup from the generic xHCI platform driver while keeping one callback signature in `struct xhci_plat_priv`.

## Risks And Test Signals
Risks are mostly configuration-related: a disabled or missing implementation silently turns the quirk into a no-op, which may leave DMA windows unprogrammed on affected SoCs. Test signals include build coverage with `CONFIG_USB_XHCI_MVEBU=y/m/n` and Armada runtime transfer tests proving the quirk was actually linked and called where required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-mvebu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-pci-renesas.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/xhci-pci-renesas.c

## Purpose
Implements a dedicated PCI driver for Renesas xHCI controllers that may require firmware loading before normal xHCI PCI probe. It handles firmware validation, download into volatile controller RAM, optional programming of an external ROM, and fallback to the shared xHCI PCI probe/remove implementation.

## Important APIs, Types, And Functions
The PCI entry point is `xhci_pci_renesas_probe()`, with removal delegated to `xhci_pci_remove()`. Firmware flow uses `renesas_xhci_check_request_fw()`, `renesas_fw_verify()`, `renesas_fw_check_running()`, `renesas_fw_download()`, `renesas_load_fw()`, `renesas_check_rom()`, `renesas_check_rom_state()`, `renesas_rom_erase()`, and `renesas_setup_rom()`. `renesas_fw_download_image()` writes alternating DATA0/DATA1 dwords and polls SET_DATA bits. The firmware name is `renesas_usb_fw.mem`.

## Control Flow
Probe first checks whether an external ROM exists and is already loaded. If not, it examines firmware download status bits to decide whether firmware is already running, blocked by a lock, stale, or absent. When firmware is needed, it requests the firmware image, verifies size/header/version-pointer bounds, then tries ROM programming if a ROM is present and falls back to RAM download otherwise. Only after firmware setup succeeds or a valid ROM fallback exists does it call `xhci_pci_common_probe()`.

## State And Persistence
State is mostly PCI configuration-space state in Renesas-specific registers. RAM firmware download is volatile and must be repeated after power loss. ROM erase/program/reload is persistent in the external ROM when successful. The Linux driver does not keep long-lived private state beyond normal PCI/xHCI objects created by common probe.

## Dependencies And Integration Points
Depends on PCI config accessors, firmware loader APIs, unaligned little-endian helpers, module firmware metadata, and exported functions from `xhci-pci.c` in the `xhci` namespace. It claims Renesas device IDs 0x0014 and 0x0015 so the generic PCI xHCI driver deliberately declines them when this driver is enabled.

## Risks And Test Signals
Risks include bricking or corrupting external ROM contents, timeout constants mismatching hardware behavior, endian mistakes in firmware dword writes, stale FW_DOWNLOAD_ENABLE states requiring power-cycle recovery, and missing firmware on systems without usable ROM. Test signals include cold boot with blank RAM firmware, boot with valid ROM, ROM programming success/failure fallback, missing firmware behavior, PCI config error injection, suspend/resume after power loss, and normal USB enumeration after `xhci_pci_common_probe()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-pci-renesas.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-pci.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/xhci-pci.c

## Purpose
Provides generic PCI bus glue for xHCI host controllers. It selects vendor/device quirks, initializes MSI/MSI-X or legacy interrupts, creates USB2 and optional USB3 root HCDs, handles PCI runtime/system PM, and exports common probe/remove helpers used by the Renesas firmware-loading driver.

## Important APIs, Types, And Functions
Public namespace exports are `xhci_pci_common_probe()` and `xhci_pci_remove()`. Core callbacks include `xhci_pci_setup()`, `xhci_pci_run()`, `xhci_pci_stop()`, `xhci_pci_suspend()`, `xhci_pci_resume()`, `xhci_pci_poweroff_late()`, and `xhci_pci_shutdown()`. Quirk and IRQ helpers include `xhci_pci_quirks()`, `xhci_try_enable_msi()`, `xhci_cleanup_msix()`, `xhci_msix_sync_irqs()`, `xhci_pme_quirk()`, `xhci_ssic_port_unused_quirk()`, `xhci_sparse_control_quirk()`, and ACPI LPM helpers.

## Control Flow
Module init initializes the generic `hc_driver` with PCI overrides and registers a class-matching PCI driver. Probe skips Renesas IDs when the dedicated Renesas driver is enabled, resets an optional reset controller, prevents runtime suspend during root-hub setup, invokes `usb_hcd_pci_probe()` for the USB2 HCD, creates and adds a shared HCD if needed, initializes xHCI extended capabilities, enables streams when supported, and adjusts runtime PM policy. Start enables MSI/MSI-X with fallback to legacy IRQ before `xhci_run()`. Suspend applies vendor PM quirks before `xhci_suspend()` and synchronizes MSI-X; resume resets optional reset control, performs Intel port switchover and PME quirks, then calls `xhci_resume()`.

## State And Persistence
State is runtime-only in `struct xhci_hcd`, `struct usb_hcd`, PCI device power/IRQ state, and quirk flags. PCI config and vendor MMIO PM tweaks persist only until device reset or power transition. The driver mutates runtime PM allow/forbid state and optional D3hot/D3cold policy but stores no filesystem data.

## Dependencies And Integration Points
Depends on PCI, ACPI, reset controls, USB HCD PCI helpers, generic xHCI setup/run/suspend/resume, tracepoints, AMD/Intel USB quirks, and the PM core. It integrates with `xhci-pci-renesas.c` through exported helpers and with usbcore through the HCD callback table.

## Risks And Test Signals
High-risk areas are vendor quirk matching, interrupt fallback and cleanup, dual-HCD lifetime, command/event behavior across PM transitions, D3cold policy, and shutdown wake quirks. Test signals include allmodconfig/randconfig builds, MSI-X/MSI/legacy IRQ operation, hotplug and remove, suspend/resume/runtime PM across Intel/AMD/ASMedia/VIA/Renesas hardware, Thunderbolt runtime PM, root hub LPM ACPI DSM handling, streams, and xHCI reset-on-resume paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-pci.h -->
# sources/distributed-fs/ceph-client/drivers/usb/host/xhci-pci.h

## Purpose
Declares the small shared interface between the generic xHCI PCI driver and the Renesas PCI firmware-loading wrapper.

## Important APIs, Types, And Functions
The header declares `xhci_pci_common_probe(struct pci_dev *dev, const struct pci_device_id *id)` and `xhci_pci_remove(struct pci_dev *dev)`. It relies on included context for `struct pci_dev` and `struct pci_device_id`.

## Control Flow
The header has no execution. It allows `xhci-pci-renesas.c` to perform Renesas firmware work, then enter the same common probe path as generic PCI xHCI, and to use the same remove callback.

## State And Persistence
No state is defined. Ownership and lifetime belong to the implementations in `xhci-pci.c` and the caller's PCI driver.

## Dependencies And Integration Points
This is a private compile-time boundary within the xHCI host directory. The implementation exports the functions in the `xhci` namespace, so module builds also depend on namespace import in the Renesas driver.

## Risks And Test Signals
Risks include declaration drift, missing PCI type declarations in include order, and namespace/export mismatches for modular builds. Test signals are successful builds with generic PCI xHCI alone and with `CONFIG_USB_XHCI_PCI_RENESAS`, plus module load/unload of both drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-plat.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/xhci-plat.c

## Purpose
Implements generic platform-device bus glue for xHCI controllers. It handles MMIO mapping, DMA mask setup, clocks, resets, optional USB PHYs, firmware/DT/ACPI quirk discovery, dual-root-hub creation, sideband-aware suspend, runtime PM, and exported probe/remove/PM hooks used by SoC-specific wrappers.

## Important APIs, Types, And Functions
Exported APIs are `xhci_plat_probe()`, `xhci_plat_remove()`, and `xhci_plat_pm_ops`. Internal callbacks include `xhci_plat_setup()`, `xhci_plat_start()`, `xhci_generic_plat_probe()`, `xhci_plat_suspend_common()`, `xhci_plat_resume_common()`, runtime PM callbacks, and quirk dispatchers `xhci_priv_init_quirk()`, `xhci_priv_suspend_quirk()`, `xhci_priv_resume_quirk()`, and `xhci_priv_post_resume_quirk()`. Match data uses `struct xhci_plat_priv`.

## Control Flow
Module init initializes the platform HCD driver and registers `xhci-hcd`. Probe chooses a firmware-visible `sysdev`, configures a 64-bit DMA mask, enables runtime PM, creates the primary HCD, maps resource 0, gets optional `reg` and core clocks plus shared reset array, deasserts reset, enables clocks, copies match-data quirks, parses parent-chain properties, initializes optional USB PHYs, adds the primary HCD, creates/adds a shared HCD when needed, enables streams, then forbids runtime PM by default. Suspend can skip work when an xHCI sideband instance is active; otherwise it calls private suspend quirks, `xhci_suspend()`, and optional clock gating. Resume re-enables clocks, runs private resume/post-resume hooks, calls `xhci_resume()`, and refreshes runtime PM state.

## State And Persistence
Runtime state lives in `struct xhci_hcd`, HCD private `struct xhci_plat_priv`, clocks, reset controls, USB PHY handles, runtime PM state, and quirk flags. The `sideband_at_suspend` and `power_lost` fields affect PM recovery but are not persistent beyond the bound device.

## Dependencies And Integration Points
Depends on platform bus, OF/ACPI properties, DMA mapping, clock/reset/USB PHY APIs, generic xHCI core, `xhci-mvebu.h`, and `xhci-sideband`. Renesas and other wrappers call its exported probe/remove/PM operations with custom `struct xhci_plat_priv`.

## Risks And Test Signals
Risks include incorrect `sysdev` selection for DMA, clock/reset unwind bugs, PHY ownership conflicts with DWC3, shared-HCD lifetime errors, sideband suspend mismatches, and parent-property quirks unexpectedly applying to child controllers. Test signals include generic OF and ACPI probing, DWC3 child platform cases, PCI-parent child cases, USB2/USB3 enumeration, suspend/resume/runtime PM with wake and no-wake, sideband active suspend, missing optional PHYs/clocks, and reset/clock failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-plat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-plat.h -->
# sources/distributed-fs/ceph-client/drivers/usb/host/xhci-plat.h

## Purpose
Defines the private platform xHCI extension structure and exported platform glue interfaces used by generic and SoC-specific xHCI platform drivers.

## Important APIs, Types, And Functions
`struct xhci_plat_priv` contains an optional firmware name, xHCI quirk bitmask, `power_lost`, `sideband_at_suspend`, and hook pointers for platform start, init, suspend, resume, and post-resume quirks. Helpers `hcd_to_xhci_priv()` and `xhci_to_priv()` cast the generic xHCI private area. Exported declarations are `xhci_plat_probe()`, `xhci_plat_remove()`, and `xhci_plat_pm_ops`.

## Control Flow
No code runs here. Match data in generic or SoC-specific drivers is copied into the HCD private area by `xhci_plat_probe()`, then the hooks are called during setup, start, suspend, resume, and post-resume paths.

## State And Persistence
The structure is runtime-only and stored in the extra private bytes requested by `xhci-plat.c` overrides. It persists for the lifetime of the HCD and carries platform-specific recovery decisions, but has no stable userspace or disk representation.

## Dependencies And Integration Points
The header is included by `xhci-plat.c`, `xhci-rcar.c`, and RZ helper code. It forms the callback contract that keeps SoC-specific register and firmware operations outside the generic platform wrapper.

## Risks And Test Signals
Risks include private-size mismatches, callbacks being called with uninitialized private data, and hook ordering assumptions across setup/start/PM. Test signals include builds of generic platform, Renesas R-Car/RZ, MVEBU, and Broadcom variants, plus PM tests that exercise every hook slot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-plat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-port.h -->
# sources/distributed-fs/ceph-client/drivers/usb/host/xhci-port.h

## Purpose
Defines xHCI port register bit fields and helper macros used by hub, port, ring, and PM code to interpret and update PORTSC, PORTPMSC, PORTLI, and related port-management registers.

## Important APIs, Types, And Functions
Important masks and values include `PORT_CONNECT`, `PORT_PE`, `PORT_RESET`, `PORT_PLS_MASK`, link states `XDEV_U0` through `XDEV_RESUME`, speed helpers `DEV_FULLSPEED()`, `DEV_SUPERSPEED_ANY()`, `DEV_PORT_SPEED()`, slot speed encodings, change bits in `PORT_CHANGE_MASK`, wake bits, `PORT_WR`, `PORT_U1_TIMEOUT()`, `PORT_U2_TIMEOUT()`, USB2 L1 fields, USB3 lane/link information helpers, default `XHCI_L1_TIMEOUT`, `XHCI_DEFAULT_BESL`, and `XHCI_PORT_POLLING_LFPS_TIME`.

## Control Flow
The header has no execution. Its macros are used by code that handles port status events, root-hub control requests, suspend/resume, warm reset, LPM programming, wake setup, and port polling. Correct neutralizing and write-one-to-clear behavior is enforced in callers using these definitions.

## State And Persistence
No state is allocated here. The macros describe volatile hardware state in xHCI port registers and derived software state such as root-hub status, link state, speed, and wake policy.

## Dependencies And Integration Points
Included by xHCI core files through private headers. It integrates with USB hub semantics, USB2/USB3 link power management, root-hub emulation, and event handling in `xhci-ring.c` and hub code.

## Risks And Test Signals
Risks include incorrect bit definitions corrupting port control writes, speed misclassification, mishandled write-one-to-clear change bits, and LPM fields violating device latency constraints. Test signals include connect/disconnect, reset/warm reset, over-current, remote wake, U1/U2/U3 transitions, USB2 L1 suspend/resume, SuperSpeedPlus speed reporting, and root-hub `GetPortStatus`/`SetPortFeature` tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-port.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-rcar-regs.h -->
# sources/distributed-fs/ceph-client/drivers/usb/host/xhci-rcar-regs.h

## Purpose
Defines Renesas R-Car USB3/xHCI wrapper register offsets and magic values used for firmware download, PLL status polling, interrupt enablement, and Gen2 PHY/configuration startup.

## Important APIs, Types, And Functions
Register offsets include `RCAR_USB3_AXH_STA`, `RCAR_USB3_INT_ENA`, `RCAR_USB3_DL_CTRL`, `RCAR_USB3_FW_DATA0`, `RCAR_USB3_LCLK`, `RCAR_USB3_CONF1`, `RCAR_USB3_CONF2`, `RCAR_USB3_CONF3`, `RCAR_USB3_RX_POL`, and `RCAR_USB3_TX_POL`. Bit/value macros include PLL active masks, interrupt enables, firmware download enable/success/set-data bits, Gen2 configuration values, and RX/TX polarity values.

## Control Flow
No code executes here. `xhci-rcar.c` uses these constants to poll PLL readiness, stream firmware dwords into the controller, enable wrapper interrupts, and program Gen2-specific link clock/configuration/polarity registers before running the generic xHCI core.

## State And Persistence
The header defines volatile MMIO register meanings. Firmware success and configuration bits persist only until reset or power loss, depending on SoC wrapper behavior.

## Dependencies And Integration Points
Private to the Renesas xHCI platform driver. It integrates with the `xhci_plat_priv` init/start/resume hooks that are selected by R-Car OF compatible strings.

## Risks And Test Signals
Risks include wrong offsets or magic constants causing failed firmware download, bad PLL readiness detection, broken Gen2 signal polarity, or missing interrupts. Test signals include R-Car Gen2/Gen3 probe, firmware download success, PLL timeout handling, USB3 link training, interrupt delivery, and resume after controller reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-rcar-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-rcar.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/xhci-rcar.c

## Purpose
Implements the Renesas R-Car and RZ platform xHCI wrapper. It provides firmware download and startup hooks for R-Car Gen2/Gen3, start/reset hooks for RZ/G3E and RZ/V2M, SoC match data, and a platform driver that delegates generic HCD work to `xhci_plat_probe()`.

## Important APIs, Types, And Functions
Key helpers are `xhci_rcar_start_gen2()`, `xhci_rcar_start()`, `xhci_rcar_download_firmware()`, `xhci_rcar_wait_for_pll_active()`, `xhci_rcar_init_quirk()`, and `xhci_rcar_resume_quirk()`. RZ/G3E helpers are `xhci_rzg3e_start()`, `xhci_rzg3e_suspend()`, `xhci_rzg3e_resume()`, and `xhci_rzg3e_post_resume()`. Match-data objects are `xhci_plat_renesas_rcar_gen2`, `xhci_plat_renesas_rcar_gen3`, `xhci_plat_renesas_rzv2m`, and `xhci_plat_renesas_rzg3e`.

## Control Flow
Probe gets OF match data and calls `xhci_plat_probe()`. For R-Car, the platform init quirk waits for PLL active and downloads firmware unless already successful. Firmware download requests the selected `.dlmem`, enables download mode, packs bytes into big-endian-style dwords written to `FW_DATA0`, sets the data-ready bit, polls until hardware clears it, disables download mode, and polls success. Start enables wrapper interrupts and, for Gen2, writes LCLK/configuration/polarity values. Resume re-downloads firmware if needed and restarts the wrapper. RZ/G3E start writes pipe settings and interrupt enables, with suspend/resume asserting/deasserting reset around generic xHCI PM.

## State And Persistence
State lives in wrapper MMIO registers, firmware-loaded controller RAM, reset state, and `struct xhci_plat_priv` match data. R-Car firmware is not durable across power/reset unless hardware keeps it loaded; the driver explicitly rechecks on init/resume. The driver stores no separate private object beyond generic platform xHCI state.

## Dependencies And Integration Points
Depends on firmware loader, MMIO polling, OF platform matching, reset controls, `xhci-plat.h`, `xhci-rcar-regs.h`, `xhci-rzg3e-regs.h`, and optional RZ/V2M helper declarations. It integrates with generic platform xHCI via callback hooks rather than direct HCD registration.

## Risks And Test Signals
Risks include firmware missing or malformed, atomic polling timeouts, byte packing mistakes for non-4-byte firmware tails, reset ordering on RZ/G3E, Gen2/Gen3 firmware mismatch, and 32-bit DMA/slow suspend quirk regressions. Test signals include all Renesas compatibles probing, firmware load logs, USB2/USB3 enumeration, Gen2 polarity/config behavior, RZ/G3E suspend/resume with reset, restore from hibernate, and missing firmware failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-rcar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-ring.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/xhci-ring.c

## Purpose
Implements the xHCI command, event, and endpoint transfer ring machinery. It is the central producer/consumer layer that queues command and transfer TRBs, rings doorbells, handles IRQ event TRBs, completes URBs, manages cancellation and halted endpoints, recovers command timeouts, and keeps software ring state synchronized with hardware dequeue/enqueue pointers.

## Important APIs, Types, And Functions
Exported or externally used APIs include `xhci_trb_virt_to_dma()`, `inc_deq()`, `xhci_ring_cmd_db()`, `xhci_ring_ep_doorbell()`, `xhci_ring_doorbell_for_active_rings()`, `xhci_triad_to_transfer_ring()`, `xhci_process_cancelled_tds()`, `xhci_hc_died()`, `xhci_cleanup_command_queue()`, `xhci_handle_command_timeout()`, `xhci_is_vendor_info_code()`, `xhci_update_erst_dequeue()`, `xhci_skip_sec_intr_events()`, `xhci_irq()`, `xhci_msi_irq()`, transfer queueing functions `xhci_queue_intr_tx()`, `xhci_queue_bulk_tx()`, `xhci_queue_ctrl_tx()`, `xhci_queue_isoc_tx_prepare()`, and command queueing functions such as `xhci_queue_slot_control()`, `xhci_queue_address_device()`, `xhci_queue_configure_endpoint()`, `xhci_queue_stop_endpoint()`, and `xhci_queue_reset_ep()`.

## Control Flow
Producer-side queueing first calls `prepare_ring()` or `prepare_transfer()` to verify endpoint state, expand transfer rings, link URBs to endpoints, and append TDs to ring TD lists. Queue functions build the required TRB sequence for bulk/interrupt, control, or isochronous transfers while withholding the first TRB cycle bit until the entire TD/URB is ready, then call `giveback_first_trb()` and ring the endpoint doorbell. Command queueing reserves command ring space, appends the command object to `cmd_list`, starts the command timeout timer for the head command, queues the command TRB, and rings doorbell 0.

IRQ-side flow starts in `xhci_irq()`, checks fatal/non-owned interrupt status, clears `STS_EINT`, and drains the primary interrupter event ring through `xhci_handle_events()`. Event handling dispatches command completions, transfer events, port status events, device notifications, and vendor events. Transfer completion maps event DMA back to a transfer ring and TD, translates completion codes, updates URB or isochronous frame lengths/status, handles skipped isochronous TDs, resets halted endpoints, and gives URBs back once all TDs are done. Command completions update command-specific state, run stop-endpoint/set-dequeue/reset handlers, complete waiting commands, advance the command ring dequeue pointer, and maintain the command timeout timer.

Cancellation flow stops endpoints elsewhere, then `xhci_process_cancelled_tds()` no-ops cancelled TDs when safe, queues Set TR Dequeue Pointer if hardware stopped inside a cancelled/cached TD, and gives back cleared TDs. Halt recovery queues Reset Endpoint and may clear TT buffers for FS/LS devices behind HS hubs. Host death cleanup marks the controller dying, aborts all commands, and returns pending URBs with shutdown status.

## State And Persistence
All state is volatile. Ring state includes segments, enqueue/dequeue pointers, cycle state, TD lists, old completion code, and optional bounce-buffer metadata. Endpoint state flags track stopped, halted, clearing TT, streams, set-dequeue pending, skip, and queued dequeue targets. Controller state includes `cmd_list`, `current_cmd`, command ring state, interrupter ERDP, root-hub port state, and xHC dying/removing flags. DMA-visible TRBs and contexts are persistent only while allocated and valid for hardware.

## Dependencies And Integration Points
Depends on xHCI register/context/TRB definitions from private headers, DMA mapping, scatterlist helpers, usbcore HCD/URB APIs, hub TT clearing, root-hub polling, command timer work, tracepoints, and quirk flags set by PCI/platform wrappers. It integrates with endpoint allocation, hub/port management, device addressing/configuration, stream rings, and PM paths that need events drained or skipped.

## Risks And Test Signals
High-risk areas are cycle-bit ordering, link TRB traversal, ring expansion near dequeue, command timeout/abort races, Set TR Dequeue synchronization, stale hardware dequeue caches, stream ID validation, bounce-buffer alignment and unmap direction, short packet accounting, isochronous skip/error handling, halted endpoint reset policy, and lock dropping during URB giveback or root-hub polling. Test signals include control/bulk/interrupt/isoc traffic, SG transfers crossing 64KB boundaries, zero-length packets, IDT transfers, streams, endpoint halt/stall/clear-halt, URB dequeue races, stop endpoint timeouts, command abort recovery, event ring full pressure, MSI/MSI-X IRQs, port remote wake events, KASAN/KCSAN/lockdep, and fault injection for host death.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-ring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-rzg3e-regs.h -->
# sources/distributed-fs/ceph-client/drivers/usb/host/xhci-rzg3e-regs.h

## Purpose
Defines the small RZ/G3E USB3 host wrapper register subset used by the Renesas xHCI platform driver.

## Important APIs, Types, And Functions
Macros define `RZG3E_USB3_HOST_INTEN`, per-pipe status/control offset `RZG3E_USB3_HOST_U3P0PIPESC(x)`, interrupt bits `RZG3E_USB3_HOST_INTEN_XHC` and `RZG3E_USB3_HOST_INTEN_HSE`, and combined enable value `RZG3E_USB3_HOST_INTEN_ENA`.

## Control Flow
No code runs here. `xhci-rcar.c` uses these offsets in `xhci_rzg3e_start()` to write five pipe configuration values and enable host-controller/system-error interrupts.

## State And Persistence
The header defines volatile MMIO state only. Register programming persists until reset, suspend reset assertion, or firmware/hardware reinitialization.

## Dependencies And Integration Points
Private to the Renesas RZ/G3E xHCI wrapper path selected by the `renesas,r9a09g047-xhci` compatible in `xhci-rcar.c`.

## Risks And Test Signals
Risks include wrong pipe offsets or interrupt masks preventing link bring-up or error reporting. Test signals include RZ/G3E probe, pipe configuration readback where possible, USB3 device enumeration, host/system-error interrupt delivery, and suspend/resume reset cycling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-rzg3e-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-rzv2m.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/xhci-rzv2m.c

## Purpose
Provides RZ/V2M-specific xHCI platform hooks for the Renesas wrapper. It resets the shared USB3 dual-role controller block during xHCI initialization and enables host interrupt sources when xHCI starts.

## Important APIs, Types, And Functions
The exported hook functions are `xhci_rzv2m_init_quirk(struct usb_hcd *hcd)` and `xhci_rzv2m_start(struct usb_hcd *hcd)`. Register definitions include `RZV2M_USB3_INTEN`, `RZV2M_USB3_INT_XHC_ENA`, `RZV2M_USB3_INT_HSE_ENA`, and `RZV2M_USB3_INT_ENA_VAL`.

## Control Flow
`xhci_rzv2m_init_quirk()` is called by the Renesas platform match data before generic xHCI setup and invokes `rzv2m_usb3drd_reset(dev->parent, true)` on the parent dual-role device. `xhci_rzv2m_start()` runs during HCD start and, if registers are mapped, ORs xHCI and host system error interrupt enables into the wrapper interrupt-enable register.

## State And Persistence
State is entirely hardware-side: the parent DRD reset line/state and the interrupt enable register. No private RZ/V2M software state is allocated.

## Dependencies And Integration Points
Depends on `linux/usb/rzv2m_usb3drd.h`, generic xHCI types, and `xhci-plat.h`. It is selected by `xhci-rcar.c` match data for `renesas,rzv2m-xhci`.

## Risks And Test Signals
Risks include parent-device assumptions, reset ordering with the DRD block, and missing interrupts if the enable register is not retained. Test signals include RZ/V2M host probe, parent reset side effects on role switching, USB enumeration after reset, interrupt delivery, and remove/reprobe cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-rzv2m.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-rzv2m.h -->
# sources/distributed-fs/ceph-client/drivers/usb/host/xhci-rzv2m.h

## Purpose
Declares the optional RZ/V2M xHCI hook functions used by the Renesas platform wrapper and provides compile-time stubs when RZ/V2M support is disabled.

## Important APIs, Types, And Functions
The header declares or stubs `xhci_rzv2m_start(struct usb_hcd *hcd)` and `xhci_rzv2m_init_quirk(struct usb_hcd *hcd)` behind `IS_ENABLED(CONFIG_USB_XHCI_RZV2M)`.

## Control Flow
In enabled builds, `xhci-rcar.c` match data calls the real init and start hooks. In disabled builds, start is a no-op and init returns `-EINVAL`, making accidental selection of RZ/V2M match data fail rather than silently proceeding without required reset handling.

## State And Persistence
No state is defined. Runtime state belongs to the RZ/V2M implementation and generic platform HCD.

## Dependencies And Integration Points
Private compile-time boundary between `xhci-rcar.c` and `xhci-rzv2m.c`. It relies on the caller including suitable USB HCD type declarations.

## Risks And Test Signals
Risks include disabled-build stubs causing probe failure for RZ/V2M compatibles, declaration drift, and missing type visibility. Test signals include builds with `CONFIG_USB_XHCI_RZV2M` enabled and disabled, plus RZ/V2M platform probe confirming the real hooks are linked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/xhci-rzv2m.h -->
