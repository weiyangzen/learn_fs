# sources/distributed-fs/eos/mgm/adminsocket/AdminSocket.cc

Purpose: implements a small ZeroMQ REP admin socket that accepts IPC requests, maps them to MGM proc commands, executes them as root identity, and returns command output.

Important APIs and functions: `AdminSocket::Run` creates a ZMQ context/socket, binds to `mSocket`, polls with a 100 ms timeout, receives request bytes, splits command and CGI at `?`, creates an `IProcCommand` through `ProcInterface::GetProcCommand`, opens/stat/reads/closes it, and sends the result as the reply.

Control flow: the thread loops until `ThreadAssistant` reports termination. Invalid receives are ignored after logging. Requests without `?` do not create a proc command and receive an empty reply. ZMQ send/receive exceptions are logged and the loop continues.

State and persistence: no persistent state is owned here. The socket path is in `mSocket`; all command side effects are delegated to the proc command implementation and global MGM services.

Dependencies and integration points: depends on `zmq.hpp`, `IProcCommand`, `ProcInterface`, `XrdOucErrInfo`, EOS logging, and `VirtualIdentity::Root`. The header starts this function in an `AssistedThread`.

Risks: every valid command is executed as root and identified as `adminsocket@localhost`, so socket filesystem permissions and path ownership are the effective security boundary. There is no explicit maximum reply size beyond command `stat` result. Empty or malformed input silently returns an empty frame, which may hide client errors. Binding failures are not caught in `Run`.

Test signals: tests should cover command/CGI splitting, empty request behavior, proc command errors, large outputs, termination while polling, ZMQ exception handling, and deployment checks for IPC socket permissions.
