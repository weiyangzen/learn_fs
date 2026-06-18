# Research: sources/distributed-fs/ceph-client/include/linux/mfd/max77705-private.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max77705-private.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/max77705-private.h

**Purpose:** Internal register and field definitions for the MAX77705 PMIC family, covering top-system, charger, fuel gauge, RGB LED, haptics, revision, and interrupt source bits.

**Important APIs and types:** Defines source IRQ bits, PMIC revision masks, main control and haptic config bits, system IRQ masks, RGB LED blink timing constants, hardware revision enum, PMIC/charger/fuel-gauge/RGB LED register enums, and charger battery/charge state enums.

**Control flow:** Parent and child drivers use source bits to demultiplex PMIC/top/charger/fuel-gauge/USBC interrupts, then access relative charger/LED register blocks and absolute PMIC/fuel-gauge addresses.

**State and persistence:** Hardware registers retain PMIC control, charger policy/status, fuel-gauge measurements, LED brightness/blink, and haptic mode. This header has no runtime struct.

**Dependencies and integration:** Uses bit macros expected from including contexts and integrates with the shared MAX77693-family state, charger/power-supply, fuel-gauge, RGB LED, haptic, and USBC-related drivers.

**Risks:** Charger register enum starts with a base plus relative offsets, so consumers must add the base consistently. RGB blink timing constants encode nonlinear steps and need conversion tests. Fuel-gauge register names are generic, increasing collision risk if included broadly.

**Test signals:** Register-address tests for base-relative blocks, revision decode tests, charger/fuel-gauge state decode tests, RGB blink conversion tests, and interrupt-source demux tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max77705-private.h -->
