# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_ste.h

## Purpose
`dr_ste.h` defines shared constants, field-setting macros, action modify enums, and the `struct mlx5dr_ste_ctx` vtable used by the software steering code to isolate generic rule/matcher logic from STE hardware-format versions.

## Important APIs, Types, And Functions
The header exports constants for IP/L4/VLAN encodings and L2 header lengths, helper macros such as `DR_STE_SET_VAL`, `DR_STE_SET_TAG`, `DR_STE_SET_ONES`, `DR_STE_SET_TCP_FLAGS`, `DR_STE_SET_MPLS`, and `DR_STE_SET_FLEX_PARSER_FIELD`, and parser helpers like `dr_ste_calc_flex_parser_offset()`. It declares `mlx5dr_ste_conv_bit_to_byte_mask()` and version context getters `mlx5dr_ste_get_ctx_v0()` through `mlx5dr_ste_get_ctx_v3()`.

The central type is `struct mlx5dr_ste_ctx`, which contains builder initializers for L2/L3/L4/tunnel/register/flex-parser match types, core STE getters/setters, action encoding callbacks, modify-header field metadata, reformat action callbacks, and an optional postsend preparation hook.

## Control Flow
Generic code calls wrapper functions in `dr_ste.c`; those wrappers populate common fields in `struct mlx5dr_ste_build` and invoke the matching `mlx5dr_ste_ctx` function pointer. Version-specific files fill this vtable with callbacks that know their hardware layout. Macros both set hardware tag/mask fields and clear consumed software fields, which drives the residual-mask and residual-value validation model.

## State And Persistence
The header itself owns no runtime state, but its vtable controls all persistent hardware encoding state written into STE ICM memory. The field-clearing macros intentionally mutate temporary masks or values to mark fields consumed. `actions_caps`, `modify_field_arr`, and `modify_field_arr_sz` describe the action surface supported by the selected STE version.

## Dependencies And Integration Points
It includes `dr_types.h` and relies on mlx5 IFC structures through the `MLX5_SET` family used by implementation files. `dr_matcher.c` selects builders through this interface, `dr_rule.c` invokes generated builder chains, `dr_actions` code uses action callbacks and modify-field mappings, `dr_send.c` calls `prepare_for_postsend()`, and `dr_ste.c` dispatches version selection.

## Risks
Because macros clear source fields, callers must pass temporary copies when they need to reuse match parameters. Adding a builder callback to generic code requires adding it to this context and all supported version implementations or guarding for NULL. Flex parser offset calculation assumes groups of four parser IDs and tag layout compatibility. Incorrect length constants for L2 decap actions would reject valid reformat data or emit malformed modify actions.

## Test Signals
Compile coverage across all STE format versions is important because the vtable is broad. Unit-like signals include macro consumption behavior, flex parser offset placement, TCP flag expansion, MPLS field packing, action modify field lookups, and NULL handling for optional callbacks. Integration tests should exercise the same match/action feature on each supported steering format version.
