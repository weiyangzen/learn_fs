# sources/distributed-fs/ceph-client/mm/memcontrol-v1.h

## Purpose

This header declares the interface between the shared memory-controller code and the cgroup-v1-specific implementation in `memcontrol-v1.c`. It also provides common memcg iteration macros, shared declarations used by both cgroup v1 and v2 code, v1 resource-type encoding constants, and no-op stubs when `CONFIG_MEMCG_V1` is disabled.

## Important APIs, types, and functions

The common iteration macros are `for_each_mem_cgroup_tree(iter, root)` and `for_each_mem_cgroup(iter)`, both built on `mem_cgroup_iter()` and requiring `mem_cgroup_iter_break()` if the loop exits early. Common declarations include `drain_all_stock()`, `memcg_events()`, `memory_stat_show()`, and `mem_cgroup_private_id_get_online()`.

When `CONFIG_MEMCG_V1` is enabled, `do_memsw_account()` reports whether legacy memory+swap accounting is active by checking that the memory controller is not on the default hierarchy. The header declares v1 local stat/event readers, per-memcg event allocation, v1 memcg initialization/offline cleanup, soft-limit reset/removal, OOM prepare/finish/recover hooks, charge and uncharge hooks, stats formatting and reparenting helpers, kmem/tcp accounting helpers, and the `memsw_files[]` and `mem_cgroup_legacy_files[]` cftype arrays.

The `enum res_type` values `_MEM`, `_MEMSWAP`, `_KMEM`, and `_TCP` are used by cgroup-v1 file handlers to encode resource selection into `cftype.private`. Inline helpers include `memcg1_soft_limit_reset()`, `memcg1_tcpmem_active()`, and `memcg1_uncharge_skmem()` in v1 builds.

When `CONFIG_MEMCG_V1` is disabled, the header supplies static inline fallbacks that return success/false or do nothing: legacy memsw accounting is false, events allocation succeeds without allocation, v1 init/offline/OOM/charge/stat/kmem/tcp hooks are inert, and socket memory charges always succeed. This lets shared memcg code call v1 hooks without spreading preprocessor conditionals.

## Control flow

Shared memcg code includes this header and calls the declared hooks at lifecycle, charge, uncharge, swap, OOM, and stats points. In v1-enabled builds the calls resolve to `memcontrol-v1.c` behavior; in v1-disabled builds the compiler inlines the stubs and removes legacy behavior. `do_memsw_account()` is the runtime gate for legacy memory+swap accounting even when v1 support is compiled in, allowing the same kernel to distinguish default-hierarchy operation from legacy hierarchy operation.

The iteration macros start at `mem_cgroup_iter(root, NULL, NULL)` and feed each previous result back into `mem_cgroup_iter()`. The comment makes reference handling part of the contract: callers that break early must call `mem_cgroup_iter_break()` to release iterator references.

## State and persistence behavior

The header owns no standalone storage except inline effects on `struct mem_cgroup` fields. `memcg1_soft_limit_reset()` writes `PAGE_COUNTER_MAX` to `memcg->soft_limit`; `memcg1_tcpmem_active()` reads `memcg->tcpmem_active`; and `memcg1_uncharge_skmem()` decrements `memcg->tcpmem`. All persistent runtime state is stored in `struct mem_cgroup`, page counters, or implementation globals declared in the C file.

## Dependencies and integration points

The header depends on `linux/cgroup-defs.h` for cgroup subsystem declarations and on types supplied by surrounding memcg headers, including `struct mem_cgroup`, `struct folio`, `struct seq_file`, `struct seq_buf`, `struct cftype`, `gfp_t`, and page-counter primitives. It is an integration boundary between shared memcg code, cgroup core file registration, swap accounting, OOM handling, kernel memory accounting, TCP socket memory accounting, and cgroup-v1-only control files.

## Risks

The main risk is semantic drift between stubs and real v1 implementations. Stubs must preserve shared-code assumptions when v1 is disabled; for example, allocation hooks return success, OOM prepare returns true, and socket charges succeed so non-v1 builds do not fail legacy-only paths. `do_memsw_account()` must match cgroup hierarchy semantics or memory+swap accounting can be enabled in the wrong mode. The iteration macros can leak references if callers break without `mem_cgroup_iter_break()`.

The header also exposes `enum res_type` values used for `cftype.private` encoding in `memcontrol-v1.c`; adding or reordering values without updating file handlers would misroute reads and writes. Inline writes to memcg fields rely on the same concurrency expectations as the implementation file, including `WRITE_ONCE()` for soft-limit reset and page-counter operations for socket memory.

## Test signals

Build coverage should include `CONFIG_MEMCG_V1=y` and `CONFIG_MEMCG_V1=n`, with and without cgroup v2 as the default hierarchy. Runtime signals include successful registration of `mem_cgroup_legacy_files[]` and `memsw_files[]` in v1 mode, absence of those behaviors in non-v1 mode, correct memory+swap behavior gated by `do_memsw_account()`, and no link errors from shared memcg callers. Static analysis should flag early exits from `for_each_mem_cgroup*()` loops that omit `mem_cgroup_iter_break()`.
