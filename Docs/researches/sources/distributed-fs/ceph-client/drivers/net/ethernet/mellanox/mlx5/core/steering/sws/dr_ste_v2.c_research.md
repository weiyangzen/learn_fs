# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_ste_v2.c

## Purpose
This file defines the steering format v2 context by reusing almost all v1 builders, setters, and action assembly while substituting the v2 modify-header field mapping and a slightly different action capability mask.

## Important APIs, Types, And Functions
The only exported function is `mlx5dr_ste_get_ctx_v2()`. It returns a static `mlx5dr_ste_ctx` whose builder and getter/setter pointers mostly target `dr_ste_v1_*` functions. The context uses `dr_ste_v2_action_modify_field_arr` from `dr_ste_v2.h`.

## Control Flow
Generic STE code selects this context when the domain reports steering format v2. From that point, rule building, tag building, miss/hit address programming, action packing, and pre-send preparation run through the inherited v1 implementations. Modify-header software fields are translated through the v2 field array.

## State And Persistence
The file owns only the static function table. Persistent state is in the domain, STE buffers, ICM chunks, and modify-header objects allocated by the inherited helpers.

## Dependencies And Integration Points
It includes `dr_ste_v1.h` for all shared behavior and `dr_ste_v2.h` for v2 hardware field-code definitions. It is selected indirectly by `mlx5dr_ste_get_ctx()` in the generic STE layer.

## Risks
The intentional inheritance means any behavioral change in v1 action ordering or builder mutation also affects v2. The context drops `DR_STE_CTX_ACTION_CAP_POP_MDFY` compared with v1, so tests must ensure pop-VLAN plus modify-header splitting remains correct on v2 devices. A stale v2 modify-field array would corrupt modify-header actions even if matching still works.

## Test Signals
Test modify-header actions touching metadata register C fields, because v2 changes those field codes. Also test mixed pop/modify actions to verify action-cap splitting and traffic tests for representative v1-inherited builders.
