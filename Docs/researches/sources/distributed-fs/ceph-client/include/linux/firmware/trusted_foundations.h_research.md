# sources/distributed-fs/ceph-client/include/linux/firmware/trusted_foundations.h

## Purpose
This header provides the platform contract for NVIDIA Trusted Foundations secure monitor support on older ARM/Tegra consumer devices. It exists because those systems require proprietary SMC calls for CPU reset vectors and power management rather than PSCI.

## APIs, types, and control flow
`struct trusted_foundations_platform_data` carries secure monitor version fields. With `CONFIG_TRUSTED_FOUNDATIONS`, the header declares registration, device-tree registration, and status queries. Without support, `register_trusted_foundations()` deliberately degrades the system: it logs errors, optionally installs a dummy L2X0 secure write hook, disables SMP by setting `setup_max_cpus = 0`, and enables idle polling. `of_register_trusted_foundations()` detects the compatible node and triggers the degraded path when support is missing.

## State and dependencies
State is global secure-monitor registration and platform version information. Dependencies include Open Firmware, CPU/SMP control, printk, L2X0 outer cache hooks, and idle polling.

## Integration, risks, and tests
This header affects early boot, secondary CPU bring-up, cache controller access, and CPU PM. Risks are silent feature loss when support is disabled, nonstandard SMC ABI assumptions, and boot failures if device tree requires TF but the kernel cannot implement it. Tests include DT-compatible detection, disabled-config degradation logs, SMP disabled behavior, L2X0 fallback hook installation, and registered-status checks on supported builds.
