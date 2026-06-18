## sources/distributed-fs/moosefs/mfsmaster/mfssupervisor.c

Purpose: command-line supervisor client for the MooseFS master control port. It connects to master servers, optionally requests forced metadata storage, and supports verbose/debug output.

Important APIs and types: no custom types. `usage` prints command help and exits. `main` parses `-h`, `-v`, `-x`, `-s`, `-H`, `-P`, and `-B`, initializes string error handling, fills defaults from `DEFAULT_MASTERNAME` and `DEFAULT_MASTER_CONTROL_PORT`, then calls `msupervisor_simple(masterhost, masterport, bindhost, debug, store)`.

Control flow: options allocate replacement strings with `strdup` and free old values if repeated. Help/version exit early via a shared cleanup label. After defaulting missing host/port/bind values, the result of `msupervisor_simple` becomes the process exit code.

State and persistence behavior: no persistent state is stored locally. With `-s`, the remote master may perform metadata storage through the supervisor protocol handled by `matomlserv.c`.

Dependencies and integration points: depends on `mastersupervisor.h` for client protocol, `strerr` initialization, `idstr` for version/default constants, libc `getopt`, and heap allocation. It integrates operationally with the `MATOML` master control service.

Risks: all host/port/bind inputs are trusted strings passed to the supervisor library; validation belongs there. `usage` exits with status 1 even for `-h`, but `main` calls it directly for `-h`, so the later `res=0` path is unreachable in that case.

Test signals: CLI tests should cover help/version, repeated options, default values, bind address handling, `-s` store flag propagation, and connection failures from `msupervisor_simple`.
