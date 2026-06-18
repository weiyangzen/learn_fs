# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/rule.h

## Purpose
`rule.h` declares the private HWS rule state and low-level rule helper API. It defines STE/tag sizes, rule lifecycle statuses, resize move states, match-tag storage, resize metadata, and the fields a rule needs for creation, update, deletion, action STE cleanup, and matcher resize.

## Important APIs, types, and functions
Constants define STE control size, action segment size, normal and jumbo match tag sizes, and jumbo tag offset. `enum mlx5hws_rule_status` tracks unknown, creating, created, updating, updated, deleting, deleted, failing, and failed states. `enum mlx5hws_rule_move_state` tracks idle, writing, and deleting during matcher resize.

`struct mlx5hws_rule_match_tag` overlays a jumbo tag with an action-reserved prefix plus normal match tag. `struct mlx5hws_rule_resize_info` stores old RTCs, rule index, move state, and saved WQE control/data segments. `struct mlx5hws_rule` stores matcher pointer, tag or resize info, current and old action STE chunks, active RTC IDs, status, pending WQEs, and `skip_delete`.

Declared helpers cover flow-source skip decisions, action STE free, resize remove/add, move-in-progress tests, and resize-info cleanup.

## Control flow
The header has no executable flow beyond declarations. `rule.c` mutates the declared state during create/update/delete/move, while matcher resize code calls move helpers and other modules free action STE chunks after completions.

## State and persistence behavior
The rule struct is the persistent handle supplied by API callers. Its RTC IDs and action STE chunks describe hardware resources currently associated with the rule. During resize, the union switches from tag storage to `resize_info`, which owns copied WQE segments required to recreate and delete the rule across matchers.

## Dependencies and integration points
The header depends on matcher declarations, action STE chunk types, WQE size constants, and public rule attributes. It is included by `internal.h`, matcher code, send completion code, BWC code, and action STE cleanup paths.

## Risks and edge cases
The union between `tag` and `resize_info` means code must know whether a matcher is resizable before reading deletion metadata. Status values must align with send completion transitions. `old_action_ste` is valid during updates only and must be freed after it is no longer referenced by hardware. `skip_delete` is specialized for complex rules and can intentionally suppress hardware deletion.

## Test signals
Build coverage plus rule create/update/delete, completion status transitions, action STE cleanup after update and delete, resizable matcher moves, non-resizable delete-tag storage, jumbo tag handling, and complex-rule skip-delete paths validate this header's contracts.
