<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/big-endian.S -->
# sources/distributed-fs/ceph-client/arch/arm/boot/compressed/big-endian.S

## Purpose
This startup fragment switches capable ARM CPUs into big-endian mode for BE32 decompressor configurations.

## Important APIs, Types, and Functions
Assembly-visible symbols include none. Included source files are none. Embedded binary inputs are none.

## Control Flow
It reads CP15 control register c1, sets the big-endian bit, and writes the control register back in the `.start` section before the rest of decompressor startup proceeds.

## State and Persistence Behavior
State is register, cache/MMU, copied-memory, or linked-binary state during the boot wrapper/decompressor phase. It is not persistent storage, but it determines the exact payload bytes, CPU mode, early memory layout, and handoff arguments observed by the decompressed kernel.

## Dependencies and Integration Points
Dependencies include ARM assembler macros, `arch/arm/boot/compressed/Makefile`, linker scripts, binary payload generation, bootloader register ABI, CPU control registers, optional EFI/HYP paths, and shared ARM library assembly where included.

## Risks
Risks are executing on a CPU/configuration where CP15 endian switching is unavailable or already controlled by hardware design.

## Test Signals
Build BE32/CP15 configurations and boot under an emulator or board that supports the mode; verify early decompressor and kernel endianness.

Source read size: 14 lines, 329 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/big-endian.S -->
