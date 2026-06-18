# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/smuio_v13_0_3.c

Purpose: SMUIO v13.0.3 topology helper table focused on die ID, socket ID, and package type.

Important APIs, types, and functions: defines `smuio_v13_0_3_funcs` with `get_die_id`, `get_socket_id`, and `get_pkg_type`. Package type uses local `PKG_TYPE_MASK`.

Control flow: each helper reads `regSMUIO_MCM_CONFIG`; die/socket helpers extract fields directly. Package helper extracts `PKG_TYPE`, masks low bits, and maps `0` to CEM, `1` to OAM, `2` to APU, otherwise unknown.

State and persistence: state is the hardware MCM config register. No software persistence.

Dependencies and integration points: used by amdgpu topology/package code through `amdgpu_smuio_funcs` for ASICs with this SMUIO revision.

Risks and test signals: reserved package encodings deliberately become unknown. Test signals are correct die/socket ID reporting and package classification across CEM/OAM/APU devices.
