<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mtmips-sysc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mtmips-sysc.h

Purpose: Defines clock IDs for older Ralink/MediaTek MIPS system controllers: RT2880, RT305X, RT3352, RT3883, RT5350, MT7620, and MT76X8 families.

Important APIs, types, and functions: Exports SoC-prefixed IDs such as `RT2880_CLK_*`, `RT305X_CLK_*`, `RT3352_CLK_*`, `RT3883_CLK_*`, `RT5350_CLK_*`, `MT7620_CLK_*`, and `MT76X8_CLK_*`. There are no structures or functions.

Control flow: No code executes. The compatible-specific sysc/clock driver selects the appropriate ID table and maps DT clock specifiers to fixed, gate, or derived clocks.

State and persistence: Numeric IDs are stable binding ABI for MIPS router/access-point DTBs. Runtime clock state lives in the sysc driver and hardware registers.

Dependencies and integration points: Used by Ralink/MTMIPS DTS files and drivers for UART, I2C, SPI, Ethernet, PCI, USB, watchdog, timers, MMC, PCM/I2S, and Wi-Fi MAC blocks.

Risks and test signals: Main risks are cross-family ID confusion and missing peripherals on board variants. Test by compiling affected DTBs, booting representative SoCs, checking sysc clock provider registration, and validating serial console, Ethernet, USB, PCI, Wi-Fi, and timer/watchdog operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mediatek,mtmips-sysc.h -->
