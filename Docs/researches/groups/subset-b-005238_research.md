# subset-b-005238 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/arm/queue.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/arm/queue.c

Purpose: implements a small exported SCSI command queue helper for ARM/Acorn-style SCSI host drivers. It stores `struct scsi_cmnd *` values in a fixed pool of queue entries and supports ordered insertion, target/lun/tag lookup, exclusion by busy target/lun bitmap, and command removal.

Important APIs/types/functions: private `QE_t` wraps a `list_head`, `SCpnt`, and optional debug magic. `queue_initialise()` allocates `NR_QE` entries with `kmalloc_objs()` and populates the free list. `__queue_add()` moves an entry from `free` to `head`, optionally at the head for priority commands. `queue_remove()`, `queue_remove_exclude()`, `queue_remove_tgtluntag()`, `queue_remove_cmd()`, `queue_remove_all_target()`, and `queue_probetgtlun()` traverse or modify the queue. All public symbols are exported for other SCSI drivers.

Control flow: callers initialize `Queue_t`, enqueue commands through the macros in `queue.h` or direct `__queue_add()`, then dequeue based on scheduling needs. `__queue_remove()` is the central primitive: it deletes a used entry, marks it free, pushes it back to the free list, and returns the stored command. Most operations take `queue_lock` with IRQ saving, making them usable in interrupt-adjacent host-driver paths.

State and persistence: all state is in-memory and per `Queue_t`: active commands in `head`, available entry objects in `free`, and the original allocation pointer in `alloc`. There is no persistence across driver unload or host reset. Debug magic detects use/free list corruption during development.

Dependencies and integration: depends on Linux list APIs, spinlocks, slab allocation, SCSI command/device APIs, request tags via `scsi_cmd_to_rq()`, and SCSI constants such as `REQUEST_SENSE`. Integration is by exported helper symbols consumed by legacy SCSI host drivers.

Risks and test signals: queue depth is fixed at 32 entries, so callers must handle enqueue failure. `queue_remove_all_target()` removes entries during `list_for_each()` without using a safe iterator; because `__queue_remove()` relinks the current node onto the free list, this is a list-walk corruption risk if more matching or nonmatching entries follow. `queue_remove_exclude()` indexes `target * 8 + (lun & 7)`, so high LUNs alias. Test signals are enqueue failure at capacity, REQUEST_SENSE head insertion, removal by tag, excluded busy LUN scheduling, concurrent IRQ-safe access, and debug-magic BUGs under misuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/arm/queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/arm/queue.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/arm/queue.h

Purpose: declares the public contract for the ARM SCSI queue helper implemented in `queue.c`.

Important APIs/types/functions: `Queue_t` owns the active list, free list, spinlock, and allocation base. The header declares initialization, teardown, generic dequeue, exclude-based dequeue, target/lun/tag dequeue, target-wide removal, target/lun probing, command-specific removal, and raw `__queue_add()`. `queue_add_cmd_ordered()` places `REQUEST_SENSE` at the head; `queue_add_cmd_tail()` appends normally.

Control flow: host drivers include this header, allocate a `Queue_t`, call `queue_initialise()`, enqueue commands through the macros, dequeue with the selector matching their scheduler or error-recovery path, and finally call `queue_free()`.

State and persistence: `Queue_t` is intentionally small and caller-owned. The helper manages only volatile command pointers and list nodes; commands themselves remain owned by the SCSI mid-layer or host driver.

Dependencies and integration: requires prior visibility of `struct list_head`, `spinlock_t`, `struct scsi_cmnd`, and `REQUEST_SENSE` through including C files. It is a narrow integration layer between SCSI host drivers and the queue implementation exports.

Risks and test signals: the macro API evaluates `SCpnt` more than once, so callers should pass stable expressions. The header exposes `__queue_add()`, allowing callers to bypass ordering policy. Build tests should compile users with modern SCSI headers; behavioral tests should verify macro ordering and every declared symbol links to the exported implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/arm/queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/atari_scsi.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/atari_scsi.c

Purpose: implements the Atari TT/Falcon native SCSI platform driver around the shared NCR5380 core. It supplies Atari-specific register access, DMA setup/residual handling, interrupt dispatch, ST-DMA locking, platform probe/remove, and SCSI host-template wiring.

Important APIs/types/functions: NCR5380 integration is provided by macro aliases such as `NCR5380_read`, `NCR5380_write`, `NCR5380_queue_command`, and DMA hooks before including `NCR5380.h` and `NCR5380.c`. TT and Falcon hardware paths use `scsi_tt_intr()`, `scsi_falcon_intr()`, `atari_scsi_dma_setup()`, `atari_scsi_dma_xfer_len()`, `atari_scsi_tt_reg_read/write()`, and `atari_scsi_falcon_reg_read/write()`. Probe/remove are `atari_scsi_probe()` and `atari_scsi_remove()`. Error handling uses `atari_scsi_host_reset()`.

Control flow: platform probe selects TT or Falcon register access, applies module/boot parameters, derives host id from setup or NVRAM, allocates Falcon ST-RAM bounce memory when needed, allocates and initializes an NCR5380-backed `Scsi_Host`, requests IRQs for TT, resets/scans the bus, then registers the SCSI host. Command execution is mostly in the NCR5380 core; this file participates when the core requests DMA setup, residual length, register access, DMA lock acquisition, or reset. Interrupts stop or inspect DMA, calculate residual bytes, copy Falcon bounce-buffer reads, then invoke `NCR5380_intr()`.

State and persistence: runtime state is in file-static DMA variables: residual length, start address, active flag, Falcon bounce buffer, physical bounce address, original read destination, and ST-RAM address mask. Module parameters control queue depth, commands per LUN, scatter-gather size, host ID, and Toshiba delay. No driver settings are persisted; NVRAM is only read for an existing TT host-id setting.

Dependencies and integration: depends on Atari m68k hardware definitions, MFP delays, Atari ST-DMA locking (`stdma_try_lock`, `stdma_release`), Atari STRAM allocation, NVRAM, platform bus, SCSI host APIs, and the NCR5380 core. Falcon integration is constrained by shared DMA ownership with IDE/floppy and by ST-DMA transfer granularity.

Risks and test signals: TT and Falcon paths have very different DMA semantics and many busy waits. Falcon reads cannot safely DMA non-512-byte byte-mode transfers, so `falcon_classify_cmd()` and `atari_scsi_dma_xfer_len()` are critical. Bounce-buffer copies rely on transfer-length limiting to `STRAM_BUFFER_SIZE`. Reset must avoid leaving ST-DMA locked or active. Test signals include TT and Falcon probe, IRQ handling during disconnect/reselect, residual accounting for partial DMA, non-ST-RAM bounce reads/writes, host reset during active DMA, module parameter overrides, suspend/resume-like reinitialization through reset, and scan behavior with TT NVRAM host IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/atari_scsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/atp870u.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/atp870u.c

Purpose: implements the PCI SCSI host driver for ACARD/ARTOP ATP870U-family adapters, including AEC671x, ATP880, and ATP885 variants. It manages PCI resources, chip initialization, bus scanning and negotiation, SCSI command queueing, PRD DMA programming, interrupt-driven completion, and SCSI host registration.

Important APIs/types/functions: low-level I/O helpers wrap `inb/outb/outw/outl` against base, channel I/O, and PCI windows. `atp870u_intr_handle()` is the interrupt state machine. `atp870u_queuecommand_lck()` accepts SCSI commands into a per-channel ring. `send_s870()` programs command registers, maps DMA with `scsi_dma_map()`, builds PRD entries, and starts device-to-host or host-to-device DMA. `tscam()` and `fun_scam()` implement SCAM ID assignment. `atp_is()` scans targets and negotiates wide/synchronous/Ultra modes. `atp870_init()`, `atp880_init()`, and `atp885_init()` perform chip-specific setup. `atp870u_probe()` and `atp870u_remove()` own PCI lifecycle.

Control flow: PCI probe enables the device, enforces a 32-bit DMA mask, requests regions, allocates `Scsi_Host` plus `struct atp_unit`, allocates coherent PRD tables for every channel/target, runs chip-specific initialization and SCSI device discovery, registers the interrupt, adds the host, and scans. Queueing validates channel and active target, advances a ring tail, stores the command, and may call `send_s870()` immediately. Interrupts identify the active channel, decode controller status, handle disconnect/reselect and transfer phase changes, adjust PRD position for residual transfers, unmap DMA, complete commands with `scsi_done()`, clear `curr_req`, decrement `working`, and schedule more queued work.

State and persistence: `struct atp_unit` in host private data holds per-channel ports, queue head/tail, active and wide target bitmaps, host IDs, current commands per target, transfer direction, last and remaining transfer lengths, PRD virtual/bus addresses, and chip status flags. All state is volatile and rebuilt on probe. Adapter EEPROM or setup data is read into speed/global maps but not persisted by this driver.

Dependencies and integration: integrates with PCI, Linux DMA mapping, SCSI mid-layer host templates, IRQ handling, proc/seq show hooks, and legacy port I/O. It exposes a SCSI host template with `queuecommand`, abort diagnostics, BIOS geometry, queue depth `qcnt`, scatter-gather size `ATP870U_SCATTER`, and PCI device IDs.

Risks and test signals: many polling loops have no timeout and can hang on broken hardware. `scsi_dma_map()` return is not checked for negative errors before `scsi_for_each_sg()`. The ring uses one empty slot to distinguish full from empty and returns `DID_BUS_BUSY` on overflow. `atp870u_abort()` logs state and returns `SUCCESS` without actually aborting hardware, which can mislead error recovery. Status handling is dense and chip-specific, especially ATP885 CRC and reselect logic. Test signals include probe/remove failure-path cleanup, queue wrap and full handling, missing-target fake timeout, DMA map/unmap correctness, PRD splitting at 64 KiB boundaries, reselect after disconnect, ATP870/880/885 initialization paths, and negotiated wide/sync mode discovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/atp870u.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/atp870u.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/atp870u.h

Purpose: defines constants and the host-private data structure used by the ATP870U-family SCSI driver.

Important APIs/types/functions: constants define command/sense limits, queue depth `qcnt`, scatter-gather limit, adapter/target counts, max sectors, and ATP880/ATP885 PCI device IDs. `struct atp_unit` stores base/I/O/PCI ports, per-channel queue state, target maps, speed/async data, queued commands, nested per-target DMA/PRD/current-command state, and pointers to `Scsi_Host` and `pci_dev`.

Control flow: the header has no executable flow. `atp870u.c` allocates `struct atp_unit` as SCSI host private data, initializes its arrays in `atp870u_init_tables()`, mutates it in queue/interrupt paths, and frees coherent PRD tables during teardown.

State and persistence: this structure is the volatile state container for the whole adapter. Per-target `prd_table` memory is coherent DMA memory, `curr_req` tracks the active command, and maps such as `active_id`, `wide_id`, `ultra_map`, and `async` summarize discovery/negotiation.

Dependencies and integration: depends on kernel integer and DMA address types plus SCSI/PCI structures supplied by the C file. It forms the internal ABI between initialization, interrupt, queueing, and scan code in `atp870u.c`.

Risks and test signals: fixed dimensions assume at most two channels and sixteen SCSI IDs. PRD table size is hardcoded in the C file at 1024 bytes and must remain sufficient for `ATP870U_SCATTER` entries plus splitting. Test signals are compile-time structure use across all chip variants, coherent allocation/free for every populated `id[channel][target]`, and queue arrays cleared before scan or command submission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/atp870u.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/be2iscsi/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/scsi/be2iscsi/Kconfig

Purpose: declares the `BE2ISCSI` kernel configuration option for the Emulex/Broadcom BladeEngine 2/OneConnect 10Gbps iSCSI offload driver.

Important APIs/types/functions: `config BE2ISCSI` is a tristate option labeled `Emulex 10Gbps iSCSI - BladeEngine 2`. It depends on `PCI`, `SCSI`, and `NET`, and selects `SCSI_ISCSI_ATTRS`, `ISCSI_BOOT_SYSFS`, and `IRQ_POLL`.

Control flow: there is no runtime flow. Kconfig decides whether the driver is built in, built as `be2iscsi.ko`, or omitted. Selected symbols ensure the transport attributes, iSCSI boot sysfs support, and IRQ polling infrastructure are present.

State and persistence: state is the generated kernel configuration only. The choice persists in `.config` and controls build outputs.

Dependencies and integration: integrates the driver into the SCSI configuration tree and expresses required subsystems for code in `be_main.c`, `be_cmds.c`, `be_mgmt.c`, and `be_iscsi.c`.

Risks and test signals: missing or stale selects would show up as unresolved symbols or disabled sysfs/transport features. Build tests should cover `BE2ISCSI=m`, `BE2ISCSI=y`, and dependency-disabled configurations such as `NET=n` or `PCI=n`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/be2iscsi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/be2iscsi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/scsi/be2iscsi/Makefile

Purpose: defines the Kbuild composition of the `be2iscsi` driver.

Important APIs/types/functions: `obj-$(CONFIG_BE2ISCSI) += be2iscsi.o` declares the composite object. `be2iscsi-y := be_iscsi.o be_main.o be_mgmt.o be_cmds.o` links transport/session logic, main HBA and I/O logic, firmware management helpers, and mailbox/MCC command helpers.

Control flow: Kbuild evaluates this file at build time only. Runtime initialization is provided by the linked C files, primarily `be_main.c`.

State and persistence: no runtime state is held here; it controls reproducible object composition from `.config`.

Dependencies and integration: must stay aligned with cross-file prototypes in `be.h`, `be_cmds.h`, `be_iscsi.h`, `be_main.h`, and `be_mgmt.h`.

Risks and test signals: object-list drift causes link failures or missing transport callbacks. Test signals are clean modular and built-in builds with `CONFIG_BE2ISCSI` enabled, plus ensuring all helper implementations referenced by the transport template and PCI driver are linked into the composite object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/be2iscsi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/be2iscsi/be.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/be2iscsi/be.h

Purpose: provides core BladeEngine iSCSI controller data structures and helper primitives shared by BE2 iSCSI command, management, and main driver code.

Important APIs/types/functions: `struct be_dma_mem` describes DMA allocations. `struct be_queue_info` models firmware rings with DMA memory, length, entry size, id, head/tail, creation flag, and used count. Queue helpers include `MODULO()`, `index_inc()`, `queue_head_node()`, `queue_tail_node()`, `queue_get_wrb()`, and head/tail increment wrappers. `struct be_eq_obj`, `struct be_mcc_obj`, `struct beiscsi_mcc_tag_state`, and `struct be_ctrl_info` hold event queues, MCC queues, mailbox DMA memory, locks, wait queues, and MCC tag bookkeeping. AMAP helpers set/get packed firmware bitfields, and `swap_dws()` handles big-endian dword conversion.

Control flow: this header supplies inline mechanics used whenever code allocates a WRB, advances a queue, waits on a mailbox tag, or fills firmware bitfield contexts. `be_cmds.c` uses `be_ctrl_info` for mailbox/MCC serialization and `be_queue_info` for ring creation and command submission.

State and persistence: controller state is volatile and tied to a PCI function. Mailbox memory, MCC queue state, tag arrays, tag status, and tag wait queues live in `be_ctrl_info` for the lifetime of the HBA. Firmware-assigned queue IDs are cached in `be_queue_info.created/id`.

Dependencies and integration: includes PCI, VLAN, and IRQ polling headers, then includes `be_cmds.h`, making command structures part of the shared controller contract. It integrates tightly with `be_main.h` for `struct beiscsi_hba` and with firmware queue formats in `be_cmds.h`.

Risks and test signals: `MODULO()` assumes power-of-two queue lengths and warns otherwise; all ring lengths must satisfy that. Pointer arithmetic on `void *` relies on GNU C kernel conventions. MCC tag state uses bit flags and DMA memory retention for timeout cleanup, so races between timeout and late completion are important. Test signals include endian builds, queue wraparound, MCC tag exhaustion/reuse, late completion cleanup, and firmware context bitfield encoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/be2iscsi/be.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/be2iscsi/be_cmds.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/be2iscsi/be_cmds.c

Purpose: implements BladeEngine firmware command submission and completion handling for the iSCSI driver. It covers bootstrap mailbox commands, runtime MCC queue commands, queue creation/destruction, default PDU/WRBQ/template/SGL setup, VLAN and firmware queries, function reset, SLI-port initialization, cleanup, and hardware error detection.

Important APIs/types/functions: MCC lifecycle functions include `alloc_mcc_wrb()`, `free_mcc_wrb()`, `be_mcc_notify()`, `beiscsi_mccq_compl_wait()`, `__beiscsi_mcc_compl_status()`, and `beiscsi_process_mcc_compl()`. Bootstrap mailbox handling uses `be_mbox_notify()`, `be_mbox_db_ready_poll()`, and `beiscsi_process_mbox_compl()`. Queue/config commands include `beiscsi_cmd_eq_create()`, `beiscsi_cmd_cq_create()`, `beiscsi_cmd_mccq_create()`, `beiscsi_cmd_q_destroy()`, `be_cmd_create_default_pdu_queue()`, `be_cmd_wrbq_create()`, `be_cmd_iscsi_post_template_hdr()`, `be_cmd_iscsi_post_sgl_pages()`, and `be_cmd_set_vlan()`. Firmware/HBA functions include `beiscsi_check_supported_fw()`, `beiscsi_get_fw_config()`, `beiscsi_get_port_name()`, `beiscsi_set_host_data()`, `beiscsi_set_uer_feature()`, `beiscsi_check_fw_rdy()`, `beiscsi_init_sliport()`, `beiscsi_cmd_iscsi_cleanup()`, `beiscsi_detect_ue()`, and `beiscsi_detect_tpe()`.

Control flow: init-time commands serialize on `mbox_lock`, build one WRB in mailbox DMA memory, ring the MPU mailbox doorbell in high-address then low-address phases, poll ready, and parse the embedded completion. Runtime MCC commands allocate a ring WRB and tag under `mcc_lock`, mark the tag running, ring the MCC doorbell, and wait on a tag-specific wait queue. MCC completion processing decodes tag and WRB index, handles late timeout completions, invokes async callbacks, frees ignored commands, or wakes waiters. Queue creation commands fill firmware contexts with AMAP macros, page-address arrays, and chip-generation-specific formats.

State and persistence: persistent firmware-facing state includes created EQ/CQ/MCC/WRBQ/default-PDU queue IDs, firmware configuration cached in `phba->fw_config`, port name, firmware version string, UER support flags, and HBA state bits. MCC timeout state retains non-embedded DMA command memory until a late firmware completion can free it. Network settings such as VLAN are applied to adapter firmware through MCC commands and may outlive individual sessions according to firmware behavior.

Dependencies and integration: depends on `be_main.h`, `be.h`, `be_mgmt.h`, PCI MMIO/config access, DMA coherent memory, wait queues, mutexes/spinlocks, iSCSI constants, and firmware command layouts from `be_cmds.h`. It is called by main HBA setup/teardown, management helpers, interrupt/completion processing, and transport-facing network/session operations.

Risks and test signals: mailbox polling can set `BEISCSI_HBA_FW_TIMEOUT`; callers must stop issuing commands once the HBA enters error state. `be_cmd_iscsi_post_sgl_pages()` mutates `q_mem->dma` while posting chunks, so callers must not expect that field to remain unchanged unless reset elsewhere. `be_cmd_set_vlan()` returns a tag or zero, so callers need to distinguish submission failure from asynchronous command status. Firmware response formats vary by chip generation and dual-ULP awareness. Test signals include MCC queue full/tag exhaustion, timeout followed by late completion, mailbox ready timeout, BE2/BE3 versus newer context formats, queue create/destroy ordering, firmware config validation bounds, link/SLI async event handling, function reset/special WRB load, and UE/TPE detection paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/be2iscsi/be_cmds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/be2iscsi/be_cmds.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/be2iscsi/be_cmds.h

Purpose: defines the firmware command ABI for the BE2 iSCSI driver: mailbox and MCC WRBs, completions, doorbells, queue contexts, async events, network/iSCSI management payloads, firmware configuration structures, CQE layouts, opcodes, statuses, and exported command-helper prototypes.

Important APIs/types/functions: core transport structures include `struct be_sge`, `struct be_mcc_wrb`, `struct be_mcc_compl`, and `struct be_mcc_mailbox`. Command headers are `be_cmd_req_hdr` and `be_cmd_resp_hdr`. Queue context requests cover EQ, CQ, MCCQ, default PDU queues, WRBQ, template pages, and SGL pages. Management structures cover CHAP/login options, session info, IP address records, gateway/VLAN, TCP connect/offload, invalidation, TCP upload, firmware config, and port name. CQE structures include solicited and driver-message variants plus masks for parsing status, CID, WRB index, residuals, and validity. Prototypes expose all command helpers implemented in `be_cmds.c`.

Control flow: this header is declarative, but its constants drive all firmware interactions. Callers build a WRB, choose a subsystem/opcode, set request length and version, populate payload-specific structures, convert contexts to little endian where needed, post through mailbox or MCC, then parse completion/status fields using the masks defined here.

State and persistence: the structures describe transient command payloads and firmware-owned resources. Some commands create durable firmware objects for the life of the HBA function, such as queue IDs, CID/ICD ranges, and network interface settings. Completion codes and async events update driver state in other files.

Dependencies and integration: depends on iSCSI naming and kernel types made visible through including files. It is included from `be.h` and therefore sits at the center of command exchange among `be_cmds.c`, `be_mgmt.c`, `be_main.c`, and `be_iscsi.c`.

Risks and test signals: this file is layout-sensitive; field size, packing, endian conversion, and opcode values must match firmware. BE2/BE3 and newer chips use different context versions for some commands. The duplicated opcode names for common/iSCSI domains require correct subsystem pairing. Test signals are compile-time size/layout checks where available, successful firmware queue creation on each supported chip generation, network config commands, TCP offload/invalidate/upload, async link/SLI events, and solicited CQE parsing for normal and error completions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/be2iscsi/be_cmds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/be2iscsi/be_iscsi.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/be2iscsi/be_iscsi.c

Purpose: implements the SCSI transport/libiscsi-facing operations for the BE2 iSCSI offload driver. It creates and destroys sessions/connections/endpoints, binds libiscsi objects to firmware CIDs, exposes iface and host parameters, applies network settings, starts hardware offload, reports stats, and disconnects TCP/iSCSI endpoints.

Important APIs/types/functions: session and connection lifecycle functions are `beiscsi_session_create()`, `beiscsi_session_destroy()`, `beiscsi_session_fail()`, `beiscsi_conn_create()`, `beiscsi_conn_bind()`, `beiscsi_conn_start()`, and `beiscsi_conn_get_stats()`. Interface management uses `beiscsi_iface_create_default()`, `beiscsi_iface_destroy_default()`, `beiscsi_iface_set_param()`, `beiscsi_iface_get_param()`, and helpers for IPv4/IPv6/VLAN. Endpoint lifecycle uses `beiscsi_ep_connect()`, `beiscsi_open_conn()`, `beiscsi_ep_poll()`, `beiscsi_ep_disconnect()`, `beiscsi_conn_close()`, `beiscsi_get_cid()`, `beiscsi_put_cid()`, and `beiscsi_free_ep()`. Host information is served by `beiscsi_get_host_param()` and `beiscsi_get_macaddr()`.

Control flow: userspace/open-iscsi creates an endpoint, causing the driver to allocate a `struct iscsi_endpoint`, reserve a firmware CID from the best available ULP, allocate a non-embedded TCP connect command, submit `mgmt_open_connection()`, wait for MCC completion, and store the firmware connection handle. Session creation calls `iscsi_session_setup()` and creates a DMA pool for BHS buffers. Connection creation calls `iscsi_conn_setup()`, while bind verifies the endpoint belongs to the same HBA, stores the CID and endpoint link, records the WRBQ doorbell offset, and installs the connection in `phba->conn_table`. Connection start clamps/encodes negotiated parameters, posts offload state to hardware, and starts libiscsi. Disconnect invalidates and uploads the connection, flushes CQs, returns the CID, clears endpoint/connection tables, and destroys the endpoint.

State and persistence: per-session state includes a BHS DMA pool in `beiscsi_session`. Per-connection state links `iscsi_conn`, `beiscsi_conn`, endpoint, CID, doorbell offset, login progress, and offload parameters. Per-HBA state includes IPv4/IPv6 iface pointers, cached MAC address, interface handle, CID free rings, endpoint array, connection table, link/online bits, and firmware configuration. Network settings are applied to firmware through management commands; driver objects are volatile.

Dependencies and integration: depends on libiscsi, `scsi_transport_iscsi`, netlink attributes, firmware management helpers from `be_mgmt.c`, command helpers from `be_cmds.c`, and main HBA structures from `be_main.h`. It is plugged into the externally defined `beiscsi_iscsi_transport` in `be_main.c`.

Risks and test signals: most operations reject offline/error HBAs, but disconnect deliberately frees CIDs even if firmware close fails to avoid reuse starvation. CID allocation chooses the ULP with more free CIDs and must respect firmware-supported ULP bits. `beiscsi_ep_poll()` simply reports `cid_vld`, because open waits synchronously before returning. Interface setters support only iface number 0 and often translate unsupported parameters to no-op success after logging. Test signals include endpoint connect with link down, CID exhaustion/reuse, bind mismatch across HBAs, session command-depth clamping, parameter clamping before offload, VLAN/IP/gateway set/get, MAC caching, invalidate/upload retry behavior, CQ flush during disconnect, and teardown after login-in-progress failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/be2iscsi/be_iscsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/be2iscsi/be_iscsi.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/be2iscsi/be_iscsi.h

Purpose: declares the BE2 iSCSI transport-facing API implemented by `be_iscsi.c` and consumed by the driver's transport template/main code.

Important APIs/types/functions: prototypes cover default iface create/destroy, iface parameter get/set and visibility, connection/session creation and binding, endpoint connect/poll/disconnect/get-param, host parameter retrieval, MAC formatting, connection parameter setting/start/statistics, and offload helper entry points `beiscsi_offload_connection()` and `beiscsi_offload_iscsi()`.

Control flow: this header has no runtime flow. It lets `be_main.c` register transport callbacks and lets other driver components invoke offload or session failure helpers without depending on `be_iscsi.c` internals.

State and persistence: no state is stored here. The declared functions operate on `beiscsi_hba`, `beiscsi_conn`, `iscsi_cls_session`, `iscsi_cls_conn`, and `iscsi_endpoint` objects owned by the main driver, libiscsi, and transport class.

Dependencies and integration: includes `be_main.h` and `be_mgmt.h`, binding transport declarations to the driver-private structures and firmware management types. It is the local API boundary between iSCSI transport code and the broader BE2 driver.

Risks and test signals: prototype drift affects the transport template and cross-file calls at build time. Because several functions are invoked by SCSI transport class callbacks, return semantics must stay aligned with libiscsi expectations. Test signals are full driver builds, transport registration, iface sysfs visibility, endpoint lifecycle operations, and connection start/stat callbacks through open-iscsi.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/be2iscsi/be_iscsi.h -->
