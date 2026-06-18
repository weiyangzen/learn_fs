
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gm20b.c

## Purpose
Implements Tegra GM20B Maxwell B GR support with FECS secure loading, non-secure GPCCS blob loading, Tegra-specific bootloader descriptors, GPC MMU programming, and GK20A-style firmware netlist initialization.

## Important APIs, types, and functions
- `gm20b_gr_acr_bld_write()` and `gm20b_gr_acr_bld_patch()` handle Falcon bootloader descriptors with high address fields.
- `gm20b_gr_fecs_acr` describes FECS ACR loading.
- `gm20b_gr_init_gpc_mmu()` optionally bypasses secure-boot MMU checks when no ACR exists, then programs GM20B MMU registers.
- `gm20b_gr_set_hww_esr_report_mask()` writes Maxwell warning masks.
- `gm20b_gr_load()` loads signed FECS, raw GPCCS inst/data, and SW packs.
- `gm20b_gr_new()` constructs through `gf100_gr_new_()`.

## Control flow
Firmware load first secures FECS through ACR, loads GPCCS directly, marks firmware mode, then loads SW netlists. Init uses `gk20a_gr_init()`, which is tailored for Tegra firmware-provided noncontext registers and memory-scrubbing waits, while GM20B hooks provide MMU and warning-mask differences.

## State and persistence
Runtime state includes firmware blobs, SW packs, ACR bootloader descriptors, and common `gf100_gr` context/ZBC/topology fields. Hardware state includes optional MMU bypass register `0x100ce4` and GR MMU registers.

## Dependencies and integration points
Depends on ACR, firmware loader, GK20A init/SW conversion, GM200 topology/tile helpers, GM20B context data, and Tegra-specific firmware files.

## Risks
The non-secure boot bypass path warns that failure should lead to later errors. FECS and GPCCS are loaded through different mechanisms. Firmware availability is mandatory on Tegra. Address packing in bootloader descriptors is easy to get wrong.

## Test signals
Signals include FECS ACR load success, GPCCS firmware load success, absence of secure-boot bypass warnings on secure systems, no memory-scrubbing timeout, and working `MAXWELL_B` classes on Tegra 210.
