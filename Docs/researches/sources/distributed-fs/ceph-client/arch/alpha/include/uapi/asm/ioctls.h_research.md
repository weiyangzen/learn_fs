<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/ioctls.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/ioctls.h

**Purpose:** UAPI header that defines Alpha terminal, socket, serial, and file ioctl numbers. It is part of the stable Alpha userspace ABI, so values and layouts are consumed by libc, debuggers, syscall wrappers, and user programs.

**Important APIs/types/functions:** `FIOCLEX`, `FIONBIO`, `TCGETS`, `TIOC*`, `TIOCSER*`, pty, RS485, ISO7816, and modem controls.

**Control flow:** The file is declarative: kernel build, exported header installation, libc, or userspace code include it and compile the constants/layouts into ABI calls. Runtime behavior occurs in tty, socket, and serial userspace ABI rather than in this header.

**State and persistence behavior:** It owns no mutable runtime state. Its values are persistent ABI: changing numeric constants, field order, padding, or type widths can break existing binaries and core/debug tooling.

**Dependencies and integration points:** Depends on adjacent Linux UAPI/generic headers where included and integrates with tty, socket, and serial userspace ABI. It must stay synchronized with Alpha kernel implementation files and generated syscall/header plumbing.

**Risks:** Primary risks are ABI drift, mismatches with libc definitions, accidental renumbering, and padding/type-size changes that only show up on real Alpha user programs.

**Test signals:** Run UAPI header-install checks, libc/header compile tests, syscall or subsystem ABI tests for the defined constants, and binary-compatibility checks where structures are exposed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/uapi/asm/ioctls.h -->
