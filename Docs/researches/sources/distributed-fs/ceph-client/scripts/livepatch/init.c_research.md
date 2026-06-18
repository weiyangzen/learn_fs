# sources/distributed-fs/ceph-client/scripts/livepatch/init.c

## Purpose
`init.c` is generic init/exit code for a generated livepatch kernel module. It builds a runtime `struct klp_patch` from linker-provided `.init.klp_objects` metadata and enables the livepatch.

## Important APIs, Types, and Functions
Global `static struct klp_patch *patch` stores the enabled patch. `livepatch_mod_init()` uses `klp_find_section_by_name()`, `kzalloc_obj()`, `kzalloc()`, `memcpy()`, and `klp_enable_patch()`. `livepatch_mod_exit()` iterates with `klp_for_each_object_static()` and frees allocated function arrays, objects, and patch. Module metadata is set with `MODULE_LICENSE`, `MODULE_INFO(livepatch, "Y")`, and `MODULE_DESCRIPTION`.

## Control Flow
On init, the module locates `.init.klp_objects`, computes object count, rejects empty patches, allocates patch and object arrays with sentinel entries, allocates each object's function array with a sentinel, copies old function names, replacement function pointers, symbol positions, object names, and callbacks, sets `patch->mod` and `patch->objs`, chooses replace behavior based on `KLP_NO_REPLACE`, and calls `klp_enable_patch()`. Error paths free partially allocated state. On exit, the module frees per-object function arrays and top-level allocations.

## State and Persistence
Patch state persists for the lifetime of the loaded module in `patch` and in livepatch core after enablement. Allocated arrays are freed on module exit.

## Dependencies and Integration Points
Depends on Linux kernel livepatch APIs, generated section data types `struct klp_object_ext` and `struct klp_func_ext`, module loader section lookup, and generated livepatch build tooling.

## Risks and Edge Cases
The error path inside function allocation appears to free `objs[i].funcs` in a loop over `j < i`, likely intending `objs[j].funcs`; this would leak earlier allocations and may double-check as a bug. The code assumes `.init.klp_objects` size is an exact multiple of the metadata struct. `patch->states` is TODO. Replace behavior defaults true unless `KLP_NO_REPLACE` is defined.

## Test Signals
Build and load generated livepatch modules with zero objects, one object, multiple objects/functions, allocation failure injection, callbacks, replace/no-replace modes, and unload after enablement.
