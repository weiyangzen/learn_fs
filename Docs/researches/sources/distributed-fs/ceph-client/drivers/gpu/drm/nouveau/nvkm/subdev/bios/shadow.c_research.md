<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/shadow.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/shadow.c

### Purpose

VBIOS shadow-source orchestrator. It tries multiple ROM sources, validates and scores candidate images, supports a user-specified `NvBios` source or firmware file, and installs the best image into `bios->data`.

### Important APIs, types, and functions

`nvbios_shadow()` is the public entry. Internal helpers include `shadow_fetch()`, `shadow_image()`, `shadow_method()`, firmware read/init/release callbacks, and the `shadow` candidate state.

### Control flow

Each source initializes backend data, fetches enough bytes, validates ROM images through `nvbios_image()`, checks checksum policy for type-0 images, recursively scores multi-image ROMs, then detaches candidate data for comparison. The best score wins; losing buffers are freed.

### State and persistence behavior

`bios->data` and `bios->size` become the selected ROM image for the BIOS subdevice lifetime. Candidate `shadow` structs temporarily own backend data and scores.

### Dependencies and integration points

Depends on `priv.h` source backends, firmware loader, core options, image parsing, checksum, and BIOS buffer extension. `base.c` calls it during BIOS construction.

### Risks

Source selection is foundational. Bad scoring can select a stale or corrupted ROM; checksum policy must balance firmware quirks against safety. User-specified invalid sources must be rejected cleanly.

### Test signals

Source read size: 248 lines, 6259 bytes. Boot tests for every source backend, `NvBios=` override tests, corrupt checksum tests, multi-image ROM validation, and firmware-file override tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/shadow.c -->
