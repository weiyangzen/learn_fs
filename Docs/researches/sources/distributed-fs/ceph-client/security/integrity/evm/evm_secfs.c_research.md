<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/evm/evm_secfs.c -->
# sources/distributed-fs/ceph-client/security/integrity/evm/evm_secfs.c

## Purpose
Implements the EVM securityfs control plane under `/sys/kernel/security/integrity/evm`. It exposes the EVM initialization/key state and, when enabled, lets privileged users extend or lock the set of protected xattrs.

## Important APIs, Types, And Functions
- `evm_read_key()` and `evm_write_key()` implement the `evm` control file.
- Optional `evm_read_xattrs()` and `evm_write_xattrs()` implement `evm_xattrs` under `CONFIG_EVM_ADD_XATTRS`.
- `evm_init_secfs()` creates the securityfs directory, control file, symlink, and optional xattr file.
- State includes `evm_dir`, `evm_symlink`, optional `evm_xattrs`, `xattr_list_mutex`, and `evm_xattrs_locked`.

## Control Flow
Initialization calls `integrity_fs_init()`, creates `integrity/evm`, creates an `evm` file backed by key operations, then creates a top-level symlink and optional xattr-control file. Writing a valid initialization bitmask to `evm` requires `CAP_SYS_ADMIN`; HMAC initialization calls `evm_init_key()` and sets `EVM_SETUP_COMPLETE`, preventing further writes. Optional xattr writes add security-prefixed names to `evm_config_xattrnames`, re-enable existing disabled names, or lock the file by writing `.`.

## State And Persistence
Securityfs files are runtime state, not on-disk configuration. The writes mutate global in-kernel state: `evm_initialized`, the protected-xattr list, and a lock bit that turns `evm_xattrs` read-only. Audit records persist externally through the audit subsystem.

## Dependencies And Integration Points
This file depends on securityfs, audit, capabilities, EVM key initialization, and the shared `integrity_dir` from `iint.c`. The protected-xattr list is consumed locklessly by HMAC/hash calculation and EVM policy checks, so new entries are appended and never deleted.

## Risks And Edge Cases
Incorrect initialization writes can permanently set setup completion for the boot. The xattr list uses a mutex only for read/write operations while hot paths traverse locklessly, making append-only behavior essential. `evm_xattrs` accepts only `security.*` names and enforces maximum xattr-name length; a lock write changes file mode to prevent later mutation.

## Test Signals
Read `/sys/kernel/security/integrity/evm/evm` for initialization bits, write valid and invalid bitmasks as privileged user, observe `EVM_SETUP_COMPLETE` after HMAC load, read/write `evm_xattrs` when configured, and check audit events for protected-xattr additions and failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/evm/evm_secfs.c -->
