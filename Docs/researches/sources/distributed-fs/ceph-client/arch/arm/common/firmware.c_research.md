<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/firmware.c -->
# sources/distributed-fs/ceph-client/arch/arm/common/firmware.c

## Purpose
Provides the default ARM firmware operations pointer.

## Important APIs/types/functions
- `static const struct firmware_ops default_firmware_ops;`
- Global `const struct firmware_ops *firmware_ops = &default_firmware_ops;`

## Control flow
There is no function flow in this file. Platform code can replace or use `firmware_ops` through declarations in `asm/firmware.h`.

## State and persistence behavior
The global pointer is process-wide kernel state representing the active firmware operation table. The default table is empty/zeroed.

## Dependencies and integration points
Depends on `asm/firmware.h` and firmware-aware ARM platform code. Used by suspend, PSCI, or platform firmware hooks where available.

## Risks and edge cases
Callers must tolerate absent operations when `firmware_ops` points to the default zero table. Replacing the pointer must be done early enough and with lifetime-stable storage.

## Test signals
Compile ARM platforms with and without firmware providers; boot logs and suspend/CPU bring-up paths should show correct firmware hook behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/firmware.c -->
