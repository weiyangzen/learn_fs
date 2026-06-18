# subset-b-000668 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/amlogic/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/amlogic/Makefile

### Purpose
This Makefile selects Amlogic/Meson ARM64 device-tree blobs for the kernel DT build. It contributes 108 DTB/DTBO references under `CONFIG_ARCH_MESON`, covering newer `amlogic-a4/a5/c3/s6/s7/t7` boards and established Meson A1, AXG, G12, GXBB/GXL/GXM, S4, and SM1 boards.

### Important APIs, Types, And Functions
The public surface is Kbuild data: repeated `dtb-$(CONFIG_ARCH_MESON) += ...` assignments plus four composite `*-dtbs := base.dtb overlay.dtbo` definitions. There are no C functions or runtime types. The build contract is the exact DTB target names and overlay composition variables.

### Control Flow
Kbuild includes this file while descending through `arch/arm64/boot/dts`. If `CONFIG_ARCH_MESON` is enabled, each listed target is queued for DTC compilation. For composite targets such as `meson-g12a-fbx8am-brcm`, Kbuild first builds the base DTB and overlay DTBO, then emits the named composite DTB.

### State, Persistence, And Dependencies
State is build-system state only: generated `.dtb` and `.dtbo` artifacts in the kernel build output. It depends on matching `.dts`/`.dtso` source files in the same directory, the top-level arm64 DT Makefiles, DTC, and Kconfig selection of `CONFIG_ARCH_MESON`.

### Integration Points
The generated blobs are consumed by boot firmware, bootloaders, and test infrastructure for Amlogic boards. Reset binding headers in this directory are included by DTS files that describe reset-controller cells for newer Amlogic SoCs.

### Risks
Target names must match source filenames exactly; stale entries break `make dtbs`. Composite overlay targets are sensitive to overlay symbol support and base/overlay compatibility. A broad `CONFIG_ARCH_MESON` target set means a single bad board DTS can break all Meson DT builds.

### Test Signals
Run `make ARCH=arm64 dtbs` with `CONFIG_ARCH_MESON=y`, and separately build the composite overlay targets. DTC warnings, missing-source errors, and boot smoke tests on representative Meson boards are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/amlogic/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/amlogic/amlogic-a4-reset.h -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/amlogic/amlogic-a4-reset.h

### Purpose
This header defines Amlogic A4 reset-controller IDs for device-tree `resets` cells. It maps named peripherals and bus bridges onto sparse numeric reset lines across RESET0 through RESET5.

### Important APIs, Types, And Functions
The API is 48 `RESET_*` macros, including USB, USB PHY, audio, DDR, video output, Ethernet, MMC arbitration, IR, SPI, ADC, watchdog, PWM, UART, I2C, SD/eMMC, and AO/main/audio NIC bridge resets. There are no functions or data structures; the include guard is `__DTS_AMLOGIC_A4_RESET_H`.

### Control Flow
There is no runtime control flow in the header. DTS preprocessing substitutes symbolic reset names with integer IDs, and the reset-controller driver later interprets those IDs when kernel consumers request reset assertion or deassertion.

### State, Persistence, And Dependencies
The header has no persistent state. The numeric values encode hardware reset-line positions and depend on the A4 reset-controller binding and driver using the same ID layout.

### Integration Points
A4 board and SoC DTSI files include this header for `resets = <&reset RESET_...>` references. Downstream drivers for USB, audio, Ethernet, MMC, serial, I2C, PWM, and bridge fabrics indirectly depend on these constants resolving to the proper hardware lines.

### Risks
Sparse numbering leaves reserved holes; adding a macro in the wrong slot can reset an unrelated block. Similar macro names across A4/A5/T7 are not interchangeable, so includes must match the SoC-specific compatible.

### Test Signals
Compile all A4 DTBs with `make ARCH=arm64 dtbs`; DTC catches unknown macro references. Hardware validation should exercise each consumer through probe, suspend/resume, and reset recovery paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/amlogic/amlogic-a4-reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/amlogic/amlogic-a5-reset.h -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/amlogic/amlogic-a5-reset.h

### Purpose
This header provides Amlogic A5 reset IDs for device-tree reset consumers. It is close to the A4 map but adds A5-specific DSP, NNA, RTC, SPI flash, and UART/I2C slave reset lines.

### Important APIs, Types, And Functions
The exported surface is 51 `RESET_*` macros under `__DTS_AMLOGIC_A5_RESET_H`. Important constants include `RESET_DSPA_DEBUG`, `RESET_DSPA`, `RESET_NNA`, `RESET_ABUS_ARB`, `RESET_SPIFC`, `RESET_RTC`, `RESET_UART_C`, `RESET_I2C_S_A`, and A5-specific bridge resets such as `RESET_BRG_AO_NIC_DSPA` and `RESET_BRG_NIC_NNA`.

### Control Flow
DTS preprocessing expands these macros into integer reset cells. Runtime sequencing is handled by Linux reset consumers and the Amlogic reset controller, not by this header.

### State, Persistence, And Dependencies
There is no stored state. The numbers are ABI-like binding constants and must stay aligned with the A5 reset controller's register/bit layout and DTS includes.

### Integration Points
A5 DTSI files use the constants to wire device nodes to reset-controller lines. The constants integrate with peripheral drivers for USB, DSP/NNA, Ethernet, SD/eMMC, UART, I2C, SPI, watchdog, and bus fabric.

### Risks
A4 and A5 share many macro names but differ in some line assignments and available blocks. Copying a DTS include from the wrong SoC can silently target the wrong reset. The comment around UART offsets has a stale-looking reserved range label, so numeric values, not comments, must be treated as authoritative.

### Test Signals
Build A5 DTBs, validate reset references with `dtbs_check` where bindings are available, and confirm affected peripherals probe cleanly after cold boot, module reload, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/amlogic/amlogic-a5-reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/amlogic/amlogic-t7-reset.h -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/amlogic/amlogic-t7-reset.h

### Purpose
This header defines the larger Amlogic T7 reset ID namespace for DTS reset cells. It spans RESET0 through RESET6 and covers display, video, GPU, DSP, PCIe, camera, bus bridge, and peripheral reset lines.

### Important APIs, Types, And Functions
The API is 163 `RESET_*` macros under `__DTS_AMLOGIC_T7_RESET_H`. Notable groups include USB/U2/U3 resets, HDMI/eDP/MIPI/VDAC/VIU/VENC display resets, MALI/DOS/DSP/ANAKIN compute blocks, PCIe resets, Ethernet, SPI/SmartCard/RSA, UART/I2C/SD-eMMC, NoC/NIC bridges, and RESET6 pipeline/AMPIPE/AXI bridge lines up to ID 223.

### Control Flow
The header is compile-time data only. DTS files include it, C preprocessor emits integer cells, and the reset controller performs runtime assertions/deassertions when drivers request them.

### State, Persistence, And Dependencies
The constants encode hardware register bit positions and have no persistence beyond generated DTBs. Correctness depends on the T7 reset-controller binding, the SoC DTSI reset provider, and the reset controller driver using the same numbering scheme.

### Integration Points
T7 board DTBs in the Amlogic Makefile, including `amlogic-t7-a311d2-*`, can reference these constants. Driver integration is broad because display, video codec, GPU, PCIe, Ethernet, SPI, UART, I2C, SD/eMMC, watchdog, and fabric resets are all represented.

### Risks
The namespace is dense and hardware-facing; an off-by-one macro can reset the wrong display, PCIe, memory, or bridge path. Some macros represent fabric or pipeline resets, where incorrect use can affect multiple consumers rather than one leaf device.

### Test Signals
Build T7 DTBs, run `dtbs_check`, then validate boot logs for reset-controller probe and peripheral resets. Display/video, PCIe, network, storage, and suspend/resume tests give the strongest coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/amlogic/amlogic-t7-reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/apm/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/apm/Makefile

### Purpose
This Makefile registers AppliedMicro X-Gene ARM64 board DTBs for the kernel build.

### Important APIs, Types, And Functions
It exports two Kbuild targets via `dtb-$(CONFIG_ARCH_XGENE)`: `apm-mustang.dtb` and `apm-merlin.dtb`. There are no functions, types, or stateful APIs.

### Control Flow
When `CONFIG_ARCH_XGENE` is enabled, arm64 DT Kbuild compiles both listed DTS files into DTBs during `make dtbs`.

### State, Persistence, And Dependencies
Generated DTBs are build artifacts. The file depends on matching DTS sources, the top-level arm64 DT build, and Kconfig selecting `CONFIG_ARCH_XGENE`.

### Integration Points
The outputs describe X-Gene platforms used by boot firmware and the Linux kernel at boot. They indirectly affect storage/network/filesystem behavior by describing platform buses, interrupts, and devices.

### Risks
The file is small; the main risk is stale target names or disabled coverage for older X-Gene boards.

### Test Signals
Run an arm64 `dtbs` build with `CONFIG_ARCH_XGENE=y` and boot-test the Mustang/Merlin DTBs if hardware or emulation is available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/apm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/apple/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/apple/Makefile

### Purpose
This Makefile enumerates Apple ARM64 device-tree blobs for many iPhone, iPad, and Apple Silicon Mac platforms. It contributes 92 DTB targets gated by `CONFIG_ARCH_APPLE`.

### Important APIs, Types, And Functions
The public surface is Kbuild target data: `dtb-$(CONFIG_ARCH_APPLE) += ...`. Targets cover SoC families such as `s5l8960x`, `t7000/t7001`, `s8000/s8001/s8003`, `t8010/t8011/t8012/t8015`, `t8103`, `t6000/t6001/t6002`, `t6020/t6021/t6022`, and `t8112`.

### Control Flow
Kbuild appends all listed Apple DTB targets when `CONFIG_ARCH_APPLE` is enabled. DTC compiles each matching DTS file; no runtime code is generated beyond DTB data consumed at boot.

### State, Persistence, And Dependencies
State is generated DTB build output. The Makefile depends on same-directory DTS/DTSI files, the arm64 DT build, DTC, and Apple platform Kconfig. Multi-die Apple DTS sources may also include `multi-die-cpp.h`.

### Integration Points
The generated DTBs are consumed by Apple boot flows and Linux platform drivers for Apple SoCs. They integrate with Apple-specific interrupt, power, PCIe, display, storage, and I/O controllers.

### Risks
Large board lists are vulnerable to filename drift and accidental omission of variants. Apple device identifiers are terse; swapping a board code can produce a valid DTB for the wrong hardware variant.

### Test Signals
Run `make ARCH=arm64 dtbs` with `CONFIG_ARCH_APPLE=y`, check DTC warnings, and boot-test representative phone/tablet/Mac DTBs. For multi-die platforms, ensure preprocessor-generated labels resolve as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/apple/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/apple/multi-die-cpp.h -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/apple/multi-die-cpp.h

### Purpose
This helper header supplies C preprocessor macros used by Apple `t600x` multi-die DTS files to generate die-specific node names and labels.

### Important APIs, Types, And Functions
The exported macros are `__stringify_1`, `__stringify`, `__concat_1`, `__concat`, `DIE_NODE(a)`, and `DIE_LABEL(a)`. `DIE_NODE(a)` token-pastes a caller token with `DIE`; `DIE_LABEL(a)` stringifies that pasted token. There are no runtime functions or structs.

### Control Flow
DTS preprocessing expands node/label macros before DTC parses the tree. The two-stage stringify/concat helpers ensure macro arguments expand before stringification or token pasting.

### State, Persistence, And Dependencies
The header has no state. It conditionally defines stringify/concat helpers only if they are not already provided, reducing conflicts with other DTS preprocessor helpers.

### Integration Points
Apple multi-die DTSI files use the macros to describe repeated die-local blocks without manually duplicating node and label names. The generated labels are then referenced by normal phandles.

### Risks
Token-pasting errors are hard to diagnose once expanded into DTS. The macros depend on a `DIE` macro or token context supplied by the including DTS file; missing or unexpected `DIE` values can create duplicate or invalid labels.

### Test Signals
Build Apple multi-die DTBs with preprocessor output inspection when needed. DTC duplicate-label, unresolved-phandle, and syntax errors are the key validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/apple/multi-die-cpp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/arm/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/arm/Makefile

### Purpose
This Makefile registers Arm reference, model, and development-platform DTBs for ARM64 builds.

### Important APIs, Types, And Functions
It exports 19 DTB targets under `CONFIG_ARCH_VEXPRESS`, including Foundation models, Juno variants, RTSM/FVP models, Corstone1000, Morello, and Zena CSS. The file is pure Kbuild metadata.

### Control Flow
When the Versatile Express architecture option is enabled, Kbuild compiles all listed model/platform DTS files during `make dtbs`.

### State, Persistence, And Dependencies
Generated DTBs are build artifacts. The file depends on same-directory DTS sources, DTC, and Kconfig selection of `CONFIG_ARCH_VEXPRESS`.

### Integration Points
These DTBs support Arm reference platforms used heavily for validation and CI. They integrate with generic Arm platform, PSCI, GIC, SCMI, and model-specific device descriptions.

### Risks
Because these DTBs are often used in CI and emulator flows, target breakage can block broad arm64 test coverage. Some variants encode subtle PSCI/GIC/SCMI differences that must not be collapsed accidentally.

### Test Signals
Build the DTBs with `CONFIG_ARCH_VEXPRESS=y`, run DTC/dt-schema checks, and boot smoke-test FVP/Juno/Corstone/Morello targets where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/arm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/axiado/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/axiado/Makefile

### Purpose
This Makefile adds the Axiado AX3000 evaluation-kit DTB to the arm64 DT build.

### Important APIs, Types, And Functions
The only build API is `dtb-$(CONFIG_ARCH_AXIADO) += ax3000-evk.dtb`.

### Control Flow
Kbuild includes `ax3000-evk.dtb` only when `CONFIG_ARCH_AXIADO` is enabled.

### State, Persistence, And Dependencies
State is the generated DTB artifact. The Makefile depends on `ax3000-evk.dts`, DTC, and Axiado Kconfig support.

### Integration Points
The DTB describes the AX3000 EVK for boot firmware and Linux platform drivers.

### Risks
The small file has low internal risk; the main failure mode is a missing or renamed DTS target.

### Test Signals
Build with `CONFIG_ARCH_AXIADO=y`, run DT schema checks, and boot-test the EVK DTB if hardware is available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/axiado/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/bitmain/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/bitmain/Makefile

### Purpose
This Makefile registers the Bitmain BM1880 Sophon Edge board DTB.

### Important APIs, Types, And Functions
Its single target is `dtb-$(CONFIG_ARCH_BITMAIN) += bm1880-sophon-edge.dtb`. It contains no runtime code.

### Control Flow
Kbuild compiles the Sophon Edge DTS into a DTB when `CONFIG_ARCH_BITMAIN` is set.

### State, Persistence, And Dependencies
The only persistent output is the generated build artifact. It depends on the DTS file, DTC, and Bitmain architecture Kconfig.

### Integration Points
The DTB feeds boot-time hardware discovery for the BM1880 platform and any drivers bound through its compatible strings.

### Risks
The SPDX line uses `GPL-2.0+`, so license scanners may distinguish it from the more common `GPL-2.0-only` spelling used elsewhere. Build risk is otherwise limited to target/source drift.

### Test Signals
Run the arm64 DTB build with `CONFIG_ARCH_BITMAIN=y` and check DTC/schema output for the board.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/bitmain/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/blaize/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/blaize/Makefile

### Purpose
This Makefile adds the Blaize BLZP1600 CB2 DTB to arm64 DT builds.

### Important APIs, Types, And Functions
The only exported build target is `dtb-$(CONFIG_ARCH_BLAIZE) += blaize-blzp1600-cb2.dtb`.

### Control Flow
Kbuild queues the DTB when the Blaize architecture option is enabled.

### State, Persistence, And Dependencies
Generated DTB output is the only state. The target depends on the same-named DTS file, DTC, and `CONFIG_ARCH_BLAIZE`.

### Integration Points
The DTB integrates platform hardware description with Linux driver probing on the BLZP1600 CB2 board.

### Risks
As with other one-target platform Makefiles, stale filenames and missing Kconfig coverage are the primary risks.

### Test Signals
Build with `CONFIG_ARCH_BLAIZE=y` and run DT schema validation for the board DTS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/blaize/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/broadcom/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/broadcom/Makefile

### Purpose
This parent Broadcom DT Makefile enables Raspberry Pi/Broadcom BCM283x/BCM271x DTBs and descends into Broadcom subfamilies.

### Important APIs, Types, And Functions
It sets global `DTC_FLAGS := -@` for overlay symbol generation, adds 11 `dtb-$(CONFIG_ARCH_BCM2835)` Raspberry Pi targets, and declares `subdir-y += bcmbca`, `northstar2`, and `stingray`.

### Control Flow
Kbuild applies the DTC symbol flag while building this directory, compiles BCM2835-family DTBs when configured, and always descends into the listed subdirectories so their own Kconfig-gated targets can participate.

### State, Persistence, And Dependencies
State is generated DTB output, including symbol metadata from `-@`. Dependencies include Raspberry Pi DTS files, subdirectory Makefiles, DTC overlay support, and Kconfig options for Broadcom platforms.

### Integration Points
The output feeds Raspberry Pi boot flows and Broadcom platform driver probing. Subdirectories integrate additional BCA, iProc Northstar2, and Stingray SoC families.

### Risks
The global `DTC_FLAGS := -@` affects all DTs in this directory; it is useful for overlays but can alter generated blob contents. Subdirectory recursion must be preserved or entire Broadcom families disappear from `make dtbs`.

### Test Signals
Build Broadcom DTBs with `CONFIG_ARCH_BCM2835`, `CONFIG_ARCH_BCMBCA`, and `CONFIG_ARCH_BCM_IPROC`; check that symbol-enabled blobs still pass DTC and dt-schema validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/broadcom/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/broadcom/bcmbca/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/broadcom/bcmbca/Makefile

### Purpose
This Makefile registers Broadcom BCA broadband/router platform DTBs.

### Important APIs, Types, And Functions
It contributes 13 DTB targets under `CONFIG_ARCH_BCMBCA`, including BCM4906/4908/4912 retail boards and BCM94908/94912/963158/96858/963146/96856/96813 reference platforms.

### Control Flow
When the BCA architecture option is enabled, Kbuild compiles all listed DTB targets.

### State, Persistence, And Dependencies
State is generated DTB artifacts. Dependencies are matching DTS files, the parent Broadcom Makefile recursion, DTC, and `CONFIG_ARCH_BCMBCA`.

### Integration Points
The DTBs describe router and broadband SoC boards for boot firmware and Linux networking/storage drivers.

### Risks
Retail-board names encode vendor/model variants; naming mistakes can select wrong flash, Ethernet, GPIO, or wireless-support descriptions. Broadcom platform variants often differ subtly in board wiring.

### Test Signals
Run `make ARCH=arm64 dtbs` with `CONFIG_ARCH_BCMBCA=y`, validate DTC warnings, and boot-test representative router/reference boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/broadcom/bcmbca/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/broadcom/northstar2/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/broadcom/northstar2/Makefile

### Purpose
This Makefile registers Broadcom Northstar2 iProc DTBs.

### Important APIs, Types, And Functions
It exports `ns2-svk.dtb` and `ns2-xmc.dtb` through `dtb-$(CONFIG_ARCH_BCM_IPROC)`.

### Control Flow
Kbuild builds both Northstar2 DTBs when the iProc architecture option is enabled and the parent Broadcom Makefile recurses into this directory.

### State, Persistence, And Dependencies
Generated DTBs are the only persistent outputs. Dependencies include matching DTS files, DTC, parent `subdir-y`, and `CONFIG_ARCH_BCM_IPROC`.

### Integration Points
The DTBs support Northstar2 SVK/XMC hardware and integrate with Broadcom iProc platform drivers.

### Risks
Shared `CONFIG_ARCH_BCM_IPROC` also gates Stingray targets, so coverage must include both subfamilies. Missing parent recursion would hide this file entirely.

### Test Signals
Build iProc DTBs and run schema checks for `ns2-svk` and `ns2-xmc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/broadcom/northstar2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/broadcom/stingray/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/broadcom/stingray/Makefile

### Purpose
This Makefile registers Broadcom Stingray iProc DTBs.

### Important APIs, Types, And Functions
It contributes three `CONFIG_ARCH_BCM_IPROC` targets: `bcm958742k.dtb`, `bcm958742t.dtb`, and `bcm958802a802x.dtb`.

### Control Flow
Kbuild compiles these targets when iProc support is enabled and the parent Broadcom Makefile descends into `stingray`.

### State, Persistence, And Dependencies
The file creates build artifacts only. It depends on same-directory DTS files, DTC, the parent `subdir-y` entry, and iProc Kconfig.

### Integration Points
The generated DTBs describe Stingray development/reference boards and feed Broadcom iProc driver probing at boot.

### Risks
The board names are similar and easy to mistype. Because Northstar2 and Stingray share the same Kconfig gate, CI should not assume one subdirectory covers the other.

### Test Signals
Build with `CONFIG_ARCH_BCM_IPROC=y`, inspect DTC/dt-schema output, and boot-test at least one Stingray board DTB.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/broadcom/stingray/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/bst/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/bst/Makefile

### Purpose
This Makefile adds the BST C1200 CDCU ADAS board DTB.

### Important APIs, Types, And Functions
The exported Kbuild target is `dtb-$(CONFIG_ARCH_BST) += bstc1200-cdcu1.0-adas_4c2g.dtb`.

### Control Flow
The DTB is compiled only when `CONFIG_ARCH_BST` is enabled.

### State, Persistence, And Dependencies
State is the generated DTB. The target depends on the matching DTS, DTC, and BST architecture Kconfig.

### Integration Points
The DTB describes the BST automotive/ADAS board for Linux boot and platform-driver matching.

### Risks
The filename includes punctuation and memory-size metadata, making accidental renames or shell/glob handling mistakes more likely than for simpler names.

### Test Signals
Build with `CONFIG_ARCH_BST=y` and run DTC/schema checks on the target.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/bst/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/cavium/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/cavium/Makefile

### Purpose
This Makefile registers the Cavium ThunderX 88xx DTB.

### Important APIs, Types, And Functions
It exports `dtb-$(CONFIG_ARCH_THUNDER) += thunder-88xx.dtb`.

### Control Flow
Kbuild compiles `thunder-88xx.dtb` when Thunder architecture support is configured.

### State, Persistence, And Dependencies
The only output is a generated DTB artifact. Dependencies are `thunder-88xx.dts`, DTC, and `CONFIG_ARCH_THUNDER`.

### Integration Points
The DTB supports ThunderX server-class ARM64 hardware and affects platform discovery for PCIe, network, storage, interrupt, and NUMA-adjacent resources.

### Risks
The target is single-board but server hardware has broad driver impact; stale DT data can surface as storage or network failures well above the DT layer.

### Test Signals
Build with `CONFIG_ARCH_THUNDER=y`, run DTC/schema checks, and boot-test with PCIe/network/storage enumeration where possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/cavium/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/cix/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/cix/Makefile

### Purpose
This Makefile registers CIX Sky1 platform DTBs for arm64 builds.

### Important APIs, Types, And Functions
It exports two targets under `CONFIG_ARCH_CIX`: `sky1-orion-o6.dtb` and `sky1-xcp.dtb`.

### Control Flow
Kbuild compiles both Sky1 DTBs when CIX architecture support is enabled.

### State, Persistence, And Dependencies
Generated DTBs are build output. The file depends on Sky1 DTS/DTSI sources, CIX binding headers such as `sky1-pinfunc.h` and `sky1-power.h`, DTC, and `CONFIG_ARCH_CIX`.

### Integration Points
The outputs integrate Sky1 board descriptions with pinctrl, power-domain, PCIe, display, media, NPU/GPU, and peripheral drivers.

### Risks
Sky1 support is relatively new; mismatches between DTS constants and drivers can break platform bring-up. Both board targets should be kept in sync with binding changes.

### Test Signals
Run `make ARCH=arm64 dtbs` with `CONFIG_ARCH_CIX=y`, schema-check Sky1 bindings, and verify boot/probe logs for power-domain and pinctrl consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/cix/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/cix/sky1-pinfunc.h -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/cix/sky1-pinfunc.h

### Purpose
This header defines CIX Sky1 pin-function constants for DTS pinctrl nodes. It maps each pad/function choice to an encoded value of `(pad_index << 8 | mux_function)`.

### Important APIs, Types, And Functions
The file exports 390 macros under `__CIX_SKY1_H`, mainly named `CIX_PAD_<pad>_FUNC_<function>`. It covers GPIO001-GPIO153 plus alternate functions for SFI I2C/I3C/SPI/GPIO, SPI, USB over-current/VBUS, UART, I2C, I2S, HDA, GMAC, PM GPIO, and other Sky1 pad groups.

### Control Flow
There is no runtime logic. DTS pinctrl properties use these macros; the preprocessor emits encoded integers that the Sky1 pinctrl driver decodes into pad index and mux selection.

### State, Persistence, And Dependencies
The header has no storage. The encoded values are binding constants and depend on the Sky1 pin controller driver and hardware register layout using the same pad numbering and mux values.

### Integration Points
Sky1 board DTS files include this header for pin groups used by serial, SPI, I2C/I3C, USB, audio, Ethernet, and GPIO consumers. It is a key integration layer between board wiring and the CIX pinctrl driver.

### Risks
The compact bit encoding makes pad-index or mux-value errors compile cleanly but configure the wrong pin function at runtime. Pads often have several valid functions, so duplicate-looking macros must not be normalized without checking the hardware manual.

### Test Signals
Build Sky1 DTBs, run dt-schema checks for pinctrl properties, and validate peripheral I/O on hardware. Pinmux debugfs output and failed driver probe due to missing pins are useful runtime signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/cix/sky1-pinfunc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/cix/sky1-power.h -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/cix/sky1-power.h

### Purpose
This header defines Sky1 power-domain IDs for device-tree power-domain references.

### Important APIs, Types, And Functions
It exports 22 domain macros from `SKY1_PD_AUDIO` through `SKY1_PD_GPU`, including PCIe controller/hub, multimedia hub and SMMU, DPU0-DPU4, VPU top/cores, NPU cores/top, ISP0, and GPU.

### Control Flow
DTS preprocessing converts symbolic `SKY1_PD_*` names into integer domain cells. Runtime sequencing is handled by the Sky1 power-domain provider and generic PM domain framework.

### State, Persistence, And Dependencies
No state is stored in the header. The numeric IDs are an ABI between DTS, firmware expectations noted by the comment about Rich OS macro flow, and the Sky1 power-domain driver.

### Integration Points
Sky1 DTS nodes use these IDs in `power-domains` properties for audio, PCIe, display, video, NPU, ISP, and GPU devices.

### Risks
Incorrect IDs can power-manage the wrong hardware island, causing probe failures, hangs, or data loss for active devices. The cross-OS comment implies external consumers may depend on stable values.

### Test Signals
Build Sky1 DTBs, run power-domain binding checks, and exercise runtime PM, suspend/resume, display/media/GPU/NPU workloads, and PCIe enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/cix/sky1-power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/Makefile

### Purpose
This Makefile registers Samsung Exynos ARM64 DTBs and recurses into Axis ARTPEC and Google GS101 subdirectories.

### Important APIs, Types, And Functions
It declares `subdir-y += axis` and `subdir-y += google`, then adds 19 `dtb-$(CONFIG_ARCH_EXYNOS)` targets covering Exynos2200, 5433, 7, 7870, 7885, 850, 8895, 9810, 990, ExynosAuto v9, and ExynosAuto v920 boards.

### Control Flow
Kbuild always descends into `axis` and `google`; this file's own Exynos DTBs build when `CONFIG_ARCH_EXYNOS` is enabled.

### State, Persistence, And Dependencies
State is generated DTB output. Dependencies include DTS sources, Exynos pinctrl headers, child Makefiles, DTC, and Exynos Kconfig.

### Integration Points
The DTBs drive boot-time hardware discovery for Samsung phones, boards, and automotive platforms. Child directories add Axis ARTPEC and Google Tensor/GS101 board support.

### Risks
Subdirectory recursion is important even though child targets have their own Kconfig gates. Exynos board naming often encodes product SKUs; wrong target names can produce valid DTBs for the wrong device variant.

### Test Signals
Build with `CONFIG_ARCH_EXYNOS=y` and `CONFIG_ARCH_ARTPEC=y`, run dt-schema validation, and boot-test representative mobile, board, auto, Axis, and GS101 DTBs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/axis/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/axis/Makefile

### Purpose
This Makefile registers Axis ARTPEC ARM64 DTBs under the Exynos DTS hierarchy.

### Important APIs, Types, And Functions
It exports two targets under `CONFIG_ARCH_ARTPEC`: `artpec8-grizzly.dtb` and `artpec9-alfred.dtb`.

### Control Flow
The parent Exynos Makefile descends into this directory, and Kbuild compiles both ARTPEC DTBs when `CONFIG_ARCH_ARTPEC` is enabled.

### State, Persistence, And Dependencies
Generated DTBs are the output. Dependencies include ARTPEC DTS files, `artpec-pinctrl.h`, DTC, and the ARTPEC Kconfig option.

### Integration Points
The DTBs describe Axis ARTPEC platforms and integrate Samsung-derived pinctrl constants with Axis board hardware.

### Risks
The directory sits under `exynos`, so parent recursion must remain intact. ARTPEC pinctrl constants differ from generic Exynos enough that using the wrong header can misconfigure pins.

### Test Signals
Build ARTPEC DTBs, run schema checks, and validate pinctrl/peripheral probing on grizzly/alfred hardware or CI fixtures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/axis/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/axis/artpec-pinctrl.h -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/axis/artpec-pinctrl.h

### Purpose
This header defines Axis ARTPEC pinctrl constants used by DTS pin configuration nodes.

### Important APIs, Types, And Functions
It exports 19 macros: pull values `ARTPEC_PIN_PULL_NONE/DOWN/UP`, pin functions `INPUT`, `OUTPUT`, `FUNC_2` through `FUNC_6`, `EINT`, alias `FUNC_F`, and ARTPEC drive-strength values `ARTPEC_PIN_DRV_SR1` through `SR6` encoded as `0x8` through `0xd`.

### Control Flow
DTS preprocessing substitutes these constants into pin configuration properties. The pinctrl driver consumes the resulting numeric values during boot and pin-state changes.

### State, Persistence, And Dependencies
The header has no state. Its values depend on the ARTPEC pinctrl binding and driver interpretation of pull, mux, external interrupt, and drive-strength fields.

### Integration Points
ARTPEC DTSI/board files include this header for pin groups. It integrates with the ARTPEC pinctrl driver and with peripherals that request pin states.

### Risks
The constants resemble Exynos values but ARTPEC drive strengths are separate. Reusing generic Exynos drive macros could produce incorrect electrical characteristics.

### Test Signals
Build ARTPEC DTBs, run pinctrl schema checks, and test GPIO, EINT, serial, storage, and high-speed pins on hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/axis/artpec-pinctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/exynos-pinctrl.h -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/exynos-pinctrl.h

### Purpose
This header provides Samsung Exynos DTS pinctrl constants for pull configuration, power-down behavior, drive strength, and mux function selection.

### Important APIs, Types, And Functions
It exports 49 macros under `__DTS_ARM64_SAMSUNG_EXYNOS_PINCTRL_H__`: pull values, power-down modes, drive-strength sets for Exynos5420-family, Exynos5433, Exynos7, Exynos7 FSYS1, Exynos850 HSI, and function values `INPUT`, `OUTPUT`, `FUNC_2` through `FUNC_6`, `EINT`, and alias `FUNC_F`.

### Control Flow
There is no C flow. DTS pinctrl states expand these macros into numeric cells; the Exynos pinctrl driver interprets them while applying default, sleep, or runtime pin states.

### State, Persistence, And Dependencies
The header stores no state. The values are hardware/binding constants and must match Exynos pinctrl driver tables and SoC-specific register encodings.

### Integration Points
Exynos DTSI and board files include this header for GPIO, external interrupt, storage, serial, audio, display, and other pin groups. It is part of the common include-time ABI for many Exynos platforms.

### Risks
Drive-strength encodings differ between SoCs and even blocks such as Exynos7 FSYS1 or Exynos850 HSI. Choosing the wrong macro can compile but yield signal-integrity or boot-device failures.

### Test Signals
Build Exynos DTBs, run dt-schema pinctrl checks, and exercise boot-critical pins, GPIO interrupts, suspend/resume pin states, and high-speed interfaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/exynos-pinctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/google/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/google/Makefile

### Purpose
This Makefile registers Google GS101/Tensor board DTBs under the Exynos hierarchy.

### Important APIs, Types, And Functions
It exports `gs101-oriole.dtb` and `gs101-raven.dtb` under `CONFIG_ARCH_EXYNOS`.

### Control Flow
The parent Exynos Makefile descends into this directory, and these DTBs are compiled when Exynos support is enabled.

### State, Persistence, And Dependencies
State is generated DTB output. Dependencies include GS101 DTS files, `gs101-pinctrl.h`, DTC, and `CONFIG_ARCH_EXYNOS`.

### Integration Points
The DTBs describe Pixel 6 family boards and integrate GS101-specific pinctrl values with Exynos-derived platform support.

### Risks
Both targets share SoC support but differ by board. Incorrect target mapping can produce a booting kernel with wrong board-level peripherals, regulators, or GPIOs.

### Test Signals
Build GS101 DTBs, run schema checks, and boot-test both oriole and raven variants with attention to pinctrl, storage, display, modem-adjacent, and power behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/google/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/google/gs101-pinctrl.h -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/google/gs101-pinctrl.h

### Purpose
This header defines GS101 pinctrl binding constants for Google Tensor/Pixel DTS files.

### Important APIs, Types, And Functions
It exports 17 macros: pull values, power-down modes, drive strengths in mA (`2_5`, `5`, `7_5`, `10`), and function constants for input, output, alternate functions 2/3, and external interrupt.

### Control Flow
DTS preprocessing expands constants in pin configuration states; the GS101/Exynos pinctrl driver applies the numeric values when selecting active or sleep pin states.

### State, Persistence, And Dependencies
The header is stateless. Values are part of the GS101 DTS binding contract and must match the driver and SoC register encodings.

### Integration Points
`gs101-oriole` and `gs101-raven` DTS files include this header for GPIO/peripheral pin states. It integrates Pixel board descriptions with the Exynos pinctrl subsystem.

### Risks
GS101 drive strength uses explicit mA-level names, unlike generic Exynos level names. Mixing headers or copying pin states across SoCs can produce incorrect electrical behavior.

### Test Signals
Build GS101 DTBs, run pinctrl schema checks, and validate GPIO interrupts, serial/storage/display-related pins, and suspend/resume pin states on both board variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/exynos/google/gs101-pinctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/Makefile

### Purpose
This large Makefile registers NXP/Freescale ARM64 DTBs and overlays for Layerscape, i.MX, and S32 platforms. It contributes 579 DTB/DTBO references across `CONFIG_ARCH_LAYERSCAPE`, `CONFIG_ARCH_MXC`, and `CONFIG_ARCH_S32`.

### Important APIs, Types, And Functions
The surface is Kbuild metadata: `dtb-$(CONFIG_...) += ...`, many composite `*-dtbs :=` or `+=` variables for base-plus-overlay builds, and target-specific `DTC_FLAGS_*`. Layerscape targets include LS1012/1028/1043/1046/1088/208x/LX216x; i.MX targets span i.MX8DX/DXL/DXP/MM/MN/MP/MQ/QM/QP/QXP/ULP, i.MX91/93/93W/943/95/952; S32 targets include S32G/S32N/S32V boards.

### Control Flow
Kbuild queues target lists according to each architecture Kconfig symbol. Composite variables define how generated DTBs combine a base `.dtb` and one or more `.dtbo` overlays. Target-specific `DTC_FLAGS_*` suppress known interrupt-map warnings or enable overlay symbol generation with `-@`.

### State, Persistence, And Dependencies
State is generated DTB/DTBO build output. Dependencies include hundreds of same-directory DTS/DTSO files, shared overlays such as PCIe endpoint and panel variants, DTC overlay support, dt-schema bindings, and the selected Kconfig families.

### Integration Points
These DTBs feed boot firmware and Linux platform probing for NXP networking, storage, PCIe, display, camera, audio, industrial, and automotive boards. Pin-function and AIPSTZ headers in this directory are included by DTS sources selected here.

### Risks
The file mixes base DTBs, raw DTBO targets, and composite DTBs; missing one entry can silently omit an overlay product. Some lines use `dtb-${CONFIG_ARCH_MXC}` instead of the more common `dtb-$(CONFIG_ARCH_MXC)`, which should be preserved or reviewed with Kbuild behavior in mind. Warning suppressions can hide real interrupt-map regressions if overused.

### Test Signals
Run `make ARCH=arm64 dtbs` for Layerscape, MXC, and S32 configs; run `dtbs_check`; explicitly build representative overlay composites for LS1028, LX2160, i.MX8MM/MN/MP/MQ/QM/QXP, i.MX91/93/95, and S32. Boot tests should cover network, storage, PCIe, display/camera overlays, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx8mm-pinfunc.h -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx8mm-pinfunc.h

### Purpose
This header defines i.MX8M Mini IOMUX and pad-control constants for DTS pinctrl states.

### Important APIs, Types, And Functions
It exports 649 macros under `__DTS_IMX8MM_PINFUNC_H`. Pad-control helpers include drive strength (`MX8MM_DSE_X1/X2/X4/X6`), slew rate, open drain, pull, hysteresis, pull enable, `MX8MM_SION`, and defaults such as `MX8MM_USDHC_DATA_DEFAULT` and `MX8MM_I2C_DEFAULT`. Function macros follow the tuple `<mux_reg conf_reg input_reg mux_mode input_val>`.

### Control Flow
DTS pinctrl entries expand macros into five-cell tuples consumed by the i.MX pinctrl driver. The driver writes mux, pad configuration, and select-input registers during boot and pin-state transitions.

### State, Persistence, And Dependencies
The header is stateless but encodes hardware register offsets and mux modes. It depends on the i.MX8MM IOMUXC binding and driver interpreting five-cell tuples and pad-control flags consistently.

### Integration Points
i.MX8MM DTS files in the Freescale Makefile include this header for GPIO, USDHC, ENET, ECSPI, SAI, NAND/QSPI, UART, I2C, PCIe clock request, watchdog, and clock pins.

### Risks
The tuple fields are positional; a wrong input-select value or mux mode compiles but breaks peripheral routing. Pad-control defaults combine multiple bits, so changes can affect signal integrity, pull behavior, and forced input behavior for I2C or storage.

### Test Signals
Build all i.MX8MM DTBs, run pinctrl schema checks, inspect generated DTS preprocessing for suspect tuples, and validate storage, Ethernet, serial/I2C/SPI, audio, PCIe clock request, and suspend/resume pin states on hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx8mm-pinfunc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx8mn-pinfunc.h -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx8mn-pinfunc.h

### Purpose
This header defines i.MX8M Nano IOMUX function tuples for DTS pinctrl states.

### Important APIs, Types, And Functions
It exports 632 macros under `__DTS_IMX8MN_PINFUNC_H`, using the same five-field tuple contract `<mux_reg conf_reg input_reg mux_mode input_val>`. Macro groups cover boot mode pins, GPIO1, ENET, NAND, SD1/SD2, SAI, ECSPI, UART, I2C, PWM, GPT, USB, and clock/root functions.

### Control Flow
The header participates only in DTS preprocessing. The i.MX pinctrl driver consumes expanded tuples and applies mux, pad configuration, and select-input settings at runtime.

### State, Persistence, And Dependencies
There is no mutable state. Numeric offsets and input values must match the i.MX8MN IOMUXC hardware manual, binding, and driver.

### Integration Points
i.MX8MN board DTS files include this header for pin groups used by storage, Ethernet, audio, serial, SPI, I2C, GPIO, USB, and low-power states. The Freescale Makefile selects many i.MX8MN boards and overlays that depend on these constants.

### Risks
The Nano and Mini headers look similar but are not identical; copying `MX8MM_*` tuples into `MX8MN_*` contexts can misroute signals. Select-input registers are especially error-prone because some alternate functions share mux modes but differ by input value.

### Test Signals
Build i.MX8MN DTBs, run dt-schema validation, and test storage boot, Ethernet, UART/I2C/SPI, audio, USB, and suspend/resume. Peripheral probe failures and pinctrl debugfs state are strong diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx8mn-pinfunc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx8mp-aipstz.h -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx8mp-aipstz.h

### Purpose
This header defines i.MX8M Plus AIPSTZ consumer types, permission flags, and master IDs for DTS access-protection configuration.

### Important APIs, Types, And Functions
It exports 17 macros under `__IMX8MP_AIPSTZ_H`: consumer types `IMX8MP_AIPSTZ_MASTER` and `IMX8MP_AIPSTZ_PERIPH`, master flags `MPL/MTW/MTR/MBW`, peripheral flags `TP/WP/SP/BW`, and master IDs for EDMA, Cortex-A53, SDMA2, SDMA3, HIFI4, and Cortex-M7. `SDMA2` and `SDMA3` intentionally both use ID 3 in this file.

### Control Flow
DTS preprocessing emits numeric cells for an AIPSTZ provider/consumer binding. Runtime enforcement is performed by the relevant i.MX platform or bus-protection driver that programs access-control registers.

### State, Persistence, And Dependencies
The header has no runtime state. The values define a binding contract with i.MX8MP AIPSTZ hardware and its driver/firmware expectations.

### Integration Points
i.MX8MP DTS files can include the header to describe access permissions for bus masters and peripherals, affecting DMA engines, CPU cluster, DSP, and Cortex-M7 interactions with protected regions.

### Risks
Permission bits are security-sensitive; overly broad flags can expose protected peripherals, while restrictive or wrong master IDs can break DMA, DSP, or M7 operation. The duplicate SDMA2/SDMA3 ID deserves careful validation against hardware documentation.

### Test Signals
Build i.MX8MP DTBs, run binding checks, and validate DMA, audio DSP, M7 remoteproc, and protected peripheral access. Security/regression tests should cover denied and allowed access paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/freescale/imx8mp-aipstz.h -->
