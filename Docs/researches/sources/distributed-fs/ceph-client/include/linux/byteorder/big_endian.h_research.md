## sources/distributed-fs/ceph-client/include/linux/byteorder/big_endian.h

**Purpose:** This header selects big-endian byteorder definitions for kernel code.

**Important APIs/types/functions:** It includes `<uapi/linux/byteorder/big_endian.h>`, emits a preprocessor warning if `CONFIG_CPU_BIG_ENDIAN` is not set, then includes `linux/byteorder/generic.h`.

**Control flow, state, persistence:** There is no runtime state. It establishes compile-time conversion macros such as `cpu_to_be*`, `be*_to_cpu`, and little-endian swap forms through the UAPI and generic layers.

**Dependencies/integration:** Depends on the architecture/Kconfig endian selection and generic byteorder aliases.

**Risks and test signals:** Risks are inconsistent Kconfig/include selection and drivers manually bypassing conversion macros. Test signals are big-endian compile builds, sparse endian annotations, and protocol/filesystem round-trip tests on big-endian targets.
