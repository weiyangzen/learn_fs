# sources/distributed-fs/ceph-client/include/linux/eventpoll.h

Purpose: internal epoll hooks for file release, event delivery, control operations, and ARM OABI event translation.

Important APIs/types/functions: `eventpoll_release_file()`, `eventpoll_release()`, `epoll_sendevents()`, `do_epoll_ctl()`, `ep_op_has_event()`, optional `get_epoll_tfile_raw_ptr()` for KCMP, and `ep_take_care_of_epollwakeup()` for ARM OABI compat handling.

Control flow: file close/release calls `eventpoll_release()` to detach watched files; syscalls use `do_epoll_ctl()` and `epoll_sendevents()`; operation validation checks whether an op includes an event payload.

State/persistence: epoll interest lists and ready lists live in epoll file state. No persistence beyond file lifetime.

Dependencies/integration: `CONFIG_EPOLL`, file/VFS lifecycle, user-copy of `struct epoll_event`, KCMP, ARM OABI compatibility.

Risks/test signals: risks are dangling watched-file references on close, wrong op validation, user event copy/compat translation errors, and config-off callers. Test epoll_ctl add/mod/del, concurrent close, nested epoll, KCMP inspection, ARM OABI compat, and disabled config builds.
