<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-highlander/pinmux-r7785rp.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-highlander/pinmux-r7785rp.c

## Purpose
Minimal R7785RP board pinmux setup. highlander_plat_pinmux_setup requests the needed FPGA/GPIO pins for the SH7785 Highlander variant before device drivers depend on them.

## Important APIs, Types, and Functions
- functions: highlander_plat_pinmux_setup.
- integration hooks: gpio_request.

## Control Flow
- The file is invoked by board setup or initcall paths and translates fixed board registers/GPIOs into kernel subsystem callbacks.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- headers: linux/init.h, linux/gpio.h, cpu/sh7785.h, mach/highlander.h.
- Source-tree integration: mach-highlander; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- pinmux/GPIO conflicts can break unrelated peripherals because most requests ignore errors.

## Test Signals
- compile coverage plus boot-time subsystem probe messages are the available signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-highlander/pinmux-r7785rp.c -->
