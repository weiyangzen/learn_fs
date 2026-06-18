# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/ref/gh100/dev_therm.h

## Purpose
Defines the GH100 thermal I2CS scratch register and FSP boot-complete status aliases.

## Important APIs, Types, And Functions
Exports `NV_THERM_I2CS_SCRATCH`, data field definitions, and `FSP_BOOT_COMPLETE_STATUS` values for success `0xff` and failure `0x00`.

## Control Flow
Declarative only. Firmware code reads the scratch register as a boot-status mailbox.

## State And Persistence
Scratch data is hardware/firmware state that persists until changed or reset.

## Dependencies And Integration Points
Integrated with GH100 FSP/GSP initialization and thermal PRI register access.

## Risks
The GH100 address differs from GB202; classifying statuses too loosely can hide failed firmware boot.

## Test Signals
FSP boot-completion logs, timeout behavior, and scratch register dumps are useful validation.
