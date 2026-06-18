<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/FileDescriptor.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/FileDescriptor.h

Purpose: Adapts a raw file descriptor to the BeeGFS `Pollable` interface with read/write helpers.

Important APIs/types: `FileDescriptor` wraps an fd, exposes `readExact`, `read`, `write`, and `getFD`.

Control flow/state/persistence: `readExact` loops until the requested byte count is read or an error/EOF occurs. `read` and `write` delegate to POSIX calls. Descriptor ownership is not clearly RAII here; caller semantics matter.

Dependencies/integration: Depends on `Pollable` and POSIX IO. Used where fd-backed objects participate in polling/event loops.

Risks/test signals: Partial reads/writes and EINTR/EAGAIN handling should be verified. Tests should cover EOF before exact length, write errors, invalid fd, and poll integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/FileDescriptor.h -->
