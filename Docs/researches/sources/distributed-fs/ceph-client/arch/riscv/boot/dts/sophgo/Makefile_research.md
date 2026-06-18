<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/dts/sophgo/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/boot/dts/sophgo/Makefile

## Purpose
Adds cv1800b-milkv-duo, cv1812h-huashan-pi, sg2002-licheerv-nano-b, sg2042-milkv-pioneer, sg2042-evb-v1, sg2042-evb-v2, sg2044-sophgo-srd3-10 RISC-V devicetree blobs to the kernel DTB build when `CONFIG_ARCH_SOPHGO` is enabled.

## Important APIs, Types, And Functions
The file exports `dtb-$(CONFIG_ARCH_SOPHGO)` entries. The important API surface is the DTB target list consumed by kbuild, not C symbols.

## Control Flow
During a DTB build, kbuild evaluates the SoC Kconfig symbol and appends the listed .dtb targets to the vendor directory's build. There is no runtime control flow in this file.

## State And Persistence
State is build-time only: the enabled target list determines generated DTB artifacts under the object tree. No persistent runtime state is created.

## Dependencies And Integration Points
Depends on the arch/riscv DTS build traversal, the matching SoC Kconfig symbol, dtc, and the named .dts/.dtsi files in the same vendor directory. Integration is through Linux kbuild's dtb-y aggregation and install targets.

## Risks And Edge Cases
A missing, renamed, or stale DTS target breaks `make dtbs` for the affected platform. Incorrect Kconfig gating can omit a supported board or build an irrelevant board for another SoC family.

## Test Signals
Useful signals are `make ARCH=riscv dtbs`, per-board dtc warnings, and checking that enabling the vendor SoC option produces the expected DTB names.

Source read size: 8 lines, 397 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/dts/sophgo/Makefile -->
