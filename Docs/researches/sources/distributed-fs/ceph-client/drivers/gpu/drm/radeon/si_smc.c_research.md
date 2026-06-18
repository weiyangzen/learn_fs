# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/si_smc.c

## Purpose
`si_smc.c` implements low-level Southern Islands System Management Controller access. It provides serialized SMC SRAM reads/writes, SMC microcode loading, SMC reset/start/clock control, and synchronous PPSMC message delivery. Higher-level DPM code in `si_dpm.c` depends on this file to load firmware, populate SMC tables, and issue runtime power-management commands.

## Important APIs and functions
- `si_copy_bytes_to_smc` copies arbitrary bytes to SMC SRAM with alignment and limit checks. It writes full dwords in SMC big-endian byte order and performs read-modify-write for trailing partial dwords.
- `si_start_smc`, `si_reset_smc`, `si_stop_smc_clock`, `si_start_smc_clock`, and `si_is_smc_running` control or inspect SMC reset and clock bits.
- `si_program_jump_on_start` writes a small startup jump sequence at SMC address zero before releasing the SMC.
- `si_send_msg_to_smc` writes a PPSMC message to `SMC_MESSAGE_0`, polls `SMC_RESP_0` up to `rdev->usec_timeout`, and returns the firmware response code.
- `si_wait_for_smc_inactive` polls SMC clock-control state after halt-style messages.
- `si_load_smc_ucode` loads either newer header-described firmware or legacy family-specific firmware at known SMC addresses and sizes.
- `si_read_smc_sram_dword` and `si_write_smc_sram_dword` provide locked indexed dword access to SMC SRAM.
- Internal helper `si_set_smc_sram_address` validates alignment/range and programs the indexed SMC SRAM address.

## Control flow
All SRAM access goes through the SMC indexed register pair. Address setup validates 4-byte alignment and the caller-supplied SRAM limit, writes `SMC_IND_INDEX_0`, and disables auto-increment unless the bulk firmware loader explicitly enables it. Byte copying serializes on `rdev->smc_idx_lock`, writes big-endian dwords, and preserves untouched bytes in the last dword.

Firmware loading first validates that firmware is present. For new firmware it parses `smc_firmware_header_v1_0` to get the ucode start, size, and payload offset; for legacy firmware it selects family-specific start and size constants for Tahiti, Pitcairn, Verde, Oland, or Hainan. It then enables SMC auto-increment, streams big-endian dwords to `SMC_IND_DATA_0`, disables auto-increment, and releases the lock.

Message delivery first checks `si_is_smc_running`; if reset or clock-disabled, it fails immediately. Otherwise it writes the message and polls for any nonzero response. DPM callers interpret only `PPSMC_Result_OK` as success for most transitions.

## State and persistence behavior
Persistent hardware state includes SMC SRAM contents, loaded SMC firmware, SMC reset state, SMC clock-gate state, SMC message/response registers, and the SMC indexed access auto-increment setting. The spinlock protects the shared indexed register window from concurrent users on the CPU side. The file does not allocate persistent memory; it consumes `rdev->smc_fw`, `rdev->new_fw`, `rdev->family`, `rdev->usec_timeout`, and `rdev->smc_idx_lock`.

## Dependencies and integration points
The file depends on Radeon MMIO accessors and SI register definitions from `radeon.h`, `sid.h`, `ppsmc.h`, `radeon_ucode.h`, and `sislands_smc.h`. It is called heavily by `si_dpm.c` for firmware upload, SMC firmware header reads, SMC state/table writes, soft register writes, CAC/DTE/fan table uploads, and PPSMC state-transition messages. `sislands_smc.h` exposes the function prototypes to the DPM layer.

## Risks and edge cases
- SMC SRAM is big-endian, so byte order is critical. Incorrect packing corrupts firmware or SMC data tables.
- Alignment and limit checks are the primary protection against bad SRAM accesses. Callers must pass the correct firmware-discovered SRAM end and table offsets.
- Partial dword writes perform read-modify-write; failure to serialize indexed access would corrupt unrelated bytes, which is why the spinlock is required.
- `si_send_msg_to_smc` treats any nonzero response as completion and returns the raw response. Callers must check for `PPSMC_Result_OK`.
- Legacy firmware loading uses a `BUG()` on unknown ASIC family, making unsupported family routing fatal.
- `si_wait_for_smc_inactive` currently returns OK after polling regardless of timeout details, so higher-level code may not distinguish a slow or stuck SMC.

## Test signals
Useful validation includes successful SI SMC firmware load, DPM enablement, SMC firmware header parsing from SRAM, repeated state transitions, fan-control start/stop messages, CAC/DTE enable messages, suspend/resume, and failure-path tests for missing firmware, unaligned SMC addresses, oversized copies, and SMC-not-running message sends. Kernel logs around `si_upload_firmware`, `si_process_firmware_header`, and DPM state-switch failures are the most direct runtime signals.
