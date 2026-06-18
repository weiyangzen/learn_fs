<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/user/graphite_connect_test.c -->
# sources/distributed-fs/orangefs/src/apps/user/graphite_connect_test.c

## Purpose
Standalone connectivity probe that repeatedly sends a fixed metric to a hard-coded Graphite endpoint on TCP port 2003.

## Important APIs, Types, And Functions
`main` loops forever building `system.graphite_test 1000 <timestamp>` and writing it to a socket. `graphite_connect` opens an IPv4 TCP socket, resolves the address with `gethostbyname`, fills `sockaddr_in`, and connects.

## Control Flow
Every 20 seconds it opens a fresh connection, writes the NUL-terminated metric buffer, closes the socket, and repeats. There is no command-line parsing.

## State And Persistence
No local persistence. External state is one metric stream delivered to Graphite if the endpoint is reachable.

## Dependencies And Integration Points
Uses POSIX sockets, DNS/host lookup APIs, and Graphite plaintext protocol conventions. It is a developer/test utility related to `ofs_graphite_driver.c`.

## Risks And Test Signals
Risks include hard-coded IP address, implicit prototype for `graphite_connect` in old C modes, unused variables, printing `server->h_addr` as a string, no handling for failed connect before `write`, and sending `strlen()+1` including a NUL byte. Test signals are connection success to a test Graphite listener, failure handling for invalid host, and validating the emitted plaintext metric format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/user/graphite_connect_test.c -->
