# sources/distributed-fs/ceph-client/drivers/hwmon/k8temp.c

## Purpose
`k8temp.c` exposes AMD K8 core temperature sensors through the AMD K8 northbridge miscellaneous PCI function. It supports up to four temperature channels representing core and sensor-place selections.

## Important APIs, types, and functions
The driver uses PCI config-space access, CPUID data, mutex locking, and `devm_hwmon_device_register_with_info()`. `struct k8temp_data` stores an update lock, detected selectable sensor bits, whether core selection is inverted, and a model-specific temperature offset. `k8temp_is_visible()` hides absent core/place channels. `k8temp_read()` selects the requested core/place in `REG_TEMP`, reads the same register as a dword, and converts the value with `TEMP_FROM_REG()`. `is_rev_g_desktop()` implements AMD RevG desktop offset detection.

## Control flow
Probe rejects unsupported early revisions, sets `swap_core_select` and warns for RevF/RevG erratum-sensitive models, applies a 21 C desktop offset for RevG desktop CPUs, tests whether core and place selection bits can be toggled, validates that secondary sensors are plausible, initializes the mutex, and registers four possible hwmon temp channels. Runtime reads serialize selector writes and raw reads under `update_lock`.

## State and persistence
There is no persistent configuration beyond transient selector writes to PCI config register `0xe4`. Runtime state records which dimensions are selectable and whether a temperature offset applies. No cached temperature values are kept.

## Dependencies and integration points
The driver depends on AMD K8 PCI IDs, boot CPU model/stepping, CPUID brand-index decoding, and the hwmon core. It is specific to x86 K8-era hardware and uses PCI config accesses directly.

## Risks
The hardware selector register is shared state; serialized driver access avoids internal races but not external firmware or tooling changes. Erratum #141 means readouts may be wrong on later models even when exposed. Presence detection treats zero raw temperatures as invalid because -49 C is unlikely, which could theoretically hide a valid extreme reading.

## Test signals
Test older unsupported revisions, RevF/RevG warning and core-select inversion, RevG desktop offset, channel visibility when place/core bits are absent, repeated reads for all channels, and comparison against known-good thermal telemetry on real K8 hardware.
