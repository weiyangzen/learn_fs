# sources/distributed-fs/ceph-client/include/uapi/linux/openat2.h

Purpose: Defines `openat2(2)` argument layout and path-resolution hardening flags.

Important APIs/types/functions: Exports `struct open_how` with `flags`, `mode`, and `resolve`, plus `RESOLVE_NO_XDEV`, `RESOLVE_NO_MAGICLINKS`, `RESOLVE_NO_SYMLINKS`, `RESOLVE_BENEATH`, `RESOLVE_IN_ROOT`, and `RESOLVE_CACHED`.

Control flow: Userspace passes `open_how` and its size to `openat2`. The kernel validates unknown bits strictly, checks mode only with creation flags, and applies resolution constraints while walking the path. `RESOLVE_CACHED` can short-circuit with `-EAGAIN` if a nonblocking cached lookup is not possible.

State and persistence behavior: The header defines one syscall argument snapshot. No persistent state is stored; resulting file descriptors and filesystem side effects follow normal open semantics.

Dependencies and integration points: Depends on `<linux/types.h>`. Integrates with libc wrappers, sandboxing/container runtimes, package managers, and security-sensitive path opening code.

Risks: Userspace must pass correct structure size for forward compatibility. Misunderstanding `RESOLVE_BENEATH` versus `RESOLVE_IN_ROOT`, magic links, or mount crossing can create directory traversal vulnerabilities. The comment typo `OEXT_NO_MAGICLINKS` should be read as implying `RESOLVE_NO_MAGICLINKS`.

Test signals: Run path traversal tests with symlinks, `..`, bind mounts, procfs magic links, and absolute paths; verify unknown flag rejection; verify `RESOLVE_CACHED` `-EAGAIN`; and test structure size extension behavior.
