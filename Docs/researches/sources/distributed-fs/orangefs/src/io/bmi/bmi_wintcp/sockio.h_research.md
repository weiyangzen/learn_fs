# sources/distributed-fs/orangefs/src/io/bmi/bmi_wintcp/sockio.h

Purpose: declares the WinSock utility interface used by `bmi-wintcp.c` and provides convenience macros for socket buffer/low-water settings and Windows blocking-mode control.

Important APIs/types/macros: function prototypes cover socket creation, any-address bind, specific-address bind, connect, address initialization, nonblocking recv/send/peek, vector I/O through `LPWSABUF`, socket option get/set, TCP option set, and optional sendfile. `GET_RECVBUFSIZE`, `GET_SENDBUFSIZE`, `SET_RECVBUFSIZE`, `SET_SENDBUFSIZE`, `GET_MINSENDSIZE`, `GET_MINRECVSIZE`, `SET_MINSENDSIZE`, and `SET_MINRECVSIZE` wrap the option helpers. `SET_NONBLOCK`, `SET_NONBLOCK_AND_SIGIO`, and `CLR_NONBLOCK` use `ioctlsocket(FIONBIO)` because Windows does not use `fcntl` for socket nonblocking mode.

Control flow support: the header intentionally presents a POSIX-like API while hiding WinSock-specific types and calls. `SET_NONBLOCK_AND_SIGIO` degrades to `SET_NONBLOCK` because there is no direct Windows equivalent for `FASYNC` in this implementation. `BRAINDEADSOCKS` can compile out buffer-size setters on platforms where changing socket buffers is unsafe.

State and persistence behavior: no state is stored by the header. The macros directly mutate socket blocking mode or options on caller-owned sockets. Socket buffer tuning flows from `BMI_tcp_set_info` through `bmi_set_sock_buffers` and these macros.

Dependencies and integration: includes WinSock2, `sys/types.h`, `stdio.h`, and `bmi-types.h`. The `LPWSABUF` signature links the vector I/O API to WinSock. `bmi-wintcp.c` includes this header for all low-level socket operations and uses its macros during server setup, accepted connection setup, outbound connection setup, and tuning.

Risks: macros do not report failures; callers of `SET_NONBLOCK` and `CLR_NONBLOCK` cannot tell if `ioctlsocket` failed. The public prototypes use `int` for socket descriptors even though `BMI_sockio_new_sock` returns `SOCKET`, which can be wider or unsigned on Windows. Low-water option macros may not be supported consistently by WinSock. The comment block still references older POSIX/Linux behavior, so maintainers need to distinguish historical intent from the active Windows implementation.

Test signals: compile on supported Windows toolchains, verify socket descriptor type conversions, nonblocking and blocking transitions, buffer option macros with valid and invalid sockets, and feature-flag builds for `BRAINDEADSOCKS` and `__USE_SENDFILE__`.
