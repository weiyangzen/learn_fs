<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/compiler.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/compiler.h

**Purpose:** UAPI header that provides userspace-visible Alpha compiler instruction helpers for byte/word loads and stores. It is part of the stable Alpha userspace ABI, so values and layouts are consumed by libc, debuggers, syscall wrappers, and user programs.

**Important APIs/types/functions:** `__kernel_ldbu`, `__kernel_ldwu`, `__kernel_stb`, and `__kernel_stw` with compiler-dependent inline assembly or fallbacks.

**Control flow:** The file is declarative: kernel build, exported header installation, libc, or userspace code include it and compile the constants/layouts into ABI calls. Runtime behavior occurs in UAPI helpers and kernel shared instruction abstractions rather than in this header.

**State and persistence behavior:** It owns no mutable runtime state. Its values are persistent ABI: changing numeric constants, field order, padding, or type widths can break existing binaries and core/debug tooling.

**Dependencies and integration points:** Depends on adjacent Linux UAPI/generic headers where included and integrates with UAPI helpers and kernel shared instruction abstractions. It must stay synchronized with Alpha kernel implementation files and generated syscall/header plumbing.

**Risks:** Primary risks are ABI drift, mismatches with libc definitions, accidental renumbering, and padding/type-size changes that only show up on real Alpha user programs.

**Test signals:** Run UAPI header-install checks, libc/header compile tests, syscall or subsystem ABI tests for the defined constants, and binary-compatibility checks where structures are exposed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/compiler.h -->
