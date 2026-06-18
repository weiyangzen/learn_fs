# subset-b-005262 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic_trace.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic_trace.c

## Purpose

`fnic_trace.c` implements Cisco FNIC diagnostic trace support. It owns two global circular buffers: a generic FNIC event trace with fixed 64-byte records and an FC control-frame trace with fixed 256-byte records. It also formats driver statistics and live FNIC/iport/tport state into debugfs buffers.

## Important APIs, types, and functions

- `fnic_role_to_str()` converts supported FNIC roles to debug text.
- `fnic_trace_get_buf()` reserves the next generic trace slot under `fnic_trace_lock`.
- `fnic_get_trace_data()` formats generic trace entries, resolving function addresses with `sprint_symbol()` and jiffies timestamps with `jiffies_to_timespec64()`.
- `fnic_get_stats_data()` emits atomic counters from `struct fnic_stats`, including IO, abort, terminate, reset, firmware, VLAN, and miscellaneous counters.
- `fnic_get_debug_info()` prints current adapter, iport, fabric, and tport-list state.
- `fnic_trace_buf_init()`/`fnic_trace_free()` allocate and release the generic trace ring and debugfs hooks.
- `fnic_fc_trace_init()`/`fnic_fc_trace_free()` allocate and release the FC control trace ring.
- `fnic_fc_trace_set_data()` records transmit, receive, and link-event frames.
- `fnic_fc_trace_get_data()` and `copy_and_format_trace_data()` dump FC traces in formatted or raw hex form.

## Control flow

Initialization computes entry counts from module-controlled page counts, allocates one contiguous vmalloc-backed data area plus an array of per-entry offsets, initializes read/write indexes to zero, and registers debugfs files. Producers call `FNIC_TRACE()` or `fnic_fc_trace_set_data()` from driver paths; both advance a write index and, on overlap, advance the read index to preserve ring semantics. Readers snapshot the current read/write indexes while holding the relevant lock and append formatted text into a caller-provided debugfs buffer.

FC receive traces add synthetic Ethernet and FCoE header bytes filled with `0xff` because receive tracepoints do not have those headers available. Formatted FC output prints a timestamp, host number, frame type, length, and frame bytes with line breaks at Ethernet, FCoE, and FC header boundaries.

## State and persistence behavior

All trace state is process-lifetime kernel memory. Generic trace state is `fnic_trace_entries`, `fnic_trace_buf_p`, `fnic_max_trace_entries`, `trace_max_pages`, and `fnic_tracing_enabled`. FC trace state is `fc_trace_entries`, `fnic_fc_ctlr_trace_buf_p`, `fc_trace_max_entries`, `fnic_fc_tracing_enabled`, and `fnic_fc_trace_cleared`. Trace contents persist only until module teardown, explicit clear, wraparound overwrite, or reboot. Stats formatting mutates `stats->stats_timestamps.last_read_time`.

## Dependencies and integration points

The file depends on FNIC private headers `fnic_io.h` and `fnic.h`, trace types from `fnic_trace.h`, debugfs setup/teardown functions implemented elsewhere, SCSI FC transport definitions, vmalloc allocation, spinlocks, kernel time helpers, and kallsyms symbol formatting. It is consumed by FNIC IO, FC control, debugfs, and stats paths.

## Risks and edge cases

- The debugfs buffer size estimate uses `trace_max_pages * PAGE_SIZE * 3`; callers must allocate matching buffers or formatting truncates.
- Trace read formatting holds spinlocks while doing repeated `scnprintf()` and symbol lookup, which can be expensive for large rings.
- `min_t(u8, fc_trc_frame_len, ...)` truncates lengths through an 8-bit type; values above 255 are bounded by the 256-byte record design but must be understood as intentionally clipped.
- `fnic_fc_trace_cleared` causes the FC trace setter to zero the whole buffer under the trace lock on the next write.
- Generic trace stores function addresses differently for 32-bit and 64-bit builds, so mixed assumptions in consumers would corrupt output.

## Test signals

Useful checks include enabling/disabling trace module parameters, reading generic and FC debugfs files after IO, forcing ring wraparound, verifying FC receive traces include synthetic headers, checking formatted and raw FC dump modes, and validating teardown paths with module unload. KASAN/KCSAN coverage around concurrent trace writes and debugfs reads would be valuable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic_trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic_trace.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic_trace.h

## Purpose

`fnic_trace.h` defines the FNIC trace ABI shared between trace producers, trace storage, and debugfs readers. It specifies record sizes, frame-type constants, trace record layouts, global controls, and the `FNIC_TRACE()` producer macro.

## Important APIs, types, and data

- `FNIC_ENTRY_SIZE_BYTES`, `FC_TRC_SIZE_BYTES`, and `FC_TRC_HEADER_SIZE` define generic and FC trace record sizing.
- `FNIC_FC_RECV`, `FNIC_FC_SEND`, and `FNIC_FC_LE` classify FC trace records.
- `fnic_trace_dbg_t` stores ring read/write indexes plus the per-entry address table.
- `fnic_dbgfs_t` wraps a debugfs memory buffer and current length.
- `struct fnic_trace_data` is a packed 64-byte generic trace record with timestamp, function address, host number, tag, and five data words.
- `struct fc_trace_hdr` prefixes each 256-byte FC trace slot with a real-time timestamp, host number, frame type, and frame length.
- `FC_TRACE_ADDRESS()` returns the payload address after an FC trace header.
- `FNIC_TRACE()` performs the fast-path conditional trace write and records jiffies, function address, host/tag, and five caller values.

## Control flow

The header does not execute by itself, but the macro expands directly into producer sites. If `fnic_tracing_enabled` is true, the macro obtains a slot from `fnic_trace_get_buf()`, fills architecture-dependent timestamp/address fields, then records caller-supplied values. Function prototypes connect the storage implementation, debugfs setup/teardown, and FC trace helpers.

## State and persistence behavior

The header declares global trace configuration and enable flags owned by implementation files or module parameters. Trace records are packed and fixed-size so rings can be indexed by simple offsets. No state is allocated in the header.

## Dependencies and integration points

It relies on kernel types such as `u32`, `u64`, `ssize_t`, `loff_t`, and `struct timespec64`, and on `jiffies` being available at macro expansion sites. It is included by FNIC driver code that emits trace points and by debugfs code that reads the trace buffers.

## Risks and edge cases

- `FNIC_TRACE()` is a multi-statement macro without `do { } while (0)`, so use in conditional contexts requires care.
- The `FNIC_TRACE_ENTRY_SIZE` name is misleading: it computes remaining payload bytes after the packed trace struct and is zero with the current 64-byte structure.
- Packed structures avoid padding drift but can generate unaligned accesses on some architectures.
- The comment contains a typo, but the important semantic point is that frame type bytes are printable ASCII-like markers.

## Test signals

Build tests should cover all FNIC translation units that include the macro. Runtime tests should verify that records generated by `FNIC_TRACE()` decode correctly on both 32-bit and 64-bit configurations and that FC frame headers lead to the expected payload address.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/rq_enet_desc.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/fnic/rq_enet_desc.h

## Purpose

`rq_enet_desc.h` defines the 16-byte Ethernet receive queue descriptor used by Cisco vNIC/FNIC receive queues. It provides encode/decode helpers for DMA address, receive descriptor type, and buffer length.

## Important APIs, types, and data

- `struct rq_enet_desc` contains a little-endian 64-bit buffer address, a little-endian combined length/type field, and reserved bytes.
- `enum rq_enet_type_types` defines SOP-only and non-SOP descriptor type values.
- `RQ_ENET_LEN_MASK` and `RQ_ENET_TYPE_MASK` bound the 14-bit length and 2-bit type fields.
- `rq_enet_desc_enc()` writes CPU values into descriptor endian format.
- `rq_enet_desc_dec()` reads descriptor values back into CPU-endian outputs.

## Control flow

Receive-buffer preparation calls `rq_enet_desc_enc()` before posting descriptors to hardware. Debug or cleanup paths can call `rq_enet_desc_dec()` to inspect descriptor contents. The type is stored in bits above the length inside `length_type`.

## State and persistence behavior

The descriptor is persistent only as DMA ring memory shared with hardware. The header owns no mutable state.

## Dependencies and integration points

It depends on Linux endian helpers `cpu_to_le64()`, `cpu_to_le16()`, `le64_to_cpu()`, and `le16_to_cpu()`. It is integrated with `vnic_rq` rings and any FNIC receive path that posts Ethernet/FCoE receive buffers.

## Risks and edge cases

- Length is truncated to 14 bits; callers must ensure buffer sizes fit.
- Reserved type values are not rejected by the encode helper.
- The descriptor must be fully initialized before the RQ posted index is advanced, which is enforced by queue-level memory barriers rather than this header.

## Test signals

Unit-style encode/decode round trips for boundary lengths and all type values are useful. Runtime receive tests should verify hardware consumes posted descriptors and reports completions with the expected buffer address and length.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/rq_enet_desc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_cq.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_cq.c

## Purpose

`vnic_cq.c` implements allocation, initialization, cleanup, and release of vNIC completion queues. Completion queues are DMA rings populated by hardware and consumed by the driver.

## Important APIs, types, and functions

- `vnic_cq_alloc()` binds a CQ to a BAR resource and allocates its descriptor ring.
- `vnic_cq_init()` programs the CQ control registers: ring base/size, flow control, color, head/tail, interrupt controls, completion entry/message settings, and message address.
- `vnic_cq_clean()` resets software consumer state, hardware head/tail/color, and clears ring memory.
- `vnic_cq_free()` releases the coherent descriptor ring.

## Control flow

Probe/setup calls `vnic_cq_alloc()` for each completion queue and later `vnic_cq_init()` with interrupt and ring parameters. Interrupt or poll paths consume completions through the inline service function in `vnic_cq.h`. Reset/shutdown calls `vnic_cq_clean()` or `vnic_cq_free()`.

## State and persistence behavior

Persistent queue state is split between host memory (`cq->ring.descs`, `cq->to_clean`, `cq->last_color`) and memory-mapped control registers. `vnic_cq_clean()` sets software consumption back to descriptor zero and color zero while programming hardware tail color to one.

## Dependencies and integration points

The file depends on `vnic_dev_alloc_desc_ring()`, `vnic_dev_get_res()`, `vnic_dev_clear_desc_ring()`, and `writeq()/iowrite32()` register accessors. It is used by FNIC queue setup and by WQ/RQ completion handlers.

## Risks and edge cases

- Incorrect color initialization causes completions to be skipped or reread.
- Register programming must match the hardware's control layout from `struct vnic_cq_ctrl`.
- The code assumes descriptor memory allocation and MMIO resource discovery already respect device alignment requirements.

## Test signals

Tests should allocate/init/clean CQs under probe and reset, verify completions advance `to_clean` and wrap color correctly, and exercise both interrupt-enabled and CQ-entry/message modes where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_cq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_cq.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_cq.h

## Purpose

`vnic_cq.h` defines vNIC completion queue control registers, software queue state, symbol-renaming aliases for FNIC, and the inline completion service loop.

## Important APIs, types, and data

- `struct vnic_cq_ctrl` maps completion queue MMIO registers.
- `struct vnic_cq` stores queue identity, device pointer, MMIO control pointer, DMA ring, next descriptor to clean, and expected color.
- `vnic_cq_service()` decodes `struct cq_desc` records, calls a supplied queue-service callback, advances the clean index, toggles color on wrap, and stops at a work budget.
- Function prototypes expose allocation, initialization, cleanup, and release.

## Control flow

The service loop reads the descriptor at `to_clean`, decodes type/color/queue/completed index, and processes entries while hardware color differs from software `last_color`. Each accepted completion is passed to the caller's callback, then the consumer advances and wraps as necessary.

## State and persistence behavior

The in-memory `to_clean` and `last_color` fields are the key persistent software state between interrupts or poll cycles. Descriptor contents are device DMA state. The header itself allocates no state.

## Dependencies and integration points

It depends on `cq_desc.h` for descriptor decoding and `vnic_dev.h` for rings. It integrates with WQ, RQ, copy WQ, and FNIC completion paths.

## Risks and edge cases

- `work_done` is incremented after reading the next descriptor, so callbacks must not assume exactly one descriptor is consumed after a break.
- A callback returning nonzero stops service without advancing the current descriptor, which is intentional but can stall if the callback condition is persistent.
- Correct color behavior depends on hardware writing descriptors before flipping color.

## Test signals

Useful tests include synthetic rings with color transitions, budget-limited polling, callback-stop behavior, and wraparound at `desc_count`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_cq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_cq_copy.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_cq_copy.h

## Purpose

`vnic_cq_copy.h` provides the specialized completion queue service helper for FNIC copy work queues, where completion descriptors are FCPIO firmware request records rather than generic CQ descriptors.

## Important APIs, types, and data

- `vnic_cq_copy_service()` reads `struct fcpio_fw_req` entries from a `struct vnic_cq` ring.
- It uses `fcpio_color_dec()` to check ownership/color.
- The callback receives the vNIC device, queue index, and firmware request descriptor.

## Control flow

The helper starts at `cq->to_clean`, processes entries while descriptor color differs from `cq->last_color`, invokes the caller callback, advances and wraps the clean pointer, toggles software color on wrap, and honors a work budget.

## State and persistence behavior

State is inherited from `struct vnic_cq`: `to_clean`, `last_color`, and DMA ring memory. No additional state is owned by this header.

## Dependencies and integration points

It depends on FCPIO descriptor definitions in `fcpio.h` and generic CQ state from `vnic_cq.h`. It is used by FNIC firmware completion processing for copy WQs.

## Risks and edge cases

- The helper assumes the ring descriptor size matches `struct fcpio_fw_req`.
- Callback nonzero return leaves the current descriptor unconsumed.
- Color mismatch is the sole ownership test; descriptor initialization ordering depends on hardware and queue barriers.

## Test signals

Synthetic FCPIO completion rings should validate color handling, callback stop, budget exhaustion, and wraparound behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_cq_copy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_dev.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_dev.c

## Purpose

`vnic_dev.c` is the shared Cisco vNIC device-control layer used by FNIC. It discovers hardware resources from BAR0, allocates coherent descriptor rings, wraps firmware device commands, exposes link/stats/notification helpers, and registers/unregisters the private `struct vnic_dev`.

## Important APIs, types, and functions

- `struct vnic_dev` stores PCI/device-private pointers, discovered resources, command backend, DMA notification/stat/fw buffers, interrupt mode, and devcmd2 state.
- `vnic_dev_discover_res()` parses the BAR0 resource table and records WQ/RQ/CQ/interrupt/devcmd resources.
- `vnic_dev_get_res_count()` and `vnic_dev_get_res()` return resource counts and MMIO addresses.
- `vnic_dev_alloc_desc_ring()`/`vnic_dev_free_desc_ring()` allocate 512-byte-aligned coherent descriptor rings.
- `vnic_dev_cmd1()` implements the legacy MMIO devcmd register path.
- `vnic_dev_cmd2()` implements the queued devcmd2 path using a WQ plus a result ring and color bit.
- `vnic_dev_cmd_init()` selects devcmd2 when present and falls back to devcmd1.
- Helper commands include firmware info, dev-specific values, stats dump/clear, open/close/init/enable/disable, reset status, MAC address, packet filter, address add/delete, notification buffer setup, link status, port speed, MTU, message level, and link-down count.

## Control flow

Registration allocates a `struct vnic_dev`, binds PCI/private pointers, and discovers BAR resources. Command initialization checks for `RES_TYPE_DEVCMD2`; if present it allocates a devcmd2 WQ and results ring, initializes firmware with `CMD_INITIALIZE_DEVCMD2`, and then routes future commands through queued descriptors. Otherwise it uses the legacy status/cmd/args MMIO block.

Legacy commands check `STAT_BUSY`, write input args, post the command, poll status in 100 microsecond intervals, translate firmware errors, and read output args. Devcmd2 commands check queue fullness through posted/fetch indexes, fill a command descriptor, post it, and poll the next result entry until its color matches.

## State and persistence behavior

The object caches DMA buffers for notification, stats, and firmware info. `vdev->args[]` is scratch space for command execution. Resource mappings persist for the life of the device. Notification state is shared with firmware through a checksum-protected coherent structure copied by `vnic_dev_notify_ready()`.

## Dependencies and integration points

The file depends on PCI DMA APIs, `vnic_resource.h`, `vnic_devcmd.h`, `vnic_wq.h`, and `vnic_stats.h`. It is the lower layer for FNIC queue setup, firmware control, link monitoring, and statistics retrieval.

## Risks and edge cases

- `vnic_dev_cmd1()` maps firmware error indexes through a small local array; unexpected firmware error values would index out of bounds.
- Devcmd2 treats `0xffffffff` posted/fetch indexes as surprise-removal evidence and returns `-ENODEV`.
- `vnic_dev_spec()` copies a value into the caller even if the command returned an error.
- Notification checksum polling loops until a consistent copy appears; corrupted shared memory could spin longer than expected.
- `vnic_dev_set_default_vlan()` returns the command return code cast to `u16`, not the output argument, which is suspicious against the command comment.

## Test signals

Tests should exercise BAR resource parsing, ring alignment, devcmd1 fallback, devcmd2 initialization and teardown, command timeout/error paths, stats dump, notification checksum reads, link-state helpers, and surprise-removal handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_dev.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_dev.h

## Purpose

`vnic_dev.h` declares the vNIC device-control interface and shared descriptor-ring structure used by FNIC queue, interrupt, and firmware-command code.

## Important APIs, types, and data

- The top block aliases generic `vnic_dev_*` names to `fnic_dev_*` names to avoid built-in symbol clashes with Cisco ENIC.
- `readq()`/`writeq()` fallbacks implement 64-bit MMIO accesses when the architecture does not provide them.
- `enum vnic_dev_intr_mode` records INTx, MSI, or MSI-X mode.
- `struct vnic_dev_bar` describes mapped PCI BAR state.
- `struct vnic_dev_ring` records coherent descriptor memory, aligned base address, descriptor size/count, and software availability.
- Prototypes cover resource lookup, ring allocation, firmware commands, stats, notification, link helpers, open/close/reset, interrupt mode, and registration.

## Control flow

The header is consumed by queue helpers and the FNIC driver. Probe code registers a device with a BAR, initializes command support, allocates rings through the declared helpers, and later uses command wrappers for device lifecycle and state.

## State and persistence behavior

No state is allocated in the header. The key persistent state described here is `struct vnic_dev_ring`, whose `desc_avail` field is maintained by queue helpers while the DMA memory remains shared with hardware.

## Dependencies and integration points

It depends on `vnic_resource.h` and `vnic_devcmd.h`, kernel DMA/MMIO types, and PCI device structures. It is included by all FNIC vNIC queue/control modules.

## Risks and edge cases

- The alias `#define vnic_dev_desc_ring_size fnic_dev_desc_ring_siz` appears truncated; it must match object naming expectations at compile/link time.
- The fallback `writeq()` writes low then high 32-bit halves; hardware must tolerate that ordering.
- Consumers must maintain ring availability consistently or hardware/software ownership breaks.

## Test signals

Compile coverage with FNIC and ENIC built-in together is important for alias correctness. Runtime ring allocation tests should validate alignment and descriptor counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_devcmd.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_devcmd.h

## Purpose

`vnic_devcmd.h` defines the firmware command ABI for Cisco vNIC devices. It encodes command number, vNIC type, flags, direction, status/error codes, legacy MMIO command registers, and devcmd2 descriptor/result formats.

## Important APIs, types, and data

- `_CMDC()` and `_CMDCNW()` build commands from direction, vNIC type, flags, and command number.
- `_CMD_DIR()`, `_CMD_FLAGS()`, `_CMD_VTYPE()`, and `_CMD_N()` decode command fields.
- `enum vnic_devcmd_cmd` lists commands for firmware info, device spec, stats, packet filters, MAC/address/VLAN, reset/open/init/enable, notification, capabilities, persistent binding, default VLAN, devcmd2 initialization, and other vNIC features.
- `enum vnic_devcmd_status` and `enum vnic_devcmd_error` define status and firmware error values.
- `struct vnic_devcmd_fw_info`, `struct vnic_devcmd_notify`, and `struct vnic_devcmd_provinfo` define command payloads.
- `struct vnic_devcmd` is the legacy MMIO register block.
- `struct vnic_devcmd2` and `struct devcmd2_result` define the queued command interface.

## Control flow

Command users build or select an enum value and pass it with up to 15 arguments to `vnic_dev_cmd()`. The implementation writes arguments for host-to-device commands, posts the command, polls or returns immediately for no-wait commands, and reads arguments for device-to-host commands. Devcmd2 carries the same command enum in WQ descriptors and reads results from a host result ring.

## State and persistence behavior

The header defines on-wire and MMIO layouts only. Persistent command state lives in firmware, MMIO registers, coherent command/result rings, and notification buffers.

## Dependencies and integration points

This ABI is shared by `vnic_dev.c`, queue setup, firmware, and potentially multiple Cisco drivers. The vNIC type bits allow commands to be scoped to Ethernet, FC, SCSI, or all.

## Risks and edge cases

- Command comments are the contract; implementation and firmware must agree on argument sizes and directions.
- `_CMD_NBITS`, `_CMD_VTYPEBITS`, `_CMD_FLAGSBITS`, and `_CMD_DIRBITS` define a packed ABI; changing them would break firmware compatibility.
- Some commands are deprecated but remain defined for compatibility.
- Devcmd2 result errors are stored in an 8-bit field, so error-code space is limited.

## Test signals

Compile-time checks should validate structure sizes and command encoding. Runtime tests should query `CMD_CAPABILITY`, exercise representative read/write/nowait commands, and verify devcmd2 initialization and result color handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_devcmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_intr.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_intr.c

## Purpose

`vnic_intr.c` implements basic allocation, initialization, cleanup, and release of vNIC interrupt control resources.

## Important APIs, types, and functions

- `vnic_intr_alloc()` binds a software interrupt object to a `RES_TYPE_INTR_CTRL` MMIO resource.
- `vnic_intr_init()` programs coalescing timer, coalescing type, mask-on-assertion behavior, and clears credits.
- `vnic_intr_clean()` clears interrupt credits.
- `vnic_intr_free()` drops the MMIO control pointer.

## Control flow

Probe/setup allocates one interrupt control object per vector and initializes coalescing policy. Runtime code uses inline helpers from `vnic_intr.h` to mask, unmask, and return credits. Teardown clears software pointers.

## State and persistence behavior

State is primarily hardware register state in `struct vnic_intr_ctrl`. The software object persists an index, device pointer, and MMIO control address.

## Dependencies and integration points

The file depends on `vnic_dev_get_res()` and the register layout from `vnic_intr.h`. It integrates with FNIC interrupt setup and completion servicing.

## Risks and edge cases

- Missing interrupt control resources return `-EINVAL`, so probe must handle partial resource tables.
- Coalescing timer values are not range-checked here; callers must respect hardware limits.

## Test signals

Tests should cover vector allocation, coalescing initialization, mask/unmask and credit-return behavior, and cleanup during reset/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_intr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_intr.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_intr.h

## Purpose

`vnic_intr.h` defines vNIC interrupt control registers and inline helpers for masking, unmasking, credit accounting, and legacy PBA reads.

## Important APIs, types, and data

- `VNIC_INTR_TIMER_MAX` bounds the coalescing timer.
- `VNIC_INTR_TIMER_TYPE_ABS` and `VNIC_INTR_TIMER_TYPE_QUIET` define coalescing modes.
- `struct vnic_intr_ctrl` maps coalescing, mask, credit, and credit-return registers.
- `struct vnic_intr` stores vector index, device pointer, and MMIO control pointer.
- Inline helpers: `vnic_intr_unmask()`, `vnic_intr_mask()`, `vnic_intr_return_credits()`, `vnic_intr_credits()`, `vnic_intr_return_all_credits()`, and `vnic_intr_legacy_pba()`.

## Control flow

Completion handling typically reads/returns credits and optionally unmasks and resets the coalescing timer in one write to `int_credit_return`. Mask and unmask helpers directly write the `mask` register.

## State and persistence behavior

Interrupt state persists in hardware registers. Credits represent completion/interrupt work acknowledged back to the device.

## Dependencies and integration points

It depends on MMIO accessors and `vnic_dev.h`. It integrates with CQ servicing and interrupt-vector management in FNIC.

## Risks and edge cases

- Credit return packs credits, unmask, and reset-timer bits into one register; incorrect bit shifts can cause interrupt storms or stalls.
- `vnic_intr_legacy_pba()` intentionally reads without clearing, so callers must not assume acknowledgement.
- Timer range checking is left to callers.

## Test signals

Hardware tests should verify interrupt masking, credit return after CQ service, coalescing modes, and legacy PBA behavior under INTx.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_intr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_nic.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_nic.h

## Purpose

`vnic_nic.h` provides a small helper for packing Cisco vNIC NIC configuration bits, mainly RSS, TSO IPID split, and ingress VLAN strip settings.

## Important APIs, types, and data

- `NIC_CFG_*` masks and shifts define fields for RSS default CPU, RSS hash type, RSS hash bits, RSS base CPU, RSS enable, TSO IPID split enable, and ingress VLAN strip enable.
- `vnic_set_nic_cfg()` packs caller-provided values into a 32-bit NIC configuration word.
- The generic helper name is aliased to `fnic_set_nic_cfg` to avoid symbol clashes.

## Control flow

Callers pass desired field values and receive a packed configuration word suitable for a firmware command or NIC config register.

## State and persistence behavior

The header owns no state. The packed value persists only when written by a caller to firmware/hardware.

## Dependencies and integration points

It is shared vNIC NIC configuration code. FNIC may use it when configuring Ethernet/FCoE-facing vNIC behavior.

## Risks and edge cases

- Inputs are masked and silently truncated.
- The helper only builds the word; it does not validate whether a feature is supported by the current firmware.

## Test signals

Encode tests should verify each field's shift and truncation behavior. Firmware tests should validate that the resulting NIC configuration produces expected RSS/offload/VLAN behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_nic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_resource.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_resource.h

## Purpose

`vnic_resource.h` defines the BAR resource-table format used by Cisco vNIC hardware to advertise queue, interrupt, command, and other resource blocks to the driver.

## Important APIs, types, and data

- `VNIC_RES_MAGIC` and `VNIC_RES_VERSION` identify a valid resource table.
- `enum vnic_res_type` defines WQ, RQ, CQ, NIC config, interrupt control/table/PBA, devcmd, pass-through, subvnic, MQ queues, and devcmd2 resource types.
- `struct vnic_resource_header` is the table header.
- `struct vnic_resource` records type, BAR number, BAR offset, and count.

## Control flow

`vnic_dev_discover_res()` reads this table from BAR0, validates header magic/version, iterates entries until `RES_TYPE_EOL`, and stores recognized BAR0 resources in the vNIC device object.

## State and persistence behavior

The resource table is hardware/firmware-provided MMIO metadata. The header defines layout only.

## Dependencies and integration points

It is consumed by `vnic_dev.c` and all queue/interrupt allocation code that requests resources by type and index.

## Risks and edge cases

- Resource type numbering is firmware ABI and must remain stable.
- The discovery implementation only maps BAR0 resources for most queue types; non-BAR0 resources are ignored.
- Counts and offsets must be bounds-checked before being trusted.

## Test signals

Probe tests should validate correct resource discovery, malformed magic/version rejection, out-of-bounds resource rejection, and devcmd2 presence/absence handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_rq.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_rq.c

## Purpose

`vnic_rq.c` implements receive queue allocation, initialization, enable/disable, cleanup, and release for Cisco vNIC rings.

## Important APIs, types, and functions

- `vnic_rq_alloc()` binds an RQ to a `RES_TYPE_RQ` MMIO resource, disables it, allocates a coherent descriptor ring, and builds software buffer metadata.
- `vnic_rq_init()` programs ring base/size, completion queue index, error interrupt settings, clears dropped/error counters, and aligns software pointers to the hardware fetch index.
- `vnic_rq_enable()`/`vnic_rq_disable()` control queue execution and poll for disable acknowledgement.
- `vnic_rq_clean()` calls a buffer-clean callback for outstanding descriptors, realigns to the current fetch index, and clears descriptor memory.
- `vnic_rq_free()` releases descriptor memory and buffer blocks.

## Control flow

Allocation creates a circular list of `struct vnic_rq_buf` entries in 64-entry blocks. Receive-fill code uses inline helpers in `vnic_rq.h` to obtain descriptors and post buffers. Completion processing services buffers up to the completed index. Reset/shutdown disables and cleans the ring.

## State and persistence behavior

Persistent software state includes `to_use`, `to_clean`, `buf_index`, and `ring.desc_avail`. Hardware state lives in RQ control registers: base, size, posted/fetch indexes, CQ index, enable/running, dropped counts, and error status.

## Dependencies and integration points

The file depends on `vnic_dev` ring allocation and resource lookup. It integrates with receive buffer posting, CQ completion handling, and FNIC FCoE receive paths.

## Risks and edge cases

- The circular buffer allocation assumes descriptor count does not exceed the 4096-descriptor block limit.
- `vnic_rq_init()` trusts the current hardware fetch index to index into allocated buffer blocks.
- Disable timeout returns `-ETIMEDOUT`; callers must avoid cleaning an enabled queue.
- The queue posts descriptor indexes in batches controlled by `VNIC_RQ_RETURN_RATE`, so low traffic can leave descriptors unposted until the batching threshold.

## Test signals

Tests should exercise allocation sizes, fill/post/service loops, fetch-index-based initialization, disable timeout handling, dropped-count clearing, and cleanup with outstanding receive buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_rq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_rq.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_rq.h

## Purpose

`vnic_rq.h` defines vNIC receive queue control registers, software buffer metadata, queue state, and inline helpers for posting and servicing receive descriptors.

## Important APIs, types, and data

- `struct vnic_rq_ctrl` maps RQ MMIO registers including ring, posted/fetch, CQ index, enable/running, error, and dropped counts.
- `struct vnic_rq_buf` tracks each posted OS buffer, DMA address, length, descriptor pointer, and circular next pointer.
- `struct vnic_rq` owns queue identity, MMIO pointer, DMA ring, buffer blocks, software producer/consumer pointers, and counters.
- Inline helpers expose descriptor availability, next descriptor/index, buffer-index allocation, descriptor posting, batched posted-index updates, descriptor return, completion service, and ring fill.

## Control flow

Receive fill loops call `vnic_rq_fill()`, which repeatedly invokes a caller buffer-fill callback while more than one descriptor is available. Posting records the OS buffer/DMA metadata, advances `to_use`, decrements availability, and periodically writes the posted index after a memory barrier. Completion service walks from `to_clean` to a completed index, calls a callback for each skipped/final buffer, and optionally returns descriptors immediately.

## State and persistence behavior

`ring.desc_avail`, `to_use`, `to_clean`, and `buf_index` are persistent software ownership state. Hardware ownership is communicated through the posted and fetch indexes.

## Dependencies and integration points

It depends on PCI types, `vnic_dev.h`, and `vnic_cq.h`. FNIC receive paths pair it with `rq_enet_desc.h` descriptors and CQ completion handlers.

## Risks and edge cases

- `vnic_rq_next_buf_index()` monotonically increments without wrap in the helper; callers must treat it as an OS-side identifier, not a ring index.
- Posting updates hardware only every `VNIC_RQ_RETURN_RATE + 1` descriptors.
- `vnic_rq_service()` can call the callback for skipped descriptors before the completed descriptor, so callbacks must handle skipped=true cleanup semantics.

## Test signals

Unit tests should cover descriptor availability math, batched posting boundaries, skipped completion handling, deferred descriptor return, and fill-loop error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_rq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_scsi.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_scsi.h

## Purpose

`vnic_scsi.h` defines FNIC-specific vNIC SCSI configuration limits, defaults, feature flags, and the device-specific FC configuration structure read from firmware/device-specific space.

## Important APIs, types, and data

- `VNIC_FNIC_*` constants bound WQ, copy WQ, RQ, timer, retry, timeout, max data field size, IO throttle, link-down, port-down, LUN, and queue-depth settings.
- `struct vnic_fc_config` contains WWNs, flags, descriptor counts, FLOGI/PLOGI retry and timeout settings, IO throttle, timeout policies, max data field size, FC timers, interrupt settings, queue depth, and copy-WQ count.
- Feature flags include FCP sequence-level error recovery, persistent binding, FIP capability, FC initiator/target, and FC-NVMe initiator/target roles.

## Control flow

FNIC probe/configuration code reads device-specific values into `struct vnic_fc_config`, validates them against the min/max constants, and uses them to size queues and configure FC behavior.

## State and persistence behavior

The structure is configuration state obtained from firmware and then used by the driver at runtime. The header itself owns no mutable state.

## Dependencies and integration points

It integrates `vnic_dev_spec()`/firmware configuration with FNIC queue allocation, libfc/libfcoe behavior, and SCSI host settings.

## Risks and edge cases

- Invalid firmware values must be clamped or rejected by consumers; this header only declares bounds.
- `VNIC_FNIC_FLOGI_RETRIES_DEF` is unlimited (`0xffffffff`), so retry logic must avoid unbounded blocking behavior.
- Feature flags include roles that may not be supported by the rest of this FNIC code path.

## Test signals

Configuration tests should cover boundary values for descriptor counts, timers, retries, max frame size, queue depth, and role/feature flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_scsi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_stats.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_stats.h

## Purpose

`vnic_stats.h` defines firmware-populated vNIC transmit and receive statistics structures used by FNIC/ENIC-style stats dump commands.

## Important APIs, types, and data

- `struct vnic_tx_stats` contains successful frame/byte counters by traffic type, drops, errors, TSO count, and reserved expansion fields.
- `struct vnic_rx_stats` contains receive frame/byte counters, drops, no-buffer count, errors, RSS count, CRC errors, frame-size buckets, and reserved expansion fields.
- `struct vnic_stats` groups TX and RX stats for `CMD_STATS_DUMP`.

## Control flow

`vnic_dev_stats_dump()` allocates coherent `struct vnic_stats` memory and asks firmware to fill it. Higher-level code formats or exports the counters.

## State and persistence behavior

The stats memory is DMA-coherent and persists while the vNIC device object holds it. Counter values are firmware snapshots and can be cleared through `CMD_STATS_CLEAR`.

## Dependencies and integration points

It depends only on fixed-width integer types. It is used by `vnic_dev.c` and FNIC debug/stat reporting paths.

## Risks and edge cases

- Structure layout is firmware ABI; changing field order or size would break stats dumps.
- Reserved fields must remain reserved for compatibility.
- Counters are raw 64-bit firmware values; callers must handle wrap or reset semantics externally.

## Test signals

Stats tests should verify `CMD_STATS_DUMP` fills expected fields, `CMD_STATS_CLEAR` resets counters, and formatted output handles large 64-bit values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_stats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_wq.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_wq.c

## Purpose

`vnic_wq.c` implements transmit/work queue allocation, initialization, enable/disable, cleanup, and release for Cisco vNIC queues. It also supports the special devcmd2 WQ resource.

## Important APIs, types, and functions

- `vnic_wq_alloc()` binds a WQ resource, disables it, allocates a coherent descriptor ring, and creates software buffer tracking.
- `vnic_wq_devcmd2_alloc()` binds the devcmd2 resource and allocates only the descriptor ring required for queued firmware commands.
- `vnic_wq_init_start()` initializes a WQ using explicit fetch and posted indexes, used by devcmd2 setup.
- `vnic_wq_init()` initializes a normal WQ from index zero.
- `vnic_wq_enable()`/`vnic_wq_disable()` control queue execution.
- `vnic_wq_clean()` cleans outstanding buffers, resets indexes/error status, and clears descriptors.
- `vnic_wq_free()` releases ring and buffer-block memory.

## Control flow

Allocation builds a circular chain of `struct vnic_wq_buf` entries that map one-to-one with descriptors. Producers fill the descriptor at `to_use`, call `vnic_wq_post()` from the header, and hardware owns descriptors up to `posted_index`. Completion paths service buffers through `vnic_wq_service()`. Reset/shutdown disables then cleans.

## State and persistence behavior

Persistent software state includes `to_use`, `to_clean`, `ring.desc_avail`, and `pkts_outstanding`. Hardware state is in the WQ control registers: ring base/size, posted/fetch indexes, CQ index, enable/running, DCA, and error interrupt/status fields.

## Dependencies and integration points

It depends on `vnic_dev` for resources and DMA rings. It is used by normal transmit/FCoE work queues and by `vnic_dev.c` for devcmd2 command submission.

## Risks and edge cases

- `vnic_wq_init_start()` indexes `wq->bufs[...]`; devcmd2 allocation does not allocate buffer metadata, so this path relies on the selected usage not dereferencing `to_use` later for devcmd2 buffer servicing.
- Disable waits only 100 microseconds total; slow hardware can produce timeout errors.
- Cleaning asserts the queue is disabled with `BUG_ON()`, which is harsh if callers violate ordering.

## Test signals

Tests should cover normal WQ allocation/post/service/clean, devcmd2 allocation/init, disable timeout, descriptor wraparound, and memory-barrier-sensitive posting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_wq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_wq.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_wq.h

## Purpose

`vnic_wq.h` defines vNIC work queue control registers, software buffer metadata, queue state, and inline helpers for descriptor posting and completion servicing.

## Important APIs, types, and data

- `struct vnic_wq_ctrl` maps WQ MMIO registers.
- `struct vnic_wq_buf` tracks one posted descriptor's OS buffer, DMA address, length, SOP flag, descriptor pointer, and index.
- `struct vnic_wq` stores queue identity, device, MMIO control, DMA ring, buffer blocks, producer/consumer pointers, and outstanding packet count.
- `vnic_wq_desc_avail()`/`vnic_wq_desc_used()` expose ownership counts.
- `vnic_wq_next_desc()` returns the next descriptor to fill.
- `vnic_wq_post()` records buffer metadata, advances producer state, and posts to hardware on end-of-packet.
- `vnic_wq_service()` cleans descriptors through a completed index.

## Control flow

Transmit paths fill one or more descriptors, call `vnic_wq_post()` for each, and set `eop` on the final descriptor to update hardware after a write barrier. Completion paths start at `to_clean`, call a buffer-service callback for each descriptor through the completed index, increment availability, and advance consumer state.

## State and persistence behavior

Descriptor ownership is tracked by `ring.desc_avail`, `to_use`, `to_clean`, and hardware posted/fetch indexes. Multi-descriptor packets retain the OS buffer pointer only on the EOP descriptor.

## Dependencies and integration points

It depends on PCI types, `vnic_dev.h`, and `vnic_cq.h`. It integrates with Ethernet/FCoE descriptor encoders, completion queues, and devcmd2 setup.

## Risks and edge cases

- The alias `vnic_wq_next_desc` maps to `fni_cwq_next_desc`, which looks inconsistent with the other `fnic_*` aliases and should be compile-verified.
- Posting decrements availability for every descriptor but only writes hardware on EOP; callers must set EOP correctly.
- Completion service loops until a completed index is found; a bad completion index can overrun logical work.

## Test signals

Tests should validate availability math, multi-descriptor packet posting, EOP hardware posting, completion cleanup through wraparound, and alias compilation with ENIC also enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_wq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_wq_copy.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_wq_copy.c

## Purpose

`vnic_wq_copy.c` implements allocation, initialization, enable/disable, cleanup, and release of the FNIC copy work queue used for FCPIO host requests.

## Important APIs, types, and functions

- `vnic_wq_copy_alloc()` binds a copy WQ to a normal WQ resource, disables it, and allocates a coherent descriptor ring.
- `vnic_wq_copy_init()` programs ring base/size, fetch/posted indexes, CQ index, error interrupt settings, and error status.
- `vnic_wq_copy_enable()`/`vnic_wq_copy_disable()` control hardware execution.
- `vnic_wq_copy_clean()` services outstanding descriptors with an optional cleaner, resets indexes/status, and clears descriptor memory.
- `vnic_wq_copy_free()` releases the descriptor ring.

## Control flow

The copy WQ uses index-based state rather than a per-descriptor buffer metadata array. Producers fill `struct fcpio_host_req` descriptors through the inline helper and post them. Completion/cleanup advances `to_clean_index` and restores descriptor availability.

## State and persistence behavior

Software state is `to_use_index`, `to_clean_index`, and `ring.desc_avail`. Hardware state is the shared WQ control block for ring base/size, posted/fetch, enable/running, CQ, and error fields.

## Dependencies and integration points

It depends on `vnic_wq_copy.h`, `vnic_dev_alloc_desc_ring()`, and WQ MMIO register definitions. It is integrated with FNIC FCPIO request submission.

## Risks and edge cases

- Disable timeout returns `-ENODEV`, unlike normal WQ/RQ timeout paths that return `-ETIMEDOUT`.
- Cleaning requires the queue to be disabled and warns through `BUG_ON()` if not.
- Allocation uses `RES_TYPE_WQ`, so index ownership must not conflict with normal WQs.

## Test signals

Tests should cover copy WQ descriptor posting, completion cleanup, disable timeout logging, reset cleanup with outstanding descriptors, and queue-index assignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_wq_copy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_wq_copy.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_wq_copy.h

## Purpose

`vnic_wq_copy.h` defines FNIC copy work queue state and inline helpers for FCPIO host request descriptor management.

## Important APIs, types, and data

- `VNIC_WQ_COPY_MAX` declares a single copy WQ.
- `struct vnic_wq_copy` stores queue identity, device, WQ control MMIO pointer, DMA ring, producer index, and consumer index.
- `vnic_wq_copy_desc_avail()` and `vnic_wq_copy_desc_in_use()` expose descriptor ownership.
- `vnic_wq_copy_next_desc()` returns the next `struct fcpio_host_req` descriptor.
- `vnic_wq_copy_post()` advances producer state, decrements availability, applies a write barrier, and writes `posted_index`.
- `vnic_wq_copy_desc_process()` and `vnic_wq_copy_service()` return descriptors through a completed index or all outstanding descriptors.

## Control flow

Callers fill the next FCPIO descriptor, post it, and later process completions by completed index. The service helper optionally invokes a callback for each descriptor and advances `to_clean_index` until it reaches the completion or catches up to `to_use_index` when called with `(u16)-1`.

## State and persistence behavior

The queue is a ring with one reserved descriptor, tracked through `ring.desc_avail`, `to_use_index`, and `to_clean_index`.

## Dependencies and integration points

It depends on `vnic_wq.h` for control-register layout and `fcpio.h` for descriptor types. It integrates copy WQ submission with copy CQ completion handling.

## Risks and edge cases

- The service helper increments availability itself; callers must not also call `vnic_wq_copy_desc_process()` for the same completion.
- `(u16)-1` is a sentinel for clean-all, so real completion indexes must never be confused with it.
- Descriptor memory ordering depends on the barrier in `vnic_wq_copy_post()`.

## Test signals

Tests should exercise descriptor availability, wraparound, clean-all behavior, callback invocation order, and producer/consumer synchronization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/vnic_wq_copy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/wq_enet_desc.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/fnic/wq_enet_desc.h

## Purpose

`wq_enet_desc.h` defines the 16-byte Ethernet transmit/work queue descriptor used by Cisco vNIC hardware and helpers to encode/decode DMA address, length, offload, segmentation, FCoE, VLAN, and loopback fields.

## Important APIs, types, and data

- `struct wq_enet_desc` stores little-endian address, length, MSS/loopback, header-length/flags, and VLAN tag.
- Field masks and shifts define length, MSS, header length, offload mode, EOP, CQ entry request, FCoE encapsulation, VLAN tag insertion, and loopback.
- Offload modes include checksum, L4 checksum, and TSO.
- `wq_enet_desc_enc()` writes CPU values into descriptor bitfields.
- `wq_enet_desc_dec()` reads descriptor bitfields back to CPU-endian outputs.

## Control flow

Transmit code fills descriptors with `wq_enet_desc_enc()` before calling WQ post helpers. Debug/test code can decode descriptors for inspection. EOP and CQ-entry flags affect completion generation and packet segmentation.

## State and persistence behavior

Descriptor state persists in the DMA WQ ring until hardware consumes or the driver clears it. The header owns no software state.

## Dependencies and integration points

It depends on endian conversion helpers and integrates with `vnic_wq` transmit posting and completion handling.

## Risks and edge cases

- Length, MSS, header length, and offload mode are masked and silently truncated.
- Callers must supply semantically valid combinations, such as TSO with meaningful MSS/header length.
- EOP/CQ-entry flags directly affect completion behavior; incorrect flags can leak descriptors or lose completions.

## Test signals

Encode/decode tests should cover max field values, flag combinations, VLAN insertion, FCoE encapsulation, and TSO descriptors. Hardware tests should verify completions and packet output for each offload mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/fnic/wq_enet_desc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/g_NCR5380.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/g_NCR5380.c

## Purpose

`g_NCR5380.c` is the generic ISA/PNP/MMIO front end for NCR5380, NCR53C400, NCR53C400A, DTC3181E, and HP C2502 SCSI adapters. It configures board-specific IO resources and pseudo-DMA behavior, then includes and binds the shared `NCR5380.c` core to the SCSI midlayer.

## Important APIs, types, and functions

- Module parameters select IRQs, base addresses, and card types for up to eight adapters, with old-style compatibility parameters.
- `NCR5380_read()`/`NCR5380_write()` map core register access through hostdata IO base and offset.
- `g_NCR5380_trigger_irq()` and `g_NCR5380_probe_irq()` implement IRQ autoprobing.
- `magic_configure()` writes legacy configuration sequences for 53C400A/DTC436/HP C2502 style cards.
- `generic_NCR5380_init_one()` performs resource reservation, IO/MMIO mapping, host allocation, board setup, IRQ setup, core initialization, and SCSI host registration.
- `generic_NCR5380_release_resources()` reverses host registration, IRQ, core, mapping, and region state.
- `generic_NCR5380_precv()`/`generic_NCR5380_psend()` implement 53C400 pseudo-DMA receive/send in 128-byte chunks.
- `generic_NCR5380_dma_xfer_len()` decides whether pseudo-DMA is usable for a command.
- ISA and PNP driver callbacks wrap probe/remove around `generic_NCR5380_init_one()`.

## Control flow

Module init translates old parameters when needed, registers the PNP driver when enabled, and registers an ISA driver for up to eight configured cards. Probe reserves IO or memory regions, maps them, allocates a `Scsi_Host`, fills NCR5380 hostdata, validates register access, initializes the shared NCR5380 core, configures board-specific CSR registers, resets or probes the bus, selects/probes IRQ, registers with the SCSI midlayer, and scans.

Pseudo-DMA paths program the 53C400 control/status and block-count registers, wait for host-buffer readiness or gated 53C80 IRQs, move 128-byte chunks with `insb`/`insw`/`memcpy_fromio` or `outsb`/`outsw`/`memcpy_toio`, reset 53C400 logic on residual, and wait for 53C80 access to return.

## State and persistence behavior

Persistent state lives in `struct NCR5380_hostdata` fields injected through `NCR5380_implementation_fields`: register offsets, board type, IO width, pseudo-DMA residual, and 53C400 register locations. Module parameters persist adapter configuration. Hardware register state persists until reset, removal, or reboot.

## Dependencies and integration points

The file depends on ISA, PNP, SCSI host, IO-port/MMIO APIs, interrupt probing, and the shared NCR5380 core (`NCR5380.h` and included `NCR5380.c`). It integrates with the SCSI midlayer through `driver_template`.

## Risks and edge cases

- Legacy IRQ autoprobing and magic IO writes can disturb hardware if parameters are wrong.
- Pseudo-DMA requires transfer lengths divisible by 128; other sizes fall back to PIO.
- DTC3181E limits DMA sends to 512 bytes to avoid known corruption.
- `request_irq()` failure sets `instance->irq = NO_IRQ` before printing, so the denied IRQ message reports `NO_IRQ` instead of the attempted IRQ.
- Error paths must release the correct IO region; for some board types `hostdata->io_port` is adjusted from the originally reserved base.

## Test signals

Validation needs compile coverage for ISA and PNP builds, parameter parsing, probe failure cleanup, IRQ autoprobe/no-IRQ modes, pseudo-DMA send/receive success and timeout paths, and SCSI scan on each supported board variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/g_NCR5380.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/gvp11.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/gvp11.c

## Purpose

`gvp11.c` is the Amiga Zorro driver for GVP Series II SCSI boards using a WD33C93 SCSI controller and GVP DMA engine. It probes compatible Zorro products, validates the WD33C93, initializes DMA and WD33C93 core glue, and registers a SCSI host.

## Important APIs, types, and functions

- `struct gvp11_hostdata` embeds `struct WD33C93_hostdata` and stores GVP registers plus the device pointer.
- `gvp11_intr()` handles shared Amiga port interrupts and dispatches to `wd33c93_intr()` when the GVP DMA interrupt bit is pending.
- `dma_setup()` maps SCSI data, allocates bounce buffers when addresses violate the DMA mask, programs CNTR/ACR/BANK, and starts DMA.
- `dma_stop()` stops DMA, unmaps/free bounce buffers, and copies read data back when needed.
- `check_wd33c93()` probes indirect WD33C93 registers to distinguish real SCSI boards from same-product-code RAM boards.
- `gvp11_probe()` claims Zorro memory, validates board size and chip, allocates a SCSI host, initializes registers, configures DMA mask, initializes WD33C93 core, requests IRQ, and scans.
- `gvp11_remove()` disables interrupts, removes the SCSI host, frees IRQ, releases host and memory.

## Control flow

Zorro probe first checks DMA mask and board size, reserves the first 256 bytes, maps registers through `ZTWO_VADDR()`, and runs the WD33C93 detection sequence. It then allocates `Scsi_Host`, initializes GVP DMA secret registers and control state, prepares WD33C93 register pointers, selects DMA mask from module override or product data, initializes the WD33C93 core with callbacks, requests the shared Amiga port IRQ, enables DMA interrupts, registers the host, and scans.

DMA setup first tries direct `dma_map_single()`. If the mapped address violates the controller mask, it unmaps and uses a kernel or chip-RAM bounce buffer, copying write data into the bounce buffer as needed. It programs direction, DMA address, bank register, and starts DMA. Stop reverses this and copies from bounce buffer for successful reads.

## State and persistence behavior

Per-host state is in `gvp11_hostdata` and embedded WD33C93 state, including bounce-buffer pointers, DMA direction, and DMA mask. Hardware state persists in GVP registers (`CNTR`, `BANK`, `ACR`, start/stop DMA) and WD33C93 indirect registers.

## Dependencies and integration points

The driver depends on Amiga/Zorro bus APIs, Amiga chip RAM allocation, DMA mapping, WD33C93 core callbacks, and the SCSI midlayer. The Zorro ID table maps board products to default DMA masks.

## Risks and edge cases

- Bounce-buffer handling is complex; a failed remap path calls `dma_unmap_single()` even after the original mapping was cleared, so error handling deserves scrutiny.
- A static `scsi_alloc_out_of_range` changes future allocation strategy globally after one out-of-range allocation.
- The interrupt handler reads `CNTR` directly and assumes the pending bit is stable.
- Busy-waiting on `GVP11_DMAC_BUSY` during probe has no timeout.
- Chip RAM bounce buffers bypass cache maintenance by using physical addresses directly.

## Test signals

Hardware tests should cover direct DMA, kernel bounce buffer DMA, chip RAM bounce fallback, read/write transfers, shared IRQ handling, WD33C93 detection failure, board-size rejection, and remove cleanup. Static checks should inspect DMA unmap/free paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/gvp11.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/gvp11.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/gvp11.h

## Purpose

`gvp11.h` defines register layout, queue defaults, DMA mask, and control-bit constants for the GVP Series II Amiga SCSI controller.

## Important APIs, types, and data

- `CMD_PER_LUN` and `CAN_QUEUE` default to 2 and 16 if not already defined.
- `GVP11_XFER_MASK` describes address bits that prevent direct DMA.
- `struct gvp11_scsiregs` maps padded hardware registers: CNTR, WD33C93 SASR/SCMD, BANK, ACR, start/stop DMA, and undocumented secret registers.
- CNTR bits define DMA busy, interrupt pending, interrupt enable, and write direction.

## Control flow

The header is consumed by `gvp11.c`, which writes the secret registers during probe, uses SASR/SCMD for WD33C93 core access, programs `ACR` and `BANK` for DMA, and toggles `ST_DMA`/`SP_DMA`.

## State and persistence behavior

The structure maps volatile hardware state in Zorro memory space. No software state is allocated here.

## Dependencies and integration points

It depends on Linux fixed-width types and the Amiga/Zorro memory mapping performed by the driver.

## Risks and edge cases

- Register padding is hardware ABI; any layout change breaks MMIO access.
- The include guard lacks a `#define GVP11_H`, so repeated inclusion in one translation unit would not be prevented.
- Secret registers are documented only by comments and driver behavior.

## Test signals

Compile tests can catch the include-guard issue only if the header is included twice with conflicting definitions. Hardware probe and DMA tests validate the register layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/gvp11.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/hisi_sas/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/scsi/hisi_sas/Kconfig

## Purpose

`hisi_sas/Kconfig` declares configuration options for the HiSilicon SAS driver family, including the core/platform driver, PCI variant, and default debugfs enablement.

## Important APIs, types, and data

- `CONFIG_SCSI_HISI_SAS` builds the core/platform HiSilicon SAS driver. It depends on MMIO, ARM64 or compile testing, ATA, and selects libsas, block integrity, and SATA host support.
- `CONFIG_SCSI_HISI_SAS_PCI` builds PCI support and depends on the core option, PCI, and ACPI.
- `CONFIG_SCSI_HISI_SAS_DEBUGFS_DEFAULT_ENABLE` defaults debugfs on when the core driver is enabled.

## Control flow

Kconfig selection controls which objects from the local Makefile are built and whether debugfs defaults are enabled in `hisi_sas_main.c`.

## State and persistence behavior

Build-time configuration persists in the kernel config. Runtime debugfs default state is derived from the debugfs option.

## Dependencies and integration points

It integrates the driver with SCSI SAS libsas, ATA/SATA support, block integrity for DIF/DIX, platform devices, and PCI/ACPI variants.

## Risks and edge cases

- PCI support is ACPI-only by dependency, so non-ACPI PCI environments will not build that variant.
- The core option depends on ATA and selects SATA host support because SAS HBAs may attach SATA/STP devices.

## Test signals

Build matrix tests should cover core-only, PCI-enabled, debugfs-default-enabled, ARM64 native, and COMPILE_TEST configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/hisi_sas/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/hisi_sas/Makefile -->
# sources/distributed-fs/ceph-client/drivers/scsi/hisi_sas/Makefile

## Purpose

`hisi_sas/Makefile` maps Kconfig options to HiSilicon SAS driver objects.

## Important APIs, types, and data

- `hisi_sas_main.o` is built for `CONFIG_SCSI_HISI_SAS`.
- Hardware v1 and v2 platform implementations are also built for the core option.
- Hardware v3 PCI implementation is built for `CONFIG_SCSI_HISI_SAS_PCI`.

## Control flow

Kbuild includes the common core and platform hardware versions when the core driver is selected, and adds PCI v3 support when the PCI option is enabled.

## State and persistence behavior

No runtime state exists. The file controls build artifacts.

## Dependencies and integration points

It ties `Kconfig` selections to `hisi_sas_main.c`, `hisi_sas_v1_hw.c`, `hisi_sas_v2_hw.c`, and `hisi_sas_v3_hw.c`.

## Risks and edge cases

- The core option always builds v1 and v2 hardware files, so those files must compile for all core-supported environments.
- v3 support is isolated behind the PCI option.

## Test signals

Kbuild tests should verify object inclusion for each config combination and link success when PCI support is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/hisi_sas/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/hisi_sas/hisi_sas.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/hisi_sas/hisi_sas.h

## Purpose

`hisi_sas.h` is the common private interface for the HiSilicon SAS HBA driver. It defines constants, host/phy/port/device/slot state, hardware-version callback operations, DMA memory layouts, debugfs capture structures, and exported common-core APIs.

## Important APIs, types, and data

- Global limits include max phys, queues, queue slots, ITCT/device entries, commands, reserved IPTT tags, CDB length, and block queue depth.
- `struct hisi_sas_phy`, `struct hisi_sas_port`, `struct hisi_sas_cq`, `struct hisi_sas_dq`, `struct hisi_sas_device`, and `struct hisi_sas_slot` model libsas phys/ports, hardware queues, devices, and in-flight commands.
- `struct hisi_sas_hw` is the hardware-version callback table for initialization, command preparation, PHY control, reset, ITCT setup/clear, debugfs snapshots, GPIO, and queue delivery.
- `struct hisi_hba` is the central host object, embedding `sas_ha_struct`, SCSI host pointer, MMIO bases, queue arrays, phy/port arrays, device table, DMA memory pointers, flags, workqueue, reset work, debugfs state, BIST state, and iopoll queue count.
- DMA ABI structures include command headers, ITCT, IOST, initial FIS, breakpoint buffers, SGE pages, command tables for SSP/SMP/STP, status buffers, and slot buffer tables.
- Address macros compute per-slot DMA and CPU addresses for status, command table, SGE, and DIF SGE buffers.
- Extern declarations expose common functions to hardware-specific source files.

## Control flow

Hardware-specific drivers allocate/populate `struct hisi_hba`, set a `struct hisi_sas_hw` table, and call common probe/allocation helpers. Common queue submission fills `struct hisi_sas_slot` and calls hardware callbacks to encode command headers. Completion and reset paths use shared state and hardware callbacks to recover, reinitialize, and notify libsas.

## State and persistence behavior

The header defines the persistent in-memory driver model. Device, slot, queue, debugfs, and DMA structures live for the HBA lifetime. Flags such as resetting, reject-command, PM, and hardware-fault persist across asynchronous work and error handling. Hardware-visible DMA tables persist until device removal or managed resource cleanup.

## Dependencies and integration points

The file includes ACPI, platform, PCI, libsas, libata, debugfs, DMA, blk-mq, runtime PM, regmap, and SCSI transport headers. It is the integration surface between `hisi_sas_main.c` and hardware version files.

## Risks and edge cases

- `struct hisi_hba` requires `struct sas_ha_struct *p` as the first element for `SHOST_TO_SAS_HA` usage; reordering would break conversions.
- `struct hisi_sas_slot` explicitly warns not to reorder members after `buf`; cleanup uses `offsetof(struct hisi_sas_slot, buf)`.
- Hardware callback availability varies by version; common code must check optional callbacks before calling.
- DMA layout structures are hardware ABI and must remain aligned and endian-correct.
- The debugfs arrays are large, especially at the maximum dump count.

## Test signals

Compile all hardware versions, validate structure sizes and alignments against hardware manuals, test DIF/DIX and non-protection allocations, verify reset flags and slot cleanup invariants, and exercise debugfs snapshot storage at configured dump counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/hisi_sas/hisi_sas.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/hisi_sas/hisi_sas_main.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/hisi_sas/hisi_sas_main.c

## Purpose

`hisi_sas_main.c` is the common core for HiSilicon SAS HBAs. It implements libsas transport operations, task submission, DMA mapping, PHY/port events, device discovery/removal, error handling and task management, controller reset sequencing, common memory allocation, platform probe/remove, and module-level debugfs/transport registration.

## Important APIs, types, and functions

- ATA/SATA helpers: `hisi_sas_get_ata_protocol()`, `hisi_sas_sata_done()`, `hisi_sas_softreset_ata_disk()`, and ATA reset FIS construction.
- Slot/tag management: `hisi_sas_slot_index_alloc()`, `hisi_sas_slot_task_free()`, and hardware-specific slot-index override support.
- DMA setup: `hisi_sas_dma_map()`, `hisi_sas_dma_unmap()`, `hisi_sas_dif_dma_map()`, and `hisi_sas_dif_dma_unmap()`.
- Submission: `hisi_sas_queue_command()` validates device/port/reset state, chooses a delivery queue, maps data/protection SGs, allocates a slot, and calls `hisi_sas_task_deliver()`.
- Completion synchronization: `hisi_sas_sync_cq()`, `hisi_sas_sync_cqs()`, and poll-queue synchronization.
- Discovery: `hisi_sas_dev_found()`, `hisi_sas_dev_gone()`, `hisi_sas_sdev_init()`, `hisi_sas_sdev_configure()`, scan start/finished callbacks.
- PHY/port handling: `hisi_sas_phy_oob_ready()`, `hisi_sas_notify_phy_event()`, `hisi_sas_phy_enable()`, `hisi_sas_phy_down()`, `hisi_sas_phy_bcast()`, and `hisi_sas_control_phy()`.
- Error handling/TMF: `hisi_sas_abort_task()`, `hisi_sas_abort_task_set()`, `hisi_sas_I_T_nexus_reset()`, `hisi_sas_lu_reset()`, `hisi_sas_clear_nexus_ha()`, and `hisi_sas_query_task()`.
- Reset: `hisi_sas_controller_reset_prepare()`, `hisi_sas_controller_reset_done()`, `hisi_sas_controller_prereset()`, `hisi_sas_controller_reset()`, and reset work handlers.
- Allocation/probe: `hisi_sas_alloc()`, `hisi_sas_free()`, `hisi_sas_get_fw_info()`, `hisi_sas_probe()`, and `hisi_sas_remove()`.

## Control flow

Module initialization attaches a SAS domain transport with `hisi_sas_transport_ops` and optionally creates the top-level debugfs directory. Platform hardware drivers call `hisi_sas_probe()` with their callback table. Probe allocates a SCSI host and `hisi_hba`, reads firmware properties (`sas-addr`, `phy-count`, `queue-count`, and platform reset/syscon properties), maps registers, allocates coherent command/completion/ITCT/IOST/slot buffers, wires libsas phy/port arrays, preinitializes interrupts, registers the SCSI host and SAS HA, runs hardware initialization, and scans.

Task submission enters through libsas `lldd_execute_task`. The driver rejects or waits during reset, verifies device and port state, chooses a blk-mq hardware queue or fallback queue, maps data and protection SGs, allocates a command slot/tag, fills common slot state, links the slot onto delivery and device lists, clears command/status memory, dispatches to a protocol-specific hardware prep callback, marks the slot ready with a memory barrier, and starts hardware delivery.

PHY events are queued onto an ordered workqueue. PHY-up work validates port ID changes, notifies SSP link layer when needed, copies identify/FIS data to libsas, and sends `PORTE_BYTES_DMAED`. PHY-down notifies loss-of-signal, updates port attachment, and ignores transient down events while resetting. Timers handle OOB-ready without PHY-up by scheduling link resets with bounded retries.

Error handling first synchronizes completions to avoid freeing tasks being completed concurrently. SSP aborts issue libsas TMF and internal aborts; SATA aborts abort device state, deregister hardware device state, and often soft-reset the disk; SMP aborts use internal abort and may detach the slot. Controller reset blocks SCSI requests, waits for commands, rejects new commands, performs hardware soft reset, restarts PHYs, refreshes ITCT/port IDs, reinitializes devices, unblocks requests, and rescans topology.

## State and persistence behavior

Driver state persists in `struct hisi_hba`: queue pointers, slots, device table, phys, ports, DMA tables, flags, workqueue, timers, and debugfs configuration. Each in-flight task persists as a `struct hisi_sas_slot` until completion, abort, release, or reset. Slot indexes below `HISI_SAS_RESERVED_IPTT` are reserved for internal/non-request operations unless hardware supplies its own allocator; request-backed IO uses blk-mq tags offset by the reserved range. Hardware-visible state persists in coherent command headers, completion headers, ITCT, IOST, FIS, breakpoint, status, and SGE buffers.

## Dependencies and integration points

The file integrates deeply with libsas (`sas_domain_function_template`), libata, SCSI midlayer, blk-mq, DMA mapping, platform firmware properties, syscon/regmap, clocks, runtime PM, async domains, debugfs, and hardware-specific HiSilicon callback implementations. Exported symbols are used by `hisi_sas_v1_hw.c`, `hisi_sas_v2_hw.c`, and `hisi_sas_v3_hw.c`.

## Risks and edge cases

- Reset and device-gone paths coordinate through `sem`, flags, workqueue, timers, and completion synchronization; missed ordering can race command submission or task freeing.
- `hisi_sas_debug_I_T_nexus_reset()` calls `sas_put_local_phy(local_phy)` before later checking `scsi_is_sas_phy_local(local_phy)` and using `local_phy->number`, which is a use-after-put pattern worth review.
- `hisi_sas_slot_task_free()` returns early if `task->lldd_task` is already NULL, which can skip slot cleanup when callers pass a slot with a cleared task pointer.
- DMA mapping error labels note that direct `dma_unmap_sg()` would be better but messy; SG mapping/unmapping paths deserve stress testing.
- `hisi_sas_alloc_dev()` loop control mutates `i` both in the `for` expression and inside the loop, which is unusual and should be checked for full table coverage.
- Reset failure paths must clear reject/reset flags and unblock SCSI requests; the code handles the main soft-reset failure path, but hardware callback failures elsewhere need validation.

## Test signals

High-value tests include boot/probe/remove for platform and PCI hardware versions, libsas discovery with direct SAS, SATA, and expander devices, blk-mq multi-queue submission, DIF/DIX IO, SMP requests with 4-byte alignment checks, IO aborts, LU reset, I_T nexus reset, host reset, device removal during IO, PHY flap/link-reset timers, runtime PM PHY-up work, debugfs register snapshots on timeout, and fault injection for DMA mapping, queue full, hardware fault, and soft reset failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/hisi_sas/hisi_sas_main.c -->
