# sources/distributed-fs/ceph-client/drivers/clk/qcom/reset.h

## Purpose
This header declares the shared reset descriptor and controller types used by Qualcomm clock-controller drivers, plus the exported `qcom_reset_ops` operations implemented in `reset.c`.

## Important APIs, types, and functions
- `struct qcom_reset_map` describes one reset line: register offset, bit index, optional pulse delay in microseconds, and optional multi-bit `bitmask`.
- `struct qcom_reset_controller` bundles a reset map, target `struct regmap`, and embedded `struct reset_controller_dev`.
- `to_qcom_reset_controller()` converts a reset-controller device pointer back to the qcom container.
- `extern const struct reset_control_ops qcom_reset_ops` is the operation table shared by qcom CC drivers.

## Control flow
Clock-controller drivers define static arrays of `qcom_reset_map` and pass them through qcom CC descriptors. The common probe path creates a `qcom_reset_controller`, sets up the embedded reset framework device, and routes reset framework callbacks to `qcom_reset_ops`.

## State and persistence behavior
The header defines no runtime state by itself. It shapes how reset state is represented: static reset maps plus a regmap pointer to persistent hardware reset registers.

## Dependencies and integration points
It includes Linux reset-controller declarations and forward-declares `struct regmap`. It is included by qcom CC drivers with reset support and by `reset.c`.

## Risks
The macro includes a trailing semicolon in its definition, which matches current usage but can surprise unusual expression contexts. `qcom_reset_map` can represent either a bit or bitmask; authors must avoid setting inconsistent fields. Map order must match dt-binding reset IDs.

## Test signals
Compile coverage from qcom CC drivers is the primary signal. Runtime tests should indirectly validate that maps declared with this type register reset controls and that both bit and bitmask entries operate through `qcom_reset_ops`.
