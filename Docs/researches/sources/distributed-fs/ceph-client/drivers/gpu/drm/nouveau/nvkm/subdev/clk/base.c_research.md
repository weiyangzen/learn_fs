# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/base.c

## Purpose
Implements the common NVKM clock subdevice policy: BIOS/static pstate discovery, cstate selection, voltage/fan sequencing, power-source and thermal reclock triggers, and the subdevice init/fini/dtor glue used by all Nouveau clock families.

## Important APIs, types, and functions
Key entry points are `nvkm_clk_ctor()`, `nvkm_clk_new_()`, `nvkm_clk_read()`, `nvkm_clk_ustate()`, `nvkm_clk_astate()`, `nvkm_clk_tstate()`, `nvkm_clk_dstate()`, and `nvkm_clk_pwrsrc()`. Internals include `nvkm_pstate_new()`, `nvkm_cstate_new()`, `nvkm_cstate_prog()`, `nvkm_pstate_work()`, and BIOS boost/perf/cstep parsing through `nvbios_*` helpers.

## Control flow
Construction builds the pstate list from a family static table or VBIOS performance tables, applies `NvClkMode*` options, and records VP-state base/boost caps. Init snapshots boot clocks into `bstate`, calls family `init` when present, otherwise chooses the highest application state and schedules a synchronous pstate calculation. Pstate work merges user AC/DC state, automatic state, thermal lower bound, and power-source selection, then programs PCIe link, RAM timing, fan, voltage, and family `calc/prog/tidy` hooks.

## State and persistence
Persistent runtime state lives in `struct nvkm_clk`: pstate/cstate lists, boot-state snapshot, current pstate, user/auto/thermal state requests, temperature, boost limits, waitqueue/work item, and family function pointers. Hardware persistence is delegated to family hooks and voltage/thermal/PCIe/fb subdevices.

## Dependencies and integration points
Depends on BIOS perf/cstep/boost/vpstate tables, `nvkm_volt`, `nvkm_therm`, `nvkm_fb` RAM callbacks, PCIe link management, power supply state, and the `nvkm_subdev` lifecycle. It is the integration point for sysfs/debug/user reclock requests and thermal/power policy.

## Risks
The state resolver is global policy for reclocking. Bad voltage mapping, cstate validity, workqueue waiting, or pstate index conversion can select unsafe clocks or leave callers waiting. The destructor intentionally skips freeing static pstate arrays, so mixed static/dynamic state ownership must remain clear.

## Test signals
Useful signals are `nvkm_trace()` pstate decisions, pstate info debug lines, voltage/fan error logs, suspend/resume reclock behavior, `NvClkMode*` option parsing, and stress that changes AC/DC power, temperature, and user requested states while memory reclocking is available.
