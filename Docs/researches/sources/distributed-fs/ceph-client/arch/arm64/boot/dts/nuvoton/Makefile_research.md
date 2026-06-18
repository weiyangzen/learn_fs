# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/nuvoton/Makefile

## Purpose
This Makefile registers Nuvoton arm64 board DTBs for the MA35 and NPCM families.

## APIs, Types, And Functions
There are no runtime APIs. Kbuild consumes three `dtb-$(CONFIG_...)` assignments: two MA35D1 boards under `CONFIG_ARCH_MA35` and the `nuvoton-npcm845-evb.dtb` under `CONFIG_ARCH_NPCM`.

## Control Flow, State, And Persistence
Kbuild conditionally appends DTB targets based on the selected architecture config. The only persisted artifacts are built DTBs.

## Dependencies And Integration
The Makefile depends on the named DTS files and on architecture Kconfig symbols. It integrates with the arm64 DTS build target list.

## Risks And Test Signals
Risks are omitted boards, renamed DTS files, or incorrect Kconfig gating. Run `make ARCH=arm64 dtbs` with each architecture enabled and confirm all three DTB outputs are produced.
