# sources/control-plane/longhorn-engine/integration/common/constants.py

## Purpose
Collects integration test constants for instance-manager addresses, binary paths, retry intervals, volume/engine/replica names, sizes, backup paths, backing files, frontend type, and metadata filenames.

## Important APIs, Types, and Functions
- Instance-manager addresses/types and process states.
- Size constants: `SIZE`, `EXPANDED_SIZE`, `BLOCK_SIZE`, `PAGE_SIZE`.
- Name constants derived from required `TESTPREFIX` environment variable.
- Backup/backing paths such as `BACKUP_DIR`, `VFS_DIR`, qcow2/raw backing file paths.
- Metadata names such as `REPLICA_META_FILE_NAME`, expansion disk names, and `LOGS_DIR`.

## Control Flow
Module import reads `TESTPREFIX` from environment and builds deterministic names.

## State and Persistence Behavior
No runtime mutation, but constants determine test-created process names, volume names, filesystem paths, and backup bucket locations. Missing `TESTPREFIX` fails import.

## Dependencies and Integration Points
Imported by nearly all integration helpers and tests. Values must align with container/test environment paths and generated fixtures.

## Risks and Edge Cases
Hardcoded `/tmp`, `/data/backupbucket`, `/dev/longhorn`, and `/engine-binaries` paths assume a specific integration environment. `TESTPREFIX` lookup via `dict(os.environ)["TESTPREFIX"]` raises `KeyError` if not set.

## Test Signals
Constants are indirectly validated whenever integration tests run; mismatched paths fail process creation, device lookup, or backup operations.
