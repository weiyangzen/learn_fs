# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v15_0_8.c

Purpose: SMUIO v15.0.8 operations for ROM offsets, GPU clock counter, topology IDs, host-GPU XGMI detection, package type, and placeholder ROM clock-gating support.

Important APIs, types, and functions: defines `smuio_v15_0_8_funcs` with ROM callbacks, `get_gpu_clock_counter`, `get_die_id`, `get_socket_id`, `is_host_gpu_xgmi_supported`, `update_rom_clock_gating`, `get_clock_gating_state`, and `get_pkg_type`. Ethernet-switch and custom-HBM helpers are present but compiled out.

Control flow: ROM helpers return SOC15 offsets; ROM CG update is a no-op. Clock counter uses the upper/lower/upper rollover-safe read. Die/socket/XGMI/package helpers read `regSMUIO_MCM_CONFIG`; XGMI tests topology bit 0 and package type maps bits `0xC` to BB or CEM, otherwise unknown.

State and persistence: state is SMUIO register contents. No persistent software state exists.

Dependencies and integration points: feeds ROM access, timing, topology, and package decisions through `amdgpu_smuio_funcs` for v15.0.8 devices.

Risks and test signals: ROM CG state query reads `regCGTT_ROM_CLK_CTRL0` while update does nothing, which can produce read-only reporting semantics. Package mapping ignores lower package bits except `0xC` mask. Test signals are ROM reads, monotonic counter reads, die/socket reporting, XGMI topology detection, and package classification.
