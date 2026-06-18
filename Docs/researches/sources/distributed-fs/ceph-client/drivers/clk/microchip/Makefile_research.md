# sources/distributed-fs/ceph-client/drivers/clk/microchip/Makefile

Purpose: This Makefile maps Microchip clock Kconfig symbols to build objects.

Important APIs, types, and functions: `clk-core.o` is built for `CONFIG_COMMON_CLK_PIC32`, `clk-pic32mzda.o` for `CONFIG_PIC32MZDA`, and both `clk-mpfs.o` and `clk-mpfs-ccc.o` for `CONFIG_MCHP_CLK_MPFS`.

Control flow: Kbuild includes these objects in the driver build according to configuration. There is no runtime control flow.

State and persistence behavior: The file has build-system state only. It determines object inclusion and link order within the Microchip clock directory.

Dependencies and integration points: It aligns with the Kconfig fragment and separates shared PIC32 operations from the PIC32MZDA SoC instantiation. MPFS core clock and CCC fabric clock drivers are both compiled when MPFS support is enabled.

Risks and edge cases: `clk-pic32mzda.o` depends on the shared `clk-core.o` APIs, so configuration must ensure both are available in PIC32MZDA builds. Enabling MPFS builds two platform drivers with different compatibles. Test signals are build coverage for each config combination and link checks for exported/internal symbols.
