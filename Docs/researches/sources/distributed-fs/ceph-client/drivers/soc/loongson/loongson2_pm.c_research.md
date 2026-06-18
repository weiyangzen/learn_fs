
# sources/distributed-fs/ceph-client/drivers/soc/loongson/loongson2_pm.c

## Purpose
Loongson-2 power-management controller driver. It handles PM wake/status registers, registers a power-button input device, services PM IRQs, configures suspend-to-RAM entry when firmware address is provided, and populates PM child devices.

## Important APIs, Types, and Functions
- Global `struct loongson2_pm` stores register base, input device, and suspended flag.
- Helpers clear status and enable PM IRQ bits.
- Suspend hooks: `loongson2_suspend_begin()`, `loongson2_suspend_enter()`, and valid-state check.
- `loongson2_power_button_init()` creates input device and wake IRQ.
- `loongson2_pm_irq_handler()` reports KEY_POWER unless suspended.
- `loongson2_pm_probe()` maps registers, configures suspend address, requests IRQ, enables status, sets suspend ops, and populates children.

## Control Flow
Probe maps resource 0, obtains IRQ 0, optionally reads `loongson,suspend-address` into `loongson_sysconf.suspend_addr`, initializes/registers a power button input device, requests shared IRQ, enables PM1 interrupt and power-button enable bits, clears status, registers suspend ops if suspend address exists, and populates child nodes. IRQ handler reads PM1 status, reports press/release when not suspended and power-button status is set, then clears PM/GPE status. Suspend entry clears status, calls architecture suspend/resume hooks, re-enables PM IRQ, and marks resume via firmware.

## State and Persistence
Global singleton state persists for the driver lifetime. Hardware PM status/enable registers persist until reset/rewrite. Input device and wake IRQ persist after probe. The firmware suspend address is stored globally in `loongson_sysconf`.

## Dependencies and Integration Points
Depends on LoongArch suspend hooks, input subsystem, wake IRQ helpers, OF platform, PM core suspend ops, and compatible `loongson,ls2k0500-pmc`.

## Risks
- `loongson2_power_button_init()` checks `if (!dev)` after `input_allocate_device()` instead of checking `button`, so allocation failure would dereference NULL.
- Global singleton state assumes one PM controller.
- If suspend address is missing, S3 is unavailable but probe continues.
- The input device parent is set to NULL, which may affect device hierarchy/power management expectations.

## Test Signals
Probe with/without suspend address, input allocation failure, IRQ request failure, power-button event reporting, suspended IRQ suppression, wake IRQ setup, suspend/resume path, child population, and PM status clear behavior.
