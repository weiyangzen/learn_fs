## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/intel/Makefile

### Purpose
This Kbuild fragment declares Intel ARM64 DTBs for SoCFPGA and Keem Bay platforms. It controls which board device trees are compiled for matching architecture config options.

### Important APIs, Types, And Functions
There are no functions or types. The exported build interface is `dtb-$(CONFIG_ARCH_INTEL_SOCFPGA)` with a multiline list of Agilex, Agilex3, Agilex5, and N5X board DTBs, plus `dtb-$(CONFIG_ARCH_KEEMBAY)` for `keembay-evm.dtb`.

### Control Flow
Kbuild conditionally appends DTB targets when the relevant `CONFIG_ARCH_*` symbols are enabled. The backslash-continued SoCFPGA list is parsed as one assignment containing multiple output targets.

### State, Persistence, And Dependencies
There is no runtime state. The persistent outputs are compiled DTBs. Dependencies are Kbuild syntax, the referenced DTS files, and the configuration symbols for Intel SoCFPGA and Keem Bay.

### Integration Points
Integration points include parent ARM64 DTB makefiles, Intel platform DTS sources, CI and package `dtbs` targets, U-Boot/firmware DTB loading, and board support documentation.

### Risks
Continuation-line mistakes can drop or merge DTB names. Missing entries reduce build coverage for a board. Incorrect config guards can cause DTB artifacts to disappear from expected build products.

### Test Signals
Useful signals include `make ARCH=arm64 dtbs` with Intel SoCFPGA and Keem Bay configs, checking that 11 DTB targets are produced, and booting or schema-validating the Agilex/N5X/Keem Bay DTBs. Source reading signal: 12 lines; 11 DTB references; no functions.
