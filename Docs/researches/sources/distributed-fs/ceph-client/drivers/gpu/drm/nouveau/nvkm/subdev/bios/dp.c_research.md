<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/dp.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/dp.c

### Purpose

Parser for DisplayPort output and AUX/link policy tables nested under DCB/display data.

### Important APIs, types, and functions

`nvbios_dp_table()`, `nvbios_dpout_match()`, output parse helpers, and DP data accessors decode DP flags, link settings, and condition data used by display init scripts.

### Control flow

The code derives DP table locations from DCB/output metadata, validates header/version fields, scans records by output type and OR/link mask, and fills `struct nvbios_dpout` for the matched output.

### State and persistence behavior

No persistent state. Parsed flags and link capabilities are returned to callers while the ROM image remains immutable.

### Dependencies and integration points

Depends on DCB output parsing, connector data, and generic BIOS access. `init_generic_condition()` uses `nvbios_dpout_match()` for SPPLL and eDP-related conditions.

### Risks

Incorrect matching can choose the wrong PLL or AUX behavior for a DP output. Version/length mismatches must fail cleanly to avoid using garbage flags.

### Test signals

Source read size: 232 lines, 6321 bytes. DP/eDP link training tests, init-script condition tracing, SPPLL selection tests, and VBIOS corpus comparison for DP output records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/dp.c -->
