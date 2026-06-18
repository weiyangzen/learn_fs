# sources/distributed-fs/ceph-client/drivers/clk/mmp/pwr-island.c

Purpose: generic PM domain implementation for MMP APMU power islands.

Important APIs/functions: `mmp_pm_domain_register` creates a `generic_pm_domain` with `mmp_pm_domain_power_on` and `mmp_pm_domain_power_off` callbacks.

Control flow: power-on sets configured power bits, disables isolation via bit `0x100`, optionally toggles reset and clock-enable bits for blocks that need post-power reset sequencing, and restores the post-power-on value. Power-off clears power and isolation bits unless `MMP_PM_DOMAIN_NO_DISABLE` is set.

State and persistence: each allocated `mmp_pm_domain` stores MMIO address, masks, flags, lock, and embedded `generic_pm_domain`. Hardware register bits hold actual island state.

Dependencies and integration: used by `clk-of-mmp2.c` to expose GPU/audio/camera domains through genpd. Depends on PM domain core, MMIO, and optional spinlocks shared with clock gates.

Risks: isolation bit `0x100` is hard-coded for all users. Incorrect masks can reset or gate unrelated block bits. No unregister path or devm ownership exists for early-init allocations.

Test signals: genpd provider registration, runtime PM of GPU/audio/camera devices, power-on reset sequence validation on hardware, and suspend/resume checks.
