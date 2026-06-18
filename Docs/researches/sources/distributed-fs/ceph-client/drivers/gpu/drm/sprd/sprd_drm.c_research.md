# sources/distributed-fs/ceph-client/drivers/gpu/drm/sprd/sprd_drm.c

Purpose: master DRM driver for the Unisoc display subsystem. It allocates the DRM device, binds DPU/DSI components, initializes mode config, vblank, polling, registration, and platform driver lifecycle.

Important APIs and types: `struct sprd_drm` embeds `drm_device`. `sprd_drm_bind()` is the component master bind callback. `sprd_drm_mode_config_init()` sets 0..8192 size limits and DRM atomic/GEM callbacks. `sprd_drm_drivers[]` registers the master, DPU, and DSI platform drivers together.

Control flow: module init skips when firmware drivers only are requested, then registers all platform drivers. The master probe calls `drm_of_component_probe()`. Bind allocates the DRM device, initializes mode config, binds all components, initializes vblank for created CRTCs, resets state, starts HPD polling, and registers the DRM device. Unbind unregisters DRM, stops polling, and unbinds components. Shutdown calls atomic helper shutdown if the DRM device exists.

State and persistence: master state is the devm-managed `sprd_drm`/`drm_device`; subcomponent state is owned by DPU/DSI components. No persistent storage.

Dependencies and integration: depends on OF component framework, DRM DMA GEM, atomic helpers, vblank, KMS polling, and external `sprd_dpu_driver`/`sprd_dsi_driver` symbols.

Risks: on bind failure after component binding, cleanup must unbind all components; the code handles this for vblank/register failures. `drm_kms_helper_poll_init()` is used even though the attached DSI panel may not have HPD. Master max dimensions are broad and not tied to hardware limits.

Test signals: component probe ordering, bind failure unwinding, module init/exit, firmware-driver-only boot, and shutdown with/without completed bind.
