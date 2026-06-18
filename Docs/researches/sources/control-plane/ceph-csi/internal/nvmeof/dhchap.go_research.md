# sources/control-plane/ceph-csi/internal/nvmeof/dhchap.go

Purpose: Implements DH-CHAP key identity, generation, storage, lookup, and removal helpers for NVMe-oF authentication.

Important APIs/types/functions: Exports mode constants (`DHCHAPEmpty`, `DHCHAPModeNone`, `DHCHAPModeUniDirectional`, `DHCHAPModeBiDirectional`), hash constants, `DHCHAPKeys`, `GetOrCreateDHCHAPHostKey`, `GetOrCreateDHCHAPSubsystemKey`, `RemoveDHCHAPHostKey`, `RemoveDHCHAPSubsystemKey`, and internal helpers for key IDs and key generation.

Control flow: Get-or-create first attempts lookup through `SecurityKeyManager`. Only `ErrKeyNotFound` triggers generation; other errors abort to avoid replacing existing keys during KMS/storage failures. Generation builds a deterministic key ID from key prefix, node ID, and a 16-character SHA-256 hash of subsystem NQN, then invokes `nvme gen-dhchap-key` and stores the resulting key string.

State and persistence behavior: Key values are persisted encrypted through `SecurityKeyManager`. Key IDs are deterministic per node/subsystem and split host versus subsystem direction. Raw random bytes are generated in-process but the actual key output comes from `nvme gen-dhchap-key`; the generated `keyBytes` are not passed to that command.

Dependencies and integration points: Depends on `crypto/rand`, SHA-256 hashing, `util.ExecCommandWithTimeout`, `nvme` CLI availability, shared `connectTimeout`, and Ceph-CSI logging. Controller uses returned keys for gateway host configuration; node uses the same key IDs to set `nvme connect` DH-CHAP arguments.

Risks: The allocated random bytes are unused, so entropy comes from `nvme gen-dhchap-key`, not the local buffer. Key ID includes raw node ID; unusual characters may propagate into backend key names. The code assumes missing keys map to `ErrKeyNotFound`. External KMS backends with different not-found errors could prevent key generation.

Test signals: No direct unit tests for key ID format, hashing, generation validation, or command invocation. Security correctness depends on integration and manual validation.
