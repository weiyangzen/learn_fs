# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/psp.h

Purpose: PSP offload public definitions, capability gate, lifecycle declarations, and disabled-build stubs.

Important APIs, types, and functions: `struct mlx5e_psp_stats` mirrors PSP hardware/software stats for RX/TX packets, bytes, auth failures, frame errors, and drops. `struct mlx5e_psp` stores the kernel `psp_dev`, caps, flow-steering state, TX key count, and TX drop counter. `mlx5_is_psp_device()` checks generic PSP support plus AES-GCM-128 encrypt/decrypt firmware capabilities. Declarations cover PSP flow-table init/cleanup, register/unregister, and overall init/cleanup.

Control flow: callers use `mlx5_is_psp_device()` before allocating PSP resources. Netdev lifecycle invokes init/cleanup and register/unregister if PSP state exists. RX/TX table helpers are called as queues/flow steering become active.

State and persistence: the header describes state allocated in `psp.c` and attached to `priv->psp`. Atomic counters persist until cleanup.

Dependencies and integration points: depends on kernel PSP types and mlx5e private structures. Disabled stubs keep non-PSP builds compiling and returning no-op success.

Risks: the capability helper requires AES-GCM-128 support but AES-GCM-256 is optional and added later in registration. Callers must not assume `priv->psp` exists merely because the kernel config includes PSP.

Test signals: build with PSP enabled/disabled, probe devices with missing individual caps, verify no-op table functions without PSP, and check capability-driven registration versions.
