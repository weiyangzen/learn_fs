# sources/distributed-fs/ceph-client/include/soc/tegra/common.h

## Purpose

`common.h` provides small common helpers for Tegra SoC detection and device OPP table setup.

## Important APIs, Types, and Functions

`struct tegra_core_opp_params` currently contains `init_state`. With `CONFIG_ARCH_TEGRA`, the header declares `soc_is_tegra()` and `devm_tegra_core_dev_init_opp_table()`. Without it, stubs return `false` and `-ENODEV`. `devm_tegra_core_dev_init_opp_table_common()` sets `init_state = true`, calls the main initializer, and treats `-ENODEV` as success.

## Control Flow

The wrapper lets shared drivers unconditionally request Tegra OPP setup. Missing Tegra support is normalized to success; other errors propagate.

## State and Persistence

The header has no persistent state. Real OPP state is device-managed by the implementation behind `devm_tegra_core_dev_init_opp_table()`.

## Dependencies and Integration Points

It includes Linux errno/types and forward-declares `struct device`. It integrates Tegra SoC code with the Linux OPP framework.

## Risks

The intentional `-ENODEV` suppression can hide absence of Tegra support if a caller expected mandatory OPP setup. Other errors must still be checked.

## Test Signals

Cover enabled and disabled `CONFIG_ARCH_TEGRA`, OPP success, missing support, malformed OPP tables, and callers that rely on initialized OPP state.
