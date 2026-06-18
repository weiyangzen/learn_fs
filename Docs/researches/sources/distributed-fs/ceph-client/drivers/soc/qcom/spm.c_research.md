# sources/distributed-fs/ceph-client/drivers/soc/qcom/spm.c

## Purpose

`spm.c` programs Qualcomm SAW/SPM low-power sequencers for supported CPU and L2 power controllers. It writes SoC-specific micro-sequences and control registers, exposes `spm_set_low_power_mode()` for idle code, and optionally registers a CPU-affine voltage regulator for SPM v1.1.

## Important APIs, Types, and Functions

`enum spm_reg` indexes logical registers whose physical offsets vary by hardware version. `struct spm_reg_data` stores register offsets, configuration words, PMIC/AVS fields, sequencer bytes, sleep-mode start indexes, and optional regulator data. `struct spm_driver_data` stores MMIO base and selected table. Important functions are `spm_register_write()`, `spm_register_write_sync()`, `spm_set_low_power_mode()`, `smp_set_vdd_v1_1()`, `spm_register_regulator()`, `spm_get_cpu()`, and `spm_dev_probe()`.

## Control Flow

Probe selects match data from compatible strings, maps the resource, copies the sequence table into `SPM_REG_SEQ_ENTRY`, then writes AVS, CFG, delay, PMIC, and default standby-mode control registers. If regulator support is enabled and the table supplies `set_vdd`, the driver finds the CPU whose DT node references this SAW node, initializes voltage selector state, executes the first voltage write on that CPU, and registers a regulator.

## State and Persistence Behavior

SPM hardware retains the programmed sequencer and control register state until reset or later writes. Driver state is per-device and devm-managed. Regulator state tracks `volt_sel` in memory, but actual voltage programming is stored in SAW/PMIC-related registers. `spm_set_low_power_mode()` mutates the sequencer start index in SPM control state.

## Dependencies and Integration Points

The file depends on platform MMIO, OF match tables, `soc/qcom/spm.h` sleep modes, SMP cross-calls, regulator framework, bitfield helpers, and relaxed I/O. It is registered by `arch_initcall()` so idle and cpufreq-related users can find programmed SPM state early.

## Risks and Edge Cases

Register offset tables contain zero for unsupported registers, so callers must avoid reads of absent registers; `spm_register_read()` itself does not guard missing offsets. Sequence copying always copies 64 bytes divided as words; sequence table alignment and endian assumptions matter. Voltage writes are CPU-affine and can fail if the CPU mapping is missing or offline. `smp_set_vdd_v1_1()` polls for the target level for only 200 microseconds and then re-enables AVS even on timeout. Initial-voltage selector calculation has legacy and linear-range paths that must stay consistent.

## Test Signals

Build and boot on each compatible family. Verify programmed sequence bytes, default standby selection, SPC selection through idle code, regulator registration only for v1.1 CPU SAW nodes, voltage transitions on the target CPU, AVS disable/re-enable behavior, and timeout logging. Fault tests should cover missing `qcom,saw` phandles, invalid compatible data, absent sequence offset, and regulator disabled builds.
