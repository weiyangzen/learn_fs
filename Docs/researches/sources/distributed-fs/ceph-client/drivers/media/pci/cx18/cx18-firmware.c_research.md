# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-firmware.c

## Purpose
This file initializes cx23418 chip clocks, power, DDR memory, and CPU/APU firmware. It also halts firmware during removal and validates firmware writes through MMIO readback.

## Important APIs, Types, and Functions
Public functions are `cx18_firmware_init()`, `cx18_halt_firmware()`, `cx18_init_memory()`, and `cx18_init_power()`. Static loaders are `load_cpu_fw_direct()` for `v4l-cx23418-cpu.fw` and `load_apu_fw_direct()` for segmented `v4l-cx23418-apu.fw`. `struct cx18_apu_rom_seghdr` describes APU firmware segments.

## Control Flow
Power initialization programs PLLs, clock selectors, half-clock selectors, and clock enables. Memory initialization resets DDR, writes board-specific DDR timing from `cx->card->ddr`, enables bus timeout, and configures write memory buffers. Firmware init masks DSP interrupts, stops CPU/APU, enables mailbox interrupts, loads CPU firmware through paged encoder memory, reinitializes SCB, loads APU segments, starts CPU, waits for APU reset release, disables CPU-side ack interrupts, tests firmware with `CX18_CPU_DEBUG_PEEK32`, and initializes GPIO-related firmware state.

## State and Persistence
Hardware clock, reset, DDR, SCB, CPU program, APU program, and interrupt-enable state persist until reset or module removal. `CX18_F_I_LOADED_FW` controls logging across reloads. Firmware files are transient resources.

## Dependencies and Integration Points
It depends on Linux firmware loading, MMIO/page helpers, IRQ enable helpers, SCB initialization, mailbox API, and board DDR tables. It is invoked during probe for power/memory and during first-open firmware bootstrap.

## Risks and Edge Cases
Firmware writes assume 32-bit alignment and validate by readback. APU segment parsing must respect little-endian headers and segment bounds. Board-specific DDR values are critical. Failure after enabling interrupts can leave partial firmware state. The double firmware load is orchestrated by `cx18-driver.c`, so this routine must remain idempotent enough for retries.

## Test Signals
Boot with missing CPU/APU firmware, verify firmware size/version logs, capture after repeated open/close, compare DDR stability per board, and inspect mailbox liveness through the debug peek command.
