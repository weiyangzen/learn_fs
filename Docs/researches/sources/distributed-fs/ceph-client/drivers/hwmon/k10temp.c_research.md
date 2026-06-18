# sources/distributed-fs/ceph-client/drivers/hwmon/k10temp.c

## Purpose
`k10temp.c` is the AMD Family 10h and newer CPU temperature hwmon driver. It exposes Tctl, optional Tdie, and optional Zen CCD temperatures through PCI device matches on AMD/Hygon northbridge/data-fabric function 3 devices.

## Important APIs, types, and functions
The driver uses PCI probing, CPU feature/model data, AMD SMN access (`amd_smn_read`), hwmon `with_info`, and CPUID helpers. `struct k10temp_data` stores the PCI device, register read callbacks, offset metadata, channel visibility bitmask, Zen CCD offset, and negative-temperature policy. `get_raw_temp()` decodes the reported temperature register. `k10temp_read_temp()` provides input/max/crit/hyst values. `k10temp_is_visible()` hides channels and critical attributes depending on CPU family, HTC support, and discovered CCD validity. `has_erratum_319()` blocks unreliable Family 10h socket cases unless `force=1`.

## Control flow
Probe checks erratum 319, allocates state, always enables Tctl, selects PCI-indexed or SMN temperature register readers based on CPU family/model, discovers supported CCDs for known Zen model ranges, applies model-name-based Tctl offsets to expose Tdie on selected Ryzen/Threadripper CPUs, and registers hwmon. Reads dispatch by channel: Tctl and Tdie come from the current temperature register, CCD channels read SMN per-CCD registers, and critical/hysteresis values come from hardware thermal control when available.

## State and persistence
The driver does not program thresholds or persistent settings. State is runtime-only: callback selection, offset values, CCD visibility, and whether negative values should be displayed for AMD 3255 industrial processors. Hardware registers are read on demand.

## Dependencies and integration points
It integrates with the PCI subsystem, x86 CPU identification, AMD northbridge node numbering, AMD SMN reads, and the hwmon ABI. It also uses PCI config space for older families and HTC capability reporting.

## Risks
Temperature formulas for Zen CCD registers are based on reverse-engineered sources rather than public datasheets. Model-range tables must be maintained for new AMD families. Erratum handling protects known unreliable sensors, but `force` can expose bad data. CCD discovery guards against `0xffffffff` responses, but platform firmware or SMN access failures can still hide valid sensors.

## Test signals
Test probe on representative Family 10h, 15h, 16h, 17h, 19h, and 1Ah systems; erratum 319 blocked and forced paths; Tdie offset models; HTC critical visibility; CCD valid/invalid SMN reads; Hygon PCI IDs; negative-temperature behavior for 3255; and sysfs label visibility only on Zen.
