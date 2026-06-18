# sources/distributed-fs/ceph-client/drivers/soundwire/amd_init.h

## Purpose
Provides private declarations shared by the AMD SoundWire init library and manager driver. It exposes the manager startup function and a small MMIO read-modify-write helper used for ACP shared registers.

## Important APIs, Types, and Functions
The header declares `int amd_sdw_manager_start(struct amd_sdw_manager *amd_manager);` and defines `amd_updatel(void __iomem *mmio, int offset, u32 mask, u32 val)`. It includes `<linux/soundwire/sdw_amd.h>` for `struct amd_sdw_manager` and AMD SoundWire resource definitions.

## Control Flow
There is no standalone control flow. Callers use `amd_updatel()` to read a 32-bit register, clear bits in `mask`, OR in `val`, and write the result back. `amd_init.c` calls `amd_sdw_manager_start()` after creating a platform device whose driver has populated drvdata.

## State and Persistence Behavior
The helper mutates MMIO register state directly. It has no locking of its own; callers must hold the appropriate ACP shared lock where required. The function does not cache state or validate masks.

## Dependencies and Integration Points
This header ties `amd_init.c` and `amd_manager.c` together and depends on Linux I/O accessors. `amd_updatel()` is used for ACP pad and interrupt-control registers in both AMD source files.

## Risks
Because `amd_updatel()` is a raw read-modify-write helper, concurrent callers can lose updates unless they use `acp_sdw_lock` around shared ACP registers. The helper accepts any offset and mask, so incorrect constants directly program hardware. The declaration creates a private compile-time dependency from the init library to the manager driver.

## Test Signals
Compile coverage for `soundwire-amd.o`, register writes under single-link and dual-link startup, lockdep review around shared ACP register updates, and failure injection around `amd_sdw_manager_start()` users are useful checks.
