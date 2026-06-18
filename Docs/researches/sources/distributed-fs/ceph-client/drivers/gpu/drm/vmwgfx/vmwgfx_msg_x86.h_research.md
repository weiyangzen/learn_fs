# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_msg_x86.h

Purpose: Provides the x86 architecture include bridge for VMware hypercall helpers used by the common vmwgfx message layer.

Important APIs/types/functions: The header conditionally includes `<asm/vmware.h>` when building for `__i386__` or `__x86_64__`. The actual helper APIs (`vmware_hypercall1`, `vmware_hypercall5`, `vmware_hypercall6`, `vmware_hypercall7`, high-bandwidth helpers) are supplied by the architecture header.

Control flow: There is no runtime control flow here. The common message code includes this header and the arm64 header; preprocessor architecture guards ensure only the matching helper definitions are present.

State and persistence: No persistent state. This is a compile-time integration shim.

Dependencies and integration points: Depends on the kernel x86 VMware helper header and must stay API-compatible with `vmwgfx_msg_arm64.h`. Risks are mostly build-configuration risks: unsupported architectures get no helper definitions, x86 helper API changes would break `vmwgfx_msg.c`, and license/include guard mismatches can affect module builds. Test signals include x86_64 and i386 build coverage and exercising all message/mksstat hypercall paths through `vmwgfx_msg.c`.
