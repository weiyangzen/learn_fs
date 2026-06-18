# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/gaudi/gaudi.c lines 8622-9236

## Scope And Purpose

This chunk is the closing section of the Gaudi ASIC implementation. It completes wait-command-buffer generation for sync-object waits, implements Gaudi-specific state-dump callbacks, exposes a small VRM sysfs attribute, and publishes the final `hl_asic_funcs` dispatch table through `gaudi_set_asic_funcs()`.

The code is mostly glue between common HabanaLabs core interfaces and Gaudi register layouts. Its main runtime effects are:

- translate Gaudi hardware queue IDs into fence-read-data register addresses for wait CBs;
- emit monitor and fence packets that make a wait CB arm a monitor and signal completion through QMAN fence 2;
- reset SOB hardware state and local refcounts;
- build diagnostic state-dump metadata and formatted monitor/fence text;
- wire every Gaudi lifecycle, DMA, MMU, firmware, queue, debug, state-dump, and sysfs hook into common driver code.

## Important APIs, Types, And Functions

- `gaudi_get_fence_addr(struct hl_device *hdev, u32 queue_id, u64 *addr)` maps `GAUDI_QUEUE_ID_*` values to `mm*QM_CP_FENCE2_RDATA_*` register offsets and returns `CFG_BASE + offset`. The chunk starts inside its switch, covering TPC7 and NIC queue cases plus the `-EINVAL` default.
- `gaudi_add_mon_pkts(void *buf, u16 mon_id, u64 fence_addr)` appends three `PACKET_MSG_SHORT` monitor payload writes: low fence address, high fence address, and payload data value `1`.
- `gaudi_gen_wait_cb(struct hl_device *hdev, struct hl_gen_wait_properties *prop)` is the common core callback for wait CB generation. It casts `prop->data` to `struct hl_cb`, writes packets into `cb->kernel_address` at `prop->size`, resolves the queue fence address, emits monitor payload packets, arms the monitor with `gaudi_add_arm_monitor_pkt()`, and appends `gaudi_add_fence_pkt()`.
- `gaudi_reset_sob(struct hl_device *hdev, void *data)` clears a hardware SOB register and reinitializes the corresponding `struct hl_hw_sob` kref.
- `gaudi_get_device_time()` reads the device timestamp high and low registers and combines them into a 64-bit time value.
- `gaudi_get_hw_block_id()` and `gaudi_block_mmap()` currently deny direct hardware-block mmap support with `-EPERM`.
- `gaudi_enable_events_from_fw()` writes an interrupt to firmware using either the GIC distributor SPI register or the firmware-provided host interrupt register from `cpu_dyn_regs`.
- `gaudi_ack_mmu_page_fault_or_access_error()` returns `-EINVAL`, indicating no chunk-local MMU error acknowledgment implementation.
- `gaudi_map_pll_idx_to_fw_idx()` maps driver-facing `HL_GAUDI_*_PLL` indexes to firmware PLL enum values and returns `-EINVAL` for unknown indexes.
- `gaudi_add_sync_to_engine_map_entry()` allocates and inserts a sync-object-to-engine hash entry after normalizing a register value by subtracting `lower_32_bits(CFG_BASE)`.
- `gaudi_gen_sync_to_engine_map()` reads configured sync-object registers for TPC, MME, and DMA engines using `hdev->state_dump_specs.props`, inserts mappings, and frees the whole map on allocation failure.
- `gaudi_monitor_valid()` extracts the monitor valid bit from `struct hl_mon_state_dump.status`.
- `gaudi_fill_sobs_from_mon()` decodes monitor arm data into a comma-separated list of monitored SOB IDs.
- `gaudi_print_single_monitor()` formats one monitor dump through `hl_snprintf_resize()`, using object names, decoded group/mask/value fields, write address/data, pending bits, and decoded SOB IDs.
- `gaudi_print_fences_single_engine()` allocates temporary arrays, reads fence status and fence values for one engine, and appends formatted lines for active fences.
- `gaudi_state_dump_funcs` and `gaudi_state_dump_init()` register Gaudi state-dump callbacks, known sync-object names, known monitor names, sync manager names, and property tables.
- `gaudi_get_stream_master_qid_arr()` returns the static Gaudi stream-master queue array.
- `gaudi_set_dram_properties()`, `gaudi_set_binning_masks()`, `gaudi_check_if_razwi_happened()`, and `gaudi_send_device_activity()` are no-op/success hooks for common callback slots.
- `infineon_ver_show()`, `DEVICE_ATTR_RO(infineon_ver)`, `gaudi_vrm_dev_attrs`, and `gaudi_add_device_attr()` expose the Infineon VRM firmware version from `hdev->asic_prop.cpucp_info.infineon_version` and attach common clock sysfs attributes.
- `gaudi_funcs` is the large `const struct hl_asic_funcs` instance that binds common core operations to Gaudi implementations.
- `gaudi_set_asic_funcs(struct hl_device *hdev)` stores `&gaudi_funcs` in `hdev->asic_funcs`.

## Control Flow

Wait CB generation follows a strict packet-building path. `gaudi_gen_wait_cb()` resolves a fence target for `prop->q_idx` through `gaudi_get_fence_addr()`. If the queue ID is not in the supported DMA/TPC/MME/NIC switch table, it logs a critical error and returns `0`, meaning no wait packets were emitted. On success, it appends monitor payload-address/data setup packets, arms the selected monitor for the requested SOB base/mask/value, and finally appends a fence packet. The returned size is the updated command-buffer offset.

State-dump initialization is callback registration, not an immediate dump. `gaudi_state_dump_init()` populates hash tables in `hdev->state_dump_specs` from static Gaudi name arrays, points `sds->props` at `gaudi_state_dump_specs_props`, sets sync manager names, and copies the callback table. Later common state-dump code calls these callbacks to validate monitors, build sync-to-engine maps, and format monitors/fences.

`gaudi_gen_sync_to_engine_map()` derives diagnostics by reading live hardware configuration registers. It iterates TPC engines, then each MME sub-engine, then DMA engines. Each nonzero/non-`0xffffffff` sync-object register becomes one hash entry keyed by the sync ID. Any allocation failure aborts and calls `hl_state_dump_free_sync_to_engine_map()` so callers do not observe a partially built map.

`gaudi_print_fences_single_engine()` reads all configured fence status/value registers for one engine, filters to queues whose CP status has `FENCE_IN_PROGRESS`, decodes the active fence ID, computes the corresponding `CNT` and `RDATA` register addresses, and appends human-readable diagnostic lines. The function always frees its temporary arrays before returning.

The final dispatch table is passive until `gaudi_set_asic_funcs()` is called by device selection/probe code. After that, common driver paths invoke lifecycle, queue, MMU, firmware, debug, sysfs, and state-dump operations through `hdev->asic_funcs`.

## State And Persistence Behavior

This chunk mutates both hardware registers and per-device in-memory state:

- wait-CB helpers write into kernel command-buffer memory and encode little-endian packet fields consumed later by Gaudi QMAN hardware;
- `gaudi_reset_sob()` writes zero to `mmSYNC_MNGR_W_S_SYNC_MNGR_OBJS_SOB_OBJ_0 + sob_id * 4` and resets the SOB kref, changing hardware synchronization state and software lifetime tracking together;
- `gaudi_enable_events_from_fw()` writes an interrupt register to enable/notify firmware event delivery;
- `gaudi_state_dump_init()` inserts static name nodes into hash tables embedded in `hdev->state_dump_specs`; this persists for later state-dump lookups during the device lifetime;
- `gaudi_gen_sync_to_engine_map()` allocates transient hash entries owned by the caller-provided state-dump map and frees them on local failure;
- `gaudi_add_device_attr()` mutates the provided sysfs attribute group pointers, assigning Gaudi VRM attributes in addition to common clock attributes;
- `gaudi_set_asic_funcs()` persists the Gaudi callback table pointer in `hdev`.

There is no file persistence in this chunk. User-visible persistent surfaces are kernel sysfs attributes and debug/state-dump text generated from live device state.

## Dependencies And Integration Points

The code depends heavily on generated Gaudi register and mask headers included earlier in the file: `gaudi_masks.h`, `gaudi_reg_map.h`, `gaudi_fw_if.h`, and `gaudi_async_ids_map_extended.h`. Register access uses the driver `RREG32` and `WREG32` macros, while bit packing and extraction use Linux `FIELD_PREP()` and `FIELD_GET()`.

Common HabanaLabs core dependencies include:

- `struct hl_device`, `struct hl_cb`, `struct hl_hw_sob`, `struct hl_gen_wait_properties`, `struct hl_state_dump_specs`, `struct hl_mon_state_dump`, `struct hl_sync_to_engine_map`, and `struct hl_asic_funcs` from common headers;
- common state-dump utilities such as `hl_state_dump_get_monitor_name()`, `hl_state_dump_free_sync_to_engine_map()`, `hl_sync_engine_to_string()`, `hl_format_as_binary()`, and `hl_snprintf_resize()`;
- sysfs helpers such as `hl_sysfs_add_dev_clk_attr()`;
- generic helpers assigned in `gaudi_funcs`, including `hl_asic_dma_map_sgtable`, `hl_asic_dma_unmap_sgtable`, `hl_rreg`, `hl_wreg`, `hl_mmu_scramble_addr`, `hl_mmu_descramble_addr`, `hl_mmu_get_real_page_size`, and `hl_access_dev_mem`.

The `gaudi_funcs` table is the main integration boundary. It connects this file's earlier definitions and this chunk's callbacks to core device management. The table also explicitly advertises unsupported operations by assigning `NULL` for selected optional hooks such as `mmu_prefetch_cache_range`, `pb_print_security_errors`, and `get_dec_base_addr`, while some present hooks return no-op success or errors.

## Risks And Edge Cases

- `gaudi_get_fence_addr()` must stay synchronized with Gaudi queue ID definitions and register-map layout. Missing or wrong queue mappings cause wait CB generation to return `0`, which can break wait semantics for affected queues.
- `gaudi_gen_wait_cb()` assumes `prop->data` points to a valid `struct hl_cb` and that enough command-buffer space exists for the appended packets. Size accounting is additive but no local bounds check is visible in this chunk.
- Monitor packet address offsets assume the monitor base register matches `mmSYNC_MNGR_W_S_SYNC_MNGR_OBJS_MON_PAY_ADDRL_0`; a register-map change would affect all three monitor message-short writes.
- `gaudi_reset_sob()` resets the software kref immediately after clearing hardware. Callers must ensure no outstanding users still hold or expect the previous SOB state.
- `gaudi_add_sync_to_engine_map_entry()` subtracts `CFG_BASE` from the raw register value after filtering only zero and all-ones values. Unexpected raw values below `CFG_BASE` would underflow as an unsigned sync ID.
- `gaudi_print_fences_single_engine()` allocates `statuses` using `SP_ENGINE_NUM_OF_QUEUES` but fills it in a loop bounded by `SP_ENGINE_NUM_OF_FENCES`; if those properties diverge unexpectedly, this is a potential out-of-bounds write/read risk. The later loops assume fence and queue property values match the register layout.
- Several hooks are stubs returning success or error (`gaudi_set_dram_properties()`, `gaudi_set_binning_masks()`, `gaudi_send_device_activity()`, `gaudi_ack_mmu_page_fault_or_access_error()`, hardware block mmap helpers). Common code must tolerate these as Gaudi-specific unsupported/no-op behaviors.
- `infineon_ver_show()` uses `sprintf()` into a sysfs buffer, which is common in older kernel code but less defensive than `sysfs_emit()`.
- `gaudi_state_dump_init()` inserts static hash nodes; repeated initialization without matching cleanup/reinitialization discipline could re-add the same nodes.

## Test Signals

Useful validation signals for this chunk include:

- command-submission tests that generate wait CBs for DMA, TPC, MME, and NIC queue IDs and verify packet size progression plus encoded monitor/fence packet fields;
- negative wait-CB tests with an invalid queue ID, expecting a zero return and a critical log;
- SOB reset tests that confirm the hardware SOB register is cleared and the kref is reinitialized;
- firmware/event initialization tests that verify the correct interrupt register is written depending on `gic_interrupts_enable`;
- PLL mapping unit tests for every `HL_GAUDI_*_PLL` value and invalid inputs;
- state-dump tests with synthetic monitor dumps to validate valid-bit extraction, monitored SOB list formatting, and formatted monitor text;
- state-dump map tests that mock register reads for TPC/MME/DMA engines, confirm hash entries are created with normalized sync IDs, and exercise allocation-failure cleanup;
- fence dump tests with mocked CP status/fence registers to ensure only in-progress fences are printed and temporary allocations are freed;
- sysfs smoke tests reading `infineon_ver` and checking little-endian conversion from `cpucp_info`;
- probe-level tests confirming `gaudi_set_asic_funcs()` installs `gaudi_funcs` and that expected optional hooks are either populated or intentionally `NULL`.
