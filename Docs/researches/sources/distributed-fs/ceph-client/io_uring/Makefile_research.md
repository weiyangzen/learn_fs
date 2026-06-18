# sources/distributed-fs/ceph-client/io_uring/Makefile

## Purpose
The Makefile defines the io_uring object composition for core support and optional feature objects.

## Important APIs, Types, And Functions
- `obj-$(CONFIG_IO_URING)` builds the core aggregate with files such as `io_uring.o`, `opdef.o`, `rsrc.o`, `filetable.o`, `rw.o`, `poll.o`, `eventfd.o`, `fs.o`, `cancel.o`, `register.o`, `alloc_cache.o`, and `loop.o`.
- Optional objects include `io-wq.o`, `futex.o`, `epoll.o`, `napi.o`, `net.o`, `cmd_net.o`, `fdinfo.o`, `mock_file.o`, `bpf_filter.o`, and `bpf-ops.o`.
- `CONFIG_GCOV_PROFILE_URING` can enable GCOV profiling for this directory.

## Control Flow
Build-time only. Object inclusion follows Kconfig symbols.

## State And Persistence
The resulting kernel image/module includes only selected object files. No runtime state lives here.

## Dependencies And Integration Points
This file binds Kconfig to implementation. Many files in this research set rely on being compiled only when their subsystem dependencies exist, while headers provide stubs for callers in disabled configurations.

## Risks And Edge Cases
Duplicated or missing objects can create link failures or silently omit operations. The core list includes many operation adapters; additions to `opdef` often need corresponding Makefile updates.

## Test Signals
Successful allmodconfig/allyesconfig/minimal builds and io_uring operation tests across feature combinations validate this file.
