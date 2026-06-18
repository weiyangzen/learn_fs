# sources/distributed-fs/openafs/src/afs/AIX/osi_groups.c

Purpose: AIX PAG and group-list manipulation for OpenAFS authentication state.

Important APIs and functions: legacy `setgroups` wrapper preserves an existing PAG across `osetgroups`; `setpag` creates or installs a PAG; AIX 5.1 `do_setpag` uses `kcred_setpag`; pre-5.1 helpers `afs_getgroups`, `copy_to_cred`, and `afs_setgroups` encode the PAG into the first two group IDs.

Control flow: `setpag` generates a PAG if requested, ensures room for two PAG groups on legacy AIX, stores `*newpag`, then either calls `do_setpag` or rewrites group arrays. `change_parent` controls whether the existing credential is modified or a duplicated current credential is installed with `crset`.

State and persistence: mutates process credentials and optionally shared parent credentials. On failure it sets user error with `setuerror`.

Dependencies and integration: uses OpenAFS PAG encoding helpers, AIX credential functions (`crref`, `crdup`, `crset`, `crfree`), and kernel PAG APIs on AIX 5.1.

Risks and test signals: group-list capacity can return `E2BIG`; parent credential sharing is subtle; AIX 5.1 errors are recovered from `getuerror`. Signals are successful `pagsh`/`klog -setpag`, retained PAG after `setgroups`, and correct token visibility.
