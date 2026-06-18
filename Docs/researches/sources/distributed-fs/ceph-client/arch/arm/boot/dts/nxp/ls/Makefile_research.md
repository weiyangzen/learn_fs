# sources/distributed-fs/ceph-client/arch/arm/boot/dts/nxp/ls/Makefile

Purpose: this Kbuild fragment lists Layerscape LS1021A DTB outputs and composed overlay DTB targets.

Important API surface: under `CONFIG_SOC_LS1021A`, it builds base boards such as `ls1021a-iot.dtb`, `ls1021a-moxa-uc-8410a.dtb`, `ls1021a-qds.dtb`, `ls1021a-tqmls1021a-mbls1021a.dtb`, `ls1021a-tsn.dtb`, and `ls1021a-twr.dtb`. It also defines four `*-dtbs` composition variables pairing the TQMLS1021A base DTB with HDMI, LVDS, and RGB display overlay `.dtbo` files, then exposes the resulting composed `.dtb` targets.

Control flow: Kbuild expands conditional `dtb-y` style variables and recognizes `<target>-dtbs` lists to build composite DTBs from a base plus overlays.

State and persistence: no mutable state. The file persists board support in the build graph, including display-panel variants that become separate generated artifacts.

Dependencies and integration: depends on LS1021A `.dts` and `.dtso` files, the kernel overlay composition machinery, and `CONFIG_SOC_LS1021A`. Bootloader or distribution packaging may depend on the exact composed target names.

Risks and test signals: overlay ordering and target naming are fragile. A wrong base/overlay pairing can compile but describe the wrong display hardware. Test `make dtbs` with LS1021A enabled and inspect that all four composed display DTBs are emitted.
