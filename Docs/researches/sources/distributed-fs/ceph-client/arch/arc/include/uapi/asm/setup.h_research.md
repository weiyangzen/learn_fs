# sources/distributed-fs/ceph-client/arch/arc/include/uapi/asm/setup.h

Placeholder UAPI setup header. It intentionally exports a non-empty comment so header generation keeps asm/setup.h even though ARC has no userspace setup structures. Control flow is headers_install producing an include file for compatibility. State is none. Dependencies are UAPI install scripts and patch behavior. Risks are low; removal can break includes expecting <asm/setup.h>. Test signals are headers_install and userspace builds including asm/setup.h.
