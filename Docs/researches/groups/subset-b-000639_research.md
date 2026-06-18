# subset-b-000639 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/st/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/st/Makefile

## Purpose
Build manifest for STMicroelectronics, ST-Ericsson, SPEAr, Nomadik, U8500, STI, and STM32 ARM devicetree blobs and overlays. It maps SoC Kconfig selections to concrete `.dtb` and `.dtbo` outputs consumed by the ARM `dtbs` build.

## Important APIs/types/functions
- Kbuild variables: `dtb-$(CONFIG_ARCH_NOMADIK)`, `dtb-$(CONFIG_ARCH_SPEAR13XX)`, `dtb-$(CONFIG_ARCH_SPEAR3XX)`, `dtb-$(CONFIG_ARCH_SPEAR6XX)`, `dtb-$(CONFIG_ARCH_STI)`, `dtb-$(CONFIG_ARCH_STM32)`, and `dtb-$(CONFIG_ARCH_U8500)`.
- Overlay aggregation variables such as `stm32mp15xx-avenger96-overlay-...-dtbs` pair a base board `.dtb` with one `.dtbo`.
- Build products include classic board DTBs and overlay DTBs/DTBOs for STM32MP13/15 expansion boards, LCD panels, CAN, EEPROM, camera, Wi-Fi, and Raspberry Pi display adapters.

## Control flow
There is no runtime control flow. Kbuild expands the active `dtb-*` lists from enabled configuration symbols; composite `*-dtbs` targets cause `scripts/Makefile.lib` to build merged overlay targets from the listed base and overlay inputs. `make dtbs` or `make ARCH=arm dtbs` is the entry point.

## State and persistence behavior
The file persists the source-to-binary DT build contract. It stores no kernel runtime state, but it decides which DTBs enter build artifacts, install trees, and CI output. Overlay pairing names are durable target names and must remain aligned with corresponding `.dts` and `.dtso` files.

## Dependencies and integration points
Depends on the ARM devicetree Kbuild infrastructure, DTC overlay support, SoC Kconfig symbols, and matching source files in the same directory. Integrates with board firmware/bootloaders that select the generated DTB/DTBO names.

## Risks and edge cases
Missing or misspelled DTB names fail the `dtbs` build. Incorrect overlay pairings can produce a syntactically valid DTB with resources for the wrong board. Composite overlay targets require the base and overlay names to remain synchronized; stale targets are easy to leave behind when board DTS files are renamed.

## Test signals
Run `make ARCH=arm dtbs` for relevant `ARCH_STM32`, `ARCH_U8500`, `ARCH_STI`, `ARCH_SPEAR*`, and `ARCH_NOMADIK` configurations. `make ARCH=arm dtbs_check` should validate the resulting DTBs against binding schemas, especially STM32MP overlay combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/st/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/st/st-pincfg.h -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/st/st-pincfg.h

## Purpose
Devicetree include header defining ST pin-control bit encodings for alternate functions, direction, pull-up/open-drain behavior, clock retiming, and retime clock selection. Board DTS files include it to express pin mux and electrical configuration in readable macros.

## Important APIs/types/functions
- Alternate function constants: `ALT1` through `ALT7`.
- Direction and electrical flags: `OE`, `PU`, `OD`, `IN`, `IN_PU`, `OUT`, `BIDIR`, `BIDIR_PU`.
- Retime/clock flags: `RT`, `INVERTCLK`, `CLKNOTDATA`, `DOUBLE_EDGE`, `CLK_A` through `CLK_D`, `BYPASS`, `SE_NICLK_IO`, `SE_ICLK_IO`, `DE_IO`, `ICLK`, and `NICLK`.

## Control flow
No executable flow. The C preprocessor substitutes macros into DTS pin configuration cells before DTC encodes them into the DTB.

## State and persistence behavior
The header defines a persistent ABI between DTS files and ST pinctrl drivers: the encoded bit positions become values in built DTBs. Changing bit values would alter board pin behavior at boot.

## Dependencies and integration points
Used by ST pinctrl DTS nodes and consumed by the corresponding kernel pinctrl driver that interprets these bitfields. It depends only on preprocessor inclusion and the shared bit layout expected by firmware/kernel pin configuration code.

## Risks and edge cases
Bit overlap or value drift can silently misconfigure pins. The `CLK_A` value is zero, so absence of a clock-select macro may be indistinguishable from selecting clock A. User-friendly direction macros combine electrical flags but do not validate SoC-specific pin capabilities.

## Test signals
Compile all ST DTBs with `make ARCH=arm dtbs`; run `dtbs_check` against ST pinctrl bindings; boot affected boards and verify muxed peripherals, pull-ups, bidirectional buses, and retimed clock/data pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/st/st-pincfg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/sunplus/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/sunplus/Makefile

## Purpose
Kbuild manifest for Sunplus SP7021 ARM devicetree output.

## Important APIs/types/functions
- `dtb-$(CONFIG_SOC_SP7021)` appends `sunplus-sp7021-demo-v3.dtb`.

## Control flow
Kbuild includes the DTB when `CONFIG_SOC_SP7021` is enabled.

## State and persistence behavior
No runtime state. The persistent contract is the output DTB name used by installers, CI, and bootloaders.

## Dependencies and integration points
Depends on `sunplus-sp7021-demo-v3.dts`, the Sunplus SoC Kconfig symbol, and ARM DTC build rules.

## Risks and edge cases
The DTB is listed twice under the same config in this file, which can cause duplicate build-list entries and should be watched in build output. A renamed DTS must update both lines.

## Test signals
Run `make ARCH=arm dtbs` with `CONFIG_SOC_SP7021=y` and check for duplicate-target warnings; run `dtbs_check` for the SP7021 board.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/sunplus/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/synaptics/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/synaptics/Makefile

## Purpose
Kbuild manifest for Synaptics/Marvell Berlin ARM board DTBs.

## Important APIs/types/functions
- `dtb-$(CONFIG_ARCH_BERLIN)` lists Berlin2, Berlin2CD, and Berlin2Q boards: Sony NSZ-GS7, Google Chromecast, Valve Steam Link, and Marvell DMP.

## Control flow
Kbuild appends the listed DTBs when `CONFIG_ARCH_BERLIN` is enabled.

## State and persistence behavior
No runtime state. It persists the set of Berlin board DTB targets shipped by the kernel build.

## Dependencies and integration points
Depends on matching DTS files and Berlin SoC Kconfig. Generated DTBs integrate with Berlin bootloaders and `dtbs_check`.

## Risks and edge cases
Board name changes or source deletion break the DTB build. Missing entries mean a board DTS can exist but not be generated by normal `dtbs`.

## Test signals
Run `make ARCH=arm dtbs` for `ARCH_BERLIN`; run `make ARCH=arm dtbs_check` on Berlin boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/synaptics/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/ti/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/ti/Makefile

## Purpose
Top-level TI ARM devicetree Kbuild router. It delegates TI board DTB builds to `davinci`, `keystone`, and `omap` subdirectories.

## Important APIs/types/functions
- `subdir-y += davinci`
- `subdir-y += keystone`
- `subdir-y += omap`

## Control flow
Kbuild descends into all three subdirectories whenever this directory is visited by the ARM DT build.

## State and persistence behavior
No runtime state. The persistent behavior is source-tree organization: TI DTB target lists live in child Makefiles rather than this router.

## Dependencies and integration points
Depends on child directories and their Makefiles. Integrates with `arch/arm/boot/dts/Makefile` recursion.

## Risks and edge cases
Adding a new TI DT subdirectory without updating this file prevents normal `dtbs` traversal. Removing a subdirectory without removing the line breaks the build.

## Test signals
Run `make ARCH=arm dtbs` and verify Kbuild visits `ti/davinci`, `ti/keystone`, and `ti/omap`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/ti/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/ti/davinci/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/ti/davinci/Makefile

## Purpose
Kbuild manifest for TI DaVinci ARM board DTBs.

## Important APIs/types/functions
- `dtb-$(CONFIG_ARCH_DAVINCI)` lists `da850-lcdk.dtb`, `da850-enbw-cmc.dtb`, `da850-evm.dtb`, and `da850-lego-ev3.dtb`.

## Control flow
Kbuild appends DaVinci board DTBs when `CONFIG_ARCH_DAVINCI` is enabled.

## State and persistence behavior
No runtime state; it persists the board DTB output set.

## Dependencies and integration points
Depends on DaVinci DTS files and the ARM DTC pipeline. Bootloaders and board packaging use these exact DTB names.

## Risks and edge cases
Missing board entries prevent DTB generation; stale names break `dtbs`. DaVinci boards often rely on legacy platform integration, so schema regressions may surface in peripheral probe failures.

## Test signals
Run `make ARCH=arm dtbs` with DaVinci enabled; run `dtbs_check` for DA850 boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/ti/davinci/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/ti/keystone/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/ti/keystone/Makefile

## Purpose
Kbuild manifest for TI Keystone ARM board DTBs.

## Important APIs/types/functions
- `dtb-$(CONFIG_ARCH_KEYSTONE)` lists K2HK, K2L, K2E, K2G EVM, and K2G ICE DTBs.

## Control flow
The DTBs are built when `CONFIG_ARCH_KEYSTONE` is enabled.

## State and persistence behavior
No runtime state. The file persists board DTB publication for Keystone platforms.

## Dependencies and integration points
Depends on Keystone DTS files, SoC Kconfig, DTC, and binding schemas for TI Keystone peripherals.

## Risks and edge cases
Renamed DTS files or missing board entries break build coverage. Board DTBs must stay aligned with boot firmware expectations and Keystone interrupt/timer bindings.

## Test signals
Run `make ARCH=arm dtbs` with Keystone enabled and `make ARCH=arm dtbs_check` for K2 boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/ti/keystone/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/ti/omap/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/ti/omap/Makefile

## Purpose
Large Kbuild manifest for TI OMAP, AM33xx, AM43xx, DRA7xx, OMAP5, and TI81xx ARM DTBs and selected overlays.

## Important APIs/types/functions
- Kconfig-gated DTB lists: `CONFIG_ARCH_OMAP2`, `CONFIG_ARCH_OMAP3`, `CONFIG_ARCH_OMAP4`, `CONFIG_SOC_AM33XX`, `CONFIG_SOC_AM43XX`, `CONFIG_SOC_DRA7XX`, `CONFIG_SOC_OMAP5`, and `CONFIG_SOC_TI81XX`.
- Composite overlay targets: `am335x-bonegreen-hdmi-00a0-dtbs`, `am57xx-evm-dtbs`, `am57xx-evm-reva3-dtbs`, `am571x-idk-overlays-dtbs`, and `am572x-idk-overlays-dtbs`.
- `DTC_FLAGS_am335x-* += -@` enables symbol generation required by overlays for BeagleBone-family base DTBs.
- `dtb- += ...` entries mark build-time overlay test targets enabled by `CONFIG_OF_ALL_DTBS`.

## Control flow
Kbuild evaluates enabled SoC symbols to build the matching board DTBs. Composite `*-dtbs` rules combine base DTB and overlay DTBO dependencies. DTC flags are applied per base target before overlay builds.

## State and persistence behavior
No runtime state. This file persists the canonical list of generated TI board DTBs and overlay-enabled base targets, which affects release artifacts and downstream bootloader references.

## Dependencies and integration points
Depends on DTS/DTSO sources in `ti/omap`, DTC overlay support, TI SoC Kconfig, and binding schemas. Integrates with board packaging and U-Boot/extlinux DTB naming for OMAP/AM/DRA platforms.

## Risks and edge cases
Overlay targets require `-@` on matching bases; missing flags break phandle symbol resolution. `dtb- +=` test-only targets may be built only under all-DTB modes, so normal builds may miss overlay regressions. Long board lists are prone to stale entries and missing new boards.

## Test signals
Run `make ARCH=arm dtbs` across OMAP/AM/DRA configs and `make ARCH=arm dtbs_check`. Include `CONFIG_OF_ALL_DTBS=y` or equivalent all-DTB builds to exercise test-only overlay compositions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/ti/omap/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/unisoc/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/unisoc/Makefile

## Purpose
Kbuild manifest for Unisoc/RDA ARM DTBs.

## Important APIs/types/functions
- `dtb-$(CONFIG_ARCH_RDA)` lists Orange Pi 2G-IoT and Orange Pi i96 DTBs based on RDA8810PL.

## Control flow
Kbuild builds the listed DTBs when `CONFIG_ARCH_RDA` is enabled.

## State and persistence behavior
No runtime state; it persists board DTB output names.

## Dependencies and integration points
Depends on RDA DTS files, `ARCH_RDA`, and ARM DTC build rules.

## Risks and edge cases
Stale DTB names break the build; absent entries reduce board coverage.

## Test signals
Run `make ARCH=arm dtbs` and `dtbs_check` with RDA enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/unisoc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/vt8500/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/vt8500/Makefile

## Purpose
Kbuild manifest for VIA/WonderMedia VT8500-family board DTBs.

## Important APIs/types/functions
- `dtb-$(CONFIG_ARCH_VT8500)` lists VT8500, WM8505, WM8650, WM8750, WM8850, and WM8950 boards.

## Control flow
The DTBs are included in the build when `CONFIG_ARCH_VT8500` is enabled.

## State and persistence behavior
No runtime state. The persistent artifact is the set of generated DTB names.

## Dependencies and integration points
Depends on matching DTS files, VT8500 Kconfig, DTC, and platform binding schemas.

## Risks and edge cases
Legacy boards may receive less CI coverage; missing schema coverage can hide resource mismatches until boot.

## Test signals
Run `make ARCH=arm dtbs` and `dtbs_check` with VT8500 enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/vt8500/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/xen/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/xen/Makefile

## Purpose
Kbuild manifest for the ARM Xen virtual machine DTB.

## Important APIs/types/functions
- `dtb-$(CONFIG_ARCH_VIRT)` lists `xenvm-4.2.dtb`.

## Control flow
Kbuild builds the Xen VM DTB when `CONFIG_ARCH_VIRT` is enabled.

## State and persistence behavior
No runtime state. It persists the virtual platform DTB artifact used for Xen guest or VM boot scenarios.

## Dependencies and integration points
Depends on the Xen VM DTS source, virtual platform Kconfig, DTC, and Xen/ARM boot ABI expectations.

## Risks and edge cases
Virtual platform DTB changes can affect guest boot even without physical hardware. The config gate means it is missed by non-virt builds.

## Test signals
Run `make ARCH=arm dtbs` with `ARCH_VIRT`; boot a Xen guest or run DT schema validation for the virtual DTB.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/xen/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/xilinx/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/xilinx/Makefile

## Purpose
Kbuild manifest for Xilinx Zynq ARM board DTBs.

## Important APIs/types/functions
- `dtb-$(CONFIG_ARCH_ZYNQ)` lists ZC702/ZC706/ZC770 variants, MicroZed, ZedBoard, Zybo, Z-turn, Parallella, EBAZ4205, and related Zynq boards.

## Control flow
Kbuild includes all listed Zynq DTBs when `CONFIG_ARCH_ZYNQ` is enabled.

## State and persistence behavior
No runtime state. It persists the Zynq DTB target set and names expected by board boot flows.

## Dependencies and integration points
Depends on Zynq DTS files, the Zynq Kconfig symbol, DTC, and Xilinx platform binding schemas.

## Risks and edge cases
Board revisions with similar names can be easy to confuse. Missing DTB entries reduce board coverage; stale names break `dtbs`.

## Test signals
Run `make ARCH=arm dtbs` with Zynq enabled and `make ARCH=arm dtbs_check` for Zynq boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/xilinx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/install.sh -->
# sources/distributed-fs/ceph-client/arch/arm/boot/install.sh

## Purpose
Architecture-specific `make install` helper for ARM kernel images. It copies a built image and `System.map` to the requested install directory using versioned names.

## Important APIs/types/functions
- Positional arguments: `$1` kernel version, `$2` kernel image file, `$3` System.map file, `$4` install path.
- Image basename dispatch: `zImage` installs as `vmlinuz-$version`; other images install as `vmlinux-$version`.
- Existing installed files are renamed to `.old`.
- Optional `/sbin/loadmap` is executed if present.

## Control flow
The script enables `set -e`, chooses `base` from `basename $2`, rotates existing `$4/$base-$1`, copies the image via `cat`, rotates/copies `$4/System.map-$1`, and either runs `/sbin/loadmap` or prints a manual-install message.

## State and persistence behavior
Persists files in the install directory and creates `.old` backups. It has no kernel runtime state, but it mutates host filesystem install artifacts.

## Dependencies and integration points
Called by the kernel install target. Depends on a POSIX shell, writable install path, the built image, the map file, and optionally `/sbin/loadmap`.

## Risks and edge cases
Variables are unquoted in path tests and copy commands, so paths containing spaces or glob characters are unsafe. A blank `$4` intentionally addresses root-relative paths but can surprise callers. `cat` rather than `cp` may drop metadata. `set -e` stops on copy or move failure.

## Test signals
Run `make ARCH=arm install INSTALL_PATH=/tmp/...` with `zImage` and non-`zImage` inputs; verify backup rotation, final image contents, and `System.map` placement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/install.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arm/common/Kconfig

## Purpose
Defines hidden ARM common support configuration symbols for legacy companion chips and SoC helper code.

## Important APIs/types/functions
- `SA1111` selects `ZONE_DMA` on `ARCH_SA1100`.
- `KRAIT_L2_ACCESSORS`, `SHARP_LOCOMO`, `SHARP_PARAM`, and `SHARP_SCOOP` are boolean feature symbols selected by platforms or drivers.

## Control flow
Kconfig selection controls which objects from `arch/arm/common/Makefile` are compiled.

## State and persistence behavior
No runtime state. The selected symbols persist in `.config` and drive object inclusion.

## Dependencies and integration points
Integrated by ARM platform Kconfig files and `arch/arm/common/Makefile`. `SA1111` changes DMA zoning behavior for SA1100 builds.

## Risks and edge cases
These are hidden symbols, so platform Kconfig must select them correctly. Incorrect selection can either omit required platform support or include legacy code on unsupported boards.

## Test signals
Inspect `.config` for platform builds using SA1111, LoCoMo, Sharp SL params, Scoop, and Krait L2 accessors; run `make ARCH=arm olddefconfig` and compile affected platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/common/Makefile

## Purpose
Build manifest for ARM common support objects.

## Important APIs/types/functions
- Always builds `firmware.o`.
- Conditional objects: `sa1111.o`, `krait-l2-accessors.o`, `locomo.o`, `sharpsl_param.o`, `scoop.o`, `secure_cntvoff.o`, `mcpm_head.o`, `mcpm_entry.o`, `mcpm_platsmp.o`, `vlock.o`, `bL_switcher.o`, and `bL_switcher_dummy_if.o`.
- `CFLAGS_REMOVE_mcpm_entry.o = -pg` prevents function graph/profile instrumentation in sensitive MCPM entry code.

## Control flow
Kbuild maps config symbols to object files and links them into the ARM kernel or modules as appropriate.

## State and persistence behavior
No runtime state. It defines which support code is present in the kernel image.

## Dependencies and integration points
Integrates with Kconfig symbols, ARM common code, MCPM, CPUv7 timer offset setup, and legacy companion-chip drivers.

## Risks and edge cases
Profiling removal for `mcpm_entry.o` is important because low-level power paths cannot tolerate instrumentation. Missing object gating can create unresolved symbols or unsupported hardware access.

## Test signals
Run ARM allyesconfig/defconfig builds and platform-specific builds for SA1111, LoCoMo, MCPM, BL switcher, and Krait targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/bL_switcher.c -->
# sources/distributed-fs/ceph-client/arch/arm/common/bL_switcher.c

## Purpose
Core big.LITTLE switcher for ARM MCPM systems. It exposes a logical CPU migration mechanism that swaps a running logical CPU between paired physical CPUs in different clusters while hiding one CPU of each pair from normal scheduling.

## Important APIs/types/functions
- Exported API: `bL_switch_request_cb()`, `bL_switcher_register_notifier()`, `bL_switcher_unregister_notifier()`, `bL_switcher_trace_trigger()`, `bL_switcher_get_enabled()`, and `bL_switcher_put_enabled()`.
- Switch path: `bL_switch_to()`, `bL_switchpoint()`, and `bL_do_switch()`.
- Worker state: `struct bL_thread`, `bL_threads[]`, `bL_switcher_cpu_pairing[]`, `bL_gic_id[][]`, `bL_switcher_active`, original cluster tracking, and removed logical CPU mask.
- Sysfs under `/sys/kernel/bL_switcher`: `active` and `trace_trigger`.
- Init and CPU hotplug integration: `late_initcall(bL_switcher_init)`, `cpuhp_setup_state_nocalls()`, and `core_param(no_bL_switcher, ...)`.

## Control flow
Initialization requires MCPM availability, installs CPU hotplug veto callbacks, optionally enables the switcher, and creates sysfs. Enable flow notifies listeners, pairs online CPUs across two clusters, offlines unpaired logical CPUs, records GIC IDs, emits trace markers, and starts one FIFO switcher kthread per visible CPU. A switch request records the wanted cluster under a per-thread spinlock and wakes the worker. The worker calls `bL_switch_to()`, which powers up the inbound CPU through MCPM, gates entry vectors, migrates GIC target state, suspends local ticks, enters CPU PM, swaps `cpu_logical_map()` entries, runs `cpu_suspend()` through a stack-isolated switchpoint, resumes on the inbound CPU, and handshakes with the outbound CPU so it can power down.

## State and persistence behavior
Persistent in-kernel state is global: active flag, pairing table, original clusters, GIC IDs, per-CPU switcher threads, and removed CPU mask. Runtime synchronization uses completions, wait queues, spinlocks, mutexes, CPU hotplug locking, CPU PM callbacks, SGIs, WFE/SEV handshakes, and MCPM entry vectors. No on-disk state exists.

## Dependencies and integration points
Depends on MCPM (`asm/mcpm.h`), CPU suspend/resume, GIC migration helpers, CPU hotplug/device online-offline, clock/tick suspend, PM notifiers, power tracepoints, sysfs, kthreads, and logical MPIDR mappings. Consumers issue `bL_switch_request()` wrappers and may subscribe to activation notifications.

## Risks and edge cases
Only dual-cluster systems are supported. The switch path is fragile: interrupts/FIQs are disabled, CPU logical maps are rewritten, and a failed CPU PM entry triggers panic. CPU hotplug is vetoed for removed or unpaired CPUs while active. The source contains a duplicated `cpu_pm_enter()` call in the critical path, which is a high-risk signal for unmatched PM nesting unless intentional in this tree. Pairing logic intentionally odd-pairs CPUs, so users must not assume physical/logical adjacency. Sysfs writes can enable/disable the mechanism at runtime.

## Test signals
Boot an MCPM big.LITTLE platform, verify `/sys/kernel/bL_switcher/active`, exercise switch requests with callbacks, trace `power_cpu_migrate` events, run CPU hotplug online/offline attempts, and run suspend/resume. Build coverage requires `CONFIG_MCPM`, `CONFIG_BL_SWITCHER`, GIC, CPU suspend, and hotplug combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/bL_switcher.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/bL_switcher_dummy_if.c -->
# sources/distributed-fs/ceph-client/arch/arm/common/bL_switcher_dummy_if.c

## Purpose
Debug-only misc-device user interface for triggering big.LITTLE switch requests from userspace.

## Important APIs/types/functions
- `bL_switcher_write()` parses three-byte input `<cpu>,<cluster>`.
- Misc device: `/dev/b.L_switcher` with dynamic minor and `.write` handler.
- Calls `bL_switch_request(cpu, cluster)`.

## Control flow
Userspace writes at least three bytes. The driver copies the first three bytes, validates digit-comma-cluster format, converts one decimal CPU digit and cluster digit, then delegates to the switcher core.

## State and persistence behavior
No persistent state beyond misc-device registration. It causes state changes in `bL_switcher.c` by enqueueing switch requests.

## Dependencies and integration points
Depends on miscdevice, uaccess, module registration, and the exported big.LITTLE switcher API.

## Risks and edge cases
Only single-digit CPU IDs and cluster `0` or `1` are accepted. Input beyond three bytes is ignored. This is intentionally a debugging interface, so exposing it in production can let privileged users trigger disruptive CPU migration paths.

## Test signals
Build with `CONFIG_BL_SWITCHER_DUMMY_IF`, confirm `/dev/b.L_switcher` exists, write values like `0,1`, and verify switcher trace events or callback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/bL_switcher_dummy_if.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/firmware.c -->
# sources/distributed-fs/ceph-client/arch/arm/common/firmware.c

## Purpose
Provides the default ARM firmware operations pointer.

## Important APIs/types/functions
- `static const struct firmware_ops default_firmware_ops;`
- Global `const struct firmware_ops *firmware_ops = &default_firmware_ops;`

## Control flow
There is no function flow in this file. Platform code can replace or use `firmware_ops` through declarations in `asm/firmware.h`.

## State and persistence behavior
The global pointer is process-wide kernel state representing the active firmware operation table. The default table is empty/zeroed.

## Dependencies and integration points
Depends on `asm/firmware.h` and firmware-aware ARM platform code. Used by suspend, PSCI, or platform firmware hooks where available.

## Risks and edge cases
Callers must tolerate absent operations when `firmware_ops` points to the default zero table. Replacing the pointer must be done early enough and with lifetime-stable storage.

## Test signals
Compile ARM platforms with and without firmware providers; boot logs and suspend/CPU bring-up paths should show correct firmware hook behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/firmware.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/krait-l2-accessors.c -->
# sources/distributed-fs/ceph-client/arch/arm/common/krait-l2-accessors.c

## Purpose
Exports serialized indirect accessors for Qualcomm Krait L2 cache controller registers accessed through CP15 selector/data registers.

## Important APIs/types/functions
- `krait_set_l2_indirect_reg(u32 addr, u32 val)`
- `krait_get_l2_indirect_reg(u32 addr)`
- Global `raw_spinlock_t krait_l2_lock`
- CP15 operations: write selector `c15,c0,6`, write/read data `c15,c0,7`, with `isb()` ordering.

## Control flow
Both functions take the raw spinlock with IRQ save, select the indirect register address, issue an ISB, access the data register, and release the lock.

## State and persistence behavior
State is in hardware L2 registers; the only software state is the lock. Writes persist until hardware reset or later writes by other code.

## Dependencies and integration points
Depends on Krait-specific CP15 register behavior, ARM barriers, raw spinlocks, and callers in Krait cache/SoC support code.

## Risks and edge cases
Using these helpers on non-Krait CPUs would access implementation-defined CP15 registers. Missing serialization can corrupt selector/data transactions, so all indirect accesses must go through these helpers.

## Test signals
Build Krait platforms with `CONFIG_KRAIT_L2_ACCESSORS`; exercise cache/L2 setup paths on hardware and verify no concurrent indirect register corruption under SMP load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/krait-l2-accessors.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/locomo.c -->
# sources/distributed-fs/ceph-client/arch/arm/common/locomo.c

## Purpose
Core driver and bus implementation for Sharp LoCoMo companion chips used by older Sharp handhelds. It initializes the chip, cascades interrupts, creates child devices, and exports GPIO, DAC, and frontlight helpers.

## Important APIs/types/functions
- Core state: `struct locomo` with device, physical base, IRQ, IRQ base, lock, I/O base, and saved PM state.
- Child description: `struct locomo_dev_info locomo_devices[]`.
- IRQ path: `locomo_handler()`, `locomo_mask_irq()`, `locomo_unmask_irq()`, `locomo_setup_irq()`.
- Probe/remove/PM: `__locomo_probe()`, `locomo_probe()`, `locomo_suspend()`, `locomo_resume()`, `__locomo_remove()`.
- Exported helpers: `locomo_gpio_set_dir()`, `locomo_gpio_read_level()`, `locomo_gpio_read_output()`, `locomo_gpio_write()`, `locomo_m62332_senddata()`, `locomo_frontlight_set()`, `locomo_driver_register()`, and `locomo_driver_unregister()`.
- Bus type: `locomo_bus_type`.

## Control flow
Platform probe maps the MMIO page, clears interrupt/GPIO/frontlight/SPI state, initializes timing/DAC registers, reads version, installs a chained interrupt handler if IRQ resources exist, and registers child devices on the LoCoMo bus. Interrupt handling acknowledges the parent, reads request bits from `LOCOMO_ICR`, and dispatches up to four child IRQs. PM suspend saves selected registers and powers down outputs/clocks; resume restores state and reinitializes keyboard clocking. Child drivers bind through the custom bus by matching `devid`.

## State and persistence behavior
Runtime state lives in the mapped LoCoMo registers, child `struct device` instances, `saved_state` allocated across suspend, and spinlock-protected GPIO/DAC/frontlight access. There is no disk persistence.

## Dependencies and integration points
Depends on platform data for IRQ base, `asm/hardware/locomo.h` register definitions, platform resources, the driver core, chained IRQ handling, and Sharp handheld child drivers for keyboard, frontlight, backlight, audio, LED, UART, and SPI.

## Risks and edge cases
Legacy custom bus and platform-data-only discovery limit DT/ACPI integration. The bit-banged DAC path holds the spinlock across many `udelay()` calls. Child registration errors are mostly not propagated after probe starts. IRQ base handling uses legacy static IRQ assumptions. Suspend/resume saves only selected registers, so child drivers must restore their own state.

## Test signals
Boot a LoCoMo-based Sharp platform, verify child devices bind, trigger keyboard/GPIO/SPI interrupts, exercise frontlight/DAC helpers, and run suspend/resume. Build with `CONFIG_SHARP_LOCOMO`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/locomo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/mcpm_entry.c -->
# sources/distributed-fs/ceph-client/arch/arm/common/mcpm_entry.c

## Purpose
High-level C implementation of ARM multi-cluster power management (MCPM) state transitions. It coordinates CPU and cluster power-up/down, race avoidance, platform hooks, and synchronization state shared with the assembly entry path.

## Important APIs/types/functions
- Global synchronization: `struct sync_struct mcpm_sync`.
- Entry vector APIs: `mcpm_set_entry_vector()` and `mcpm_set_early_poke()`.
- Platform registration: `mcpm_platform_register()`, `mcpm_is_available()`.
- Power APIs: `mcpm_cpu_power_up()`, `mcpm_cpu_power_down()`, `mcpm_wait_for_cpu_powerdown()`, `mcpm_cpu_suspend()`, `mcpm_cpu_powered_up()`.
- Initialization/test APIs: `mcpm_sync_init()` and, under CPU suspend, `mcpm_loopback()`.
- Internal state: `platform_ops`, `arch_spinlock_t mcpm_lock`, and `mcpm_cpu_use_count[][]`.

## Control flow
`mcpm_sync_init()` initializes all clusters down except the boot cluster and writes the optional physical setup hook for assembly entry. `mcpm_cpu_power_up()` increments a use count under `mcpm_lock`, powers a cluster if unused, then powers the CPU. `mcpm_cpu_power_down()` marks the CPU going down, decrements use counts, determines whether it is the last CPU in the cluster, optionally enters the outbound critical section, runs platform prepare hooks, disables CPU or cluster cache, marks CPU down, waits for power removal, and if necessary resets through `mcpm_entry_point`. `mcpm_cpu_powered_up()` marks the CPU/cluster live after entry.

## State and persistence behavior
State is volatile but shared across cache-off and MMU-off transitions: `mcpm_sync` is cacheline-aligned and explicitly cleaned, entry vectors are physical addresses, early pokes are physical MMIO writes, and use counts track requested liveness. WFE/SEV and cache maintenance provide persistence across power-state transitions, not storage.

## Dependencies and integration points
Depends on platform `mcpm_platform_ops`, CPU reset, idmap/reboot MM setup, CPU PM, cacheflush helpers, `asm/mcpm.h`, CPU suspend, and the assembly `mcpm_entry_point`. The big.LITTLE switcher and SMP operations use this API.

## Risks and edge cases
The algorithm is race-sensitive and assumes correct platform hooks. Incorrect cache maintenance or sync state alignment can deadlock CPU bring-up/down. Use counts can be `0`, `1`, or transient `2`; other values are BUGs. Power-down requires IRQs disabled. If platform wait-for-powerdown is absent, callers receive `-EUNATCH`.

## Test signals
Run SMP secondary boot, CPU hotplug, suspend/resume, MCPM loopback, and big.LITTLE switcher tests on a multi-cluster ARM platform. Enable lockdep and trace CPU PM events where possible, but keep instrumentation out of `mcpm_entry.o` as the Makefile does.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/mcpm_entry.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/mcpm_head.S -->
# sources/distributed-fs/ceph-client/arch/arm/common/mcpm_head.S

## Purpose
Low-level MMU-off ARMv7 MCPM kernel entry point used when CPUs power up or re-enter after cluster power transitions.

## Important APIs/types/functions
- Entry symbol: `mcpm_entry_point`.
- BSS symbols: `mcpm_entry_vectors`, `mcpm_entry_early_pokes`, and `mcpm_power_up_setup_phys`.
- Per-cluster `first_man_locks` using `vlock_trylock()` and `vlock_unlock()`.
- Uses `mcpm_sync` offsets and state constants from `asm/mcpm.h`.

## Control flow
The entry code reads MPIDR, derives CPU/cluster indices, parks unexpected CPUs in WFI/WFE, locates shared variables position-independently, performs optional early MMIO pokes, marks the CPU `CPU_COMING_UP`, attempts to become the first CPU setting up the cluster, waits for teardown races to resolve, invokes `power_up_setup` for cluster and CPU levels, marks the cluster and CPU up, then spins at a gate until the C code installs an entry vector. Finally it branches to the vector, such as `secondary_startup` or `cpu_resume`.

## State and persistence behavior
State is in `.bss` arrays and `mcpm_sync`, accessed before normal virtual addressing is available. It relies on barriers, WFE/SEV, and byte stores visible across CPUs. Entry vectors are physical addresses written by C code.

## Dependencies and integration points
Depends on ARMv7-A, `assembler.h`, `vlock.h`, MCPM sync layout, optional debug LL printing, and `mcpm_entry.c` initialization. Used by CPU reset paths and platform power controllers.

## Risks and edge cases
Struct layout assumptions are enforced with assembler `.error`. Incorrect MPIDR affinity, wrong `MAX_CPUS_PER_CLUSTER`, or broken Device/Strongly-Ordered memory assumptions can park CPUs forever. The gate intentionally waits for nonzero vectors, so missed `mcpm_set_entry_vector()` calls deadlock bring-up.

## Test signals
CPU hotplug and secondary boot must reliably pass through this entry. Debug LL traces can show "kernel mcpm_entry_point" and "released" when enabled. Stress with repeated cluster power-down/up cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/mcpm_head.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/mcpm_platsmp.c -->
# sources/distributed-fs/ceph-client/arch/arm/common/mcpm_platsmp.c

## Purpose
SMP operation glue that connects generic ARM SMP boot/hotplug callbacks to MCPM physical CPU and cluster power APIs.

## Important APIs/types/functions
- `mcpm_smp_set_ops()` installs `mcpm_smp_ops`.
- SMP callbacks: `mcpm_boot_secondary()`, `mcpm_secondary_init()`, and under hotplug `mcpm_cpu_kill()`, `mcpm_cpu_can_disable()`, `mcpm_cpu_die()`.
- Helper `cpu_to_pcpu()` maps logical CPU to MPIDR affinity levels.

## Control flow
Booting a secondary clears its entry vector, powers up the physical CPU/cluster, sets entry vector to `secondary_startup`, sends wakeup IPI, and emits SEV. Secondary init calls `mcpm_cpu_powered_up()`. CPU hotplug die clears the local entry vector and enters MCPM power-down; kill waits for platform powerdown completion.

## State and persistence behavior
No private persistent state. It mutates MCPM entry vectors and MCPM power state via shared APIs.

## Dependencies and integration points
Depends on `cpu_logical_map()`, ARM SMP core, `secondary_startup`, MCPM APIs, and CPU hotplug.

## Risks and edge cases
Incorrect logical-to-physical mapping boots the wrong CPU. Missing platform `wait_for_powerdown` weakens hotplug kill verification. The code assumes all CPUs may be disabled.

## Test signals
Boot all secondary CPUs, repeatedly online/offline CPUs, verify MPIDR debug logs, and confirm platform power controller state matches kernel CPU state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/mcpm_platsmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/sa1111.c -->
# sources/distributed-fs/ceph-client/arch/arm/common/sa1111.c

## Purpose
Core driver, custom bus, IRQ controller, GPIO provider, power management, and helper API for the Intel SA1111 companion chip.

## Important APIs/types/functions
- Core state: `struct sa1111` with clock, MMIO base, IRQ domain, GPIO chip, platform data, lock, and saved PM state.
- Child descriptors: `sa1111_devices[]` for USB, SAC audio, SSP, PS/2 keyboard/mouse, and PCMCIA.
- IRQ domain and chip: `sa1111_irq_handler()`, `sa1111_irqdomain_map()`, `sa1111_setup_irq()`, `sa1111_remove_irq()`.
- GPIO callbacks: direction/get/set/set_multiple/to_irq.
- Probe/remove/PM: `__sa1111_probe()`, `sa1111_probe()`, `sa1111_suspend_noirq()`, `sa1111_resume_noirq()`, `__sa1111_remove()`.
- Exported child APIs: `sa1111_pll_clock()`, `sa1111_select_audio_mode()`, `sa1111_set_audio_rate()`, `sa1111_get_audio_rate()`, `sa1111_enable_device()`, `sa1111_disable_device()`, `sa1111_get_irq()`, `sa1111_driver_register()`, and `sa1111_driver_unregister()`.
- Bus: `sa1111_bus_type`.

## Control flow
Subsys init registers the SA1111 bus and platform driver. Probe requires platform data, prepares the clock, maps registers, validates chip ID, wakes the chip through the documented clock/reset sequence, initializes the cascaded IRQ domain, registers GPIOs, configures SA1100 memory controller details when applicable, and creates child devices from `sa1111_devices[]`. Child drivers match by bitmask `devid`. IRQ handling reads and clears status banks, dispatches mapped hwirqs, and unmasks the parent for level-triggered sources. Suspend saves clock/interrupt state and sleeps the chip; resume wakes it and restores saved registers.

## State and persistence behavior
State lives in SA1111 hardware registers, clock state, irqdomain mappings, GPIO chip registration, child device objects, `g_sa1111`, and suspend `saved_state`. Register writes persist until reset, suspend, or later writes.

## Dependencies and integration points
Depends on platform resources/data, SA1111 register definitions, IRQ domains, gpiolib, platform driver core, clocks, SA1100 memory-bus hooks, DMA masks, and child drivers for SA1111 functions.

## Risks and edge cases
Legacy platform data and static IRQ assumptions complicate modern DT use. `g_sa1111` is a global singleton used by legacy code. Some register access and IRQ retrigger behavior is hardware-erratum-sensitive. Probe creates multiple children; partial child failures are logged but not always fatal. Suspend/resume assumes chip identity remains stable.

## Test signals
Boot an SA1111 board, verify child devices, GPIO lines, IRQ mapping, audio clock/rate helpers, PCMCIA/USB/PS2 peripherals, and suspend/resume. Build with `CONFIG_SA1111` and SA1100/PXA platform variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/sa1111.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/scoop.c -->
# sources/distributed-fs/ceph-client/arch/arm/common/scoop.c

## Purpose
Platform driver and GPIO/register helper support for Sharp SCOOP interface chips used by Sharp PDAs, including PCMCIA linkage.

## Important APIs/types/functions
- Global `platform_scoop_config`.
- Core state `struct scoop_dev` with MMIO base, GPIO chip, lock, suspend masks, and saved GPIO output.
- Exported helpers: `reset_scoop()`, `read_scoop_reg()`, and `write_scoop_reg()`.
- GPIO callbacks: `scoop_gpio_set()`, `scoop_gpio_get()`, `scoop_gpio_direction_input()`, and `scoop_gpio_direction_output()`.
- Platform flow: `scoop_probe()`, `scoop_remove()`, `scoop_suspend()`, `scoop_resume()`.

## Control flow
Probe maps MMIO, initializes reset/control registers from platform `scoop_config`, stores suspend masks, and optionally registers a 12-line GPIO chip. GPIO operations lock around GPCR/GPWR writes. Suspend records GPWR and applies board-provided clear/set masks; resume restores GPWR.

## State and persistence behavior
Runtime state is in SCOOP registers, GPIO chip registration, platform driver data, and saved `scoop_gpwr` across suspend. No disk state exists.

## Dependencies and integration points
Depends on platform resources/data, `asm/hardware/scoop.h`, gpiolib, platform driver core, and Sharp PDA PCMCIA/board code.

## Risks and edge cases
Probe assumes platform data is present and dereferences it. Legacy `gpiochip_add_data()` cleanup must match remove ordering. The GPIO bit numbering starts at hardware PA11 and uses `offset + 1`, so off-by-one mistakes affect real pins.

## Test signals
Boot Sharp PDA platforms, verify SCOOP reset, exported register helpers, GPIO direction/output/input, PCMCIA integration, and suspend/resume GPIO retention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/scoop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/secure_cntvoff.S -->
# sources/distributed-fs/ceph-client/arch/arm/common/secure_cntvoff.S

## Purpose
Secure-mode helper that initializes the ARM architectural timer virtual offset register `CNTVOFF` to zero.

## Important APIs/types/functions
- Entry symbol `secure_cntvoff_init`.
- Uses Monitor mode, SCR non-secure bit, `mcrr p15, 4, ..., c14` to write `CNTVOFF`, and returns to SVC mode.

## Control flow
The routine switches to Monitor mode, reads Secure Configuration Register, sets SCR.NS, writes zero to `CNTVOFF`, restores the original secure configuration, switches back to SVC mode, and returns.

## State and persistence behavior
It mutates secure architectural CPU state: SCR transiently and CNTVOFF persistently for the CPU until reset or later firmware/kernel writes.

## Dependencies and integration points
Requires ARMv7 virtualization extensions and execution privilege that permits Monitor-mode SCR/CNTVOFF access. Built for `CONFIG_CPU_V7` and used by platforms that need kernel-side virtual timer offset initialization.

## Risks and edge cases
Running this when TrustZone firmware owns secure state can be unsafe. CPUs lacking virtualization extensions or Monitor access will fault. SMP systems need per-CPU consideration if each CPU has separate timer offset state.

## Test signals
Boot affected ARMv7 platforms and verify virtual counter behavior, timer interrupts, and absence of undefined-instruction or monitor-mode faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/secure_cntvoff.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/sharpsl_param.c -->
# sources/distributed-fs/ceph-client/arch/arm/common/sharpsl_param.c

## Purpose
Early boot helper for preserving manufacturing hardware parameters from Sharp SL-series bootloader memory before the kernel overwrites them.

## Important APIs/types/functions
- Exported global `struct sharpsl_param_info sharpsl_param`.
- `sharpsl_save_param()` copies from `PARAM_BASE`.
- Magic constants: `COMADJ_MAGIC`, `UUID_MAGIC`, `TOUCH_MAGIC`, `AD_MAGIC`, and `PHAD_MAGIC`.

## Control flow
`sharpsl_save_param()` maps or directly references `PARAM_BASE`, copies the full parameter structure, and invalidates individual fields by setting them to `-1` when their keyword magic does not match.

## State and persistence behavior
The copied `sharpsl_param` global persists for the lifetime of the booted kernel. It preserves bootloader/manufacturing data in RAM; no disk state is written.

## Dependencies and integration points
Depends on `asm/mach/sharpsl_param.h`, Sharp SL board early init calling `sharpsl_save_param()`, and consumers such as LCD, touch, battery/AD, UUID, or calibration drivers.

## Risks and edge cases
Must be called before the parameter memory is overwritten. Physical address differs for SA1100 versus other platforms. Field invalidation is per-magic, so structure layout mismatches can silently produce wrong calibration.

## Test signals
Boot Sharp SL devices and verify exported calibration/UUID fields; test missing/bad magic values produce `-1` sentinel fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/sharpsl_param.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/vlock.S -->
# sources/distributed-fs/ceph-client/arch/arm/common/vlock.S

## Purpose
ARM assembly implementation of the MCPM voting lock used for first-man cluster setup coordination during low-level power transitions.

## Important APIs/types/functions
- `vlock_trylock(base, cpu)` returns zero on success and nonzero on loss.
- `vlock_unlock(base)` releases ownership.
- Macros `voting_begin` and `voting_end` maintain per-CPU voting bytes with barriers and SEV.

## Control flow
`vlock_trylock()` marks the calling CPU as voting, checks whether owner is empty, writes its owner vote, clears its voting byte, waits until all voting bytes are zero, then checks whether its vote won. If owner was already set, it clears its vote and fails. `vlock_unlock()` clears owner and sends SEV.

## State and persistence behavior
The lock structure stores an owner byte and per-CPU voting bytes. It must reside in Strongly-Ordered or Device memory as the algorithm relies on neighboring byte writes not interfering and on explicit barriers.

## Dependencies and integration points
Depends on `vlock.h`, ARMv7-A WFE/SEV/DMB/DSB behavior, MCPM `MAX_CPUS_PER_CLUSTER`, and `mcpm_head.S` first-man lock arrays.

## Risks and edge cases
Using cacheable normal memory violates assumptions. Incorrect `VLOCK_VOTING_SIZE` or CPU IDs outside the cluster range corrupt lock state. Lost SEV or memory-ordering bugs can deadlock cluster bring-up.

## Test signals
Stress MCPM cluster power-up with multiple CPUs racing to enter; verify only one first-man executes cluster setup and non-winners wait/retry correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/vlock.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/vlock.h -->
# sources/distributed-fs/ceph-client/arch/arm/common/vlock.h

## Purpose
Shared layout constants for the ARM MCPM voting lock structure used by `vlock.S` and `mcpm_head.S`.

## Important APIs/types/functions
- `VLOCK_OWNER_OFFSET`
- `VLOCK_VOTING_OFFSET`
- `VLOCK_VOTING_SIZE`
- `VLOCK_SIZE`
- `VLOCK_OWNER_NONE`

## Control flow
No executable flow. The constants drive assembler offsets and allocation sizes.

## State and persistence behavior
Defines the memory layout of lock state: owner byte at offset zero and a word-rounded per-CPU voting region after offset four.

## Dependencies and integration points
Depends on `asm/mcpm.h` for `MAX_CPUS_PER_CLUSTER`. Included by `vlock.S` and `mcpm_head.S`.

## Risks and edge cases
Changing these constants without updating assembly users breaks low-level locking. Size rounding must remain compatible with word-wide scans in the `MANY` case.

## Test signals
Assembler builds should pass layout expectations; MCPM multi-CPU bring-up stress tests validate runtime behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/vlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/crypto/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arm/crypto/Kconfig

## Purpose
Kconfig menu for ARM accelerated cryptographic algorithms using kernel-mode NEON, ARMv8 Crypto Extensions, and PMULL.

## Important APIs/types/functions
- `CRYPTO_GHASH_ARM_CE`: AES-GCM AEAD using ARMv8 Crypto Extensions/PMULL; selects AEAD, AES library, and GF128 multiplication.
- `CRYPTO_AES_ARM_BS`: bit-sliced NEON AES for ECB/CBC/CTR/XTS; selects SKCIPHER and AES library.
- `CRYPTO_AES_ARM_CE`: ARMv8 Crypto Extensions AES for ECB/CBC/CTS/CTR/XTS; selects SKCIPHER and AES library.

## Control flow
Menu selections gate objects in `arch/arm/crypto/Makefile`. All options depend on `KERNEL_MODE_NEON`.

## State and persistence behavior
Selections persist in `.config` and determine algorithm registration availability at boot/module load.

## Dependencies and integration points
Integrates with the Linux CryptoAPI, module autoload aliases, CPU feature checks in module init, and ARM NEON/SIMD context management.

## Risks and edge cases
Enabling code on CPUs lacking runtime features must fail gracefully in module init. NEON use requires correct `kernel_neon_begin/end` pairing to avoid corrupting user/kernel SIMD state.

## Test signals
Build with each config as built-in and module; run `crypto/testmgr`, `tcrypt`, AF_ALG users, and CPU-feature-negative boot tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/crypto/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/crypto/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/crypto/Makefile

## Purpose
Kbuild manifest for ARM architecture-specific CryptoAPI modules.

## Important APIs/types/functions
- `aes-arm-bs-y := aes-neonbs-core.o aes-neonbs-glue.o`
- `aes-arm-ce-y := aes-ce-core.o aes-ce-glue.o`
- `ghash-arm-ce-y := ghash-ce-core.o ghash-ce-glue.o`
- Module objects gated by `CONFIG_CRYPTO_AES_ARM_BS`, `CONFIG_CRYPTO_AES_ARM_CE`, and `CONFIG_CRYPTO_GHASH_ARM_CE`.

## Control flow
Kbuild links assembly cores with C glue into CryptoAPI modules or built-ins according to config.

## State and persistence behavior
No runtime state. It controls which algorithm providers are linked and named.

## Dependencies and integration points
Depends on C glue symbols matching assembly exports and CryptoAPI Kconfig symbols.

## Risks and edge cases
Mismatched object lists or symbol names produce link failures. Assembly cores require appropriate toolchain/architecture flags from the ARM build system.

## Test signals
Run ARM crypto builds with each algorithm enabled as module and built-in; confirm module names and CryptoAPI registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/crypto/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/crypto/aes-ce-core.S -->
# sources/distributed-fs/ceph-client/arch/arm/crypto/aes-ce-core.S

## Purpose
ARMv8 Crypto Extensions assembly core for AES block modes on 32-bit ARM: ECB, CBC, CTS-CBC, CTR, XTS, key substitution, and inverse mix-columns helper.

## Important APIs/types/functions
- Exported entry points: `ce_aes_ecb_encrypt/decrypt`, `ce_aes_cbc_encrypt/decrypt`, `ce_aes_cbc_cts_encrypt/decrypt`, `ce_aes_ctr_encrypt`, `ce_aes_xts_encrypt/decrypt`, `ce_aes_sub`, and `ce_aes_invert`.
- Internal helpers: `aes_encrypt`, `aes_decrypt`, `aes_encrypt_4x`, `aes_decrypt_4x`, and `ce_aes_xts_init`.
- Uses AES instructions (`aese`, `aesmc`, `aesd`, `aesimc`) and NEON vector registers for parallel blocks.

## Control flow
Mode entry points loop over full blocks, prefer 4-block parallel paths where possible, then handle remaining blocks and tails. CBC encrypt chains each ciphertext block through the IV; CBC decrypt can parallelize decrypt then XOR previous ciphertext. CTR constructs counter blocks, handles counter carry, and supports a tail-keystream path. XTS initializes tweak from the second key and IV, updates tweaks per block, and handles ciphertext stealing.

## State and persistence behavior
No global state. State is passed in key schedules, IV/tweak/counter buffers, input/output pointers, block counts, and vector registers. IV/counter buffers are updated by the assembly routines for chaining modes.

## Dependencies and integration points
Called from `aes-ce-glue.c` inside `kernel_neon_begin/end`. Requires CPU AES extension availability and correct key schedule layout from `struct crypto_aes_ctx`.

## Risks and edge cases
Assembly ABI must exactly match C prototypes. Tail and ciphertext-stealing paths are high risk for off-by-one and overlap errors. Counter carry and XTS tweak multiplication must match CryptoAPI test vectors. NEON/AES register use must remain inside protected SIMD sections.

## Test signals
Run CryptoAPI AES test vectors for ECB, CBC, CTS-CBC, CTR, XTS with 128/192/256-bit keys, unaligned scatterlists, in-place and out-of-place buffers, partial tails, and counter carry cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/crypto/aes-ce-core.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/crypto/aes-ce-glue.c -->
# sources/distributed-fs/ceph-client/arch/arm/crypto/aes-ce-glue.c

## Purpose
C CryptoAPI glue for ARMv8 Crypto Extensions AES skcipher algorithms, registering ECB, CBC, CTS-CBC, CTR, and XTS providers backed by `aes-ce-core.S`.

## Important APIs/types/functions
- Key setup: `ce_aes_expandkey()`, `ce_aes_setkey()`, `xts_set_key()`, `num_rounds()`.
- Request handlers: `ecb_encrypt/decrypt`, `cbc_encrypt/decrypt`, `cts_cbc_encrypt/decrypt`, `ctr_encrypt`, `xts_encrypt/decrypt`.
- Registered `skcipher_alg aes_algs[]` with driver names `ecb-aes-ce`, `cbc-aes-ce`, `cts-cbc-aes-ce`, `ctr-aes-ce`, and `xts-aes-ce`.
- Module feature gating: `module_cpu_feature_match(AES, aes_init)`.

## Control flow
Key expansion validates AES key sizes, builds encryption keys, then uses AES extension helpers to derive decryption keys. Each skcipher handler creates a `skcipher_walk`, enters kernel NEON around assembly calls, processes full walk segments, and returns walk residuals. CTS and XTS create subrequests when ciphertext stealing spans scatterlist boundaries. CTR handles final partial block by generating one keystream block and XOR-copying the tail.

## State and persistence behavior
Algorithm state is per-tfm in `crypto_aes_ctx` or `crypto_aes_xts_ctx`. Request state lives in `skcipher_walk`, IV buffers, scatterlist subrequests, and stack tail buffers. Module registration persists providers until `aes_exit()`.

## Dependencies and integration points
Depends on CryptoAPI skcipher internals, ARM NEON/SIMD management, CPU feature matching, AES library constants, scatterwalk helpers, XTS key verification, and assembly entry points.

## Risks and edge cases
NEON begin/end pairing is critical; this source contains duplicate `kernel_neon_begin()` calls in `xts_encrypt()` and an extra brace in `cbc_encrypt_walk()` as read, both strong compile/runtime risk signals if present in the active tree. CTS/XTS scatterlist tail handling must preserve IV/tweak state across subrequests. XTS rejects messages shorter than one block.

## Test signals
Run `crypto/testmgr` and `tcrypt` for all registered modes, including scatterlist splits, in-place operation, partial CTR tails, CTS one-block and partial-final-block cases, XTS stealing, and module load on CPUs with/without AES feature.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/crypto/aes-ce-glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/crypto/aes-neonbs-core.S -->
# sources/distributed-fs/ceph-client/arch/arm/crypto/aes-neonbs-core.S

## Purpose
NEON bit-sliced AES assembly core for 32-bit ARM, processing eight AES blocks in parallel for ECB, CBC decrypt, CTR, and XTS.

## Important APIs/types/functions
- Exported entry points: `aesbs_convert_key`, `aesbs_ecb_encrypt/decrypt`, `aesbs_cbc_decrypt`, `aesbs_ctr_encrypt`, `aesbs_xts_encrypt/decrypt`.
- Internal helpers: `aesbs_encrypt8`, `aesbs_decrypt8`, `__xts_prepare8`, permutation tables, ShiftRows/MixColumns/S-box macro sequences.

## Control flow
`aesbs_convert_key()` transforms conventional round keys into bit-sliced layout. ECB and CTR process groups of eight blocks, with permutations between byte layout and bit-sliced vectors. CBC decrypt decrypts parallel blocks then XORs with prior ciphertext/IV. CTR generates counter vectors and handles tails. XTS prepares eight tweak values, applies encrypt/decrypt, and updates tweak order for ciphertext stealing.

## State and persistence behavior
No global state. State is in vector registers, key schedule memory, IV/counter/tweak buffers, and input/output pointers. IV/counter/tweak buffers are mutated for chaining modes.

## Dependencies and integration points
Called from `aes-neonbs-glue.c` under `kernel_neon_begin/end`. Requires NEON availability and key layout produced by `aesbs_convert_key()`.

## Risks and edge cases
Eight-block granularity requires fallback or special handling for small/tail buffers. Assembly/C ABI mismatches, scatterlist stride mistakes, or tweak reordering bugs break only specific sizes. Constant-time bit-sliced logic reduces table-timing exposure but still depends on correct SIMD context management.

## Test signals
CryptoAPI vectors for ECB/CBC/CTR/XTS across key sizes, messages below/equal/above eight blocks, unaligned buffers, in-place buffers, and ciphertext stealing are required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/crypto/aes-neonbs-core.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/crypto/aes-neonbs-glue.c -->
# sources/distributed-fs/ceph-client/arch/arm/crypto/aes-neonbs-glue.c

## Purpose
C CryptoAPI glue for the NEON bit-sliced AES implementation, registering ECB, CBC, CTR, and XTS skcipher providers.

## Important APIs/types/functions
- Contexts: `struct aesbs_ctx`, `struct aesbs_cbc_ctx`, and `struct aesbs_xts_ctx`.
- Key setup: `aesbs_setkey()`, `aesbs_cbc_setkey()`, `aesbs_xts_setkey()`.
- Request handlers: `__ecb_crypt()`, `cbc_encrypt()`, `cbc_decrypt()`, `ctr_encrypt()`, `__xts_crypt()`, `xts_encrypt()`, `xts_decrypt()`.
- Registered drivers: `ecb-aes-neonbs`, `cbc-aes-neonbs`, `ctr-aes-neonbs`, and `xts-aes-neonbs`.

## Control flow
Key setup expands normal AES keys then converts encryption keys into bit-sliced form. ECB/CBC decrypt/CTR/XTS walk scatterlists and call assembly for block batches. CBC encryption uses the scalar AES fallback because encryption is inherently serial. CTR pads sub-block tails into a stack buffer. XTS encrypts the tweak with the fallback key, processes full blocks via bit-sliced assembly, then handles ciphertext stealing with scalar fallback on a two-block stack buffer.

## State and persistence behavior
Per-tfm state stores bit-sliced round keys, scalar fallback keys, and XTS tweak key. Request state is in scatterwalks, IV buffers, and stack buffers. Module registration persists until unload.

## Dependencies and integration points
Depends on HWCAP_NEON runtime check, CryptoAPI skcipher, AES library fallback routines, XTS helpers, scatterwalk, and `aes-neonbs-core.S`.

## Risks and edge cases
The source as read contains a duplicate `kernel_neon_begin()` in `ctr_encrypt()` without a matching second end, which is a serious SIMD nesting risk if active. CBC encryption fallback is table/scalar dependent and may not share bit-sliced side-channel properties. Tail and XTS stealing paths use stack bounce buffers and scatterwalk copies that need overlap testing.

## Test signals
Run CryptoAPI AES vectors with NEON present/absent, all key sizes, batch and non-batch message lengths, CTR partial blocks, XTS tails, and in-place scatterlists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/crypto/aes-neonbs-glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/crypto/ghash-ce-core.S -->
# sources/distributed-fs/ceph-client/arch/arm/crypto/ghash-ce-core.S

## Purpose
ARM PMULL/NEON assembly core for GHASH and fused AES-GCM encrypt/decrypt/finalization operations.

## Important APIs/types/functions
- Exported functions: `pmull_ghash_update_p64`, `pmull_gcm_encrypt`, `pmull_gcm_decrypt`, `pmull_gcm_enc_final`, and `pmull_gcm_dec_final`.
- Internal helpers: PMULL GHASH aggregation, AES encrypt helpers, final tag generation/verification, and byte-permutation table `.Lpermute`.

## Control flow
GHASH update multiplies input blocks into the running digest using precomputed hash powers. GCM encrypt/decrypt routines interleave AES counter-mode keystream generation with GHASH accumulation over ciphertext. Final routines process tail bytes, fold lengths into GHASH, encrypt `J0`, produce or compare tags, and return authentication status for decrypt.

## State and persistence behavior
No global state. Digest, hash key powers, AES round keys, IV/counter, source/destination pointers, and tag buffers are caller-provided. Digest and output buffers are mutated.

## Dependencies and integration points
Called by `ghash-ce-glue.c` inside NEON sections. Requires PMULL and NEON hardware capability, key layout from ARM AES library, and GHASH reflection/precomputation in C.

## Risks and edge cases
Authentication correctness depends on exact GHASH endian/reflection convention. Tail handling and final tag comparison are security-critical. Assembly ABI and PMULL availability must match runtime feature checks.

## Test signals
Run AES-GCM and RFC4106 vectors with varied AAD/plaintext lengths, tails, tag sizes, invalid tags, in-place buffers, and scatterlist splits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/crypto/ghash-ce-core.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/crypto/ghash-ce-glue.c -->
# sources/distributed-fs/ceph-client/arch/arm/crypto/ghash-ce-glue.c

## Purpose
C CryptoAPI AEAD glue for ARM PMULL AES-GCM and RFC4106(GCM(AES)) providers.

## Important APIs/types/functions
- Context `struct gcm_key` stores hash powers, AES round keys, round count, and RFC4106 nonce tail.
- Key/auth setup: `gcm_aes_setkey()`, `gcm_aes_setauthsize()`, `rfc4106_setkey()`, `rfc4106_setauthsize()`.
- MAC helpers: `ghash_reflect()`, `gcm_update_mac()`, `gcm_calculate_auth_mac()`.
- AEAD handlers: `gcm_encrypt()`, `gcm_decrypt()`, `rfc4106_encrypt()`, `rfc4106_decrypt()`.
- Registered drivers: `gcm-aes-ce` and `rfc4106-gcm-aes-ce`.

## Control flow
Key setup builds an AES encrypt key, encrypts the zero block to get GHASH H, precomputes reflected powers H through H^4, and stores round keys. Encryption walks AEAD data, authenticates AAD with GHASH, encrypts plaintext blocks while updating digest, finalizes tail/length/tag, writes the tag after ciphertext, and completes the walk. Decryption copies the received tag, authenticates/decrypts ciphertext, finalizes and verifies the tag, and returns `-EBADMSG` on failure. RFC4106 prepends the fixed nonce to request IV and excludes the explicit IV from authenticated payload length.

## State and persistence behavior
Per-tfm state stores AES and GHASH precomputation; per-request state stores digest, counter, stack buffers, and copied tag. Module registration persists providers until unload.

## Dependencies and integration points
Depends on CryptoAPI AEAD/skcipher walking, ARM NEON, HWCAP_NEON and HWCAP2_PMULL checks, AES library key layout, GF128 multiplication helpers, GCM/RFC4106 validation helpers, and `ghash-ce-core.S`.

## Risks and edge cases
Auth failure must not expose unauthenticated plaintext semantics to callers beyond CryptoAPI norms. The source as read contains a stray duplicated block-comment terminator in the encrypt tail comment area, which is a compile-risk signal if present. Scatterwalk page-boundary handling restarts NEON sections and must stay balanced. RFC4106 associated-data length validation is mandatory.

## Test signals
Run CryptoAPI AEAD vectors for valid/invalid tags, all allowed tag sizes, zero/nonzero AAD, partial tails, RFC4106 nonce/IV layouts, in-place buffers, scatterlist splits, and CPUs without PMULL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/crypto/ghash-ce-glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/Kbuild -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/Kbuild

## Purpose
Header export/generation manifest for ARM architecture include files.

## Important APIs/types/functions
- Generic header mappings: `early_ioremap.h`, `extable.h`, `flat.h`, and `parport.h`.
- Generated headers: `mach-types.h` and `unistd-nr.h`.

## Control flow
Kbuild uses `generic-y` to source generic versions of headers not supplied by ARM and `generated-y` to track generated architecture headers.

## State and persistence behavior
No runtime state. It controls generated/exported include tree contents during builds.

## Dependencies and integration points
Integrates with Kbuild header generation, UAPI/syscall generation, and asm-generic fallbacks.

## Risks and edge cases
Incorrect generic mapping can hide an architecture-specific header or break includes. Missing generated header declarations can cause stale or absent build products.

## Test signals
Run full ARM builds and header install checks; verify generated `mach-types.h` and `unistd-nr.h` exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/arch_gicv3.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/arch_gicv3.h

## Purpose
ARM32 architecture-specific GICv3 system-register and MMIO accessor layer used by the generic irqchip GICv3 driver.

## Important APIs/types/functions
- CP15 register aliases for ICC registers: `ICC_EOIR1`, `ICC_DIR`, `ICC_IAR1`, `ICC_SGI1R`, `ICC_PMR`, `ICC_CTLR`, `ICC_SRE`, `ICC_IGRPEN1`, `ICC_BPR1`, `ICC_RPR`, AP registers.
- `CPUIF_MAP()` creates AArch64-style read/write wrappers for selected ICC registers.
- Low-level helpers: `gic_read_iar()`, `gic_write_dir()`, `gic_write_ctlr()`, `gic_write_grpen1()`, `gic_write_sgi1r()`, SRE/PMR/BPR/RPR accessors.
- Non-atomic 64-bit MMIO helpers for IROUTER, BASER, PROPBASER, PENDBASER, and ITS registers.
- ARM32 stubs for priority masking: `gic_prio_masking_enabled()` false and warning stubs for PMR masking.

## Control flow
Inline functions translate generic GIC driver operations into ARM32 CP15 `read_sysreg/write_sysreg` or ordered 32-bit MMIO pairs. Some writes issue `isb()` and interrupt acknowledge issues `dsb(sy)`.

## State and persistence behavior
State is hardware interrupt-controller state: ICC CPU interface registers, distributor/redistributor/ITS MMIO registers, and dcache flush side effects. The header itself stores no data.

## Dependencies and integration points
Depends on ARM CP15 accessors, IO helpers, cache flush, barriers, and GIC register definitions. Used by the GICv3 irqchip driver when built for AArch32.

## Risks and edge cases
64-bit accesses are deliberately non-atomic; comments document when that is safe. `gicr_write_vpendbaser()` must clear Valid before changing fields. Calling PMR masking stubs on ARM32 warns because that feature is unsupported here.

## Test signals
Boot ARM32 GICv3 platforms, exercise interrupts, SGIs, LPIs/ITS if available, CPU hotplug, and virtualization pending-table paths. Run irqchip selftests where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/arch_gicv3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/arch_timer.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/arch_timer.h

## Purpose
ARM32 architectural timer accessors for the clocksource/clockevent driver.

## Important APIs/types/functions
- `arch_timer_arch_init()`
- CP15 timer accessors: `arch_timer_reg_write_cp15()`, `arch_timer_reg_read_cp15()`, `arch_timer_get_cntfrq()`, `__arch_counter_get_cntpct()`, `__arch_counter_get_cntvct()`, stable variants, `arch_timer_get_cntkctl()`, and `arch_timer_set_cntkctl()`.
- Event stream feature helpers: `arch_timer_set_evtstrm_feature()` and `arch_timer_have_evtstrm_feature()`.
- Erratum macros: `has_erratum_handler()` false and `erratum_handler()`.

## Control flow
Inline switch statements emit the correct CP15 read/write instruction for physical or virtual timer control and compare-value registers. Counter reads issue `isb()` before `mrrc`. Control writes issue `isb()` after writes.

## State and persistence behavior
State is architectural timer hardware state: control registers, compare values, frequency, kernel control, and advertised HWCAP event stream bit. No file-local storage exists.

## Dependencies and integration points
Depends on `clocksource/arm_arch_timer.h`, CP15 timer registers, barriers, HWCAP, and the generic ARM arch timer driver.

## Risks and edge cases
Unsupported access/register combinations use `BUILD_BUG()`. ARM32 declares no timer erratum handlers here, so affected hardware must be handled elsewhere or not supported. Counter reads require barriers for ordering.

## Test signals
Boot with `CONFIG_ARM_ARCH_TIMER`, verify clocksource registration, timer interrupts, virtual/physical timer modes, event stream HWCAP, and suspend/resume timer continuity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/arch_timer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/archrandom.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/archrandom.h

## Purpose
ARM32 architecture random header that disables SMCCC TRNG probing and falls back to generic archrandom behavior.

## Important APIs/types/functions
- `smccc_probe_trng()` returns false.
- Includes `asm-generic/archrandom.h`.

## Control flow
No dynamic flow beyond callers seeing `smccc_probe_trng()` as false.

## State and persistence behavior
No state. It affects whether SMCCC TRNG is treated as available.

## Dependencies and integration points
Integrates with generic random/archrandom infrastructure and SMCCC feature probing.

## Risks and edge cases
ARM32 platforms with firmware TRNG support through SMCCC will not expose it via this hook. Entropy must come from other random sources.

## Test signals
Build random subsystem on ARM32; verify no SMCCC TRNG provider is registered from this path and generic fallbacks compile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/archrandom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/arm-cci.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/arm-cci.h

## Purpose
ARM32 helper for deciding whether the platform has secure access to ARM CCI registers.

## Important APIs/types/functions
- `platform_has_secure_cci_access()` returns `mcpm_is_available()` when `CONFIG_MCPM` is enabled, otherwise false.

## Control flow
Compile-time conditional selects MCPM-backed detection or a false stub.

## State and persistence behavior
No state. Result reflects MCPM platform registration state when compiled with MCPM.

## Dependencies and integration points
Depends on `asm/mcpm.h` under `CONFIG_MCPM`. Used by ARM CCI/cache-coherency code that needs to know whether secure-only CCI registers can be touched.

## Risks and edge cases
MCPM availability is a proxy, not direct hardware detection. Platforms with secure CCI access but no MCPM will return false; platforms with MCPM but restricted secure access may need platform-specific care.

## Test signals
Build with and without `CONFIG_MCPM`; boot CCI/MCPM platforms and verify CCI secure register paths behave correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/arm-cci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/arm_pmuv3.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/arm_pmuv3.h

## Purpose
ARM32 PMUv3 CP15 accessor header for the perf ARM PMU driver and related virtualization stubs.

## Important APIs/types/functions
- CP15 register aliases for PMCR, PMCCNTR, PMCNTEN*, PMOVSR, PMSELR, PMXEVTYPER, PMXEVCNTR, PMUSERENR, PMINTEN*, PMCEID*, PMMIR, PMCCFILTR, and numbered event counters/types.
- Dynamic event accessors: `read_pmevcntrn()`, `write_pmevcntrn()`, `write_pmevtypern()`.
- PMU control helpers: `read_pmuver()`, `pmuv3_implemented()`, `is_pmuv3p4/p5/p9()`, `read_pmceid0/1()`, counter/filter/interrupt/user access writes.
- ARM32 stubs for instruction counter and KVM PMU hooks.

## Control flow
Inline helpers map generic PMUv3 operations to CP15 system-register reads/writes. PMU version is decoded from `CPUID_EXT_DFR0`; feature predicates interpret version numbers. PMCEID reads include extension registers for PMUv3.1+.

## State and persistence behavior
State is hardware PMU register state and perf event configuration. The header stores no data, but write helpers mutate counters, event selectors, filters, enable bits, interrupt enables, and overflow status.

## Dependencies and integration points
Depends on `asm/cp15.h`, `asm/cputype.h`, `PMEVN_SWITCH` macro definitions, and the ARM perf PMU driver. KVM hooks are stubs on ARM32 in this file.

## Risks and edge cases
Invalid event counter indices fall through `PMEVN_SWITCH` behavior and return zero/no-op. FEAT_PMUv3 instruction counter is not accessible for 32-bit here. PMU version handling treats IMP_DEF as not implemented.

## Test signals
Run `perf stat`, overflow interrupt tests, event enumeration, counter read/write tests, and builds across PMUv3 versions. Verify PMCEID extension reads on PMUv3.1+ hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/arm_pmuv3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/asm-offsets.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/asm-offsets.h

## Purpose
Thin include wrapper that exposes generated assembler offset definitions to ARM headers and assembly sources.

## Important APIs/types/functions
- Includes `<generated/asm-offsets.h>`.

## Control flow
No executable flow; preprocessing pulls in generated constants.

## State and persistence behavior
No runtime state. Build-generated offset constants persist in the build directory and are consumed by assembly.

## Dependencies and integration points
Depends on the kernel `asm-offsets` generation step. Included by `assembler.h` and other assembly-facing headers.

## Risks and edge cases
If generated offsets are stale or missing, assembly may build against wrong structure layouts or fail to compile.

## Test signals
Clean ARM build should regenerate `generated/asm-offsets.h`; assembly files using task/thread offsets should compile and boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/asm-offsets.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/assembler.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/assembler.h

## Purpose
Central ARM assembly macro header for low-level kernel code. It provides endian helpers, interrupt control, tracing hooks, SMP alternatives, current-task/per-CPU access, user access exception table helpers, branch/return helpers, bug annotations, and long-address load/store macros.

## Important APIs/types/functions
- Byte/endian macros: `lspull`, `lspush`, `get_byte_*`, `put_byte_*`, `ARM_BE8`.
- Barriers and IRQ macros: `disable_irq_notrace`, `enable_irq_notrace`, `dsb`, `isb`, `asm_trace_hardirqs_*`, `save_and_disable_irqs`, `restore_irqs`.
- Address/control helpers: `badr*`, `get_thread_info`, `set_current`, `get_current`, `reload_current`, `this_cpu_offset`, `ldr_this_cpu`.
- SMP alternatives: `ALT_SMP`, `ALT_UP`, `ALT_UP_B`.
- User access helpers: `USERL`, `USER`, `usracc`, `strusr`, `ldrusr`.
- Utility macros: `safe_svcmode_maskall`, `setmode`, `string`, `ret*`, `bug`, `_ASM_NOKPROBE`, `mov_l`, `adr_l`, `ldr_l`, `str_l`, `ldr_va`, `str_va`, `rev_l`, and `bl_r`.

## Control flow
The header is included only from assembly and emits instruction sequences conditionally based on architecture level, ARM/Thumb2 mode, SMP, tracing, endian mode, V7M, CPUv6, module PLT support, and relocation capabilities. Many macros create local labels, exception-table entries, or alternative instruction sections.

## State and persistence behavior
No runtime variables are defined here, but emitted macros mutate CPU state: CPSR/PRIMASK, current task TLS registers, per-CPU address registers, barriers, exception tables, bug tables, and kprobe blacklist sections. These generated sections persist in object files.

## Dependencies and integration points
Depends on ARM assembler syntax, `asm/ptrace.h`, `asm/opcodes-virt.h`, generated asm offsets, page/table/thread info headers, and uaccess assembly helpers. Used throughout ARM entry, exception, MMU, copy, crypto, and power-management assembly.

## Risks and edge cases
Macros must assemble to exact sizes for SMP alternatives, especially Thumb2 `ALT_UP()`. Incorrect CPSR/mode manipulation can break boot or exception return. User access macros must create correct exception table entries. Long-address macros vary by architecture and module relocation support; wrong assumptions cause relocation or literal-range failures.

## Test signals
Full ARM builds in ARM and Thumb2 modes, SMP and UP, V7M and classic ARM, big/little endian, modules, kprobes, lockdep IRQ tracing, and boot/exception/uaccess tests all exercise this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/assembler.h -->
