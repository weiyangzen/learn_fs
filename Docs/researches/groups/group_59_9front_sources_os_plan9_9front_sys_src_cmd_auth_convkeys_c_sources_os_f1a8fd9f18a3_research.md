# Group Research: group_59_9front_sources_os_plan9_9front_sys_src_cmd_auth_convkeys_c_sources_os_f1a8fd9f18a3

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/convkeys.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/convkeys.c

Key database re-encryption and migration tool for Plan 9 auth key files.

Key responsibilities:
- Reads an encrypted key database into memory and decrypts it with either NVRAM machine key or an entered password.
- Recognizes legacy DES format and AES format with `"AES KEYS"` header.
- Validates fixed-size records by checking user names as UTF.
- In verbose mode, prints decrypted usernames without re-encrypting.
- Re-encrypts the database with a newly entered key.
- Optionally converts legacy DES records to AES-format records, appending zeroed AES-key fields.

Dependencies:
- Uses `Authkey`, key database constants, `getauthkey`, `getpass`, `private`, DES/AES CBC routines, and Plan 9 auth command helpers.

Notable risks:
- Operates in place on the key file after successful conversion.
- AES conversion requires an AES machine key; old NVRAM without AES material aborts conversion.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/convkeys.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/cron.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/cron.c

Plan 9 cron daemon for per-user scheduled jobs stored under `/cron`.

Key responsibilities:
- Parses `/cron/<user>/cron` entries with minute/hour/monthday/month/weekday/host/command fields.
- Watches each user's cron file by Qid and reloads jobs when the file changes.
- Enforces that `/cron/<user>` is owned by the same user name.
- Runs jobs locally through `rc -lc` or remotely through `/bin/rx`.
- Creates per-user cron directories/files with `-c`.
- Maintains a `/cron/lock` exclusive file to prevent multiple daemon instances.
- Handles time jumps by adapting backward jumps and capping forward catch-up to one day.
- Uses kernel uid capabilities through `/dev/caphash` and `/dev/capuse` to become the target user before running jobs.

Dependencies:
- Uses Plan 9 auth command helpers, syslog, `/cron`, `newns`, `rx`, `/dev/caphash`, `/dev/capuse`, and `/dev/null`.

Notable risks:
- Command execution is intentionally shell-based and wrapped as `exec rc -c '...'`, with quote escaping.
- Job ownership validation is important because jobs run after uid changes.
- Long time jumps can cause many missed-minute jobs to run in one pass, bounded to one day.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/cron.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/debug.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/debug.c

Diagnostic tool for Plan 9 authentication setup and factotum keys.

Key responsibilities:
- Scans `/mnt/factotum/ctl` for `p9sk1` and `dp9ik` keys.
- Locates/dials auth servers for a key's auth domain, printing the lookup path.
- Prompts for a password and tests whether ticket requests decrypt correctly.
- Supports the `dp9ik` PAK preliminary exchange before ticket tests.
- Verifies returned client/server tickets and challenge echo values.

Dependencies:
- Uses factotum control format, Plan 9 auth server ticket routines, `csgetvalue`, `dial`, ndb/cs lookup, PAK helpers, and authsrv ticket conversion.

Research notes:
- This is a troubleshooting command, not a service.
- It performs interactive password prompting and clears password buffers after use.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/debug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/disable -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/disable

Small rc script to disable a user in mounted auth key databases.

Key responsibilities:
- Requires exactly one username argument.
- If `/mnt/keys/<user>` exists, writes `disabled` to its `status`.
- If `/mnt/netkeys/<user>` exists, writes `disabled` to its `status`.

Dependencies:
- Assumes `keyfs`-style key databases are mounted at `/mnt/keys` and `/mnt/netkeys`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/disable -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/enable -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/enable

Small rc script to re-enable a user in mounted auth key databases.

Key responsibilities:
- Requires exactly one username argument.
- If `/mnt/keys/<user>` exists, writes `ok` to its `status`.
- If `/mnt/netkeys/<user>` exists, writes `ok` to its `status`.

Dependencies:
- Assumes `keyfs`-style key databases are mounted at `/mnt/keys` and `/mnt/netkeys`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/enable -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/factotum/apop.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/factotum/apop.c

Factotum protocol module for APOP and CRAM-MD5 challenge/response authentication.

Key responsibilities:
- Implements shared state machine for `apop` and `cram`.
- Client mode accepts a challenge, finds a password key, and returns an MD5 or HMAC-MD5 response.
- Server mode obtains a challenge from the Plan 9 auth server, receives user/response, and validates via authsrv.
- Produces `AuthInfo` on successful server-side validation.
- Disables a server key after an auth-server protocol failure if it has never succeeded.

Dependencies:
- Uses factotum `Proto`, key lookup, authsrv requests/responses, MD5/HMAC-MD5, and ticket/authenticator conversion helpers.

Notable risks:
- Client mode does not authenticate the server.
- Response size is fixed to hex MD5 length.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/factotum/apop.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/factotum/chap.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/factotum/chap.c

Factotum protocol module for CHAP, MSCHAP, MSCHAPv2, NTLM, and NTLMv2.

Key responsibilities:
- Implements shared client/server state machines for CHAP-family mechanisms.
- Client mode generates CHAP MD5, MSCHAP, MSCHAPv2, NTLM, or NTLMv2 replies from a password key.
- Server mode obtains challenge material from authsrv, collects user/domain/response fields, and relays protocol-specific replies to authsrv.
- Computes NT hash, LM hash, MSCHAP response blocks, NTLMv2 blob, and MSCHAPv2 peer challenge response.
- Produces MPPE/session secret material for MSCHAP/MSCHAPv2 where available.
- Produces `AuthInfo` after successful server-side validation.

Dependencies:
- Uses factotum key lookup, libsec MD4/MD5/SHA1/HMAC/DES helpers, authsrv ticket/authenticator routines, and protocol reply structures.

Notable risks:
- Client modes do not authenticate the server except for derived secret semantics.
- This file contains compatibility cryptography for legacy Microsoft protocols.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/factotum/chap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/factotum/confirm.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/factotum/confirm.c

Factotum support for `/mnt/factotum/confirm` and `/mnt/factotum/needkey` wait queues.

Key responsibilities:
- Queues RPC reads waiting for user confirmation of keys marked with `confirm`.
- Emits confirmation requests into a log-style buffer and accepts `tag`/`answer=yes|no` writes.
- Applies confirmation decisions back to the waiting `Fsstate`.
- Queues RPC reads that need new keys and emits `needkey tag=...` messages.
- Accepts needkey completion/error writes and resumes blocked RPC reads.
- Handles flush/interruption for both confirmation and needkey waiters.

Dependencies:
- Uses `Logbuf` helpers from `log.c`, factotum `Fsstate`, 9P `Req`, and RPC continuation helpers.

Notable risks:
- Confirmation and needkey code paths are parallel copies with separate queues and locks.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/factotum/confirm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/factotum/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/factotum/dat.h

Shared factotum declarations, constants, data structures, and protocol table exports.

Key contents:
- Defines common protocol phases: `Notstarted`, `Broken`, `Established`.
- Defines factotum RPC return codes: failure, needkey, ok, errstr, toosmall, phase, confirm.
- Defines `Fsstate`, the per-open-file state for RPC parsing, protocol state, attributes, authinfo, and confirmations.
- Defines `Key`, `Keyinfo`, `Keyring`, `Logbuf`, and `Proto`.
- Declares globals for command flags, mount/service state, protocol table, and keyring.
- Declares shared helpers from `confirm.c`, `fs.c`, `log.c`, `rpc.c`, `util.c`, and all protocol modules.

Role:
- Acts as the internal ABI between factotum's 9P server, RPC dispatcher, keyring, GUI helpers, and authentication protocol modules.

Notable risks:
- Protocol modules depend on the exact `Fsstate` and `Proto` contracts.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/factotum/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/factotum/ecdsa.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/factotum/ecdsa.c

Factotum ECDSA signing protocol for secp256k1-style private keys.

Key responsibilities:
- Supports client-side signing only; server mode is unimplemented.
- Finds a key/password pair, decrypts a base58-encoded encrypted private key, and derives the public point.
- Signs written message bytes with ECDSA over secp256k1.
- DER-encodes `r` and `s` signature integers for reads.
- Frees mpint and EC private-key material on close.

Dependencies:
- Uses factotum key lookup, base58 decode, SHA-256, AES-CBC, mpint EC routines, and `secp256k1` domain initialization.

Notable risks:
- Password/key validation returns `RpcNeedkey` for bad decrypt/checksum.
- The encrypted-key format is specific: version byte, 32-byte private scalar, checksum, and IV.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/factotum/ecdsa.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/factotum/fgui.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/factotum/fgui.c

Graphical factotum helper for confirmation prompts and missing-key entry.

Key responsibilities:
- Opens `/mnt/factotum/confirm` and `/mnt/factotum/needkey`, reads request messages, and serializes them through a main UI loop.
- Displays key-use confirmation windows with Accept/Refuse and optional remember behavior.
- Caches remembered confirmation answers by matching attribute sets.
- Displays needkey entry forms for queried attributes, masking private fields with an invisible font.
- Writes newly entered keys to `/mnt/factotum/ctl`.
- Writes completion, denial, or cancellation responses back to the relevant factotum file.
- Hides the window while idle and unhides it for active prompts.

Dependencies:
- Uses Plan 9 draw/mouse/keyboard/control libraries, factotum attribute formatting/parsing, and `/mnt/factotum` control files.

Notable risks:
- Remembered confirmations are in-memory only.
- Needkey form construction mutates the parsed attribute list to add blank query fields.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/factotum/fgui.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/factotum/fs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/factotum/fs.c

Factotum main program and 9P file server exposing `/mnt/factotum`.

Key responsibilities:
- Parses factotum flags for server/user mode, debug, prompting, secstore use, mount point, service name, and bootstrap auth addresses.
- Initializes the keyring, protocol table, formatters, capability support, and optional NVRAM keys.
- Mounts/posts the factotum file server, normally as `/mnt/factotum`.
- Optionally imports keys from secstore.
- Exposes files `ctl`, `rpc`, `proto`, `log`, `confirm`, and `needkey`.
- Implements attach, walk, stat, open, read, write, flush, and fid cleanup for the virtual filesystem.
- Routes `rpc` operations to `rpc.c`, control writes to `ctlwrite`, and confirm/needkey/log reads to their queues.
- Lists keys via `ctl` reads and supported protocol names via `proto`.

Dependencies:
- Uses lib9p `Srv`, factotum protocol modules, `postsrerv`/mount semantics, NVRAM auth helpers, and secstore command execution.

Notable risks:
- `confirm`, `needkey`, and `log` are exclusive-use files.
- Each open file gets a fresh `Fsstate`; cleanup must close protocol state and free attrs.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/factotum/fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/factotum/httpdigest.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/factotum/httpdigest.c

Factotum client-side HTTP Digest response generator for RFC 2617-style MD5 digest auth.

Key responsibilities:
- Supports client role only; server role returns unsupported.
- Accepts challenge data as `nonce method uri`.
- Finds a key with `user`, `realm`, and private `!password`.
- Computes `MD5(HA1:nonce:HA2)` with lowercase hex encoding.
- Returns the digest response and marks authentication established without `AuthInfo`.

Dependencies:
- Uses factotum key lookup, attribute handling, tokenize, MD5, and hex encoding.

Notable risks:
- Only the older/simple digest formula is implemented; no qop/cnonce/nc support is present.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/factotum/httpdigest.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/factotum/log.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/factotum/log.c

Factotum in-memory log buffer and blocking log-read support.

Key responsibilities:
- Maintains a 128-message ring buffer.
- Queues 9P read requests until log messages are available.
- Flushes/interupts queued reads.
- Truncates long messages safely, avoiding splitting UTF-8 continuation bytes.
- Mirrors messages to stderr when factotum debug mode is enabled.
- Provides `flog` formatted logging.

Dependencies:
- Uses factotum `Logbuf`, lib9p `Req`, locks, and `estrdup9p`.

Notable risks:
- Old messages are dropped by overwriting ring slots when the write pointer wraps.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/factotum/log.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/factotum/p9any.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/factotum/p9any.c

Factotum protocol negotiator for Plan 9 authentication mechanisms.

Key responsibilities:
- Negotiates `p9sk1` and `dp9ik` between client and server.
- Server side advertises available `proto@domain` pairs from matching server keys.
- Client side chooses a preferred protocol/domain for which it has or can ask for a key.
- Supports version marker `v.2` and an explicit server `OK` step.
- Delegates subsequent read/write operations to the selected sub-protocol.
- Propagates sub-protocol return codes, needkey requests, confirmations, phase changes, and `AuthInfo`.

Dependencies:
- Uses factotum key lookup, attribute mutation, `p9sk1`/`dp9ik` protocol modules, and RPC logging helpers.

Notable risks:
- `p9sk1` is intentionally listed before `dp9ik` for drawterm compatibility.
- The wrapper shares selected attributes and confirmation arrays with the sub-`Fsstate`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/factotum/p9any.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/factotum/p9cr.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/factotum/p9cr.c

Factotum protocol module for legacy Plan 9 textual challenge/response and VNC DES challenge auth.

Key responsibilities:
- Implements `p9cr` client/server challenge-response flow.
- Implements `vnc` client challenge-response using bit-reversed DES key bytes.
- Client mode reads a challenge and returns the computed response.
- Server mode obtains a challenge from authsrv, receives a response, and validates it through authsrv.
- Produces `AuthInfo` after successful server-side validation.
- Provides VNC key parsing from `!password`.

Dependencies:
- Uses factotum key lookup, Plan 9 authsrv challenge requests, DES routines, and ticket/authenticator conversion.

Notable risks:
- The `p9cr` client path maps to `p9sk1` key material for the DES response.
- VNC password handling truncates/zero-pads to 8 DES-key bytes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/factotum/p9cr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/factotum/p9sk1.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/factotum/p9sk1.c

Factotum implementation of Plan 9 `p9sk1` and `dp9ik` authentication.

Key responsibilities:
- Implements client, server, and login-style state machines for Plan 9 secret-key authentication.
- Handles challenge exchange, ticket requests, tickets, authenticators, and final `AuthInfo`.
- Adds `dp9ik` PAK exchange to protect password-derived keys from offline dictionary attacks.
- Supports speak-for keys and client keys with owner/sysuser restrictions.
- Requests tickets from authsrv and falls back to locally generated tickets when authid and hostid match.
- Derives session secrets: DES-derived secret for `p9sk1`, HKDF-expanded secret for `dp9ik`.
- Parses keys from `!hex` or `!password`, hashes AES keys for PAK, and stores parsed `Authkey` in key private state.
- Disables never-successful bad client keys after failed ticket decryption where applicable.

Dependencies:
- Uses authsrv ticket/authenticator encoders, PAK helpers, HKDF/HMAC/SHA-256, DES key conversion, factotum keyring, capability-independent authinfo support.

Notable risks:
- This is the core Plan 9 authentication mechanism; phase ordering and ticket challenge checks are security-critical.
- Local ticket fallback is intentionally constrained to matching authid/hostid.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/factotum/p9sk1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/factotum/pass.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/factotum/pass.c

Factotum protocol module that returns a stored username/password pair.

Key responsibilities:
- Finds a key with `user` and private `!password`.
- Returns quoted `user password` on read.
- Does not support writes or server-side authentication.
- Holds the selected key until close.

Dependencies:
- Uses factotum key lookup and quoting/attribute helpers.

Research notes:
- Comments explicitly discourage this as a general mechanism; it is just a password repository.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/factotum/pass.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/factotum/rpc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/factotum/rpc.c

Factotum `/mnt/factotum/rpc` dispatcher and `/ctl` command parser.

Key responsibilities:
- Enforces paired write/read RPC cycles.
- Parses RPC verbs: `start`, `read`, `write`, `authinfo`, and `attr`.
- Starts protocol modules from `proto=...` attributes and manages implicit close on repeated start.
- Routes protocol read/write calls and formats responses: `ok`, `done`, `needkey`, `toosmall`, `phase`, `error`.
- Serializes `AuthInfo` and injects uid-change capability strings through `mkcap`.
- Logs protocol transitions when debug mode is enabled.
- Parses control verbs: `key`, `delkey`, and `debug`.
- Adds keys for all supplied `proto=` values, splitting public and private attributes.
- Deletes matching keys, allowing private-field patterns only as private queries.

Dependencies:
- Uses factotum `Fsstate`, `Proto`, keyring utilities, confirm/needkey queues, authinfo serialization, and attribute parser/formatter.

Notable risks:
- RPC writes can contain binary arguments after the first verb separator.
- Multi-line control writes are rejected except for a single trailing newline.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/factotum/rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/factotum/rsa.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/factotum/rsa.c

Factotum RSA protocol module for legacy SSH challenge response, signing, and verification.

Key responsibilities:
- Parses RSA public/private key attributes into `RSApriv`.
- Client role exposes public keys, accepts a hex challenge, and returns RSA private-key decrypted response.
- Sign role accepts a hash and returns PKCS#1 padded RSA signature bytes.
- Verify role accepts a hash and signature and returns `ok` or failure text.
- Supports hash algorithms `sha1`, `md5`, and `sha256`.
- Builds simple ASN.1 DigestInfo structures for PKCS#1 signing/verification.
- Requires confirmation for key use when key attributes request it.

Dependencies:
- Uses factotum keyring, libsec RSA/mpint helpers, ASN.1 encode conventions, and hash constants.

Notable risks:
- Only private keys are usable for client/signing operations.
- ASN.1 length handling is intentionally simple for short DigestInfo values.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/factotum/rsa.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/factotum/totp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/factotum/totp.c

Factotum TOTP/HOTP one-time password generator.

Key responsibilities:
- Finds a key with private base32 `!secret`.
- Supports optional public `digits` and `period` attributes.
- Decodes the secret, computes HOTP with HMAC-SHA1 dynamic truncation, and derives TOTP from current nanosecond time.
- Returns a zero-padded code with default 6 digits and 30-second period.
- Rejects invalid digit counts and non-positive periods.

Dependencies:
- Uses factotum key lookup, base32 decode, HMAC-SHA1, and `nsec`.

Notable risks:
- Maximum generated code length is 8 digits.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/factotum/totp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/factotum/util.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/factotum/util.c

Shared factotum utility layer for auth dialing, key lookup, capabilities, authinfo serialization, and attribute handling.

Key responsibilities:
- Dials auth servers via normal `/net/cs` lookup or bootstrap `authaddr`/`/net/ndb` fallback.
- Performs auth-server request setup, including PAK key negotiation when AES key material exists.
- Prompts users for missing keys and writes them to `/mnt/factotum/ctl`.
- Implements key confirmation tracking and reference-counted key cleanup.
- Serializes `AuthInfo` into the factotum RPC wire format.
- Implements `failure`, `toosmall`, phase naming, and phase-error helpers.
- Searches the keyring with attribute patterns, owner restrictions, disabled-key filtering, confirmation checks, and needkey generation.
- Finds Plan 9 server auth keys, preferring `dp9ik` then `p9sk1`.
- Imports NVRAM keys into the factotum keyring.
- Creates uid-change capabilities through `/dev/caphash`.
- Replaces/adds keys in the keyring, copies/sets/sorts attributes, writes hostowner, and disables bad keys.

Dependencies:
- Uses Plan 9 networking, authsrv, NVRAM, factotum key structures, attr parser/formatter, HMAC-SHA1, and `/dev/hostowner`.

Notable risks:
- Key matching semantics combine requested attributes, protocol prompts, owner restrictions, and private attrs.
- Needkey prompts intentionally remove ignored attrs such as `role` and `disabled`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/factotum/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/factotum/wpapsk.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/factotum/wpapsk.c

Factotum WPA-PSK pairwise transient key generator.

Key responsibilities:
- Supports client role only; server role is unimplemented.
- Accepts binary challenge: supplicant MAC, authenticator MAC, supplicant nonce, authenticator nonce.
- Finds a key with `essid` and private `!password`.
- Converts password to PMK either from 64 hex chars or PBKDF2-HMAC-SHA1 over ESSID.
- Computes WPA pairwise key expansion PRF to produce a 64-byte PTK.
- Returns the PTK on read.

Dependencies:
- Uses factotum key lookup, PBKDF2, HMAC-SHA1, and WPA key derivation conventions.

Notable risks:
- Challenge size must exactly match 2 MAC addresses plus 2 nonces.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/factotum/wpapsk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/guard.srv.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/guard.srv.c

Guard service for Securenet/SecurID-style challenge-response authentication.

Key responsibilities:
- Reads a username from stdin using null-terminated argument protocol.
- Generates a numeric challenge and writes a challenge/response prompt.
- Reads a response with a three-minute alarm timeout.
- Accepts either stored network DES-key response via `netcheck` or SecureID response via `secureidcheck`.
- Writes `OK` or `NO`, logs debug details, and updates auth keyfs bad/good logs.
- Extracts remote address from a service directory's `remote` file when provided.

Dependencies:
- Uses auth command helpers, `/lib/ndb/auth`, local ndb, NETKEYDB, `netcheck`, `secureidcheck`, `fail`, and `succeed`.

Notable risks:
- Debug logging masks only the PIN portion of responses to avoid logging full secrets.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/guard.srv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/httpauth.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/httpauth.c

Command-line HTTP Basic authentication checker.

Key responsibilities:
- Accepts either `user pass` or a Basic Authorization value.
- Strips optional `Basic ` prefix and base64-decodes credentials.
- Splits decoded `user:password`.
- Rejects empty usernames and bad base64/format.
- Calls `auth_userpasswd` and prints the authenticated username on success.

Dependencies:
- Uses Plan 9 auth library and base64 decode helper.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/httpauth.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/keyfs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/keyfs.c

9P key database file server for Plan 9 auth key files.

Key responsibilities:
- Mounts a virtual filesystem, default `/mnt/keys`, backed by encrypted `/adm/keys`-style database records.
- Supports DES and AES key database formats; AES format stores DES key, status, warnings, expiration, secret, and AES key per user.
- Decrypts/encrypts the backing key database with NVRAM key or entered password.
- Exposes users as directories with files: `key`, `aeskey`, `pakhash`, `secret`, `log`, `status`, `expire`, and `warnings`.
- Enforces disabled, expired, and purgatory states on key reads.
- Tracks bad login counts through `log`; repeated bad attempts trigger temporary purgatory.
- Supports user create, remove, rename, status updates, expiration updates, secret/key writes, and warning reset.
- Reloads the key database when the backing file mtime changes.
- Optionally runs a daily warning command.
- Supports read-only mounts and alternate mount/keyfile paths.

Dependencies:
- Uses 9P fcall encoding/decoding directly, auth command helpers, DES/AES CBC, NVRAM keys, PAK hash generation, and Plan 9 mount over a pipe.

Notable risks:
- The server rewrites the whole encrypted key file on most mutations.
- Usernames are fixed-length in the on-disk record and validated for UTF/control/slash/space issues.
- The virtual files are mode `0666`, relying on mount/auth service context and data checks rather than per-file Plan 9 ownership.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/keyfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/lib/answer.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/lib/answer.c

Interactive yes/no prompt helper for auth commands.

Key responsibilities:
- Prompts with `<question> [y/n]`.
- Returns true for `y` or `Y`; false otherwise.
- Frees the console response buffer.

Dependencies:
- Uses `readcons` from Plan 9 auth command environment.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/lib/answer.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/lib/error.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/lib/error.c

Shared fatal error helper for auth commands.

Key responsibilities:
- Formats `argv0: ...` messages with varargs.
- Writes the message to stderr.
- Exits with the formatted error buffer.

Dependencies:
- Used by many auth command helper routines and tools.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/lib/error.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/lib/fs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/lib/fs.c

Static description table for mounted auth key filesystems.

Key contents:
- Defines `fs[Plan9]` as `/mnt/keys`, label `plan 9 key`, bio file `/adm/keys.who`.
- Defines `fs[Securenet]` as `/mnt/netkeys`, label `network access key`, bio file `/adm/netkeys.who`.

Role:
- Shared by account/key management tools to address Plan 9 and Securenet databases consistently.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/lib/fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/lib/getauthkey.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/lib/getauthkey.c

Loads the machine auth key from NVRAM or prompts for it.

Key responsibilities:
- Clears the target `Authkey`.
- Calls `readnvram`.
- On failure, prompts for the machine key using `getpass`.
- On success, copies DES and AES machine keys from `Nvrsafe`.
- Clears the temporary NVRAM structure.

Dependencies:
- Uses `Nvrsafe`, `readnvram`, `getpass`, and authsrv key constants.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/lib/getauthkey.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/lib/getexpiration.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/lib/getexpiration.c

Interactive account expiration-date helper.

Key responsibilities:
- Reads an existing `<db>/<user>/expire` value when present.
- Displays defaults as `YYYYMMDD` or `never`.
- Prompts for a new expiration date.
- Accepts empty input as unchanged sentinel `-1`, `never` as `0`, or a date within now and two years from now.
- Converts accepted dates to seconds.

Dependencies:
- Uses Plan 9 `Tm`, `tm2sec`, `localtime`, and console prompting.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/lib/getexpiration.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/lib/getpass.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/lib/getpass.c

Password prompt and key-derivation helper.

Key responsibilities:
- Prompts for a password with echo disabled.
- Optionally validates with `okpasswd`.
- Enforces `PASSWDLEN` maximum.
- Optionally prompts for confirmation and retries on mismatch.
- Derives an `Authkey` with `passtokey` and/or copies the plaintext password to caller buffer.
- Clears temporary password buffers before returning or retrying.

Dependencies:
- Uses `readcons`, `okpasswd`, `passtokey`, and shared `error`.

Notable risks:
- If caller asks for plaintext output, the caller owns later clearing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/lib/getpass.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/lib/keyfmt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/lib/keyfmt.c

Formatter for DES keys in traditional octal presentation.

Key responsibilities:
- Converts 7-byte DES key material into 8 bytes with parity bits cleared.
- Formats the resulting bytes as eight three-digit octal values.
- Installs as a `Fmt` formatter, commonly `%K`.

Dependencies:
- Used by netkey/key printing tools.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/lib/keyfmt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/lib/log.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/lib/log.c

Auth database success/failure logging helper.

Key responsibilities:
- Writes `bad` or `good` messages to `<db>/<user>/log`.
- Applies bad/good records to both Plan 9 key DB and network key DB.
- `fail(user)` logs failure and exits with `failure`.

Dependencies:
- Uses `KEYDB`, `NETKEYDB`, and keyfs `log` file semantics.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/lib/log.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/lib/netcheck.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/lib/netcheck.c

Securenet challenge-response helper routines.

Key responsibilities:
- Computes DES key verification checksum.
- Computes hex challenge response by encrypting ASCII challenge text.
- Converts hex answers to decimal-mode answers for older Securenet modes.
- Checks responses against smart-token format, hex format, and decimal format.
- Implements `smartcheck` checksum-style response validation.

Dependencies:
- Uses DES `encrypt`, shared `error`, and Plan 9 auth key constants.

Notable risks:
- Mutates the response buffer while normalizing uppercase and stripping newline.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/lib/netcheck.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/lib/okpasswd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/lib/okpasswd.c

Basic password policy checker.

Key responsibilities:
- Trims trailing spaces from a password copy.
- Requires at least eight characters.
- Rejects trivial strings such as `login`, `guest`, `passwd`, `anonymous`, and their reverses.

Dependencies:
- Used by `getpass` when password policy checking is requested.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/lib/okpasswd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/lib/private.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/lib/private.c

Process hardening helper for commands handling keys or passwords.

Key responsibilities:
- Opens `/proc/<pid>/ctl`.
- Writes `private` to prevent debugging by other processes.
- Writes `noswap` to prevent sensitive pages from being swapped.
- Emits warnings if either protection fails.

Dependencies:
- Uses Plan 9 proc control semantics.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/lib/private.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/lib/querybio.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/lib/querybio.c

Interactive account biography editor.

Key responsibilities:
- Loads existing bio data with `rdbio`.
- Prompts for post id, full name, department, primary email, sponsor email, and additional email addresses.
- Supports retaining defaults, clearing optional fields with a space, and marking whether data changed.
- Returns whether any field changed.

Dependencies:
- Uses `Acctbio`, `Nemail`, `readcons`, and `rdbio`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/lib/querybio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/lib/rdbio.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/lib/rdbio.c

Reader and clearer for account biography records.

Key responsibilities:
- Frees and clears all dynamically allocated fields in `Acctbio`.
- Reads pipe-separated bio records from a file.
- Selects records matching the requested user.
- Populates post id, name, department, and up to `Nemail` email fields.
- Always sets `a->user` to the requested user.

Dependencies:
- Uses Plan 9 `Biobuf` and `getfields`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/lib/rdbio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/lib/readarg.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/lib/readarg.c

Null-terminated argument reader.

Key responsibilities:
- Reads one byte at a time from an fd.
- Copies up to `len-1` bytes into the destination.
- Stops successfully at NUL and leaves the output NUL-terminated.
- Returns `-1` on EOF before NUL.

Dependencies:
- Used by simple auth service protocols such as guard.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/lib/readarg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/lib/readwrite.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/lib/readwrite.c

File-level key/secret read-write helpers for mounted auth key databases.

Key responsibilities:
- Reads and writes small files by path.
- Finds DES keys, AES keys, PAK hashes, combined `Authkey` records, and account secrets.
- When AES key exists, reads or computes PAK hash with `authpak_hash`.
- Writes DES keys, AES keys, combined keys, and secrets.
- Suppresses writing AES key when it is all zeros.

Dependencies:
- Uses keyfs file layout: `key`, `aeskey`, `pakhash`, and `secret`.
- Uses libsec constant-time comparison and auth PAK hashing.

Notable risks:
- Helpers expect exact byte counts for key files.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/lib/readwrite.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/lib/wrbio.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/lib/wrbio.c

Appender for account biography records.

Key responsibilities:
- Opens or creates the bio file.
- Seeks to end and appends one pipe-separated record.
- Fills absent post id/name/dept as empty strings.
- Defaults first email to the username if absent.
- Writes all present email fields.

Dependencies:
- Uses `Acctbio`, `Nemail`, and shared `error`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/lib/wrbio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/login.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/login.c

Interactive local login command that authenticates a user and starts an rc session.

Key responsibilities:
- Prompts for a user's password and authenticates with `auth_userpasswd`.
- Consumes the returned uid-change capability through `/dev/capuse`.
- Starts a fresh factotum instance and loads `dp9ik` and `p9sk1` password keys into it.
- Builds the authenticated user's namespace with `newns`.
- Re-mounts the new factotum into the namespace and removes the temporary srv file.
- Rebuilds a clean environment with user, home, service, cputype, sysname, and timezone.
- Changes to `/usr/<user>` or `/`, then execs interactive login rc.

Dependencies:
- Uses Plan 9 auth library, `/boot/factotum`, `/srv`, `/mnt/factotum/ctl`, `/dev/capuse`, ndb/csipinfo authdom lookup, and `newns`.

Notable risks:
- Warns if run on a CPU server.
- Password is passed to the child factotum through its control file, then cleared locally.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/login.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/netkey.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/netkey.c

Interactive Securenet response calculator.

Key responsibilities:
- Refuses to run when `service=cpu`.
- Hardens itself with `private`.
- Prompts for a password and derives a DES key.
- Repeatedly reads numeric challenges from stdin and prints `netcrypt` responses.

Dependencies:
- Uses auth command helpers, `passtodeskey`, `netcrypt`, and console prompting.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/netkey.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/newns.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/newns.c

Command wrapper that builds or extends the current user's namespace before running a command.

Key responsibilities:
- Supports `-n namespace`, `-d` namespace debug, and `-a` additive namespace mode.
- Calls `newns(getuser(), namespace)` or `addns(getuser(), namespace)` in a fresh name group.
- Defaults to interactive `/bin/rc -i`.
- Executes requested command, retrying relative command names under `/bin`.

Dependencies:
- Uses Plan 9 auth namespace helpers and `newnsdebug`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/newns.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/none.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/none.c

Command wrapper that becomes user `none`, builds a namespace, and runs a command.

Key responsibilities:
- Supports `-n namespace` and `-d` namespace debug.
- Calls `procsetuser("none")`.
- Builds namespace for `none`.
- Defaults to interactive `/bin/rc -i`.
- Executes requested command, retrying relative command names under `/bin`.

Dependencies:
- Uses Plan 9 auth namespace helpers, `procsetuser`, and `newnsdebug`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/none.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/passwd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/passwd.c

Password-change client for Plan 9 auth server accounts.

Key responsibilities:
- Authenticates the old password against the auth server.
- Defaults to `dp9ik` PAK flow, with `-1` selecting legacy non-PAK path.
- Supports `user@domain` target syntax.
- Prompts whether to change Plan 9 password and/or Inferno/POP secret.
- Sends `Passwordreq` encrypted/packed with the authenticated ticket.
- Retries new password/secret prompts if the server refuses.

Dependencies:
- Uses `authdial`, authsrv ticket/password request functions, `getpass`, `answer`, PAK hashing, and shared hardening via `private`.

Notable risks:
- Old password is retained in the request structure for the password-change protocol.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/passwd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/pemdecode.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/pemdecode.c

PEM section decoder.

Key responsibilities:
- Reads all input from a file or stdin.
- Extracts a named PEM section with `decodePEM`.
- Writes decoded binary to stdout.
- Fails on missing section, read, or write errors.

Dependencies:
- Uses libsec PEM/base64 support.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/pemdecode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/pemencode.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/pemencode.c

PEM section encoder.

Key responsibilities:
- Reads all binary input from a file or stdin.
- Base64-encodes it and wraps output in `-----BEGIN <section>-----` / `-----END <section>-----`.
- Emits 64-character base64 lines.

Dependencies:
- Uses libsec base64 encoding.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/pemencode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/printnetkey.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/printnetkey.c

Network key display tool.

Key responsibilities:
- Looks up a user's DES network key in `NETKEYDB`.
- Prints it using the DES key formatter.
- Rejects overlong/non-NUL-terminated usernames.

Dependencies:
- Uses `finddeskey`, `deskeyfmt`, `NETKEYDB`, and shared `error`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/printnetkey.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/readnvram.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/readnvram.c

NVRAM key dumper in factotum control format.

Key responsibilities:
- Reads `Nvrsafe` from NVRAM.
- Prints `p9sk1` key line when DES machine key is present.
- Prints `dp9ik` key line when AES machine key is present.
- Uses hex-encoded private key fields and placeholder password.
- Fails if no keys are available.

Dependencies:
- Uses `readnvram`, authsrv key constants, and hex formatter.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/readnvram.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/respond.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/respond.c

Small wrapper around `auth_respond`.

Key responsibilities:
- Accepts auth parameter string and challenge.
- Calls `auth_respond` with `auth_getkey`.
- Writes the response and newline to stdout.

Dependencies:
- Uses Plan 9 auth library key lookup and response generation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/respond.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/rsa2any.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/rsa2any.c

Shared RSA key parser and binary encoding helpers for RSA conversion commands.

Key responsibilities:
- Reads a Plan 9 factotum-style `key proto=rsa ...` line from a file or stdin.
- Parses public fields `ek`, `n`, and optional/corrected `size`.
- Optionally requires and parses private fields `!dk`, `!p`, `!q`, `!kp`, `!kq`, `!c2`.
- Regenerates missing or bad CRT fields with `rsafill`.
- Removes RSA numeric/private fields from the returned residual attribute list.
- Provides SSH-style helpers for big-endian 4-byte lengths, strings, raw bytes, and mpints.

Dependencies:
- Uses Plan 9 auth attribute parser, libmp/libsec RSA helpers, and `rsa2any.h`.

Notable risks:
- Error paths do not uniformly free all partial allocations, acceptable for short-lived conversion tools.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/rsa2any.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/rsa2any.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/rsa2any.h

Shared declarations for RSA conversion tools.

Key contents:
- Declares `getrsakey`.
- Declares binary packing helpers: `put4`, `putmp2`, `putn`, and `putstr`.

Role:
- Small common interface used by `rsa2asn1`, `rsa2csr`, `rsa2jwk`, `rsa2pub`, `rsa2ssh`, `rsa2x509`, and `rsafill`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/rsa2any.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/rsa2asn1.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/rsa2asn1.c

RSA key converter to ASN.1 DER.

Key responsibilities:
- Reads a Plan 9 RSA key.
- With `-a`, emits private PKCS#1 DER.
- Without `-a`, emits public PKCS#1 DER by default or SPKI DER with `-f spki`.
- Writes binary DER to stdout.

Dependencies:
- Uses `getrsakey`, `asn1encodeRSApriv`, `asn1encodeRSApub`, and `asn1encodeRSApubSPKI`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/rsa2asn1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/rsa2csr.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/rsa2csr.c

RSA certificate signing request generator.

Key responsibilities:
- Reads a private RSA key.
- Accepts a subject string such as `C=US ... CN=...`.
- Calls `X509rsareq` to create a DER CSR.
- Writes the CSR bytes to stdout.

Dependencies:
- Uses `getrsakey`, libsec X.509 request generation, and mp/hex formatters.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/rsa2csr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/rsa2jwk.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/rsa2jwk.c

RSA public key converter to JSON Web Key format.

Key responsibilities:
- Reads a public RSA key.
- Encodes modulus and exponent as base64url without padding.
- Prints a minimal JSON object with `kty`, `n`, and `e`.

Dependencies:
- Uses `getrsakey`, mpint big-endian conversion, and custom base64url character mapping.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/rsa2jwk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/rsa2pub.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/rsa2pub.c

RSA key public-half extractor.

Key responsibilities:
- Reads a Plan 9 RSA key.
- Preserves residual non-key attributes.
- Prints a factotum-style public key line with `size`, `ek`, and `n`.

Dependencies:
- Uses `getrsakey`, auth attribute formatting, and mpint formatting.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/rsa2pub.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/rsa2ssh.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/rsa2ssh.c

RSA public key converter to OpenSSH authorized-key format.

Key responsibilities:
- Reads a public RSA key.
- Packs SSH wire fields: string `ssh-rsa`, exponent, modulus.
- Base64-encodes the packed key.
- Supports optional `-c comment`.
- Accepts `-2` for backwards compatibility.

Dependencies:
- Uses `getrsakey`, `put4`, `putn`, `putmp2`, and Plan 9 base64 formatter.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/rsa2ssh.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/rsa2x509.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/rsa2x509.c

Self-signed RSA X.509 certificate generator.

Key responsibilities:
- Reads a private RSA key.
- Accepts a subject string.
- Supports `-e expireseconds`; default validity is about three years.
- Calls `X509rsagen` and writes DER certificate bytes to stdout.

Dependencies:
- Uses `getrsakey`, libsec X.509 generation, and time validity array.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/rsa2x509.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/rsafill.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/rsafill.c

RSA private-key normalizer that fills missing CRT fields.

Key responsibilities:
- Reads a private Plan 9 RSA key.
- Uses shared parser, which regenerates missing/bad `!kp`, `!kq`, and `!c2`.
- Prints a full factotum-style private key line with size, public fields, and private CRT fields.

Dependencies:
- Uses `getrsakey`, auth attribute formatting, and mpint formatting.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/rsafill.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/rsagen.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/rsagen.c

RSA private key generator.

Key responsibilities:
- Generates RSA keys with default 2048 bits or `-b bits`.
- Loops until modulus bit length matches the requested size.
- Supports `-t` to add arbitrary factotum key attributes.
- Prints a factotum-style `key proto=rsa ...` private key line.

Dependencies:
- Uses libsec `rsagen`, mpint formatting, and Plan 9 I/O.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/rsagen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/secstore/SConn.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/secstore/SConn.c

Delimited secure connection wrapper used by secstore.

Key responsibilities:
- Wraps an fd in `SConn` with read/write/free/secret callbacks.
- Initially sends and receives SSL-style length-prefixed clear records.
- After `secret`, derives separate in/out RC4 and SHA1 keys from a shared secret and direction.
- Adds SHA1 integrity digest and RC4 encryption to records.
- Tracks per-direction sequence numbers in integrity hashes.
- Provides `writerr` in-band `!message` errors and `readstr` string reads.

Dependencies:
- Uses RC4, HMAC-SHA1/SHA1, Plan 9 fd I/O, and `SConn.h`.

Notable risks:
- This is legacy RC4/SHA1 transport protection.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/secstore/SConn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/secstore/SConn.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/secstore/SConn.h

Header for secstore's delimited authenticated/encrypted connection abstraction.

Key contents:
- Defines `Maxmsg` as 4096.
- Defines `SConn` callback structure: `secret`, `read`, `write`, and `free`.
- Declares `newSConn`, `writerr`, `readstr`, and allocation helpers.
- Documents direction semantics for deriving read/write secrets.

Role:
- Shared interface for secstore client/server PAK and encrypted message exchange.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/secstore/SConn.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/secstore/aescbc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/secstore/aescbc.c

Standalone AES-CBC file encrypt/decrypt utility used by secstore workflows.

Key responsibilities:
- Reads password from console, fd 3 (`-i`), or NVRAM config (`-n`).
- Derives AES key from SHA1 label plus passphrase, then derives HMAC key with MD5 of AES key.
- Encrypts with header `AES CBC SHA1  2\n`, random IV, random initial plaintext block, AES-CBC data, and HMAC-SHA1 trailer.
- Decrypts v2 format, verifies HMAC, and writes plaintext.
- Includes compatibility decryption path for older secstore format with sentinel block.
- Supports `-e` encryption; default path is decryption despite usage text mentioning `-d`.

Dependencies:
- Uses libsec AES-CBC, SHA1, HMAC-SHA1, MD5, NVRAM, Biobuf, and console prompting.

Notable risks:
- Legacy compatibility path has weaker authentication semantics than the v2 HMAC path.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/secstore/aescbc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/secstore/dirls.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/secstore/dirls.c

Directory listing formatter for secstore.

Key responsibilities:
- Reads all directory entries for a path and sorts by name.
- Computes SHA1 digest for each listed file.
- Formats lines with aligned name, size, ctime-derived timestamp, and base64 SHA1 digest.
- Returns the accumulated listing as a newly allocated string.

Dependencies:
- Uses Plan 9 `dirreadall`, `dirstat`, SHA1, base64 encoding, and secstore allocation helpers.

Notable risks:
- `sha1file` returns nil for unreadable files, but listing code assumes a digest pointer when encoding.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/secstore/dirls.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/secstore/pak.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/secstore/pak.c

Secstore Password Authenticated Key Exchange implementation.

Key responsibilities:
- Defines fixed PAK group parameters and initializes them lazily.
- Computes long password hash `H` and inverse `Hi` from version, client id, and passphrase hash.
- Provides `PAK_Hi` for account password verifier generation.
- Implements short hashes for server proof, client proof, and session secret derivation.
- Implements `PAKclient`: sends client id and blinded exponent, verifies server proof, sends client proof, and installs session secret.
- Implements `PAKserver`: parses first client message, loads password verifier, sends server proof, verifies client proof, installs session secret, and updates failed login counters.

Dependencies:
- Uses libmp modular arithmetic, SHA1/HMAC-SHA1, secstore `SConn`, password database helpers from `password.c`, and `secstore.h`.

Notable risks:
- File comments note PAK patent/licensing history.
- Authentication failure updates account failed counters and may trigger lockout behavior in password handling.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/secstore/pak.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/secstore/password.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/secstore/password.c

Secstore account password-verifier file reader/writer.

Key responsibilities:
- Opens account files under `SECSTORE_DIR/who/<id>` after filename validation.
- Falls back to `FICTITIOUS` account when requested account is absent.
- Parses account fields: expiration, disabled status, STA flag, failed count, other data, and `PAK-Hi`.
- Rejects expired, disabled, corrupted, or temporarily locked accounts unless caller requests dead-or-alive editing.
- Resets failed counter after five minutes when lockout period passes.
- Writes updated account records with `putPW`.
- Frees `PW` structures and mpint verifier material.

Dependencies:
- Uses secstore path definitions, Plan 9 Biobuf, mpint parsing/formatting, and file mtimes.

Notable risks:
- Missing accounts deliberately map to a fictitious account to avoid leaking existence during PAK handling.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/secstore/password.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/secstore/secchk.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/auth/secstore/secchk.c

Small SecureID check test command for secstore/auth configuration.

Key responsibilities:
- Opens `/lib/ndb/auth` and local ndb, concatenating them for lookup.
- Prints current user.
- Calls `secureidcheck(getenv("user"), argv[1])` and prints the result.

Dependencies:
- Uses ndb and external `secureidcheck`.

Research notes:
- Usage string says the single argument is `pinsecurid`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/auth/secstore/secchk.c -->