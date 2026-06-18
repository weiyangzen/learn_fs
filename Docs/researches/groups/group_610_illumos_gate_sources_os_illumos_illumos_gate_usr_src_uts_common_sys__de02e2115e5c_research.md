# Group Research: group_610_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_sys__de02e2115e5c

Scope verified against `Docs/research_subset_a.md`. The subset includes `sources/os/illumos/illumos-gate`, and all requested source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/adapters/nv_sata/nv_sata.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/adapters/nv_sata/nv_sata.h

## Role

Private header for the illumos NVIDIA SATA HBA driver. It defines the controller, port, command slot, DMA PRD, interrupt, reset, NCQ, hotplug, and optional SGPIO state used by the `nv_sata` adapter.

## Key Elements

- `nv_ctl_t` holds controller-wide state: BAR handles/addresses, PCI identity, interrupt handles, SATA HBA transport, chipset-specific interrupt/register hooks, MCP5x/CK804 register pointers, controller lock, DMA capability flags, and SGPIO common state when enabled.
- `nv_port_t` holds per-port state: task-file register pointers, bus-master registers, SATA SCRs, slot array, NCQ counters, reset/link-event timing, hotplug/reset flags, condition variables, and debug counters.
- `nv_slot_t` binds an active SATA packet to data-buffer state, request-sense buffer, start/intr callbacks, and slot flags.
- `nv_sgp_cmn` and `nv_sgp_cbp2cmn` coordinate SGPIO LED taskq/common data across controllers when `SGPIO_SUPPORT` is enabled.
- Defines chipset register offsets and bits for task-file I/O, bus-master DMA, MCP5x NCQ/interrupt registers, CK804 interrupt status, ADMA reset/hotplug controls, and SATA SCR offsets.
- Defines ATA reset signatures for disk, ATAPI, port multiplier, and no-device cases.
- Defines timing constants for resets, signature polling, link-event settling, interrupt loop limits, and debug throttling.
- Defines attachment progress flags and port/controller state flags used for teardown and recovery.

## Dependencies and Coupling

This header is tightly coupled to illumos DDI/DKI types, `sata_hba_t`/`sata_pkt_t`, PCI BAR layout, chipset-specific register maps, and optional SGPIO support from `nv_sgpio.h`.

## Research Notes

The file is driver-private infrastructure rather than a public ABI. Most constants encode hardware behavior and timing assumptions. The NCQ model is conservative: the per-port state tracks NCQ and non-NCQ exclusivity, active slots, queue depth, and cached SActive state to serialize command modes safely.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/adapters/nv_sata/nv_sata.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/adapters/nv_sata/nv_sgpio.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/adapters/nv_sata/nv_sgpio.h

## Role

Private NVIDIA SGPIO register and bitfield definition header for `nv_sata`. It describes the NVIDIA SGPIO command/status register, control block, configuration registers, and LED transmit-register encodings.

## Key Elements

- Defines SGPIO PCI config offsets `SGPIO_CSRP` and `SGPIO_CBP`.
- Defines SGPIO command/status register masks and helpers for command, command status, sequence bit, and SGPIO state.
- Defines command values for reset, read parameters, read data, and write data.
- `nv_sgp_cb_t` models the SGPIO control block, including scratch registers, NVIDIA configuration register, SGPIO configuration registers, GP transmit/receive config, and SGPIO transmit registers.
- Defines NVIDIA-specific configuration fields for initiator count, control-block size, and control-block version.
- Defines generic SGPIO CR0 fields for version, enable, GP/config register count, and supported drive count.
- Under `SGPIO_BLINK`, defines blink generator rates and blink-mode LED encodings.
- Provides macros for packing/unpacking per-drive activity, locate, and error indicator fields in SGPIO transmit registers.

## Dependencies and Coupling

Used by `nv_sata` only when SGPIO support is compiled in. The layout differs between `__amd64` and non-amd64 for the scratch-register representation, preserving expected hardware layout.

## Research Notes

The header is exclusively register vocabulary. Comments note that NVIDIA-documented blink generator values did not actually produce blinking LEDs, so blink support is conditional and likely experimental or disabled in normal builds.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/adapters/nv_sata/nv_sgpio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/adapters/si3124/si3124reg.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/adapters/si3124/si3124reg.h

## Role

Register, DMA descriptor, FIS, PRB, and error-code definition header for the Silicon Image 3124/3132/3531 SATA HBA driver.

## Key Elements

- Uses packed structures for hardware-facing layouts.
- `si_sge_t` describes one scatter/gather element with 64-bit address, byte count, and control bits for terminate/link.
- `si_sgt_t` groups four SGEs into one scatter/gather table.
- `fis_reg_h2d_t` models a SATA Register Host-to-Device FIS with macros to set and get command, features, LBA, sector count, device/head, and extended fields.
- `si_prb_t` models a Port Request Block with control override, received count, embedded H2D FIS, and initial SGEs.
- Defines interrupt bits for command completion, command error, port ready, power/PHY changes, unrecognized FIS, CRC/handshake errors, and device exchange.
- Defines disk/ATAPI/port-multiplier signatures.
- Defines global and per-port register address macros, including LRAM, port control/status, interrupt enable/status, command error, slot status, SCR registers, command activation, and signature offsets.
- Defines port-control/status bits, command posting macro `POST_PRB_ADDR`, slot masks, device IDs, BAR indexes, PSCR/SStatus fields, and command error codes.

## Dependencies and Coupling

The address macros assume `si_ctl_state_t` fields from `si3124var.h`. `POST_PRB_ADDR` also assumes per-port PRB/SGB DMA handles and the global `si_dma_sg_number`.

## Research Notes

This file is the hardware contract for command submission. The command activation path syncs both PRB and S/G memory for device access before writing the PRB physical address to the command-activation register.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/adapters/si3124/si3124reg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/adapters/si3124/si3124var.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/adapters/si3124/si3124var.h

## Role

Private state and tunable header for the Silicon Image 3124 family SATA HBA driver.

## Key Elements

- Defines supported port counts for SI3124, SI3132, and SI3531.
- Defines return codes, log buffer size, timing/polling constants, and attach-progress flags.
- Defines SGT table limits and `SGE_LENGTH()` for chained scatter/gather capacity.
- `si_sgblock_t` is a logical wrapper around SGTs, allowing tunable chained S/G tables per PRB request.
- `si_event_arg_t` carries controller/port context for timeout callbacks.
- `si_portmult_state_t` tracks port-multiplier child port types.
- `si_port_state_t` holds per-port state: port type/activity, port-multiplier state, PRB and S/G pools plus DMA handles, mutex, pending tags, slot packet array, reset/mop/error-recovery state, and NCQ counters.
- `si_ctl_state_t` holds controller state: devinfo, port array, PCI config handle, BAR mappings, SATA HBA transport, timeout, interrupt handles, power and FMA capability state.
- Defines controller flags for PM, attach/detach, timeout suppression, and SATA framework attachment.
- Defines debug flags/macros and reset-control flags.

## Dependencies and Coupling

Depends on hardware structures from `si3124reg.h` and framework types from the SATA HBA layer. Warlock annotations document lock ownership and read-only fields.

## Research Notes

The driver tracks “mopping” operations for abort/reset/timeout/error recovery and uses that count to reject new `tran_start` work while cleanup is in progress. Port-multiplier state is deliberately compact because all child ports share one physical controller port.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/adapters/si3124/si3124var.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/impl/sata.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/impl/sata.h

## Role

Internal SATA framework header. It defines framework-private HBA instance state, controller/device/port runtime state, SCSI-to-SATA packet translation state, event flags, minor-number encoding, target-number encoding, and debug hooks.

## Key Elements

- `sata_hba_inst_t` tracks one registered SATA HBA instance: devinfo, linked-list links, SCSI and SATA transport pointers, taskq, event/open flags, controller stats, and controller port array.
- `sata_cport_info_t` tracks a controller port: address, mutex, state/events, SCR copy, device type, attached drive or port multiplier, link/attach timestamps, stats, and target-node cleanliness.
- `sata_drive_info_t` tracks attached drive identity, state/events, status/error registers, feature support/enabled flags, queue depth, capacity, IDENTIFY data, stats, standby timer, and saved power level.
- `sata_pmult_info_t` and `sata_pmport_info_t` track port multiplier state and child device ports.
- Defines power levels, PM capability mappings, valid device masks, device feature bits, drive setting bits, and internal event/lock flags.
- `sata_pkt_txlate_t` links SCSI packet, SATA packet, DMA handles/cookies, temp buffers, and transfer window state.
- Defines ATA pass-through sense data and additional SCSI ASC constants used by translation.
- Defines `SATA_IS_MEDIUM_ACCESS_CMD()` for identifying commands that access media.
- Provides many accessor macros for transport callbacks, port structures, drive structures, pmult structures, packet translation fields, and task queues.
- Defines devctl/AP minor-number layout and SCSI target encoding for direct and port-multiplier-attached devices.
- Defines debug flags and debug macros under `DEBUG`.

## Dependencies and Coupling

Includes SCSI headers, `sata_defs.h`, and `sata_hba.h`. It is internal to the framework and should not be treated as an HBA driver ABI.

## Research Notes

This file is the core glue between the generic SCSI target view and SATA HBA transports. It preserves separate state machines for controller ports, port-multiplier child ports, and attached drives, while sharing event serialization flags between event processing and cfgadm operations.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/impl/sata.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/sata_blacklist.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/sata_blacklist.h

## Role

Small SATA framework header containing a blacklist for port multipliers that report faulty port counts in GSCR2.

## Key Elements

- Defines `sata_pmult_bl_t` with GSCR0, GSCR1, GSCR2, and flags fields.
- Defines `sata_pmult_blacklist[]` entries for Silicon Image 3726, 4726, and 4723 port multipliers.
- The comments state these devices report pseudo-port counts due to vendor configuration; the table records the actual usable port count in `bl_flags`.

## Dependencies and Coupling

Used by SATA port-multiplier discovery logic that interprets GSCR registers. The table is defined in the header, so inclusion must be controlled to avoid duplicate definitions.

## Research Notes

This is a hardware quirk table, not a generic policy module. It corrects known bad GSCR2 values during enumeration.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/sata_blacklist.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/sata_cfgadm.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/sata_cfgadm.h

## Role

Interface header between the SATA framework and the `cfgadm` plugin/devctl ioctl path.

## Key Elements

- `sata_cfga_apctl_t` enumerates attachment-point control subcommands:
  get AP type, model, firmware revision, serial number, reset port/device/all, port deactivate/activate, self-test, and device path lookup.
- `sata_ioctl_data_t` is the native ioctl payload with command, encoded port, size-query flag, buffer pointer, buffer size, and reserved argument.
- `sata_ioctl_data_32_t` provides 32-bit app / 64-bit kernel layout compatibility.
- Defines port-encoding masks and shift values matching SATA/SCSI target encoding for controller ports and port-multiplier ports.

## Dependencies and Coupling

Coupled to SATA devctl minor/target encoding from the framework and to cfgadm plugin expectations.

## Research Notes

The file contains no implementation, only ioctl command shape. Compatibility is explicit via the 32-bit structure.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/sata_cfgadm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/sata_defs.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/sata_defs.h

## Role

Shared SATA/ATA/SAT protocol definition header. It provides command opcodes, IDENTIFY data layout, SMART/log structures, ATAPI constants, NCQ constants, SCR bitfields, port-multiplier register definitions, and SCSI translation support constants.

## Key Elements

- Defines common ATA, ATAPI, SMART, SET FEATURES, queued I/O, port-multiplier, power-management, and microcode-download command/subcommand values.
- `sata_id_t` models ATA IDENTIFY DEVICE data across all 256 words, including serial, firmware, model, capabilities, command sets, SATA capabilities, sector sizing, WWN-ish fields, DSM/TRIM, SCT, rotation rate, and integrity word.
- Defines IDENTIFY word masks for ATA type, media/removable status, DMA/LBA support, command set support, SATA speed/NCQ support, write cache/read ahead, SMART, GPL, DSM/TRIM, SCT, and physical sector layout.
- Defines ATAPI type/signature/packet/DMA/interrupt-reason constants and default geometry/sector sizes.
- Defines NCQ and FIS constants.
- Defines ATA status, error, device-control, and device-head register bits.
- Defines SCSI/SAT support constants for log sense, self-test results, diagnostics, SMART mapping, SCSI ASC/ASCQ values, and device statistics logs.
- Defines packed-like protocol structures for NCQ error recovery log page, SMART data, SMART self-test logs, extended SMART self-test logs, read-log directory, log parameter, and acoustic management mode page.
- Defines port-multiplier GSCR/PSCR offsets and capability bits.
- Defines SStatus, SError, and SControl masks, shifts, values, and setter/getter macros, including SATA Gen3 and DevSleep-related IPM restrictions.

## Dependencies and Coupling

Included by both framework and HBA interface headers. It includes SCSI mode definitions and intentionally carries some SCSI constants that comments say should eventually live in generic SCSI headers.

## Research Notes

This header is protocol vocabulary rather than state. It spans older ATA/ATAPI compatibility through newer features such as Gen3 signaling, DSM/TRIM, SCT, device statistics, and extended SMART self-test logs.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/sata_defs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/sata_hba.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/sata_hba.h

## Role

Public SATA HBA driver transport interface header. It defines the ABI-like structures and callbacks used by SATA HBA drivers to register with and interact with the SATA framework.

## Key Elements

- Defines success/failure/retry values and framework limits for controller ports and port-multiplier ports.
- `sata_address_t` identifies controller ports, port-multiplier ports, controllers, devices, and port multipliers through mutually exclusive qualifier bits.
- `sata_port_scr_t` holds copies of SStatus, SError, SControl, SActive, and SNotification.
- `sata_pmult_gscr_t` holds port multiplier GSCR values.
- `sata_device_t` is the framework/HBA state exchange structure for ports, devices, controllers, and port multipliers.
- Defines common, drive-specific, and port-specific state flags, plus masks for power-state classes.
- Defines SATA device type bits for ATA disk, ATAPI subtypes, port multiplier, unknown, and no device.
- `sata_cmd_t` is the full ATA/ATAPI command descriptor passed to HBA drivers, including address type, task-file registers, flags, ATAPI CDB, request-sense buffer, error-retrieval DMA handle, and DMA cookie list.
- Command flags cover data direction, queue tag type, queued command, reset-state handling, special registers, copy-out fields, and maximum queue depth.
- `sata_pkt_t` wraps `sata_device_t`, HBA/framework private pointers, operation mode, command, timeout, completion callback, and completion reason.
- Defines packet operation modes, completion reasons, error-retrieval packet types, and port-multiplier read/write packet types.
- Defines hotplug and power-management transport vectors.
- `sata_hba_tran_t` is the HBA registration vector: device info, DMA attributes, port count, feature flags, queue depth, probe/start/abort/reset/selftest callbacks, optional hotplug/power ops, and ioctl hook.
- Defines controller feature flags for ATAPI, port multiplier, hotplug, ASN, queued commands, NCQ, and FIS-based switching.
- Declares SATA framework entry points: init/fini, attach/detach, event notify, error-retrieval packets, port-multiplier helpers, DMA cleanup, and model splitting.
- Defines SATA trace ring buffer structures and trace APIs.

## Dependencies and Coupling

This is the contract consumed by HBA drivers such as `nv_sata` and `si3124`. It depends on `sata_defs.h` and DDI/SCSI kernel types.

## Research Notes

The comments are unusually detailed and encode behavioral obligations for HBA drivers: register load ordering for LBA48, completion register copy-out rules, ATAPI request-sense handling, NCQ error retrieval, reset-state semantics, and callback lifetime constraints.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/sata_hba.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/sata_satl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/sata_satl.h

## Role

Small SATL/SAT-2 support header for SCSI ATA PASS THROUGH translation.

## Key Elements

- Includes SPC-3 SCSI type definitions.
- Defines ATA PASS THROUGH protocol field values for hardware reset, software reset, non-data, PIO data-in/out, DMA, DMA queued, diagnostics, device reset, UDMA in/out, FPDMA, and return-response-info.
- Defines bit masks for ATA PASS THROUGH EXTEND, CK_COND, T_DIR, and BYTE_BLOCK bits.

## Dependencies and Coupling

Used by SATL translation code in the SATA framework. It is protocol-constant-only and has no state structures.

## Research Notes

This header narrows in on SAT ATA PASS THROUGH CDB interpretation; broader ATA command and status constants live in `sata_defs.h`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/sata_satl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sbp2/bus.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sbp2/bus.h

## Role

SBP-2 bus-provider interface header. It defines the callback contract between the SBP-2 layer and an underlying serial bus implementation.

## Key Elements

- Defines SBP-2 bus interface revision.
- `sbp2_bus_buf_t` describes a bus/DMA buffer, including free-list link, bus handle, SBP-2 private data, length, flags, DMA flags, kernel address, physical/bus address, and quadlet/block read/write callbacks.
- Buffer flags distinguish DMA, read, write, posted, read/write, and write-posted buffers.
- Buffer request return codes distinguish success, generic failure, bad length, and busy device.
- `sbp2_bus_t` holds static bus parameters and function pointers for:
  interrupt-cookie lookup, node ID lookup, buffer allocation/free/sync, completion notifications, command allocation/free, and quadlet/block read/write bus transactions.

## Dependencies and Coupling

Includes `sbp2/common.h` and uses STREAMS `mblk_t`, DDI interrupt cookies, and SBP-2 buffer callbacks. The actual bus provider supplies all transport operations.

## Research Notes

This header abstracts FireWire/serial-bus operations away from SBP-2 target/session logic. Buffers can also expose remote read/write callbacks for address space exported to devices.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sbp2/bus.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sbp2/common.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sbp2/common.h

## Role

Common SBP-2 helper header for endian conversion, serial-bus address packing, ORB-pointer packing, and shared return codes.

## Key Elements

- Provides byte-swap macros for little-endian systems and no-op versions for big-endian systems.
- Defines `sbp2_addr_t` as two quadlets representing a 64-bit serial-bus address with node ID and aligned offset.
- Defines masks/shifts and `SBP2_ADDR_SET()`/`SBP2_ADDR2UINT64()` helpers.
- Defines `sbp2_orbp_t` as two quadlets representing an ORB pointer without node ID.
- Defines ORB null/offset masks and `SBP2_ORBP_SET()`/`SBP2_ORBP2UINT64()` helpers.
- Defines common SBP-2 return codes, aligned so success/failure match DDI success/failure.

## Dependencies and Coupling

Used by all SBP-2 headers. The swap macros depend on `_LITTLE_ENDIAN`.

## Research Notes

The address types are arrays of two 32-bit words, not native `uint64_t`, because SBP-2 ORB structures require quadlet alignment and wire-format ordering.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sbp2/common.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sbp2/defs.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sbp2/defs.h

## Role

SBP-2 wire-protocol definition header. It describes ORB formats, management operations, login/query/reconnect/logout/task-management ORBs, status blocks, command block agent registers, page-table elements, and Config ROM keys.

## Key Elements

- Defines dummy ORB and command ORB structures plus common ORB parameter bits.
- Defines command ORB fields for direction, speed, max payload, page table, and page size.
- Defines management ORB base structure and function codes for login, query logins, reconnect, set password, logout, abort task, abort task set, LUN reset, and target reset.
- Defines specialized login, query-logins, reconnect, logout, and task-management ORB structures.
- Defines login response layout, including login ID and command agent address.
- Defines `sbp2_status_t` and status parameter fields for source, response, dead bit, length, SBP status, failed object, and serial bus error.
- Defines command block agent register offsets and agent states.
- Defines unrestricted page table element layout and max segment size.
- Defines Config ROM key type/value constants for management agent, LUN, and unit characteristics.
- Defines LUN and unit-characteristic bit masks.

## Dependencies and Coupling

Includes `sbp2/common.h` for address and ORB pointer types. Warlock annotations mark protocol structures as unique per ORB.

## Research Notes

The file is a direct translation of ANSI NCITS 325-1998 SBP-2 protocol layout. It avoids implementation policy except for constants needed by the driver layer.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sbp2/defs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sbp2/driver.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sbp2/driver.h

## Role

SBP-2 driver-interface and implementation-state header. It defines parsed Config ROM structures, target/LUN/session/task/agent state, statistics, lock annotations, and exported SBP-2 driver functions.

## Key Elements

- Config ROM structures:
  `sbp2_cfgrom_bib_t`, `sbp2_cfgrom_dir_t`, `sbp2_cfgrom_ent_t`, and `sbp2_cfgrom_t`.
- Task state and error enums track task lifecycle and completion failure source.
- `sbp2_task_t` tracks task list links, session, driver-private data, bus buffer, timeout, timeout ID, state/error, bus error, status block, and timing.
- `sbp2_agent_t` models a command block agent with mutex/CV, state, acquired flag, command buffers, active task, and agent register offsets.
- `sbp2_ses_t` represents a login session with login ID, command agent, status FIFO, task list, and status callback.
- `sbp2_lun_t` tracks one logical unit, its sessions, ORB freelist, login response, and reconnect/login state.
- `sbp2_tgt_t` tracks a target: bus handle, LUNs, parsed Config ROM, management agent state, management ORB/status buffers, login response buffer, and statistics.
- Defines lock-order and data-protection annotations for target, session, agent, task list, and LUN state.
- Declares target lifecycle, disconnect/reconnect/reset, Config ROM access, LUN lookup, LUN login/logout/reset, session reconnect/task submission/cancel/reset/abort, ORB alloc/free/sync, byte swapping, and Config ROM walking/query helpers.

## Dependencies and Coupling

Includes SBP-2 protocol definitions and bus interface headers. It is the central internal API consumed by SBP-2 target drivers.

## Research Notes

The state model separates target management-agent operations from per-LUN sessions and per-session task queues. Several fields are marked stable-data while mutable queue/task fields are protected by separate mutexes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sbp2/driver.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sbp2/impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sbp2/impl.h

## Role

SBP-2 implementation-private helper header for Config ROM parsing and bus operation dispatch macros.

## Key Elements

- `sbp2_cfgrom_parse_arg_t` carries parser recursion state: current directory, parent directory, referred entry, and depth.
- `sbp2_cfgrom_ent_by_key_t` carries lookup criteria and result state for Config ROM entry searches.
- Defines parser limits and defaults:
  maximum Config ROM depth, directory entry growth increment, minimum/default management ORB timeout, and minimum/default ORB size.
- Defines macro wrappers for every `sbp2_bus_t` operation, including CSR base, Config ROM address, interrupt cookie, node ID, buffer alloc/free/sync, read/write completion, command alloc/free, and quadlet/block read/write.
- Declares `sbp2_cfgrom_parse()` and `sbp2_cfgrom_free()`.

## Dependencies and Coupling

Includes common, bus, and driver SBP-2 headers. The bus macros assume a valid `sbp2_tgt_t *` with populated `t_bus` and `t_bus_hdl`.

## Research Notes

This file exists to keep implementation code concise and to centralize the bus-provider dispatch layer. Config ROM parsing is bounded by a fixed recursion depth.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sbp2/impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/schedctl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/schedctl.h

## Role

Private kernel/libc/libsched scheduling-control shared-memory interface header.

## Key Elements

- Defines `sc_public_t`, the user-visible preemption control portion with `sc_nopreempt` and `sc_yield`.
- Defines `sc_shared_t`, the private shared LWP scheduler state used by user-level threading support:
  state, signal-block flag, flags, last CPU, scheduling class ID, class priority, dispatch priority, padding, and preemption-control data.
- Documents that Java has a contract to inspect `sc_state` and `sc_cpu`.
- Defines flags for park, cancellation pending, and EINTR due to cancellation.
- Defines schedctl state values matching kernel thread states except zombie.
- Defines maximum preemption-blocking ticks.
- Under `_KERNEL`, declares schedctl lifecycle, cleanup, preemption/yield setters, class/priority setter, signal-block handling, cancellation, EINTR, and park/unpark helpers.

## Dependencies and Coupling

Includes processor and type definitions for non-assembly consumers. The comment explicitly identifies this as a private interface between system libraries and the kernel.

## Research Notes

Although installed in `sys`, this is not a general public API. Its layout is sensitive because libc/libsched and Java depend on selected fields.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/schedctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/iscsi_door.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/iscsi_door.h

## Role

iSCSI door-call interface header used for kernel-to-user name service lookup support and iSCSI service status signaling.

## Key Elements

- Defines door request signature, version, maximum data size, opcodes, and status codes.
- `iscsi_door_msg_hdr_t` is the common message header.
- `getipnodebyname_req_t` encodes a hostname lookup request with name buffer offset/length, address family, and flags.
- `getipnodebyname_cnf_t` encodes lookup response metadata: required size, address list, address type/length, canonical name, aliases, and error number.
- Defines request/confirm/indication/message unions for generic door message handling.
- Under `_KERNEL`, copies relevant `netdb.h` constants and `AI_*` flags, defines a kernel `hostent`, and declares door init/term/bind/unbind plus kernel wrappers for `getipnodebyname` and `freehostent`.
- In userland, maps `kfreehostent` and `kgetipnodebyname` to libc functions.
- Defines iSCSI initiator SMF service status values: enabled, disabled, transition.

## Dependencies and Coupling

Used by iSCSI initiator code that needs name resolution from kernel context via a userland door server.

## Research Notes

The message format uses offsets and lengths rather than embedded pointers, making it suitable for door IPC buffers shared across address spaces.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/iscsi_door.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/iscsi_if.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/iscsi_if.h

## Role

iSCSI initiator management ioctl interface header. It defines user/kernel structures for target/session/login/discovery/authentication/configuration management.

## Key Elements

- Defines interface version and numeric login parameter IDs.
- Defines initiator devctl path and many ioctl command values for OID creation, login/logout, parameter get/set/clear, target/static/discovery management, CHAP/auth/RADIUS, LUN/connection queries, USCSI passthrough, SMF state, SendTargets, iSNS, config sessions, boot properties, tunables, target re-enumeration, and debug dump.
- Defines CHAP, target-list, static target, digest, and parameter-type constants.
- Defines discovery method enum with static, SLP, iSNS, SendTargets, and boot discovery.
- `iscsi_oid_t` identifies target objects by name/TPGT and returns an OID.
- `iscsi_login_params_t` stores negotiated/configured session and connection login parameters.
- `entry_t` describes a login endpoint, including IPv4/IPv6 address, port, TPGT, and boot-session flag.
- Defines structures for node names, min/max integer/bool parameter values, parameter get/set payloads, tunable object values, CHAP properties, auth properties, RADIUS properties, IP addresses, target addresses, address lists, target properties, target OID lists, static target properties, LUN properties/lists, connection properties/lists, discovery properties, USCSI passthrough, SendTargets results, static target entries, iSNS portal groups, configured session bindings, re-enumeration, and boot properties.
- Defines sysevent class/subclass strings for iSCSI discovery and property-change events.
- Under `_KERNEL`, declares filesystem/socket helper wrappers used by the iSCSI code.
- Declares common utility functions for IQN creation, bitmap printing, login parameter mapping, and address/port/TPGT parsing.

## Dependencies and Coupling

Includes networking, SCSI USCSI, and iSCSI protocol headers. The structures form an ioctl ABI consumed by management tools and kernel driver code.

## Research Notes

Most variable-length outputs use a one-element trailing array pattern with input/output counts. The file is intentionally broad because it centralizes management ABI for discovery, authentication, session binding, LUN visibility, and boot-time iSCSI configuration.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/iscsi_if.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mfi/mfi.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mfi/mfi.h

## Role

Core MegaRAID Firmware Interface header shared by illumos MFI-compatible drivers. It defines firmware commands, statuses, DCMD opcodes, packed command frames, controller properties/info, and patrol-read structures.

## Key Elements

- Forward-declares all major MFI protocol structures from this and companion headers.
- Defines controller limits for logical and physical drives.
- Defines firmware init/reset flags and common reset flag combination.
- Defines frame flags for reply queue posting, 64-bit SGL/sense, data direction, and IEEE SGL format.
- Defines MFI command opcodes for init, logical drive read/write/SCSI I/O, physical drive SCSI I/O, DCMD, abort, SMP, STP, and invalid command.
- Defines many firmware completion statuses.
- Defines DCMD opcodes for controller info/properties/events/shutdown/time/flash, patrol read, physical-drive list/info/state/rebuild/clear/locate, logical-drive map/list/info/property/delete, config read/add/clear/spare/foreign config, and BBU operations.
- Defines BBU type, patrol-read state/mode, and physical/logical-drive query types.
- Packed protocol types:
  `mfi_cap_t`, `mfi_sgl_t`, `mfi_header_t`, init/I/O/passthrough/DCMD/abort payloads, and 64-byte `mfi_frame_t`.
- `mfi_ctrl_props_t` models controller tunables and feature toggles.
- `mfi_image_comp_t` models firmware image component metadata.
- `mfi_ctrl_info_t` is a large 0x800-byte packed controller information block covering PCI identity, host/device interfaces, firmware images, drive counts, memory/error counters, RAID capabilities, adapter options, controller properties, package version, physical-drive limits, feature options, temperatures, cluster state, and later adapter capability bitsets.
- `mfi_pr_properties_t` and `mfi_pr_status_t` describe patrol-read configuration and state.
- `mfi_progress_t` stores progress and elapsed time.

## Dependencies and Coupling

Includes bitfield and debug support, uses packed firmware layouts, and relies on `CTASSERT` to enforce expected wire sizes and offsets.

## Research Notes

This file is a hardware/firmware ABI map. The compile-time assertions are critical: frame size, controller info size, and property block sizes must match firmware expectations exactly.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mfi/mfi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mfi/mfi_bbu.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mfi/mfi_bbu.h

## Role

MFI battery backup unit definition header.

## Key Elements

- Defines packed BBU capacity, design information, iBBU state, traditional BBU state, combined BBU status, and BBU properties structures.
- `mfi_bbu_capacity_t` reports charge, capacity, runtime, cycle count, error, and alarm thresholds.
- `mfi_bbu_design_info_t` reports manufacturing date, design capacity/voltage, serial, manufacturer/device/chemistry strings, and manufacturing data.
- `mfi_ibbu_state_t` and `mfi_bbu_state_t` model state details for intelligent BBU and regular BBU variants.
- `mfi_bbu_status_t` includes BBU type, voltage/current/temperature, state bitfield, padding, and a union for BBU/iBBU state.
- `mfi_bbu_properties_t` includes auto-learn period, next learn time, delay interval, learn mode, and BBU mode.
- Compile-time assertions enforce firmware-visible sizes.

## Dependencies and Coupling

Includes `mfi.h` for shared typedefs and MFI constants. Used with BBU DCMDs defined in the core header.

## Research Notes

The BBU status union lets the same 64-byte status block carry either classic BBU or iBBU-specific details after common health and sensor fields.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mfi/mfi_bbu.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mfi/mfi_evt.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mfi/mfi_evt.h

## Role

MFI event and asynchronous event notification definition header.

## Key Elements

- Forward-declares AEN, event log, event detail/list, and all event argument structures.
- Defines event codes for configuration, patrol-read, logical-drive initialization/check/creation/deletion/state, physical-drive insertion/removal/change/reset/progress, foreign configuration, controller property/performance/boot/personality changes, and snapdump count.
- Defines event classes from debug/progress/info through fatal/dead.
- Defines event locales for logical drive, physical drive, enclosure, BBU, SAS, controller, config, cluster, and all.
- Defines event argument type IDs for none, CDB/sense, logical drive, physical drive, counts, LBAs, owners, progress, state, PCI, rate, string, time, and ECC.
- Packed structures:
  `mfi_aen_t`, `mfi_evt_t`, `mfi_evt_log_info_t`, logical/physical drive argument variants, CDB/sense payload, PCI/time/ECC arguments, and `mfi_evt_detail_t`.
- `mfi_evt_detail_t` stores sequence, timestamp, code, class/locale, argument type, a union of typed arguments or string, and a description string.
- `mfi_evt_list_t` is a variable-length event-list wrapper.

## Dependencies and Coupling

Includes `mfi.h` for common types such as `mfi_progress_t`. Size of `mfi_evt_detail_t` is asserted to 256 bytes.

## Research Notes

The event format is designed for firmware log retrieval and AEN processing. The typed union makes event interpretation depend on `evt_argtype`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mfi/mfi_evt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mfi/mfi_ioctl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mfi/mfi_ioctl.h

## Role

Shared MFI ioctl interface definition used by MFI-family drivers and closed-source management utilities.

## Key Elements

- Defines ioctl signatures for driver, firmware, and AEN requests.
- Defines common driver ioctl control codes for driver version, PCI information, and MRRAID statistics.
- Defines fixed sense length for ioctl payloads.
- Packed structures:
  `mfi_drv_ver_t` for driver signature/OS/driver version/release strings.
  `mfi_pci_info_t` for bus/device/function/interrupt, PCI config header, capability bytes, and reserved space.
  `mfi_ioctl_t` for the external ioctl payload: version, controller ID, signature, control code, embedded `mfi_frame_t`, SGL, sense buffer, and trailing data array.

## Dependencies and Coupling

Includes DDI/cred/file/errno headers and `mfi.h`. Comments state the interface must not be changed because closed-source utilities such as StorCLI depend on it.

## Research Notes

This is an ABI-sensitive header. The trailing `ioc_data[0]` supports variable-sized firmware/user data transfers after the fixed ioctl header.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mfi/mfi_ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mfi/mfi_ld.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mfi/mfi_ld.h

## Role

MFI logical-drive and RAID configuration definition header.

## Key Elements

- Defines spare flags, logical-drive states, initialization modes, access policies, cache policy bits, and maximum array/row/span sizes.
- `mfi_array_t` describes one array: size, drive count, reference, padding, and per-row physical drive references/state/enclosure location.
- `mfi_spare_t` describes a spare drive, spare type, and associated array references.
- `mfi_ld_ref_t` identifies a logical drive by target ID and sequence number.
- `mfi_ld_list_t` returns all logical drives with reference, state, and size.
- `mfi_ld_parameters_t` stores RAID levels, stripe, drive count, span depth, state, init state, consistency, and SSD cache flag.
- `mfi_ld_properties_t` stores logical drive reference, name, cache/access/disk-cache policies, background-init flag, and reserved bytes.
- `mfi_span_t` describes logical-drive spans over arrays.
- `mfi_ld_config_t` combines properties, parameters, and spans.
- `mfi_ld_progress_t` reports active consistency-check, background-init, foreground-init, and reconstruction progress.
- `mfi_ld_info_t` combines logical-drive config, size, progress, cluster owner, reconstruction state, VPD page 83 data, and reserved space.
- `mfi_ld_tgtid_list_t` and `mfi_config_data_t` are variable-length wrappers for target IDs and full RAID configuration data.

## Dependencies and Coupling

Includes `mfi.h` and `mfi_pd.h` because logical-drive configuration embeds physical-drive references. Uses packed structures and size assertions for firmware layout.

## Research Notes

`mfi_config_data_t` has multiple zero-length arrays representing arrays, logical drives, and spares in one firmware buffer. Consumers must use the count/size fields to walk it safely.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mfi/mfi_ld.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mfi/mfi_pd.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mfi/mfi_pd.h

## Role

MFI physical-drive definition header.

## Key Elements

- Defines physical-drive firmware states: unconfigured good/bad, hot spare, offline, failed, rebuild, online, copyback, and system.
- Defines physical-drive cache policy values.
- `mfi_pd_ref_t` identifies a physical drive by device ID and sequence number.
- `mfi_pd_info_t` is a 512-byte packed physical-drive information block containing:
  inquiry and VPD data, device type, connected ports, speed, media/other/predictive error counts, firmware state, removal/link state, DDF type flags, path information and SAS addresses, raw/non-coerced/coerced sizes, enclosure/slot info, rebuild/patrol/clear/copyback/erase/locate progress, bad-block and config usability flags, extended VPD, power/enclosure position, allowed operations, copyback/enclosure partners, security state, media and bridge identity, SAT bridge flag, interface/temperature/blocksize fields, PI/NCQ/WCE/UNMAP properties, shield diagnostic state, alternate link speed, BBM error count, and reserved padding.
- `mfi_pd_cfg_t` maps firmware physical-drive sequence/device handle to target ID and task-management capability.
- `mfi_pd_map_t` is a variable-length physical-drive config map.
- `mfi_pd_addr_t` describes physical-drive address/location and SAS addresses.
- `mfi_pd_list_t` is a variable-length physical-drive address list.

## Dependencies and Coupling

Includes `mfi.h` for shared progress and MFI types. The size assertion for `mfi_pd_info_t` is skipped under `__CHECKER__` due to a known smatch packing issue.

## Research Notes

This header exposes detailed drive health, topology, enclosure, security, and progress state. It is firmware-layout sensitive and uses packed structs throughout.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mfi/mfi_pd.h -->