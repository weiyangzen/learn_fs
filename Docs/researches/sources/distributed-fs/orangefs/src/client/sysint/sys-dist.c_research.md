# sources/distributed-fs/orangefs/src/client/sysint/sys-dist.c
## sources/distributed-fs/orangefs/src/client/sysint/sys-dist.c

**Purpose:** Implements sysint-facing helpers for OrangeFS distribution lookup, release, parameter setting, and parsing distribution parameter/value strings.

**APIs and control flow:** `PVFS_sys_dist_lookup()` finds a registered `PINT_dist` by name and deep-copies its name/params into a `PVFS_sys_dist`. `PVFS_sys_dist_free()` frees that object. `PVFS_sys_dist_setparam()` looks up the registered distribution methods and calls `set_param`. `PVFS_dist_pv_pairs_extract_and_add()` tokenizes a parameter/value-pair string and calls `PVFS_dist_pv_pair_split()` for each. The split helper currently recognizes `strip_size`, parses it with `strtoll`, and sets that parameter.

**State and dependencies:** Depends on registered distribution subsystem state, token utilities, hint string limits, and gossip logging. No persistent state here.

**Risks and tests:** Parameter parsing is intentionally narrow and only handles `strip_size`; other distribution parameters are rejected or ignored. `strtoll` errors are not checked, so invalid values can become zero. Tests should include unknown dist names, allocation failures, malformed parameter strings, too many/too-long tokens, invalid numeric strip sizes, and valid strip-size propagation.
