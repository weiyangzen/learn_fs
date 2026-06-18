# File Research: sources/block-storage/linux-dm/drivers/md/dm-exception-store.c

## Role
Implements the registry and common constructor/destructor helpers for device-mapper snapshot exception stores. Exception stores manage COW metadata for persistent and transient snapshots.

## Registry Mechanics
- `_exception_store_types` is a global list protected by `_lock`.
- `dm_exception_store_type_register()` adds a named store type if not already present.
- `dm_exception_store_type_unregister()` removes an existing type.
- `get_type()` first searches loaded types, then tries to autoload `dm-exstore-<type_name>`, truncating at the last dash and retrying for compound type names.
- Store type references are protected with module reference counts via `try_module_get()` and `module_put()`.

## Store Creation
- `dm_exception_store_create()` expects at least two arguments: persistence selector and chunk size.
- The first argument must start with `P` for persistent or `N` for transient; remaining characters are passed as store-type options.
- The chunk size is parsed and validated through `dm_exception_store_set_chunk_size()`.
- The selected type constructor is called, and the helper returns the number of consumed arguments.

## Chunk Size Validation
- Chunk size 0 is accepted as an unset/special state.
- Nonzero chunk size must be a power of two.
- It must be a multiple of both origin and COW device logical block sizes.
- It must fit within `INT_MAX >> SECTOR_SHIFT`.

## Lifecycle
- `dm_exception_store_init()` registers transient and persistent store implementations.
- `dm_exception_store_exit()` unregisters persistent then transient implementations.
- `dm_exception_store_destroy()` invokes the store-specific destructor, drops the module reference, and frees the common wrapper.

## Filesystem/Storage Relevance
Snapshot exception stores are the metadata layer that records origin-to-COW chunk mappings for DM snapshots. They are central to copy-on-write snapshot correctness and merge behavior.

## Notable Risks
- Autoload depends on the `dm-exstore-*` module naming convention.
- Chunk size choices are constrained by both origin and COW block sizes; invalid sizing would break snapshot chunk addressing.
