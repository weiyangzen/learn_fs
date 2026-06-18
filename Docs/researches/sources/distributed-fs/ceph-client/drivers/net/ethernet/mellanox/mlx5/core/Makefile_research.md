# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/Makefile

## Purpose

This Makefile maps mlx5 Kconfig symbols to the object files that compose `mlx5_core.o` and the separate `mlx5_dpll.o` module. It is the build manifest for the mlx5 core, Ethernet datapath, TC/offload stack, steering implementations, accelerators, subfunctions, diagnostics, and support libraries.

## Important Build Groups

- Base `mlx5_core-y`: core probe, command interface, debugfs, firmware, EQ, UAR, page allocation, health, MCG, CQ, allocation, port, MR/PD, transport objects, vport, SR-IOV, flow steering, IRQ, counters, rate limiting, lag, devlink, diagnostics, reset, QoS, timeout, ASO, write-combining, and support libraries.
- `CONFIG_MLX5_CORE_EN`: Ethernet channels, RX/TX, XDP, stats, selftests, reporters, params, XSK, devlink, PTP, QoS, traps, selected queues, and congestion event support.
- `CONFIG_MLX5_CLS_ACT`: TC classifier/action implementation, representor TC, tunneling offloads, post actions, meters, action stats, and individual TC action handlers.
- `CONFIG_MLX5_ESWITCH`: e-switch core/offloads, ECPF, RDMA hooks, legacy mode, vport tables, QoS, IPsec, and ACL helpers.
- `CONFIG_MLX5_SW_STEERING` and `CONFIG_MLX5_HW_STEERING`: separate software and hardware steering object sets.
- Optional accelerators: FPGA, MACsec, IPsec, TLS, PSP.
- Optional support: HWMON, MPFS, VXLAN, PTP clock, Hyper-V, IPoIB, bridge offloads, SF/SF manager, PCIe TPH.
- `obj-$(CONFIG_MLX5_DPLL)` builds `mlx5_dpll.o` from `dpll.o`.

## Control Flow

The file is declarative build control. Kbuild appends object files to `mlx5_core-y` or `mlx5_core-$(CONFIG_*)` depending on configuration symbols. Conditional `ifneq` blocks handle symbols where non-empty values include built-in or module states.

## State And Persistence Behavior

There is no runtime state. The persistent effect is the compiled module layout and which translation units are linked into `mlx5_core.o` or `mlx5_dpll.o`.

## Dependencies And Integration Points

The Makefile consumes symbols from `Kconfig`, adds `-I$(src)` include scope, and integrates many subdirectories: `en/`, `en/tc/`, `esw/`, `lag/`, `lib/`, `diag/`, `steering/sws/`, `steering/hws/`, `sf/`, `fpga/`, `ipoib/`, and `en_accel/`. Its organization mirrors feature ownership and is the final authority on which source files participate in each feature.

## Risks

- Object inclusion must match Kconfig dependencies; adding source files under the wrong symbol can cause unresolved references or dead feature code.
- `ifneq ($(CONFIG_*),)` includes objects for both `y` and `m`; this is deliberate but easy to misuse when code assumes built-in-only behavior.
- Large feature groups can hide accidental cross-feature dependencies because many objects are linked together whenever `MLX5_CORE_EN` or `MLX5_ESWITCH` is enabled.

## Test Signals

Build matrix coverage is the main signal: core-only, Ethernet-only, switchdev/e-switch, TC CT/sample, software steering only, hardware steering only, crypto accelerators, SF, FPGA, IPoIB, DPLL, and modular vs built-in combinations. Link errors and missing object references identify mismatches between Kconfig and Makefile.
