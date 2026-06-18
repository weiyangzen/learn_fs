# sources/distributed-fs/ceph-client/sound/isa/msnd/msnd_classic.c

## Purpose
`msnd_classic.c` is a wrapper translation unit for the MultiSound Classic/Monterey/Tahiti variant. It defines `MSND_CLASSIC` and includes `msnd_pinnacle.c`, causing the shared board driver to compile with Classic register constants and conditional branches.

## Important APIs, Types, and Functions
This file defines no functions of its own. Its public surface is inherited from the included `msnd_pinnacle.c` build, with names and metadata selected by `MSND_CLASSIC`, `msnd_classic.h`, `LOGNAME`, and `DEV_NAME`.

## Control Flow
Compilation control flow is the whole purpose: defining `MSND_CLASSIC` selects Classic-specific reset, memory ID, IRQ mask, and Pro reset code inside `msnd_pinnacle.c`, while excluding Pinnacle PnP/config-device paths.

## State and Persistence
Runtime state is the same `struct snd_msnd` state used by the included implementation. Classic-specific state includes `memid` and `irqid` values derived from module parameters.

## Dependencies and Integration Points
It depends entirely on `msnd_pinnacle.c`, `msnd.h`, and `msnd_classic.h`. Build integration must compile it as a distinct module/object only where Classic support is enabled.

## Risks and Test Signals
Including a `.c` file is fragile: symbol names, module metadata, and static variables are duplicated per variant and can diverge silently. Test signals are successful Classic build, distinct module registration name `msnd-classic`, correct parameter validation for Classic I/O/memory/IRQ values, and no accidental Pinnacle-only PnP code compiled into the Classic variant.
