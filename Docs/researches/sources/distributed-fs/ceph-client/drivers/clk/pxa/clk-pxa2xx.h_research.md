# sources/distributed-fs/ceph-client/drivers/clk/pxa/clk-pxa2xx.h

Purpose: Defines PXA2xx clock-register offsets and bit masks shared by PXA25x and PXA27x clock drivers.

Important APIs, types, and functions: Provides offsets for `CCCR`, `CCSR`, `CKEN`, and `OSCC`; masks and bit positions for CCCR/CCSR frequency fields; CKEN bit assignments for peripherals; and OSCC 32.768 kHz oscillator bits.

Control flow: SoC-specific PXA clock files include this header to decode frequency registers and build CKEN descriptors with `CKEN_*` bit constants.

State and persistence: No state. It describes hardware register layout.

Dependencies and integration points: Private to PXA2xx clock support. Must match the processor reference manuals and the PXA dt-binding clock IDs used by higher-level code.

Risks: Several CKEN bit numbers are aliases across SoC variants, for example USB host/NSSP and SSP/SSP2. Callers must use the correct symbol for their SoC. Wrong masks here directly break rate computation or peripheral gating.

Test signals: Register readback tests for CCCR/CCSR fields should match computed rates. Peripheral enable tests should confirm the expected CKEN bits toggle for each PXA25x/PXA27x device.
