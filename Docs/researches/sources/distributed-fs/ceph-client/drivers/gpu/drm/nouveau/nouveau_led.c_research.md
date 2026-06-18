
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_led.c

## Purpose
Registers and controls the NVIDIA logo LED through the Linux LED class when a matching BIOS GPIO function exists. Brightness is implemented by programming a display SOR PWM divider and duty register.

## Important APIs, Types, and Functions
External lifecycle functions are `nouveau_led_init()`, `nouveau_led_suspend()`, `nouveau_led_resume()`, and `nouveau_led_fini()`. LED callbacks are `nouveau_led_get_brightness()` and `nouveau_led_set_brightness()`.

## Control Flow
Initialization checks for an NVKM GPIO subdevice, searches for `DCB_GPIO_LOGO_LED_PWM`, allocates `drm->led`, fills a `led_classdev` named `nvidia-logo`, and registers it. Brightness reads register `0x61c880` as divider and `0x61c884` as duty, scaling to `LED_FULL`. Brightness writes use a 27 MHz input clock and 100 Hz PWM frequency, compute divider/duty, and write the SOR PWM registers. Suspend/resume forward to LED class helpers; fini unregisters and frees the wrapper.

## State and Persistence
Persistent state is `struct nouveau_led` stored in `drm->led`, containing the DRM device and LED class device. Actual brightness state is in hardware PWM registers.

## Dependencies and Integration Points
Depends on Linux LED class support, NVKM GPIO discovery, and NVIF register access. Called from the DRM device init/fini and PM paths. The code assumes the logo LED is controlled by `PDISPLAY.SOR[1].PWM` and that Nouveau does not otherwise manage those registers.

## Risks and Test Signals
Risk comes from direct magic register access, hardware assumptions about the PWM controller, runtime PM interactions during sysfs brightness access, and absence of locking around register updates. Test signals include devices with and without logo LED GPIO, LED sysfs brightness read/write, suspend/resume preserving sane state, module unload, and GSP/non-GSP register access behavior.
