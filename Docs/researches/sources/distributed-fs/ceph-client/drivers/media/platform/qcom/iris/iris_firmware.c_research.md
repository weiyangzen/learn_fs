# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_firmware.c

## Purpose
`iris_firmware.c` loads Qualcomm MDT firmware into reserved memory, authenticates and resets the video subsystem through SCM/PAS, applies trusted-zone content-protection memory settings, unloads firmware, and toggles remote hardware state.

## Important APIs, Types, And Functions
`iris_fw_load()` selects the firmware path from device tree `firmware-name` or platform default, calls the private `iris_load_fw_to_memory()`, authenticates and resets using `qcom_scm_pas_auth_and_reset()`, then applies each `tz_cp_config` through `qcom_scm_mem_protect_video_var()`. `iris_fw_unload()` calls `qcom_scm_pas_shutdown()`. `iris_set_hw_state()` wraps `qcom_scm_set_remote_state()`.

## Control Flow
Firmware loading obtains the first reserved-memory region as a resource, requests the firmware, checks MDT total size against reserved memory size, maps reserved memory with write-combining, calls `qcom_mdt_load()`, unmaps, and releases the firmware. After successful load, PAS auth/reset starts the subsystem. If any TZ memory protection step fails, the code shuts down PAS before returning.

## State And Persistence Behavior
Firmware image state is external to driver heap and lives in reserved memory and SCM-managed subsystem state. The function does not cache firmware data. PAS and TZ memory protection state persist until shutdown or system reset.

## Dependencies And Integration Points
The file depends on Linux firmware APIs, reserved-memory OF APIs, `qcom_mdt_loader`, and Qualcomm SCM calls. `iris_core_init()` invokes `iris_fw_load()` after VPU power-on and before firmware boot/switch-to-hwmode; suspend/resume paths use `iris_set_hw_state()`.

## Risks And Test Signals
`iris_fw_load()` reports firmware download failure as `-ENOMEM` even when lower layers returned another error, which can obscure diagnostics. Tests should cover missing firmware property fallback, too-large firmware image, reserved-memory lookup failure, SCM auth failure, TZ protection failure with PAS shutdown, repeated load/unload, and invalid overly long firmware names.
