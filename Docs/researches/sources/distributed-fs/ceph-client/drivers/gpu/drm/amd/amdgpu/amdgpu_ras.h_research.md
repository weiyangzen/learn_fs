# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ras.h

## Purpose

`amdgpu_ras.h` defines the public and internal contract for AMDGPU RAS. It names RAS blocks, error types, query modes, event types, persistent runtime structures, per-block callback interfaces, bad-page structures, poison handling structures, EEPROM/SMU integration hooks, and exported functions used by AMDGPU IP blocks and lifecycle code.

## Important APIs, Types, And Constants

- Boot/FW status helpers: `AMDGPU_RAS_GPU_ERR_*`, `AMDGPU_RAS_BOOT_STATUS_*`, and related masks decode MP0 boot failures.
- Feature/event constants: `AMDGPU_RAS_FLAG_INIT_BY_VBIOS`, `AMDGPU_RAS_INST_MASK`, `AMDGPU_RAS_FEATURES_SOCKETID_*`, `AMDGPU_RAS_RESERVED_VRAM_SIZE_DEFAULT`, `RAS_EVENT_INVALID_ID`, `RAS_EVENT_ID_IS_VALID()`, and `RAS_EVENT_LOG()`.
- `enum amdgpu_ras_block` enumerates UMC, SDMA, GFX, MMHUB, ATHUB, PCIE_BIF, HDP, XGMI_WAFL, DF, SMN, SEM, MP0, MP1, FUSE, MCA, VCN, JPEG, IH, MPIO, MMSCH, plus sentinels.
- `enum amdgpu_ras_mca_block` splits MCA into MP0, MP1, MPIO, and IOHC sub-blocks.
- `enum amdgpu_ras_gfx_subblock` provides detailed GFX SRAM/ECC sub-block indices for injection/reporting.
- `enum amdgpu_ras_error_type`, `enum amdgpu_ras_ret`, and `enum amdgpu_ras_error_query_mode` define RAS error and query semantics.
- `struct ras_common_if` is the common block/type/sub-block/name key used by query, injection, sysfs, debugfs, manager lookup, and feature control.
- `struct amdgpu_ras` is the main runtime context: feature/schema masks, manager objects, sysfs/debugfs attributes, recovery work/locks, EEPROM control, thresholds, poison FIFO, page-retirement thread, ECC log, event manager, critical regions, RMA state, UniRAS flag, and SMU RAS driver pointer.
- `struct ras_manager` stores per-block manager state, custom use count, sysfs/debugfs metadata, interrupt ring, accumulated error data, and ACA handle.
- `struct amdgpu_ras_block_object` and `struct amdgpu_ras_block_hw_ops` define per-IP callbacks for match, late init, fini, interrupt callback, injection, query, reset, poison status, and poison consumption.
- `struct ras_err_data`, `struct ras_err_node`, and `struct ras_err_info` support aggregate and socket/die-scoped CE/UE/DE counters.
- Public declarations cover RAS init/fini, recovery, suspend/resume, feature enablement, sysfs/debugfs, query/reset/inject, interrupt dispatch, bad-page add/save/reserve, context access, block registration, register helpers, error-data helpers, ACA binding, FED/error state, event IDs, critical regions, poison requests, RMA state, and reset pre/post hooks.

## Control Flow

The header’s workflow comment defines the RAS sequence: VBIOS enables features, PSP/RAS framework initializes during IP init, IPs add interrupt handlers, debugfs/sysfs nodes are created, users or driver code query/inject, nodes and handlers are removed, and features are disabled.

The main context layout mirrors that lifecycle. Early init sets masks and manager arrays. Late init creates managers and binds sysfs/debugfs/IH state. Recovery init fills EEPROM and page-retirement fields. Fini tears down work, filesystem nodes, managers, and context.

Per-IP flow is callback-driven through `amdgpu_ras_block_object`. Blocks can provide custom matching for sub-blocks, custom late init/fini, interrupt callbacks, and hardware ops while sharing common RAS object and filesystem handling.

Query flow is represented by `ras_query_if` and `ras_err_data`: callers select a block through `ras_common_if`, and implementation fills CE/UE/DE totals and optional source-aware error nodes.

Poison flow is represented by `ras_poison_msg` plus the FIFO, waitqueue, atomic counters, and page-retirement fields in `struct amdgpu_ras`.

## State And Persistence Behavior

Feature state is split between device masks (`ras_hw_enabled`, `ras_enabled`) and `amdgpu_ras.features`, whose high bits can contain socket ID. `AMDGPU_RAS_GET_FEATURES()` masks off socket ID when checking feature bits.

Persistent bad-page state enters through embedded `struct amdgpu_ras_eeprom_control`; in-memory bad pages use `eeprom_table_record` from the EEPROM header plus RAS error-handler state in the implementation.

Recovery state is represented by atomics, mutexes, work items, waitqueues, poison FIFO, page-retirement counters, and GPU reset flags. Event state can be local in `__event_mgr` or shared through `event_mgr` for XGMI hives.

Error statistics can be flat counters or source-aware linked nodes keyed by `amdgpu_smuio_mcm_config_info`.

## Dependencies And Integration Points

The header includes Linux debugfs/list/kfifo/radix-tree APIs, `ta_ras_if.h`, `amdgpu_ras_eeprom.h`, `amdgpu_smuio.h`, and `amdgpu_aca.h`. Its declarations are consumed by UMC, GFX, SDMA, MMHUB, NBIO, XGMI, KFD/poison, reset, PSP, SMU, virtualized RAS, and EEPROM code.

## Risks And Edge Cases

- `struct amdgpu_ras` is large and exposed across subsystems; representation changes can ripple widely.
- `struct ras_manager.use` is an `int`, not `refcount_t`, so lifetime safety depends on balanced manual calls.
- RAS block enum values are used as bit indices, array indices, TA conversion inputs, and names; adding a block requires coordinated updates.
- MCA blocks use `AMDGPU_RAS_BLOCK__MCA` plus `sub_block_index`, with manager array slots after normal blocks.
- `ras_debug_if` layout is used through debugfs and can affect userspace tools.
- `struct eeprom_table_record` from the EEPROM header is part of the RAS contract but has context-dependent fields.

## Test Signals

- Compile all RAS-enabled configurations after any signature, enum, or structure change.
- When adding blocks, verify strings, masks, TA conversions, sysfs/debugfs names, and manager indexing.
- Validate debugfs `ras_debug_if` compatibility.
- Test XGMI hive and single-device event-manager initialization.
- Use lockdep/KASAN-style tests for workqueue teardown, manager references, poison FIFO use, and asynchronous callbacks.
