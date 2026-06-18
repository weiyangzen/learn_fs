# sources/distributed-fs/ceph-client/tools/testing/selftests/net/epoll_busy_poll.c

Purpose: this C kselftest validates the epoll busy-poll ioctl API. It does not build a network traffic topology; it focuses on ioctl behavior, validation, default values, permission behavior, and error codes for `EPIOCGPARAMS` and `EPIOCSPARAMS`.

Important APIs and types: it uses the kselftest harness fixture macros, `struct epoll_params`, epoll ioctls, `epoll_create1`, `ioctl`, libcap functions `cap_get_proc`, `cap_get_flag`, `cap_set_flag`, `cap_set_proc`, `cap_free`, and capability `CAP_NET_ADMIN`. Like `busy_poller.c`, it supplies local ioctl definitions when headers lack them.

Control flow: fixture `invalid_fd` opens an AF_UNIX datagram socket, then `test_invalid_fd` confirms both epoll ioctls fail with `ENOTTY` on a non-epoll fd. Fixture `epoll_busy_poll` creates an epoll fd and snapshots process capabilities. `test_get_params` seeds the params struct with garbage, verifies `EPIOCGPARAMS` returns zeroed defaults, then checks an invalid userspace pointer yields `EFAULT`. `test_set_invalid` checks invalid padding, too-large `busy_poll_usecs`, invalid `prefer_busy_poll`, large budget with and without `CAP_NET_ADMIN`, and invalid pointer handling. `test_set_and_get_valid` writes valid values and reads them back. `test_invalid_ioctl` verifies an unknown ioctl number fails with `EINVAL`.

State and persistence: state is one epoll fd and temporary process effective capability changes. No files or network devices are modified. The teardown restores resource ownership but capability restoration occurs inside the test before invalid pointer checks.

Dependencies and integration points: requires libcap headers/library, kselftest harness, and kernel epoll busy-poll ioctl support. The test should run with `CAP_NET_ADMIN` for the privileged budget path.

Risks and test signals: because it drops and restores capabilities inside a test, failure before restoration could affect later assertions in the same process. It assumes `CAP_NET_ADMIN` is present at test start. Strong signals are exact errno checks for invalid fd, invalid userspace pointer, invalid fields, permission denial, valid set/get round trip, and unknown ioctl.
