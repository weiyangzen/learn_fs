## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/dcr-regs.h

Purpose: collects common fixed and indirect DCR/SDR/CPR register numbers and bit definitions for IBM/AMCC 4xx processors.

Important APIs/types/functions: defines DCR address/data register pairs for CPR0 and SDR0, SDR fields for Ethernet/UART/reset, SRAM controller register offsets and bits, L2 cache controller offsets and fields, I2O/DMA registers, and memory queue bit positions.

Control flow: constants only. Drivers and platform code combine these offsets with DCR accessors from `dcr-native.h`.

State and persistence: no local state. Constants name persistent SoC control registers that affect clocks, reset, SRAM, L2 cache, Ethernet, and DMA behavior.

Dependencies and integration: integrates with DCR access macros and 4xx platform/device code. Many offsets intentionally exclude a base address that comes from the device tree.

Risks and test signals: wrong register numbers can reset or reconfigure unrelated hardware. Base-relative comments must be honored by callers. Test signals include 4xx board boot, Ethernet clock setup, SRAM/L2 cache init, I2O/DMA probe, and device-tree DCR resource validation.
