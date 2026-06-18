# sources/distributed-fs/openafs/src/afs/afs_osi.c

## Purpose
`afs_osi.c` provides common operating-system-interface initialization and process/credential helpers for the Cache Manager. It sets up global locks, initializes the long-lived AFS kernel credential, masks or unmasks signals for kernel threads, marks AFS threads as system/invisible where supported, and cleans OSI sleep resources on shutdown.

## Important APIs, types, and functions
Globals include `afs_ftf`, `afs_osi_credp`, and platform-specific global-lock variables for Solaris, SGI, Darwin, BSD, FreeBSD, and AIX. Main functions are `osi_Init`, `afs_osi_MaskSignals`, `afs_osi_UnmaskRxkSignals`, `afs_osi_MaskUserLoop`, `afs_osi_RxkRegister`, `afs_osi_Invisible`, `afs_osi_Visible`, `shutdown_osi`, `shutdown_osisleep`, and `afs_osi_suser`.

## Control flow
`osi_Init` is guarded by a static one-time flag. It initializes the global AFS lock, hcrypto kernel mutex, and if needed creates or references `afs_osi_credp` according to platform conventions: BSD duplicates current credentials, Solaris uses `kcred`, Darwin allocates and initializes a credential object, Linux initializes group info for the static credential, and other platforms zero and hold `afs_osi_cred`. It also initializes error-code translation and SGI lock-owner data.

Signal helpers defer to Linux-specific masks or Darwin invisible/full-mask behavior. Visibility helpers set or clear system process flags where the platform exposes them. `shutdown_osi` releases Darwin context state, tears down OSI sleep hashes on non-Linux/non-Darwin platforms, and reinitializes `afs_ftf` on cold shutdown.

## State and persistence behavior
All state is in memory and tied to kernel module lifetime: global lock primitives, static credentials, Darwin context references, event sleep hash entries, and process flags. There is no on-disk persistence.

## Dependencies and integration points
The file depends on `osi_machdep` platform code, OS credential APIs, sleep/event hash definitions, AFS global lock initialization, hcrypto initialization, and error mapping. Many other AFS files assume `afs_osi_credp` exists for anonymous/internal requests and that OSI sleep/wakeup resources are initialized.

## Risks and edge cases
Credential lifetime differs significantly by platform. Incorrect reference ownership can leak or free kernel credentials too early. Marking processes invisible/system is platform-specific and may be a no-op on newer kernels. `shutdown_osisleep` warns on nonzero event refcounts, signaling potential sleeping waiters during shutdown.

## Test signals
Verify one-time init, platform credential setup, Linux signal masking, Darwin context release, system flag toggling where supported, sleep hash cleanup, and superuser checks through `afs_osi_suser`.
