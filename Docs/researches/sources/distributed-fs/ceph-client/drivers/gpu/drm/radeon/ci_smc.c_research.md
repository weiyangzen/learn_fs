# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/ci_smc.c

## Purpose

`ci_smc.c` provides the low-level SMC firmware and SRAM access primitives for the CIK Radeon DPM implementation. It controls SMC reset/clock state, loads SMC microcode, programs the startup jump, checks whether the SMC is running, and reads/writes SMC SRAM through indirect MMIO registers. `ci_dpm.c` builds policy and table contents; this file is the transport and lifecycle layer that moves bytes and dwords into the SMC address space.

## Important APIs, Types, and Functions

Public functions declared in `ci_dpm.h`:

- `ci_copy_bytes_to_smc()` copies arbitrary bytes into SMC SRAM, requiring a 4-byte-aligned start address and checking the caller-supplied limit.
- `ci_start_smc()` clears `RST_REG` in `SMC_SYSCON_RESET_CNTL`.
- `ci_reset_smc()` sets `RST_REG` in `SMC_SYSCON_RESET_CNTL`.
- `ci_program_jump_on_start()` writes a fixed 4-byte jump sequence at SMC address zero.
- `ci_stop_smc_clock()` sets `CK_DISABLE` in `SMC_SYSCON_CLOCK_CNTL_0`.
- `ci_start_smc_clock()` clears `CK_DISABLE`.
- `ci_is_smc_running()` checks that the clock is not disabled and that `SMC_PC_C` is at or beyond `0x20100`.
- `ci_load_smc_ucode()` copies SMC firmware into SRAM, supporting both new firmware headers and legacy family-specific firmware sizes/addresses.
- `ci_read_smc_sram_dword()` reads one dword from SMC SRAM.
- `ci_write_smc_sram_dword()` writes one dword to SMC SRAM.

The internal `ci_set_smc_sram_address()` validates alignment and bounds, writes `SMC_IND_INDEX_0`, and disables auto-increment for indexed access. A `ci_wait_for_smc_inactive()` implementation is present only under `#if 0`.

## Control Flow

All SRAM accesses use indirect index/data registers. Dword read/write helpers hold `rdev->smc_idx_lock`, set the address, and access `SMC_IND_DATA_0`. `ci_copy_bytes_to_smc()` holds the same lock across the full transfer, packs full dwords in SMC big-endian order, and handles a final partial dword with a read/modify/write preserving trailing bytes.

`ci_load_smc_ucode()` chooses firmware layout from `rdev->new_fw`. New firmware uses `struct smc_firmware_header_v1_0` for start address, size, and payload offset. Legacy firmware selects fixed Bonaire or Hawaii start/size constants. It requires dword-aligned firmware size, enables indirect auto-increment, streams packed big-endian dwords, then disables auto-increment.

Clock and reset helpers directly manipulate SMC system-control registers. The DPM enable path stops and resets the SMC before firmware upload, then programs the startup jump, starts the clock, releases reset, and waits in `ci_dpm.c` for firmware flags.

## State and Persistence Behavior

This file allocates no persistent memory. It mutates SMC SRAM contents and SMC control/access registers. The `smc_idx_lock` serializes CPU access to indirect SMC index/data registers, but it does not enforce higher-level firmware sequencing; callers must still ensure firmware loading, SMC start/stop, and PPSMC messages occur in the right order.

## Dependencies and Integration Points

`ci_smc.c` depends on `radeon.h`, `cikd.h`, `ppsmc.h`, `radeon_ucode.h`, and `ci_dpm.h`. Its primary consumer is `ci_dpm.c`, which uses these helpers to load firmware, read firmware header offsets, upload DPM/MC/Powertune/fan tables, write soft registers, start/stop the SMC, and check whether PPSMC messaging is legal. Firmware selection/request happens elsewhere in the CIK/Radeon initialization path; this file assumes `rdev->smc_fw` is already available.

## Risks and Edge Cases

- Address validation depends on the caller-supplied `limit`.
- `ci_copy_bytes_to_smc()` rejects unaligned start addresses even for byte fragments.
- SMC SRAM byte order is big-endian, so callers must not double-swap fields.
- Partial-dword writes preserve low-order bytes from existing SMC SRAM, which assumes that read is valid and meaningful.
- `ci_load_smc_ucode()` relies on firmware validation/header correctness and known constants rather than explicitly checking every payload byte against `limit`.
- Unknown legacy ASIC family calls `BUG()`.
- `ci_is_smc_running()` uses a simple PC threshold and can misclassify unusual firmware states.
- `ci_program_jump_on_start()` uses `sizeof(data) + 1` as the write limit, which is sufficient but unusual.

## Test Signals

Useful validation signals include kernel build coverage; boot on Bonaire/Hawaii with SMC firmware; repeated DPM enable/disable; instrumentation of table uploads for byte ordering and partial writes; concurrency stress across fan/sysfs/debugfs/media/display paths; and fault injection for missing firmware, malformed size, bad SRAM limits, and SMC nonresponse.
