# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/therm/base.c

## Purpose
Implements the common Nouveau thermal subdevice: fan policy, temperature attributes, threshold programming hooks, lifecycle, and clockgating wrappers.

## Important APIs, Types, And Functions
Public entry points include `nvkm_therm_temp_get()`, `nvkm_therm_cstate()`, `nvkm_therm_fan_mode()`, `nvkm_therm_attr_get()`, `nvkm_therm_attr_set()`, `nvkm_therm_clkgate_enable()`, `nvkm_therm_clkgate_fini()`, `nvkm_therm_clkgate_init()`, `nvkm_therm_ctor()`, and `nvkm_therm_new_()`.

## Control Flow
Oneinit constructs sensor, external IC, and fan backends, switches to automatic fan mode, probes sensor availability, and reports clockgating. Init calls chip setup, restores suspend fan mode, starts threshold polling/interrupts, and initializes the fan. Fini disables chip hooks, fan alarms, and sensor alarms.

## State, Persistence, And Dependencies
State includes `therm->mode`, suspend mode, cstate fan target, BIOS sensor/fan thresholds, timer alarms, locks, fan backend, external IC pointer, and clockgating enablement from `NvPmEnableGating`.

## Integration Points
Depends on BIOS parsers, PMU fan-control detection, timer alarms, fan/sensor helpers, chip-specific `nvkm_therm_func` callbacks, and public therm attribute APIs.

## Risks
Automatic mode is rejected if PMU firmware owns fan control or no sensor exists. Attribute setters immediately reprogram alarms, so invalid BIOS or userspace values can alter safety behavior. Lock ordering between fan and alarm paths matters.

## Test Signals
Signals include fan mode transitions, temperature reads, threshold events, suspend/resume fan restoration, clockgating logs, and absence of deadlocks in alarm callbacks.
