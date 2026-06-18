<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/mxm.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/mxm.c

### Purpose

Parser for MXM board information and SOR mapping. It handles explicit MXM SOR map tables and chipset-specific fallback maps for older MXM VBIOS layouts.

### Important APIs, types, and functions

`mxm_table()` locates BIT `x`; `mxm_sor_map()` maps MXM digital connector ids to SOR/link values using table data or hard-coded G84/G92/G94/G98 maps.

### Control flow

The parser requires BIT `x` version 1 with at least three bytes. If a SOR map pointer exists and has version 0x10/0x11, it indexes the table by connector id; otherwise it falls back by VBIOS chip version.

### State and persistence behavior

No persistent state. Returned SOR map bytes guide display routing decisions.

### Dependencies and integration points

Depends on BIT parsing and BIOS version fields. Display output code uses the map for MXM modules whose DCB data needs connector-to-SOR translation.

### Risks

Fallback maps are heuristic and chipset-limited. Missing or wrong maps can route display outputs to the wrong SOR/link.

### Test signals

Source read size: 137 lines, 3861 bytes. MXM board display tests, VBIOS fixtures with explicit SOR maps, fallback map validation on G84/G92/G94/G98, and warnings for unknown chips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/mxm.c -->
