# sources/distributed-fs/ceph-client/arch/arm/kernel/signal.h

Purpose: shares ARM signal-frame layout definitions between signal delivery code and process setup code.

Important APIs/types/functions: defines structures for signal frames, realtime frames, and auxiliary VFP/iWMMXt blocks plus magic/size constants consumed by `signal.c`.

Control flow: no runtime flow; layout is used by copy-to/from-user paths.

State and persistence: describes persistent user-stack ABI content during signal delivery.

Dependencies and integration: tied to UAPI signal context, VFP/iWMMXt save formats, sigreturn trampoline code, and `process.c` sigpage mapping.

Risks: any layout change can break existing userspace signal return. Test signals include ABI size/offset compile assertions and userspace signal-frame compatibility tests.
