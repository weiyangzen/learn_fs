<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/gentrap.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/gentrap.h

**Purpose:** UAPI header that defines Alpha generic trap negative reason codes. It is part of the stable Alpha userspace ABI, so values and layouts are consumed by libc, debuggers, syscall wrappers, and user programs.

**Important APIs/types/functions:** `GEN_INTOVF`, `GEN_FLTOVF`, `GEN_FLTDIV`, range/subscript errors, and assertion/null/stack errors.

**Control flow:** The file is declarative: kernel build, exported header installation, libc, or userspace code include it and compile the constants/layouts into ABI calls. Runtime behavior occurs in PAL `gentrap`, signal, and language-runtime trap mapping rather than in this header.

**State and persistence behavior:** It owns no mutable runtime state. Its values are persistent ABI: changing numeric constants, field order, padding, or type widths can break existing binaries and core/debug tooling.

**Dependencies and integration points:** Depends on adjacent Linux UAPI/generic headers where included and integrates with PAL `gentrap`, signal, and language-runtime trap mapping. It must stay synchronized with Alpha kernel implementation files and generated syscall/header plumbing.

**Risks:** Primary risks are ABI drift, mismatches with libc definitions, accidental renumbering, and padding/type-size changes that only show up on real Alpha user programs.

**Test signals:** Run UAPI header-install checks, libc/header compile tests, syscall or subsystem ABI tests for the defined constants, and binary-compatibility checks where structures are exposed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/gentrap.h -->
