<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gpio/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gpio/base.c

## Purpose
Implements the common GPIO subdevice: BIOS lookup, set/get helpers, interrupt event dispatch, initialization power checks, and teardown.

## Important APIs, Types, And Functions
Exports `nvkm_gpio_reset`, `nvkm_gpio_find`, `nvkm_gpio_set`, `nvkm_gpio_get`, and `nvkm_gpio_new_`. Defines event callbacks `nvkm_gpio_intr_init/fini`, ISR `nvkm_gpio_intr`, lifecycle `nvkm_gpio_init/fini/dtor`, Apple reset DMI quirk, and external-power GPIO checks.

## Control Flow
Callers locate GPIO lines by tag/line via DCB BIOS records or an Apple TV GPIO quirk. Set/get map logical states through BIOS `log[]` bits and call generation `drive`/`sense`. Interrupt subscription masks line/type pairs; the subdev ISR reads hi/lo status and notifies `nvkm_event`. Init optionally resets GPIOs on selected Apple hardware and checks external power warning GPIOs unless `NvPowerChecks=0`.

## State And Persistence
Stores `struct nvkm_gpio`, function table, and event object. It changes hardware interrupt masks and GPIO output direction/state through generation hooks.

## Dependencies And Integration Points
Depends on BIOS DCB GPIO parsers, DMI, NVKM events, config options, and generation function tables. Used by display, memory reclocking, thermal, and power-management paths.

## Risks And Edge Cases
Wrong BIOS GPIO metadata can invert or drive pins incorrectly. Power checks can block driver init if GPIOs report missing power. Interrupt masks must be cleared on fini to prevent stale notifications.

## Test Signals
Successful GPIO lookup/set/get, hotplug or GPIO event delivery, absence of false power-cable errors, and clean interrupt masking during shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gpio/base.c -->
