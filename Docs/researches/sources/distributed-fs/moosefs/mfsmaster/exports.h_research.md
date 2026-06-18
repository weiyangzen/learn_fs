# sources/distributed-fs/moosefs/mfsmaster/exports.h

Purpose: public interface for MooseFS export authorization and export-info serialization. It is used by client-session handling and administrative listing paths in the master.

Important APIs/types/functions: `exports_info_size(versmode)` computes the byte size needed for serialized export records; `exports_info_data(versmode, buff)` writes those records. `exports_check()` authorizes a client IP, protocol version, path or meta request, optional password challenge/response, and returns session flags, umask, uid/gid mappings, storage-class groups, trash-retention bounds, and disabled operation bits. `exports_reload()` reloads configuration. `exports_checksum()` returns the current aggregate checksum. `exports_init()` initializes and validates that at least one export exists.

Control flow: startup calls `exports_init()`. Client session setup calls `exports_check()` with a real path for filesystem sessions or `NULL` path for metadata sessions; password-protected exports require the caller to supply the challenge and response buffers. Administrative clients first call `exports_info_size()` to allocate a packet and then `exports_info_data()` to fill it. Reload is coordinated elsewhere, with this header exposing the reload hook.

State/persistence: the header exposes only in-memory operations. The implementation reads an external config file and keeps active records in process memory. `exports_checksum()` is the state-change signal passed to session management.

Dependencies/integration: includes fixed-width integer types and semantically depends on MooseFS protocol status codes, session flags, export groups, and disabled-operation masks. Main consumers are `matoclserv.c` and the sessions subsystem.

Risks/test signals: callers must provide valid output pointers to `exports_check()`; the implementation writes all result fields on success. Callers must also respect `MFS_ERROR_NOPASSWORD` and `MFS_ERROR_BADPASSWORD` distinctly so password negotiation works. Tests should cover allocation using `exports_info_size()` followed by `exports_info_data()`, meta versus filesystem checks, checksum propagation into session changes, and reload-triggered session invalidation.
