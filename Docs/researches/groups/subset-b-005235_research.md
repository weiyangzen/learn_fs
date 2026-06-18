# subset-b-005235 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_reg_def.h -->
## sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_reg_def.h

Purpose: this header is the low-level hardware register, bit-mask, interrupt, OOB/PHY, sequencer-CIO, sequencer-scratch, PCI/EXSI, and timer address contract for the aic94xx SAS/SATA driver. It is intentionally data-only: consumers such as `aic94xx_reg.h`, `aic94xx_seq.c`, `aic94xx_scb.c`, and the HWI path use these constants to issue memory-mapped register reads/writes without open-coded offsets.

Important APIs/types/functions: there are no functions or C types beyond macros. The important surfaces are register base/address macros such as `COMBIST`, `COMSTAT`, `CHIMINT`, `CMDCTXBASE`, `CARP2CTL`, `CSEQm_CIO_REG()`, `LmSEQ_PHY_REG()`, `LmARP2CTL()`, `LmPRMSTAT0()`, and `LmSCRATCH()`. Bit groups include reset/BIST bits, done-list availability and exception interrupt masks, overlay-DMA controls, ARP2 pause/halt flags, CSEQ/LSEQ interrupt masks, primitive status masks, OOB status/clear/enable bits, PHY tuning values, PCI config offsets, flash BAR access offsets, and scratch-memory aliases such as `CSEQ_Q_EXE_HEAD` and `LmSEQ_CONNECTION_STATE`.

Control flow and state: the file does not execute control flow, but it defines the state machine vocabulary used elsewhere. Sequencer setup writes CSEQ/LSEQ queue heads, tails, interrupt vectors, timeout constants, and `DDB 0` link maps through these scratch offsets. Event handling decodes done-list status with primitive/OOB masks. PHY control builds `CONTROL_PHY` SCBs from `FUNCTION_MASK_DEFAULT`, `SPEED_MASK`, `CURRENT_*`, and OOB constants. Firmware download uses overlay-DMA constants such as `OVLYDMACTL`, `STARTOVLYDMA`, `OVLYCSEQ`, and `OVLYDMADONE`.

Persistence behavior: none in the filesystem sense. The persistence is hardware-resident: register values, sequencer scratch RAM, SCB/DDB context memory, and flash-bar configuration survive only according to adapter reset/firmware behavior. Incorrect constants can corrupt hardware state across tasks until a chip reset.

Dependencies and integration points: depends on `REG_BASE_ADDR`, `REG_BASE_ADDR_CSEQCIO`, and `REG_BASE_ADDR_EXSI` from `aic94xx_reg.h`. It is coupled to the sequencer firmware ABI and to packed SCB/DDB layouts from `aic94xx_sas.h`; offsets written in `aic94xx_seq.c` must match the firmware's expected scratch layout.

Risks: high blast radius from any offset or mask change. Duplicate macro definitions exist for a few names, so refactors must avoid accidentally changing semantics. Endianness is implicit in the caller helpers, not this file. Several masks define hardware errata/workarounds and are hard to validate without real controllers.

Test signals: a successful kernel build catches syntax and missing macro users. Runtime signals are adapter probe, sequencer firmware download/verify, phy bring-up, link reset events, done-list interrupts, and task I/O on SAS/SATA targets. Hardware or emulation is required for meaningful regression confidence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_reg_def.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_sas.h -->
## sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_sas.h

Purpose: this header defines the aic94xx hardware ABI for SAS/SATA domain state, scatter/gather elements, 128-byte SCBs, done-list entries, and per-phy driver state. It is the bridge between libsas concepts (`sas_task`, `domain_device`, SSP/SMP/STP frames) and what the Adaptec sequencers consume in DMA-visible memory.

Important APIs/types/functions: key packed types include DDB formats (`asd_ddb_ssp_smp_target_port`, `asd_ddb_stp_sata_target_port`, `asd_ddb_init_port`, SATA tag/PM tables, `asd_ddb_seq_shared`), hardware SG elements (`sg_el`), `scb_header`, protocol SCB payloads (`initiate_ssp_task`, `initiate_ata_task`, `initiate_smp_task`, `control_phy`, `abort_task`, `clear_nexus`, `initiate_ssp_tmf`, `send_prim`), the `scb` union, `done_list_struct`, and `asd_phy`. Constants define SCB opcodes, done-list completion opcodes, nexus selectors, data directions, SG flags, timer defaults, and notify/spinup policy.

Control flow and state: no executable flow lives here, but its layouts drive all SCB construction and completion decoding. `aic94xx_task.c` fills SSP/SMP/ATA SCB payloads and SG elements; `aic94xx_tmf.c` fills abort, TMF, and clear-nexus payloads; `aic94xx_scb.c` decodes `done_list_struct` and empty-buffer events; `aic94xx_seq.c` initializes DDB 0 and SCB/DDB sites using structure offsets. `asd_phy` stores libsas phy state plus hardware profile and received frame buffers.

Persistence behavior: SCBs and SG lists are transient DMA descriptors. DDBs are hardware context memory entries that persist across commands until cleared/reset. Done-list entries are hardware completion records. Per-phy frame buffers and `asd_port` association are driver memory state updated during hotplug and link reset.

Dependencies and integration points: includes `<scsi/libsas.h>` and relies on SAS frame structs, task status enums, and libsas phy/port notifications. It is tightly coupled to sequencer firmware expectations and register scratch offsets in `aic94xx_reg_def.h`.

Risks: packed layout drift is catastrophic because firmware reads exact byte offsets. Endianness annotations are mixed big/little endian according to SAS frame and hardware fields. SG list chaining is limited by the three embedded elements and external list convention, so DMA mapping changes need careful cleanup and EOL/EOS validation.

Test signals: build-time struct-field users, sparse/endian checks, successful SSP/SMP/STP I/O, task-management operations, wide-port formation, hotplug, and completion status mapping. Hardware tests should cover no-data, single-buffer, multi-SG, SMP response, ATA NCQ, and error-completion paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_sas.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_scb.c -->
## sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_scb.c

Purpose: this file manages non-I/O SCB behavior for aic94xx, especially empty SCB event handling, phy/link event translation, port formation/deformation, EDB recycling, and libsas phy-control requests.

Important APIs/types/functions: exported/externally used functions are `asd_invalidate_edb()`, `asd_init_post_escbs()`, `asd_build_control_phy()`, `asd_ascb_timedout()`, and `asd_control_phy()`. Internal handlers include `get_lrate_mode()`, `asd_phy_event_tasklet()`, `asd_get_attached_sas_addr()`, `asd_form_port()`, `asd_deform_port()`, `asd_bytes_dmaed_tasklet()`, `asd_link_reset_err_tasklet()`, `asd_primitive_rcvd_tasklet()`, `escb_tasklet_complete()`, `control_phy_tasklet_complete()`, and `set_speed_mask()`.

Control flow and state: posted ESCBs receive hardware empty-buffer events. `escb_tasklet_complete()` decodes the done-list opcode/status block, handles special sequencer requests (`REQ_TASK_ABORT`, `REQ_DEVICE_RESET`, NCQ error notices), dispatches BYTES_DMAED/primitive/phy/link/timer events, then invalidates the used EDB. BYTES_DMAED copies identify/FIS data into `sas_phy.frame_rcvd`, derives attached SAS addresses for SATA, forms or updates ports, and notifies libsas. Link reset and timer failures turn LEDs off, disconnect libsas phys, deform ports, and may post an enable-phy SCB when retries are exhausted. `asd_control_phy()` translates libsas `phy_func` requests into `CONTROL_PHY` SCBs.

Persistence behavior: mutates in-memory phy/port association, `hw_prof.enabled_phys`, LED state, libsas negotiated linkrate, received frame buffers, and EDB validity. EDBs are recycled only after all buffers in an ESCB have been invalidated and the ESCB is reposted.

Dependencies and integration points: depends on aic94xx register/OOB macros, ASCB allocation/posting, LED helpers, dump helpers, and libsas notifications (`sas_notify_phy_event`, `sas_notify_port_event`, `sas_phy_disconnected`). It calls `asd_update_port_links()` in `aic94xx_seq.c` to update DDB 0.

Risks: many paths run in tasklet/IRQ context and allocate with `GFP_ATOMIC`; missed EDB invalidation can starve event buffers. Port formation relies on SAS address matching and lock discipline. Special sequencer requests walk `seq.pend_q` and abort tasks asynchronously, so races with normal completion are a key risk.

Test signals: hotplug/unplug, OOB error, hard reset primitive, broadcast change, spinup-hold, link-reset retry exhaustion, libsas phy control operations, and repeated empty-buffer recycling. Instrumented tests should watch `frame_rcvd_size`, `phy_mask`, LED changes, and absence of EDB leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_scb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_sds.c -->
## sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_sds.c

Purpose: this file reads and writes shared data structures for adapter configuration. It imports BIOS/OCM metadata, flash manufacturing/user settings, SAS addresses, PHY parameters, and exposes flash programming helpers.

Important APIs/types/functions: exported functions are `asd_read_ocm()`, `asd_read_flash()`, `asd_verify_flash_seg()`, `asd_write_flash_seg()`, `asd_chk_write_status()`, `asd_erase_nv_sector()`, and `asd_check_flash_type()`. Internal structures include OCM directory entries, BIOS CHIM metadata, flash directory entries, manufacturing sectors, CTRL-A phy settings, and linked-list elements. Internal processing functions include `asd_read_ocm_seg()`, `asd_read_ocm_dir()`, `asd_get_bios_chim()`, `asd_hwi_check_ocm_access()`, `asd_flash_getid()`, `asd_find_flash_dir()`, `asd_process_ms()`, `asd_ms_get_phy_params()`, and `asd_process_ctrl_a_user()`.

Control flow and state: probe-time HWI code calls `asd_read_ocm()` and `asd_read_flash()`. OCM access verifies BIOS initialization, optionally initializes a default OCM directory, reads BIOS CHIM data, and records BIOS/UE metadata in `hw_prof`. Flash reading resets and identifies flash, locates the Adaptec flash directory, validates revision, extracts the manufacturing sector, copies adapter SAS address and PCBA serial, applies manufacturing PHY states, then applies CTRL-A per-phy SAS address/link-rate/user flags. Flash write helpers identify the flash command method, erase affected sectors, program byte-by-byte, poll DQ toggle bits, reset, and allow explicit verification.

Persistence behavior: read paths populate `asd_ha->hw_prof` and allocated UE/manufacturing data. Write/erase paths permanently mutate adapter flash sectors. Default paths synthesize configuration when manufacturing or CTRL-A sections are missing but do not persist defaults unless flash write APIs are invoked by higher layers.

Dependencies and integration points: depends on PCI config space, MMIO register helpers, flash BAR from PCI config, OCM accessors, `aic94xx_sds.h` flash constants, manufacturing structure definitions from other aic94xx headers, and HWI probe sequencing.

Risks: flash writes are destructive and hardware-specific; bad method detection, sector math, or timeout handling can corrupt firmware/config. Some checksum failures are logged but not fatal. Linked-list parsing trusts offsets after minimal validation. Default PHY data may mask missing flash content but can change port exposure.

Test signals: probe on boards with initialized and uninitialized OCM, valid/invalid flash directories, missing manufacturing or CTRL-A sections, supported flash IDs for method A/B, flash verify mismatch, erase/write timeout, and SAS address/link-rate propagation into phy descriptors. Hardware-backed tests are required for write paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_sds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_sds.h -->
## sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_sds.h

Purpose: this header provides the public flash/SDS constants and prototypes used by aic94xx code that reads adapter configuration or updates flash.

Important APIs/types/functions: it defines flash programming methods (`FLASH_METHOD_UNKNOWN`, `FLASH_METHOD_A`, `FLASH_METHOD_B`), manufacturer/device IDs, DQ status-bit masks, erase/write poll delays, sector size/mask, error/status codes, and firmware image header structures (`controller_id`, `image_info`, `bios_file_header`). Function prototypes expose `asd_verify_flash_seg()`, `asd_write_flash_seg()`, `asd_chk_write_status()`, `asd_check_flash_type()`, and `asd_erase_nv_sector()`.

Control flow and state: no control flow is implemented here. `aic94xx_sds.c` uses these constants to detect flash command-set style, program/erase flash sectors, and return stable status codes. The `bios_file_header` and image descriptors describe BIOS image files rather than in-kernel runtime state.

Persistence behavior: constants in this header gate persistent flash operations. Callers using the write/erase prototypes can mutate NVRAM/flash content, while verify/status helpers only observe.

Dependencies and integration points: references `struct asd_ha_struct` by pointer without defining it, so it is intended for internal aic94xx compilation units. It aligns with flash BAR/profile fields in `asd_ha->hw_prof.flash` and with SDS parsing in `aic94xx_sds.c`.

Risks: numeric status codes are not `errno` values, so callers must not blindly mix them with negative Linux errors. Flash ID aliases overlap among vendors; method selection must be kept in sync with the implementation. Header structures lack endian annotations for image fields, requiring caller discipline when parsing external files.

Test signals: compile users of all prototypes, flash type detection for supported IDs, sector erase/write/verify loops, and user-facing error propagation for every `FAIL_*` value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_sds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_seq.c -->
## sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_seq.c

Purpose: this file loads aic94xx sequencer firmware, downloads CSEQ/LSEQ microcode, verifies it, initializes sequencer scratch/CIO/SCB/DDB state, starts sequencers, and updates DDB 0 link maps as ports form.

Important APIs/types/functions: exported functions are `asd_init_seqs()`, `asd_start_seqs()`, `asd_release_firmware()`, and `asd_update_port_links()`. Key internals pause/unpause CSEQ/LSEQs, verify/download code (`asd_verify_cseq()`, `asd_verify_lseq()`, `asd_download_seq()`), request/parse firmware (`asd_request_firmware()`), initialize CSEQ/LSEQ scratch pages and CIO registers, initialize SCB sites, initialize DDB 0 and DDB sites, and start the sequencer program counters.

Control flow and state: `asd_init_seqs()` requests `aic94xx-seq.fw`, validates checksum/table sizes/major version, sets vector/code globals, downloads CSEQ then LSEQ code using overlay DMA (or PIO fallback), verifies downloaded RAM, and initializes all sequencer state. Setup zeros DDB/SCB sites, builds a valid SCB free list excluding invalid sites, initializes CSEQ queues/done-list DMA pointers, initializes per-link OOB/timer/interrupt state, writes SAS addresses, and sets DDB 0. `asd_start_seqs()` unpauses CSEQ and each enabled LSEQ at firmware-provided idle-loop addresses.

Persistence behavior: firmware data is cached in static globals until `asd_release_firmware()`. Hardware state includes instruction RAM, scratch RAM, SCB/DDB context memory, interrupt masks, DMA pointers, and DDB 0 port/link bits. `asd_update_port_links()` mutates DDB 0 under `ddb_lock` with retry-on-update semantics.

Dependencies and integration points: depends on Linux firmware loader, PCI device naming, DMA allocation, register helpers, `aic94xx_reg_def.h` offsets, `aic94xx_sas.h` DDB/SCB layouts, and HWI initialization order (`asd_init_seqs()` before `asd_start_seqs()`). `aic94xx_scb.c` calls `asd_update_port_links()` after port formation.

Risks: firmware ABI mismatch, checksum bugs, or offset drift can prevent probe or corrupt command execution. Static firmware globals imply shared firmware state across adapters. Overlay DMA errors must restore interrupt enable state. SCB free-list construction changes queue capacity and must respect hardware errata macros.

Test signals: missing firmware, bad checksum, bad major version, CSEQ/LSEQ verify mismatch, no enabled phys, multi-phy download fallback, successful start on all enabled phys, and port-map updates after hotplug/wide-port formation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_seq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_seq.h -->
## sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_seq.h

Purpose: this header defines the firmware-file ABI and exported sequencer lifecycle functions for aic94xx.

Important APIs/types/functions: constants include `CSEQ_NUM_VECS`, `LSEQ_NUM_VECS`, `SAS_RAZOR_SEQUENCER_FW_FILE`, and required firmware major version. `struct sequencer_file_header` describes the little-endian firmware header: checksum, major/minor, printable version, CSEQ/LSEQ vector tables, CSEQ/LSEQ code blobs, mode-2 task address, and idle-loop addresses. Kernel prototypes expose `asd_init_seqs()`, `asd_start_seqs()`, `asd_release_firmware()`, and `asd_update_port_links()`.

Control flow and state: no flow is implemented here. `aic94xx_seq.c` reads this header layout directly from `request_firmware()` data, validates sizes and version, and uses the parsed offsets to populate static firmware globals before downloading microcode.

Persistence behavior: none directly. The header defines how firmware bytes become persistent in hardware instruction RAM during driver initialization and how DDB 0 link-state updates are exposed to other files.

Dependencies and integration points: requires `struct asd_ha_struct` and `struct asd_phy` declarations from the internal aic94xx environment when `__KERNEL__` is defined. The firmware file name is also declared with `MODULE_FIRMWARE()` in `aic94xx_seq.c`.

Risks: all quantities are noted as little-endian; any parser changes must retain conversions. Table-size constants must match the firmware image. The major version constant is a hard compatibility gate.

Test signals: firmware header parsing, checksum validation, vector count validation, major-version mismatch handling, and callers compiling against the lifecycle prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_seq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_task.c -->
## sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_task.c

Purpose: this file is the normal I/O submission and completion path from libsas `sas_task` objects to aic94xx hardware SCBs for SSP, SMP, SATA/STP, and ATAPI.

Important APIs/types/functions: the exported entry point is `asd_execute_task()`. Core helpers are `asd_can_queue()`/`asd_can_dequeue()`, `asd_map_scatterlist()`, `asd_unmap_scatterlist()`, `asd_get_response_tasklet()`, `asd_task_tasklet_complete()`, and protocol builders/unbuilders for ATA, SMP, and SSP SCBs. `data_dir_flags[]` maps Linux DMA directions to hardware data-direction bits.

Control flow and state: `asd_execute_task()` reserves queue capacity, allocates an ASCB, attaches it to `task->lldd_task`, normalizes STP protocol bits, builds a protocol-specific SCB, posts it, and unwinds DMA/ASCB state on errors. Builders fill opcode, protocol/rate, frame fields, CDB/FIS/SMP SG descriptors, connection handle, retry count, data direction, and hardware SG list. Completion translates done-list opcodes into libsas task response/status, optionally reads response IU/FIS data from an EDB, unmaps DMA, marks task state done, frees the ASCB, and invokes `task_done()` unless the upper layer already marked the task aborted.

Persistence behavior: mutates `seq.can_queue`, `task->lldd_task`, task state flags, ASCB SG allocations, DMA mappings, and task status/residual data. Hardware SCBs and external SG lists are transient until completion or abort cleanup.

Dependencies and integration points: depends on libsas task/protocol structures, PCI DMA mapping APIs, ASCB allocation/posting, `aic94xx_sas.h` layouts/opcodes, and `asd_invalidate_edb()` from `aic94xx_scb.c`. TMF paths in `aic94xx_tmf.c` depend on `task->lldd_task` and transaction context indices created here.

Risks: cleanup asymmetry around ATA pre-mapped SG lists is subtle; the `err_unmap` branch appears to unmap ATA when allocation of an external SG list fails even though comments say libata already mapped it. Completion races with abort handling rely on task state locks and completion pointers. Multi-SG chaining depends on exact EOL/EOS flags and external list allocation.

Test signals: queue-full handling, allocation failure unwind, no-data/single-buffer/multi-SG DMA, ATA device-control updates, ATAPI packet copy, SMP request/response DMA, SSP response IU handling, every major done-list opcode mapping, and abort-vs-completion races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_task.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_tmf.c -->
## sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_tmf.c

Purpose: this file implements aic94xx task-management and nexus cleanup operations used by libsas error handling: abort task, abort/clear task set, LU reset, I_T nexus reset, query task, adapter/port clear nexus, and lower-level sequencer clear-nexus commands.

Important APIs/types/functions: exported functions are `asd_clear_nexus_ha()`, `asd_clear_nexus_port()`, `asd_I_T_nexus_reset()`, `asd_abort_task()`, `asd_abort_task_set()`, `asd_clear_task_set()`, `asd_lu_reset()`, and `asd_query_task()`. Internal helpers enqueue internal SCBs with timers, build/complete clear-nexus SCBs, parse TMF responses from EDBs, clear nexus by tag or transaction index, and initiate generic SSP TMFs.

Control flow and state: internal TMF SCBs are posted with a timer and stack completion. Clear-nexus helpers build `CLEAR_NEXUS` SCBs for adapter, port, I_T, I_T_L, tag, or transaction context and translate `TC_NO_ERROR` to libsas TMF completion. `asd_I_T_nexus_reset()` suspends transmit, issues a libsas phy reset, clears outstanding commands, and retries resume. `asd_abort_task()` sends `SCB_ABORT_TASK`, copies returned tag information back to the target ASCB, then either clears nexus, waits for late completion, or maps sequencer TMF errors to SAS TMF responses. Generic SSP TMFs build task-management IUs and optionally clear I_T_L after success.

Persistence behavior: mutates task ASCB completion pointers, task tags/tag_valid, task `lldd_task`, timers, and ASCB lifecycle. It also changes sequencer queue/nexus state through clear-nexus SCBs and may reset phys through libsas.

Dependencies and integration points: depends on `aic94xx_task.c`-created ASCB/task state, `aic94xx_sas.h` TMF/clear-nexus layouts, ASCB posting/freeing, EDB invalidation, and libsas TMF/phy reset contracts. Error handlers above this file must set aborted state before abort calls as documented.

Risks: many stack completion/status objects are referenced by ASCB callbacks, so timer deletion and completion ordering are critical. If clear-nexus resume fails, the sequencer can remain suspended for a device. Return values mix done-list opcodes and SAS TMF responses in some paths, requiring careful caller interpretation. Races with normal task completion are expected and handled but fragile.

Test signals: abort of pending, already-done, tag-known, tag-unknown, and device-lost tasks; QUERY TASK for present/missing task; abort/clear task set and LU reset on SSP devices; I_T reset for SATA versus SSP reset type; TMF timeout; EDB response parsing; and clear-nexus resume retry failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_tmf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/am53c974.c -->
## sources/distributed-fs/ceph-client/drivers/scsi/am53c974.c

Purpose: this is a PCI driver for AMD AM53C974/Tekram DC-390 style ESP SCSI controllers. It plugs controller-specific register, DMA, EEPROM, probe, and remove behavior into the shared `esp_scsi` core.

Important APIs/types/functions: main driver callbacks are `pci_esp_probe_one()` and `pci_esp_remove_one()`, registered through `module_pci_driver()`. The `esp_driver_ops` implementation provides register I/O, IRQ pending checks, DMA reset/drain/invalidate/error/start, and DMA length limiting. EEPROM helpers bit-bang DC-390 config data and apply SCSI ID, tag count, and active-negation settings. Module parameters are `am53c974_debug` and `am53c974_fenab`.

Control flow and state: probe enables the PCI device, sets a 32-bit DMA mask, allocates a SCSI host and private state, requests BAR regions, maps registers, allocates a coherent command block, registers the shared IRQ with `scsi_esp_intr`, reads EEPROM, initializes host IDs/limits/clock, and registers with `scsi_esp_register()`. DMA start programs ESP transfer count and controller DMA registers, emits the ESP command, then starts DMA. IRQ pending caches DMA status before the ESP core handles interrupts. Removal unregisters ESP, frees IRQ/DMA/register/PCI resources, and drops the SCSI host.

Persistence behavior: no disk persistence. Runtime state includes `pci_esp_priv.dma_status`, ESP config fields, EEPROM-derived SCSI ID/tag/active-negation settings, PCI drvdata, mapped MMIO, IRQ registration, and coherent command memory.

Dependencies and integration points: depends on Linux PCI, DMA, IRQ, module, and SCSI host APIs plus the common `esp_scsi` core and `scsi_esp_template`. PCI ID table binds AMD SCSI devices; module alias preserves `tmscsim` compatibility.

Risks: DMA residual BLAST handling is explicitly noted as untested. DMA direction logic is inverted for writes and easy to regress. FENAB changes transfer-count width and DMA length limits. Probe failure labels must stay paired with resources. EEPROM access uses magic PCI config offsets/timings and weak validation via checksum.

Test signals: PCI probe/remove, IRQ sharing, DMA read/write with and without FENAB, transfers crossing 24-bit boundaries, DMA error/abort paths, FIFO command submission workaround, valid and invalid DC-390 EEPROM contents, module parameters, and cleanup under every probe failure injection point.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/am53c974.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/arcmsr/Makefile -->
## sources/distributed-fs/ceph-client/drivers/scsi/arcmsr/Makefile

Purpose: this Makefile wires the ARECA ARCMSR PCI-X/PCIe SATA RAID SCSI driver into the kernel build.

Important APIs/types/functions: it declares the composite object list `arcmsr-objs := arcmsr_attr.o arcmsr_hba.o` and the Kconfig-controlled build target `obj-$(CONFIG_SCSI_ARCMSR) := arcmsr.o`.

Control flow and state: no runtime flow. During kbuild, enabling `CONFIG_SCSI_ARCMSR` links `arcmsr_attr.o` and `arcmsr_hba.o` into `arcmsr.o`, which is then built as built-in or module according to the config value.

Persistence behavior: none. It only affects build artifacts.

Dependencies and integration points: depends on the surrounding kernel SCSI Makefile descending into `drivers/scsi/arcmsr` and on `CONFIG_SCSI_ARCMSR` being defined by Kconfig. It assumes `arcmsr_attr.c` and `arcmsr_hba.c` exist in the same directory.

Risks: small but build-breaking if object names diverge from source files or Kconfig symbol changes. No conditional per-feature object selection is present, so both objects are always required when the driver is enabled.

Test signals: `make M=drivers/scsi/arcmsr` or an equivalent tree build with `CONFIG_SCSI_ARCMSR=m/y`, plus a disabled-config build verifying the object is omitted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/arcmsr/Makefile -->
