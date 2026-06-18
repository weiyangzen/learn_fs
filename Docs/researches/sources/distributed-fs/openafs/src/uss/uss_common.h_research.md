
# sources/distributed-fs/openafs/src/uss/uss_common.h

Purpose: `uss_common.h` is the shared contract for `uss` state, constants, and helper routines. It centralizes legacy field sizes, default password, verbosity constants, path sizes, volume status layout, cleanup-list type, and all exported globals.

Important types and APIs: `struct uss_subdir` records directories whose ACLs must be restored, with a backward link, path, and final ACL string. `uss_VolumeStatus_t` mirrors the volume status structure needed for pioctl quota/status calls without including conflicting headers. The API exposes `uss_common_Init()`, `uss_common_Reset()`, and `uss_common_FieldCp()`.

Control flow and integration: nearly every `uss` implementation includes this header. The parser, command layer, PTS/KAS/VLDB modules, ACL code, and filesystem template actions communicate mostly through these globals instead of explicit context objects.

State and persistence: the header declares process-global mutable fields that represent one current user/account operation. Persistent side effects are not in the header, but this state determines PTS/KAS identities, mount-point paths, volume metadata, ACL cleanup, and dry-run/overwrite behavior.

Risks and test signals: fixed sizes and global mutability are the dominant hazards. APIs do not enforce initialization order or safe copying. Test coverage should include maximum-size boundary values for each exported buffer, reset of `uss_currentDir`, and interactions between saved and per-operation values.
