# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/papr-sysparm.c

Purpose: Implements kernel and `/dev/papr-sysparm` access to PAPR system parameters through RTAS `ibm,get-system-parameter` and `ibm,set-system-parameter`.

Important APIs/types/functions: Provides `papr_sysparm_buf_alloc()`, `papr_sysparm_buf_free()`, `papr_sysparm_get()`, `papr_sysparm_set()`, ioctl handlers for `PAPR_SYSPARM_IOC_GET` and `PAPR_SYSPARM_IOC_SET`, and a miscdevice named `papr-sysparm`.

Control flow: Kernel callers allocate a `papr_sysparm_buf`, seed its big-endian length/value, and call get or set. The code validates that the encoded length fits the fixed value buffer, copies the buffer into an RTAS work area, retries while firmware reports busy, maps documented RTAS status codes to errno, and copies successful get results back with length clamping. Userspace follows the same path through ioctl marshaling, with write-mode required for set.

State and persistence: The driver itself keeps no persistent parameter cache. State lives in transient heap buffers, RTAS work-area allocations, and userspace I/O blocks. Firmware is the persistent store for settable parameters.

Dependencies and integration points: Depends on RTAS token lookup/calls, `rtas_work_area_alloc()`, PAPR sysparm UAPI structures, miscdevice registration, pseries machine initcalls, and `setup.c` callers such as CMO feature parsing.

Risks: Length and endian handling are security-critical because firmware can return malformed lengths and userspace can provide bogus input lengths. `copy_to_user()` intentionally exports the full maximum output buffer, so clamping only protects kernel interpretation rather than reducing copied bytes. RTAS work-area allocation may sleep.

Test signals: Exercise ioctl get/set with valid and invalid lengths, missing RTAS tokens, unauthorized and unsupported parameters, busy retry paths, read-only fd set rejection, and boot-time CMO sysparm parsing on pseries.

Source read size: 352 lines, 10206 bytes.
