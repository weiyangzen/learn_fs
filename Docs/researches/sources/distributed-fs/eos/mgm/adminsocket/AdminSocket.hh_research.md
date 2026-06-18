# sources/distributed-fs/eos/mgm/adminsocket/AdminSocket.hh

Purpose: declares `eos::mgm::AdminSocket`, a lightweight threaded wrapper around the ZeroMQ admin command loop.

Important APIs and types: default constructor leaves the object inactive. The path constructor prefixes `ipc://`, logs the socket path, stores it in `mSocket`, and starts `mThread` with `AdminSocket::Run`. The destructor joins the assisted thread. `Run(ThreadAssistant&) noexcept` is implemented in the `.cc`.

Control flow: construction with a path starts serving immediately; destruction requests/join behavior is delegated to `AssistedThread`.

State and persistence: state is limited to an `AssistedThread` and socket URI string. It does not persist admin command results.

Dependencies and integration points: includes `AssistedThread`, logging, namespace macros, `zmq.hpp`, and standard string/types. Integrates with MGM process command handling through the implementation.

Risks: starting a thread in the constructor can expose partially constructed object state if future fields are added. The default constructor creates an object whose destructor still joins `mThread`, so `AssistedThread` must tolerate a never-started thread. Socket lifecycle and unlink behavior are not visible in the header.

Test signals: constructor/destructor lifecycle tests should validate default and path-created objects, fast destruction after construction, and safe shutdown when `Run` is blocked in polling.
