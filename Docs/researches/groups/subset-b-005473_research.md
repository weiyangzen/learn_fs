# Research: subset-b-005473

Grouped research for UIO PCI/platform drivers, USB build configuration, USB ATM DSL core and mini-drivers, and Cypress C67X00 host-controller support. Each section preserves the original source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/uio/uio_netx.c -->
# sources/distributed-fs/ceph-client/drivers/uio/uio_netx.c

## Purpose
`uio_netx.c` exposes Hilscher netX, netPLC, and PLX-bridged fieldbus PCI cards as UIO devices. It maps the card dual-port memory into a UIO memory region and provides a small interrupt handler that validates and disables device interrupts so userspace can acknowledge device-specific causes and re-enable them as needed.

## Important APIs, Types, And Functions
- `netx_pci_ids` matches Hilscher native PCI IDs and PLX 9030 subdevice IDs for NXSB-PCA/NXPCA variants.
- `netx_handler()` reads `DPM_HOST_INT_EN0` and `DPM_HOST_INT_STAT0`, checks `DPM_HOST_INT_MASK`, and clears `DPM_HOST_INT_GLOBAL_EN`.
- `netx_pci_probe()` allocates `struct uio_info`, enables the PCI function, requests regions, chooses BAR 0 or BAR 2, maps dual-port memory, initializes UIO metadata, disables interrupts, and registers the UIO device.
- `netx_pci_remove()` disables interrupts, unregisters UIO, releases PCI regions, disables the device, and unmaps memory.
- `module_pci_driver(netx_pci_driver)` supplies module load/unload registration.

## Control Flow
Probe starts by enabling PCI and reserving all BAR regions. Device identity selects the UIO name and BAR containing dual-port memory. The BAR is mapped with `ioremap`, then `uio_info.mem[0]` is filled as `UIO_MEM_PHYS`, IRQ sharing is enabled, and the device interrupt enable register is cleared before `uio_register_device()`. Interrupt delivery enters `netx_handler()`, which returns `IRQ_NONE` unless an enabled masked status bit belongs to this device, then disables the global interrupt enable bit and returns `IRQ_HANDLED`.

## State And Persistence Behavior
State is limited to `struct uio_info`, PCI driver data, the mapped BAR pointer, and hardware interrupt-enable bits. No persistent storage is written. The interrupt-disabled state persists in hardware until userspace or removal changes it.

## Dependencies And Integration Points
The file integrates Linux PCI, MMIO, IRQ, and UIO subsystems. Userspace receives `/dev/uioX`, maps dual-port memory, observes UIO interrupt notifications, performs card-specific acknowledgement, and re-enables interrupts through the mapped registers.

## Risks And Edge Cases
Most probe failures collapse to `-ENODEV`, losing detailed causes. BAR selection depends on the device ID and may expose no memory if firmware or board routing differs. Interrupt handling assumes BAR memory remains mapped and that the enable/status register offsets are valid for all matched boards. Because userspace owns detailed interrupt acknowledgement, a faulty userspace driver can leave interrupts disabled or unacknowledged.

## Test Signals
Build with `CONFIG_UIO` and target PCI IDs. Bind a supported or emulated PCI ID and check that `/sys/class/uio/uio*/maps/map0` matches the selected BAR. Trigger a device interrupt and confirm the UIO event count increments once and the card interrupt enable register is cleared. Validate remove/unbind leaves PCI regions released and no stale mapping is used.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/uio/uio_netx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/uio/uio_pci_generic.c -->
# sources/distributed-fs/ceph-client/drivers/uio/uio_pci_generic.c

## Purpose
`uio_pci_generic.c` is a dynamic-ID generic UIO driver for PCI 2.3 and PCIe devices. It exposes memory BARs to userspace and uses the PCI interrupt disable bit to safely mask INTx interrupts after each event.

## Important APIs, Types, And Functions
- `struct uio_pci_generic_dev` embeds `struct uio_info` and stores the bound `struct pci_dev`.
- `release()` calls `pci_clear_master()` when the UIO fd is closed.
- `irqhandler()` calls `pci_check_and_mask_intx()` and returns `IRQ_HANDLED` only for this device.
- `probe()` uses `pcim_enable_device()`, validates `pci_intx_mask_supported()`, fills memory maps from `pdev->resource[]`, and registers with `devm_uio_register_device()`.
- `uio_pci_driver.id_table = NULL` means users must add IDs through sysfs `new_id`.

## Control Flow
Userspace or admin policy adds a PCI vendor/device ID to the driver. Probe enables the device through managed PCI helpers, refuses interrupt-capable devices without INTx masking support, allocates driver state, sets UIO open/release and optional IRQ handler fields, and scans resources for memory BARs exactly matching `IORESOURCE_SIZEALIGN | IORESOURCE_MEM`. Each mapped BAR is page-aligned with `addr`, `offs`, and rounded `size`. On an interrupt, the handler masks INTx and lets the UIO core wake userspace.

## State And Persistence Behavior
The driver maintains no hardware-specific state beyond UIO memory descriptions, IRQ metadata, and the `pdev` pointer. On close, bus mastering is cleared to reduce lingering DMA exposure. Dynamic IDs remain in driver sysfs state only for the loaded module lifetime unless external policy recreates them.

## Dependencies And Integration Points
It depends on PCI core managed device enablement, UIO core, PCI resource tables, and INTx mask support. It is commonly integrated by unbinding a kernel driver and binding this UIO driver so userspace can implement device logic.

## Risks And Edge Cases
The header comment explicitly notes DMA insecurity: userspace BAR access plus bus mastering can compromise memory if no IOMMU or isolation exists. The resource flag equality check is strict and can skip resources with additional flags. MSI/MSI-X are not supported here. Devices with no IRQ still bind with a warning, leaving polling-only userspace. Clearing bus master on release can wedge some devices until reset.

## Test Signals
Add a dynamic ID, bind a PCIe device with memory BARs, and verify UIO maps expose page offsets correctly. Trigger INTx and confirm interrupts are masked until userspace reenables them through PCI config or device handling. Close the UIO fd and verify bus mastering clears. Exercise no-IRQ devices to confirm polling mode registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/uio/uio_pci_generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/uio/uio_pci_generic_sva.c -->
# sources/distributed-fs/ceph-client/drivers/uio/uio_pci_generic_sva.c

## Purpose
`uio_pci_generic_sva.c` is a generic PCI UIO driver variant that binds a PCI device to the current process address space with IOMMU Shared Virtual Addressing on UIO open, exposes the assigned PASID through sysfs, and maps PCI memory BARs for userspace.

## Important APIs, Types, And Functions
- `struct uio_pci_sva_dev` stores `pdev`, embedded `uio_info`, `iommu_sva *sva_handle`, and `pasid`.
- `uio_pci_sva_open()` detaches any existing IOMMU domain and calls `iommu_sva_bind_device(&pdev->dev, current->mm)`.
- `uio_pci_sva_release()` calls `iommu_sva_unbind_device()`.
- `probe()` enables PCI, sets a 64-bit coherent DMA mask, enables bus mastering, allocates MSI/MSI-X vectors when available, fills UIO memory maps, and registers UIO.
- `pasid_show()` exports `udev->pasid`; `uio_pci_sva_attr_groups` attaches it to the PCI driver device.

## Control Flow
Binding is dynamic because `id_table` is `NULL`. Probe enables the device, configures DMA, sets bus master, optionally allocates one MSI or MSI-X vector, initializes UIO callbacks and memory maps, registers the UIO device, and stores `udev` in PCI driver data. When userspace opens the UIO device, the driver binds the PCI device to `current->mm` through SVA and records the PASID. On release it unbinds that SVA handle.

## State And Persistence Behavior
Per-device runtime state includes the PASID and SVA handle for the currently open userspace address space. This state is not persistent and should be valid only between open and release. The device remains bus-master capable after probe until remove or external reset.

## Dependencies And Integration Points
The driver integrates PCI, UIO, DMA mask setup, MSI/MSI-X allocation, and Linux IOMMU SVA APIs. Userspace consumes BAR mappings, UIO interrupts, and the `pasid` sysfs attribute to coordinate device-side address-space tagging.

## Risks And Edge Cases
The implementation mixes devm allocation/registration with manual `kfree()` in error/remove paths, which is a lifetime risk. It does not request PCI regions before mapping resource descriptors and remove calls `pci_release_regions()` despite no matching request in probe. `info.irq = 0` may be set for polling fallback instead of `UIO_IRQ_NONE`. `uio_pci_sva_release()` unconditionally unbinds `sva_handle` and does not clear it. There is no locking around PASID/SVA state for multiple opens. Detaching an existing IOMMU domain on open is a broad side effect.

## Test Signals
Build only where IOMMU SVA is available. Bind a capable PCIe device, open `/dev/uioX`, and verify `pasid` becomes non-negative. Close and reopen from another process and confirm unbind/rebind behavior. Exercise probe failure paths with no MSI vectors and with no IOMMU SVA support. Use kmemleak/KASAN or devres debugging to catch the devm/manual-free mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/uio/uio_pci_generic_sva.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/uio/uio_pdrv_genirq.c -->
# sources/distributed-fs/ceph-client/drivers/uio/uio_pdrv_genirq.c

## Purpose
`uio_pdrv_genirq.c` is a generic platform-device UIO driver for memory-mapped devices whose interrupt can be disabled in the interrupt controller while userspace performs device-specific acknowledgement. It supports platform data and firmware-node-created devices.

## Important APIs, Types, And Functions
- `struct uio_pdrv_genirq_platdata` holds `uio_info`, a spinlock, an IRQ-disabled bit, and the platform device.
- `uio_pdrv_genirq_open()` and `release()` bridge UIO fd lifetime to runtime PM get/put.
- `uio_pdrv_genirq_handler()` disables the IRQ once with `disable_irq_nosync()`.
- `uio_pdrv_genirq_irqcontrol()` lets userspace enable or disable the IRQ without corrupting IRQ depth.
- `uio_pdrv_genirq_probe()` validates platform/fwnode metadata, discovers optional IRQ and memory resources, initializes UIO callbacks, enables runtime PM, and registers the UIO device.

## Control Flow
Probe either uses existing `struct uio_info` platform data or allocates one from a firmware node and assigns a name from `linux,uio-name` or the firmware node path. It rejects preconfigured handlers, irqcontrol callbacks, and shared IRQs because this driver owns generic IRQ masking. It obtains IRQ 0 if not supplied, maps platform memory resources into UIO physical maps, sets level-triggered IRQs to `IRQ_DISABLE_UNLAZY`, enables runtime PM, and registers the UIO device. Interrupt handling disables the IRQ and records `UIO_IRQ_DISABLED`; userspace writes to the UIO control path to re-enable after clearing the device cause.

## State And Persistence Behavior
The private flag bit tracks whether the IRQ is currently disabled, protecting IRQ depth across concurrent handler and userspace control paths. Runtime PM state is held while the UIO fd is open and released on close. Memory maps and UIO registration are devm-managed and last for the platform-device lifetime.

## Dependencies And Integration Points
The driver integrates platform devices, firmware node properties, Open Firmware matching through the `of_id` module parameter, IRQ core, runtime PM, and UIO core. Device-specific userspace must know how to map registers, acknowledge interrupts, and write UIO irqcontrol.

## Risks And Edge Cases
Interrupt sharing is intentionally unsupported. The firmware-node match table is populated by module parameter, so incorrect `of_id` can bind unintended hardware. `pm_runtime_get_sync()` return values are ignored, so wake failures are not propagated to userspace open. Platform data must not predefine handler/irqcontrol. Userspace failure to re-enable IRQ leaves the device quiet.

## Test Signals
Bind a simple platform MMIO device with one IRQ and confirm `/dev/uioX` appears with expected maps. Trigger an interrupt and verify it is disabled once, not repeatedly depth-disabled. Write irqcontrol values from multiple processes and verify enable/disable balance. Test level-triggered IRQs for immediate retrigger prevention. Validate runtime PM transitions on UIO open and close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/uio/uio_pdrv_genirq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/uio/uio_sercos3.c -->
# sources/distributed-fs/ceph-client/drivers/uio/uio_sercos3.c

## Purpose
`uio_sercos3.c` exposes Automata Sercos III PLX 9030 PCI cards as UIO devices. It maps five PCI BARs and implements device-specific interrupt enable-register caching so userspace can safely re-enable the interrupt sources that were active before the kernel handler disabled them.

## Important APIs, Types, And Functions
- `struct sercos3_priv` stores `ier0_cache` and a spinlock.
- `sercos3_disable_interrupts()` ORs the current interrupt-enable register into the cache and writes zero to the device IER.
- `sercos3_enable_interrupts()` ORs cached enable bits back into the device IER and clears the cache.
- `sercos3_handler()` verifies `ISR0 & IER0`, disables interrupts, and reports a UIO event.
- `sercos3_irqcontrol()` exposes enable/disable through UIO writes.
- `sercos3_setup_iomem()` maps a selected BAR into `uio_info.mem[n]`.

## Control Flow
Probe enables the PLX PCI function, requests regions, maps BARs 0, 2, 3, 4, and 5 into UIO map slots 0 through 4, initializes the private spinlock, fills UIO metadata, and registers the device. The interrupt handler checks status against enabled sources in BAR4 offsets `ISR0_OFFSET` and `IER0_OFFSET`; if no enabled status exists it returns `IRQ_NONE`. Otherwise it caches enabled bits, disables the register, and lets UIO wake userspace. Userspace can re-enable cached sources by writing irqcontrol on.

## State And Persistence Behavior
`ier0_cache` is runtime state preserving interrupt-enable bits observed before disable. Device registers retain interrupt state across userspace accesses until changed. UIO maps remain for the PCI device lifetime. No persistent storage exists.

## Dependencies And Integration Points
The file depends on PCI, MMIO, UIO, and PLX 9030 subvendor/subdevice matching. Userspace must understand the Sercos III register layout and should coordinate direct IER writes with UIO irqcontrol.

## Risks And Edge Cases
The source comment explicitly warns that direct userspace writes to the interrupt-enable register can race with kernel cache/restore logic. Setup errors return `-ENODEV` and manual iounmap cleanup must match successfully mapped BARs. No DMA isolation is provided. Only three subdevice IDs are matched. The handler assumes BAR4 is mapped in `mem[3]`.

## Test Signals
Bind supported PLX IDs and inspect five UIO maps. Trigger interrupts and confirm `IER0` is zeroed while `ier0_cache` restores prior bits on irqcontrol enable. Test direct userspace IER writes during interrupt traffic to understand expected race behavior. Unbind after partial probe failures under fault injection and check all mapped BARs are unmapped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/uio/uio_sercos3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/usb/Kconfig

## Purpose
`drivers/usb/Kconfig` is the top-level USB configuration menu. It defines foundational endianness symbols, the `USB_SUPPORT` and `USB` core options, PCI host support toggles, and includes submenus for common USB code, core, monitors, HCDs, class/storage/image/USBIP drivers, dual-mode controllers, serial/misc/ATM peripheral drivers, PHY, gadget, Type-C, and role-switch support.

## Important APIs, Types, And Functions
- `USB_SUPPORT` gates the entire USB menu and depends on `HAS_IOMEM`.
- `USB` builds host-side USB core support and selects `GENERIC_ALLOCATOR`, `USB_COMMON`, and `NLS`.
- `USB_PCI` and `USB_PCI_AMD` control PCI-specific host integration and AMD quirk support.
- Endianness booleans such as `USB_OHCI_BIG_ENDIAN_DESC` and `USB_EHCI_BIG_ENDIAN_MMIO` are selected by lower-level host drivers.
- `source` directives include all child Kconfig files in a deliberate dependency order.

## Control Flow
Kconfig evaluation starts with low-level helper symbols, then displays `USB_SUPPORT`. If enabled, common USB code and host-side USB become available. If `USB` is selected, host core, monitor, HCD, class, storage, image, and USBIP menus are included. Dual-mode controller menus are included under USB support even outside the `if USB` block where appropriate. USB serial, misc, and ATM drivers are included only when host USB is enabled. PHY, gadget, Type-C, and role-switch menus are then sourced before closing `USB_SUPPORT`.

## State And Persistence Behavior
The file contributes build-time `.config` state only. It does not define runtime state, but selected symbols determine which USB subsystems and modules exist in the built kernel.

## Dependencies And Integration Points
This file integrates with the kernel Kconfig system and child USB subsystem Kconfigs. It coordinates dependencies for the Makefile paths in `drivers/usb/Makefile`, including `drivers/usb/atm/Kconfig` for the DSL modem files in this work item.

## Risks And Edge Cases
Misplaced `source` directives can expose options without required host support or hide drivers unexpectedly. `USB_PCI` defaults to yes on PCI systems but can be disabled for SoCs with non-PCI USB. Endianness helper symbols are invisible and rely on child drivers selecting them correctly. The `USB` tristate controls `usbcore` module availability and can ripple widely.

## Test Signals
Run `make menuconfig` or `scripts/kconfig/conf` for configs with `USB_SUPPORT=n`, `USB_SUPPORT=y USB=n`, and `USB=m/y`. Confirm USB ATM appears only under host USB. Verify generated `.config` drives expected object directories in `drivers/usb/Makefile`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/Makefile -->
# sources/distributed-fs/ceph-client/drivers/usb/Makefile

## Purpose
`drivers/usb/Makefile` maps USB Kconfig symbols to subdirectory builds. It is the top-level kbuild dispatcher for USB common/core code, host controllers, dual-mode controllers, class/storage/image/serial/misc drivers, USB ATM, gadgets, USBIP, Type-C, and role-switch support.

## Important APIs, Types, And Functions
- `obj-$(CONFIG_USB_COMMON) += common/` and `obj-$(CONFIG_USB) += core/` build core infrastructure.
- Multiple HCD symbols append `host/`, allowing the host subdirectory to be entered for many controller choices.
- `obj-$(CONFIG_USB_C67X00_HCD) += c67x00/` dispatches the Cypress controller files in this work item.
- `obj-$(CONFIG_USB_ATM) += atm/` and `obj-$(CONFIG_USB_SPEEDTOUCH) += atm/` enter the ATM subdirectory.
- `obj-$(CONFIG_USB) += storage/` and `obj-$(CONFIG_USB_STORAGE) += storage/` keep storage subdirectory traversal available for core storage glue.

## Control Flow
Kbuild evaluates each `obj-*` line against the final configuration. Built-in `y` descends into a subdirectory for built-in objects; `m` descends for modules. The same subdirectory can appear from multiple config symbols, and kbuild coalesces traversal. This file does not compile C directly; child Makefiles define exact objects.

## State And Persistence Behavior
It creates build graph state only. There is no runtime behavior, but enabled symbols determine which modules and built-in objects are present.

## Dependencies And Integration Points
The Makefile must stay aligned with `drivers/usb/Kconfig` and child Makefiles. It integrates with `drivers/usb/atm/Makefile` for `usbatm`, `speedtch`, `cxacru`, `ueagle-atm`, and `xusbatm`, and with `drivers/usb/c67x00/Makefile` for the Cypress host controller aggregate object.

## Risks And Edge Cases
Duplicate subdirectory entries are intentional but can obscure why a directory is entered. If a Kconfig symbol is renamed without updating this file, selected code silently stops building. Entering `atm/` on `CONFIG_USB_SPEEDTOUCH` as well as `CONFIG_USB_ATM` protects SpeedTouch selection, but child dependencies still matter.

## Test Signals
Run targeted builds with `CONFIG_USB_C67X00_HCD=m`, `CONFIG_USB_ATM=m`, and individual ATM mini-drivers. Use `make V=1` to confirm subdirectory traversal and resulting module names. Compare generated `modules.order` with expected USB modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/atm/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/usb/atm/Kconfig

## Purpose
`drivers/usb/atm/Kconfig` defines USB DSL modem support and the selectable USB ATM mini-drivers. It gates the shared `usbatm` core on ATM support and offers SpeedTouch, Conexant AccessRunner, ADI/eagle, and parameterized generic modem drivers.

## Important APIs, Types, And Functions
- `menuconfig USB_ATM` is a tristate depending on `ATM` and selecting `CRC32`; it builds the shared `usbatm` module.
- `USB_SPEEDTOUCH`, `USB_CXACRU`, and `USB_UEAGLEATM` select `FW_LOADER` because they need firmware blobs.
- `USB_XUSBATM` provides generic support using module parameters for vendor/product and endpoint numbers.
- Help text documents module names: `usbatm`, `speedtch`, `cxacru`, `ueagle-atm`, and `xusbatm`.

## Control Flow
When `USB_ATM` is enabled, the child driver prompts become visible. Each selected mini-driver builds alongside the shared core and calls into `usbatm_usb_probe()`/`usbatm_usb_disconnect()` at runtime. Firmware-loading drivers select firmware loader support automatically.

## State And Persistence Behavior
The file defines build-time configuration state only. Runtime persistence is limited to module parameters in the C drivers, not this Kconfig file.

## Dependencies And Integration Points
It integrates USB host support from the parent Kconfig with the Linux ATM stack. The corresponding object mapping lives in `drivers/usb/atm/Makefile`; the C files implement the mini-driver hooks declared in `usbatm.h`.

## Risks And Edge Cases
`USB_ATM` depends on `ATM`, so users may not see USB DSL options unless ATM support is enabled. Firmware help links are historical and may be stale. Selecting a mini-driver without correct firmware files will build successfully but fail at runtime during heavy initialization.

## Test Signals
Run Kconfig with and without `CONFIG_ATM` to verify visibility. Build each mini-driver as `m` and confirm the shared `usbatm` module is included. Boot tests should check firmware request names and module autoload aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/atm/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/atm/Makefile -->
# sources/distributed-fs/ceph-client/drivers/usb/atm/Makefile

## Purpose
`drivers/usb/atm/Makefile` maps the USB ATM Kconfig symbols to the shared core module and mini-driver modules.

## Important APIs, Types, And Functions
- `obj-$(CONFIG_USB_CXACRU) += cxacru.o`
- `obj-$(CONFIG_USB_SPEEDTOUCH) += speedtch.o`
- `obj-$(CONFIG_USB_UEAGLEATM) += ueagle-atm.o`
- `obj-$(CONFIG_USB_ATM) += usbatm.o`
- `obj-$(CONFIG_USB_XUSBATM) += xusbatm.o`

## Control Flow
Kbuild includes object files according to the tristate values selected in Kconfig. The mini-drivers are independent modules that depend on symbols exported by `usbatm.o`, so module dependency generation should load `usbatm` first.

## State And Persistence Behavior
This file affects build graph state only. Runtime state is entirely in the generated modules.

## Dependencies And Integration Points
The object names align with `drivers/usb/atm/Kconfig` module descriptions and with C module names. It integrates with the top-level USB Makefile, which descends into `atm/` for USB ATM-related configurations.

## Risks And Edge Cases
If a mini-driver symbol is selected while `USB_ATM` is absent or misconfigured, linking would fail because the mini-driver calls shared `usbatm` exports. Current Kconfig nesting prevents that. Renaming `ueagle-atm.o` or other hyphenated module names requires matching source and firmware documentation updates.

## Test Signals
Build each symbol as module and verify `modules.order` includes the expected `.ko` files. Run `modinfo` to confirm dependencies on `usbatm` for mini-drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/atm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/atm/cxacru.c -->
# sources/distributed-fs/ceph-client/drivers/usb/atm/cxacru.c

## Purpose
`cxacru.c` is a `usbatm` mini-driver for Conexant AccessRunner USB ADSL modems. It handles modem-specific firmware loading, command-channel transfers, sysfs DSL status/configuration, MAC acquisition, line start/stop, and periodic status polling while delegating ATM cell I/O to the shared `usbatm` core.

## Important APIs, Types, And Functions
- `struct cxacru_data` stores the `usbatm` instance, modem type, ADSL status, card-info array, polling state, command URBs, command buffers, completions, and mutexes.
- `cxacru_bind()` allocates command buffers/URBs, validates command endpoints, initializes polling work, and sets `UDSL_SKIP_HEAVY_INIT` if firmware is already alive.
- `cxacru_heavy_init()` requests `cxacru-fw.bin` and optional `cxacru-bp.bin`, writes PLL/SDRAM/firmware/signature memory, starts firmware, clears halts, and verifies card status.
- `cxacru_cm()` serializes command-monitor packets over endpoint 1 and validates response command/status packets.
- `cxacru_atm_start()` fetches MAC address, starts the ADSL line, and starts polling.
- `cxacru_poll_status()` reads `CARD_INFO_GET`, updates `card_info`, logs line transitions, updates ATM signal, and reschedules delayed work.
- Sysfs attributes expose rates, margins, attenuation, errors, modulation, MAC, `adsl_state`, and write-only `adsl_config`.

## Control Flow
The USB driver filters out vendor-specific "USB NET CARD" routers, then calls `usbatm_usb_probe()` with `cxacru_driver`. Bind creates the mini-driver state and command URBs. If `cxacru_card_status()` succeeds, heavy init is skipped; otherwise the `usbatm` heavy-init thread loads firmware and then initializes ATM. ATM start fetches the MAC and sends `CHIP_ADSL_LINE_START`. Poll work periodically retrieves card info, updates sysfs-backed cached values, changes ATM carrier state, and reschedules until stopped or shutdown.

## State And Persistence Behavior
Runtime state includes the cached `card_info[]`, line and ADSL status, polling state machine, command buffers, command URBs, and firmware-loaded hardware state. Sysfs writes can change modem card-data configuration and start/stop state in hardware, but the driver does not persist those settings to disk.

## Dependencies And Integration Points
The driver depends on USB core, firmware loader, sysfs attribute groups, `usbatm`, Linux ATM, and firmware files. It integrates with `usbatm` through `bind`, `heavy_init`, `unbind`, `atm_start`, endpoint definitions, and RX/TX padding values.

## Risks And Edge Cases
Command transfers require serialized send/receive URBs and timeouts; failures disable polling until userspace restarts it. The firmware path contains multiple device-memory writes with limited recovery if firmware partially starts. Sysfs `adsl_config` accepts index/value pairs and requires `CAP_NET_ADMIN`, but malformed input returns early. Poll cancellation depends on `CXPOLL_SHUTDOWN` and delayed work ordering. Historical devices vary between interrupt and bulk command endpoints.

## Test Signals
Test both already-firmware-loaded and cold firmware paths. Verify firmware request names, MAC retrieval, `/sys/bus/usb/.../cxacru` attributes, `adsl_state` start/stop/restart/poll writes, and ATM carrier transitions. Exercise command timeout paths by unplugging during polling. Confirm RX/TX padding interworks with `usbatm` cell traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/atm/cxacru.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/atm/speedtch.c -->
# sources/distributed-fs/ceph-client/drivers/usb/atm/speedtch.c

## Purpose
`speedtch.c` is the `usbatm` mini-driver for Alcatel/Thomson SpeedTouch USB DSL modems. It handles multi-interface claiming, two-stage firmware upload, interface altsetting selection for bulk or isochronous data, modem synchronization commands, status polling, and interrupt-driven line state hints.

## Important APIs, Types, And Functions
- Module parameters include `altsetting`, `dl_512_first`, `enable_isoc`, `sw_buffering`, `BMaxDSL`, `ModemMode`, and `ModemOption`.
- `struct speedtch_instance_data` stores a snapshot of parameters, status and resubmit timers, status work, interrupt URB/data, poll delay, and scratch buffer.
- `speedtch_upload_firmware()` uploads stage 1 and stage 2 firmware through endpoint 5, sets the data interface, optionally enables software buffering, and sends the magic test/option sequence.
- `speedtch_check_status()` reads multiple control status fields and updates ATM signal/link rate.
- `speedtch_handle_int()` handles known up/down interrupt packets and resubmits or schedules recovery.
- `speedtch_bind()` claims all interfaces, chooses data altsetting, detects isochronous support, allocates the interrupt URB, and detects preloaded firmware.
- `speedtch_atm_start()` derives ESI from USB serial, starts synchronization, submits interrupt URB, and starts polling.

## Control Flow
Probe delegates to `usbatm_usb_probe()`. Bind verifies vendor-specific class, claims companion interfaces, snapshots mutable module parameters, tries requested or default altsettings, sets `UDSL_USE_ISOC` if applicable, allocates timers/work/interrupt URB, and resets the device if firmware is absent. Heavy init requests `speedtch-1.bin*` and `speedtch-2.bin*`, uploads both firmware blocks, then configures the modem. ATM start prods synchronization and starts both interrupt URB and periodic status timer. Status work reads modem state and adapts the polling delay after failures.

## State And Persistence Behavior
The driver keeps per-device parameter snapshots so later module parameter changes do not affect an already-bound modem. Runtime state includes last status, adaptive poll delay, interrupt URB lifecycle, and timers. Firmware-loaded state exists in the modem, not on disk. The driver does not persist line settings.

## Dependencies And Integration Points
It depends on USB core, firmware loader, workqueues, timers, `usbatm`, and ATM. It integrates with `usbatm` through `bind`, `heavy_init`, `unbind`, `atm_start`, `atm_stop`, and endpoint declarations for bulk and isochronous data.

## Risks And Edge Cases
Firmware naming falls back through device-revision-specific names to generic names. Interrupt URB and resubmit timer can schedule each other, so `speedtch_atm_stop()` uses a two-step shutdown with `instance->int_urb = NULL`, barriers, kills, and timer deletion. MAC parsing from the serial string assumes 12 hex characters. Status polling backs off and eventually disables itself after repeated failures. Interface claiming must be released on every bind failure.

## Test Signals
Test cold firmware upload and already-loaded detection. Verify bulk default and isochronous altsetting paths. Confirm ESI from serial number, line-up/down ATM signal changes, status polling backoff, interrupt URB resubmission, and clean disconnect during active polling. Validate all claimed interfaces are released on unbind and bind failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/atm/speedtch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/atm/ueagle-atm.c -->
# sources/distributed-fs/ceph-client/drivers/usb/atm/ueagle-atm.c

## Purpose
`ueagle-atm.c` is a `usbatm` mini-driver for ADI 930 and Eagle USB ADSL modems. It handles pre-firmware USB bootstrap, DSP page loading, CMV configuration, modem reset/reboot, status monitoring, optional synchronization wait, sysfs statistics, and multiple chip generations including Eagle IV protocol differences.

## Important APIs, Types, And Functions
- `struct uea_softc` stores USB/usbatm pointers, chip metadata, annex selection, boot/reset flags, wait queue, control thread, CMV descriptors, work item, DSP firmware, interrupt URB, protocol function pointers, and exported PHY stats.
- `uea_probe()` resets the USB device, loads pre-firmware for prefirm IDs, or delegates post-firmware devices to `usbatm_usb_probe()`.
- `uea_bind()` claims monitor/upstream/downstream interfaces, selects annex and altsetting, sets `UDSL_USE_ISOC`/`UDSL_IGNORE_EILSEQ`, and calls `uea_boot()`.
- `uea_boot()` chooses Eagle I/IV handlers, allocates the interrupt URB, submits it, and creates the monitoring kthread.
- `uea_start_reset()` drives modem reset, schedules DSP page 0 load, waits for modem-ready CMV, sends CMV configuration, and clears reset.
- `uea_load_page_e1()` and `uea_load_page_e4()` send DSP blocks over IDMA when interrupt packets request swap pages.
- `uea_cmv_e1()`/`uea_cmv_e4()` issue CMV reads/writes and wait for interrupt acknowledgements.
- `uea_stat_e1()`/`uea_stat_e4()` poll modem state and update ATM signal, link rate, margins, attenuation, and error counters.

## Control Flow
Pre-firmware devices request generation-specific firmware asynchronously and upload it through vendor control writes. Post-firmware devices bind through `usbatm`, claim extra interfaces, and create a control thread but only start it after generic initialization completes. The thread loops: reset or recover on errors, load DSP pages on interrupt requests via workqueue, wait for modem-ready CMV, send CMV files, then poll stats every second. Interrupt URBs dispatch either swap-page requests or CMV replies and resubmit themselves.

## State And Persistence Behavior
Runtime state is substantial: CMV ack state, current DSP page/overlay, loaded firmware pointer, modem stats, reset flag, synchronization wait queue, and module-parameter-derived annex/altsetting choices. Sysfs attributes expose and sometimes reset cached counters; writing `stat_status` requests reset. Firmware and CMV files are read from the firmware loader but no persistent state is written.

## Dependencies And Integration Points
The driver depends on USB core, firmware loader, CRC validation, kthreads, workqueues, wait queues, sysfs, `usbatm`, and ATM. It declares many `MODULE_FIRMWARE()` names for bootstrap, DSP, FPGA, and CMV files. It integrates with `usbatm` via mini-driver hooks and endpoint definitions.

## Risks And Edge Cases
There are many hardware-generation branches and endian-specific packet formats. CMV ack waits can timeout, causing reboot loops. Interrupt resubmission errors are not strongly recovered. Interface-claim failure paths in `uea_bind()` can leave earlier claimed interfaces until generic disconnect/release. Firmware/CMV validation prevents some corruption but missing files are common deployment failures. `modem_index` is global and wraps, so module-parameter association across multiple devices is order-dependent.

## Test Signals
Test prefirm and postfirm IDs for each chip family. Validate firmware CRC/corruption rejection, DSP page loading after interrupt requests, CMV v1/v2 fallback, annex auto/manual selection, bulk and isochronous modes, `sync_wait`, sysfs stats, write-triggered reset, and disconnect while the kthread waits for CMV or sync. Confirm ATM carrier becomes lost during reset and found when operational.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/atm/ueagle-atm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/atm/usbatm.c -->
# sources/distributed-fs/ceph-client/drivers/usb/atm/usbatm.c

## Purpose
`usbatm.c` is the shared USB ATM/DSL core used by mini-drivers. It registers an ATM device, manages USB RX/TX URB pools, performs ATM cell extraction and AAL5 reassembly, encodes outbound AAL5 PDUs into ATM cells, handles VCC open/close/send callbacks, runs optional mini-driver heavy initialization, and coordinates disconnect cleanup.

## Important APIs, Types, And Functions
- Module parameters `num_rcv_urbs`, `num_snd_urbs`, `rcv_buf_bytes`, and `snd_buf_bytes` size URB pools and buffers.
- `struct usbatm_vcc_data` tracks VPI/VCI, `atm_vcc`, and SAR reassembly buffer.
- `struct usbatm_control` stores outbound skb ATM metadata, original length, and CRC in `skb->cb`.
- `usbatm_usb_probe()` allocates `struct usbatm_data`, calls mini-driver `bind`, allocates URBs/buffers, starts heavy init or ATM init, and sets USB interface data.
- `usbatm_usb_disconnect()` marks disconnected, stops heavy init, releases VCCs, kills URBs/timers/tasklets, calls mini-driver stop/unbind, frees buffers, deregisters ATM, and drops references.
- `usbatm_extract_one_cell()`/`usbatm_extract_cells()` implement AAL5 receive reassembly and CRC validation.
- `usbatm_write_cells()` and `usbatm_tx_process()` implement outbound cell segmentation.
- `usbatm_atm_open()`, `close()`, `send()`, `ioctl()`, and `proc_read()` implement ATM operations.

## Control Flow
Probe builds one RX and one TX channel, chooses bulk or isochronous RX based on mini-driver flags, allocates URBs, queues TX URBs as spares, and either starts a heavy-init kthread or initializes ATM directly. ATM init registers the ATM device, lets the mini-driver start it, then submits RX URBs. RX completion queues URBs to a tasklet; the tasklet extracts complete cells, handles partial strides, and resubmits URBs. TX send queues skb PDUs; the TX tasklet pops spare URBs and encodes cells until buffers are full or queues drain. Disconnect serializes against open/close, cancels asynchronous activity, releases VCCs, and deregisters ATM.

## State And Persistence Behavior
Per-device state includes kref lifetime, disconnect flag, serialization mutex, heavy-init thread completions, VCC list, cached VPI/VCI lookup, partial RX cell buffer, current TX skb, skb send queue, URB arrays, channel timers/tasklets, and ATM device pointer. No on-disk state exists. ATM counters are maintained through the ATM stack.

## Dependencies And Integration Points
The file depends on USB core, Linux ATM, sk_buffs, CRC32, tasklets, timers, kthreads, completions, and mini-driver hooks declared in `usbatm.h`. Mini-drivers provide endpoints, padding, firmware/control-plane behavior, and optional ATM start/stop callbacks.

## Risks And Edge Cases
URB submit errors are treated as transient and can throttle via timers. RX isochronous frame merging must preserve cell boundaries and resets partial buffers on frame errors. VCC list and cached lookup are protected by disabling RX tasklet during updates. Disconnect ordering is delicate because heavy init, ATM callbacks, tasklets, timers, and URBs can all race. `skb->cb` size is checked at module init. Only AAL5 is supported; OAM F5 is counted as unsupported.

## Test Signals
Run with mini-drivers in bulk and isochronous modes. Open multiple VCCs, verify VPI/VCI demultiplexing and duplicate rejection, send max-size AAL5 PDUs, inject CRC/length errors, and confirm ATM stats. Fault-inject URB submit failures and unplug during heavy init, active RX, active TX, and VCC close. Validate module parameter bounds at init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/atm/usbatm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/atm/usbatm.h -->
# sources/distributed-fs/ceph-client/drivers/usb/atm/usbatm.h

## Purpose
`usbatm.h` defines the shared interface between the generic USB ATM core and USB DSL mini-drivers. It declares logging helpers, mini-driver flags and callbacks, endpoint/padding configuration, probe/disconnect exports, channel state, and the main per-device `struct usbatm_data`.

## Important APIs, Types, And Functions
- Logging macros `usb_err`, `usb_info`, `atm_err`, `atm_warn`, and debug variants standardize USB and ATM messages.
- Flags `UDSL_SKIP_HEAVY_INIT`, `UDSL_USE_ISOC`, and `UDSL_IGNORE_EILSEQ` let mini-drivers alter core behavior.
- `struct usbatm_driver` defines `bind`, `heavy_init`, `unbind`, `atm_start`, `atm_stop`, endpoint numbers, and RX/TX padding.
- `usbatm_usb_probe()` and `usbatm_usb_disconnect()` are exported for mini-driver USB probe/disconnect functions.
- `struct usbatm_channel` describes a USB pipe, ATM stride, buffer sizing, spare/completed URB list, tasklet, throttle timer, and back-pointer.
- `struct usbatm_data` combines public mini-driver-visible fields with private core state.
- `to_usbatm_driver_data()` safely retrieves mini-driver state from a USB interface.

## Control Flow
The header itself has no executable control flow. It documents the intended mini-driver callback order: `bind`, optional `heavy_init`, `atm_start`, later `atm_stop`, and `unbind`. The C core enforces that lifecycle and uses endpoint/padding fields to configure URB channels.

## State And Persistence Behavior
`struct usbatm_data` state is runtime-only and owned by the core after probe. Public fields can be initialized by mini-drivers during bind; private fields must not be touched by them. No persistent state is described.

## Dependencies And Integration Points
The header integrates USB mini-drivers with Linux ATM, USB core, kref lifetime, completions, lists, mutexes, timers, and sk_buffs. It is included by `usbatm.c`, `cxacru.c`, `speedtch.c`, `ueagle-atm.c`, and `xusbatm.c`.

## Risks And Edge Cases
The public/private split is by comment, not compiler enforcement. Mini-drivers must set endpoints and padding consistently with hardware or the core will segment cells incorrectly. `to_usbatm_driver_data()` returns NULL after interface data is cleared or after `driver_data` is nulled, which sysfs paths must handle.

## Test Signals
Compile every mini-driver against the header. Add sparse or runtime assertions around mini-driver flags/endpoints. Exercise sysfs reads after disconnect to verify `to_usbatm_driver_data()` NULL handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/atm/usbatm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/atm/xusbatm.c -->
# sources/distributed-fs/ceph-client/drivers/usb/atm/xusbatm.c

## Purpose
`xusbatm.c` is a generic, parameter-driven `usbatm` mini-driver for USB DSL modems that are initialized by userspace or unsupported by specific mini-drivers. It creates up to eight dynamic USB ID and mini-driver entries from module parameters and binds endpoints/altsettings without firmware logic.

## Important APIs, Types, And Functions
- Module parameter arrays define `vendor`, `product`, `rx_endpoint`, `tx_endpoint`, `rx_padding`, `tx_padding`, `rx_altsetting`, and `tx_altsetting`.
- `xusbatm_find_intf()` locates an interface containing an endpoint in a requested altsetting.
- `xusbatm_capture_intf()` optionally claims an interface and sets its altsetting.
- `xusbatm_bind()` validates RX/TX interfaces and altsettings, claims non-primary interfaces, and configures endpoints.
- `xusbatm_unbind()` releases every interface owned by this `usbatm` instance.
- `xusbatm_atm_start()` assigns a random ESI/MAC because no hardware-specific retrieval exists.
- `xusbatm_init()` validates parameter counts and fills `xusbatm_usb_ids[]` plus `xusbatm_drivers[]`.

## Control Flow
On module load, the parameter arrays must contain equal counts for vendor, product, RX endpoint, and TX endpoint. Each entry becomes a USB device ID and a `usbatm_driver`. Probe selects the corresponding driver by ID-array offset and calls `usbatm_usb_probe()`. Bind finds RX and TX interfaces at requested altsettings, rejects unrelated primary interfaces or conflicting altsettings on the same interface, claims any companion interfaces, and returns to the core for URB setup.

## State And Persistence Behavior
Global arrays store parameter-derived USB IDs and driver descriptors for the module lifetime. Per-device state is owned by `usbatm`; this driver has no extra per-device allocation. ATM ESI is random at each start and is not persistent.

## Dependencies And Integration Points
It depends on USB core, `usbatm`, and `eth_random_addr()`. Userspace is expected to handle device-specific firmware or initialization before kernel ATM traffic is useful.

## Risks And Edge Cases
Malformed parameter arrays fail module load. Endpoint numbers are normalized by forcing RX IN and TX endpoint number bits, which can surprise users who pass full endpoint addresses. Same-interface RX/TX with different altsettings is rejected. No modem status, firmware, line control, or real MAC retrieval exists, so operational success depends on external setup.

## Test Signals
Load with valid and invalid parameter counts. Bind a test USB device with RX/TX endpoints on the same and different interfaces. Verify altsetting changes, companion interface claims/releases, random ESI assignment, and clean unbind. Confirm data paths inherit padding values through `usbatm`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/atm/xusbatm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/c67x00/Makefile -->
# sources/distributed-fs/ceph-client/drivers/usb/c67x00/Makefile

## Purpose
`drivers/usb/c67x00/Makefile` builds the Cypress C67X00 USB controller driver as one composite object when `CONFIG_USB_C67X00_HCD` is enabled.

## Important APIs, Types, And Functions
- `obj-$(CONFIG_USB_C67X00_HCD) += c67x00.o` declares the module or built-in object.
- `c67x00-y := c67x00-drv.o c67x00-ll-hpi.o c67x00-hcd.o c67x00-sched.o` links common platform glue, low-level HPI access, HCD/root-hub code, and scheduler code into that object.

## Control Flow
Kbuild descends into this directory from the top-level USB Makefile and links the listed constituent objects into `c67x00.o`. This file has no runtime control flow.

## State And Persistence Behavior
It affects build state only. Runtime state is in the compiled C files.

## Dependencies And Integration Points
The Makefile must stay synchronized with C file boundaries and Kconfig symbol `USB_C67X00_HCD`. The files researched here cover three of the four linked units; `c67x00-sched.o` supplies transfer scheduling referenced by `c67x00-hcd.h`.

## Risks And Edge Cases
Removing one constituent object can create unresolved symbols because the driver is tightly split between platform, HPI, HCD, and scheduler layers. The composite object name must match module alias and user expectations.

## Test Signals
Build `CONFIG_USB_C67X00_HCD=m` and verify one `c67x00.ko` module containing symbols from all four objects. Build as built-in and confirm no duplicate object linkage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/c67x00/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/c67x00/c67x00-drv.c -->
# sources/distributed-fs/ceph-client/drivers/usb/c67x00/c67x00-drv.c

## Purpose
`c67x00-drv.c` is the platform-driver and common interrupt infrastructure for Cypress C67X00 USB controllers. It maps the Host Port Interface registers, initializes low-level hardware access, resets the controller, creates per-SIE subdrivers, and dispatches controller interrupts to each SIE.

## Important APIs, Types, And Functions
- `c67x00_probe_sie()` initializes a `struct c67x00_sie`, reads platform SIE mode, and calls `c67x00_hcd_probe()` for host mode.
- `c67x00_remove_sie()` removes host-mode SIEs.
- `c67x00_irq()` reads HPI status, acknowledges low-level IRQ state, fetches SIE messages, calls each SIE IRQ callback, and loops up to a bounded count.
- `c67x00_drv_probe()` obtains MEM and IRQ resources, platform data, maps HPI registers, initializes HPI locks and low-level registers, requests IRQ, resets hardware, and probes both SIEs.
- `c67x00_drv_remove()` removes SIEs, frees IRQ, unmaps HPI, releases memory, and frees the device.

## Control Flow
Platform probe requires one memory resource, one IRQ resource, and platform data. It reserves and maps HPI registers, initializes low-level communication, registers the IRQ handler, resets the device, then iterates over the two SIEs and starts host-controller support for those configured as host. IRQ handling reads status and repeatedly drains pending conditions: low-level mailbox completion, SIE messages, and SIE-specific callbacks. Removal reverses SIE creation before releasing common resources.

## State And Persistence Behavior
`struct c67x00_device` owns HPI base address, regstep, locks, platform data, platform device pointer, and two SIE states. Each SIE stores mode, lock, private host data, and IRQ callback. No persistent storage exists.

## Dependencies And Integration Points
The file depends on platform-device resources, platform data from `<linux/usb/c67x00.h>`, low-level HPI functions in `c67x00-ll-hpi.c`, and host-controller creation in `c67x00-hcd.c`. It is the bridge between board description and USB HCD registration.

## Risks And Edge Cases
The IRQ loop is capped and warns if status remains, which can indicate unhandled interrupt sources. Only host mode is supported; device/OTG modes report unsupported. Platform data is mandatory. Probe uses manual allocation/resource management, so failure ordering must stay correct. The IRQ is requested before reset, requiring low-level state to be ready.

## Test Signals
Instantiate a platform device with valid resources and SIE host configuration. Verify HPI mapping, reset success, two SIE mode paths, IRQ dispatch on SIE messages and SOF/EOP, and bounded-loop warning under forced stuck status. Remove while USB devices are attached to exercise HCD teardown first.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/c67x00/c67x00-drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/c67x00/c67x00-hcd.c -->
# sources/distributed-fs/ceph-client/drivers/usb/c67x00/c67x00-hcd.c

## Purpose
`c67x00-hcd.c` implements the Linux USB host-controller-driver layer and root-hub behavior for one Cypress C67X00 SIE in host mode. It provides root hub status/control operations, HCD lifecycle hooks, frame-number retrieval, IRQ callback handling, and setup/teardown of the scheduler-backed HCD instance.

## Important APIs, Types, And Functions
- `c67x00_hub_des` is the fixed two-port hub descriptor.
- `c67x00_hub_status_data()` reports port connection-change bits to USB core.
- `c67x00_hub_control()` handles hub class requests such as `GetPortStatus`, `SetPortFeature RESET`, and clear-change operations.
- `c67x00_hcd_irq()` is called by common IRQ dispatch and kicks scheduling on TD-list-done or SOF/EOP events.
- `c67x00_hcd_start()`, `stop()`, and `get_frame()` implement `hc_driver` hooks.
- `c67x00_hc_driver` wires URB enqueue/dequeue, endpoint disable, frame number, and hub operations into USB core.
- `c67x00_hcd_probe()` allocates a `usb_hcd`, initializes `struct c67x00_hcd`, starts the scheduler, adds the HCD, and attaches the SIE IRQ callback.
- `c67x00_hcd_remove()` stops the scheduler, removes the HCD, and drops the HCD reference.

## Control Flow
HCD probe creates a USB 1.1 memory-mapped HCD, initializes lists for isochronous, interrupt, control, and bulk URBs, sets C67X00 internal TD/buffer base addresses by SIE number, initializes host ports, starts the scheduler, and registers the HCD with USB core. Hub requests read/write low-level USB status/control registers and perform port reset through HPI commands. IRQ callbacks kick the scheduler when TD lists complete or SOF/EOP occurs.

## State And Persistence Behavior
Runtime host state lives in `struct c67x00_hcd`: port speed bitmask, URB counts, per-pipe queues, TD list and bandwidth accounting, internal memory allocation cursors, scheduler work, endpoint-disable completion, and frame tracking. No persistent state exists.

## Dependencies And Integration Points
The file depends on USB HCD core, root-hub request definitions, low-level C67X00 accessors, and scheduler functions declared in `c67x00-hcd.h`. It integrates with `c67x00-drv.c` through `c67x00_hcd_probe/remove` and the SIE IRQ callback pointer.

## Risks And Edge Cases
The root hub models power as always enabled and has limited suspend/over-current behavior. Port index checks use `wIndex > C67X00_PORTS`, so callers must provide one-based hub port indices as expected by USB core. Unknown SIE message flags only warn. Scheduler correctness is external but central to all URB I/O. Removal assumes `sie->private_data` is valid for host-mode SIEs.

## Test Signals
Attach low-speed and full-speed devices and verify port status bits and `low_speed_ports`. Exercise hub reset, clear connection change, frame-number reads, SOF/EOP scheduling, and TD-list-done scheduling. Run USB core enumeration and disconnect tests for both ports. Validate HCD remove with active URBs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/c67x00/c67x00-hcd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/c67x00/c67x00-hcd.h -->
# sources/distributed-fs/ceph-client/drivers/usb/c67x00/c67x00-hcd.h

## Purpose
`c67x00-hcd.h` defines the Cypress C67X00 host-controller private state, bandwidth constants, HCD conversion helpers, and cross-file prototypes for HCD setup and transfer scheduling.

## Important APIs, Types, And Functions
- Bandwidth constants define `TOTAL_FRAME_BW`, `DEFAULT_EOT`, standard and isochronous max frame bandwidth, and periodic bandwidth policy.
- `struct c67x00_hcd` stores the SIE pointer, port speed state, URB counts, per-pipe lists, bandwidth accounting, TD/buffer memory allocation cursors, scheduler work, endpoint-disable completion, and frame numbers.
- `hcd_to_c67x00_hcd()` and `c67x00_hcd_to_hcd()` convert between USB core HCD and private data.
- Prototypes expose `c67x00_hcd_probe/remove`, URB enqueue/dequeue, endpoint disable, scheduler kick/start/stop.
- `c67x00_hcd_dev()` returns the controller device for logging.

## Control Flow
The header has no executable control flow. It defines the shared contract between `c67x00-hcd.c`, the scheduler implementation, and the platform driver. Compile-time assertion checks that USB pipe constants range from 0 to 3 because the private state uses a four-entry pipe list indexed by pipe type.

## State And Persistence Behavior
All defined state is in-memory HCD state for one host-mode SIE. Bandwidth constants influence scheduler behavior but are not runtime-persistent.

## Dependencies And Integration Points
It includes USB HCD core headers and local `c67x00.h`. It is included by platform and HCD implementation files and must match scheduler expectations for TD memory and queue layout.

## Risks And Edge Cases
Bandwidth constants are tuning-sensitive and can trade bulk throughput against isochronous deadlines. The pipe-index assumption is enforced at compile time but would break if USB core pipe constants changed. TD/buffer address fields are 16-bit and tied to C67X00 internal memory limits.

## Test Signals
Compile with scheduler files to validate prototypes and pipe assertion. Stress isochronous and bulk transfers to verify bandwidth tuning. Use endpoint-disable tests to confirm completion behavior and queue cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/c67x00/c67x00-hcd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/c67x00/c67x00-ll-hpi.c -->
# sources/distributed-fs/ceph-client/drivers/usb/c67x00/c67x00-ll-hpi.c

## Purpose
`c67x00-ll-hpi.c` implements the low-level Host Port Interface access layer for Cypress C67X00 controllers. It serializes 16-bit register and memory access, handles mailbox/LCP command transactions, initializes HPI interrupt routing, controls host SIE state, resets ports, and reads/writes controller internal memory.

## Important APIs, Types, And Functions
- `hpi_read_reg()` and `hpi_write_reg()` perform raw HPI register access with the required 125 ns cycle delay.
- `hpi_read_word()`/`hpi_write_word()` and LE16 bulk helpers serialize indexed HPI address/data access under `dev->hpi.lock`.
- `c67x00_ll_hpi_status()`, `c67x00_ll_hpi_reg_init()`, `c67x00_ll_hpi_enable_sofeop()`, and `disable_sofeop()` manage HPI status/routing.
- `c67x00_comm_exec_int()` sends LCP software interrupts through communication registers and waits for mailbox completion.
- Host helpers include `c67x00_ll_husb_init_host_port()`, `reset()`, `reset_port()`, current TD get/set, frame get, USB status get/clear, and EOT setting.
- `c67x00_ll_write_mem_le16()` and `read_mem_le16()` handle aligned and unaligned controller memory transfers.
- `c67x00_ll_irq()` completes LCP mailbox waits on mailbox-out interrupts.

## Control Flow
Initialization sets up mutex/completion state, clears mailbox/status, disables IRQ routing, and clears SIE message registers. Higher layers issue reset or host-port commands through `c67x00_comm_exec_int()`, which writes command registers, sends a mailbox value, and waits up to five seconds for `c67x00_ll_irq()` to complete the transaction. Memory reads/writes use HPI address/data cycles and special-case unaligned first/last bytes.

## State And Persistence Behavior
Persistent runtime state includes HPI spinlock, LCP mutex, last mailbox message, and completion object inside the shared device. Hardware register state includes IRQ routing, host mode, current TD pointer, USB status, EOT, and controller memory contents. No disk persistence exists.

## Dependencies And Integration Points
The file depends on MMIO, delays, completions, mutexes, endian helpers, and C67X00 register definitions from local headers. It is the low-level backend for platform IRQ handling, HCD root-hub operations, and the transfer scheduler.

## Risks And Edge Cases
`BUG_ON(rc)` in host SIE init/reset paths can crash the kernel on LCP timeout. `ll_recv_msg()` warns and returns `-EIO` after timeout, but callers vary in recovery. The file assumes HPI register access is safe in IRQ context and explicitly excludes serial control interfaces. Memory write bounds only check writes beyond `0xffff`; reads do not perform the same explicit bound check. Correct locking between spinlock register access and LCP mutex is critical.

## Test Signals
Probe hardware and verify reset mailbox completion, HPI status clearing, SOF/EOP routing toggles, host port reset, TD pointer writes, frame reads, and unaligned memory read/write round trips. Fault-inject missing mailbox completion to observe timeout handling. Run IRQ-context status and SIE message fetch under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/c67x00/c67x00-ll-hpi.c -->
