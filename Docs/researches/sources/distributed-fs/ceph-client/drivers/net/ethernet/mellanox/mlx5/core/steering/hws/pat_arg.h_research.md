# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/pat_arg.h

## Purpose
`pat_arg.h` declares the pattern-cache and argument-object API for HWS modify-header and related action data. It defines the supported argument chunk sizes and the in-memory cache structures used by `pat_arg.c`.

## Important APIs, types, and functions
`enum mlx5hws_arg_chunk_size` defines supported chunk orders from one to four 64-byte chunks, with `MLX5HWS_ARG_CHUNK_SIZE_MAX` as an invalid/out-of-range marker. Constants define 8-byte modify actions and 64-byte argument data chunks. `struct mlx5hws_pattern_cache` owns the mutex and list, while `struct mlx5hws_pattern_cache_item` stores firmware pattern ID, duplicated pattern bytes, action count, refcount, and list node.

Declared functions cover argument size conversion, pattern cache init/uninit/get/put, action verification, argument create/destroy, modify-header argument create, reparse detection, WQE-based argument writes, inline synchronous writes, decap-L3 writes, and NOP calculation.

## Control flow
The header has no runtime flow. Action creation code calls these helpers to allocate or reuse firmware pattern objects, allocate argument memory with optional data upload, and normalize modify action lists before action templates are processed.

## State and persistence behavior
The declared cache structures persist under the HWS context. Pattern items refcount firmware pattern objects. Argument IDs returned by create functions represent firmware resources that persist until explicitly destroyed. WQE write helpers mutate argument memory referenced by actions and rules.

## Dependencies and integration points
The API depends on HWS context and send engine types, PRM modify-action encoding, and action code that creates modify-header STCs. It is included through `internal.h` by action, context, and rule-related modules.

## Risks and edge cases
The four supported chunk sizes cap single argument data at 512 bytes. Callers must not confuse data byte size with log chunk size. Cache refcounts are protected by the cache lock; bypassing get/put can leak or prematurely destroy firmware pattern objects. NOP location output is a bitmap, so action counts must fit its width.

## Test signals
Build coverage plus modify-header action creation, cache reuse, invalid action sizes, max-size arguments, reparse detection, NOP insertion, and write completion behavior provide the main validation signals.
