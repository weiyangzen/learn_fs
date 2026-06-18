# sources/distributed-fs/ceph-client/arch/powerpc/boot/cpm-serial.c

## Purpose
Boot-wrapper serial console driver for Freescale CPM1/CPM2 SMC/SCC UARTs, assuming firmware has already configured basic port parameters.

## Important APIs, Types, And Control Flow
Hardware structs model SMC/SCC registers, CPM parameter RAM, and buffer descriptors. `cpm_console_init()` detects compatible strings, selects CPM1/CPM2 command format and SMC/SCC enable/disable functions, maps registers via `virtual-reg` or translated `reg`, finds MURAM data space, places RX/TX buffer descriptors at the end of the first MURAM chunk, relocates CPM2 SMC parameter RAM if needed, and fills `serial_console_data` callbacks. `cpm_serial_open()` initializes parameter RAM and BDs, issues `INIT_RX_TX`, and enables the port. `putc`, `getc`, and `tstc` poll BD ownership bits with sync/eieio ordering.

## State, Dependencies, Risks, And Tests
State is global pointers to CPM registers, parameter RAM, BDs, command value, MURAM offsets, and selected function callbacks. Dependencies include boot-wrapper device-tree translation, MMIO endian accessors, and CPM-compatible DT properties. Risks include malformed MURAM/reg properties, CPM command busy-wait hangs, BD placement clobbering firmware data, cache/order bugs, and unsupported compatible strings. Test with CPM1 SMC, CPM2 SMC, and CPM2 SCC device trees, console input/output before decompression, relocated parameter RAM validation, and failure paths returning `-1`.
