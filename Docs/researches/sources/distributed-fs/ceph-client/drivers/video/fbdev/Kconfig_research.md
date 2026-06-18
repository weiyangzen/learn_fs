# sources/distributed-fs/ceph-client/drivers/video/fbdev/Kconfig

## Purpose
This Kconfig file is the build-time feature matrix for legacy Linux fbdev drivers. It defines the top-level `FB` menuconfig, common helper symbols, hardware-specific framebuffer drivers, optional per-driver subfeatures, and subordinate Kconfig includes for fbdev subdirectories. For this work item it gates the Acorn VIDC, Amiga native chipset, Arc monochrome LCD, ARK 2000PV, and Asiliant/Chips 69000 drivers that are built by the local Makefile.

## Important APIs, Types, and Functions
The file is declarative Kconfig rather than C code. Its key "APIs" are symbols and dependency expressions consumed by Kbuild, users, and defconfigs. `menuconfig FB` is a tristate root that selects `FB_CORE` and `FB_NOTIFY`; all driver symbols depend on it directly or indirectly. Common helper symbols include `FB_HECUBA`, `FB_SVGALIB`, `FB_MACMODES`, and `FB_SBUS_HELPERS`, each selected by drivers that need shared code.

The relevant local symbols are `FB_ACORN`, `FB_AMIGA`, `FB_AMIGA_OCS`, `FB_AMIGA_ECS`, `FB_AMIGA_AGA`, `FB_ARC`, `FB_ARK`, and `FB_ASILIANT`. They express platform constraints, helper selection, and module eligibility: `FB_ACORN` is bool-only for built-in Acorn ARM platforms, `FB_AMIGA` is tristate and has per-chipset bools, `FB_ARC` is tristate with `HAS_IOPORT` and x86/compile-test gating, `FB_ARK` is tristate and depends on PCI plus `HAS_IOPORT`, and `FB_ASILIANT` is bool-only for built-in PCI systems.

## Control Flow
Kconfig evaluation starts at `menuconfig FB`; if disabled, the rest of the fbdev driver tree is unavailable. Enabling `FB` exposes architecture/platform driver choices and subordinate options. Helper symbols are selected by drivers, so selecting `FB_ARC` automatically pulls in deferred sysmem helpers and selecting `FB_ARK` pulls in the cfb drawing helpers, I/O memory fb file operations, and SVGALIB helper layer. At the end of the file, subdirectory Kconfigs for `geode`, `omap`, `omap2`, `mmp`, and `core` are sourced so the menu extends beyond the flat file.

The Amiga flow is a notable hierarchy: `FB_AMIGA` enables the driver, while `FB_AMIGA_OCS`, `FB_AMIGA_ECS`, and `FB_AMIGA_AGA` choose supported chip generations. The C driver has compile-time fallbacks if none are set, but normal configuration should choose at least one relevant generation.

## State and Persistence
Kconfig state persists in kernel configuration outputs such as `.config`, generated `include/config/*` files, and built module lists. The file itself keeps no runtime state. Its choices persist into compile-time `CONFIG_*` macros that conditionally include driver code, constants, and hardware paths.

## Dependencies and Integration Points
The file integrates with Kbuild through symbol names consumed in `drivers/video/fbdev/Makefile`. It also integrates with architecture capabilities such as `ARM`, `ARCH_ACORN`, `AMIGA`, `PCI`, `HAS_IOPORT`, `COMPILE_TEST`, and helper subsystems including `APERTURE_HELPERS`, `FB_IOMEM_HELPERS`, `FB_SYSMEM_HELPERS_DEFERRED`, `FB_CFB_FILLRECT`, `FB_CFB_COPYAREA`, `FB_CFB_IMAGEBLIT`, `FB_MODE_HELPERS`, `VIDEOMODE_HELPERS`, and bus-specific libraries.

## Risks and Edge Cases
Several drivers are legacy and architecture-specific, so incorrect dependency relaxation can allow builds that compile but are unusable or unsafe on unsupported hardware. Bool-only symbols such as `FB_ACORN` and `FB_ASILIANT` prevent module builds; changing them would require code lifetime and remove-path review. Helper selections are part of the ABI between Kconfig and C code: dropping `FB_IOMEM_FOPS`, cfb helpers, or deferred sysmem helpers would lead to unresolved operations or missing fbops. `COMPILE_TEST` increases build coverage but can hide runtime assumptions about real I/O ports, VGA primary devices, or platform-provided memory.

## Test Signals
Useful validation includes `olddefconfig` and `allmodconfig`/`allyesconfig` builds for supported architectures, compile-test builds for `FB_ARC` and PCI VGA drivers, and checking that each selected symbol produces the expected object in the Makefile. For this group, direct signals are `CONFIG_FB_ACORN=y` building `acornfb.o`, `CONFIG_FB_AMIGA=m/y` building `amifb.o c2p_planar.o`, `CONFIG_FB_ARC=m/y` building `arcfb.o`, `CONFIG_FB_ARK=m/y` building `arkfb.o`, and `CONFIG_FB_ASILIANT=y` building `asiliantfb.o`.
