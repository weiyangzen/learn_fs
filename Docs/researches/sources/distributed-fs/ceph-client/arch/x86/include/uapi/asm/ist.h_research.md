<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/ist.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/ist.h

Purpose: Defines the legacy Intel SpeedStep Technology BIOS handoff structure embedded in x86 boot parameters.

Important APIs/types/functions: `struct ist_info` with `signature`, `command`, `event`, and `perf_level`.

Control flow: Boot code receives this firmware data in `boot_params`; power-management code may interpret it for legacy IST handling.

State and persistence behavior: No owned runtime state. The structure captures firmware-provided boot-time CPU performance metadata.

Dependencies and integration points: Depends on Linux UAPI types and integrates with `bootparam.h`, firmware/BIOS setup, and legacy CPU frequency support.

Risks and test signals: Risks are packed offset compatibility and obsolete firmware quirks. Test bootparam layout and legacy IST-capable system handling if available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/ist.h -->
