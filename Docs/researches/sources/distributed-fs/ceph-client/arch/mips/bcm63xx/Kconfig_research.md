# sources/distributed-fs/ceph-client/arch/mips/bcm63xx/Kconfig

Purpose: Kconfig menu for `sources/distributed-fs/ceph-client/arch/mips/bcm63xx/Kconfig`, exposing architecture configuration options for this MIPS platform area.

Important APIs and functions: declarative symbols include BCM63XX_CPU_3368, BCM63XX_CPU_6328, BCM63XX_CPU_6338, BCM63XX_CPU_6345, BCM63XX_CPU_6348, BCM63XX_CPU_6358, BCM63XX_CPU_6362, BCM63XX_CPU_6368. Notable selected dependencies include SYS_HAS_CPU_BMIPS4350, HAVE_PCI, SYS_HAS_CPU_BMIPS32_3300.

Control flow: `menuconfig` or defconfig resolution evaluates these symbols before build. Selected CPU/board/feature options control which source files, CPU support, and platform drivers Kbuild includes.

State and persistence: no runtime state. Values persist only in kernel `.config` and derived build artifacts.

Dependencies and integration points: integrates with top-level MIPS Kconfig, CPU capability symbols, board support choices, and Makefile `obj-$()` rules.

Risks and test signals: wrong dependencies can produce invalid builds or omit required CPU/platform support. Test by building representative defconfigs, checking symbol dependencies with `scripts/config` or `menuconfig`, and confirming selected objects match intended hardware.
