# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/cmd.h

## Purpose
`cmd.h` defines the data-transfer structures and exported command-wrapper API used by HWS code to interact with mlx5 firmware. It keeps PRM command details out of higher-level context, table, action, matcher, and definer code.

## Important APIs, Types, And Functions
Important structs include FTE destination and attribute records, flow table create/modify/query attributes, flow group attributes, forward-table ownership records, RTC create attributes, alias object attributes, STC create/modify attributes, STE create attributes, definer create attributes, packet reformat create attributes, generated WQE attributes, and the large queried capability record. The STC modify union is the core action command schema and includes IDs, remove/insert header parameters, modify-header IDs, inline modify data, ASO fields, vport fields, STE-table jump fields, remove-words fields, trailer fields, and destination table/TIR IDs.

The API declares all create/modify/destroy/query helpers implemented in `cmd.c`, including `mlx5hws_cmd_query_caps()` and `mlx5hws_cmd_query_gvmi()`.

## Control Flow And State
The header itself stores no runtime state except through caller-owned structs. Many returned firmware IDs become persistent state in higher layers: flow table IDs in tables and forward islands, RTC IDs in matchers/action STE tables, STC/STE object bases in pools, definer IDs in the definer cache, and packet reformat IDs in actions.

## Dependencies And Integration Points
It depends on mlx5 core types, PRM enums, HWS pool chunks, and HWS context declarations. Context initialization consumes capability fields; table/action/definer code constructs these attributes and relies on `cmd.c` to emit firmware commands.

## Risks And Test Signals
Risks are stale or mismatched struct fields relative to firmware PRM definitions, unit confusion for sizes/log sizes/word counts, and missing initialization of boolean flags before command submission. Tests should validate every command attribute through successful create/destroy loops and negative firmware responses, with special attention to STC action unions and capability-dependent paths.
