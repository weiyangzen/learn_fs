# sources/distributed-fs/ceph-client/arch/xtensa/platforms/xtfpga/include/platform/serial.h

Purpose: Provides XTFPGA serial base baud derived from the FPGA clock-frequency register.

Important APIs, types, and functions: Includes `platform/hardware.h` and defines `BASE_BAUD (*(long *)XTFPGA_CLKFRQ_VADDR / 16)`.

Control flow: Header-only; consumers read the memory-mapped clock register at runtime when evaluating `BASE_BAUD`.

State and persistence: Reads FPGA register state; does not write state.

Dependencies and integration: XTFPGA hardware clock register, generic serial/8250 code, and KIO mapping for the FPGA register virtual address.

Risks: Direct volatile-less pointer dereference may be sensitive to compiler assumptions; a bad or unmapped clock register breaks baud calculation; value changes at runtime would affect computed baud.

Test signals: Serial console baud correctness on XTFPGA, clock register accessibility early in boot, and comparison with board oscillator/FPGA-reported frequency.
