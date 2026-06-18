<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/nouveau_i2c_encoder.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/nouveau_i2c_encoder.c

## Purpose
This file provides the common bridge between Nouveau DRM encoders and slave encoder chips exposed as Linux I2C drivers.

## Important APIs, Types, and Functions
`nouveau_i2c_encoder_init` creates and binds an I2C client, holds the module owner, initializes Nouveau encoder callbacks, and applies optional platform config. Wrapper callbacks are `nouveau_i2c_encoder_mode_fixup`, `nouveau_i2c_encoder_detect`, `nouveau_i2c_encoder_save`, and `nouveau_i2c_encoder_restore`.

## Control Flow
Initialization requests the module by I2C type name, creates a client on the given adapter, verifies a driver bound, takes a module reference, records the client in `nouveau_i2c_encoder`, converts the I2C driver to a `nouveau_i2c_encoder_driver`, runs its `encoder_init`, and applies platform data through `set_config`. Failure unwinds the module ref and I2C device. Wrapper functions delegate to the slave callback table, defaulting mode fixup to true if absent.

## State and Persistence Behavior
The function installs `encoder->i2c_client`, `encoder_i2c_funcs`, and driver-private state allocated by the slave init. Module references persist while the encoder is alive; slave destroy callbacks are expected to unregister clients and release resources through `nouveau_i2c_encoder_destroy`.

## Dependencies and Integration Points
It depends on Linux I2C module autoloading, Nouveau's `encoder_i2c` abstraction, CH7006/SIL164-style drivers, and DRM encoder helper callbacks used by TV/DFP creation paths.

## Risks
Lifecycle correctness depends on slave `destroy` implementations releasing the module/device via the common destroy helper. `i2c_new_client_device` failures or unbound clients must be handled carefully. Wrappers assume callback pointers such as detect/save/restore are valid, so every slave driver must provide them when routed through helper tables.

## Test Signals
Test CH7006 and SIL164 module autoload, probe failure unwind, platform-data application, save/restore delegation, detect delegation, optional mode-fixup absence, and module unload with active/unbound encoders.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/nouveau_i2c_encoder.c -->
