# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/sf.h

## Purpose
`sf.h` provides inline helpers for mlx5 SubFunction capability and numbering. It abstracts compile-time `CONFIG_MLX5_SF` support and firmware capability fields for callers that need SF start IDs and limits.

## Important APIs, types, and functions
`mlx5_sf_start_function_id()` returns `sf_base_id`. When `CONFIG_MLX5_SF` is enabled, `mlx5_sf_supported()` returns the firmware `sf` capability and `mlx5_sf_max_functions()` returns `max_num_sf` or `1 << log_max_sf`. When disabled, support is always false and max functions is zero.

## Control flow
The helpers are pure inline queries with no side effects. Callers branch on support before creating or managing SF resources.

## State and persistence behavior
No state is stored. Values come from cached HCA capabilities in `struct mlx5_core_dev`.

## Dependencies and integration points
The header depends on Linux mlx5 driver capability macros. It is used by SF management and any code that sizes SF-related resources or IDs.

## Risks and edge cases
Callers must check support before trusting the base ID or maximum count. The fallback from `max_num_sf` to `log_max_sf` assumes firmware provides one of those encodings. Disabled builds compile out SF behavior through zero/false helpers.

## Test signals
Build with `CONFIG_MLX5_SF` enabled and disabled, verify max-function calculations on firmware exposing `max_num_sf` and legacy `log_max_sf`, and ensure callers skip SF setup when support is false.
