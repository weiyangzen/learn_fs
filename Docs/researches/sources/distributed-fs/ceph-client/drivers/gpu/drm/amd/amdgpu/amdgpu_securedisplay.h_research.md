## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_securedisplay.h

Purpose: declares secure display debugfs initialization and PSP secure display command helper functions.

Important APIs and types: includes `amdgpu.h` and `ta_secureDisplay_if.h`; declares `amdgpu_securedisplay_debugfs_init()`, `psp_securedisplay_parse_resp_status()`, and `psp_prep_securedisplay_cmd_buf()`.

Control flow: no implementation; the header exposes helpers to PSP initialization code and debugfs setup.

State and persistence: none in the header; functions operate on PSP securedisplay context and shared TA command buffers.

Dependencies and integration points: integrates AMDGPU PSP code, TA ABI definitions, and debugfs validation code.

Risks: header guard lacks trailing double underscore but is unique enough. The include of full `amdgpu.h` is broad but needed for PSP/device types.

Test signals: compile coverage in PSP and debugfs code, plus securedisplay TA debugfs runtime tests.
