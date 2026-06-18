<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mt6331/core.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/mt6331/core.h

This MT6331 core header defines the IRQ status numbering and bank-size macros for the MT6331 PMIC. The enum covers power/home key, charger detect, thermal/battery high-low, RTC, audio, MAD, accessory-detect events, and over-current events for VDVFS11-14, GPU, VCORE1/2, VIO18, and LDO. It also defines `MT6331_IRQ_CON0_BASE/BITS` and `MT6331_IRQ_CON1_BASE/BITS` to describe interrupt bank layout for the MediaTek PMIC IRQ framework.

Control flow is limited to IRQ table construction: the MFD core uses base/bit counts to register interrupt banks, reads status registers, and exposes Linux virqs for child drivers. State is hardware interrupt status/mask state. The header has no functions or software storage.

Dependencies include matching register offsets in `mt6331/registers.h`, MediaTek PMIC IRQ structs/macros, and child drivers for keys, charger, RTC, audio, accessory detect, and regulators. A notable risk is that `MT6331_IRQ_CON1_BITS` references `MT6331_IRQ_STATUS_VDFS11_OC`, while the enum defines `MT6331_IRQ_STATUS_VDVFS11_OC`; this appears to be a typo that would break compilation if the macro is used. Other risks are sparse enum values and bank-boundary assumptions. Test signals include compiling users of the bank macros, IRQ table size checks, and interrupt injection across both banks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mt6331/core.h -->
