# `sources/distributed-fs/ceph-client/include/linux/mlx5/fs_helpers.h`

## Purpose

`fs_helpers.h` provides inline helpers for identifying whether a flow-steering match specification represents an outer IPv4 or IPv6 flow. It abstracts the difference between newer devices that support matching on an explicit outer IP version field and older devices that require ethertype matching.

## Important APIs, Types, and Constants

- `MLX5_FS_IPV4_VERSION` and `MLX5_FS_IPV6_VERSION` define the expected IP version nibble values.
- `_mlx5_fs_is_outer_ipv_flow()` is the common helper. It receives an `mlx5_core_dev`, match criteria array, match value array, and target version.
- `mlx5_fs_is_outer_ipv4_flow()` and `mlx5_fs_is_outer_ipv6_flow()` are the public inline wrappers for IPv4 and IPv6.

## Control Flow and Lifetimes

The helper first checks `MLX5_CAP_FLOWTABLE_NIC_RX(mdev, ft_field_support.outer_ip_version)`. If the device does not support explicit outer IP version matching, it maps the requested version to `ETH_P_IP` or `ETH_P_IPV6` and verifies that the ethertype mask is exact (`0xffff`) and the ethertype value matches. If explicit IP-version matching is supported, it verifies that the `ip_version` mask is exact (`0xf`) and the match value is the requested version. Unsupported version input returns false.

The function reads from caller-owned match arrays only; it allocates and persists no state.

## State and Persistence Behavior

There is no persistent state. The observable behavior depends on the device's flow-table capability bits and the contents of `match_c` and `match_v`, which are expected to be firmware-layout `fte_match_param` arrays.

## Dependencies and Integration Points

The helper depends on `mlx5_ifc.h` layout macros (`MLX5_ADDR_OF`, `MLX5_GET`) and flow-table capability macros from the mlx5 include environment. It integrates with flow-steering users that need to classify or validate specs before installing rules, especially code that must work across devices with different field support.

## Risks and Edge Cases

- The function assumes `match_c` and `match_v` point to valid `fte_match_param` buffers; no null or bounds checks are present.
- For older devices, flows that match IP version indirectly through other fields but do not have an exact ethertype mask will return false.
- For newer devices, exact `ip_version` mask/value is required; partial masks intentionally do not count as IPv4/IPv6 identification.
- The capability check is NIC RX-specific. Callers applying it to other table types must confirm the capability is meaningful for their path.

## Test Signals

Unit-style validation can construct match arrays for IPv4 and IPv6 using both ethertype and explicit `ip_version` fields, toggle mocked capability values, and verify false results for unsupported versions, partial masks, wrong values, and zero masks. Integration coverage should include flow-steering callers on devices with and without `outer_ip_version` support.
