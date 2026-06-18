# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/keylargo.h

Purpose: Defines register offsets and feature-control/GPIO bit masks for Apple KeyLargo, Pangea, Intrepid, K2, and Shasta I/O controller families.

Important APIs, types, and functions: Provides offsets for MBCR/FCR/GPIO registers, GPIO lines for modem/sound/FireWire/timebase/Ethernet/CPU reset/PMU/media bay/AirPort, extensive feature bits for serial, IrDA, USB, audio/I2S, IDE, cardslot, MPIC, PLL/clock control, K2 GMAC/SATA/FireWire/UATA, and Shasta I2S. No functions are declared.

Control flow: Platform feature code reads/modifies controller registers using these constants to enable clocks, release resets, configure wake sources, and power subdevices.

State and persistence: State is controller MMIO register content and board wiring. Header has no runtime state.

Dependencies and integration points: Integrates old PowerMac feature control, MacIO, media bay, PMU, CPU bringup/reset, and suspend/resume paths.

Risks: Several bit positions are chip-revision-specific or shared under different names. Wrong masks can stop clocks, hold devices in reset, or break wakeup. One typo-like constant (`KEYLARGO_GPIO_OUTOUT_DATA`) is part of existing API spelling.

Test signals: Boot on KeyLargo/Pangea/Intrepid/K2/Shasta systems, USB/audio/IDE/SATA/GMAC enablement, GPIO read/write, CPU reset lines, timebase enable, and suspend wake-source configuration.
