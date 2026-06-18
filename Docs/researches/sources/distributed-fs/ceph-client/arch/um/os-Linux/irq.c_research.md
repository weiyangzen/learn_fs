# sources/distributed-fs/ceph-client/arch/um/os-Linux/irq.c

## Purpose
Implements host epoll wrappers used by UML IRQ file-descriptor polling.

## Important APIs, Types, and Functions
`os_setup_epoll()`, `os_waiting_for_events_epoll()`, `os_add_epoll_fd()`, `os_mod_epoll_fd()`, `os_del_epoll_fd()`, `os_epoll_get_data_pointer()`, `os_epoll_triggered()`, `os_event_mask()`, `os_set_ioignore()`, and `os_close_epoll_fd()` form the API.

## Control Flow, State, and Persistence
State is a global `epollfd` and fixed `epoll_events[MAX_EPOLL_EVENTS]`. Waits are nonblocking (`timeout=0`) and return event counts or negative errno; event data pointers link back to kernel-side IRQ descriptors.

## Dependencies and Integration Points
Used by UML IRQ core and fd activation/deactivation paths. It maps UML read/write IRQ types to host EPOLL masks and closes epoll on reboot.

## Risks and Test Signals
Risks include fixed event array overflow, edge-triggered missed events, fd leaks across reboot, and silent delete behavior hiding bugs. Test many fd-backed devices, fd add/mod/delete races, reboot cleanup, and SIGIO ignore transitions.
