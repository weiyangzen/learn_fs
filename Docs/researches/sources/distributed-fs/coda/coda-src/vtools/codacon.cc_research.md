# sources/distributed-fs/coda/coda-src/vtools/codacon.cc

## Purpose

`codacon.cc` is a text monitor for Venus mariner events. It connects to the local Venus mariner socket, requests fetch/store event reporting, suppresses selected completion noise, appends timestamps, and prints human-readable event messages.

## Important APIs, Types, and Functions

`main()` parses `-tcp` and optional host, repeatedly connects, sends `set:fetch`, and calls `CheckMariner()`. `Bind()` chooses either the configured Unix-domain `marinersocket` from `venus.conf` or a TCP connection to service `venus` using `coda_getaddrinfo`. `CheckMariner()` buffers input lines up to `MARINERBUFSIZE`, trims trailing spaces, appends current local time, and calls `CheckTheMariner()`. `CheckTheMariner()` splits optional `prefix::message` records and filters `fetch`, `store`, and `mond` messages containing ` done `.

## Control Flow

The program loops forever. A failed bind sleeps five seconds and retries. A successful bind is wrapped with `fdopen()`, configured by writing `set:fetch\n`, then read until EOF. When Venus disconnects, the stream is closed and the outer loop reconnects.

## State and Persistence Behavior

It keeps only transient socket and line-buffer state. It does not persist data, but it can keep reconnecting indefinitely and continuously writes to stdout.

## Dependencies and Integration Points

It integrates with Venus' mariner Unix/TCP control protocol, `venus.conf`, `codaconf_lookup`, service name `venus`, and Coda RPC2 address wrappers.

## Risks and Test Signals

The optional `host` argument is accepted but not actually used by TCP `Bind()`, which calls `coda_getaddrinfo(NULL, "venus", ...)`. The Unix socket path is copied into `sockaddr_un.sun_path` without bounds checking. Static line buffering truncates long records near the end. Tests should mock mariner input, verify prefix filtering/timestamp formatting, exercise reconnect paths, and cover Unix/TCP address selection.
