# sources/distributed-fs/ceph-client/arch/arm/include/asm/firmware.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/firmware.h` defines firmware operation
tables for SoC reset, idle, suspend, SMP boot, and hotplug hooks. It is part of the ARM kernel-
architecture compatibility layer imported in the Ceph client source tree, so its direct consumers
are kernel architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol
logic.

### Important APIs, Types, And Functions
macros: `call_firmware_op`; types: `firmware_ops`; functions/prototypes: `BUG_ON`, `firmware_ops`.
The file is 79 lines / 1728 bytes, and the exported surface is primarily an include-time contract
for other kernel files.

### Control Flow
This header mostly supplies constants, declarations, or compile-time glue; runtime flow is driven by
the C or assembly files that include it.

### State, Persistence, And Dependencies
Caller-visible state is represented by `firmware_ops`. External state or implementation hooks
include `firmware_ops`. There is no userspace filesystem persistence in this file; persistence is
either kernel memory, CPU register state, hardware register state, or generated ABI values. Direct
includes are `linux/bug.h`. It integrates with generic Linux ARM architecture code through include-
time contracts rather than a standalone translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `firmware.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
the main risk is ABI drift: constants and prototypes must stay synchronized with the implementation
files that include this header.

### Test Signals
compile coverage across representative ARM configs; ensure all include users still build with
sparse/objtool-style diagnostics where available.
