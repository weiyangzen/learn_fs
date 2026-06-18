<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/ior.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/ior.c

Purpose: common output-resource object lifecycle and lookup helpers. IORs represent DAC, SOR, and PIOR hardware resources used to drive connectors.

Important APIs and functions: `nvkm_ior_find()` searches `disp->iors` for a matching type and optional ID. `nvkm_ior_new_()` allocates an IOR, initializes callbacks, display pointer, type, ID, HDA flag, human-readable name (`DAC-0`, `SOR-1`, etc.), links it into `disp->iors`, and logs construction. `nvkm_ior_del()` removes and frees an IOR.

Control flow: simple list management. Generation files provide `nvkm_ior_func` tables for state, power, clock, HDMI, DP, HDA, backlight, route, and sense behavior.

State and persistence: persistent state is held in `struct nvkm_ior` as defined in `ior.h`, including function table, type/id, HDA capability, name, and arm/asy protocol state. This file owns allocation and list membership.

Dependencies and integration points: used by display oneinit/generation constructors, output acquire/release paths, DP/HDMI programming, and base display init which powers all IORs through their callbacks.

Risks: ID/type matching must reflect hardware masks; wrong HDA flag changes audio exposure. Teardown ordering must ensure outputs release IORs before IOR deletion.

Test signals: IOR count/mask creation on each generation, output acquire/release, HDMI/DP/DAC modesets, audio capability detection, and display teardown leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/ior.c -->
