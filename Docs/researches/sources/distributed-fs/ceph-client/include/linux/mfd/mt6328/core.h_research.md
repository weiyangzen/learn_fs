<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mt6328/core.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/mt6328/core.h

This MT6328 core header defines PMIC IRQ status numbers for the MT6328 MFD. The enum covers power/home key press and release, thermal/battery high-low, RTC/audio/accessory-detect events, low-battery and impedance ADC events, over-current events for VPROC/VSYS/VLTE/VCORE/VPA/LDO, charger/overvoltage/VBATON/watchdog events, fuel-gauge thresholds, and speaker fault events. The numbering is sparse at hardware bank boundaries, with groups starting at 0, 16, and 32.

Control flow is indirect: these constants are used by the MFD IRQ tables to map bits in MT6328 interrupt status registers to Linux virqs. Child drivers request the mapped IRQs and the core handles register-level masking and demux. State is hardware interrupt status/mask data; this header only defines logical positions.

Dependencies include the MT6328 register header for `INT_CON*`, `INT_STATUS*`, and `INT_TYPE_CON*`, the MediaTek PMIC IRQ framework, and child drivers for keys, charger, battery/fuel gauge, audio, accessory detect, RTC, and regulators. Risks include sparse numbering, status count lacking an explicit `_NR` sentinel, and the closing include-guard comment naming MT6323 rather than MT6328. Test signals include IRQ table coverage for all enum values, edge tests for key press/release, charger plug/overvoltage events, and over-current interrupt injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mt6328/core.h -->
