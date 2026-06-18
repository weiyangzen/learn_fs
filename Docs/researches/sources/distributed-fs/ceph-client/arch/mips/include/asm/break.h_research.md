<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/break.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/break.h

**Purpose:** Defines MIPS kernel-internal break instruction codes.

**Important APIs/types/functions:** Includes UAPI break codes and defines `BRK_KDB`, `BRK_MEMU`, `BRK_KPROBE_BP`, `BRK_KPROBE_SSTEPBP`, and `BRK_MULOVF`.

**Control flow:** No executable logic; low-level debug, emulator, kprobe, and overflow code emits or decodes these break codes.

**State, dependencies, integration:** Ties trap handling to specific break code values.

**Risks and test signals:** Code collisions misroute break exceptions. Test kprobe breakpoint/single-step, KDB entry, FPU emulator break, and multiply overflow handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/break.h -->
