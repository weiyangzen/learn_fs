# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_nbio_v7_9.h

Purpose: this header exposes the NBIO v7.9 RAS function table.

Important definition: `extern const struct ras_nbio_ip_func ras_nbio_v7_9` is selected by generic NBIO init for NBIO IP versions 7.9.0 and 7.9.1.

Control flow and state: no active code or persistent state exists here.

Dependencies and integration: includes `ras_nbio.h` for the function-table type. Risks are minimal and mostly compile/link drift if the generic NBIO function table changes. Test signals are compile coverage and generic NBIO initialization selecting this symbol for both supported v7.9 versions.
