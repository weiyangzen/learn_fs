<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/qcom/cpr.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/qcom/cpr.c

## Purpose
Qualcomm Core Power Reduction (CPR) generic PM domain driver for QCS404-style RB-CPR hardware. It exposes the CPR loop as a genpd provider, reads NVMEM fuse data, derives voltage/frequency corners from OPP data, and continuously trims the `vdd-apc` regulator around CPU OPP requests.

## Important APIs, Types, And Functions
- `struct cpr_drv` owns the genpd, MMIO base, regulator, CPU clock, TCSR regmap, IRQ state, fuse corners, runtime corners, current corner, and debugfs dentry.
- `struct cpr_desc`, `struct cpr_fuse`, `struct fuse_corner`, and `struct corner` encode SoC CPR timing, fuse-derived ceilings/floors/quotients, and per-OPP runtime voltage state.
- Genpd entry points are `cpr_power_on()`, `cpr_power_off()`, `cpr_set_performance_state()`, and `cpr_pd_attach_dev()`.
- Hardware helpers include `cpr_config()`, `cpr_ctl_enable()`, `cpr_ctl_disable()`, `cpr_corner_restore()`, `cpr_scale_voltage()`, and `cpr_irq_handler()`.
- Fuse/OPP setup flows through `cpr_get_fuses()`, `cpr_populate_ring_osc_idx()`, `cpr_fuse_corner_init()`, `cpr_corner_init()`, and `cpr_find_initial_corner()`.

## Control Flow
`cpr_probe()` matches `qcom,qcs404-cpr`, maps CPR registers, resolves the `acc-syscon` TCSR regmap, obtains the `vdd-apc` regulator, reads CPR fuse revision and per-corner NVMEM cells, initializes fuse corner voltages/quotients, requests a threaded IRQ, initializes a powered-off genpd, registers it as a simple provider, and creates debugfs. Device attachment is deferred until a CPU attaches to the domain because OPP-derived frequencies are only available then. `cpr_pd_attach_dev()` captures the CPU clock, counts domain OPPs, builds virtual corners, configures CPR registers, finds the boot-time corner, and enables ACC register programming. Runtime OPP changes call `cpr_set_performance_state()`: it decides UP/DOWN/NO_CHANGE, disables the CPR loop while changing the regulator, applies ACC settings before or after voltage changes depending on direction, restores per-corner RB-CPR registers, and re-enables the loop. CPR IRQs read status, handle UP/DOWN/MIN/MAX/MID priority, adjust voltage by regulator linear steps within min/max limits, ack/nack hardware, and save corner register state.

## State And Persistence Behavior
State is in memory plus hardware registers. `drv->corner` and `corner->last_uV` track the active OPP voltage after hardware-driven trimming. Each corner stores saved CPR control and interrupt registers so switching corners preserves loop state. Fuse data and OPP tables are read during probe/attach but not persisted. Debugfs exposes live CPR register and voltage state under `qcom_cpr/debug_info`.

## Dependencies And Integration Points
Depends on generic PM domains, OPP required-opps, NVMEM cells named `cpr_ring_oscN`, `cpr_init_voltageN`, `cpr_quotientN`, `cpr_quotient_offsetN`, the `cpr_fuse_revision` cell, a `vdd-apc` regulator with linear steps, a CPU clock, platform IRQ, MMIO resource, and the TCSR syscon referenced by `acc-syscon`. Integrates with cpufreq/OPP via genpd performance states and with ACC/TCSR via regmap sequences.

## Risks
Fuse parsing and voltage interpolation are sensitive to DT/NVMEM naming, OPP fuse-level annotations, regulator step size, and required-opps links to CPU OPPs. `cpr_debug_info_show()` assumes `drv->corner` and `corner->fuse_corner` are valid, so debugfs reads before CPU attach would be risky if reachable. IRQ handling must not run while loop-disabled unless hardware is actually quiet; otherwise it returns `IRQ_NONE` after logging. Voltage changes are mutex-protected, but the hardware loop and IRQ timing make ordering of ack/nack and saved registers important.

## Test Signals
Useful signals are successful probe and provider registration, `driver initialized with N OPPs`, valid debugfs output, regulator voltage changes matching OPP transitions, CPR IRQ up/down activity without timeout or unsupported voltage errors, and DT validation for required NVMEM/OPP/regulator/syscon resources. Compile coverage should include `qcom,qcs404-cpr` and genpd performance state paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/qcom/cpr.c -->
