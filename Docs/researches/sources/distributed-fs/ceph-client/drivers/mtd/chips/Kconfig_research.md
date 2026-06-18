# sources/distributed-fs/ceph-client/drivers/mtd/chips/Kconfig

## Purpose

This file defines the RAM/ROM/Flash chip-driver Kconfig menu for MTD. It covers CFI and JEDEC probing, CFI command-set drivers, CFI geometry and byte-swap specialization, OTP support, simple RAM/ROM/absent-chip map drivers, and XIP-aware operation for supported NOR flash.

## Important Symbols and Structure

`MTD_CFI` enables Common Flash Interface probing and selects generic probe and CFI utility support. `MTD_JEDECPROBE` enables JEDEC-style probing for non-CFI-compatible flash and also selects the generic probe/utilities. `MTD_GEN_PROBE` and `MTD_CFI_UTIL` are internal support symbols.

Advanced configuration is gated by `MTD_CFI_ADV_OPTIONS`. The byte-swap choice selects `MTD_CFI_NOSWAP`, `MTD_CFI_BE_BYTE_SWAP`, or `MTD_CFI_LE_BYTE_SWAP`. `MTD_CFI_GEOMETRY` exposes bus-width and chip-interleave selectors: map bank widths from 1 to 32 bytes and interleave counts from 1 to 8. `MTD_OTP` enables protection-register/one-time-programmable operations. Command-set drivers are `MTD_CFI_INTELEXT` for command set 0001, `MTD_CFI_AMDSTD` for command set 0002, and `MTD_CFI_STAA` for command set 0020. Simple map-backed devices are `MTD_RAM`, `MTD_ROM`, and `MTD_ABSENT`. `MTD_XIP` enables execute-in-place-aware CFI operation on eligible architectures.

## Control Flow

The menu is visible when `MTD != n`. Probe choices feed the common CFI/JEDEC probe path, which identifies flash geometry and command-set IDs. The command-set selections decide which `cfi_cmdset_*.o` driver is available to bind to probed chips. Geometry symbols are compile-time specialization knobs that can reduce code size or enable exotic widths/interleaves. XIP support is only offered for non-SMP architectures with `ARCH_MTD_XIP` and Intel/AMD CFI command-set support.

## State and Persistence Behavior

The file stores compile-time capabilities in `.config`. Some choices materially affect generated code paths, particularly byte swapping, bank-width helpers, interleave support, OTP APIs, and XIP handling. No runtime state is created by this file itself.

## Dependencies and Integration Points

Selections align with `drivers/mtd/chips/Makefile`, especially `cfi_probe.o`, `jedec_probe.o`, `gen_probe.o`, `cfi_util.o`, and the command-set modules. `MTD_XIP` integrates with architecture support and command-set driver XIP paths. OTP configuration exposes MTD protection-register hooks implemented by command-set drivers such as `cfi_cmdset_0001.c` and `cfi_cmdset_0002.c`.

## Risks and Edge Cases

Incorrect byte-swap or geometry selections can make probe commands unreadable by the chip. Reducing supported bank widths/interleaves can save code size but break boards with different wiring. OTP support is inherently risky: writes and locks are one-time operations. XIP support has tight constraints around interrupt masking and flash array mode; enabling it on unsuitable platforms would be dangerous, hence the strict dependencies.

## Test Signals

Config tests should verify that CFI and JEDEC probes select their utility dependencies, command-set symbols build the expected objects, advanced geometry defaults include common 8/16/32-bit bus widths and 1/2 interleaves, and XIP is only visible under its architecture constraints. Hardware tests should confirm probe success, correct endianness, OTP visibility when enabled, and successful command-set binding.
