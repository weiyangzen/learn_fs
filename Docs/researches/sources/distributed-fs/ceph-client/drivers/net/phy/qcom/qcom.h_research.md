# sources/distributed-fs/ceph-client/drivers/net/phy/qcom/qcom.h

Purpose: Defines shared Qualcomm/Atheros PHY register constants, bit fields, cable-test encodings, LED encodings, hardware-stat structures, status-mask structures, and helper prototypes consumed by the qcom PHY drivers and `qcom-phy-lib.c`.

Important APIs and types: Important definitions cover AT803x specific function/status registers, interrupt masks, Smart Speed downshift fields, AT803x and QCA808x cable diagnostic fields, QCA808x LED global/pattern/force fields, WoL MAC address and control registers, debug address/data registers, RGMII delay and hibernation bits, QCA808x counter registers, `enum stat_access_type`, `struct at803x_hw_stat`, `struct at803x_ss_mask`, and `struct qcom_phy_hw_stats`. Function prototypes expose debug register operations, WoL, interrupts, status decode, MDIX/autoneg preparation, tunables, CDT helpers, LED helpers, and stats helpers.

Control flow: This header has no executable control flow, but it defines the register contract that controls runtime behavior in the C files. Bitfield macros using `GENMASK`, `BIT`, and `FIELD_PREP_CONST` keep status/result decoding aligned with hardware layouts.

State and persistence: No runtime state. Struct definitions specify caller-owned software state for stat accumulation and speed-mask decoding.

Dependencies and integration: Depends on Linux bitfield macros and phylib types through including C files. It is included by `at803x.c`, `qca807x.c`, `qca808x.c`, `qca83xx.c`, and `qcom-phy-lib.c`, making it the local ABI for shared helper symbols.

Risks and test signals: Risks are incorrect bit masks, mismatched QCA808x cable code composition, undocumented LED force semantics, and prototype drift with exported helper implementations. Test by building all Qualcomm drivers together and independently, validating cable diagnostics and LED behavior against hardware, checking downshift/status decode fields for each chip family, and running sparse/compile checks for prototype mismatches.
