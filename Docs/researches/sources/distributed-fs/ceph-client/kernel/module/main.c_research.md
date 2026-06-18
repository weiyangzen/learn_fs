# sources/distributed-fs/ceph-client/kernel/module/main.c

## Purpose
Implements the core Linux module loader and unloader. It validates ELF module images, checks signatures and version compatibility, lays out sections into executable/data module memory, resolves symbols, applies relocations, creates sysfs/proc/debug integration hooks, runs module init and exit code, handles reference counting and dependencies, and provides module address lookup.

## Important APIs, Types, And Functions
User entry points are `init_module`, `finit_module`, and `delete_module`. Exported helpers include `register_module_notifier`, `unregister_module_notifier`, `find_symbol`, `find_module`, `try_module_get`, `module_put`, `__symbol_get`, `__symbol_put`, `symbol_put_addr`, `module_refcount`, `module_flags`, `search_module_extables`, `is_module_address`, `__module_address`, `is_module_text_address`, `__module_text_address`, `module_for_each_mod`, and `print_modules`. Central load helpers include `elf_validity_cache_copy`, `early_mod_check`, `layout_and_allocate`, `add_unformed_module`, `simplify_symbols`, `apply_relocations`, `post_relocation`, `complete_formation`, `prepare_coming_module`, `load_module`, and `do_init_module`.

## Control Flow
`init_module` copies a user buffer; `finit_module` reads an fd, optionally decompresses, and deduplicates same-inode loads. Both call `load_module`. The loader checks signatures first, validates ELF headers/sections/indices/string tables, rewrites section headers, checks blacklist/vermagic/modversions, allocates final module memory, inserts an unformed unique module, allocates percpu data, discovers optional sections, resolves symbols and dependencies, applies relocations, finalizes arch/kallsyms/extables, parses parameters, sets up sysfs/livepatch/codetag state, frees the temporary image, then runs `do_init_module`. Successful init switches state to live, sends notifiers/uevents, drops the initial refcount, switches to core kallsyms, makes ro-after-init read-only, removes init memory from lookup structures, and queues init memory freeing. Unload via `delete_module` verifies capability, dependency and refcount state, marks the module going, runs exit, notifiers, livepatch/ftrace cleanup, and frees all module resources.

## State And Persistence
Global state includes `module_mutex`, RCU list `modules`, `mod_tree`, module address bounds, `module_wq`, notifier chain, sysctl-controlled `modules_disabled`, blacklist, last unloaded module diagnostics, and async init-free work. Per-module persistent state includes memory ranges, exported symbols, use links, taints, parameters, args, kallsyms, sysfs kobjects, percpu storage, and optional livepatch/codetag/debug metadata.

## Dependencies And Integration Points
Integrates with LSM/audit, ELF and arch relocation hooks, execmem and strict RWX, kallsyms, modversions, module signatures, sysfs/procfs/debugfs, ftrace, livepatch, jump labels, tracepoints, BTF, dynamic debug, CFI, exception tables, kmemleak, percpu allocator, codetags, async, kmod, and userspace module tools.

## Risks And Edge Cases
The path has many ordered invariants: signatures must be stripped before ELF validation; duplicate module detection occurs before and after final allocation; state transitions protect symbol users; RCU grace periods protect module lists and kallsyms; init memory freeing is deferred; strict RWX changes must happen after relocation and before execution. Error unwinding is high risk because each stage owns different resources. Forced loading/unloading taints the kernel and can bypass compatibility checks. Symbol namespace, GPL-only symbol, and proprietary-taint inheritance rules must be enforced consistently.

## Test Signals
Signals include successful `insmod`/`rmmod`, duplicate load races returning `-EEXIST` or `-EBUSY`, modversion mismatch rejection, forced load tainting, signature enforcement, compressed loads, bad ELF rejection, dependency refcount correctness, sysfs/proc visibility, kallsyms stack traces, strict RWX permission checks, livepatch module load, and fault-injection coverage for every cleanup label.
