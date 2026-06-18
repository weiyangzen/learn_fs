# sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq-nforce2.c

## Purpose

This legacy x86 cpufreq driver changes front-side bus frequency on NVIDIA nForce2 chipsets by programming reverse-engineered PLL registers. It is explicitly risky hardware-control code and only supports CPU0.

## Important APIs, types, and functions

Global state includes `nforce2_dev`, module parameters `fid` and `min_fsb`, and computed `max_fsb`. Key helpers are `nforce2_calc_fsb()`, `nforce2_calc_pll()`, `nforce2_write_pll()`, `nforce2_fsb_read()`, `nforce2_set_fsb()`, `nforce2_get()`, `nforce2_target()`, `nforce2_verify()`, `nforce2_cpu_init()`, and `nforce2_detect_chipset()`.

## Control flow, state, and persistence

Module init finds the nForce2 PCI device and registers a cpufreq driver. CPU init reads current FSB, derives CPU multiplier from `cpu_khz` if `fid` was not supplied, reads boot FSB as the maximum, derives a safe minimum when absent, and sets policy min/max. Target converts requested CPU kHz to FSB, emits transition notifications, and calls `nforce2_set_fsb()`. The setter initializes PLL registers if needed, enables writes, walks the FSB one MHz at a time toward the target, writes calculated PLL values to all 64 PLL registers, and finally writes an address value. Hardware PLL state persists until reboot or another writer changes it.

## Dependencies and integration points

The driver depends on PCI config-space access to NVIDIA nForce2 devices, `cpu_khz`, cpufreq transition notifications, and module parameters for multiplier/minimum FSB tuning. It has no OPP, regulator, ACPI, or clock-framework integration.

## Risks and test signals

The file itself warns that FSB changing may crash or cause data loss. Risks include bad reverse-engineered PLL calculations, incorrect CPU multiplier inference, unsafe FSB bounds, ignored target failure in `nforce2_target()` transition completion, lack of IRQ disabling despite comments, and platform instability while stepping the bus. Test only on expendable supported hardware: verify detected PCI revision, current and boot FSB reads, conservative min/max policy, small incremental transitions, and system stability under disk and memory load.
