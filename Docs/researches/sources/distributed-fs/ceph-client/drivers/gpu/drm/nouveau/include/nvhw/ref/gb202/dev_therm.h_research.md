# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/ref/gb202/dev_therm.h

## Purpose
Defines the GB202 thermal I2CS scratch register used here as an FSP boot-complete status mailbox.

## Important APIs, Types, And Functions
Exports `NV_THERM_I2CS_SCRATCH`, its `DATA` field, and aliases for `NV_THERM_I2CS_SCRATCH_FSP_BOOT_COMPLETE_STATUS` with success `0xff` and failure `0x00`.

## Control Flow
Declarative only. Boot or firmware-management code polls/reads this register to decide whether FSP boot completed successfully.

## State And Persistence
The scratch value is firmware/hardware state and persists until firmware or the driver overwrites it or the GPU resets.

## Dependencies And Integration Points
Integrated with GSP/FSP initialization and thermal/PRI register access paths.

## Risks
Using the GH100 address on GB202 or vice versa would poll the wrong register. Treating any nonzero as success would differ from the explicit `0xff` definition.

## Test Signals
FSP boot logs, timeout paths, and register traces showing success/failure status are useful signals.
