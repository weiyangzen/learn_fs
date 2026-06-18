<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/headca7d.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/headca7d.c

### Purpose
`headca7d.c` implements GB202/Blackwell head programming. It follows the C57D/C37D logical model but uses `NVCA7D` methods and physical surface addresses for cursor and output LUT resources.

### Key APIs And Functions
Callbacks include `headca7d_display_id()`, `headca7d_or()`, `headca7d_procamp()`, `headca7d_dither()`, `headca7d_curs_set()`, `headca7d_curs_clr()`, `headca7d_olut_set()`, `headca7d_olut_clr()`, `headca7d_mode()`, and `headca7d_view()`. The `headca7d` table reuses `headc57d_olut()`, `head917d_curs_layout()`, `headc37d_curs_format()`, static window mapping, and 907D ILUT validation.

### Control Flow And State
Cursor and OLUT set paths split buffer offsets into high/low physical address fields, set target `PHYSICAL_NVM`, and enable the corresponding surface. Clear paths disable the low address method. Mode programming writes raster timing, progressive structure, and pixel clock frequency/max; output-resource programming uses explicit `NVCA7D` bpp constants and rejects unknown depth encodings.

### Dependencies And Integration
It depends on `clca7d`, `pushc97b`, `atom.h`, `head.h`, and shared head helpers. `coreca7d.c` selects this table for Blackwell display cores.

### Risks And Test Signals
Physical-address programming increases alignment and lifetime risk for cursor/LUT memory. Tests should cover cursor and gamma updates on GB202, 6/8/10 bpc output depth, display-id use with MST, suspend/resume, and invalid depth handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/headca7d.c -->
