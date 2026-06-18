# sources/distributed-fs/ceph-client/arch/sparc/kernel/of_device_common.h

Purpose: Declares shared SPARC Open Firmware bus-translation helpers and the `struct of_bus` descriptor used by 32-bit and 64-bit OF device scanners.

Important APIs/types/functions: `of_read_addr()` folds big-endian address cells into a `u64`. Declarations cover default bus cell counting, range checks, default mapping, default flags, SBUS matching, and SBUS cell counting. `OF_MAX_ADDR_CELLS` caps translated address arrays at four cells. `struct of_bus` names a bus, address property, optional matcher, cell counter, range mapper, and resource-flag function.

Control flow: There is no runtime control flow beyond the inline `of_read_addr()` loop. Architecture-specific scanners build ordered arrays of `struct of_bus` and invoke these callbacks while walking parent ranges.

State and persistence: The header owns no state; it defines callback contracts and constants.

Dependencies and integration points: It is consumed by `of_device_common.c`, `of_device_32.c`, and `of_device_64.c`, and depends on OF device-node types and Linux resource flag conventions.

Risks and test signals: The four-cell cap must match all supported SPARC firmware address formats. `of_read_addr()` assumes cells are already CPU-endian values supplied by OF helpers. Build tests for both SPARC32 and SPARC64 OF scanners and resource translation tests exercise this header.
