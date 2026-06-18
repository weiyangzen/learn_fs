# sources/distributed-fs/eos/mgm/misc/AuditHelpers.hh

Purpose: header-only helpers for converting EOS namespace metadata objects into `eos::audit::Stat` protobuf messages used by MGM audit logging.

Important APIs and functions: `auditutil::buildStatFromFileMD` fills ctime/mtime seconds, optional nanosecond string fields, owner uid/gid, permission mode in numeric and octal string forms, optional size, and optional checksum for an `IFileMD`. `auditutil::buildStatFromContainerMD` does the same for an `IContainerMD` except size and checksum are not applicable. Both functions are null-safe and return immediately when the shared pointer is empty.

Control flow: callers pass metadata already obtained from namespace services. The helpers read ctime/mtime into `IFileMD::ctime_t` structures, format `<sec>.<nsec>` strings with `snprintf` when requested, mask modes with `07777`, and set protobuf fields. File checksum formatting delegates to `eos::appendChecksumOnStringAsHex`.

State and persistence behavior: no state or persistence. The output protobuf becomes part of audit event records elsewhere; these helpers only copy current metadata snapshots.

Dependencies and integration points: depends on `proto/Audit.pb.h`, file/container metadata interfaces, checksum utilities, and C stdio formatting. Callers include `XrdMgmOfsFile.cc`, Fuse server operations, `Commit.cc`, and chmod/chown command handlers.

Risks and test signals: callers must ensure metadata lifetime and locking are appropriate before invoking these helpers; the helpers do not lock metadata internally. `%ld` formatting assumes time values fit long on the build platform. Mode formatting buffer is fixed at eight bytes but adequate for `0%04o`. Checksum inclusion can be more expensive and should be requested only where needed. Tests should verify null handling, namespace timestamp formatting, mode masking, checksum opt-in, and file/container field differences.
