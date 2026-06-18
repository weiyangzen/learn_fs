<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/arc/env.c -->
## sources/distributed-fs/ceph-client/arch/mips/fw/arc/env.c

**Purpose:** Provides a thin ARC firmware environment lookup wrapper.

**Important APIs/types/functions:** `ArcGetEnvironmentVariable(CHAR *name)` calls the ROM vector `get_evar` service through `ARC_CALL1` and returns a firmware string pointer.

**Control flow:** There is no local parsing or caching. Callers provide the name, the macro dispatches into firmware, and the returned pointer is passed through.

**State, dependencies, integration:** Depends on ARC type definitions and `asm/sgialib.h` ROM call macros. It integrates with PROM users that need ARC environment data during boot.

**Risks and test signals:** Returned storage belongs to firmware and may be invalid after PROM cleanup; callers must copy data they need later. Test by querying existing and missing environment variables on ARC firmware and verifying pointer lifetime assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/arc/env.c -->
