## sources/distributed-fs/lizardfs/src/mount/masterproxy.cc

Purpose: provides a local TCP proxy endpoint for tools that need to talk to the master through the mounted client. It listens on loopback, exposes its location via the `masterinfo` special file for sufficiently new masters, and forwards most packets through `fs_custom`.

Important APIs: `masterproxy_init` creates a nonblocking loopback listener on an ephemeral port and starts an acceptor thread. `masterproxy_getlocation` overwrites master host/port in a 14-byte masterinfo buffer when proxying is available and master version is at least 1.6.24. `masterproxy_term` stops the acceptor. Worker routines are `masterproxy_acceptor` and `masterproxy_server`.

Control flow: accepted client sockets get detached threads. Each server thread reads a packet header and payload, handles `CLTOMA_FUSE_REGISTER` for tools locally by validating the register blob and returning OK, otherwise calls `fs_custom` to rewrite the message id, send to master, receive a response, restore the original id, and write it back to the local client.

State and dependencies: global listener fd, proxy thread, terminate flag, proxy host/port. Uses `common/sockets`, packet serialization, `MFSCommunication`, and `mastercomm`.

Risks: each connection creates a detached pthread, so resource exhaustion is possible under local abuse. Reads and writes use 1-second timeouts and close on partial IO. Protocol validation is minimal outside the register special case. `terminate` is a plain byte read by another thread.

Test signals: best verified by opening `masterinfo`, connecting to advertised loopback location, performing tool registration, forwarding a known packet, and checking shutdown joins the acceptor.
