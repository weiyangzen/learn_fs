# sources/distributed-fs/ceph-client/security/selinux/Makefile

## Purpose
This Makefile describes how SELinux is built inside the kernel tree. It links SELinux objects into `selinux.o`, configures include paths and debug flags, conditionally adds feature objects, and builds/runs the host-side `genheaders` utility that generates `flask.h` and `av_permissions.h`.

## Important Targets and Variables
- `obj-$(CONFIG_SECURITY_SELINUX) := selinux.o`: builds SELinux only when configured.
- `ccflags-y`: adds SELinux source and include directories.
- `ccflags-$(CONFIG_SECURITY_SELINUX_DEBUG) += -DDEBUG`: enables debug preprocessor paths.
- `selinux-y`: core SELinux object list, including `avc.o`, hooks, selinuxfs, netlink, networking tables, status/initcalls, and security-server (`ss/`) policy database objects.
- Conditional objects: `xfrm.o`, `netlabel.o`, `ibpkey.o`, and `ima.o`.
- `genhdrs := flask.h av_permissions.h`: generated header outputs.
- `hostprogs := genheaders`: builds the generator as a host tool.
- `HOST_EXTRACFLAGS`: provides the host tool with SELinux include paths.

## Control Flow
The kernel build system evaluates `selinux-y`, compiles the listed objects, and links them into `selinux.o`. Before SELinux objects are built, the Makefile requires generated headers. Because older make versions lack grouped targets, the dependency is anchored on `$(obj)/flask.h`; invoking that rule runs `genheaders` and writes both `flask.h` and `av_permissions.h`.

The comments document a future simplification once GNU make 4.3 grouped targets are required: all generated headers could be modeled as one grouped target and all object files could depend directly on both outputs.

## State and Persistence Behavior
The Makefile creates generated build artifacts in the object tree, not persistent source files. The generated headers are derived from SELinux class and permission maps. Incremental rebuild correctness depends on kbuild's `if_changed` tracking and the declared target/dependency relationships.

## Dependencies and Integration Points
It integrates with kbuild variables (`obj-*`, `ccflags-*`, `targets`, `hostprogs`, `quiet_cmd_*`, `cmd_*`) and with SELinux source files that include generated `flask.h` and `av_permissions.h`. Conditional object inclusion follows kernel config symbols for XFRM, NetLabel, InfiniBand, and IMA.

## Risks and Edge Cases
- The single-output dependency workaround can be fragile if generated-header dependencies change and kbuild does not notice all consumers.
- `genheaders` must run on the build host, so host compiler flags and include paths must remain valid for non-target compilation.
- Adding new SELinux source files that depend on generated headers requires they be included in `selinux-y` or otherwise covered by the dependency rule.
- Conditional feature objects must stay aligned with Kconfig dependencies and C preprocessor guards.

## Test Signals
Useful checks include clean and incremental kernel builds with `CONFIG_SECURITY_SELINUX=y`, toggling `CONFIG_SECURITY_SELINUX_DEBUG`, building feature combinations for XFRM/NetLabel/InfiniBand/IMA, verifying `flask.h` and `av_permissions.h` regeneration after classmap changes, and checking parallel builds for missing generated-header races.
