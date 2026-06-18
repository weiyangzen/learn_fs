<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mt6332/core.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/mt6332/core.h

This MT6332 core header defines the PMIC IRQ numbering and bank layout for a charger/flash/regulator-heavy companion PMIC. The enum covers charger completion and faults, thermal shutdown/regulator events, OTG and charger over-current/thermal/short conditions, flash timeout and LED open/short events, overvoltage and charger plug events, battery/fuel-gauge thresholds, speaker faults, BIF, WLED, and regulator over-current events for VDRAM, VDVFS2, VRF1/2, VPA, VSBST, and LDO. Bank macros describe four interrupt groups using base and bit-count values.

Control flow is IRQ-bank registration and demux by the MFD core. The core uses these constants with status/control registers to map hardware interrupt bits to Linux virqs; child drivers consume the virqs. State is hardware interrupt latch/mask state only.

Dependencies include `mt6332/registers.h`, MediaTek PMIC IRQ infrastructure, charger, flash/WLED, regulator, battery/fuel-gauge, speaker, BIF, and OTG consumers. Risks include sparse values at 0, 16, 32, 45, and 48, bank bit-count macros depending on inclusive arithmetic, and event names encoding hardware fault semantics that child drivers must not reinterpret incorrectly. Test signals include interrupt mapping tests for all four banks, charger/flash fault injection, over-current virq delivery, and build checks for bank macro use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mt6332/core.h -->
