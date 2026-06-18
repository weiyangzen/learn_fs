
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/dispnv04/i2c/encoder_i2c.h

## Purpose
Defines Nouveau's generic wrapper for external display encoders connected over I2C, allowing GPU-specific code to call lower-level encoder drivers through a DRM encoder object.

## Important APIs, types, and functions
- `struct nouveau_i2c_encoder_funcs` contains callbacks for config, destroy, DPMS, save/restore, mode_fixup, prepare/commit, mode_set, detect, get_modes, create_resources, set_property, get_slave_funcs, and set_clock_mode.
- `struct nouveau_i2c_encoder` embeds `struct drm_encoder`, callback pointers, private data, and the backing `struct i2c_client`.
- `nouveau_i2c_encoder_init()` creates/initializes an I2C-backed encoder.
- `get_encoder_i2c_funcs()` and `nouveau_i2c_encoder_get_client()` are inline accessors.
- `struct nouveau_i2c_encoder_driver` wraps an `i2c_driver` plus `encoder_init`.
- `nouveau_i2c_encoder_destroy()` unregisters the I2C client, clears the pointer, and releases the driver module.
- Wrapper prototypes expose mode_fixup, detect, save, and restore.

## Control flow
The common DRM CRTC code calls normal DRM encoder hooks. Nouveau's upper layer wraps those calls and forwards them to `nouveau_i2c_encoder_funcs` only when the I2C encoder is selected for a connector. Driver initialization creates an I2C client and asks the encoder driver to populate function pointers and private data. Destroy unregisters the I2C client and drops the module reference.

## State and persistence
Persistent state lives in `struct nouveau_i2c_encoder`: the DRM encoder base, callback table pointer, implementation-private data, and I2C client. Device register state persists in the external encoder and is handled by save/restore/mode_set callbacks.

## Dependencies and integration points
Depends on Linux I2C and DRM CRTC/encoder headers. It is used by CH7006, SIL164, and similar dispnv04-era external encoder drivers.

## Risks
The callback surface is broad and many callbacks are optional, so wrapper code must null-check carefully. `nouveau_i2c_encoder_destroy()` assumes a live `client->dev.driver` and owner; calling it after partial teardown would be unsafe. Lifetime must balance `i2c_unregister_device()` and `module_put()`.

## Test signals
External encoder probe, mode detection, mode setting, DPMS, suspend/resume save/restore, and module unload paths are the key tests. Build coverage catches callback signature drift.
