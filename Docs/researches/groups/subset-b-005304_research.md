# subset-b-005304 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mesh.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/mesh.c

## Purpose
`mesh.c` is the Linux SCSI low-level driver for the Macintosh Enhanced SCSI Hardware controller found in old Power Macintosh systems. It binds a `macio` Open Firmware device, maps the MESH register block and its DBDMA engine, initializes and optionally resets the SCSI bus, queues SCSI mid-layer commands, drives a SCSI phase/message state machine, builds DBDMA descriptor lists for data transfer, handles reselection and synchronous-transfer negotiation, and exposes suspend/resume, shutdown, remove, and module registration paths.

## Important APIs, Types, And Functions
The driver-private runtime model is `struct mesh_state`, which stores MMIO register pointers, IRQs, the owning `Scsi_Host`, request queue links, current bus phase, message buffers, current target, DMA command memory, per-target state, and `macio`/PCI device pointers. Per-target state is in `struct mesh_target`, with SDTR state, negotiated sync parameters, saved data pointer, direction guess, and disconnected command pointer.

SCSI mid-layer entry points are collected in `mesh_template`: `mesh_queue`, `mesh_abort`, and `mesh_host_reset`, with `can_queue = 20`, host ID 7, `SG_ALL`, `cmd_per_lun = 2`, `max_segment_size = 65535`, and `cmd_size = sizeof(struct mesh_cmd_priv)`.

Lifecycle and platform integration are handled by `mesh_probe()`, `mesh_remove()`, `mesh_shutdown()`, optional `mesh_suspend()`/`mesh_resume()`, `set_mesh_power()`, `init_mesh()`, `exit_mesh()`, `mesh_match`, and `mesh_driver`.

Core command flow is split across `mesh_queue_lck()`, `mesh_start()`, `mesh_start_cmd()`, `start_phase()`, `mesh_interrupt()`, `cmd_complete()`, `phase_mismatch()`, `handle_error()`, `handle_exception()`, `handle_msgin()`, `reselected()`, `mesh_done()`, and reset/recovery helpers `handle_reset()`, `do_abort()`, and `mesh_host_reset()`.

DMA setup and teardown are implemented by `set_dma_cmds()` and `halt_dma()`. Sync-transfer negotiation is implemented by `add_sdtr_msg()` and `set_sdtr()`. Diagnostics are provided by `mesh_dump_regs()` and conditional `MESH_DBG` logging helpers.

## Control Flow
Module initialization clamps `sync_rate`, translates it into `mesh_sync_period` and `mesh_sync_offset`, then registers `mesh_driver` with the macio bus. Probe validates two resources and two IRQs, requests resources, allocates a SCSI host with `struct mesh_state` hostdata, maps controller and DBDMA register windows, allocates coherent DBDMA command memory, initializes all target negotiation state to asynchronous/`do_sdtr`, reads `clock-frequency` from the device tree or assumes 50 MHz, powers up the chip, calls `mesh_init()`, requests the MESH interrupt, registers the SCSI host, and scans.

`mesh_init()` stops DBDMA, clears hardware exception/error bits, resets the controller, programs interrupt masks, source ID, selection timeout, and async sync parameters, optionally asserts SCSI RST for `init_reset_delay`, flushes the FIFO, enables reselection, and returns the software phase machine to idle.

Command submission enters `mesh_queue_lck()` with the SCSI host lock held. The command is appended to the driver's singly linked `request_q` through `cmd->host_scribble`; if the bus is idle, `mesh_start()` chooses the first queued command whose target has no active/disconnected request. `mesh_start_cmd()` initializes transfer counters and message state, records target direction and current request, handles a busy bus or pending reselection, disables reselection around arbitration to avoid a known MESH race, starts `SEQ_ARBITRATE`, and applies a controller reset workaround if arbitration appears hung during a target reselection.

The phase machine starts at selection and advances through message-out, command, data, status, message-in, bus-free, and disconnect states. `start_phase()` translates the current software phase into MESH sequence commands and register writes: select with ATN, push CDB bytes into the FIFO, build and run DBDMA descriptors for data phases, fetch status, send or receive messages, or wait for bus free. `cmd_complete()` consumes command-done interrupts and either continues fragmented message I/O, records status from the FIFO, halts DMA when a data chunk finishes, moves to the next phase, completes disconnected commands, or starts the next queued command after bus free.

`phase_mismatch()` is the adaptive branch of the state machine. It samples SCSI bus phase bits, drains message-in bytes when needed, halts DMA on phase change, flushes residual FIFO data, updates direction on data phases, sends pending messages, and restarts the appropriate hardware sequence. Message handling supports command complete, SDTR negotiation and reject fallback, save/restore pointers, disconnect, abort, NOP, and identify messages on reselection.

Interrupt handling loops while the MESH interrupt register is nonzero. Error interrupts take precedence, then exceptions, then command-done. SCSI reset errors complete all active and queued commands with `DID_RESET` and reset target negotiation. Unexpected disconnect maps to `DID_ABORT` unless it is actually a reselection. Parity errors either request message parity retry or set `DID_PARITY`. Sequence errors can be converted into reselection or phase-mismatch handling when hardware reports those conditions. Exceptions handle reselection, arbitration loss, selection timeout, phase mismatch, and unknown conditions by aborting.

Reselection can happen from idle, arbitration, bus-free, or disconnecting states. The driver may requeue the command that lost arbitration, extracts the target ID from FIFO reselection data, restores the target's current command and saved data pointer, programs negotiated sync parameters, then resumes with message-in. Bogus reselection data or missing commands force an abort message path.

## State And Persistence
The driver has no filesystem persistence. Module parameters (`sync_rate`, `sync_targets`, `resel_targets`, `debug_targets`, and `init_reset_delay`) tune runtime behavior at load time. Hardware state is programmed into volatile MESH, DBDMA, and SCSI-bus registers; sync negotiation and target state are rebuilt after reset, resume, or module reload.

`struct mesh_state` persists for the lifetime of the macio device binding and owns the command queue, current request, phase machine, message buffers, DMA command allocation, and target array. `struct mesh_target` persists per target and keeps a disconnected command pointer plus `saved_ptr` for save/restore pointer messages. `struct mesh_cmd_priv` is allocated by the SCSI core per command and records residual, status, and message values that are copied into the final `scsi_cmnd` result in `mesh_done()`.

The request queue reuses `scsi_cmnd.host_scribble`; this means no other layer may depend on that field while the command is queued in this driver. DMA state is transient: `set_dma_cmds()` maps the SCSI SG list with `scsi_dma_map()`, writes DBDMA descriptors, and `halt_dma()` updates `data_ptr` and unmaps with `scsi_dma_unmap()`.

## Dependencies And Integration Points
The file depends on Linux SCSI mid-layer APIs, macio/Open Firmware device matching, PowerMac feature control, PCI DMA coherent allocation, DBDMA register definitions from `<asm/dbdma.h>`, I/O accessors (`in_8`, `out_8`, `in_le32`, `out_le32`), IRQ handling, spinlocks, sleep/delay helpers, and PowerMac platform detection. It includes `mesh.h` for register layout, sequence bits, bus phase constants, interrupt/error bits, and command-private state.

The macio core calls probe/remove/shutdown and power-management callbacks. The SCSI core calls queue, abort, and host reset handlers and owns host locking around queued commands. The IRQ core calls `do_mesh_interrupt()`, which takes `host_lock` before running the phase machine. Platform firmware provides `clock-frequency` and resources/IRQs through the OF node.

## Risks And Edge Cases
The driver has many hardware-specific timing loops and microsecond waits. Arbitration, message-out ATN timing, reselection, FIFO drain, and SCSI reset behavior rely on old MESH quirks and fixed delays; small ordering changes can break legacy hardware.

`set_dma_cmds()` uses `BUG_ON(nseg < 0)` for DMA mapping failure and panics if any SG element is at least 64 KiB, so resource pressure or unexpected SG geometry can crash the kernel instead of failing a command. The DBDMA descriptors store 32-bit physical addresses and use `virt_to_phys()` for command pointer programming and the static overrun buffer, making architecture/DMA assumptions important.

Queueing relies on `cmd->host_scribble` and host-lock serialization. Any future path touching the queue without the SCSI host lock risks list corruption. Abort handling is explicitly incomplete and always returns `FAILED`, so recovery escalates to host reset.

The data pointer can be modified by target messages, halted DMA residue, and overrun fallback buffers. Incorrect accounting can produce wrong residuals, duplicate unmaps, or resumed disconnected transfers at the wrong SG offset.

Shutdown and probe-error paths reset the SCSI bus to avoid leaving devices in synchronous mode for MacOS. This is intentional but disruptive; error injection around probe can reset shared devices on the bus.

## Test Signals
Build coverage should include `CONFIG_SCSI_MESH`, `CONFIG_PM`, and PowerPC/macintosh platform headers to validate macio, DBDMA, and SCSI API compatibility. Probe tests on supported Open Firmware nodes should verify two resources/two IRQs, register mapping, coherent DBDMA allocation, IRQ request, SCSI host registration, and resource cleanup at every failure label.

I/O testing should cover no-data commands, reads, writes, multi-segment SG lists under 64 KiB per element, residual accounting, disconnect/reselection with save/restore pointer messages, and selection timeouts. Negotiation tests should cover async mode, successful SDTR, rejected SDTR, target masks from `sync_targets` and `resel_targets`, and bus reset resetting all target sync state. Recovery tests should induce parity errors, unexpected disconnects, sequence errors, phase mismatches, arbitration loss, host reset, suspend/resume, shutdown, and module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mesh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mesh.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/mesh.h

## Purpose
`mesh.h` is the private hardware contract for the PowerMac MESH SCSI driver in `mesh.c`. It defines per-command private result storage, the memory-mapped MESH register layout, sequence-register commands, SCSI bus signal bits, bus phase encodings, exception/error/interrupt bits, and synchronous-transfer parameter helpers.

## Important APIs, Types, And Macros
`struct mesh_cmd_priv` stores the command residual counter, SCSI message byte, and status byte that `mesh.c` later folds into `struct scsi_cmnd.result`. `mesh_priv()` wraps `scsi_cmd_priv()` and depends on the SCSI host template's `cmd_size` matching `sizeof(struct mesh_cmd_priv)`.

`struct mesh_regs` maps the sparse MESH register file: count low/high, FIFO, sequence, bus status registers, FIFO count, exception, error, interrupt mask, interrupt status, initiator source ID, destination ID, sync parameters, chip ID, and selection timeout. Each visible register is separated by 15 padding bytes, matching the controller's MMIO spacing.

`SEQ_*` macros encode hardware sequence commands and modifiers. `SEQ_DMA_MODE`, `SEQ_TARGET`, `SEQ_ATN`, and `SEQ_ACTIVE_NEG` are command modifiers, while low-nibble commands include arbitration, select, command, status, data in/out, message in/out, bus-free wait, parity enable/disable, reselection enable/disable, controller reset, and FIFO flush.

`BS0_*` and `BS1_*` represent SCSI bus control/status signals. `BP_*` macros derive SCSI phase values from `BS0_MSG`, `BS0_CD`, and `BS0_IO`. `EXC_*`, `ERR_*`, and `INT_*` define exception, error, and interrupt bits consumed by `mesh.c` interrupt handlers. `SYNC_OFF()`, `SYNC_PER()`, `SYNC_PARAMS()`, and `ASYNC_PARAMS` encode the MESH sync parameter register.

## Control Flow
The header has no independent executable flow beyond `mesh_priv()`. Its constants directly drive `mesh.c`: probe and reset write `SEQ_RESETMESH`, `SEQ_FLUSHFIFO`, `SEQ_ENBRESEL`, source ID, selection timeout, and `ASYNC_PARAMS`; command start uses `SEQ_ARBITRATE`, `SEQ_SELECT`, and `SEQ_DISRESEL`; data phases combine `SEQ_DATAIN`/`SEQ_DATAOUT` with `SEQ_DMA_MODE`; message timing uses `SEQ_MSGIN`, `SEQ_MSGOUT`, and `SEQ_ATN`; interrupt dispatch reads `INT_ERROR`, `INT_EXCEPTION`, and `INT_CMDDONE`; phase mismatch dispatch compares `BP_DATAIN`, `BP_DATAOUT`, `BP_COMMAND`, `BP_STATUS`, `BP_MSGOUT`, and `BP_MSGIN`.

## State And Persistence
The structures describe volatile kernel and device state only. `struct mesh_regs` is an MMIO view and must not be copied as persistent memory. `struct mesh_cmd_priv` persists only for one SCSI command lifetime and is allocated by the SCSI core as command-private storage. The sync parameter macros encode negotiated target state kept in `struct mesh_target` in `mesh.c`, not on disk.

## Dependencies And Integration Points
The header assumes the including file has declarations for `struct scsi_cmnd` and `scsi_cmd_priv()`, which `mesh.c` gets from SCSI headers. It is private to the MESH driver and is tied to PowerMac MESH hardware rather than a UAPI. The register and bit definitions are consumed through PowerPC I/O helpers in `mesh.c`.

## Risks And Edge Cases
The sparse `struct mesh_regs` layout is ABI-sensitive. Any packing, padding, type-width, or ordering change would shift MMIO offsets and break hardware access. Register fields are declared as byte-sized C objects rather than accessor functions, so users must continue to use correct MMIO read/write helpers and ordering flushes.

The sync parameter comments assume a 50 MHz clock for their explanatory timing; `mesh.c` recalculates periods from device-tree `clock-frequency`, so future code should not hard-code the comment's example. `ASYNC_PARAMS` is a magic hardware value and must stay aligned with MESH expectations.

## Test Signals
Compile-time validation should confirm that `mesh_template.cmd_size` still matches `struct mesh_cmd_priv`, that `struct mesh_regs` offsets match hardware documentation, and that every bus phase and interrupt/error bit is exercised by `mesh.c` probe, reset, command, data, message, exception, and recovery tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mesh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/Kconfig

## Purpose
This Kconfig fragment declares the build-time option for the Broadcom MPI3 Storage Controller driver. `CONFIG_SCSI_MPI3MR` controls whether the `mpi3mr` SCSI/RAID controller driver is omitted, built in, or built as a module.

## Important APIs, Types, And Functions
The only symbol is `config SCSI_MPI3MR`, a tristate prompt named "Broadcom MPI3 Storage Controller Device Driver". It depends on `PCI` and `SCSI`, selects `BLK_DEV_BSGLIB` for block/scatter-gather helper support, and selects `SCSI_SAS_ATTRS` for SAS transport/sysfs attributes.

## Control Flow
Kconfig evaluation exposes this option only when PCI and SCSI support are enabled. If the user or defconfig enables it, the symbol value is consumed by the local Makefile through `obj-$(CONFIG_SCSI_MPI3MR) += mpi3mr.o`, which controls compilation and module/built-in linkage.

## State And Persistence
The selected value is persisted in the kernel build configuration, normally `.config`, and determines whether the driver is available in the resulting kernel/module set. It does not manage runtime device state itself.

## Dependencies And Integration Points
The option integrates with the kernel SCSI driver menu, PCI subsystem, SCSI core, block BSG library, SAS transport attributes, and the `drivers/scsi/mpi3mr/Makefile`. The help text identifies supported hardware as MPI3-based Storage and RAID controllers.

## Risks And Edge Cases
Because `SCSI_SAS_ATTRS` is selected unconditionally, builds that enable the driver also pull in SAS transport attribute support even for deployments focused on PCIe/NVMe controller personalities. Missing `PCI` or `SCSI` hides the option completely, so defconfigs for this hardware must enable those parents.

## Test Signals
Configuration tests should verify `n`, `m`, and `y` builds where applicable; that enabling `SCSI_MPI3MR` selects `BLK_DEV_BSGLIB` and `SCSI_SAS_ATTRS`; and that the resulting object linkage follows the Makefile for built-in and module builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/Makefile -->
# sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/Makefile

## Purpose
This Makefile describes how the Broadcom MPI3MR SCSI driver is built from its implementation objects and connected to `CONFIG_SCSI_MPI3MR`.

## Important APIs, Types, And Functions
`obj-$(CONFIG_SCSI_MPI3MR) += mpi3mr.o` makes `mpi3mr.o` part of the kernel or module build when the Kconfig symbol is enabled. `mpi3mr-y` lists the component objects linked into that composite object: `mpi3mr_os.o`, `mpi3mr_fw.o`, `mpi3mr_app.o`, and `mpi3mr_transport.o`.

## Control Flow
During kbuild, the value of `CONFIG_SCSI_MPI3MR` determines whether `mpi3mr.o` is built. The `mpi3mr-y` variable tells kbuild to first compile the OS-facing, firmware, application/control, and transport portions, then link them into the single driver object.

## State And Persistence
The Makefile has no runtime state. Its persistent effect is build graph membership: the same object composition is used every time the driver is enabled until the source tree changes.

## Dependencies And Integration Points
The file integrates with the SCSI driver's Kconfig symbol and kbuild composite-object conventions. It assumes the listed source files exist in the same directory and are responsible for consuming the MPI headers under `mpi/`.

## Risks And Edge Cases
Adding a new source file without updating `mpi3mr-y` would compile cleanly only if no referenced symbols are needed, but new functionality would be absent. Renaming one of the four listed implementation files requires this Makefile to change in lockstep. Because the build is a single composite object, duplicate global symbols across the component files surface at final driver link time.

## Test Signals
Useful checks are `CONFIG_SCSI_MPI3MR=m` module builds, `CONFIG_SCSI_MPI3MR=y` built-in builds, clean incremental rebuilds after touching each component source, and link validation that all symbols used across OS, firmware, app, and transport components resolve into `mpi3mr.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/mpi/mpi30_cnfg.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/mpi/mpi30_cnfg.h

## Purpose
`mpi30_cnfg.h` defines the MPI 3.0 configuration-page wire ABI used by the Broadcom `mpi3mr` driver and controller firmware. It provides config request and page header structures, page type/action/address constants, common SAS/PCIe link encodings, manufacturing pages, IO unit pages, IOC pages, driver policy pages, security pages, SAS topology pages, PCIe topology pages, enclosure pages, and device pages.

## Important APIs, Types, And Functions
The top-level request/response contract is `struct mpi3_config_request`, which carries a host tag, MPI function, change count, proxy IOC number, page version/number/type, action, page address, page length, and one SGE for the page buffer. `struct mpi3_config_page_header` prefixes each config page with version, number, attribute, length, and type.

Config selectors include `MPI3_CONFIG_PAGETYPE_*`, `MPI3_CONFIG_PAGEATTR_*`, and `MPI3_CONFIG_ACTION_*`. Page-address forms cover device handles, SAS expander handle/phy combinations, SAS phy numbers, SAS ports, enclosure handles, PCIe switch handles/ports, PCIe links, security slots, and generic instances.

Manufacturing pages `mpi3_man_page0` through `mpi3_man_page21` and `mpi3_man_page_product_specific` describe board identity, VPD, tracer data, WWIDs, GPIOs, receptacles, phy-to-slot maps, resource limits, ISTWI controllers/devices, SGPIO LED patterns, slot-status translation, certificate/SPDM/hash capabilities, licensed personalities, and OEM policies.

IO unit pages `mpi3_io_unit_page0` through `mpi3_io_unit_page19` describe NVDATA versions, write-cache and device-missing-delay policy, GPIO values, thermal thresholds/current temperatures, spin-up groups, power requirements, secure boot/current key digests, first-device ordering, firmware/silicon identifiers, profile limits, interrupt coalescing buckets, function/page access restrictions, power budgeting, current keys, direct-attached temperature polling, and per-device temperatures.

IOC pages `mpi3_ioc_page0` through `mpi3_ioc_page2` expose PCI identity, interrupt coalescing, and event masks. Driver pages `mpi3_driver_page0`, `mpi3_driver_page1`, `mpi3_driver_page2`, `mpi3_driver_page10`, `mpi3_driver_page20`, and `mpi3_driver_page30` define BIOS/driver policy, diagnostic buffer sizing, diagnostic triggers, and allowed SCSI/ATA/NVMe command lists.

Security pages define MAC/nonce/root digest/certificate/key storage through `mpi3_security_page0`, `mpi3_security_page1`, `mpi3_security_page2`, `mpi3_security_page3`, `mpi3_security_page10`, `mpi3_security_page11`, and `mpi3_security_page12`. SAS pages describe IO unit phys, expander pages, ports, phys, phy counters/events, event configuration, and initial frames. PCIe pages describe IO unit links, switch pages, link counters, ASPM, clock/reset override, and recovery actions. Device pages `mpi3_device_page0` and `mpi3_device_page1` describe SAS/SATA, PCIe/NVMe, and virtual-drive device identities and counters through form-specific unions.

## Control Flow
This header has no executable control flow. Runtime config flow in the driver builds `mpi3_config_request`, selects an action such as page-header read, current read, persistent read, current write, or persistent write, fills page address fields with the corresponding `*_PGAD_*` form, DMA maps a page buffer described by the SGE, and interprets the returned page by casting it to the matching struct and checking its page-version and bitfields.

The struct layout determines how the driver enumerates topology: get-next-handle forms walk device, enclosure, SAS expander, PCIe switch, and link pages; per-phy/per-port address forms select detailed SAS or PCIe link pages; driver and IO unit pages configure policy; security pages select certificate/key slots; and device page unions are decoded according to `device_form`.

## State And Persistence
The header describes firmware/controller state rather than local kernel state. Config actions distinguish defaults, current volatile settings, and persistent settings stored by the controller. Pages marked changeable or persistent can affect controller behavior beyond one request, while read-only pages expose hardware, topology, capability, and telemetry state.

Variable-length arrays use default maximum macros such as `MPI3_MAN*_MAX`, `MPI3_IOUNIT*_MAX`, `MPI3_SAS_*_MAX`, and `MPI3_PCIE_*_MAX`, often defaulting to 1 unless overridden before inclusion. Runtime page lengths in the header must be used to size buffers correctly when the firmware reports more entries than the compile-time default shape.

## Dependencies And Integration Points
The header depends on Linux fixed-width little-endian types (`__le16`, `__le32`, `__le64`) and MPI common definitions such as `union mpi3_sge_union` and `union mpi3_version_union` from other MPI headers included by the driver. It integrates with `mpi3mr` firmware-management code, topology discovery, SAS transport exposure, PCIe/NVMe device handling, enclosure/slot management, diagnostics, security/certificate management, and application or ioctl paths that expose controller configuration.

## Risks And Edge Cases
This is a firmware ABI surface: field ordering, endian annotations, lengths, and numeric constants must match the controller specification exactly. Any local refactor that changes struct layout or maximum-array assumptions can corrupt DMA buffers or misinterpret firmware data.

Many pages contain flexible arrays or compile-time placeholder maxima. Code must trust returned page lengths and allocate enough memory before reading full pages; using `sizeof(struct page)` with a default max of 1 can silently truncate multi-entry pages. Conversely, unvalidated firmware counts can lead to out-of-bounds parsing if consumers ignore allocated length.

Persistent-write actions can alter controller NVDATA, device exposure, security keys, access policy, power behavior, or topology configuration. Driver code must separate read-only discovery from current/persistent mutation and should gate security and policy writes carefully.

Several fields are masks and shifts over packed values for access status, link rates, ASPM, RAID state, PI capability, recovery reasons, and command blocking. Misapplying masks across SAS, PCIe, and virtual-device forms can expose the wrong queue depth, block devices incorrectly, or mishandle degraded/hidden/unauthorized devices.

## Test Signals
Build tests should validate all structs under endian type checking and all consuming code after MPI header updates. ABI tests should compare key struct sizes, offsets, page numbers, page versions, and constants against vendor specification or firmware traces. Runtime tests should read page headers and full pages for manufacturing, IO unit, IOC, driver, SAS, PCIe, enclosure, and device pages; enumerate get-next handles; parse variable-length arrays; validate persistent/current/default action separation; exercise event-mask and coalescing settings; and verify SAS transport and PCIe/NVMe device attributes derived from these pages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/mpi/mpi30_cnfg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/mpi/mpi30_image.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/mpi/mpi30_image.h

## Purpose
`mpi30_image.h` defines the MPI 3.0 firmware/component image metadata ABI for Broadcom controllers. It describes component image headers, package/component manifests, secure-boot manifest elements, extended image headers, supported-device tables, encrypted hash/public-key data, and auxiliary processor data used by firmware update, validation, and image parsing paths.

## Important APIs, Types, And Functions
`struct mpi3_component_image_header` is the central image header. It records signatures, load address, data/start offsets, flash offsets and sizes, version/build/environment string offsets, application-specific data, CRC, flags, secondary flash offset, ETP data, RMC/ETP/security versions, component image version, hash-exclusion ranges, next image header offset, and reserved space. Associated macros define expected signatures, header offsets, header size, image type signatures, and flags for signed UEFI, certificate-chain format, device-key basis, signed NVDATA, activation requirement, compression, and flashability.

`struct mpi3_comp_image_version` stores build/customer IDs and phase/generation version bytes. `struct mpi3_hash_exclusion_format` defines ranges excluded from hashes. `struct mpi3_ci_manifest_mpi` and `struct mpi3_ci_manifest_mpi_comp_image_ref` describe package manifest metadata and component references. `struct mpi3_sb_manifest_mpi`, `struct mpi3_sb_manifest_element`, and related unions describe secure-boot manifest elements for component-image references, embedded keys, and diagnostic keys.

`struct mpi3_extended_image_header` describes non-component extended images by type, checksum, size, next offset, and identify string. `struct mpi3_supported_devices_data` and `struct mpi3_supported_device` list supported PCI IDs/revisions. `struct mpi3_encrypted_hash_data` and `struct mpi3_encrypted_hash_entry` carry hash algorithm, encryption algorithm, key/signature sizes, public key data, and paired-key flags. `struct mpi3_aux_processor_data` describes auxiliary processor boot method, type, version, load addresses, and payload.

## Control Flow
The header has no executable logic. A firmware-management path uses these layouts by scanning image headers, checking `signature0`/`signature1`/`signature2`, following `next_image_header_offset`, validating `header_size` and `crc`, consulting string offsets, applying hash-exclusion ranges, and interpreting flags before deciding whether an image is flashable, compressed, signed, or requires activation.

Manifest parsing uses `manifest_type` to distinguish classic MPI package manifests from secure-boot manifests, then walks component references, digest lists, embedded keys, diagnostic authorization keys, and flexible manifest elements. Extended-image parsing uses `image_type` to branch into NVDATA, supported-devices, encrypted-hash, RDE, auxiliary-processor, or product-specific payloads.

## State And Persistence
The structures model persistent firmware package contents and flash image metadata. They do not store kernel runtime state. Offsets in the structures are relative to image/package blobs and remain meaningful across firmware update operations. Security version, package version, component versions, keys, digests, and supported-device lists are persistent properties of the image being parsed or flashed.

## Dependencies And Integration Points
The header depends on little-endian kernel types and `union mpi3_version_union` from common MPI definitions. It integrates with `mpi3mr` firmware download/update code, package validation, secure boot and diagnostic authorization handling, supported-device checks, and any application-facing management interface that reports package metadata.

## Risks And Edge Cases
This is an on-media/on-wire image ABI. Incorrect endian conversion, offset arithmetic, flexible-array bounds, or signature checks can cause the driver to parse invalid data as trusted firmware metadata. Several arrays have default maxima of 1 unless overridden (`MPI3_CI_MANIFEST_MPI_MAX`, `MPI3_SUPPORTED_DEVICE_MAX`, `MPI3_PUBLIC_KEY_MAX`, `MPI3_ENCRYPTED_HASH_ENTRY_MAX`, `MPI3_AUX_PROC_DATA_MAX`), so consumers must use image sizes and element counts rather than fixed `sizeof` assumptions for real packages.

Security-sensitive fields include certificate-chain flags, device-key basis, security versions, digest arrays, key algorithms, diagnostic authorization keys, and public keys. Firmware update code must validate sizes, offsets, and algorithms before use and must not trust manifest counts without ensuring they remain inside the image buffer.

There is a spelling inconsistency in `MPI3_IMAGE_HASH_EXCUSION_NUM` and `MPI3_IMAGE_HEADER_ENVIROMENT_VAR_OFFSET_OFFSET`; consumers must use the existing macro names as ABI source constants despite the spelling.

## Test Signals
Tests should parse known-good and malformed firmware packages, validate component header offsets and `MPI3_IMAGE_HEADER_SIZE`, walk multi-component `next_image_header_offset` chains, verify CRC/hash exclusion handling, decode package version and build strings, reject unsupported signatures and out-of-range offsets, verify supported-device matching across vendor/device/revision masks, and exercise secure-boot manifest parsing for digest, embedded-key, diagnostic-key, and encrypted-hash elements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/mpi/mpi30_image.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/mpi/mpi30_init.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/mpi/mpi30_init.h

## Purpose
`mpi30_init.h` defines the MPI 3.0 initiator I/O request and reply ABI for SCSI commands and task management in the Broadcom `mpi3mr` driver. It is the wire format used to submit SCSI I/O to firmware, describe CDB and SGL placement, request data direction and task attributes, and decode SCSI status, sense, protection-information, and task-management completion results.

## Important APIs, Types, And Functions
`struct mpi3_scsi_io_request` is the main SCSI I/O request frame. It contains host tag, function, message flags, device change count, device handle, I/O flags, skip count, data length, eight-byte LUN encoding, a CDB union, and four inline SGL entries. `union mpi3_scsi_io_cdb_union` can hold a 32-byte CDB, an EEDP32 CDB/protection-information descriptor, or a common SGE for separate CDB buffering. `struct mpi3_scsi_io_cdb_eedp32` stores a 20-byte CDB plus primary reference/application tags and transfer length.

Request flags define large-CDB placement, task attribute (`SIMPLEQ`, `HEADOFQ`, `ORDEREDQ`, `ACAQ`), command priority, data direction, host protection-information DMA operation, and divert-to-firmware reasons such as I/O throttling or oversized WRITE SAME. Message flags indicate metadata SGL validity and firmware diversion. `MPI3_SCSIIO_METASGL_INDEX` identifies the inline SGL slot used for metadata.

`struct mpi3_scsi_io_reply` carries host tag, function, IOC status/log info, SCSI status/state, device handle, transfer and sense counts, response data, task tag, status qualifier, EEDP error offset, observed application/guard/reference tags, and the sense-data buffer address. Reply flags mark which observed PI fields are valid.

The file also defines SCSI status constants, SCSI state/sense availability bits, packed response-data masks and shifts, unknown task tag value, task-management message flags, task management function types, and task management response codes.

## Control Flow
This header has no executable control flow. Driver I/O submission code fills `mpi3_scsi_io_request`, chooses CDB representation based on command length, sets data direction and task attributes from the SCSI command, maps data and optional metadata SGLs, posts the frame to firmware, then matches `host_tag` in the reply to complete the original command.

Completion code reads `mpi3_scsi_io_reply`: `ioc_status` and `ioc_log_info` describe firmware transport outcome; `scsi_status` and `scsi_state` determine SCSI result and sense handling; `transfer_count` contributes residual calculation; `sense_count` and `sense_data_buffer_address` identify sense data; task tag and response data support task-management and protocol responses; EEDP fields describe protection-information failures.

## State And Persistence
The request and reply frames are transient DMA/message-ring state shared between host and firmware. They are not persistent on disk. The only lasting effect is the completed SCSI command result or task-management recovery action. Device handles and change counts tie frames to controller-discovered device state from config pages and events.

## Dependencies And Integration Points
The header depends on endian-annotated kernel types and common MPI SGE definitions (`struct mpi3_sge_common`, `union mpi3_sge_union`). It integrates with the `mpi3mr` SCSI queuecommand path, firmware request queues, completion queues, sense-buffer management, protection-information handling, task-management/error-recovery code, and config/topology code that supplies device handles and change counts.

## Risks And Edge Cases
The request layout is firmware ABI. The driver must set flags consistently with CDB length and buffer placement; using inline CDB fields for a CDB that requires separate buffering, or failing to set `MPI3_SCSIIO_FLAGS_CDB_IN_SEPARATE_BUFFER`, can make firmware read the wrong command. Data direction, metadata SGL index, EEDP fields, and SGL counts must match mapped DMA buffers to avoid data corruption.

Completion interpretation must distinguish firmware IOC failures from target SCSI status. Sense states can report valid sense, failed sense, empty sense-buffer queue, or unavailable sense; treating all check conditions as valid sense would lose error detail or copy invalid data. PI observed tag fields are only meaningful when the corresponding reply message flag is set.

Task-management response codes include ordinary success/failure, invalid frame/LUN, overlapped tag, queued-on-IOC, and NVMe-denied cases. Error recovery should not collapse all nonzero codes into one behavior because queued or denied operations may require different retry/escalation.

## Test Signals
I/O tests should validate request frame construction for no-data, read, write, protection-information, metadata SGL, 16-byte-or-less CDB, greater-than-16 CDB, separate-CDB buffer, and diverted-to-firmware cases. Completion tests should cover good status, check condition with valid sense, busy, task set full, reservation conflict, terminated/no-status, residual calculation from `transfer_count`, EEDP observed tag reporting, and all task-management function/response mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/mpi/mpi30_init.h -->
