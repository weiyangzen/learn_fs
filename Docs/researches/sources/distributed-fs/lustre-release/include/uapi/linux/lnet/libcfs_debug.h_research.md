# sources/distributed-fs/lustre-release/include/uapi/linux/lnet/libcfs_debug.h

Purpose: user/kernel ABI definitions for Lustre/libcfs debug records, subsystem bits, and debug mask bits.

Important APIs/types: `struct ptldebug_header` is a packed record header containing length, flags, subsystem, mask, CPU/type, timestamp seconds/usec, stack, PID fields, and source line. `PH_FLAG_FIRST_RECORD` marks first records. `enum libcfs_debug_subsys` defines 32 non-overlapping subsystem bits such as MDC, MDS, OSC, OST, LNET, LND, LDLM, LOV, OSD, MGS, FID, and FLD. `enum libcfs_debug_masks` defines trace/info/error/network/config/etc. mask bits. Name macros provide ordered string lists for display tools.

Control flow/state: no executable control flow. Log writers populate packed headers; readers interpret bitmasks and names consistently across kernel/user space.

Dependencies/integration: included by debug tools and kernel code; relies on fixed-width Linux types and packed layout.

Risks and test signals: ABI risk is high because changing enum bit positions or packed struct layout breaks log parsers. Timestamp comment notes 2106 overflow for 32-bit seconds. Test signals are binary log parse compatibility, default mask/subsystem expansion, and name-array ordering against bit positions.
