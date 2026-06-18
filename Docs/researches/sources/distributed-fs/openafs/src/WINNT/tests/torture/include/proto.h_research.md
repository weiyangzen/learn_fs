# sources/distributed-fs/openafs/src/WINNT/tests/torture/include/proto.h

Purpose: function prototype header for the scriptable `nb_*` operation layer.

Important APIs and functions: declares create/delete/copy/move/attach/detach/locker functions; low-level `nb_read`, `nb_write`, and `nb_close1`; logical command wrappers such as `nb_writex`, `nb_readx`, `nb_qpathinfo`, `nb_qfileinfo`, `nb_qfsinfo`, `nb_findfirst`, `nb_deltree`, `nb_cleanup`, and `nb_lock`.

Control flow: no implementation; this header establishes the callable surface for the torture parser/dispatcher.

State and persistence: none directly, but prototypes expose operations that mutate the filesystem, open-handle table, and command counters.

Dependencies and integration: includes `common.h` and `includes.h` for `HANDLE`, `DWORD`, `NTSTATUS`, and `ssize_t`.

Risks and test signals: the include cycle is tolerated by guards but is brittle. Prototype drift from `nbio.c` would produce compile warnings/errors; the declared `nb_lock` is currently stubbed out in implementation.
