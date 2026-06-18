# sources/distributed-fs/glusterfs/libglusterfs/src/ctx.c

## Purpose
This file creates and initializes the process-wide GlusterFS context object and lazily attaches a timer-wheel context to it. The context is the shared runtime root for graphs, volume files, memory pools, logging defaults, command arguments, host identity, and statistics.

## Important APIs, types, and functions
`glusterfs_ctx_new()` allocates and initializes `glusterfs_ctx_t`; `global_ctx` stores the first created context. `glusterfs_ctx_tw_get()` lazily creates and references `struct gf_ctx_tw`, whose `timer_wheel` comes from `gf_tw_init_timers()`. `glusterfs_ctx_tw_put()` releases that reference, and `glusterfs_ctx_tw_destroy()` cleans pending timers with `gf_tw_cleanup_timers()`.

## Control flow
Context creation uses plain `CALLOC` before memory accounting is finalized, initializes graph/mempool/volfile lists, daemon pipe descriptors, default log level, valgrind-tool mode, dict statistics atomics, hostname storage, and context locks. Timer-wheel access locks `ctx->lock`, either references the existing `ctx->tw` or allocates and initializes a new one, then returns the raw timer-wheel pointer.

## State and persistence behavior
The file owns in-memory process state only. `global_ctx` is set once to the first created context. The hostname is copied from the running host. Timer-wheel state persists until all `GF_REF` holders release it and the destroy callback runs.

## Dependencies and integration points
It depends on `glusterfs/globals.h` for context structures and global memory-accounting state, `timer-wheel.h` for timer lifecycle, pthread locks, atomics, and list macros. Many libglusterfs subsystems rely on `THIS->ctx` or `global_ctx` for memory pools, logging, stats, and graph state.

## Risks and edge cases
`global_ctx` assignment is not synchronized, so concurrent context creation can race. `glusterfs_ctx_tw_get()` does not check allocation or `gf_tw_init_timers()` failure before dereferencing and returning `ctx_tw->timer_wheel`. `glusterfs_ctx_tw_put()` assumes `ctx->tw` is non-NULL. Context destruction is not present here, so ownership of allocated hostname and locks must be handled elsewhere.

## Test signals
Tests should assert initialized defaults, hostname allocation failure behavior through fault injection, global context first-set behavior, timer-wheel lazy creation and reference release, and failure paths for timer allocation. Concurrency tests around first timer access and context creation would expose races.
