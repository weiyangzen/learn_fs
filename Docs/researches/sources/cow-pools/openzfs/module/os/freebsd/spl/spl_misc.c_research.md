# File Research: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_misc.c

Miscellaneous FreeBSD SPL compatibility helpers.

Key behavior:
- Provides a Solaris-like `utsname()` backed by FreeBSD global OS strings and prison0 hostname.
- `opensolaris_utsname_init()` stores `osreldate` as the version string.
- `kmem_strdup()` allocates/copies strings with kmem.
- `ddi_copyin()` and `ddi_copyout()` bypass user copy functions for fake kernel ioctls marked `FKIOCTL`; otherwise call FreeBSD `copyin`/`copyout`.
- `spl_panic()` forwards to `vpanic()`.
- `current_is_reclaim_thread()` detects FreeBSD page daemon context via `curproc == pageproc`.

Initialization runs at tunables time.
