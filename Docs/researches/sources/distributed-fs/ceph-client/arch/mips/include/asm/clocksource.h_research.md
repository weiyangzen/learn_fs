<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/clocksource.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/clocksource.h

**Purpose:** Exposes MIPS vDSO clocksource definitions through the architecture clocksource include.

**Important APIs/types/functions:** Includes `<asm/vdso/clocksource.h>`.

**Control flow:** Header forwarding only.

**State, dependencies, integration:** Connects arch clocksource users to vDSO clocksource data structures.

**Risks and test signals:** Include path drift can break vDSO/time builds. Test MIPS vDSO clocksource compilation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/clocksource.h -->
