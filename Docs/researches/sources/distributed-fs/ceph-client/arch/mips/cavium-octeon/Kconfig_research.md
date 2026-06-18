# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/Kconfig

Purpose: Kconfig menu for `sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/Kconfig`, exposing architecture configuration options for this MIPS platform area.

Important APIs and functions: declarative symbols include CAVIUM_CN63XXP1, CAVIUM_OCTEON_CVMSEG_SIZE, CAVIUM_OCTEON_LOCK_L2, CAVIUM_OCTEON_LOCK_L2_TLB, CAVIUM_OCTEON_LOCK_L2_EXCEPTION, CAVIUM_OCTEON_LOCK_L2_LOW_LEVEL_INTERRUPT, CAVIUM_OCTEON_LOCK_L2_INTERRUPT, CAVIUM_OCTEON_LOCK_L2_MEMCPY, CAVIUM_RESERVE32, OCTEON_ILM. Notable selected dependencies include none.

Control flow: `menuconfig` or defconfig resolution evaluates these symbols before build. Selected CPU/board/feature options control which source files, CPU support, and platform drivers Kbuild includes.

State and persistence: no runtime state. Values persist only in kernel `.config` and derived build artifacts.

Dependencies and integration points: integrates with top-level MIPS Kconfig, CPU capability symbols, board support choices, and Makefile `obj-$()` rules.

Risks and test signals: wrong dependencies can produce invalid builds or omit required CPU/platform support. Test by building representative defconfigs, checking symbol dependencies with `scripts/config` or `menuconfig`, and confirming selected objects match intended hardware.
