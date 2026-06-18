# sources/distributed-fs/ceph-client/drivers/pinctrl/samsung/pinctrl-samsung.h

## Purpose
This header defines the shared data model and constants used by the Samsung pinctrl family. It is the common contract for generic driver code, Exynos data and logic, and S3C64xx support.

## Important APIs, Types, and Macros
`enum pincfg_type` defines logical configuration fields: function, data, pull, drive, power-down function, and power-down pull. `PINCFG_PACK`, `PINCFG_UNPACK_TYPE`, and `PINCFG_UNPACK_VALUE` pack Samsung-specific config type/value pairs into pinconf words. Pull and GPIO function constants define common Exynos/S5P values for input/output and pull states.

Core types are `struct samsung_pin_bank_type` for bit widths and register offsets, `struct samsung_pin_bank_data` for static bank descriptions, `struct samsung_pin_bank` for runtime bank state, `struct samsung_retention_ctrl` and `struct samsung_retention_data` for pad retention, `struct samsung_pin_ctrl` for per-controller SoC data and callbacks, `struct samsung_pinctrl_drv_data` for driver runtime data, `struct samsung_pinctrl_of_match_data` for OF match payloads, `struct samsung_pin_group`, and `struct samsung_pmx_func`.

Macros `PIN_GROUP` and `PMX_FUNC` build static group/function descriptors, although this driver also dynamically creates one-pin groups and functions from DT. The header declares all SoC `*_of_data` symbols consumed by the common OF match table.

## Control Flow
The header itself has no execution. Its structures define how probe copies static SoC data into runtime banks, how pinctrl operations interpret register fields, how GPIO and IRQ code find per-bank state, and how suspend/resume callbacks are wired.

## State and Persistence
`struct samsung_pin_bank` is the key persistent runtime object. It stores register bases, offsets, EINT metadata, bank name, ID, pin base, fwnode, GPIO and IRQ objects, spinlock, and saved power-management register values. `struct samsung_pinctrl_drv_data` persists controller-wide arrays, clock, IRQ, registered pinctrl device, pin groups/functions, and retention control. `pm_save[PINCFG_TYPE_NUM + 1]` accounts for double CON registers on wide banks.

## Dependencies and Integration Points
The header depends on Linux pinctrl, pinmux, pinconf, consumer/machine, and GPIO driver definitions. It is included by the Samsung common driver and SoC-specific files. The extern declarations integrate Kconfig-selected SoC data with `pinctrl-samsung.c`.

## Risks
The packed config format uses only 8 bits for values, so new config fields needing larger values would require a different representation. `PIN_NAME_LENGTH` is fixed at 10; longer generated bank names could truncate pin names if not controlled. Structure comments and field names need to stay synchronized with SoC macro outputs; several features such as ExynosAuto explicit EINT offsets and GS101 filter offsets rely on optional fields being copied by probe.

## Test Signals
Compile coverage is the main header-level signal. Runtime signals include correct pin name generation, correct register bitfield programming for every `samsung_pin_bank_type`, successful IRQ domain association through `samsung_pin_bank`, and correct suspend/resume save slot usage on banks with more than 32 function bits.
