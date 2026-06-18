# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_types.h

## Purpose
This header is the central private contract for the mlx5 software-steering direct-rule subsystem. It defines core constants, match structures, domain/table/matcher/rule/action state, ICM chunk abstractions, send-ring support types, command wrappers, and internal helper prototypes.

## Important APIs, Types, And Functions
Key constants include STE sizes, action limits, ICM chunk sizes, ICM memory types, match criteria bits, action type enum values, action capability bits, and flex-parser bounds. Inline helpers cover flex parser family checks, hash-table refcounting, domain RX/TX locking, chunk size conversions, and table growth thresholds.

Important structures include `mlx5dr_ste`, `mlx5dr_ste_htbl`, `mlx5dr_ste_build`, `mlx5dr_ste_actions_attr`, `mlx5dr_match_param` and its `outer`, `inner`, `misc*` substructures, `mlx5dr_cmd_caps`, `mlx5dr_domain`, `mlx5dr_table`, `mlx5dr_matcher`, `mlx5dr_action`, `mlx5dr_rule`, `mlx5dr_icm_chunk`, send-ring QP/CQ/MR types, and firmware command information structures.

The file also declares most internal subsystem APIs: STE building, action compilation, rule helpers, ICM pool management, command wrappers, send-ring posting, flow-table helper creation, pattern/argument managers, and firmware checksum recalculation helpers.

## Control Flow
There is little executable code, but the type graph describes subsystem flow. Domains own capabilities, ICM pools, send rings, caches, and STE context. Tables own RX/TX anchors and matcher lists. Matchers own builder arrays derived from masks. Rules point to RX/TX last STEs and hold action memberships. Actions carry a discriminated union based on `enum mlx5dr_action_type`. ICM chunks bind software arrays, hardware STE byte arrays, and miss lists.

## State And Persistence
This header defines the persistent in-memory state for software steering. Long-lived objects are refcounted domains, tables, matchers, actions, STE hash tables, pattern objects, and rewrite argument objects. Hardware persistence is represented by ICM chunks, firmware flow table IDs, modify-header object IDs, reformat IDs, sampler IDs, and command-created resources. Locks are per RX/TX NIC domain, and `mlx5dr_domain_lock()` always locks RX then TX and unlocks in reverse.

## Dependencies And Integration Points
It includes kernel mlx5/vport, refcount, flow steering core, work queue, mlx5 library, hardware IFC direct-rule layouts, public `mlx5dr.h`, and debug definitions. It is included widely by SW steering C files, making it the shared ABI between domain, table, matcher, rule, action, STE, command, ICM, and send modules.

## Risks
This file is high blast-radius. Structure layout changes affect many compilation units. Match parameter fields are consumed/mutated by builders, so semantic mistakes can appear as unsupported leftover fields or missed matches. Lock ordering is encoded in inline helpers and must remain consistent. Refcount fields are plain in several internal objects, so lifetime discipline depends on callers. Capability flags gate hardware features such as SW owner, flex parsers, ranges, and pattern arguments; stale capability interpretation can create invalid STEs.

## Test Signals
Broad build coverage is essential. Runtime signals include domain create/destroy, all table types, matcher builder selection for every match criteria bit, rule insertion/removal with all action types, hash-table growth/collision behavior, ICM allocation/free, send-ring posts, and capability-dependent paths such as match ranges, Geneve TLV, GTP-U flex parsers, and modify-header pattern arguments.
