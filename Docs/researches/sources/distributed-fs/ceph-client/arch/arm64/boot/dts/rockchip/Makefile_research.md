# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/rockchip/Makefile

## Purpose
This Makefile registers Rockchip arm64 board DTBs and overlay compositions under `CONFIG_ARCH_ROCKCHIP`.

## APIs, Types, And Functions
It contains 247 `dtb-$(CONFIG_ARCH_ROCKCHIP)` lines, 20 `*-dtbs :=` composition rules, 44 `.dtbo` mentions, and 297 `.dtb` mentions. A comment notes symbol generation behavior for base DTBs used with overlay composition.

## Control Flow, State, And Persistence
Kbuild assembles direct DTB targets and composed DTB targets from base DTBs plus overlays. There is no runtime state in the Makefile. Built DTBs are persistent boot artifacts.

## Dependencies And Integration
The file depends on the named Rockchip DTS/DTBO files, `CONFIG_ARCH_ROCKCHIP`, and Kbuild overlay support. It integrates board DTS additions into the global arm64 build.

## Risks And Test Signals
Risks include missing overlay symbol support, stale composed target names, and accidental omission of a board from `dtbs`. Test with `make ARCH=arm64 dtbs`, inspect outputs for composed targets, and run `dtbs_check` for changed boards.
