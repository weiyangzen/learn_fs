# sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/Makefile

## Purpose
`52xx/Makefile` maps MPC52xx Kconfig symbols to common and board-specific object files.

## Important APIs, Types, and Functions
It always builds `mpc52xx_pic.o`, `mpc52xx_common.o`, and `mpc52xx_gpt.o`. PCI adds `mpc52xx_pci.o`. Board options add `mpc5200_simple.o`, `efika.o`, `lite5200.o`, and `media5200.o`. PM adds generic sleep/PM objects, and Lite5200 PM adds board-specific sleep/PM objects.

## Control Flow, State, and Persistence
This is build-time control only. Object inclusion determines which `define_machine()` instances and suspend implementations exist in the final kernel.

## Dependencies and Integration Points
It integrates Kconfig symbols with the PowerPC platform build and makes GPT/PIC/common code baseline for every MPC52xx build.

## Risks and Test Signals
Risks are incorrect object gating, especially PM object combinations and always-on GPT driver inclusion. Test signals are allyesconfig/allmodconfig-style builds and targeted builds for simple, Efika, Lite5200, and Media5200.
