# sources/distributed-fs/ceph-client/arch/mips/bmips/Kconfig

Purpose: Kconfig menu for `sources/distributed-fs/ceph-client/arch/mips/bmips/Kconfig`, exposing architecture configuration options for this MIPS platform area.

Important APIs and functions: declarative symbols include DT_NONE, DT_BCM93384WVG, DT_BCM93384WVG_VIPER, DT_BCM96368MVWG, DT_BCM9EJTAGPRB, DT_BCM97125CBMB, DT_BCM97346DBSMB, DT_BCM97358SVMB, DT_BCM97360SVMB, DT_BCM97362SVMB, DT_BCM97420C, DT_BCM97425SVMB, DT_BCM97435SVMB, DT_COMTREND_VR3032U, DT_NETGEAR_CVG834G, DT_SFR_NEUFBOX4_SERCOMM, DT_SFR_NEUFBOX6_SERCOMM. Notable selected dependencies include BUILTIN_DTB.

Control flow: `menuconfig` or defconfig resolution evaluates these symbols before build. Selected CPU/board/feature options control which source files, CPU support, and platform drivers Kbuild includes.

State and persistence: no runtime state. Values persist only in kernel `.config` and derived build artifacts.

Dependencies and integration points: integrates with top-level MIPS Kconfig, CPU capability symbols, board support choices, and Makefile `obj-$()` rules.

Risks and test signals: wrong dependencies can produce invalid builds or omit required CPU/platform support. Test by building representative defconfigs, checking symbol dependencies with `scripts/config` or `menuconfig`, and confirming selected objects match intended hardware.
