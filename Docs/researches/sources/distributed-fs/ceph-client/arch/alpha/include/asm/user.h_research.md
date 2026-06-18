<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/user.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/user.h

**Purpose:** Defines the Alpha `struct user` core-file header layout used by traditional core dumps and debuggers.

**Important APIs/types/functions:** `struct user` with integer/FP register storage, segment sizes, start addresses, signal, register pointer, magic, and command name.

**Control flow:** Core dump code emits this structure so GDB/BFD can locate registers and process address ranges.

**State and persistence behavior:** Represents serialized process state in a core file. The header itself stores no live state.

**Dependencies and integration points:** Depends on task/ptrace headers, Alpha register indices from `asm/reg.h`, and page sizing.

**Risks:** Layout is debugger ABI. Register array sizing must match `EF_SIZE` plus FP registers.

**Test signals:** Generate core dumps, inspect with GDB, validate registers/segments and command name.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/user.h -->
