# sources/distributed-fs/ceph-client/arch/mips/bcm63xx/boards/Kconfig

Purpose: Kconfig menu for `sources/distributed-fs/ceph-client/arch/mips/bcm63xx/boards/Kconfig`, exposing architecture configuration options for this MIPS platform area.

Important APIs and functions: declarative symbols include BOARD_BCM963XX. Notable selected dependencies include SSB.

Control flow: `menuconfig` or defconfig resolution evaluates these symbols before build. Selected CPU/board/feature options control which source files, CPU support, and platform drivers Kbuild includes.

State and persistence: no runtime state. Values persist only in kernel `.config` and derived build artifacts.

Dependencies and integration points: integrates with top-level MIPS Kconfig, CPU capability symbols, board support choices, and Makefile `obj-$()` rules.

Risks and test signals: wrong dependencies can produce invalid builds or omit required CPU/platform support. Test by building representative defconfigs, checking symbol dependencies with `scripts/config` or `menuconfig`, and confirming selected objects match intended hardware.
