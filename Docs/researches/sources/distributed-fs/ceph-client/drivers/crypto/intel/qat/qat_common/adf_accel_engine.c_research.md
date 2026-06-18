# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_accel_engine.c

## Purpose
This file owns QAT accelerator-engine firmware loading, reset, start, stop, and release. It bridges Linux firmware blobs to the QAT UOF/MMP loader and hardware abstraction layer.

## Important APIs, Types, And Functions
Public functions are `adf_ae_init()`, `adf_ae_shutdown()`, `adf_ae_fw_load()`, `adf_ae_fw_release()`, `adf_ae_start()`, and `adf_ae_stop()`. The key helper `adf_ae_fw_load_images()` loads multi-object firmware by calling hardware-data callbacks `uof_get_num_objs()`, `uof_get_name()`, and `uof_get_ae_mask()`.

## Control Flow
`adf_ae_init()` allocates `adf_fw_loader_data`, initializes HAL, resets AEs, waits any chip-specific reset delay, and clears reset. `adf_ae_fw_load()` requests MMP and UOF firmware, loads MMP, then either loads per-object images for newer hardware or a single UOF image for older hardware. `adf_ae_start()` starts firmware through HAL and logs AE count. `adf_ae_stop()` stops all enabled AEs. Release/deinit frees mapped UOF objects, deinitializes HAL, and releases firmware.

## State And Persistence Behavior
State persists in `accel_dev->fw_loader` while the device is initialized/loaded. Firmware buffers are kernel firmware references and are released during `adf_ae_fw_release()`. No persistent storage is written.

## Dependencies And Integration Points
It depends on Linux firmware loading, PCI device context, QAT HAL, UOF loader, hardware-data firmware callbacks, and common lifecycle status bits set elsewhere in `adf_init.c`.

## Risks
Error paths call `adf_ae_fw_release()`, so partial loader state must be valid. Multi-object firmware selection depends on correct AE masks and object names. Missing firmware files or bad MMP/UOF contents prevent device start. Reset delay and HAL deinit ordering are hardware-sensitive.

## Test Signals
Signals include successful firmware requests, MMP/UOF load logs, per-object load for Gen4/Gen6, AE start/stop counts matching `ae_mask`, failure behavior for missing firmware, and clean reload after reset.
