# sources/distributed-fs/ceph-client/arch/parisc/include/asm/serial.h

Purpose: defines PA-RISC default serial baud-base constant.

Important APIs/types/functions: exports `BASE_BAUD` as `1843200 / 16`.

Control flow: serial drivers use this constant when initializing UART port timing unless platform data overrides it.

State and persistence: no software state; UART divisor programming persists in device registers. Dependencies and integration: consumed by 8250/serial platform setup.

Risks and test signals: wrong baud base causes console garbling. Test early and runtime serial console at standard baud rates.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
