# sources/distributed-fs/ceph-client/include/linux/mfd/intel_soc_pmic_bxtwc.h

Purpose: This header maps Intel Broxton Whiskey Cove PMIC device addresses and selected charger, USB, wake, and thermal registers.

Important APIs, types, and constants: It defines three PMIC I2C device addresses and combined address/register macros for chip ID/version, charger IRQ/control/status, battery thermal zone, USB path/PHY/ID/source-detect/debug registers, wake-source registers, charger RTT address/data, and thermal interrupt/zone high/low registers. `BXTWC_USBIDEN_MASK` identifies USB-ID enable.

Control flow, state, and persistence: There is no code. Consumers use these constants with the common Intel SoC PMIC regmap/SCU access path to configure USB/charger/thermal behavior and decode wake sources. State persists in PMIC registers and interrupt latches.

Dependencies and integration points: It integrates with Intel SoC PMIC core, charger/power-supply drivers, USB role/source detection, thermal zones, and wakeup handling.

Risks and test signals: Risks include wrong combined device/register addressing, overlapping status aliases such as charger status and USB path at the same address, and thermal-zone register pair ordering errors. Test signals include charger attach/detach IRQs, USB ID/source detection, wake-source readback, thermal threshold tests, and chip ID/version probe checks.
