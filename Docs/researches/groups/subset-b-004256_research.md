# subset-b-004256 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/eeprom/eeprom_93xx46.c -->
# sources/distributed-fs/ceph-client/drivers/misc/eeprom/eeprom_93xx46.c

## Purpose
SPI nvmem provider for 93xx46-family Microwire EEPROMs, covering 93c46, 93c56, 93c66, Atmel AT93C46D, and Microchip 93LC46B variants. It exposes the EEPROM through nvmem and, when writable, a sysfs-only whole-device erase trigger.

## Important APIs, Types, And Functions
`struct eeprom_93xx46_platform_data` carries data width, size, read-only flag, per-device quirks, and an optional select GPIO. `struct eeprom_93xx46_dev` holds the SPI device, nvmem config/device, address length, size, and mutex. `eeprom_93xx46_read()` and `eeprom_93xx46_write()` implement nvmem callbacks. `eeprom_93xx46_ew()` toggles erase/write enable, `eeprom_93xx46_write_word()` emits one byte or word write, and `eeprom_93xx46_eral()` performs erase-all. Probe parses `data-size`, `read-only`, `select-gpios`, and match-data quirks before registering nvmem.

## Control Flow
Probe builds platform data from firmware properties, computes byte size and address length, initializes nvmem callbacks, and optionally creates `erase`. Reads clamp the requested range, assert the select GPIO, send an OP_READ command/address transfer, receive data, delay for chip-select timing, and repeat for single-word-read variants. Writes clamp range, align 16-bit devices to even byte counts, enable writes, assert select, loop over words, disable writes, and return the first SPI error. The erase sysfs path parses a boolean and sequences EWEN, ERAL, EWDS.

## State, Persistence, And Dependencies
Persistent state is the EEPROM contents; driver state is only the mutex, geometry, quirks, and nvmem registration. It depends on SPI core, firmware property APIs, GPIO descriptors, nvmem-provider, delay helpers, and device-tree/SPI ID tables.

## Integration Points
Device tree compatibles and SPI IDs map to chip geometry and quirks. Consumers access data via nvmem; legacy users may see nvmem compatibility files. The `erase` attribute is writable only when the device is not read-only.

## Risks
All write and erase paths are destructive and guarded only by firmware read-only configuration plus root-only nvmem configuration. Offsets must match the configured 8-bit or 16-bit addressing mode. Single-word-read and extra-cycle quirks are timing-sensitive. SPI transfer `bits_per_word` is nonstandard and adapter support matters. The 6 ms fixed program/erase delay may be insufficient for slow parts or overly conservative for fast parts.

## Test Signals
Useful checks are probe success for each compatible, nvmem read boundary clamping, 16-bit write alignment, read-only suppression of write/erase, GPIO select transitions around transactions, SPI adapter behavior with unusual command bit widths, and erase/write/readback validation on hardware or an SPI EEPROM emulator.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/eeprom/eeprom_93xx46.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/eeprom/idt_89hpesx.c -->
# sources/distributed-fs/ceph-client/drivers/misc/eeprom/idt_89hpesx.c

## Purpose
I2C/SMBus slave-interface driver for IDT 89HPESx PCIe switches. It primarily exposes a switch-attached private EEPROM through a binary sysfs file and also exposes CSR debug access through debugfs for diagnostic reads and writes.

## Important APIs, Types, And Functions
`struct idt_89hpesx_dev` stores EEPROM geometry, EEPROM address/read-only state, initial command bits, current CSR address, selected SMBus read/write methods, mutex, client, and sysfs/debugfs handles. `struct idt_smb_seq`, `struct idt_eeprom_seq`, and `struct idt_csr_seq` describe the transport payloads. The `idt_smb_*` family implements byte, word, SMBus block, and I2C-block variants. `idt_eeprom_read()`, `idt_eeprom_write()`, `idt_csr_read()`, and `idt_csr_write()` provide higher-level operations. `idt_probe()` creates state, selects operations, verifies VID/DID, and creates user interfaces.

## Control Flow
Probe reads child firmware nodes for compatible 24c EEPROMs, EEPROM size, `reg`, and `read-only`, then chooses the fastest read/write operation supported by the adapter. It validates the switch by reading CSR 0 and checking the IDT PCI vendor ID. EEPROM sysfs reads and writes loop byte by byte through the switch SMBus command protocol. Writes read back every byte for verification. CSR debugfs writes parse either an address or address:value pair, validate 4-byte alignment and range, store the shifted CSR address, and optionally issue a CSR write; debugfs reads emit the current CSR address and value.

## State, Persistence, And Dependencies
Persistent state is external EEPROM content and switch CSR state. Driver state includes the current CSR address, the selected transport callbacks, and EEPROM access policy. It depends on I2C/SMBus functionality, firmware child-node parsing, PCI vendor IDs, sysfs bin attributes, debugfs, mutexes, and delay/retry behavior for busy EEPROMs.

## Integration Points
I2C IDs and OF compatibles cover many 89HPESx switch models. Child EEPROM compatible strings map to sizes for 24c32 through 24c512 devices. The sysfs `eeprom` file mirrors EEPROM size and read-only policy. Debugfs is under the I2C client debugfs directory using the client name.

## Risks
The driver performs byte-by-byte EEPROM writes and CSR debug writes from userspace, so misuse can corrupt switch configuration. Debugfs CSR writes are intentionally low-level and privileged. Retry loops hide transient NACKs but may still fail on persistent bus problems. Several SMBus methods cast unaligned byte arrays to `u16 *`, so architecture alignment assumptions matter. EEPROM offsets and counts are narrowed to `u16`, matching supported sizes but still worth boundary testing.

## Test Signals
Test adapter capability selection across byte, word, block, and I2C-block adapters; read-only sysfs mode; child-node parsing with default and custom EEPROM addresses; VID/DID rejection; EEPROM write/readback verification; CSR debugfs parsing failures; and behavior when the EEPROM reports busy or switch command bits report NAERR, LAERR, MSS, RERR, or WERR.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/eeprom/idt_89hpesx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/eeprom/m24lr.c -->
# sources/distributed-fs/ceph-client/drivers/misc/eeprom/m24lr.c

## Purpose
I2C driver for ST M24LR RFID/NFC EEPROM devices. It exposes EEPROM contents through nvmem and exposes the system parameter sector through sysfs attributes for UID, sector count, password update, unlock, and a binary `sss` area.

## Important APIs, Types, And Functions
`struct m24lr_chip` describes per-variant `sss_len`, `page_size`, and `eeprom_size`; `struct m24lr` holds UID, geometry, control and EEPROM regmaps, and a mutex. `m24lr_regmap_read()` and `m24lr_regmap_write()` retry transient failures until timeout. `m24lr_read()` and `m24lr_write()` dispatch to control or EEPROM regmap. `m24lr_nvmem_read()` and `m24lr_nvmem_write()` implement nvmem. Sysfs callbacks include `m24lr_ctl_sss_read/write()`, `new_pass_store()`, `unlock_store()`, `uid_show()`, and `total_sectors_show()`.

## Control Flow
Probe checks I2C capability, identifies chip data from OF/ID/ACPI, reads two `reg` cells, creates a dummy I2C client for EEPROM access, initializes one cached control regmap and one EEPROM regmap, registers nvmem, creates the `sss` binary sysfs file, then reads UID from register 2324 as a device sanity check. Reads and writes are serialized by `m24lr->lock`; writes are split at device page boundaries and retried to handle NACKs during internal write cycles.

## State, Persistence, And Dependencies
Persistent state includes EEPROM data, system security sector data, password state, lock state, and UID. Driver state is geometry, cached control regmap data, and global sysfs binary attribute configuration. Dependencies include I2C, regmap, nvmem-provider, device properties, OF matching, ACPI match data, and sysfs attribute groups.

## Integration Points
Compatible strings and I2C IDs cover `m24lr04e-r`, `m24lr16e-r`, and `m24lr64e-r`. Nvmem consumers bind to the EEPROM dummy client. Device sysfs attributes are attached through `dev_groups`; the `sss` binary file is created manually during probe and removed during remove.

## Risks
Control-sector and password writes are security-sensitive and only lightly validated. `m24lr_write()` uses `buf + offset` while also passing the device offset, which is suspicious for nonzero offsets because sysfs/nvmem buffers are normally relative to the request, not absolute device memory. The global `bin_attr_sss` is mutated per probe (`size` and `private`), making multiple devices risky. Timeout loops are fixed at 25 ms and may not match all parts.

## Test Signals
Exercise all variants, multiple instances, nonzero-offset nvmem writes, page-boundary writes, read/write timeout paths, sysfs `sss` bounds, UID read failure cleanup, password input parsing, dummy-client creation failure, and regmap cache behavior for volatile control registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/eeprom/m24lr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/eeprom/max6875.c -->
# sources/distributed-fs/ceph-client/drivers/misc/eeprom/max6875.c

## Purpose
I2C driver for MAX6874/MAX6875 devices that exposes the 512-byte user EEPROM region as a read-only binary sysfs file named `eeprom`. Register and configuration EEPROM regions are intentionally left for i2c-dev access.

## Important APIs, Types, And Functions
`struct max6875_data` stores a dummy odd-address client, update mutex, validity bitmap, cached EEPROM bytes, and per-slice timestamps. `max6875_update_slice()` refreshes one 16-byte slice from hardware. `max6875_read()` refreshes all slices covering a sysfs read and copies cached bytes to userspace. Probe validates SMBus functions, rejects odd addresses, creates the odd-address dummy client, initializes state, and creates the bin attribute.

## Control Flow
Probe only binds even I2C addresses because the chip responds to address pairs. It reserves the odd partner address with a dummy client. On sysfs read, the driver determines first and last 16-byte slices, calls `max6875_update_slice()` for each, then copies the requested range from the local cache. Slice update writes the 16-bit user-EEPROM address using `i2c_smbus_write_byte_data()`, then prefers SMBus block reads and falls back to byte reads.

## State, Persistence, And Dependencies
Persistent state is device EEPROM content. Runtime state is a 512-byte cache with a 32-bit valid bitmap and timestamps. Dependencies are I2C/SMBus byte write, byte read, optional block read, sysfs binary attributes, and a mutex.

## Integration Points
The I2C ID table contains `max6875`. The exposed sysfs ABI is a read-only `eeprom` bin file with size 512. The fake odd-address client prevents another driver from binding to the paired address.

## Risks
The file comment explicitly warns that the address-select operation is destructive if the driver binds to the wrong chip. The cache expiry check compares `jiffies` directly with `last_updated[slice]`, so slices become stale after the next tick rather than after a longer intended cache interval. If a slice refresh fails, the code still copies from the cache; invalid slices may return zeroed or stale data without propagating an error. Remove unregisters the dummy before removing sysfs, so a concurrent read during teardown would rely on core device removal serialization.

## Test Signals
Validate even-address-only binding, dummy-client reservation, block-read and byte-read fallback, partial reads crossing slice boundaries, failed address-select/read behavior, cache validity after repeated reads, and sysfs removal during device unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/eeprom/max6875.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/enclosure.c -->
# sources/distributed-fs/ceph-client/drivers/misc/enclosure.c

## Purpose
Generic Linux enclosure-services class implementation. It lets storage/enclosure drivers register an enclosure, publish component devices, link real devices to enclosure slots, and expose component state/control through sysfs.

## Important APIs, Types, And Functions
Exported APIs include `enclosure_find()`, `enclosure_for_each_device()`, `enclosure_register()`, `enclosure_unregister()`, `enclosure_component_alloc()`, `enclosure_component_register()`, `enclosure_add_device()`, and `enclosure_remove_device()`. Internal helpers manage sysfs link names, component name uniqueness, device release, and class/component attributes. Callback operations come from `struct enclosure_component_callbacks` in `linux/enclosure.h`.

## Control Flow
Module init registers the `enclosure` class. A provider calls `enclosure_register()` to allocate an enclosure device with a flexible component array, register it, initialize component sentinel values, and add it to a global list. Components are allocated by number, named uniquely, registered as child devices, and later linked to real devices. Sysfs getters call optional provider callbacks to refresh fields before emitting values. Setters parse userspace values and call optional callbacks. Unregister removes the enclosure from the global list, unregisters components, replaces callbacks with null callbacks, and unregisters the parent class device.

## State, Persistence, And Dependencies
State is in kernel objects only: global enclosure list, each enclosure component array, per-component status/fault/active/locate/power/type/slot fields, and sysfs links. Persistent hardware state lives behind provider callbacks. Dependencies include device core, sysfs, list/mutex primitives, module exports, and callback contracts from enclosure providers.

## Integration Points
The class appears under `/sys/class/enclosure`. Components expose `fault`, `status`, `active`, `locate`, `power_status`, `type`, and `slot`; enclosures expose `components` and optional `id`. Bidirectional sysfs links connect component class devices to real devices.

## Risks
`enclosure_for_each_device()` holds the global mutex across provider callbacks, so sleeping or reentrant callbacks can stall registration/removal. Several setters use `simple_strtoul()` and accept loose numeric input. Status/type arrays assume enum values are valid. Providers must manage callback lifetime carefully; unregister swaps callbacks late to prevent use-after-free after component removal starts. Duplicate component names are handled, but long names are truncated to 64 bytes before suffixing.

## Test Signals
Test duplicate component names, repeated add/remove of linked real devices, callback absence and callback error semantics, sysfs state parsing, reference release through device unregister, `enclosure_find()` iteration with start references, and unregister while userspace reads component attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/enclosure.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/fastrpc.c -->
# sources/distributed-fs/ceph-client/drivers/misc/fastrpc.c

## Purpose
Qualcomm FastRPC driver that exposes misc devices for userspace processes to invoke methods on remote DSP protection domains over rpmsg. It manages sessions, DMA buffers, dmabuf mappings, secure memory assignment, process creation, memory map/unmap RPCs, and DSP capability queries.

## Important APIs, Types, And Functions
Core state is split across `struct fastrpc_channel_ctx` for an rpmsg DSP domain, `struct fastrpc_session_ctx` for compute callbacks, `struct fastrpc_device` for misc nodes, and `struct fastrpc_user` for each open file. Invocation state lives in `struct fastrpc_invoke_ctx`; mapped buffers use `struct fastrpc_map`; driver-owned coherent buffers use `struct fastrpc_buf`. Main operations include `fastrpc_internal_invoke()`, `fastrpc_get_args()`, `fastrpc_put_args()`, `fastrpc_map_create()`, `fastrpc_req_mmap()`, `fastrpc_req_mem_map()`, process creation helpers, ioctl dispatch, rpmsg probe/remove/callback, and compute-callback platform probe/remove.

## Control Flow
Module init registers compute-callback and rpmsg drivers. Rpmsg probe reads the DSP domain label, reserved memory, VMIDs, secure-domain policy, SoC DMA settings, creates secure/non-secure misc devices, initializes IDR/list state, and populates child compute-callback nodes. Opening a misc device allocates a user, gets a channel reference, reserves an available session, and joins the channel user list. Ioctls create or attach DSP processes, allocate DMA buffers, invoke remote methods, map/unmap local or remote memory, and query DSP attributes. An invocation copies scalar descriptors from userspace, builds metadata/page lists, maps dmabufs or copies inline input into a coherent packet, sends an rpmsg, waits for callback completion, copies inline outputs back, handles returned fdlist references, and releases context state. Rpmsg callbacks look up context IDs and complete waiters.

## State, Persistence, And Dependencies
State is volatile: channel reference counts, IDR context IDs, pending invokes, per-user maps/mmaps, session allocation, cached DSP attributes, remote heap, and secure VM assignments. It depends on rpmsg, platform bus, device tree, reserved memory, DMA coherent allocation, dma-buf, scatterlists, qcom SCM hypervisor assignment, miscdevice, IDR, completions, and UAPI structs in `uapi/misc/fastrpc.h`.

## Integration Points
Device nodes are named `fastrpc-<domain>` and optionally `fastrpc-<domain>-secure`. DT labels select ADSP/MDSP/SDSP/CDSP/GDSP behavior. Compute callback children provide session devices and SIDs. Userspace interacts solely through FastRPC ioctls and returned dma-buf fds.

## Risks
This is a high-risk boundary: userspace pointers, dma-buf fds, remote DSP firmware, and hypervisor memory permissions all interact. Interrupted invokes keep contexts pending and move mmap buffers to a channel list. Secure map cleanup must return memory to HLOS; failures can leave permissions altered. Some error paths intentionally leak fds after failed `copy_to_user()` because fd installation already occurred. Session removal marks matching SIDs invalid and decrements counts, which needs care with duplicated sessions. Domain security policy must correctly reject unsigned/signed PD misuse.

## Test Signals
Test each ioctl success and failure path, interrupted invokes, rpmsg removal during pending invokes, secure and non-secure device access policy, dmabuf map/unmap reference counts, copy_from/to_user failures, DSP unsupported capability API, reserved-memory VM assignment, compute-callback session duplication, context ID reuse, and process release on file close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/fastrpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/gehc-achc.c -->
# sources/distributed-fs/ceph-client/drivers/misc/gehc-achc.c

## Purpose
SPI driver for GE Healthcare ACHC hardware that controls reset and firmware update of an attached NXP Kinetis device through its EzPort programming interface. It exposes sysfs controls for reset and firmware flashing.

## Important APIs, Types, And Functions
`struct achc_data` stores the main SPI device, ancillary EzPort SPI device, reset GPIO, and mutex. EzPort helpers implement reset sequencing, programming-mode entry/exit, status reads, write-enable, bulk/sector erase, flash transfer, flash compare, firmware-data flashing, and firmware loading. Sysfs callbacks are `update_firmware_store()` and `reset_show/store()`. Probe configures SPI mode/speed, creates the ancillary EzPort device from the second `reg` cell, and acquires reset GPIO.

## Control Flow
Probe sets conservative SPI parameters for the main device, allocates state, reads the EzPort chip-select value from DT, creates the ancillary device, registers cleanup, and requests reset GPIO. Writing `1` to `update_firmware` locks the device, enters programming mode by asserting chip select and resetting, requests `achc.bin`, erases as needed, programs in 2048-byte transfers with sector erase at 4 KiB boundaries, verifies by FAST_READ, soft-resets EzPort, exits programming mode, and unlocks. The reset sysfs attribute simply reads or drives the reset GPIO under the same mutex.

## State, Persistence, And Dependencies
Persistent state is firmware stored in target flash and reset line state. Driver state is the SPI devices, GPIO descriptor, and mutex. Dependencies include SPI core, ancillary SPI devices, firmware loader, GPIO descriptors, OF property parsing, sleep delays, and sysfs device groups.

## Integration Points
The OF compatible and SPI ID are `ge,achc`. The driver expects two `reg` entries so it can create an EzPort ancillary device. Firmware is loaded by name `achc.bin` through the kernel firmware search path. Sysfs attributes are attached via driver `dev_groups`.

## Risks
Firmware update is destructive and has no version or image validation beyond readback comparison. Secure EzPort mode can block verification; flashing treats `-EACCES` from verification as acceptable. Bulk erase may be triggered when flash security is set. Fixed delays and retry counts may not suit all target revisions. The update path holds a device mutex for the entire firmware operation, blocking reset access.

## Test Signals
Test missing second `reg`, ancillary creation cleanup, reset GPIO polarity, firmware request failure, write-enable timeout, sector alignment rejection, secure-mode behavior, verification mismatch, soft-reset warning path, and concurrent reset/update sysfs accesses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/gehc-achc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/genwqe/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/misc/genwqe/Kconfig

## Purpose
Kconfig entry for the IBM GenWQE PCIe accelerator driver and its platform recovery option.

## Important APIs, Types, And Functions
`menuconfig GENWQE` controls whether the GenWQE driver is built as disabled/built-in/module. It depends on `PCI` and `64BIT` and selects `CRC_ITU_T`. `config GENWQE_PLATFORM_ERROR_RECOVERY` controls whether the driver attempts platform recovery procedures, defaulting to enabled on PPC64 and disabled elsewhere.

## Control Flow
The build system includes the GenWQE objects when `CONFIG_GENWQE` is enabled. `CONFIG_GENWQE_PLATFORM_ERROR_RECOVERY` is consumed by `card_base.c` to initialize `cd->use_platform_recovery`, which changes fatal health-monitor behavior by attempting platform/fundamental reset recovery before giving up.

## State, Persistence, And Dependencies
No runtime state is stored here. It defines compile-time dependencies and defaults. The `CRC_ITU_T` selection supports code in the broader GenWQE module, and `PCI && 64BIT` reflects hardware and DMA assumptions.

## Integration Points
The help text points users to `include/linux/genwqe/genwqe_card.h` for the userspace interface. The platform recovery integer is surfaced indirectly through driver behavior and can be overridden at runtime through driver debugfs state in `struct genwqe_dev`.

## Risks
Non-PPC64 defaults disable platform recovery, so fatal MMIO failures may require external unbind/rebind or PCI recovery. Enabling a PCI accelerator driver with a world-writable device node has security implications handled elsewhere, not in Kconfig.

## Test Signals
Validate build combinations for `GENWQE=m`, `GENWQE=y`, disabled PCI, non-64-bit targets, PPC64 default recovery, and non-PPC default recovery. Confirm `CRC_ITU_T` is selected when the driver builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/genwqe/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/genwqe/Makefile -->
# sources/distributed-fs/ceph-client/drivers/misc/genwqe/Makefile

## Purpose
Build recipe for the GenWQE driver module.

## Important APIs, Types, And Functions
`obj-$(CONFIG_GENWQE) := genwqe_card.o` makes the module conditional on Kconfig. `genwqe_card-objs` composes the module from `card_base.o`, `card_dev.o`, `card_ddcb.o`, `card_sysfs.o`, `card_debugfs.o`, and `card_utils.o`.

## Control Flow
When `CONFIG_GENWQE` is enabled, Kbuild links the listed object files into one `genwqe_card` module or built-in object. `card_base.o` supplies module init/exit and PCI driver registration, while the other objects supply character device, DDCB queue, sysfs, debugfs, and utility support.

## State, Persistence, And Dependencies
No runtime state is stored here. The Makefile encodes intra-driver composition, so missing objects or renamed source files break the complete module.

## Integration Points
This file integrates with `drivers/misc` Kbuild and the `GENWQE` Kconfig symbol. The module name and object grouping must stay consistent with `MODULE_*` metadata and exported internal symbols across GenWQE source files.

## Risks
Object order can matter for initcall and symbol resolution only indirectly, but removing `card_base.o` would remove module entry points. The Makefile assumes all listed C files are present in the same directory.

## Test Signals
Run kernel build checks with `CONFIG_GENWQE=m` and `CONFIG_GENWQE=y`; verify `genwqe_card.ko` contains all expected objects and no unresolved internal GenWQE symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/genwqe/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/genwqe/card_base.c -->
# sources/distributed-fs/ceph-client/drivers/misc/genwqe/card_base.c

## Purpose
Core GenWQE PCI driver implementation. It owns module initialization, PCI probe/remove, BAR/DMA setup, card start/stop, character-device creation orchestration, health monitoring, fatal error recovery, FFDC buffer allocation, SR-IOV configuration, and PCI error handling.

## Important APIs, Types, And Functions
Global state includes `genwqe_devices[]`, the GenWQE class, and debugfs root. Key functions are `genwqe_dev_alloc/free()`, `genwqe_pci_setup/remove()`, `genwqe_start/stop()`, `genwqe_recover_card()`, `genwqe_health_thread()`, `genwqe_fir_checking()`, `genwqe_bus_reset()`, `genwqe_platform_recovery()`, `genwqe_reload_bistream()`, PCI error callbacks, `genwqe_sriov_configure()`, and module init/exit.

## Control Flow
Module init registers the class, creates debugfs root, and registers the PCI driver. Probe initializes CRC support, allocates a card slot, enables PCI memory, requests BARs, sets DMA mask, maps BAR0, reads hardware IDs, starts service-layer queues, applies hardware tweaks, configures PF/VF job timers, creates the char device, and starts the health thread for privileged functions. Stop tears down queues, device nodes, service layer, SR-IOV, and FFDC. The health thread periodically reads GFIR and unit registers, logs/clears informational FIRs, recovers fatal conditions via bus reset or platform recovery, and handles requested bitstream reload.

## State, Persistence, And Dependencies
Driver state is `struct genwqe_dev`: card index, state, MMIO pointer, cached unit IDs, FFDC buffers, queue and health threads, device/class/cdev data, debugfs, VF timeout settings, open-file list, and recovery knobs. Persistent hardware state includes card bitstream, FIR/GFIR registers, queues, and PCI function state. Dependencies include PCI core, DMA API, kthreads, wait queues, debugfs, class/cdev helpers from sibling files, service-layer/DDCB code, and architecture PCI error recovery.

## Integration Points
The PCI ID table covers IBM GenWQE PF/VF variants. Internal calls integrate with `card_dev.c`, `card_ddcb.c`, `card_sysfs.c`, `card_debugfs.c`, and `card_utils.c`. Kconfig controls platform recovery. Userspace observes device creation/removal under the GenWQE class and debugfs tuning/diagnostic files.

## Risks
Recovery paths deliberately tear down and recreate devices while open files may exist, so async notification and forced close behavior in sibling code is critical. Health monitoring uses raw MMIO and must distinguish fatal `IO_ILLEGAL_VALUE` from informational FIRs. Bus reset temporarily unmaps BARs and assumes later remapping succeeds. SR-IOV and PF/VF privilege detection depend on hardware register accessibility. The device node default mode is `0666`, making userspace ABI hardening important.

## Test Signals
Test PCI probe/remove, DMA32 fallback, BAR mapping failure, nonprivileged VF operation, PF health-thread recovery, injected hardware/bus/GFIR failures, platform recovery enabled/disabled, PCI AER callbacks, SR-IOV enable/disable, bitstream reload request, FFDC allocation failures, and repeated stop after failed recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/genwqe/card_base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/genwqe/card_base.h -->
# sources/distributed-fs/ceph-client/drivers/misc/genwqe/card_base.h

## Purpose
Private GenWQE module header defining shared constants, core state structures, request/mapping types, and cross-file function prototypes used by the GenWQE driver implementation.

## Important APIs, Types, And Functions
Important definitions include PCI IDs, card limits, DDCB timeout defaults, debug unit IDs, FFDC structures, error-injection flags, `struct dma_mapping`, `struct ddcb_queue`, `struct genwqe_dev`, `struct genwqe_sgl`, `struct ddcb_requ`, and `struct genwqe_file`. Inline helpers include `genwqe_mapping_init()`, `genwqe_get_slu_id()`, `dma_mapping_used()`, and `genwqe_is_privileged()`. Prototypes cover service-layer setup, DDCB execution, char-device creation, debugfs, FFDC reads, register access, DMA allocation, SGL setup, CRC, app ID, and trap control.

## Control Flow
This file does not execute control flow directly, but it defines the lifecycle contracts used by `card_base.c` and sibling files. A `genwqe_dev` is allocated at PCI probe, populated by PCI setup, used by service-layer and char-device code, monitored by the health thread, and freed at remove. `ddcb_requ` and `ddcb_queue` model request submission, queue slots, wait queues, and completion state for DDCB execution. `genwqe_file` tracks per-open mappings and async notification.

## State, Persistence, And Dependencies
The header describes all major volatile GenWQE state: MMIO, FFDC buffers, DDCB queue, health/card threads, cdev/class/debugfs handles, VF settings, cached register values, open files, and DMA mappings. Persistent state is hardware-owned and accessed through the declared register and DDCB helpers. Dependencies include PCI, cdev, semaphores, uaccess, I/O accessors, debugfs, Linux GenWQE UAPI, and local `genwqe_driver.h`.

## Integration Points
Every GenWQE object file depends on this header for shared structure layout. It bridges kernel-private implementation with public `include/linux/genwqe/genwqe_card.h` UAPI structures. Function prototypes make `card_base.c` the lifecycle owner while delegating DDCB, device, sysfs/debugfs, utilities, and memory mapping.

## Risks
Because this is a private shared header, structure layout changes can silently break assumptions across GenWQE source files. DMA mapping state must be kept consistent across map, pin, execute, and cleanup paths. Comments describe fragile recovery behavior when user file descriptors survive device teardown. Error-injection flags are useful for tests but dangerous if exposed without proper privilege checks.

## Test Signals
Compile coverage is the main signal: all GenWQE objects should build after structure/prototype changes. Runtime tests should cover DDCB request state transitions, DMA mapping lifecycle, open-file cleanup, FFDC buffer sizing, privilege detection, and all callers of declared register accessors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/genwqe/card_base.h -->
