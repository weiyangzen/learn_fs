## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_securedisplay.c

Purpose: implements a debugfs validation interface for PSP secure display trusted application commands and shared helper functions for preparing and reporting secure display TA command buffers.

Important APIs and functions: `psp_securedisplay_parse_resp_status()` maps TA status codes to device error logs. `psp_prep_securedisplay_cmd_buf()` points into the PSP securedisplay shared buffer, zeros a command, sets default generic-failure status, and sets the command ID. Under debugfs, `amdgpu_securedisplay_debugfs_write()` parses opcode input, runtime-resumes the DRM device, serializes on the securedisplay mutex, invokes query-TA or send-ROI-CRC TA commands, logs results, and runtime-autosuspends. `amdgpu_securedisplay_debugfs_init()` creates `securedisplay_test` when the TA context is initialized.

Control flow: debugfs writes are single-shot (`*pos` must be zero) and limited to a 63-byte command string. Opcode 1 sends `TA_SECUREDISPLAY_COMMAND__QUERY_TA`; opcode 2 validates `phy_id < TA_SECUREDISPLAY_MAX_PHY`, writes it into the input union, and sends `SEND_ROI_CRC`. Both commands call `psp_securedisplay_invoke()` and inspect the returned command status. Runtime PM is acquired before TA interaction and released at the end.

State and persistence: mutable state is the PSP securedisplay shared command buffer, securedisplay mutex, and runtime PM usage count. No persistent data is stored; debugfs only logs responses.

Dependencies and integration points: depends on debugfs, runtime PM, PSP context, `ta_secureDisplay_if.h`, and `psp_securedisplay_invoke()` implemented in PSP code. The debugfs node is initialized from AMDGPU debugfs setup after PSP TA load.

Risks: opcode 2 returns early on invalid input without dropping the runtime PM reference acquired earlier, which can leak a PM usage count. Input parsing via `sscanf` does not validate conversion counts. The interface is write-only debugfs and intended for validation, but it drives secure TA and I2C-related operations, so it should remain restricted. Shared-buffer layout must match TA ABI.

Test signals: debugfs writes for opcode 1 and 2, invalid opcode/phy ID, runtime PM reference accounting, TA status error logs, and securedisplay TA initialization/termination in PSP flows.
