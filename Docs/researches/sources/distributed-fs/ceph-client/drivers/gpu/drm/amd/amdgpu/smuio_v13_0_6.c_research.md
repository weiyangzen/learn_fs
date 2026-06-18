# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v13_0_6.c

Purpose: minimal SMUIO v13.0.6 ROM offset operation table.

Important APIs, types, and functions: defines `smuio_v13_0_6_funcs` with `get_rom_index_offset` and `get_rom_data_offset`.

Control flow: helpers return SOC15 offsets for `regROM_INDEX` and `regROM_DATA` using v13.0.6 generated headers.

State and persistence: no mutable software state; returned offsets point to hardware ROM index/data registers.

Dependencies and integration points: used by ROM/VBIOS access code through the generic SMUIO function table for matching ASICs.

Risks and test signals: this variant lacks CG/topology callbacks, so callers must tolerate NULL operations. Test signals are successful VBIOS ROM reads on v13.0.6 devices.
