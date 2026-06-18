# sources/distributed-fs/ceph-client/drivers/pinctrl/mvebu/pinctrl-armada-cp110.c

Purpose: this driver describes the Armada CP110/CP115 pin controller used by Armada 7K and 8K communication processor blocks. It provides a single 63-pin MPP table with functions for device bus, audio, GE/XG/MII, TDM, MSS peripherals, PTP, PCIe, SATA, SDIO, UART, LED, SyncE, and CP-to-CP links.

Important APIs, types, and functions: `armada_cp110_mpp_modes[]` holds pin modes for MPP0-62. The variant enum distinguishes `V_ARMADA_7K`, `V_ARMADA_8K_CPM`, `V_ARMADA_8K_CPS`, and `V_CP115_STANDALONE`. `armada_cp110_mpp_controls[]` is one unnamed `mvebu_regmap_mpp_ctrl` range. `mvebu_pinctrl_assign_variant()` mutates all settings in a mode to the computed availability mask. `armada_cp110_pinctrl_probe()` allocates per-device `mvebu_pinctrl_soc_info` and calls the simple regmap probe against the parent syscon.

Control flow: probe matches the compatible to a CP flavor, validates a parent syscon, allocates SoC info, and iterates the mode table assigning availability by MPP index: 0-31 are 7K/CPS/standalone, 32-38 are 7K/CPM/standalone, 39-43 are CPM/standalone only, and 44-62 are 7K/CPM/standalone. The common MVEBU core then filters unsupported settings by `soc->variant`, builds unique function lists, and programs 4-bit mux fields through regmap.

State and persistence behavior: the per-device SoC info is managed, but the mode table itself is static and is rewritten at probe with variant masks. Hardware state persists in syscon registers. No GPIO ranges are registered in this file, so GPIO integration depends on the pinctrl mux table rather than explicit ranges here.

Dependencies and integration points: dependencies are parent syscon regmap access, MVEBU core semantics, OF compatibles for Armada 7K/8K CPM/CPS and CP115 standalone, and DTS pinctrl function/group naming. It integrates with many platform controllers because CP110 carries most board-facing I/O.

Risks and test signals: mutating the global mode table at probe is risky if multiple CP110 instances with different variants probe in one kernel; the last probe's variant assignments affect the shared array used by all devices. The comment says MPP39-43 are unavailable on Armada 7K, and that policy is implemented only by the probe-time mutation. Test both CPM and CPS instances in an Armada 8K system, check function availability in debugfs for MPP39-43, validate SDIO pins 56-62, and exercise regmap write/readback on a few mux values.
