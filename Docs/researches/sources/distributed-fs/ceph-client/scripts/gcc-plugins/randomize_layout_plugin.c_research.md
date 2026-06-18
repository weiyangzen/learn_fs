# sources/distributed-fs/ceph-client/scripts/gcc-plugins/randomize_layout_plugin.c

Purpose: GCC plugin that randomizes selected kernel `struct` field layouts and warns about casts that can violate randomized type boundaries.

Important APIs/functions: Attribute handlers support `randomize_layout`, `no_randomize_layout`, `randomize_considered`, and `randomize_performed`. PRNG functions `raninit()`/`ranval()` seed from `randomize_layout_seed.h` plus struct name hash. `relayout_struct()` shuffles fields, preserves trailing flexible arrays, applies attributes, and relayouts the type. `randomize_type()`, `finish_type()`, and `randomize_layout_finish_decl()` hook type/declaration finalization. `find_bad_casts_execute()`, `check_global_variables()`, and helpers detect suspicious pointer casts/initializers.

Control flow: On type finish, eligible structs explicitly marked or consisting purely of function pointers are shuffled unless opted out, already considered, UAPI, or special-cased. Declaration finish resets and relayouts variables of randomized types, including flexible-array initializer sizing. An inserted GIMPLE pass after SSA scans local assignments for casts involving randomized record pointers and reports mismatches.

State/persistence: Global `performance_mode` and `shuffle_seed[4]`. Mutates GCC type field chains, type attributes, declaration layout fields, and emits diagnostics.

Dependencies/integration: Requires generated private seed header, GCC plugin internals, GIMPLE pass generator, and kernel annotations. Kbuild generates `randomize_layout_seed.h`.

Risks: Field-chain mutation can break code relying on positional initialization; plugin enforces `designated_init` to reduce this. Seed exposure reveals layouts. Performance mode has a comment noting group shuffle is currently a no-op. Cast detection is heuristic and must avoid false positives such as `container_of` and `IS_ERR` patterns.

Test signals: Marked/unmarked/no-randomize structs, pure ops structs, flexible arrays, UAPI path rejection, deterministic seed reproducibility, bad cast diagnostics, global/local constructor checks, and performance mode behavior.
