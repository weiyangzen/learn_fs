## sources/distributed-fs/eos/mgm/ofs/cmds/SharedPath.inc

Purpose: creates and verifies signed share URLs for EOS files. It binds a path, expiry timestamp, MGM instance name, and file identifier into a symmetric-key signature so shared links become invalid when the file id changes or the link expires.

Important APIs and types: `XrdMgmOfs::CreateSharePath`, `XrdMgmOfs::VerifySharePath`, `XrdOucEnv`, `VirtualIdentity`, `SymKey`, `gSymKeyStore`, `FileId::Fid2Hex`, `_access`, `_exists`, and `_stat`.

Control flow: `CreateSharePath()` namespace-maps the input path, requires read access, verifies the object exists and is a file, stats it as root to retrieve the inode/file id, builds query parameters `eos.share.expires`, `eos.share.fxid`, and `eos.share.signature`, fetches the current symmetric key, encrypts the canonical string `expires + path + expires + instance + fxid`, strips newlines, and returns `path?...signature=...`. `VerifySharePath()` rejects missing signature, missing/zero expiry, missing fid, stat failures, changed file ids, expired timestamps, missing symmetric key, and signature mismatches.

State and persistence behavior: no namespace mutation. Verification does a live stat, so it depends on current file id and path state. The signature uses only the current key, not key id/version data.

Dependencies and integration points: used by share-link authorization paths around XRootD opaque data. Depends on EOS symmetric-key distribution, the MGM instance name, file id stability, path canonicalization from namespace mapping, and current wall-clock time.

Risks: key rotation can invalidate all existing share URLs if only the current key is accepted. The canonical string includes `expires` twice, which must remain stable between producer and verifier. Verification stats the current path, so a replaced file with a different fid invalidates the share as intended, while a moved file likely invalidates the original path. Error logging can include opaque query strings.

Test signals: create link for readable file, reject unreadable path, reject directory, missing key creation failure, verify valid link, reject expired link, reject changed fid, reject modified signature, reject missing fields, and confirm newline stripping makes produced and verified signatures comparable.
