# sources/distributed-fs/ceph-client/arch/xtensa/platforms/xtfpga/include/platform/hardware.h

Purpose: Defines XTFPGA/XTAVNET board interrupt assignments, device physical addresses, register virtual addresses, and device sizes.

Important APIs, types, and functions: `DUART16552_INTNUM`, `OETH_IRQ`, `C67X00_IRQ`, `DUART16552_PADDR`, `XTFPGA_FPGAREGS_VADDR`, `XTFPGA_CLKFRQ_VADDR`, `DIP_SWITCHES_VADDR`, `XTFPGA_SWRST_VADDR`, `OETH_*`, and `C67X00_*`.

Control flow: Header-only constants; conditional IRQ assignments differ for `CONFIG_XTENSA_MX`.

State and persistence: No runtime state, but constants refer to memory-mapped FPGA registers such as clock frequency, DIP switches, and reset.

Dependencies and integration: `asm/types.h`, core interrupt macros, serial baud calculation, board setup, OpenCores Ethernet, USB C67X00, and reset/clock code.

Risks: Hard-coded offsets assume a specific FPGA memory map; clock register is read directly through virtual address; MX vs non-MX interrupt mapping must match bitstream.

Test signals: XTFPGA boot, UART clock read, Ethernet/USB IRQ delivery, software reset register, and MX/non-MX configurations.
