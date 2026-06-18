# sources/distributed-fs/coda/coda-src/vtools/spy.cc

## Purpose

`spy.cc` connects to Venus mariner and prints reports of open files, optionally filtered by uid.

## Important APIs, Types, and Functions

`main()` parses `-host`, `-tcp`, and `-uid`, calls `Bind()`, sends `reporton` or `reporton <uid>`, installs a SIGTERM flush handler, and reads events. `Bind()` chooses Unix-domain mariner socket from `venus.conf` unless `-tcp` is set; TCP mode resolves service `venus`. `CheckMariner()` buffers newline-terminated records up to `MAXPATHLEN` and prints them. `TERM()` flushes stdout/stderr and exits.

## Control Flow

Unlike `codacon`, it does not reconnect. A bind or command write failure exits. Once connected, it blocks in `CheckMariner()` until EOF.

## State and Persistence Behavior

The tool keeps only socket, stream, uid filter, and static input buffer state. It does not persist data or modify Coda state beyond sending the mariner reporting command.

## Dependencies and Integration Points

It depends on Venus mariner protocol, `venus.conf`, `codaconf_lookup`, `coda_getaddrinfo`, Unix sockets, and service name `venus`.

## Risks and Test Signals

As in `codacon`, `-host` is parsed but not used by TCP resolution. `sockaddr_un.sun_path` copying is unchecked. Line truncation occurs at `MAXPATHLEN - 2`. Only SIGTERM is handled; EOF just returns from the read loop and exits implicitly. Tests should mock `reporton` command selection, line buffering, uid option validation, bind failures, and long records.
