# sources/distributed-fs/ceph-client/sound/pci/asihpi/hpicmn.c

## Purpose

`hpicmn.c` implements shared HPI backend services: adapter registry management, response-header validation, subsystem common messages, control-cache allocation/parsing, cache hit resolution for common control attributes, and cache synchronization after control set operations.

## Important APIs, types, and functions

The file-local `struct hpi_adapters_list` stores a spinlock, fixed `HPI_MAX_ADAPTERS` array of `hpi_adapter_obj`, and adapter count. Exported functions are `hpi_validate_response()`, `hpi_add_adapter()`, `hpi_delete_adapter()`, `hpi_find_adapter()`, `hpi_check_control_cache_single()`, `hpi_check_control_cache()`, `hpi_cmn_control_cache_sync_to_msg_single()`, `hpi_cmn_control_cache_sync_to_msg()`, `hpi_alloc_control_cache()`, `hpi_free_control_cache()`, and `HPI_COMMON()`.

Important internals are `wipe_adapter_list()`, `subsys_get_adapter()`, `control_cache_alloc_check()`, `find_control()`, and PAD string offset metadata. `control_cache_alloc_check()` lazily walks the DSP-provided cache blob, validates control indexes and entry sizes, and builds `p_info[control_index]` pointers for direct lookup.

## Control flow

Adapter lifecycle flow is guarded by `hpios_alistlock_lock()`. `hpi_add_adapter()` rejects out-of-range indexes, relocates duplicate adapter indexes to the highest free slot, copies the temporary object into the global array, initializes its DSP lock, and increments the count. `hpi_delete_adapter()` clears the registered slot and decrements the count. `hpi_find_adapter()` returns a registered adapter pointer if the index is valid and nonempty.

Control-cache lookup starts with `hpi_check_control_cache()`, which calls `find_control()`. The first lookup initializes cache lookup pointers by scanning the DSP cache blob; later lookups use `p_info` directly. `hpi_check_control_cache_single()` handles common cached control types and attributes, fills the response union, sets response header fields on a hit, and reports invalid attributes for known-but-invalid cached values. Set-state synchronization updates mutable cached values only when the DSP response succeeded.

`HPI_COMMON()` handles subsystem request messages. Driver load wipes and initializes the adapter list; get-adapter enumerates the nth registered adapter; get-num-adapters returns the count; open/close/unload are accepted as no-ops.

## State and persistence behavior

Persistent state is the static adapter list and each allocated `hpi_control_cache` object. Cache objects persist a pointer array, the raw DSP cache buffer pointer supplied by the backend, cache size, control count, adapter index, and an `init` count used as a lazy initialization flag. Cached controls mirror DSP state and are updated from firmware DMA/PIO refreshes or from successful set messages.

## Dependencies and integration points

The file depends on `hpi_internal.h` for ABI types and constants, `hpidebug.h` for logging, `hpimsginit.h` for response initialization, and `hpicmn.h` for declarations. It is used by both `hpi6000.c` and `hpi6205.c` for adapter registry and mixer/control-cache behavior. It integrates with OS locks supplied through `hpios.h`.

## Risks and test signals

Risks include global fixed-size adapter state, shallow-copying adapter objects into the registry, duplicate-index relocation surprising callers, cache blob corruption causing pointer misbuilds, unbounded trust in DSP-provided entry sizes after minimal checks, PAD string termination writes into cache memory, and stale cache data if the backend does not refresh or apply DMA barriers. Test signals include driver-load reset, duplicate adapter insertion, adapter enumeration, invalid index handling, cache allocation failure, cache hits for volume/meter/mux/sampleclock/PAD controls, invalid cached attribute returns, set-state cache synchronization, and response validation errors for corrupted DSP replies.
