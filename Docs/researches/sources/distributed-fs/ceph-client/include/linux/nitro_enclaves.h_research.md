# sources/distributed-fs/ceph-client/include/linux/nitro_enclaves.h

Purpose: Kernel wrapper for AWS Nitro Enclaves UAPI definitions.

Important APIs, types, and functions: Includes `uapi/linux/nitro_enclaves.h` and provides the kernel include guard. Detected source surface: 11 lines; includes `uapi/linux/nitro_enclaves.h`; macros `_LINUX_NITRO_ENCLAVES_H_`; structs none; enums none; typedefs none; function-like declarations/helpers none.

Control flow: There is no executable flow in this header; driver and userspace ABI code consume the UAPI definitions.

State and persistence behavior: No state is defined here.

Dependencies and integration points: Depends entirely on Nitro Enclaves UAPI ioctl and structure definitions.

Risks and test signals: Risks are ABI drift between kernel wrapper and UAPI. Test by building enclave driver users and exercising ioctl compatibility.
