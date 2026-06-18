# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/matcher.h

## Purpose
`matcher.h` declares the private matcher data model and constants for mlx5 HWS. It captures sizing heuristics, matcher flags, match template layout, match STE identifiers, IP-version tracking, and inline predicates used by matcher and rule code.

## Important APIs, types, and functions
Constants define assured collision table behavior, update multiplier, and maximum attachable action templates. `enum mlx5hws_matcher_flags` identifies collision, resizable, and isolated matchers. `struct mlx5hws_match_template` owns a definer, field-copy array, copied match parameters, criteria enable mask, and field-copy count. `struct mlx5hws_matcher_match_ste` stores RTC IDs and STE base IDs for RX and TX. `struct mlx5hws_matcher` combines table pointer, attributes, template arrays, action STE sizing, flags, IP-version match tracking, end FT ID, collision matcher, resize destination, match STE IDs, and table list node.

Inline helpers test jumbo match templates, resizable state, resize-in-progress state, isolated state, and insert-by-index mode. The header declares `mlx5hws_matcher_update_end_ft_isolated()`.

## Control flow
This header contains only inline predicates. Runtime flow is implemented in `matcher.c` and `rule.c`; they use these predicates to choose RTC creation, action STE allocation, delete-info storage, resize behavior, and isolated matcher chaining.

## State and persistence behavior
The structs declared here are the persistent in-memory state for match templates and matchers. Firmware object IDs in `match_ste` and `end_ft_id` remain valid until matcher destruction. The IP-version fields are mutable runtime constraints updated as rules are inserted.

## Dependencies and integration points
The header depends on definer types, table attributes from the public HWS API, Linux lists, and table/rule code. It is included by `internal.h`, so it is visible throughout HWS internals.

## Risks and edge cases
Small bitfields encode whether matchers have seen outer/inner ethertype or IP-version fields and what IP version is allowed. Incorrect initialization or mutation can reject valid rules or accept inconsistent rules. Collision matchers share templates with their parent, so ownership must be handled in implementation. Maximum attached action templates limits BWC or dynamic update behavior.

## Test signals
Build coverage plus matcher create/destroy, collision matcher creation, jumbo match templates, insert-by-index rules, isolated matchers, dynamic AT attach up to the maximum, and IP-version consistency checks are the relevant signals.
