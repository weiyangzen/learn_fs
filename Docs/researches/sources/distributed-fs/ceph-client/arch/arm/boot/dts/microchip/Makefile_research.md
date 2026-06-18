# sources/distributed-fs/ceph-client/arch/arm/boot/dts/microchip/Makefile

Purpose: Kbuild manifest for Microchip/Atmel ARM device-tree blobs. It decides which `.dtb` files are built for AT91RM9200, AT91SAM9, SAM9X60, SAM9X7, SAMA5, SAMA7D65, SAMA7G5, and LAN966 families based on enabled kernel `CONFIG_SOC_*` options.

Important APIs/types/functions: the file uses standard DTS Kbuild variables: `dtb-$(CONFIG_...) +=` appends DTB targets conditionally, and `DTC_FLAGS_<target> := -@` enables symbol generation needed by overlays for selected boards. It lists around 80 DTB targets and assigns overlay-capable DTC flags to boards such as sam9x60 curiosity/ek, sama5d2 boards, sama5d3/5d4 boards, sama7d65 curiosity, and sama7g5 boards.

Control flow: there is no program flow beyond Kbuild conditional expansion. During `make dtbs`, Kbuild evaluates enabled configs, collects the DTB target list, and invokes `dtc` for matching source files.

State and persistence: no runtime state. Persistent artifacts are generated DTBs under the kernel build tree. `-@` changes compiled DTB contents by retaining symbols and fixup metadata for overlay application.

Dependencies and integration: depends on arch/arm DTS Makefile inclusion, SoC Kconfig symbols, matching `.dts` source files in this directory, and the device tree compiler. It integrates board descriptions with the kernel build so board DTBs are produced only for selected SoC families.

Risks: missing a DTB target silently prevents a board from being built in normal configurations. An incorrect `DTC_FLAGS_*` name can leave an overlay-capable board without symbols. Stale targets break `make dtbs` when the referenced `.dts` is absent. Test signals are `make ARCH=arm dtbs`, targeted `make ... <board>.dtb`, and checking overlay users with `fdtdump`/`fdtoverlay` when `-@` is expected.
