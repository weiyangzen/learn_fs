# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/rule.c

## Purpose
`rule.c` implements low-level HWS rule create, destroy, action update, and resize-move operations. It builds STE WQEs from match templates and action templates, allocates action STE chunks when rules require multiple STEs, tracks rule status and delete/resize metadata, chooses RX/TX RTCs based on flow source, and validates IP-version consistency for matchers that match both ethertype and IP version.

## Important APIs, types, and functions
Public APIs are `mlx5hws_rule_create()`, `mlx5hws_rule_destroy()`, `mlx5hws_rule_action_update()`, `mlx5hws_rule_skip()`, `mlx5hws_rule_free_action_ste()`, `mlx5hws_rule_move_hws_add()`, `mlx5hws_rule_move_hws_remove()`, `mlx5hws_rule_move_in_progress()`, and `mlx5hws_rule_clear_resize_info()`.

Key internal helpers initialize dependent WQEs, copy match tags for updates, save/delete/load delete information, save resize information, allocate action STE chunks, create/update HWS WQEs, handle failed destroys, generate completions, perform resize add/remove, precheck enqueue conditions, and check outer/inner IP version consistency.

## Control flow
Rule creation first checks IP-version consistency against matcher state, records the matcher in the rule handle, verifies that the matcher is not resizing and that the send queue has room, validates template indexes and match parameters, then calls `hws_rule_create_hws()`. That function initializes rule status and send attributes, allocates a dependent WQE, fills RTC IDs based on flow source and matcher/collision RTCs, allocates action STE chunks if the action template requires them, applies action setters from last STE to first, creates the match tag through the definer for new rules, sends action STEs and match STEs, saves delete info for later removal, saves resize info for resizable matchers, increments queue rule count, and flushes dependent WQEs unless burst mode defers notification.

Destroy validates user data and queue capacity, rejects rules still creating/updating, handles already failed rules by generating a delete completion and freeing action STEs, handles complex `skip_delete` rules by completing without hardware delete, otherwise sends a deactivate STE WQE using saved tag/delete information and clears delete info. Action update requires a resizable matcher, rule-index optimization, or insert-by-index mode and a created rule; it reuses `hws_rule_create_hws()` with `match_param == NULL`, saves old action STEs, copies the prior tag, and writes replacement action/match STEs.

Resize move is two-phase. `mlx5hws_rule_move_hws_add()` verifies the rule belongs to a matcher in resize, saves old RTC IDs and rule index in `resize_info`, resets active RTC IDs, writes the saved STE data into the destination matcher RTCs, and marks move state writing. `mlx5hws_rule_move_hws_remove()` later deactivates the old RTC IDs using saved delete info and marks state deleting.

## State and persistence behavior
Rule state includes matcher pointer, match tag or resize info, current and old action STE chunks, active RX/TX RTC IDs, status, pending WQE count, and `skip_delete`. Non-resizable rules store the match tag for deletion. Resizable rules store full WQE control/data segments and old RTC IDs so they can be moved and later removed. Hardware state persists in STE tables and action STE chunks until deactivation and completion.

## Dependencies and integration points
This file depends on matcher attributes and RTC IDs, definer tag creation, action template setters, action STE pool allocation, send engine WQE posting/dependency handling/completion generation, PRM WQE layouts, Ethernet/IP constants, and BWC/complex rule behavior through `skip_delete`. It is called by public HWS users and matcher resize logic.

## Risks and edge cases
Asynchronous status transitions are central: destroying a rule while creating/updating returns `-EBUSY`, and failed rules follow a synthetic cleanup path. Action update can leak or prematurely free old action STEs if completion ordering is wrong. Delete requires saved match tags or resize data; missing metadata prevents correct deactivation. Flow-source optimization skips RX or TX RTCs, so wrong skip logic can install rules in the wrong direction. IP-version state is mutable on the matcher; inconsistent insertion order or concurrent rule creation can reject later rules or leave a matcher constrained unexpectedly. Burst mode requires callers to drain queues.

## Test signals
Test create/destroy for single-STE and multi-STE action templates, jumbo match tags, RX-only/TX-only flow sources, collision matcher retry RTCs, insert-by-index rules, action updates with and without action STE replacement, destroy during create/update, failed queue state cleanup, burst and non-burst behavior, resize move add/remove, complex `skip_delete`, and IP-version mismatch cases for outer and inner headers.
