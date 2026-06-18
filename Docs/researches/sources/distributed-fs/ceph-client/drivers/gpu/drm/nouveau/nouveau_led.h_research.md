
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_led.h

## Purpose
Declares Nouveau LED support and provides no-op stubs when the LED class is not reachable.

## Important APIs, Types, and Functions
`struct nouveau_led` stores the owning DRM device and `struct led_classdev`. `nouveau_led()` returns the per-device LED pointer. The header exposes `nouveau_led_init()`, `nouveau_led_suspend()`, `nouveau_led_resume()`, and `nouveau_led_fini()` when `CONFIG_LEDS_CLASS` is reachable, otherwise inline stubs return success or do nothing.

## Control Flow
The conditional declarations let `nouveau_drm.c` call LED lifecycle hooks unconditionally. Compile-time configuration determines whether those calls perform real LED registration/control or no-op.

## State and Persistence
The header defines the wrapper state that persists in `drm->led` only when LED support is active and hardware registration succeeds.

## Dependencies and Integration Points
Includes the main Nouveau driver header and Linux LED class definitions. Integrated from DRM device init/fini and PM suspend/resume.

## Risks and Test Signals
Risks are low but include configuration-dependent build coverage and accidental dereference of `drm->led` when stubs are active. Test signals include builds with LED class built-in, modular, and disabled; device init/fini on hardware without a logo LED; and PM paths with no registered LED.
