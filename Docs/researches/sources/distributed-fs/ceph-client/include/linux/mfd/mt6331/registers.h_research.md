<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mt6331/registers.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/mt6331/registers.h

This MT6331 register header maps the PMIC into symbolic 16-bit offsets. It includes startup registers, hardware/software ID and top status/control/test registers, clock/reset/interrupt control and type/status registers, DEW diagnostics and cipher/CRC registers, buck global and VDVFS11/12/13/14 regulator controls, VGPU, VCORE1/2, VIO18, buck calibration, zero-cross and current sinks, analog/system/digital LDO controls, OTP output/value ranges, RTC mix, extensive audio analog/digital/MAD registers, AUXADC data/status/request/control registers, and accessory-detect controls.

No runtime code is implemented. The MFD core and child drivers use these constants with regmap: IRQ code uses `INT_*`, regulator code uses buck/LDO blocks, audio drivers use `AUD*`, ADC code uses `AUXADC_*`, and accdet uses `ACCDET_*`. Hardware registers hold all state; this header is a naming layer for address stability.

Dependencies include `mt6331/core.h`, MediaTek PMIC regmap, and block-specific child drivers. Risks include large offset surface, gaps in register sequences, sensitive OTP/test/DEW registers, and dependence on exact 16-bit address spacing. Combined with the core-header typo in `MT6331_IRQ_CON1_BITS`, IRQ-bank users need compile coverage. Test signals include symbol resolution for regulator/audio/AUXADC/accessory drivers, regmap access tests for each block, IRQ status/type handling, and read-only/volatile range validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/mt6331/registers.h -->
