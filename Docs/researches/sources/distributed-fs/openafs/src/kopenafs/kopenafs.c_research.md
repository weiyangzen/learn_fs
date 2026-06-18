## sources/distributed-fs/openafs/src/kopenafs/kopenafs.c

Purpose: `kopenafs.c` implements the public `kopenafs` wrapper API: detect AFS availability, create PAGs, issue pioctls, unlog tokens, and detect whether the process is in a PAG without dragging in the full Rx/auth stack.

Important APIs: `k_hasafs` installs a temporary `SIGSYS` handler, issues a deliberately invalid `VIOCSETTOK` pioctl through `lpioctl`, and considers AFS present if the syscall exists and returns `EINVAL`; it restores `errno` and the signal handler. `k_setpag` calls `lsetpag` retrying on `EINTR`. `k_pioctl` forwards to `lpioctl`. `k_unlog` sends `VIOCUNLOG`. `k_haspag` tries `VIOC_GETPAG` and falls back to `os_haspag`.

Control flow and OS behavior: `os_haspag` is platform-specific. AIX 5.2 uses `getpagvalue("afs")`; AIX 5.1 reports false; other systems inspect group lists for one-group PAG markers or classic two-group PAG encodings and reconstruct the PAG value to check for the `A` marker.

State and persistence: static `syscall_okay` is updated by the SIGSYS handler. `k_setpag` changes process credentials/PAG membership. `k_unlog` clears tokens in the current PAG.

Dependencies and integration points: depends on `afs/afssyscalls.h`, `afs/vioc.h` through `kopenafs.h`, OS signal/group APIs, and sys-layer `lpioctl`/`lsetpag`.

Risks: `k_hasafs` uses a process-wide signal handler and static flag, making concurrent calls signal-sensitive. `os_haspag` allocates based on `getgroups(0,NULL)` and does not handle a negative return before allocation size calculation. Group-list PAG detection is heuristic and OS-layout dependent.

Test signals: `test-setpag.c` exercises `k_hasafs`, `k_haspag`, and `k_setpag`; `test-unlog.c` exercises `k_hasafs` and `k_unlog`.
