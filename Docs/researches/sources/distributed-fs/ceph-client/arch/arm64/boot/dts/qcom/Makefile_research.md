# sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/Makefile

## Purpose
This Qualcomm arm64 DTS Makefile is a large target registry for Qualcomm phones, laptops, routers, development boards, automotive boards, and composed overlay products. It is guarded by `CONFIG_ARCH_QCOM`.

## APIs, Types, And Functions
The build API is Kbuild DTB target assignment. The file has 359 `dtb-$(CONFIG_ARCH_QCOM)` lines, 58 `*-dtbs :=` composition rules, 62 `.dtbo` mentions, and over 500 `.dtb` mentions. Composition rules combine a base DTB with one or more overlays, for example camera mezzanine, EL2, IFP, navigation, and vision mezzanine variants.

## Control Flow, State, And Persistence
Kbuild evaluates all target lists when Qualcomm architecture support is enabled. `*-dtbs := base.dtb overlay.dtbo` tells Kbuild to produce a combined DTB target from components. There is no runtime state in the Makefile, but the produced DTBs are persistent boot artifacts.

## Dependencies And Integration
The file depends on a broad set of Qualcomm DTS/DTSI/DTBO sources and Kbuild overlay-composition support. It integrates tightly with board bring-up because adding or removing a board normally requires a synchronized Makefile entry.

## Risks And Test Signals
The dominant risks are target omission, invalid composition order, stale overlay names, and unintended build coverage changes across hundreds of boards. Test signals include `make ARCH=arm64 dtbs`, `make ARCH=arm64 dtbs_check` for changed boards, and explicit verification that composed `.dtb` outputs are generated for overlay variants.
