## sources/distributed-fs/eos/mgm/zmq/ZMQ.hh

Purpose: Declares the ZeroMQ wrapper, worker, and task classes for MGM FUSE proxying.

Important APIs and types: `ZMQ` owns the bind URL and a `std::unique_ptr<Task>`, with `ServeFuse` starting proxy service. `ZMQ::Task` owns context, ROUTER frontend, DEALER backend, DEALER injector, worker thread list, and `reply`. `ZMQ::Worker` owns a DEALER socket tied to the task context.

Control flow: a `ZMQ` instance is constructed with a URL, `ServeFuse` creates a `Task`, `Task::run` starts workers and proxy, and workers call `work` until shutdown.

State and persistence: all state is runtime socket/thread state; `gFuseServer` is static process-wide service state. The destructor logs but does not itself stop the task.

Dependencies and integration: depends on MGM namespace macros, `FuseServer::Server`, `<zmq.hpp>`, and POSIX/standard threading.

Risks: detached thread lifecycle means destruction of `ZMQ` without orderly task shutdown can leave work running. `Task` constructor takes non-const `std::string&`, making it less flexible than necessary. Typo-only comments do not affect behavior but signal limited local documentation.

Test signals: compile/link tests against libzmq, lifecycle tests for create/destroy/serve, reply framing, and static fuse server availability.
