# sources/distributed-fs/lustre-release/lnet/klnds/o2iblnd/o2iblnd_modparams.c

## Purpose
`o2iblnd_modparams.c` defines o2iblnd module parameters, exposes them through `module_param()`, validates selected inputs, initializes the global tunable pointer table, computes default per-NI o2iblnd tunables, and normalizes LNet common tunables for peer credits, router credits, timeouts, FMR/FastReg pools, connection count, and RoCE ToS.

## Important APIs, types, and functions
- Module parameters include `service`, `cksum`, `timeout`, `nscheds`, `conns_per_peer`, `ntx`, `credits`, `peer_credits`, `peer_credits_hiw`, `peer_buffer_credits`, `peer_timeout`, `ipif_name`, `retry_count`, `rnr_retry_count`, `keepalive`, `ib_mtu`, `concurrent_sends`, `use_fastreg_gaps`, `map_on_demand`, `fmr_pool_size`, `fmr_flush_trigger`, `fmr_cache`, `dev_failover`, `require_privileged_port`, `use_privileged_port`, `wrq_sge`, and `tos`.
- `struct kib_tunables kiblnd_tunables` stores pointers to mutable module parameter storage consumed by the rest of the driver.
- `struct lnet_ioctl_config_o2iblnd_tunables kib_default_tunables` stores the exported default tunables snapshot.
- `param_set_tos()` validates ToS as `-1` or an 8-bit value.
- `kiblnd_msg_queue_size()` returns the v1 fixed queue depth, the NI peer TX credits, or module-level peer credits.
- `kiblnd_tunables_setup()` fills and clamps per-NI tunables and common LNet tunables.
- `kiblnd_tunables_init()` initializes the default tunable snapshot during module init.

## Control flow
At module load, static parameter defaults are registered with sysfs/module infrastructure. `ko2iblnd_init()` calls `kiblnd_tunables_init()` to seed `kib_default_tunables`. During NI startup, `kiblnd_tunables_setup()` validates IB MTU, fills unset LNet common tunables from module parameters, clamps peer credits between o2iblnd minimum/maximum and max TX credits, forces obsolete `map_on_demand` to enabled, chooses peer-credit high-water values, bounds `concurrent_sends`, fills FMR/FastReg and TX pool sizing defaults, ensures at least one connection per peer, copies ToS if unset, and records the effective timeout.

## State and persistence behavior
The module parameters are kernel module runtime state exposed through module parameter permissions. Many sizing and policy parameters are read-only after load (`0444`), while operational values such as checksum, timeout, retry counts, keepalive, and privileged port flags can be changed according to their declared permissions. Per-NI tunables get a copy or normalized value at setup time; later module parameter changes do not automatically rewrite already-initialized NI state unless the driver explicitly re-runs setup.

## Dependencies and integration points
The file depends on `o2iblnd.h` for constants, tunable structs, MTU conversion helpers, LNet common tunable types, and logging. Its outputs feed `o2iblnd.c` startup, Netlink default export, queue-depth/QP sizing, FMR/FastReg pool allocation, scheduler thread sizing, connection timeout math, CM retry parameters, keepalive decisions, and send WR SGE limits in `o2iblnd_cb.c`.

## Risks and edge cases
- Invalid `ib_mtu` is rejected only during tunable setup, so configuration failures surface at NI startup.
- `map_on_demand` is obsolete but still accepted and forced to 1; stale configs may appear accepted while behavior is fixed.
- `peer_credits_hiw` and `concurrent_sends` are auto-clamped; very low/high user values may silently change with only warnings.
- `fmr_pool_size < ntx / 4` is not rejected here but later in pool initialization.
- `wrq_sge` and pool sizes strongly influence QP and memory pressure.
- `tos` accepts `-1..255`; other values return `-ERANGE`.

## Test signals
Tests should cover module parameter parsing, ToS validation, invalid MTU rejection, default setup when common tunables are `-1`, clamping of peer credits and concurrent sends, forced `map_on_demand`, `conns_per_peer` zero fallback, FMR pool size interactions with `ntx`, and Netlink/default tunable export matching `kib_default_tunables`.
