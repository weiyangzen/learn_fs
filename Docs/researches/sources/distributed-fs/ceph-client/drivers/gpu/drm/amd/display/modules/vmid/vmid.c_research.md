# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/vmid/vmid.c

## Purpose
This file implements the Display Core `mod_vmid` helper that maps display page table base addresses to hardware VMID slots. It is a small stateful allocator around `dc_setup_vm_context()`: physical addressing uses VMID 0, while nonzero page table bases are cached in VMIDs 1..`num_vmid - 1`.

## Important APIs, Types, And Functions
`struct core_vmid` embeds public `struct mod_vmid`, owns the `struct dc *` integration handle, tracks `num_vmid`, `num_vmids_available`, the `ptb_assigned_to_vmid[MAX_VMID]` table, and a base `dc_virtual_addr_space_config` copied at creation.

`mod_vmid_create()` validates that more than one VMID exists and that `dc` is non-null, allocates with `kzalloc_obj()`, stores the base VA config, initializes the free count to `num_vmid - 1`, and returns the embedded public object. `mod_vmid_destroy()` frees the containing `core_vmid`.

`mod_vmid_get_for_ptb()` is the exported lookup/allocate path. It returns VMID 0 for `ptb == 0`, reuses an existing mapping when present, evicts stale table entries if no VMID is available, chooses the next empty VMID, records the PTB, and programs Display Core by calling `dc_setup_vm_context(core_vmid->dc, &va_config, vmid)`.

Internal helpers are `add_ptb_to_table()`, `clear_entry_from_vmid_table()`, `evict_vmids()`, `get_existing_vmid_for_ptb()`, and `get_next_available_vmid()`.

## Control Flow
The allocator first treats zero PTB as physical addressing and short-circuits to VMID 0. For nonzero PTBs it performs a linear search across the tracked table. On a miss, it clones `base_config`, sets `page_table_base_addr`, and checks `num_vmids_available`. If the count is zero, `evict_vmids()` asks DC for the current use vector via `dc_get_vmid_use_vector()` and clears table entries for VMIDs whose bit is no longer active. After that, `get_next_available_vmid()` scans from VMID 1 upward. A successful allocation decrements the free count, stores the PTB, and programs the hardware VM context.

`mod_vmid_reset()` clears all cached PTB mappings and resets the free count to `num_vmid - 1`. There is no attempt to reprogram hardware during reset; the table is only the module's software cache.

## State And Persistence
All state is in the heap-allocated `core_vmid` object. It is runtime-only and persists until `mod_vmid_destroy()` or `mod_vmid_reset()`. `ptb_assigned_to_vmid[]` is the authoritative local cache; hardware state is indirectly synchronized when new mappings call `dc_setup_vm_context()`. VMID 0 is reserved and never allocated for PTBs.

## Dependencies And Integration Points
The file includes `mod_vmid.h`, which is provided under `display/modules/inc`. It depends on Display Core APIs and types: `struct dc`, `struct dc_virtual_addr_space_config`, `dc_setup_vm_context()`, and `dc_get_vmid_use_vector()`. It also uses kernel/display infrastructure such as `container_of`, `ASSERT`, `kzalloc_obj`, `kfree`, `memset`, `uint64_t`, and `uint8_t`.

The important downstream integration is with DCN VM context programming. This module decides which VMID to request, while lower display hardware code owns the actual register programming and the VMID use vector.

## Risks
The implementation assumes single-threaded or externally serialized access. There is no lock around `ptb_assigned_to_vmid[]` or `num_vmids_available`, so concurrent callers could double-allocate or corrupt the free count.

`add_ptb_to_table()` and `clear_entry_from_vmid_table()` only check `vmid < MAX_VMID`, not `vmid < num_vmid`; callers currently satisfy that by scanning to `num_vmid`, but future direct callers could create inconsistent state. The free counter can also drift if a table entry is cleared twice or added over an occupied VMID.

`evict_vmids()` casts the use vector to `uint16_t` after asserting it is at most `0xFFFF`, so hardware exposing more than 16 meaningful VMIDs would need a broader representation. A post-eviction allocation failure only asserts and still returns the current `vmid` value after the assert path, so production behavior depends on how `ASSERT` is compiled.

## Test Signals
Useful tests are allocation reuse for the same PTB, VMID 0 for PTB 0, allocation order from VMID 1 upward, reset clearing all mappings, and eviction behavior when `dc_get_vmid_use_vector()` marks entries unused. Integration tests should verify `dc_setup_vm_context()` receives a copied base config with only `page_table_base_addr` changed and that display workloads with VM context churn do not hit the assertion path.
