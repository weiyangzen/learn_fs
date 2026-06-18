<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/vpstate.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/vpstate.c

### Purpose

Parser for voltage-pstate mapping tables. It links performance states to voltage or boost policy records.

### Important APIs, types, and functions

`nvbios_vpstateTe/Ee/Ep()` and match helpers parse table headers and entries into structures declared in `vpstate.h`.

### Control flow

The table is reached through BIT P, validated by version, then indexed with header/count/length fields. Entries expose pstate indexes and voltage-related values for caller matching.

### State and persistence behavior

No persistent state. Parsed records are consumed by clock/voltage management.

### Dependencies and integration points

Depends on BIT P, VBIOS readers, and pstate/voltage users.

### Risks

Mismatched pstate indexes can select wrong voltage limits for a performance state. Unsupported tables must not produce partial bogus records.

### Test signals

Source read size: 88 lines, 2642 bytes. Pstate/voltage transition tests, VBIOS fixture parsing, and comparison of decoded maps with vendor tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/vpstate.c -->
