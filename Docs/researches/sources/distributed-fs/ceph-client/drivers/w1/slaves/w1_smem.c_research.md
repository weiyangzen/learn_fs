# sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_smem.c

## Purpose
Simple 64-bit memory/ROM family registration for family IDs 0x01 and 0x81, covering devices such as DS2401/DS2411/DS1990 variants.

## Important APIs, Types, and Functions
Defines two `struct w1_family` objects without custom family ops. `w1_smem_init()` registers both families with rollback if the second registration fails. `w1_smem_fini()` unregisters both.

## Control Flow
Module init registers family 0x01, then 0x81. Since there are no `.fops`, discovered slaves get only the core W1 slave attributes (`name`, `id`) rather than device-specific sysfs files. Module exit unregisters both families, causing core reconnect handling for matching slaves.

## State and Persistence
No private state. The value of these devices is the immutable 64-bit ROM ID represented by core W1 slave identity.

## Dependencies and Integration Points
Depends on W1 family registration and module alias autoload for both family IDs.

## Risks and Test Signals
The driver is intentionally minimal; risk is mostly registration rollback and interaction with default-family fallback. Test module load/unload, discovery of both IDs, and that no custom attributes are expected beyond core W1 slave files.
