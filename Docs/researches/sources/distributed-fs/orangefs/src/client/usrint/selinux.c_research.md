## sources/distributed-fs/orangefs/src/client/usrint/selinux.c

Purpose: Supplies usrint interposed SELinux context functions when SELinux headers are available, but currently marks all SELinux context operations unsupported.

Important APIs, types, and functions: Defines `getfscreatecon`, `getfscreatecon_raw`, `getfilecon`, `getfilecon_raw`, `lgetfilecon`, `lgetfilecon_raw`, `fgetfilecon`, `fgetfilecon_raw`, and corresponding `set*con`/`set*con_raw` functions. All set `errno = ENOTSUP` and return `-1`.

Control flow: The file is compiled only for the SELinux-header path (`HAVE_SELINUX_H`). It undefines libc/SELinux macro redirects first, then provides concrete symbols that do not dispatch to libc or OrangeFS.

State and persistence: No state or persistent side effects except setting `errno`.

Dependencies and integration points: Includes `usrint.h`; signature constness is controlled by `HAVE_CONST_SECURITY_CONTEXT`. These symbols interpose process calls under the usrint library.

Risks and test signals: The comment says the eventual behavior should decide whether a path is PVFS or regular, but current code breaks SELinux context calls even for non-PVFS paths if this library is interposed first. Test builds with and without SELinux headers, raw and non-raw variants, fd/path variants, errno value, and applications expecting libc fallback for regular files.
