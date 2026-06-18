## sources/distributed-fs/ceph-client/arch/arm/tools/gen-mach-types

### Purpose
AWK generator that converts ARM `mach-types` rows into `include/generated/asm/mach-types.h`.

### Important APIs, Types, And Functions
The script recognizes non-comment rows with either four fields, including a registered numeric machine type, or three fields for unregistered machines. It emits `MACH_TYPE_*` constants and `machine_is_*()` macros.

### Control Flow
During `BEGIN`, it initializes a row count. Each valid line stores generated symbol names, config symbols, and optional numbers. In `END`, it prints the header guard, declares `__machine_arch_type`, emits registered `#define MACH_TYPE_*` values, then emits config-gated `machine_is_*()` predicates and always-false predicates for unregistered machines.

### State, Persistence, And Dependencies
State is AWK arrays accumulated from the input file. The persistent output is a generated C header. It depends on row ordering and field layout in `arch/arm/tools/mach-types`.

### Integration Points
Board and platform code include `mach-types.h` to select legacy machine descriptions and compare the boot machine ID.

### Risks
Malformed rows silently disappear unless they have three or four fields. Name collisions in machine or config names produce broken C macros. Registered numeric IDs are ABI-like bootloader contracts.

### Test Signals
Regenerate `mach-types.h`, compile platform code that uses `machine_is_*()`, and diff output after `mach-types` changes.
