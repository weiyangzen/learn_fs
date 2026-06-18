# sources/distributed-fs/ceph-client/arch/arm/boot/dts/realtek/Makefile

Purpose: this Makefile lists Realtek ARM DTBs for the kernel device-tree build.

Important API surface: `dtb-$(CONFIG_ARCH_REALTEK)` includes `rtd1195-horseradish.dtb` and `rtd1195-mele-x1000.dtb`.

Control flow: Kbuild conditionally appends two DTB targets based on `CONFIG_ARCH_REALTEK`.

State and persistence: no runtime state. The file persists the buildable RTD1195 board inventory.

Dependencies and integration: depends on matching Realtek DTS files and parent ARM DTS Makefile inclusion. Generated DTBs integrate with bootloader board selection for RTD1195 systems.

Risks and test signals: low complexity, but target/source drift still breaks `make dtbs`. Test with Realtek arch enabled and ensure both DTBs compile.
