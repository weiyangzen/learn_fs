# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_fw_config.h

## Purpose
This header defines the compact firmware-object mapping format used by Gen4 and Gen6 hardware-data files to load the right UOF image onto the right AE mask.

## Important APIs, Types, And Functions
`enum adf_fw_objs` names firmware object roles: symmetric, asymmetric, compression, admin, combined crypto, and wireless crypto. `struct adf_fw_config` pairs an `ae_mask` with one enum object. There are no functions.

## Control Flow
No executable flow exists. Hardware-data files build static arrays of `struct adf_fw_config`, then common firmware loading iterates through hardware-data callbacks to map object IDs to firmware names and AE masks.

## State And Persistence Behavior
No mutable state exists. Static firmware config arrays persist as read-only module data.

## Dependencies And Integration Points
It integrates `adf_accel_engine.c` firmware loading with generation-specific service layouts in 4xxx and 6xxx hardware-data files.

## Risks
Enum ordering must match firmware-name arrays in hardware-data files. Missing or incorrect object roles can load the wrong firmware image or leave service/admin AEs unloaded.

## Test Signals
Firmware load for each service mix, invalid object handling, AE mask coverage, and algorithm exposure matching loaded firmware validate this header.
