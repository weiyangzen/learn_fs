## sources/distributed-fs/ceph-client/include/linux/cciss_ioctl.h

**Purpose:** This header bridges CCISS block-driver ioctl UAPI into kernel code and defines 32-bit compat passthrough ioctl structures when needed.

**Important APIs/types/functions:** It includes `<uapi/linux/cciss_ioctl.h>`. Under `CONFIG_COMPAT`, it defines `IOCTL32_Command_struct`, `BIG_IOCTL32_Command_struct`, and compat ioctl numbers `CCISS_PASSTHRU32` and `CCISS_BIG_PASSTHRU32`, with 32-bit user pointers represented as `__u32`.

**Control flow, state, persistence:** No runtime logic is in the header. The compat structs guide ioctl translation in driver code; request execution and controller state live elsewhere.

**Dependencies/integration:** Depends on UAPI CCISS types and compat configuration. Integrated by legacy HP Smart Array/CCISS ioctl handling.

**Risks and test signals:** Risks include pointer truncation/extension mistakes, struct packing drift versus userspace ABI, and missing compat handlers on 64-bit kernels. Test signals include 32-bit userspace ioctl passthrough tests on 64-bit kernels, ABI size checks, and request error-path coverage.
