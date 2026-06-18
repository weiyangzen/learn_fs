# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mc/gk20a.c

## Purpose
Defines the Tegra GK20A MC backend by reusing GK104 interrupt/reset maps with NV50 init.

## Important APIs, Types, and Functions
The key symbols are `gk20a_mc` and `gk20a_mc_new`.

## Control Flow, State, and Persistence
All runtime behavior is delegated: init to `nv50_mc_init`, interrupts to `gt215_mc_intr` and `gk104_mc_intrs`, device control to `nv04_mc_device`, and reset mapping to `gk104_mc_reset`.

## Dependencies and Integration Points
Depends on GK104 shared tables and Tegra device routing.

## Risks and Test Signals
Risks are assuming GK104 desktop masks match GK20A SoC routing and lacking `unk260`. Test Tegra GPU interrupts, FIFO reset, PMU/top interactions, suspend/resume, and SoC boot logs.
