## sources/distributed-fs/ceph-client/include/linux/const.h

Purpose: This wrapper exposes VDSO constant macros through the normal Linux include path.

Important APIs, types, and functions: The file only includes `<vdso/const.h>` behind `_LINUX_CONST_H`.

Control flow: There is no runtime or compile-time decision beyond the include guard.

State and persistence: No state is declared. Any constant behavior is inherited from the VDSO header.

Dependencies and integration points: It integrates kernel code with VDSO-safe constant expression definitions, allowing shared constant macros to be reused.

Risks and test signals: Risks are limited to include-path breakage or VDSO constant macro changes. Test signals are compile coverage for kernel and VDSO consumers and ensuring the wrapper remains side-effect free.
