# sources/distributed-fs/ceph-client/sound/soc/amd/raven/chip_offset_byte.h

## Purpose
This generated-style register header enumerates ACP3.0 absolute byte offsets for Raven hardware blocks, including DMA, AXI2AXI ATU, clock/reset, external interrupts, PGFSM, scratch SRAM, SoundWire-related registers, audio buffers, I2S/TDM, BT/TDM, Azalia, and ACP/Azalia page tables.

## Important APIs, Types, And Functions
It contains macro definitions only, all prefixed primarily with `mmACP_`, `mmSW_`, or `mmAudio_Az_`. There are no functions or data structures.

## Control Flow
No executable control flow exists. Driver code includes this file through `acp3x.h` and uses the macros to calculate register addresses for `rv_readl()` and `rv_writel()`.

## State And Persistence Behavior
The header itself has no state. It defines the persistent MMIO register layout that the driver uses to control DMA descriptors, ring buffers, linear position counters, interrupt control/status, power-gating state, and I2S/BT TDM registers.

## Dependencies And Integration Points
The offset values are absolute addresses based around the ACP3x physical base `0x1240000`, so the Raven helper subtracts `ACP3x_PHY_BASE_ADDRESS` to convert them to offsets from the mapped BAR. The Raven I2S and DMA code depends on audio-buffer and TDM register names from this file.

## Risks And Edge Cases
Because the macros are absolute and not relative BAR offsets, using them directly with `readl(base + macro)` without the subtraction helper would access the wrong address. The file contains many registers unused by the current Raven drivers; stale or incorrect definitions may go unnoticed without hardware access.

## Test Signals
Build-time signal is successful compilation of all Raven drivers. Runtime signals are correct register side effects for external interrupt enable/status, I2S/BT ring-buffer programming, and linear position counters. Hardware register tracing can validate that helper subtraction maps macros to expected BAR-relative offsets.
