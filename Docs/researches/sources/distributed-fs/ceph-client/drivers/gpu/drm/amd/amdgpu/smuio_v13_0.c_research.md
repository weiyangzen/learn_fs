# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v13_0.c

Purpose: SMUIO v13.0 operations for ROM offsets, ROM clock gating, topology identity, host-GPU XGMI detection, and package type.

Important APIs, types, and functions: defines `smuio_v13_0_funcs` with ROM index/data callbacks, die/socket ID accessors, `is_host_gpu_xgmi_supported`, ROM clock-gating update/query, and `get_pkg_type`.

Control flow: ROM and CG operations mirror newer SMUIO register names. Identity helpers read `regSMUIO_MCM_CONFIG` and extract `DIE_ID`, `SOCKET_ID`, `TOPOLOGY_ID`, or package-related encodings. Host-GPU XGMI is inferred from topology bit 0; package type maps topology values `0x4` and `0xC` to CEM and defaults to OAM.

State and persistence: state is hardware SMUIO MCM configuration and ROM clock-control registers. No persistent software state exists.

Dependencies and integration points: feeds multi-die/socket topology, XGMI decisions, VBIOS ROM access, and CG reporting through the generic `amdgpu_smuio_funcs` interface.

Risks and test signals: package mapping defaults to OAM for all unrecognized topology values, which can hide future encodings. Host-GPU XGMI detection uses a local mask against extracted topology. Test signals include topology reporting, package classification on CEM/OAM systems, ROM access, and CG state reporting.
