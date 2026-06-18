# sources/distributed-fs/ceph-client/include/linux/mfd/mt6359/registers.h

## Purpose

This header provides the MT6359 PMIC register map and regulator bitfield contract used by MFD, IRQ, RTC, regulator, input, AUXADC, and sound consumers. Unlike the MT6358 register header, it includes many derived `RG_*`, `DA_*`, mask, and shift macros directly used by `mt6359-regulator.c`.

## Important APIs, Types, and Functions

The macro namespace includes chip and top interrupt addresses (`MT6359_SWCID`, `MT6359_TOP_INT_STATUS0`), RTC and secure RTC offsets, PSC/BM/HK/BUCK/LDO/AUD interrupt registers, buck control/debug/ELR addresses for VPU, VCORE, VGPU11, VMODEM, VPROC1/2, VS1/2, and VPA, LDO control/monitor blocks for RF, connectivity, camera, SIM, USB, VSRAM, VM18, VUFS and related rails, analog `*_ANA_CON0` addresses, and regulator helper macros such as `MT6359_RG_BUCK_VCORE_VOSEL_ADDR`, `MT6359_DA_VCORE_VOSEL_MASK`, `MT6359_RG_LDO_VSIM1_EN_SHIFT`, and `MT6359_RG_VBBCK_VOSEL_MASK`.

## Control Flow

No code runs in the header. Runtime flow is descriptor-driven: regulator registration builds descriptors from these address/mask/shift macros, regulator ops call regmap update/read helpers, IRQ setup uses top interrupt register addresses, and MFD core uses `MT6359_SWCID` plus IRQ constants from `mt6359/core.h` to instantiate child devices.

## State and Persistence Behavior

The mapped state is PMIC hardware state. Buck/LDO enable and voltage selections persist as PMIC register values until changed or reset; monitor `DA_*` addresses expose hardware-observed enable/voltage state; RTC registers hold time/alarm/power state; top interrupt registers latch and mask events. The header itself is stateless.

## Dependencies and Integration Points

Direct consumers include `drivers/regulator/mt6359-regulator.c`, `drivers/mfd/mt6358-irq.c`, `drivers/mfd/mt6397-core.c`, `drivers/input/keyboard/mtk-pmic-keys.c`, `drivers/iio/adc/mt6359-auxadc.c`, and MT6359 codec/accessory drivers. The register map also provides the base comparison point for `mt6359p/registers.h`, whose macros override shifted MT6359P addresses while reusing the same regulator driver.

## Risks and Edge Cases

Address, mask, and shift triples must remain synchronized; a correct address with an MT6359P shift, or a correct mask with the wrong monitor address, can produce silent voltage or status errors. Sparse register groups and multi-enable rails such as VCN33 and VUSB require descriptor care. Several `DA_*` monitor registers are read-only status paths, while `RG_*` registers are control paths; confusing them breaks set operations. Cross-including MT6359P macros in generic MT6359 code needs chip-version selection.

## Test Signals

Build and probe `mt6359-regulator`, verify every registered regulator can read status, test buck mode transitions and voltage changes, validate `TMA_KEY`-gated MT6359P paths are not used on plain MT6359, run RTC alarm and PMIC key IRQ tests, and use regmap debugfs traces to confirm descriptor operations hit expected `RG_*` and `DA_*` addresses.
