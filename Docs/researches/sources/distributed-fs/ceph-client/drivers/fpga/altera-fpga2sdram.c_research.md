## sources/distributed-fs/ceph-client/drivers/fpga/altera-fpga2sdram.c

Purpose: this bridge driver controls the Altera SoCFPGA FPGA-to-SDRAM bridge. It does not reconfigure SDRAM port layout; it only enables or disables the port-reset mask captured by pre-Linux handoff.

Important APIs and functions: `struct alt_fpga2sdram_data` holds the SDR controller regmap and active port mask. `alt_fpga2sdram_enable_show()` reads `ALT_SDR_CTL_FPGAPORTRST_OFST` and reports whether all configured mask bits are set. `_alt_fpga2sdram_enable_set()` updates only the handoff mask bits. The registered `fpga_bridge_ops` provide `enable_set` and `enable_show`.

Control flow: probe allocates private data, looks up `altr,sdr-ctl` and `altr,sys-mgr` syscon regmaps, reads `SYSMGR_ISWGRP_HANDOFF3` for the FPGA-to-SDRAM mask, registers an FPGA bridge named `fpga2sdram`, and optionally applies the `bridge-enable` DT property. Remove unregisters the bridge.

State and persistence: the mask comes from a system-manager handoff register populated by firmware or bootloader and is treated as the persistent SDRAM port configuration. Runtime bridge state is the SDR controller reset bits. No local software shadow is used.

Dependencies and integration: it depends on syscon/regmap, OF compatible `altr,socfpga-fpga2sdram-bridge`, and the FPGA bridge framework. FPGA regions use it to stop FPGA-originated SDRAM traffic before reprogramming.

Risks: if boot firmware provides a stale or zero handoff mask, Linux will expose a bridge that controls the wrong ports or no ports. `bridge-enable` values greater than one are warned and ignored, so board DT mistakes may leave hardware in firmware-provided state. The driver assumes syscon compatibles are globally unique and accessible.

Test signals: verify probe with valid and missing syscon nodes, correct mask load from handoff register, `bridge-enable = <0>` and `<1>` behavior, sysfs bridge enable state, and safe disable/enable around FPGA reconfiguration while SDRAM accesses are quiesced.
