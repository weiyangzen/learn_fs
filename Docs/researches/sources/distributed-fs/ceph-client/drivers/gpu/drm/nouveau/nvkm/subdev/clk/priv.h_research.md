# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/priv.h

## Purpose
Defines the private NVKM clock function-table contract and constructor prototypes shared by all clock subdevice implementations.

## Important APIs, types, and functions
Defines `struct nvkm_clk_func` with optional `init/fini/read/calc/prog/tidy`, static pstate support, pstate count, and flexible domain array. Declares `nvkm_clk_ctor()`, `nvkm_clk_new_()`, and legacy NV04 PLL callbacks.

## Control flow
No runtime flow occurs in the header. The function table determines the control flow used by `clk/base.c` during subdevice init, pstate programming, and teardown.

## State and persistence
No state is stored here; the table describes per-generation persistent behavior and static pstate ownership.

## Dependencies and integration points
Includes public `subdev/clk.h` and is included by all implementation files in this directory.

## Risks
The flexible `domains[]` member means function-table definitions must terminate with `nv_clk_src_max`. Missing hooks such as `read` on a domain-bearing implementation would break init.

## Test signals
Compile coverage across every clock generation and boot-time domain enumeration without overrunning the table.
