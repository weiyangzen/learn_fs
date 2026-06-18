<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mt6323/core.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/mt6323/core.h

This MediaTek MT6323 core header defines the PMIC interrupt status numbering used by the MT6397-family MFD/IRQ framework. `enum MT6323_IRQ_STATUS_numbers` lists status bits for speaker left alarms, battery high/low, watchdog, power key, thermal high/low, VBATON, charger-valid/detect/overvoltage, and over-current/status lines for LDO, fast charger key, accessory detect, audio, RTC, VPROC, VSYS, and VPA. `MT6323_IRQ_STATUS_NR` is the sentinel.

The header has no functions; its control-flow role is to provide stable hardware IRQ indexes to the PMIC IRQ registration tables. The MFD core reads interrupt status registers from the MT6323 register map, maps these enum values into Linux IRQs, and child drivers request the logical IRQs relevant to their blocks. State is interrupt latch/mask state in hardware, not in this header.

Dependencies are the MediaTek PMIC wrapper/MFD IRQ implementation and the matching `mt6323/registers.h` offsets, especially `MT6323_INT_STATUS0/1` and interrupt mask/control registers. Risks include sparse numbering (`LDO = 16`) matching hardware bank boundaries, uppercase enum type style that differs from later MT headers, and enum order being used by IRQ tables. Test signals include IRQ table size matching `MT6323_IRQ_STATUS_NR`, power-key/charger/RTC interrupt delivery, and status-bank boundary tests around bit 16.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mt6323/core.h -->
