# sources/distributed-fs/ceph-client/arch/loongarch/boot/dts/Makefile

## Purpose

`Makefile` is the LoongArch boot devicetree Makefile. In this snapshot it is a placeholder with SPDX metadata and no DTB targets. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

There are no local build targets; the file preserves the directory hook for future board DTBs. Concrete declarations observed in the file: Build/script rules: `dtb-y = loongson-2k0500-ref.dtb loongson-2k1000-ref.dtb loongson-2k2000-ref.dtb`.

## Control Flow, State, And Persistence

Build-time only; it is reached from the boot build when DTB targets exist.

## Dependencies And Integration Points

It integrates with `KBUILD_DTBS := dtbs` in the architecture Makefile and the boot subtree.

## Risks And Test Signals

Risks are silent absence of expected DTB targets for DT-based boards. Test signals are `make ARCH=loongarch dtbs` and manifest checks for supported boards.
 A local static signal for this file is that it has 4 lines and 121 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
