## sources/distributed-fs/ceph-client/include/linux/byteorder/little_endian.h

**Purpose:** This header selects little-endian byteorder definitions for kernel code.

**Important APIs/types/functions:** It includes `<uapi/linux/byteorder/little_endian.h>`, warns if `CONFIG_CPU_BIG_ENDIAN` is set, and includes `linux/byteorder/generic.h`.

**Control flow, state, persistence:** There is no runtime state. It defines the compile-time conversion surface used by native and protocol code.

**Dependencies/integration:** Depends on architecture/Kconfig endian selection and generic byteorder aliases.

**Risks and test signals:** Risks are Kconfig/include inconsistency and code that assumes little-endian layout without explicit conversion. Test signals include little-endian build coverage, sparse endian checking, and protocol/filesystem round trips against big-endian peers or images.
