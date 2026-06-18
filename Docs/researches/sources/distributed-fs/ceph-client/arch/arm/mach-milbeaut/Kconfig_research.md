# sources/distributed-fs/ceph-client/arch/arm/mach-milbeaut/Kconfig

Purpose: Kconfig menu for Socionext Milbeaut ARMv7 platforms.

Important APIs/types/functions: Defines `ARCH_MILBEAUT` selecting ARM GIC, and `ARCH_MILBEAUT_M10V` selecting `ARM_ARCH_TIMER`, `MILBEAUT_TIMER`, `PINCTRL`, and `PINCTRL_MILBEAUT`.

Control flow: No runtime flow; the symbols gate machine, timer, GIC, and pinctrl support at build time.

State and persistence: No runtime state. Build configuration determines whether Milbeaut M10V timer/pinctrl/SMP-related code can be linked.

Dependencies and integration points: Integrates with ARM multi-v7, the ARM GIC, Milbeaut timer driver, and Milbeaut pinctrl driver.

Risks: The top-level symbol only selects GIC; M10V-specific timer/pinctrl support requires the child symbol. A partial configuration can compile a kernel that matches the architecture but lacks board-critical drivers.

Test signals: Build `ARCH_MILBEAUT` with and without `ARCH_MILBEAUT_M10V`, check selected timer/pinctrl symbols, and boot a Milbeaut EVB DT.
