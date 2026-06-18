# sources/distributed-fs/lizardfs/utils/redirect_bind.c

Purpose: LD_PRELOAD library that intercepts `bind()` and shifts nonzero TCP stream ports by +1000. It lets tests transparently relocate services away from default ports.

Important APIs/functions: overridden `bind()` copies the supplied `sockaddr` as `sockaddr_in`, checks `SO_TYPE` with `getsockopt`, increments `sin_port` for `SOCK_STREAM` sockets with nonzero ports, lazily resolves the real `bind` with `dlsym(RTLD_NEXT, "bind")`, and calls it.

Control flow: all sockets pass through one wrapper. Only IPv4-shaped `sockaddr_in` and stream sockets are modified; zero port requests remain ephemeral.

State and persistence: no persistent state. A static function pointer caches the real symbol.

Dependencies/integration: intended for test environments using `LD_PRELOAD`. Depends on GNU dynamic linker and IPv4 socket layout.

Risks and test signals: casts every `sockaddr` to `sockaddr_in`, so IPv6 or Unix-domain bind calls can be misinterpreted before `getsockopt` determines type. Port addition can exceed 65535 and wrap through `htons`. Test signals are TCP port shift, UDP no-op, port zero no-op, and non-IPv4 socket safety.
