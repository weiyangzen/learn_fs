# sources/distributed-fs/coda/coda-src/auth2/pwsupport.c

## Purpose
Server-side auth2 password database support. It loads `auth2.pw`, keeps an indexed in-memory key array by ViceId, validates users, returns login handshake/session keys, and appends password/user changes to the password file.

## APIs, Types, and Functions
Exports `InitPW()`, `PWGetKeys()`, `PWChangePasswd()`, `PWNewUser()`, `PWDeleteUser()`, `PWChangeUser()`, `IsAUser()`, `IsAdministrator()`, and `GetVname()`. Internal helpers include `BuildPWArray()`, `EnlargePW()`, `AppendPW()`, `IsADeletedUser()`, and `BogusKey()`. Important globals are `FileKey`, `NullKey`, `DeleteKey`, `PWFile`, `PWArray`, `PWLen`, `PWCount`, `PWTime`, `AdminID`, and `CheckOnly`.

## Control Flow, State, and Persistence
`InitPW(PWFIRSTTIME)` seeds the default file key, allocates `PWArray`, opens and shared-locks `db/auth2.pw`, forces mode `0600`, reads the full file, resolves the admin group id, initializes the all-ones delete key, and parses records. `PWGetKeys()` resolves a counted identity to a ViceId, reloads the file when mtime changes, rejects missing/deleted users, decrypts the stored key with `FileKey`, and generates a random session key. Mutating RPCs check read-only mode, connection private `UserInfo`, administrator or self privileges, user existence, and bogus-key sentinel collisions before calling `AppendPW()`. `AppendPW()` XOR-encrypts the key, hex-encodes it, appends a timestamped audit line under an exclusive lock, updates `PWArray`, and refreshes `PWTime`.

## Dependencies and Integration
Depends on RPC2 secure compare/encryption/random helpers, Coda file locking, `vice_config_path()`, protection database APIs `AL_NameToId()`, `AL_IdToName()`, `AL_GetInternalCPS()`, `AL_IsAMember()`, and auth2 RPC private connection state. It is the server counterpart to `cpasswd`, user-admin tools, and `initpw`.

## Risks and Test Signals
Risks include append-only growth requiring offline compaction, weak XOR-at-rest protection, abort-heavy error handling, global mutable state without obvious synchronization, a suspicious `otherInfo` validation condition that rejects spaces and non-graph characters, possible buffer truncation in append records, and reliance on mtime for reload detection. Test signals include successful login key retrieval, mtime-triggered reloads, deletion by all-ones key, read-only rejection, administrator enforcement, file mode correction, and password-change audit lines.
