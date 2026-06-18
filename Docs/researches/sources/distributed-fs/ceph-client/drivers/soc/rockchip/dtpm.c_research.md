# sources/distributed-fs/ceph-client/drivers/soc/rockchip/dtpm.c

## Purpose

`dtpm.c` registers a Rockchip RK3399 Dynamic Thermal Power Management hierarchy. It describes virtual package nodes and DT-backed CPU/GPU power nodes for power capping.

## Important APIs, Types, and Functions

`rk3399_hierarchy[]` is a `struct dtpm_node` tree with root `rk3399`, child `package`, CPU nodes `/cpus/cpu@0` through `/cpus/cpu@101`, and GPU node `/gpu@ff9a0000`. `rockchip_dtpm_match_table` binds the hierarchy to `rockchip,rk3399`. Module init/exit call `dtpm_create_hierarchy()` and `dtpm_destroy_hierarchy()`.

## Control Flow

On module load, DTPM scans the match table against the running platform and creates the hierarchy if RK3399 matches. On unload, it destroys the hierarchy.

## State and Persistence Behavior

Hierarchy nodes are static `__initdata` descriptors used to create runtime DTPM objects. Runtime state belongs to the DTPM core and is removed at module exit.

## Dependencies and Integration Points

It depends on the DTPM framework, OF matching, and availability of panfrost and cpufreq-dt providers, noted by `MODULE_SOFTDEP("pre: panfrost cpufreq-dt")`.

## Risks and Edge Cases

Hardcoded DT paths must match board DTs. The author string appears to miss a closing `>` in the module metadata. DTPM creation failure is returned directly from module init. The `depends on DTPM && m` Kconfig shape makes this module-only.

## Test Signals

Load/unload on RK3399 with cpufreq and panfrost present, inspect DTPM hierarchy, test missing GPU/CPU provider behavior, and run module metadata checks.
