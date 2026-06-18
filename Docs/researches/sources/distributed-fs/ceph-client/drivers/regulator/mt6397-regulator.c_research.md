# sources/distributed-fs/ceph-client/drivers/regulator/mt6397-regulator.c

Purpose: implements the MediaTek MT6397 PMIC regulator driver for CPU/GPU/core bucks and numerous analog/digital LDOs through the MT6397 MFD regmap.

Important APIs/types/functions: `struct mt6397_regulator_info` extends descriptors with status query masks, hardware-voted VSEL register selection, VSEL control register/mask, and buck mode registers. Descriptor macros create buck, table LDO, and fixed-regulator entries. Key functions are `mt6397_map_mode()`, `mt6397_regulator_set_mode()`, `mt6397_regulator_get_mode()`, `mt6397_get_status()`, `mt6397_set_buck_vosel_reg()`, and `mt6397_regulator_probe()`.

Control flow: probe first calls `mt6397_set_buck_vosel_reg()` to read each buck's VSEL control bit and redirect `desc.vsel_reg` to the active `vselon_reg` when hardware control is selected. It then reads `MT6397_CID`, logs the chip ID, swaps the VGP2 voltage table for revision `MT6397_REGULATOR_ID91`, and registers each regulator. Buck mode changes write AUTO or FORCE_PWM bits; status reads the descriptor enable register and checks `qi`.

State and persistence: PMIC registers persist enable/status, voltage selector, VSEL source selection, and mode bits. The driver mutates the global descriptor table at probe time for active VSEL registers and revision-specific VGP2 voltages.

Dependencies and integration: depends on MT6397 MFD parent data, MT6397 register and regulator ID headers, regmap, regulator OF matching under compatible `mediatek,mt6397-regulator`, and DT binding mode constants.

Risks and test signals: descriptor mutation is global, so multi-instance assumptions would be unsafe even if the hardware is normally singleton. The VSEL-source read must happen before registration or voltage ops target the wrong register. Revision-specific VGP2 values can affect board constraints. Test all bucks with VSELCTRL on/off, chip ID revision 0x91 and default, sparse LDO table mapping, status `qi` masks for bucks versus LDOs, and mode invalid/error paths.
