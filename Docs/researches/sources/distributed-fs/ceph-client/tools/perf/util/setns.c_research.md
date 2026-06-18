# sources/distributed-fs/ceph-client/tools/perf/util/setns.c

`setns.c` provides a tiny compatibility wrapper for `setns(2)`. It defines `int setns(int fd, int nstype)` and directly invokes `syscall(__NR_setns, fd, nstype)`.

The file exists for build environments or libc versions where the libc `setns()` declaration/symbol is not available to perf. The API matches the Linux system call wrapper: `fd` identifies an opened namespace file descriptor and `nstype` constrains the namespace type or is zero.

There is no internal state and no persistence. The function returns the kernel syscall result directly, with errors surfaced through `-1` and `errno` as with `syscall(2)`.

Dependencies are `namespaces.h`, `<unistd.h>`, and `<sys/syscall.h>`. Integration points are perf namespace-handling code that must enter target namespaces, for example side-band build-id or symbol collection.

Risks are mostly portability and symbol-collision related: if libc already exposes `setns`, build configuration must avoid duplicate definitions; if `__NR_setns` is absent on a target architecture, compilation fails. Runtime permission and namespace-type failures are delegated to the kernel.

Test signals include compiling on libc versions with and without native `setns`, running namespace-aware perf flows, and checking that invalid descriptors/type masks return the expected kernel errors.
