
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gk20a.c

## Purpose
Implements Tegra GK20A GR support with external NVIDIA firmware loading and conversion of firmware-provided register lists into the common `gf100_gr_pack` format.

## Important APIs, types, and functions
- `gk20a_gr_av_to_init_()`, `gk20a_gr_av_to_init()`, `gk20a_gr_aiv_to_init()`, and `gk20a_gr_av_to_method()` convert firmware blobs into MMIO, context, bundle, and method packs.
- `gk20a_gr_wait_mem_scrubbing()` waits for FECS/GPCCS memory scrubbing to finish.
- `gk20a_gr_init()` is a Tegra-specific init path that loads `sw_nonctx`, waits for scrubbing/idle, programs MMU/zcull/FBP/exceptions, initializes ZBC, and starts context control.
- `gk20a_gr_load_sw()` and `gk20a_gr_load()` load required firmware blobs.
- `gk20a_gr_new()` constructs through `gf100_gr_new_()`.

## Control flow
Firmware loading pulls FECS/GPCCS inst/data and SW netlists from firmware files, converts them into runtime packs, and marks the engine as firmware-backed. Init clears SCC RAM, applies firmware-provided noncontext registers, waits for Falcon memory scrubbing, configures basic GR registers and exceptions, then starts the external context-control firmware through `gf100_gr_init_ctxctl()`.

## State and persistence
Firmware-derived packs are stored in `gr->sw_nonctx`, `gr->sw_ctx`, `gr->bundle`, and `gr->method` until destructor cleanup. FECS/GPCCS firmware blobs live in `gr->fecs` and `gr->gpccs`. Hardware state persists in GR registers and Falcon memory after init.

## Dependencies and integration points
Depends on firmware files under `nvidia/gk20a`, NVKM firmware blob loader, timer polling, GF100 common context-control code, and GK20A context data. It is compiled conditionally with Tegra firmware declarations.

## Risks
All required firmware files must be present; this path has no no-firmware fallback. Blob conversion trusts sizes to be multiples of expected structs. `gk20a_gr_av_to_method()` supports only 16 classes. Memory-scrubbing timeouts block init.

## Test signals
Signals include successful firmware load of all GK20A blobs, successful pack conversion, no FECS/GPCCS scrubbing timeout logs, valid `KEPLER_C` class operation, and stable Tegra graphics workloads.
