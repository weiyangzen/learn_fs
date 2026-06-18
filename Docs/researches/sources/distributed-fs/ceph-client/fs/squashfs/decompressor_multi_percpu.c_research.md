# sources/distributed-fs/ceph-client/fs/squashfs/decompressor_multi_percpu.c

## Purpose

This file implements the per-CPU decompressor mode. It allocates one backend stream per possible CPU and uses a `local_lock_t` to serialize decompression on the current CPU's stream.

## Important APIs, Types, and Functions

It exports `squashfs_decompressor_percpu`. The internal `struct squashfs_stream` holds a backend stream pointer and local lock. Functions are `squashfs_decompressor_create()`, `squashfs_decompressor_destroy()`, `squashfs_decompress()`, and `squashfs_max_decompressors()`.

## Control Flow

Create allocates percpu storage and initializes a backend stream for each possible CPU, then frees shared compression options. Decompress maps `msblk->stream` back to percpu storage, locks the current CPU stream, runs backend decompression, unlocks, and reports corrupt data on error. Destroy frees all per-CPU backend streams and the percpu allocation.

## State and Persistence Behavior

The per-mount state is a percpu pointer stored as `msblk->stream`. Stream count is fixed at mount time to `num_possible_cpus()`, not demand-based.

## Dependencies and Integration Points

Selected by `CONFIG_SQUASHFS_DECOMP_MULTI_PERCPU`; usable through `threads=percpu` when mount-time choice is compiled. It depends on percpu and local-lock kernel APIs and backend decompressor hooks.

## Risks and Edge Cases

Allocation failures during partial CPU initialization must free already-created streams. CPU hotplug semantics are simplified by allocating for possible CPUs. This mode can consume more memory than single or demand-based multi on large systems.

## Test Signals

Mount/read tests on SMP systems, CPU hotplug stress where available, lockdep/local-lock checking, and memory footprint comparisons across CPU counts.
