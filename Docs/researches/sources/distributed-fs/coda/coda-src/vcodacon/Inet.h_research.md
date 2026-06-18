# sources/distributed-fs/coda/coda-src/vcodacon/Inet.h

## Purpose
Declares a small portable socket wrapper for TCP, optional Unix-domain sockets, and line-oriented I/O.

## Important APIs, Types, And Functions
`Inet` exposes connection/server methods, `Accept`, `Close`, `Readline`, `Write`, `Writeline`, status/error accessors, remote-name/address helpers, and newline mode setters. Macros abstract `close`/`closesocket`, last error, and remote length type.

## Control Flow
GUI or utility code creates an `Inet`, opens a connection, registers the fd, reads lines, writes commands, and closes on errors.

## State And Persistence
The class stores socket descriptor and peer metadata only for object lifetime.

## Dependencies And Integration Points
Includes platform socket headers and optional `sys/un.h`. Used by `vcodacon` monitor code.

## Risks
Assignment is destructive move-like behavior but is exposed as `operator=`, which can surprise users. `RemoteAddr()` assumes an IPv4 sockaddr even if other address families are introduced.

## Test Signals
Compile on Unix, Cygwin/Solaris, and Windows paths; test assignment invalidates source; and validate fd/error accessors.
