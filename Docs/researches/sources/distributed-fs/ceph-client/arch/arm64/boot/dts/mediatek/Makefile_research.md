## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/mediatek/Makefile

### Purpose
This Kbuild fragment is the ARM64 MediaTek DTB and DTBO build manifest. It lists evaluation boards, phones, Chromebooks, routers, Genio platforms, Banana Pi/Radxa boards, and overlay-based composite DTB targets under `CONFIG_ARCH_MEDIATEK`.

### Important APIs, Types, And Functions
There are no C functions or types. The interface is the set of `dtb-$(CONFIG_ARCH_MEDIATEK)` entries, intermediate `*-dtbs :=` composite target definitions, and `DTC_FLAGS_* := -@` overlay-symbol flags. The file references 161 DTB/DTBO names and defines composite DTBs for Banana Pi BPI-R3/BPI-R4 and Radxa panel combinations.

### Control Flow
Kbuild appends direct DTB and DTBO targets when `CONFIG_ARCH_MEDIATEK` is enabled. Composite `*-dtbs` variables describe base-DTB plus overlay inputs; the corresponding `.dtb` targets trigger overlay composition. `DTC_FLAGS_* := -@` enables symbol generation required for overlays.

### State, Persistence, And Dependencies
The file has no runtime state. Persistent outputs are built DTBs/DTBOs and composed DTBs. Dependencies include the referenced DTS/DTSO files, Kbuild overlay support, `dtc` symbol generation, and `CONFIG_ARCH_MEDIATEK`.

### Integration Points
Integration points include the parent ARM64 DTS Makefile, MediaTek platform DTS files, overlay-aware boot flows, OpenWrt/router board packaging, ChromeOS-style board DTBs, and CI coverage through `dtbs` and `dtbs_check`.

### Risks
The main risks are overlay composition breakage, missing `-@` flags for bases that must accept overlays, stale DTB names, and accidental omission of a board from standard build artifacts. Because the file spans many SoC generations, edits can unintentionally affect unrelated products.

### Test Signals
Useful signals include `make ARCH=arm64 dtbs`, `dtbs_check`, verifying `.dtbo` and composed `.dtb` artifacts for BPI-R3/BPI-R4/Radxa combinations, and boot tests on representative MT2712, MT798x, MT818x, MT819x, MT83xx, and MT85xx hardware. Source reading signal: 182 lines; 130 `dtb-$(...)` entries; 161 DTB/DTBO references.
