# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/tesla/Makefile

## Purpose
This Makefile registers the Tesla FSD arm64 EVB DTB.

## APIs, Types, And Functions
It contains one `dtb-$(CONFIG_ARCH_TESLA_FSD)` entry for `fsd-evb.dtb`.

## Control Flow, State, And Persistence
Kbuild conditionally appends the DTB target based on the Tesla FSD architecture option. The output is a DTB artifact.

## Dependencies And Integration
The file depends on `fsd-evb.dts` and `CONFIG_ARCH_TESLA_FSD`. It integrates the board into the arm64 DTB build.

## Risks And Test Signals
Risks are stale source names or missing architecture gating. Build `dtbs` with Tesla FSD enabled and check for `fsd-evb.dtb`.
