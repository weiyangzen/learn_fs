# Research: sources/distributed-fs/ceph-client/include/linux/mfd/max77693-private.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max77693-private.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/max77693-private.h

**Purpose:** Internal register, bitfield, charger-state, LED, MUIC, haptic, and IRQ definitions for MAX77693.

**Important APIs and types:** Register enums cover PMIC/charger/flash LED, MUIC, and haptic slaves. Macros define torch/flash currents and timeouts, charger defaults and fields, MUIC status/control masks, safeout bits, source IRQ bits, LED/top/charger/MUIC IRQ masks, and haptic config bits. Enums describe charger charging/battery states plus top-level and MUIC IRQ IDs.

**Control flow:** The parent IRQ handler reads source bits and dispatches to LED, top-system, charger, and MUIC regmap IRQ chips. Child charger, flash LED, MUIC, haptic, and regulator code uses register macros to configure each block.

**State and persistence:** No runtime struct is defined here; hardware register state controls charger policy, LED current/timeout, MUIC routing, haptic mode, and interrupt masks.

**Dependencies and integration:** Includes I2C and relies on common MFD state. Integrates with power-supply, extcon/MUIC, LED flash, haptic input, regulator, and IRQ subsystems.

**Risks:** Raw charger defaults encode policy in micro-units and minutes; drivers must convert carefully. `CHG_CNFG_01_PQEN_MAKS` appears misspelled, so users looking for `_MASK` may miss it. MUIC and charger IRQ names are similar but separate domains.

**Test signals:** Compile use of all mask macros, charger status decode tests, flash current/timeout conversion tests, MUIC switch routing tests, haptic mode tests, and source IRQ demultiplex tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/max77693-private.h -->
