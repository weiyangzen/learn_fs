# sources/distributed-fs/ceph-client/kernel/module/sysfs.c

## Purpose
Creates and tears down `/sys/module/<name>` state for loaded modules, including module parameters, modinfo attributes, holder links, section addresses, and note sections.

## Important APIs, Types, And Functions
Exports `mod_sysfs_setup`, `mod_sysfs_teardown`, and `init_param_lock`. Internal helpers include `add_sect_attrs`, `remove_sect_attrs`, `add_notes_attrs`, `remove_notes_attrs`, `add_usage_links`, `del_usage_links`, `module_add_modinfo_attrs`, `module_remove_modinfo_attrs`, `mod_sysfs_init`, `mod_sysfs_fini`, and `mod_kobject_put`.

## Control Flow
Setup first initializes the module kobject under `module_kset`, rejects duplicate kobjects, creates `holders`, registers parameters, adds modinfo attributes, creates holder symlinks to dependency targets, then adds section and note attribute groups. Each failure label unwinds the already-created pieces in reverse. Teardown removes links, modinfo, parameters, driver/holder kobjects, note/section groups, and the module kobject.

## State And Persistence
State persists as sysfs kobjects, attributes, binary attributes, symlinks, `mod->sect_attrs`, `mod->notes_attrs`, `mod->modinfo_attrs`, `mod->holders_dir`, and parameter locks for the module lifetime.

## Dependencies And Integration Points
Depends on sysfs, module ktypes, kallsyms for section visibility and pointer hiding, module parameter sysfs helpers, `module_mutex`, and module use lists.

## Risks And Edge Cases
Section and note attributes share section names, so setup ordering matters. Pointer exposure must respect `kallsyms_show_value`. Kobject lifetime is synchronized through a completion in `mod_kobject_put`. Partial setup failure must remove exactly the initialized resources.

## Test Signals
Load modules with parameters, dependencies, note sections, and kallsyms enabled. Verify `/sys/module` attributes, holder links, pointer visibility restrictions, and clean teardown under load failure and unload.
