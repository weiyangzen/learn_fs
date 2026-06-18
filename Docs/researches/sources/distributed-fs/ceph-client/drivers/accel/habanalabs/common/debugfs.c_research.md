# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/debugfs.c

## Purpose
Implements debugfs support for HabanaLabs devices. It creates diagnostic and control nodes, reports live command buffers, command submissions, jobs, userptrs, VM mappings, MMU translations, engine-idle state, state dumps, and optional Direct I/O statistics. It also provides privileged debugfs paths for direct device memory access, DMA memory dump, monitor dump, I2C, LEDs, power state changes, timeout/debug toggles, memory scrub, and error acknowledgement.

## Important APIs, Types, And Functions
Device-level lifecycle APIs are `hl_debugfs_device_init()`, `hl_debugfs_device_fini()`, and `hl_debugfs_add_device()`. Object tracking APIs are `hl_debugfs_add_file()`, `hl_debugfs_remove_file()`, `hl_debugfs_add_cb()`, `hl_debugfs_remove_cb()`, `hl_debugfs_add_cs()`, `hl_debugfs_remove_cs()`, `hl_debugfs_add_job()`, `hl_debugfs_remove_job()`, `hl_debugfs_add_userptr()`, `hl_debugfs_remove_userptr()`, `hl_debugfs_add_ctx_mem_hash()`, and `hl_debugfs_remove_ctx_mem_hash()`. State dump ingestion is handled by `hl_debugfs_set_state_dump()`.

Read/show handlers include `command_buffers_show()`, `command_submission_show()`, `command_submission_jobs_show()`, `userptr_show()`, `vm_show()`, `userptr_lookup_show()`, `mmu_show()`, `mmu_ack_error()`, `engines_show()`, and optional `dio_*_show()` handlers. Memory and control handlers include `hl_access_mem()`, `device_va_to_pa()`, `hl_data_read32()`, `hl_data_write32()`, `hl_data_read64()`, `hl_data_write64()`, `hl_dma_size_write()`, `hl_monitor_dump_trigger()`, `hl_memory_scrub()`, `hl_device_write()`, `hl_stop_on_err_write()`, `hl_timeout_locked_write()`, I2C handlers, LED handlers, and power-state handlers.

## Control Flow
`hl_debugfs_device_init()` initializes the in-memory debugfs bookkeeping object, allocates the table of `hl_debugfs_entry` records, initializes lists/locks/semaphores/blob descriptors, and initializes config-access history state. `hl_debugfs_add_device()` binds the device debugfs root from DRM accel debugfs, creates common nodes through `add_files_to_device()`, and adds I2C/LED secured nodes only when firmware security is disabled.

The seq-file based nodes are driven by `hl_debugfs_list[]`, `hl_debugfs_open()`, and `hl_debugfs_write()`. Each table entry wires a show callback and optional write callback to a `hl_debugfs_entry`. The object-tracking add/remove functions maintain debugfs lists under spinlocks or mutexes, and show handlers walk those lists to render live state.

Direct memory access flows through `hl_access_mem()`. Device virtual addresses are translated through the active compute context and MMU when they fall in device VA ranges. Physical addresses are matched against configured PCI memory regions and dispatched to ASIC `access_dev_mem()`; non-IOMMU host-memory access can fall back to `phys_to_virt()` for mapped host ranges. Config-region accesses are logged in a fixed history ring for later dump by `hl_debugfs_cfg_access_history_dump()`.

## State And Persistence
Debugfs state lives primarily in `hdev->hl_debugfs`: root dentry, entry array, tracked file/CB/CS/job/userptr/context lists, locks, lookup settings, MMU address/ASID fields, DMA and monitor blob descriptors, state-dump ring, and optional DIO statistics. `hdev->debugfs_cfg_accesses` stores a bounded ring of recent config accesses with timestamps and access type. Device flags such as `memory_scrub_val`, `disabled`, `stop_on_err`, `timeout_jiffies`, `skip_reset_on_timeout`, `device_release_watchdog_timeout_sec`, and power state are directly exposed or mutated by debugfs nodes.

Blob data allocated by DMA and monitor dump nodes persists until overwritten or device debugfs finalization. State dumps are retained in a ring under `state_dump_sem` and can be discarded by writing a skip count to the `state_dump` node.

## Dependencies And Integration Points
The file depends on DRM accel debugfs roots, Linux debugfs/seq-file helpers, PCI, IOMMU detection, VM/MMU helpers, command-buffer and memory-manager objects, ASIC callbacks for CPU messages, memory access, DMA dump, monitor dump, idle checks, MMU error ack, protection-bit ack, power/debug operations, and optional `CONFIG_HL_HLDIO` Direct I/O helpers. It is fed by command submission, memory management, context management, and device error paths through the add/remove and state dump APIs.

## Risks
Many debugfs nodes deliberately perform privileged destructive actions: direct MMIO/memory writes, PCI power changes, suspend/resume, stop-on-error reset, device disable, memory scrub, and timeout changes. These are acceptable debugfs capabilities but need strict assumptions about debugfs access control. The direct host-memory fallback uses `phys_to_virt()` and is invalid when IOMMU mapping is present; address validation must remain conservative.

Concurrency risks include list traversal while tracked objects are removed, active compute context lookup during VM/MMU dumps, state dump ring updates while userspace reads, and config-access history dumping that unlocks while iterating copied entries. The `mmu_asid_va_write()` parser appears to require `0x` but parses from `c+3`, so input parsing deserves scrutiny because the expected offset after the space and `0x` prefix is easy to get wrong. Optional DIO debugfs paths parse file descriptors and device VAs from strings and depend on page alignment and kernel context use.

## Test Signals
Useful checks include debugfs creation/removal across successful init, failed init with exposed interfaces, and device fini; show handlers with empty and populated lists; concurrent add/remove stress for CB/CS/job/userptr tracking; MMU lookup for kernel and user ASIDs; invalid direct memory addresses; config-region access logging and dump expiry; memory scrub blocked by active compute context; DMA dump size/address validation; state dump ring read/write; stop-on-error reset trigger; I2C length validation; firmware-security gating of secured nodes; and optional DIO success/failure/stat reset paths.
