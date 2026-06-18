# sources/distributed-fs/ceph-client/kernel/static_call_inline.c

## Purpose
`static_call_inline.c` initializes, sorts, tracks, and patches inline static call sites for the core kernel and modules. Static calls let a call site be dynamically retargeted with near-direct-call performance by patching text rather than using an indirect call.

## Important APIs, types, and functions
- `static_call_initialized` and `static_call_force_reinit()` manage init state and early reinit behavior.
- Address/key helpers decode relative `struct static_call_site` fields and site flags (`INIT`, `TAIL`).
- `__static_call_update()` changes a key's target function, patches the trampoline, then patches all eligible call sites for built-in and module users.
- `__static_call_init()` sorts call sites by key, marks init-section sites, links sites into key metadata, and applies initial architecture transforms.
- Module integration: `static_call_add_module()`, `static_call_del_module()`, `static_call_module_notify()`, and `static_call_module_nb`.
- Text reservation: `static_call_text_reserved()` checks whether a text range overlaps static-call patch sites.
- Optional selftest defines `sc_selftest`, updates it between `func_a` and `func_b`, and verifies results.

## Control flow
Early init calls `static_call_init()`, which locks CPU hotplug and `static_call_mutex`, initializes all built-in sites, registers the module notifier, then marks the framework initialized. Updating a key locks the same domains, exits early if the target did not change, patches the trampoline, and walks each associated site list, skipping init-only sites after init and warning on non-text addresses. When modules load, raw trampoline references are fixed up to real keys, module sites are initialized and linked; on unload their `static_call_mod` records are removed.

## State and persistence behavior
State is stored in static-call keys, their `func` pointer, their site pointer or module list, and module-owned `static_call_mod` allocations. The framework permanently patches executable text until later updates repatch it. Init-section markers prevent patching discarded init text after boot.

## Dependencies and integration points
It depends on linker sections for `__start/__stop_static_call_sites` and `__start/__stop_static_call_tramp_key`, architecture `arch_static_call_transform()`, CPU hotplug read locking, module notifier callbacks, `sort()`, kernel text address validation, and module text lookup. It integrates with live text patching reservations through `static_call_text_reserved()`.

## Risks
Text patching requires strict synchronization and accurate site metadata. Bad module fixups can expose sensitive static-call keys, so non-exported module references are resolved through trampoline-key lookup. Allocation failure during module init must unwind partial state. Incorrect init-section classification could patch freed text or leave live sites stale.

## Test signals
`CONFIG_STATIC_CALL_SELFTEST` provides a direct behavior check. Additional signals are module load/unload tests with static calls, architecture text-patching tests, lockdep around `static_call_mutex`/CPU locks, warnings from "can't patch static call site", and failures from module fixup warnings.
