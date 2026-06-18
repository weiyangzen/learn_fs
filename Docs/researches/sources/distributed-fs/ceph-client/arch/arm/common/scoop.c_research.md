<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/scoop.c -->
# sources/distributed-fs/ceph-client/arch/arm/common/scoop.c

## Purpose
Platform driver and GPIO/register helper support for Sharp SCOOP interface chips used by Sharp PDAs, including PCMCIA linkage.

## Important APIs/types/functions
- Global `platform_scoop_config`.
- Core state `struct scoop_dev` with MMIO base, GPIO chip, lock, suspend masks, and saved GPIO output.
- Exported helpers: `reset_scoop()`, `read_scoop_reg()`, and `write_scoop_reg()`.
- GPIO callbacks: `scoop_gpio_set()`, `scoop_gpio_get()`, `scoop_gpio_direction_input()`, and `scoop_gpio_direction_output()`.
- Platform flow: `scoop_probe()`, `scoop_remove()`, `scoop_suspend()`, `scoop_resume()`.

## Control flow
Probe maps MMIO, initializes reset/control registers from platform `scoop_config`, stores suspend masks, and optionally registers a 12-line GPIO chip. GPIO operations lock around GPCR/GPWR writes. Suspend records GPWR and applies board-provided clear/set masks; resume restores GPWR.

## State and persistence behavior
Runtime state is in SCOOP registers, GPIO chip registration, platform driver data, and saved `scoop_gpwr` across suspend. No disk state exists.

## Dependencies and integration points
Depends on platform resources/data, `asm/hardware/scoop.h`, gpiolib, platform driver core, and Sharp PDA PCMCIA/board code.

## Risks and edge cases
Probe assumes platform data is present and dereferences it. Legacy `gpiochip_add_data()` cleanup must match remove ordering. The GPIO bit numbering starts at hardware PA11 and uses `offset + 1`, so off-by-one mistakes affect real pins.

## Test signals
Boot Sharp PDA platforms, verify SCOOP reset, exported register helpers, GPIO direction/output/input, PCMCIA integration, and suspend/resume GPIO retention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/scoop.c -->
