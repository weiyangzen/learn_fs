<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/disp.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/disp.c

### Purpose

Parser for display script/table pointers from the BIT `U`/display table family. It exposes output-specific init script locations and display table metadata to the display engine.

### Important APIs, types, and functions

`nvbios_disp_table()`, entry accessors, and parsing helpers decode display table headers and script pointers into `struct nvbios_disp*` data declared in `disp.h`.

### Control flow

The parser locates the display table through the relevant BIT entry, validates supported versions, calculates entry offsets from header/count/length fields, and returns script/data offsets for callers that execute display init sequences.

### State and persistence behavior

No mutable state. Offsets and decoded records are transient views into `bios->data`.

### Dependencies and integration points

Depends on BIT directory parsing and generic VBIOS reads. It integrates with display output init, SOR/DAC programming, and `bios/init.c` script execution.

### Risks

Display table versions vary significantly; unsupported versions can leave boards reliant on fallback paths. Wrong script offsets can cause unsafe MMIO sequences.

### Test signals

Source read size: 174 lines, 4822 bytes. Mode-set tests, display init-script tracing, VBIOS dump comparison, and boot validation across LVDS/eDP/DP/HDMI boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/disp.c -->
