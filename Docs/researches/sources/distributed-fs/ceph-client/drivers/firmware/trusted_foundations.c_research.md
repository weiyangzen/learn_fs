# sources/distributed-fs/ceph-client/drivers/firmware/trusted_foundations.c

## Purpose
`trusted_foundations.c` registers ARM firmware operations for NVIDIA/Tegra Trusted Foundations secure firmware. It provides secure monitor call wrappers for CPU boot address programming, idle low-power preparation, and optional secure L2X0 cache controller operations.

## Important APIs, types, and functions
The SMC primitive is `tf_generic_smc(type, arg1, arg2)`, which places arguments in ARM registers, preserves r4-r11, enables the `sec` architecture extension, and executes `smc #0`. `tf_set_cpu_boot_addr()` caches the boot address and sends `TF_SET_CPU_BOOT_ADDR_SMC`. `tf_prepare_idle()` maps Linux Trusted Foundations idle modes (`TF_PM_MODE_LP0`, `LP1`, `LP1_NO_MC_CLK`, `LP2`, `LP2_NOFLUSH_L2`) to firmware power commands and records `tf_idle_mode`.

When `CONFIG_CACHE_L2X0` is enabled, `tf_cache_write_sec()` handles secure writes to the L2X0 control register by issuing enable, re-enable, or disable SMCs. It derives the way mask from saved L2X0 auxiliary control and chooses `TF_CACHE_REENABLE` for LP2 resume. `tf_init_cache()` installs that hook into `outer_cache.write_sec`.

## Control flow and integration
`of_register_trusted_foundations()` looks for the `tlm,trusted-foundations` compatible node and requires `tlm,version-major` and `tlm,version-minor`; missing properties panic because firmware support was explicitly described but malformed. It then calls `register_trusted_foundations()`, which registers `trusted_foundations_ops` with the ARM firmware ops layer. `trusted_foundations_registered()` lets other code detect whether these ops are active.

## State and persistence behavior
The file maintains only two static variables: `tf_idle_mode`, used to adjust cache re-enable behavior, and `cpu_boot_addr`, reused by idle preparation SMCs. Actual CPU power, boot, and cache state is held by secure firmware and hardware.

## Dependencies and integration points
Dependencies include ARM firmware ops, ARM inline assembly/SMC support, DT, optional L2X0 cache support, and `linux/firmware/trusted_foundations.h`. It integrates with ARM CPU hotplug/suspend paths through `struct firmware_ops` and with outer-cache code through `outer_cache.write_sec`.

## Risks and test signals
Risks are architecture-specific inline assembly correctness, secure firmware availability, boot-address width/truncation on 32-bit paths, and panic-on-DT-malformation behavior. Cache operations are sensitive because incorrect way masks or idle mode tracking can corrupt L2 state. Test signals include DT registration, `firmware_ops` selection, CPU idle/suspend resume, secondary CPU boot, and L2X0 enable/disable paths on Trusted Foundations platforms.
