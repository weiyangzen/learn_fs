# sources/distributed-fs/ceph-client/drivers/hwmon/peci/cputemp.c

Purpose: auxiliary-bus hwmon client exposing Intel CPU package, DTS, control/throttle/Tjmax, and per-core temperatures over PECI. It supports several Xeon generations through per-generation resolved-core register locations and PECI revision expectations.

Important APIs/types/functions: `struct peci_cputemp` stores the PECI device, hwmon name, generation info, cached target/die/DTS/core temperatures, core labels, and core mask. `struct cpu_info` carries the resolved-core register, minimum PECI revision, and fixed-point conversion function. `update_temp_target()`, `get_die_temp()`, `get_dts()`, and `get_core_temp()` implement sensor reads. `init_core_mask()` reads platform-specific PCI/endpoint PCI registers to discover active cores. `cputemp_read()`, `cputemp_read_string()`, and `cputemp_is_visible()` implement `hwmon_ops`.

Control flow: the auxiliary driver matches names such as `peci_cpu.cputemp.hsx`, allocates private state, warns on unexpectedly low PECI revision, optionally resolves core mask and labels, then registers a hwmon device with static channel descriptors. Reads dispatch by channel: die uses `peci_temp_read()` plus Tjmax, DTS uses `PECI_PCS_THERMAL_MARGIN` plus Tcontrol, target channels read `PECI_PCS_TEMP_TARGET`, and core channels read `PECI_PCS_MODULE_TEMP` for each visible core. Per-sensor cache helpers prevent repeated PECI transactions within one second.

State and persistence: all values are runtime caches in `peci_cputemp`. `core_mask` determines which of the 64 possible core channels are visible. Target temperature values share one cache state; die, DTS, and each core have separate cache states. No values are persisted outside device lifetime.

Dependencies and integration: depends on auxiliary bus, PECI device APIs, PECI CPU namespace, hwmon info API, bitmaps, bitfields, jiffies, and unit constants. It imports namespace `PECI_CPU` and is instantiated by the PECI CPU layer rather than by direct I2C/platform discovery.

Risks: incorrect generation data can hide cores or read the wrong PCI/endpoint config register. Failure to resolve cores is non-fatal, so package sensors may work while per-core channels are absent. DTS error codes are filtered by range; hardware or firmware changes in encoded errors would need review. Visibility exposes a large static descriptor with dynamic hiding, so channel indexes must stay aligned with labels.

Test signals: auxiliary matching for all listed generations, hwmon labels `Die`, `DTS`, `Tcontrol`, `Tthrottle`, `Tjmax`, per-core label creation, package and core temperature reads, cache behavior, low PECI revision warning, and operation when core resolution fails.
