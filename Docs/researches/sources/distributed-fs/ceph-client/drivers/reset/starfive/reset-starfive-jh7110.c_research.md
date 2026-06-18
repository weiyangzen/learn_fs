# sources/distributed-fs/ceph-client/drivers/reset/starfive/reset-starfive-jh7110.c

Purpose: StarFive JH7110 auxiliary reset front-end for sys, aon, stg, isp, and vout reset domains.

Important APIs/types/functions: `jh7110_reset_info` provides per-domain reset count and assert/status offsets. `jh7110_reset_probe()` converts the auxiliary device to `jh71x0_reset_adev`, validates base/info, and calls `reset_starfive_jh71x0_register()`.

Control flow: JH7110 clock/sys controller creates auxiliary devices named `clk_starfive_jh7110_sys.rst-*`; each binds to one reset domain and registers common JH71x0 ops.

State and persistence: domain info tables are static; hardware registers hold state.

Dependencies and integration: auxiliary bus, StarFive clock driver auxiliary data, common JH71x0 reset helper, JH7110 dt-bindings.

Risks and test signals: OF node passed from parent, so child device-tree matching depends on clock-controller topology. Test all five auxiliary IDs, reset counts, offset correctness, and parent base absence.
