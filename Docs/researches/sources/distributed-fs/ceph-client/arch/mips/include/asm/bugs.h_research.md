<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/bugs.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/bugs.h

**Purpose:** Declares CPU bug detection hooks and R4x00 daddiu bug state.

**Important APIs/types/functions:** Externs `daddiu_bug`, `check_bugs64_early`, `check_bugs32`, and `check_bugs64`; inline `r4k_daddiu_bug()` validates and returns bug status when configured.

**Control flow:** Boot CPU bug detection populates state; later code queries it.

**State, dependencies, integration:** Depends on CPU info and SMP headers. Used during CPU setup and errata workarounds.

**Risks and test signals:** Querying before detection warns; missing workaround on affected CPUs causes arithmetic faults. Test configured/unconfigured R4x00 errata and ordering of early bug checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/bugs.h -->
