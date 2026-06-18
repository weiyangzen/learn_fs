# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/kv_smc.c

## Purpose

`kv_smc.c` implements the low-level SMU/SMC communication primitives used by Kaveri DPM. It sends messages to the SMU, reads the current enabled SCLK DPM mask, sends parameterized messages, reads aligned dwords from SMC SRAM, toggles DPM and BAPM, and copies arbitrary byte ranges into SMC SRAM while preserving surrounding bytes for unaligned writes.

## Important APIs and functions

- `kv_notify_message_to_smu(struct radeon_device *rdev, u32 id)`: writes a message ID to `SMC_MESSAGE_0`, polls `SMC_RESP_0` until a response appears or `rdev->usec_timeout` expires, and maps response values `0xff` and `0xfe` to `-EINVAL`.
- `kv_dpm_get_enable_mask(struct radeon_device *rdev, u32 *enable_mask)`: sends `PPSMC_MSG_SCLKDPM_GetEnabledMask` and reads `SMC_SYSCON_MSG_ARG_0` through `RREG32_SMC()` on success.
- `kv_send_msg_to_smc_with_parameter(struct radeon_device *rdev, PPSMC_Msg msg, u32 parameter)`: writes the parameter to `SMC_MSG_ARG_0`, then sends the message.
- `kv_set_smc_sram_address()`: static bounds/alignment helper that rejects unaligned dword addresses and addresses beyond the provided SRAM limit, then programs `SMC_IND_INDEX_0` and clears auto-increment through `SMC_IND_ACCESS_CNTL`.
- `kv_read_smc_sram_dword()`: sets an aligned SRAM address and reads `SMC_IND_DATA_0`.
- `kv_smc_dpm_enable()` and `kv_smc_bapm_enable()`: message wrappers for enabling/disabling DPM and BAPM.
- `kv_copy_bytes_to_smc()`: writes byte buffers into SMC SRAM, handling unaligned leading and trailing bytes with read-modify-write and writing full dwords in big-endian SMC byte order.

## Control flow

SMU message flow is synchronous: write message or parameter, poll for nonzero response one microsecond at a time up to `rdev->usec_timeout`, then return success unless the final response is one of the explicit error values. Parameterized messages write `SMC_MSG_ARG_0` before entering the same notify flow.

SMC SRAM access first validates a caller-provided firmware limit. Reads require a dword-aligned address. Writes accept arbitrary byte offsets and lengths but reject ranges where `smc_start_address + byte_count` exceeds the limit. For an unaligned start, the function backs up to the containing dword, reads original data, constructs a merged big-endian dword preserving untouched bytes, and writes it back. It then writes full aligned dwords in a loop. If trailing bytes remain, it reads the final dword, shifts the new bytes into the high-order SMC byte lanes, preserves untouched low-order bytes, and writes back.

## State and persistence behavior

This file does not allocate memory or keep driver-private state. It mutates hardware and firmware-visible state by writing SMU mailbox registers and SMC SRAM through indirect access registers. The copied bytes persist in SMC SRAM until overwritten by the driver or firmware reset. Since auto-increment is disabled before each indirect access, callers get deterministic single-address dword writes rather than streaming side effects.

## Dependencies and integration points

- Includes `radeon.h` for `struct radeon_device`, MMIO macros, delays, and timeout fields.
- Includes `cikd.h` for SMC mailbox/indirect register offsets and response masks.
- Includes `kv_dpm.h` for exported prototypes and `PPSMC_Msg` typing.
- Used heavily by `kv_dpm.c` to read firmware header pointers, upload SMU7 Fusion DPM tables, toggle feature bits, set enabled masks, power-gate media blocks, and control DPM/BAPM/CAC/ULV/NB DPM.

## Risks and edge cases

- Timeout handling is weak: if the response never becomes nonzero, the final response is zero and the function returns success. This can mask SMU non-response unless callers detect later state failures.
- Only `0xff` and `0xfe` are treated as errors; other unexpected non-1 response values return success.
- `smc_start_address + byte_count` is checked with 32-bit arithmetic and could theoretically wrap before comparison if impossible values are passed.
- Unaligned copy logic is byte-order sensitive. The code assumes SMC SRAM dword layout is big-endian and manually packs bytes accordingly.
- The helper disables auto-increment on every address set, so future changes that assume bulk auto-increment writes would not work without changing this contract.
- No locking is performed here; callers must serialize SMU mailbox and indirect SRAM access at a higher level if concurrent paths are possible.

## Test signals

- DPM enable success is the primary functional test because it depends on firmware header reads and multiple table uploads.
- Forced performance level changes exercise parameterized SMU messages and enabled-mask reads.
- BAPM toggling across AC/battery transitions validates `kv_smc_bapm_enable()`.
- Boundary tests around `kv_copy_bytes_to_smc()` should include aligned writes, unaligned leading writes, trailing byte writes, zero-length writes, and limit rejection.
- Hardware debug should confirm that SMU response timeouts are not silently accepted in problematic firmware cases.
