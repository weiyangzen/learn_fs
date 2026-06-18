# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_psp_v13_0.h

Purpose: this header exposes the PSP v13 RAS IP function table.

Important definition: `extern const struct ras_psp_ip_func ras_psp_v13_0` is the table selected by generic PSP init for supported PSP v13 IP versions.

Control flow and state: no code or state is implemented here.

Dependencies and integration: includes `ras_psp.h` for the function-table type. Risks are limited to compile/link drift if the PSP interface changes. Test signals are generic PSP init coverage for supported v13 versions and linker coverage of this symbol.
