# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/trinity_smc.c

## Purpose

`trinity_smc.c` is the low-level SMC/SMU message transport used by Trinity DPM. It writes message IDs and scratch arguments to SMC registers, polls for firmware responses, maps common DPM operations to PPSMC messages, and provides a simple SMU mutex request/release mechanism.

## Important APIs, Types, and Functions

- `trinity_notify_message_to_smu()` writes `SMC_MESSAGE_0`, polls `SMC_RESP_0` up to `rdev->usec_timeout`, and translates response codes `0xff` and `0xfe` into `-EINVAL`.
- `trinity_dpm_bapm_enable()` sends `PPSMC_MSG_EnableBAPM` or `PPSMC_MSG_DisableBAPM`.
- `trinity_dpm_config()` writes `SMU_SCRATCH0` to 1 or 0 before `PPSMC_MSG_DPM_Config`.
- `trinity_dpm_force_state()` and `trinity_dpm_n_levels_disabled()` pass an argument through `SMU_SCRATCH0`.
- `trinity_uvd_dpm_config()`, `trinity_dpm_no_forced_level()`, `trinity_dce_enable_voltage_adjustment()`, and `trinity_gfx_dynamic_mgpg_config()` send specific PPSMC messages.
- `trinity_acquire_mutex()` requests SMC ownership through `SMC_INT_REQ`; `trinity_release_mutex()` clears it.

## Control Flow

All exported command helpers funnel through `trinity_notify_message_to_smu()`. Callers that need an argument write scratch first, then send the message. Most higher-level DPM paths in `trinity_dpm.c` wrap these calls with `trinity_acquire_mutex()` and `trinity_release_mutex()`.

## State and Persistence Behavior

The file persists no C-side state. It mutates hardware registers: `SMC_MESSAGE_0`, `SMC_RESP_0`, `SMU_SCRATCH0`, and `SMC_INT_REQ`. Scratch arguments remain in SMC-visible registers until overwritten, and firmware-side DPM state changes persist after successful messages.

## Dependencies and Integration Points

- Depends on `radeon.h` register access macros, Trinity register definitions, DPM private header prototypes, and PPSMC message IDs from `ppsmc.h`.
- Called by Trinity DPM lifecycle, BAPM, UVD DPM, VCE/media, voltage-adjustment, and forced-level flows.

## Risks and Edge Cases

- `trinity_notify_message_to_smu()` treats a timeout with response value 0 as success unless the response is `0xff` or `0xfe`; callers cannot distinguish no response from success.
- `trinity_acquire_mutex()` has no return value and does not report timeout if `SMC_INT_REQ` never acknowledges.
- Message arguments use one shared scratch register, so callers must preserve ordering and locking externally.

## Test Signals

- Hardware tests should inject/observe `SMC_RESP_0` values for success, unknown message, failed handling, and timeout/no-response cases.
- DPM transition tests should confirm every scratch-argument message writes the expected value before message delivery.
- Locking tests should verify callers hold the SMC mutex around multi-register SMC sequences.
