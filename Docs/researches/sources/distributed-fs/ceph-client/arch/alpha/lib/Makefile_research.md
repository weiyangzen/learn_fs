# sources/distributed-fs/ceph-client/arch/alpha/lib/Makefile

## Purpose
Kbuild library manifest for Alpha-specific runtime helper objects, selecting generic, EV6, and EV67 implementations. The source was read as part of `subset-b-000628` and contains 46 lines.

## Important APIs, Types, and Functions
Sets `asflags-y`, feature prefixes `ev6-$(CONFIG_ALPHA_EV6)` and `ev67-$(CONFIG_ALPHA_EV67)`, populates `lib-y`, and defines special assembly flags for divide/remainder objects built from `divide.S` or `ev6-divide.S`.

## Control Flow
Kbuild resolves CPU feature prefixes, adds objects for division, delays, memory/string, checksum, user-copy, page-copy, FP register, SRM callback/printing, and bit-scan helpers, then builds four divide/remainder objects from one selected source with `-DDIV`, `-DREM`, and `-DINTSIZE` combinations.

## State and Persistence Behavior
The persistent outputs are Alpha `lib.a`/built-in objects selected at build time. No runtime state is represented here.

## Dependencies
Depends on Kbuild, Alpha config symbols, corresponding `.S`/`.c` files, and exported helper symbols consumed across the kernel and modules.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
Wrong EV6/EV67 prefix selection can link duplicate or missing symbols. Divide-object flag combinations must match ABI names. Assembly flags must include kernel C flags for symbol/ABI compatibility.

## Test Signals
Build Alpha configs for generic, EV6, and EV67; run `nm` for expected helper symbols; verify no duplicate `memcpy`/`memset`/copy-user exports; and build modules requiring exported checksum and memory helpers.
