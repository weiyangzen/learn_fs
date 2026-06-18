# sources/distributed-fs/ceph-client/fs/lockd/Makefile

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/Makefile` defines how the kernel Network Lock Manager module is built and how generated NLMv4 XDR source/header files are regenerated from the protocol specification. The source was read as a complete 41-line file.

## Important APIs, Types, and Functions

The build targets are `obj-$(CONFIG_LOCKD) += lockd.o`, the base `lockd-y` object list, `lockd-$(CONFIG_LOCKD_V4)` additions, `lockd-$(CONFIG_PROC_FS)` additions, and the phony `xdrgen` target. `ccflags-y += -I$(src)` supports trace event includes.

## Control Flow

Normal builds compile the checked-in generated files. Developers who modify `Documentation/sunrpc/xdr/nlm4.x` can run `make xdrgen`, which invokes `tools/net/sunrpc/xdrgen/xdrgen` to regenerate definitions, declarations, and source output.

## State and Persistence Behavior

No runtime state exists. Persistent build state is the selected object composition based on Kconfig and the checked-in generated `nlm4xdr_gen.{h,c}` plus generated public definitions under `include/linux/sunrpc/xdrgen/nlm4.h`.

## Dependencies and Integration Points

The Makefile integrates lockd client, server, host, monitor, XDR, trace, netlink, and optional procfs/NLMv4 code. It depends on Kconfig symbols `CONFIG_LOCKD`, `CONFIG_LOCKD_V4`, and `CONFIG_PROC_FS`.

## Risks and Edge Cases

Generated XDR drift is the main risk: changing the `.x` specification without regenerating all outputs can desynchronize server decode/encode declarations and implementation. Build coverage must include both v4/procfs enabled and disabled configurations.

## Test Signals

Signals are kernel build tests for `CONFIG_LOCKD=y/m`, `CONFIG_LOCKD_V4` toggles, `CONFIG_PROC_FS` toggles, trace include compilation, and a developer regeneration diff after running `make xdrgen`.
