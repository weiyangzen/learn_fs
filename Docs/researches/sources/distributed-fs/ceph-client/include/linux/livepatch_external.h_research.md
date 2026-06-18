<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/livepatch_external.h -->
# sources/distributed-fs/ceph-client/include/linux/livepatch_external.h

## Purpose
This header defines external livepatch metadata formats and callback naming conventions used by patch-generation tooling and livepatch modules.

## Important APIs, Types, and Functions
It exports section/name prefixes `KLP_RELOC_SEC_PREFIX`, `KLP_SYM_PREFIX`, and callback prefixes for pre/post patch and unpatch functions. Callback typedefs include `klp_pre_patch_t`, `klp_post_patch_t`, `klp_pre_unpatch_t`, and `klp_post_unpatch_t`. `struct klp_callbacks` groups optional callbacks. `struct klp_func_ext` and `struct klp_object_ext` provide compact generated descriptions consumed before conversion to core livepatch structures.

## Control Flow
Tooling emits metadata sections and callback pointers using these names. The livepatch loader later discovers sections, resolves compact external records, and invokes callbacks around object patch/unpatch operations.

## State and Persistence Behavior
The header itself owns no state. Metadata persists inside the livepatch module object file and is converted into runtime `klp_object`/`klp_func` state when loaded.

## Dependencies and Integration Points
It depends on basic types and forward-declared `struct klp_object`. It integrates with objtool/create-diff-object style tooling, module ELF sections, and `livepatch.h`.

## Risks and Test Signals
Risks include prefix mismatches, callback prototype mistakes, stale generated metadata, and callback failure semantics preventing later callbacks. Test signals are module section inspection, livepatch enable/disable tests, callback ordering tests, and symbol-resolution diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/livepatch_external.h -->
