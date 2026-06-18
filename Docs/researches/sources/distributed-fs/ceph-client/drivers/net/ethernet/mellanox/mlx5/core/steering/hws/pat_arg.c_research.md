# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/pat_arg.c

## Purpose
`pat_arg.c` implements HWS modify-header pattern caching and modify-header argument allocation/writes. It converts modify-action sizes into firmware argument allocation orders, determines when actions require packet reparse, caches firmware header-modify pattern objects, writes argument data through HWS send queues, validates modify actions, and inserts NOP actions between dependent modifications.

## Important APIs, types, and functions
Size helpers are `mlx5hws_arg_data_size_to_arg_log_size()`, `mlx5hws_arg_data_size_to_arg_size()`, `mlx5hws_arg_get_arg_log_size()`, and `mlx5hws_arg_get_arg_size()`. Pattern cache APIs are `mlx5hws_pat_init_pattern_cache()`, `mlx5hws_pat_uninit_pattern_cache()`, `mlx5hws_pat_get_pattern()`, and `mlx5hws_pat_put_pattern()`. Argument APIs are `mlx5hws_arg_create()`, `mlx5hws_arg_destroy()`, `mlx5hws_arg_create_modify_header_arg()`, `mlx5hws_arg_write()`, `mlx5hws_arg_decapl3_write()`, and `mlx5hws_arg_write_inline_arg_data()`. Validation and normalization APIs are `mlx5hws_pat_verify_actions()`, `mlx5hws_pat_require_reparse()`, and `mlx5hws_pat_calc_nop()`.

## Control flow
Pattern lookup locks the context pattern cache, searches for an equivalent pattern, moves hits to the list head as a simple LRU behavior, increments refcount, and returns the cached firmware pattern ID. On miss it creates a firmware header-modify pattern object, duplicates the pattern into a new cache item, stores refcount one, and returns the new ID. Put finds by pattern ID, decrements refcount, and when it reaches zero removes the cache item and destroys the firmware object.

Argument creation maps data size to a single-argument log size, adds the bulk log size, verifies firmware caps, creates an argument object, optionally writes initial data through the control send queue, and returns the base ID. Inline writes lock `ctx->ctrl_lock`, use the last send queue as control queue, post one or more table-access WQEs of 64 bytes each, flush, and drain synchronously. Decap-L3 writes prepare special decap data before posting.

`mlx5hws_pat_require_reparse()` scans modify actions and returns true for insert/remove/unknown actions or modifications of ethertype/next-header fields. `mlx5hws_pat_calc_nop()` detects adjacent dependent actions where one reads or writes the other's source/destination or both write the same destination, inserts a NOP before the later action, records the location bitmap, and copies the resulting sequence.

## State and persistence behavior
Pattern cache state is a mutex-protected linked list of firmware pattern IDs, duplicated pattern data, action count, and refcount. Argument objects are firmware resources created under the context PD and destroyed by ID. Writes mutate hardware argument memory and can be asynchronous at the WQE level unless the inline helper drains synchronously.

## Dependencies and integration points
This file depends on PRM modify-action layouts, HWS command helpers for pattern and argument objects, HWS send engine posting, action helper `mlx5hws_action_prepare_decap_l3_data()`, context caps and control lock, and firmware PD number. It feeds action creation and rule application paths that need modify-header or reformat argument storage.

## Risks and edge cases
Pattern comparison intentionally ignores SET/ADD values and compares only control words, while COPY/ADD_FIELD compare full words. That is correct for separating pattern from argument data but risky if a future action encodes structural fields outside the compared portion. Cache uninit only frees the cache object; callers must have put all patterns first. Argument size must stay within firmware granularities. `mlx5hws_arg_write()` uses multiple WQEs for data larger than 64 bytes, so completion/user-data assumptions must match the caller. NOP insertion can fail if `max_actions` cannot accommodate dependencies.

## Test signals
Test pattern cache hit/miss/refcount/destroy, equivalent SET patterns with different values, COPY patterns with different fields, argument size boundary mapping, invalid firmware argument sizes, inline write drain failure, multi-WQE argument writes, decap-L3 argument formatting, reparse detection for ethertype/next-header/insert/remove actions, and NOP insertion for dependent modify sequences.
