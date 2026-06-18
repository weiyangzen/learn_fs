## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/subdev.c

### Purpose
`subdev.c` implements the common lifecycle, reference management, logging identity, and callback dispatch for NVKM subdevices and engines embedded in a device.

### Important APIs, types, and functions
Key APIs include `nvkm_subdev_intr()`, `nvkm_subdev_info()`, `nvkm_subdev_preinit()`, `nvkm_subdev_oneinit()`, `nvkm_subdev_init()`, `nvkm_subdev_fini()`, `nvkm_subdev_ref()`, `nvkm_subdev_unref()`, `nvkm_subdev_del()`, `nvkm_subdev_disable()`, `__nvkm_subdev_ctor()`, and `nvkm_subdev_new_()`. `nvkm_subdev_type[]` is generated from `core/layout.h`.

### Control flow
Construction records the device, type, instance, generated name, debug level, initial refcount, and device list membership. `preinit`, `oneinit`, `init`, and `fini` dispatch optional callbacks with timing and logging. `oneinit` is one-shot. `init` is skipped when already enabled or when no users hold references. `fini` marks the subdevice disabled and resets it through MC. Ref/unref transitions call init on first reference and fini when the final reference drops.

### State and persistence behavior
Each subdevice keeps a refcount, mutex, enabled flag, interrupt handle, list node, `pself` backpointer, and oneinit flag. The device owns the subdevice list. `nvkm_subdev_disable()` nulls the owning device pointer slot and deletes the matching subdevice.

### Dependencies
It depends on `core/subdev.h`, `core/device.h`, option parsing for debug levels, and MC reset support from `subdev/mc.h`.

### Integration points
Every NVKM subdevice and engine constructor calls this layer, and `device/base.c` drives these lifecycle hooks during device bring-up, suspend, runtime suspend, and teardown. Logging macros in `subdev.h` depend on the debug level set here.

### Risks
Reference transitions must hold `use.mutex` correctly; otherwise init/fini can race with users. Constructors add the subdevice to the device list before later setup finishes, so failure cleanup must delete partially built subdevices. `nvkm_subdev_fini()` ignores non-suspend callback failures after logging, which is intentional for poweroff but can hide shutdown errors. MC reset after fini is a hardware-visible side effect.

### Test signals
Use refcount transition tests, bind/unbind or module unload, suspend and runtime-suspend failure injection, oneinit idempotence checks, debug option parsing per subdevice name, and interrupt callback smoke tests.
