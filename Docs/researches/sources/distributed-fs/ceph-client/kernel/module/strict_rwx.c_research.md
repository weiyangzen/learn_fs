# sources/distributed-fs/ceph-client/kernel/module/strict_rwx.c

## Purpose
Applies strict memory permissions to module allocations and rejects invalid writable-executable module sections.

## Important APIs, Types, And Functions
Exports `module_enable_text_rox`, `module_enable_rodata_ro`, `module_enable_rodata_ro_after_init`, `module_enable_data_nx`, `module_enforce_rwx_sections`, and `module_mark_ro_after_init`. The local helper `module_set_memory` wraps permission changes for one module memory type.

## Control Flow
Before layout, `module_enforce_rwx_sections` rejects any ELF section with both write and execute flags under `CONFIG_STRICT_MODULE_RWX`. `module_mark_ro_after_init` tags known sections such as `.data..ro_after_init`, `__jump_table`, and optionally `.static_call_sites`. After relocation, `complete_formation` makes rodata read-only, data non-executable, and text executable/read-only. After init, ro-after-init memory becomes read-only.

## State And Persistence
It updates page table permissions for `mod->mem[]` regions and section flags used by layout. Permissions persist until the module is unloaded or memory is restored/freed.

## Dependencies And Integration Points
Depends on vmalloc/set_memory APIs, execmem ROX restoration, `rodata_enabled`, module memory type iteration, and loader sequencing in `main.c`.

## Risks And Edge Cases
Permission changes are architecture-sensitive and can fail. Text memory may already be ROX from execmem and must be restored rather than blindly changed. Section tagging must happen before layout or ro-after-init data lands in the wrong memory range. W+X rejection is a security boundary.

## Test Signals
Load normal modules under strict RWX, inject W+X sections and expect `-ENOEXEC`, verify text is executable but not writable, data is NX, rodata and ro-after-init become read-only, and error paths restore/free ROX memory correctly.
