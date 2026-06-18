<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/hw_breakpoint.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/hw_breakpoint.h

Purpose: Placeholder UAPI header for x86 hardware breakpoint definitions. The file intentionally exports no x86-specific declarations in this tree.

Important APIs/types/functions: None beyond the file's presence and SPDX marker.

Control flow: No control flow.

State and persistence behavior: No state.

Dependencies and integration points: Included by generic perf or userspace code that expects an architecture hardware-breakpoint UAPI path to exist.

Risks and test signals: Risks are include-path breakage if removed or populated incompatibly. Test userspace builds that include `<asm/hw_breakpoint.h>` and perf breakpoint tooling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/hw_breakpoint.h -->
