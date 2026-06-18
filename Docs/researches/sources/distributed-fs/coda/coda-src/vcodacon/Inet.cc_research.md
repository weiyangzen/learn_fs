# sources/distributed-fs/coda/coda-src/vcodacon/Inet.cc

## Purpose
Implements the `Inet` socket wrapper used by `vcodacon` to connect to Coda's mariner/codacon stream over TCP or Unix-domain sockets.

## Important APIs, Types, And Functions
`Inet` methods include constructor/destructor, move-like assignment, `TcpOpen(host,port)`, Unix-socket `TcpOpen(path)`, `TcpServer`, `Accept`, `Close`, `Readline`, `Write(char *)`, `Write(int)`, and `Writeline`. Platform sections handle Winsock startup/cleanup and Unix socket APIs.

## Control Flow
Client open creates a socket, resolves host or fills `sockaddr_un`, connects, and records `remname`. Server open binds/listens. Accept fills a target `Inet` and resolves remote name. `Readline()` reads one byte at a time until newline/CRLF or buffer limit depending on `unixlines`. Writes send strings and append line endings for `Writeline()`.

## State And Persistence
State is per-object descriptor, last error, server flag, remote name/address/length, and newline mode. No persistent storage exists.

## Dependencies And Integration Points
Depends on POSIX sockets or Winsock, config feature macros, and `Inet.h`. `monitor.cc` uses it for GUI event-loop integration through `FileNo()`.

## Risks
`remname` is allocated with `strdup()` but freed with `delete[]`, which mismatches allocation. `Readline()` writes `data[length] = 0` when full, one past the caller's length. The Unix/newline conditional structure means CRLF handling is tied to `unixlines` logic and deserves scrutiny. Name resolution uses legacy `gethostbyname/gethostbyaddr`.

## Test Signals
Connect to TCP and Unix sockets, read LF and CRLF lines at buffer boundaries, write strings/integers/lines, close/reopen, accept clients, run under ASAN for allocation mismatch and buffer limits, and test Winsock lifecycle if supported.
