# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/kv_smc.c

## Purpose

`kv_smc.c` provides the low-level SMC communication helpers used by Kaveri/Kabini legacy DPM. It sends messages to the SMU, passes one message argument, reads SMC SRAM dwords, enables/disables DPM and BAPM, and copies arbitrary byte ranges into SMC SRAM while preserving unaligned leading/trailing bytes.

## Important APIs and Functions

`amdgpu_kv_notify_message_to_smu()` writes a message ID to `mmSMC_MESSAGE_0`, polls `mmSMC_RESP_0` up to `adev->usec_timeout`, and treats response values `0xff` and `0xfe` as invalid. `amdgpu_kv_send_msg_to_smc_with_parameter()` writes `mmSMC_MSG_ARG_0` before calling the notify helper. `amdgpu_kv_dpm_get_enable_mask()` sends `PPSMC_MSG_SCLKDPM_GetEnabledMask` and reads `ixSMC_SYSCON_MSG_ARG_0`.

`kv_set_smc_sram_address()` validates 4-byte alignment and upper bound, writes `mmSMC_IND_INDEX_0`, and disables auto-increment through `mmSMC_IND_ACCESS_CNTL`. `amdgpu_kv_read_smc_sram_dword()` uses that address setup and reads `mmSMC_IND_DATA_0`. `amdgpu_kv_copy_bytes_to_smc()` handles bounded byte copies into the big-endian SMC address space, using read-modify-write for unaligned first and final dwords. `amdgpu_kv_smc_dpm_enable()` and `amdgpu_kv_smc_bapm_enable()` wrap DPM and BAPM enable/disable messages.

## Control Flow

Higher-level DPM code first calls `amdgpu_kv_read_smc_sram_dword()` to discover firmware DPM table offsets, then repeatedly calls `amdgpu_kv_copy_bytes_to_smc()` to upload generated table fields. Runtime changes use `amdgpu_kv_send_msg_to_smc_with_parameter()` for enabled masks and forced levels, while feature toggles use the direct message wrappers.

## State and Persistence Behavior

This file maintains no software state of its own. Its effects persist in hardware mailboxes, SMC SRAM, and SMU firmware state. SRAM writes remain active until overwritten or the SMU/device resets. Message responses are transient and must be interpreted immediately by callers.

## Dependencies and Integration Points

The file includes `amdgpu.h`, `cikd.h`, `kv_dpm.h`, and SMU 7.0 register headers. It depends on AMDGPU MMIO macros `RREG32`, `WREG32`, `RREG32_SMC`, and `WREG32_P`, plus SMC message IDs from `ppsmc.h`. Its functions are declared in `kv_dpm.h` and used throughout `kv_dpm.c`.

## Risks and Edge Cases

The notify helper returns success for any nonzero response other than `0xff` or `0xfe`; if firmware uses additional failure codes, callers may miss them. Timeout leaves `tmp == 0` but still returns success, which is a notable risk. SRAM address setup rejects unaligned reads but byte-copy supports unaligned writes through RMW. The big-endian packing must match firmware layout; mistakes silently corrupt DPM tables. `smc_start_address + byte_count` can overflow if ever called with hostile values, though current callers use small trusted table offsets.

## Test Signals

Validation should include SMU message success during DPM enable/disable, correct SCLK enable-mask reads, firmware table upload without `-EINVAL`, suspend/resume re-upload, and hardware behavior after unaligned writes such as single-byte boot-level fields. Instrumenting SMC response codes is useful when diagnosing failures.
