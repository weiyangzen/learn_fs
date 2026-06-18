# sources/distributed-fs/ceph-client/include/linux/mfd/syscon.h

## Purpose

This 80-line header is the generic Linux syscon API for looking up and registering regmaps backed by system-controller device nodes.

## Important APIs, Types, and Functions

When `CONFIG_MFD_SYSCON` is enabled it declares `device_node_to_regmap()`, `syscon_node_to_regmap()`, compatible and phandle lookup helpers including args and optional variants, and `of_syscon_register_regmap()`. When disabled, inline stubs return `ERR_PTR(-ENOTSUPP)`, `NULL` for optional lookup, or `-EOPNOTSUPP`.

## Control Flow

With syscon enabled, callers resolve device-tree nodes or phandles to shared regmaps. With syscon disabled, control returns immediately through stubs so callers can handle unsupported configuration.

## State and Persistence Behavior

The header owns no state. Registered regmaps represent shared SoC control registers whose values persist in hardware and are shared across unrelated drivers.

## Dependencies and Integration Points

It integrates device-tree consumers, MFD syscon provider registration, regmap clients, clock/reset/PHY/display/network drivers, and optional-property lookup behavior.

## Risks and Edge Cases

Callers must use `IS_ERR()` for required lookups and handle `NULL` from optional lookups. Shared syscon registers require masked updates to avoid clobbering other fields.

## Test Signals

Build tests with syscon enabled/disabled, phandle lookup tests, optional missing-property tests, and shared regmap update-bit tests.
