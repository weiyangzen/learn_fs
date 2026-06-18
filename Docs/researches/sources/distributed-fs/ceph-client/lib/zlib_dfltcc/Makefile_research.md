# sources/distributed-fs/ceph-client/lib/zlib_dfltcc/Makefile

Purpose: Builds the s390 DFLTCC zlib hardware acceleration object when `CONFIG_ZLIB_DFLTCC` is enabled.

Important entries:
- `obj-$(CONFIG_ZLIB_DFLTCC) += zlib_dfltcc.o`.
- `zlib_dfltcc-objs := dfltcc.o dfltcc_deflate.o dfltcc_inflate.o`.

Control flow: Kbuild links the common DFLTCC support plus deflate and inflate hook implementations into one object.

State and persistence: No runtime state; build configuration controls whether hook implementations are available to the zlib deflate/inflate objects.

Dependencies and integration:
- Integrates with `lib/zlib_deflate/deflate.c` and `lib/zlib_inflate/inflate.c` through `CONFIG_ZLIB_DFLTCC` include hooks.
- Architecture dependency is implicit: headers use s390 facility/setup and the DFLTCC instruction wrapper.

Risks:
- If enabled on an unsupported architecture, the architecture headers or inline assembly will fail; Kconfig must constrain selection.
- Partial object list changes can leave hooks unresolved.

Test signals:
- `CONFIG_ZLIB_DFLTCC=y/m` kernel build on s390.
- Build without the config to verify software zlib path remains independent.
