# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_mp1_v13_0.h

Purpose: this header exposes the MP1 v13 RAS function table.

Important definition: `extern const struct ras_mp1_ip_func mp1_ras_func_v13_0` is the table selected by `ras_mp1.c` for supported MP1 v13 IP versions.

Control flow and state: no code or persistent state exists. It is a narrow declaration header.

Dependencies and integration: includes `ras_mp1.h`, so users receive the generic MP1 function-table type. Risks are minimal but include stale declaration if the implementation table changes shape. Test signals are compile coverage of generic MP1 init selecting this symbol and linker coverage for all supported v13 IP version cases.
