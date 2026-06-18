# sources/distributed-fs/ceph-client/arch/um/os-Linux/user_syms.c

## Purpose
Exports selected compiler/libc string helper symbols that UML modules may need when user-side code is linked into the kernel environment.

## Important APIs, Types, and Functions
Conditionally exports `strstr`, and on non-x86_64 exports `memcpy`, `memmove`, and `memset`. When fortify is enabled, exports `__sprintf_chk`. Defines `__NO_FORTIFY` before includes to avoid fortify rewrites in this file.

## Control Flow, State, and Persistence
No runtime control flow or state. It only affects module symbol resolution.

## Dependencies and Integration Points
Integrates with module export infrastructure and architecture string implementation choices. Comments warn against expanding this as a broad hostfs/user-code API boundary.

## Risks and Test Signals
Risks are missing exports on specific compiler/libc/architecture combinations or encouraging improper module dependencies on host-side functions. Test module builds on i386/x86_64 and fortify-enabled configs.
