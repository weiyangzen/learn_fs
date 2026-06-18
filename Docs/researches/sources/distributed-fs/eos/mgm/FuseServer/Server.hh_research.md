# sources/distributed-fs/eos/mgm/FuseServer/Server.hh

Purpose: declares the FUSEX metadata `Server` class in `eos::mgm::FuseServer`. The class owns the managers used by FUSE clients (`Clients`, `Caps`, `Lock`, `Flush`) and exposes the operation surface implemented in `Server.cc`.

Important APIs and types: public accessors `Client`, `Cap`, `Locks`, and `Flushs` expose internal managers. Metadata helpers `FillContainerMD`, `FillFileMD`, and `FillContainerCAP` serialize namespace state and issue capabilities. Authorization helpers `ValidateCAP`, `ValidatePERM`, and `InodeFromCAP` guard mutating operations. The operation API mirrors FUSEX protobuf operations: flush begin/end, get/list, set directory/file/link, get cap, delete directory/file/link, get/set lock, and top-level `HandleMD`. Lifecycle methods are `start`, `shutdown`, `MonitorCaps`, `terminate`, and `should_terminate`.

Control flow: callers are expected to use `HandleMD` for dispatch, while individual `Op*` methods are exposed for internal routing and tests. The class keeps a termination atomic used by background monitor threads. `Header` formats framed synchronous responses.

State and persistence: the header itself stores no persistent namespace state, but it declares in-memory `mClients`, `mCaps`, `mLocks`, `mFlushs`, the termination flag, and `c_max_children`, which bounds directory listing size. Persistent effects are performed by the implementation through MGM namespace services.

Dependencies and integration points: includes namespace macros from `Namespace.hh`, generated `fusex.pb.h`, lock tracker headers, FUSE server subcomponents, and `IFileMD`. The class inherits `eos::common::LogId`, making it part of EOS logging/audit context. Consumers include the MGM ZMQ/FUSE server path.

Risks: the accessors expose mutable internal managers directly, so thread safety depends on each manager and caller discipline. `Flushs` is misspelled but part of the public interface. Many methods accept mutable `VirtualIdentity&`, and implementation can rewrite it for owner-auth; tests need to check caller-visible mutation expectations.

Test signals: compile/API tests should ensure operation declarations match protobuf dispatch in `Server.cc`; unit seams can target `Header`, cap validation, permission fallback, and lifecycle termination behavior with fake manager state.
