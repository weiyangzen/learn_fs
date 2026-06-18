# Group Research: group_1500_plan9_sources_os_plan9_plan9_sys_src_cmd_auth_factotum_fgui_c_sourc_8f7c20dc5181

Scope: `Docs/research_subset_a.md`; source tree `sources/os/plan9/plan9`. This grouped report covers Plan 9 authentication utilities, factotum protocol/server code, secstore client/server code, and a few auxiliary command tools.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/fgui.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/fgui.c

Implements the graphical front end for factotum prompts. It opens `/mnt/factotum/confirm` and `/mnt/factotum/needkey`, starts reader procs for each, parses request attributes, extracts `tag=...`, and serializes handling through a channel in `threadmain`.

The confirmation path builds a control window showing key attributes and `Accept`/`Refuse` controls plus a “remember” checkbox. Remembered answers are stored in an in-memory `Memory` linked list keyed by matching request attributes, then reused without prompting.

The need-key path builds a dynamic form from query attributes, adds two extra blank query rows, fills defaults such as `user=getuser()`, masks private `!` fields with the invisible password font, and writes the completed key to `/mnt/factotum/ctl` as `key %A`.

Important dependencies: Plan 9 draw/control/thread APIs, factotum attr parsing/formatting (`_parseattr`, `%A`), and mounted factotum files. Notable risk: the code comments admit need-key error handling after writing `/mnt/factotum/ctl` is incomplete.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/fgui.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/fs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/fs.c

Defines factotum’s 9P file server and process entry point. `main` parses flags, optionally protects itself with `private` and `noswap`, initializes protocol table entries, loads nvram/secstore keys, and posts/mounts the service.

The exported tree is `/factotum` with files `confirm`, `needkey`, `ctl`, `rpc`, `proto`, and `log`. `confirm`, `needkey`, and `log` are exclusive where appropriate; `rpc` is world-readable/writable for authentication exchanges; `ctl` accepts key-management writes and lists keys on read.

Open allocates an `Fsstate` per fid, read dispatches to RPC/confirm/needkey/log/list handlers, write dispatches to `rpcwrite`, `needkeywrite`, `confirmwrite`, or `ctlwrite`, and destroy closes active protocol state.

Important behavior: server mode `-S` disables prompting and loads nvram only; `-g` prompts for a key and sends it to an existing factotum; secstore fetching can be driven by nvram config password. This file is the central integration point for all factotum protocol modules.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/httpdigest.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/httpdigest.c

Implements client-side HTTP Digest MD5 authentication for RFC 2617 style challenge/response. Server mode is explicitly unsupported.

Protocol state is `CNeedChal -> CHaveResp -> Established`. On write, it finds a matching key with `user`, `realm`, and private `!password`, parses `nonce method uri`, and computes `MD5(HA1:nonce:HA2)` as lowercase hex. On read, it returns the stored digest response.

Key prompt is `user? realm? !password?`; `addkey` uses `replacekey`. Dependencies include MD5, attr/key matching, and factotum phase/error helpers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/httpdigest.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/log.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/log.c

Implements an asynchronous ring-buffer log for factotum’s `/mnt/factotum/log`. Readers are queued in `Logbuf.wait`; log messages are delivered as they arrive.

`logbufproc` pairs waiting reads with queued messages, truncating safely when the caller’s buffer is too small and avoiding cutting UTF-8 continuation bytes before appending `...\n`. `logbufflush` interrupts queued reads.

`flog` formats into a fixed 1024-byte stack buffer and appends to the global `logbuf`; if global `debug` is enabled, log entries are also printed to stderr.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/log.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/p9any.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/p9any.c

Implements the `p9any` protocol negotiator. Its negotiable protocol list contains `p9sk1`; it exchanges `proto@domain` offerings and then relays to a selected subprotocol.

Client flow reads server protocol list, selects a matching key/protocol/domain, writes `proto dom`, optionally waits for `OK` in version 2, then relays read/write calls to the subprotocol. Server flow advertises available `p9sk1@dom` keys, receives client selection, initializes the subprotocol, optionally returns `OK`, then relays.

`passret` propagates subprotocol return states, authinfo, needkey strings, confirmation requests, and toosmall sizes to the outer `Fsstate`. This file is a wrapper state machine around `p9sk1`, with careful ownership of `subfss` and shared attrs.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/p9any.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/p9cr.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/p9cr.c

Implements text challenge/response protocols `p9cr` and `vnc`. Client protocol writes a challenge and reads a response; server protocol writes a user, reads a challenge, writes a response, then validates through the auth server.

`p9cr` uses DES password-derived response formatting for Plan 9 netkey-style challenges. `vnc` derives an 8-byte DES key from `!password` after reversing bits in each byte, then encrypts the VNC challenge.

Server-side `getchal` contacts the auth server with a `Ticketreq`, reads a challenge, and later validates the response by reading a ticket and authenticator. Bad first-use keys can be disabled. `vncaddkey` stores preprocessed key material in `Key.priv`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/p9cr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/p9sk1.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/p9sk1.c

Implements Plan 9 shared-secret authentication protocols `p9sk1` and the incomplete `p9sk2`. It manages ticket requests, tickets, authenticators, challenges, and authinfo secrets.

Client `p9sk1` starts by generating and reading a client challenge; server waits for that challenge, sends a ticket request, receives ticket/authenticator, and returns a server authenticator. `p9sk2` skips the initial challenge and is marked flawed/incomplete.

Client key lookup supports both normal `role=client` keys and `role=speakfor` keys, allowing the host owner to speak for another local user while preserving restrictions for non-owner callers. Tickets are fetched from an auth server or locally generated when possible. Key addition accepts `!hex` or `!password`, converting to DES key material.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/p9sk1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/pass.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/pass.c

Implements a simple password repository protocol named `pass`. It has no server-side exchange and only supports reading a stored user/password pair.

`passinit` finds a matching key, copies its public attributes into the current state, and enters `HavePass`. `passread` returns quoted `user password` from public `user` and private `!password`. `passwrite` is always a phase error.

Used by callers that need factotum-managed retrieval of username/password credentials. Key prompt is `user? !password?`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/pass.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/rpc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/rpc.c

Implements `/mnt/factotum/rpc` request parsing and `/mnt/factotum/ctl` key-management writes. RPCs are paired write/read cycles with verbs `start`, `read`, `write`, `authinfo`, and `attr`.

`rpcwrite` records a pending verb and binary argument. `rpcread` executes it: `start` parses attrs and initializes a protocol; `read` and `write` dispatch to the active protocol state machine; `authinfo` serializes `AuthInfo` with a generated capability; `attr` returns current attrs.

Return handling maps internal `Rpc*` codes into textual responses or queues confirmation/needkey requests. `ctlwrite` supports `key`, `delkey`, and `debug`, splits public/private attrs, handles multi-protocol key addition, and validates private-field deletion patterns.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/rsa.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/rsa.c

Implements factotum’s `rsa` protocol for old SSH challenge response plus signing and verification roles. Supported roles are `client`, `sign`, and `verify`.

For `client`, reads iterate over candidate public moduli, then a written challenge is private-key decrypted after confirmation checks. For `sign`, a caller writes a hash and reads a PKCS#1-padded RSA signature. For `verify`, caller writes hash then signature and reads `ok` or failure text.

`readrsapriv` parses public and private mpints from key attrs; `rsaaddkey` stores an `RSApriv` in `Key.priv`. The signing path builds ASN.1 `DigestInfo` for SHA1 or MD5 and applies PKCS#1 v1.5-style padding.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/rsa.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/secstore.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/secstore.c

Embeds a reduced secstore client inside factotum for boot-time key retrieval. `havesecstore` probes the secstore server for the current `owner`, and `secstorefetch` authenticates, handles optional STA, fetches the `factotum` file, decrypts it, and feeds each line to `ctlwrite`.

This file duplicates enough of secstore’s secure connection and PAK password-authenticated key exchange to operate without the full secstore command. `SConn` records are framed with SSL-style two-byte lengths, can switch to RC4/SHA1 authenticated encryption, and use sequence-numbered SHA1 integrity checks.

Fetched secstore files are AES-CBC decrypted using a key derived from the secstore password and authenticated by a trailing `XXXXXXXXXXXXXXXX` sentinel. The decrypted file is expected to contain factotum `key ...` control lines.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/secstore.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/util.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/util.c

Large shared utility layer for factotum. It covers network/auth dialing, secstore dialing, console prompting, key insertion/replacement, key matching, protocol lookup, nvram key conversion, authinfo serialization, capability creation, and attr manipulation.

`findkey` is central: it combines current attrs with extra query attrs, checks ownership, skips disabled keys unless requested, handles confirmation through `canusekey`, and returns `RpcNeedkey` with a sorted query string when prompting is allowed. `matchattr` implements query/nameval/default matching across public and private attrs.

Security-related helpers include `private` setup elsewhere, `mkcap` using `#¤/caphash`, `disablekey` after failed authentication, zeroing selected secrets, and owner/secstore host derivation through `writehostowner`. `memrandom` uses `fastrand`, so protocol callers relying on it inherit that randomness quality.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/wep.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/wep.c

Implements a factotum `wep` protocol for configuring wireless WEP keys on a supplied Plan 9 ether device. All work occurs after finding a key and writing device control commands.

`wepinit` searches for a key with at least one private `!key1`, `!key2`, or `!key3`, then stores it in state. `wepwrite` accepts a device name, requires it to start with `#l`, dials its control channel, writes available keys, optional `essid`, and `crypt on`.

There is no meaningful read phase; `wepread` is a phase error. Key prompt is `!key1? !key2? !key3? essid?`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/wep.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/guard.srv.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/guard.srv.c

Implements the guard network authentication service. It reads a user argument from fd 0, sends a numeric challenge prompt, reads a NUL-terminated response, and validates it with netkey or SecurID.

It uses `/lib/ndb/auth` plus local ndb data, extracts remote address from an optional connection directory, and logs debug failures without exposing the PIN portion of SecurID responses. Authentication success writes `OK`; failure writes `NO`, records failed login state, and exits failure.

The netkey check currently uses `NETKEYDB`; a commented block shows prior Plan 9 key fallback. Timeout is enforced with `alarm` and a notify handler.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/guard.srv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/keyfs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/keyfs.c

Implements a standalone 9P filesystem serving encrypted account key databases, mounted by default at `/mnt/keys`. It exposes users as directories with files `key`, `secret`, `log`, `status`, `expire`, and `warnings`.

The server reads/writes `/adm/keys`-style fixed-record databases encrypted with old DES CBC using an auth key from nvram or an entered password. It supports creating/removing/renaming user directories, reading and writing DES keys/secrets, recording bad/good login counts, purgatory delays after repeated failures, expiration, disabled status, and warning counters.

The 9P server is handwritten around `Fcall`, fid tracking, qids, and `convM2S`/`convS2M`. It reloads the key file when mtime changes and can periodically exec `auth/warning`. User records use fixed `ANAMELEN` names and hash buckets.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/keyfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/lib/error.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/lib/error.c

Defines `error`, a shared fatal helper for auth commands. It prefixes messages with `argv0`, formats varargs into a stack buffer, writes to stderr, and exits with the same message buffer.

Used by many small auth utilities as the common fatal error path.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/lib/error.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/lib/fs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/lib/fs.c

Defines the global `fs` table for Plan 9 and Securenet key databases. Each entry records mount path, user-facing key description, `who` metadata file, and cached `Biobuf`.

Used by warning and account-management tools to operate on `/mnt/keys` and `/mnt/netkeys` uniformly.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/lib/fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/lib/getauthkey.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/lib/getauthkey.c

Reads the machine authentication key from nvram into an 8-byte DES key buffer. If nvram cannot be read, it prompts the operator to enter the machine key using `getpass`.

`getkey` zeroes the `Nvrsafe` struct after copying `machkey`; `getauthkey` always returns success after prompting fallback.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/lib/getauthkey.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/lib/getexpiration.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/lib/getexpiration.c

Provides expiration-date prompting for account tools. `getdate` parses `YYYYMMDD` into a `Tm`; `getexpiration` reads the current expiration from `<db>/<user>/expire`, displays it as a default, then prompts for `YYYYMMDD` or `never`.

It validates that new expiration is in the future and within two years. Return values are epoch seconds, `0` for never, or `-1` when the user accepts no change.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/lib/getexpiration.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/lib/keyfmt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/lib/keyfmt.c

Defines `%K` formatting for DES keys. It converts the internal 7-byte DES key representation into 8 parity-cleared bytes and prints each byte in three-digit octal.

Used by tools such as `printnetkey` for operator-readable key display.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/lib/keyfmt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/lib/log.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/lib/log.c

Provides shared login-attempt logging helpers. `record` writes `bad` or `good` to a user’s `log` file in a key database.

`logfail` records failures for both Plan 9 and network key databases; `succeed` records successes for both; `fail` logs a failure and exits. These integrate with `keyfs` log counters.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/lib/log.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/lib/netcheck.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/lib/netcheck.c

Implements network challenge-response helpers for Securenet/netkey. `netresp` encrypts the ASCII decimal challenge with the DES key and formats the high 32 bits as hex. `netdecimal` maps hex letters to keypad-style decimal digits.

`netcheck` accepts either the hex response or decimal-mapped response, after first trying `smartcheck`. `smartcheck` implements a checksum-like variant that transforms challenge digits, encrypts them, and compares decimalized bytes.

Also provides `checksum`, a key verification checksum formatted as `C xx...`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/lib/netcheck.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/lib/okpasswd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/lib/okpasswd.c

Checks password quality for auth tools. It trims trailing spaces, requires at least 8 characters, and rejects a small list of trivial passwords and their reverses.

Returns `nil` for acceptable passwords or an explanatory string for rejection.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/lib/okpasswd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/lib/querybio.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/lib/querybio.c

Prompts interactively for account biography metadata. It first loads existing data with `rdbio`, then prompts for post id, full name, department, user email, sponsor email, and additional emails.

`defreadln` supports defaults, required fields, and clearing optional fields with a leading space. `querybio` returns whether any field changed.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/lib/querybio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/lib/rdbio.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/lib/rdbio.c

Reads account biography records from a pipe-delimited file. `rdbio` scans for matching username, clears previous `Acctbio`, and fills post id, full name, department, and up to `Nemail` email fields.

`clrbio` frees all dynamically allocated fields and zeroes the structure.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/lib/rdbio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/lib/readarg.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/lib/readarg.c

Reads a NUL-terminated argument from a file descriptor into a fixed buffer. It zeroes the destination first, stores up to `len-1` bytes, and succeeds once `\0` is read.

Used by service protocols that exchange NUL-terminated text fields over stdin/stdout.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/lib/readarg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/lib/readln.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/lib/readln.c

Provides console input helpers for auth commands. `readln` prints a prompt, optionally enables raw console mode, handles backspace and interrupt character, and enforces a fixed buffer length.

`getpass` loops until a password converts with `passtokey`, optionally confirms and runs `okpasswd`. `getsecret` asks whether to assign an Inferno/POP secret and can reuse the Plan 9 password.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/lib/readln.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/lib/readn.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/lib/readn.c

Defines a small exact-read helper. It loops until `len` bytes have been read or a read returns zero/error, returning `-1` on short read.

Used by auth protocol code that needs fixed-size records.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/lib/readn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/lib/readwrite.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/lib/readwrite.c

Provides file-backed key and secret helpers. `findkey` and `setkey` read/write `DESKEYLEN` bytes at `<db>/<user>/key`; `findsecret` and `setsecret` read/write string secrets at `<db>/<user>/secret`.

`readfile` and `writefile` wrap simple open/read/write/close behavior with minimal error propagation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/lib/readwrite.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/lib/wrbio.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/lib/wrbio.c

Appends an `Acctbio` record to a biography file. It defaults missing fields to empty strings, defaults missing first email to the username, then writes `user|postid|name|dept|email...`.

Used with `rdbio/querybio` account metadata workflows.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/lib/wrbio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/login.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/login.c

Implements a console login program. It prompts for a password, authenticates via `auth_userpasswd`, writes the returned capability to `#¤/capuse` to change uid, starts a private factotum, seeds it with a `p9sk1` password key, builds the user namespace, and starts interactive `rc`.

It preserves selected environment variables (`cputype`, `sysname`, `timezone`) while creating a fresh environment with `service=con`, `user`, `home`, and object type. It warns when run on a CPU server.

Contains local copies of `readln`, `setenv`, factotum mount/start helpers, and uid-change logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/login.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/netkey.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/netkey.c

Interactive netkey response generator. It refuses to run on CPU servers, prompts for a password, derives a DES key with `passtokey`, then loops reading numeric challenges from stdin and printing encrypted responses.

Uses `netcrypt` to produce the response string.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/netkey.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/newns.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/newns.c

Command wrapper for constructing a new namespace and then execing a command. Supports `-a` to add namespace rules, `-d` for debug, and `-n namespace` to select the namespace file.

Defaults to `/lib/namespace` and `/bin/rc -i`. If exec of a relative command fails, it retries under `/bin`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/newns.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/none.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/none.c

Runs a command as user `none` in a new environment/name group. It writes `none` to `#c/user`, builds a namespace for `none`, then execs the requested command or `/bin/rc`.

Useful for dropping privilege into the conventional unauthenticated Plan 9 user.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/none.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/passwd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/passwd.c

Client for changing Plan 9 and Inferno/POP passwords via the auth server. It requests an `AuthPass` ticket, asks for the old password, verifies it can decrypt the ticket, then loops prompting for optional new Plan 9 password and optional secret.

It marshals `Passwordreq` encrypted with the ticket key and sends it to the auth server until accepted. `asrdresp` handles `AuthOK` and `AuthErr` response framing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/passwd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/pemdecode.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/pemdecode.c

Reads a PEM file or stdin, extracts the named section with `decodePEM`, and writes raw decoded bytes to stdout.

The command requires a section tag and optional file path. It reads the entire input into memory before decoding.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/pemdecode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/pemencode.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/pemencode.c

Reads binary input from a file or stdin, base64 encodes it, and emits a PEM block with the supplied tag. Output lines are wrapped at 64 characters.

The usage string mistakenly says `auth/pemdecode`, but behavior is PEM encoding.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/pemencode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/printnetkey.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/printnetkey.c

Prints the network key for a named user from `NETKEYDB`. It validates the username fits `ANAMELEN`, reads the key file, and formats it with `%K`.

Intended for auth administrators inspecting network access keys.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/printnetkey.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/readnvram.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/readnvram.c

Reads auth nvram and prints a factotum `key proto=p9sk1 ... !hex=...` control line for the stored machine key. It tolerates `readnvram` returning `-1` if auth fields are still populated.

Rejects all-zero machine keys. Output includes a placeholder `!password=______`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/readnvram.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/respond.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/respond.c

Small wrapper around `auth_respond`. It accepts auth params and a challenge, uses `auth_getkey` to obtain key material, writes the generated response to stdout, and appends a newline.

Useful for testing or scripting Plan 9 auth challenge responses.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/respond.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/rsa2any.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/rsa2any.c

Shared RSA/DSA key parser and SSH-style binary encoding helpers. `getkey` reads a factotum `key proto=rsa ...` line, parses public/private mpints, validates/corrects `size`, and regenerates CRT fields with `rsafill` when missing or malformed.

`getdsakey` parses `proto=dsa` keys with public `p`, `q`, `alpha`, `key` and private `!secret`. Both functions return remaining non-key attrs through `pa`.

`put4`, `putn`, `putstr`, and `putmp2` serialize fields for SSH-compatible buffers, including positive mpint leading-zero handling.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/rsa2any.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/rsa2any.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/rsa2any.h

Header declaring shared RSA/DSA key parsing and binary serialization helpers used by the `rsa2*` tools.

No implementation logic; it defines the cross-file interface for `getkey`, `getdsakey`, `put4`, `putn`, `putstr`, and `putmp2`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/rsa2any.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/rsa2csr.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/rsa2csr.c

Generates an X.509 certificate signing request from an RSA private key. It takes a subject string and optional key file, loads the key with `getkey(..., needprivate=1)`, calls `X509req`, and writes DER output.

Installs mpint and hex formatters for diagnostics/output support.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/rsa2csr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/rsa2pub.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/rsa2pub.c

Converts an RSA key line to a public-only factotum key line. It preserves non-key attrs, emits `size`, `ek`, and `n`, and omits private fields.

Uses `getkey(..., needprivate=0)` so it can process public or private input.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/rsa2pub.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/rsa2ssh.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/rsa2ssh.c

Converts an RSA key to old SSH public-key text format: bit length, exponent, modulus. It accepts an optional input file and requires only public key fields.

Uses `%B` mpint formatting with precision limits for exponent/modulus.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/rsa2ssh.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/rsa2x509.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/rsa2x509.c

Generates a self-signed X.509 certificate from an RSA private key and subject string. `-e` sets validity duration in seconds; default validity is roughly three leap years from current time.

Calls `X509gen` and writes DER certificate bytes to stdout.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/rsa2x509.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/rsafill.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/rsafill.c

Reads an RSA private key, regenerates/ensures CRT components through shared `getkey`, and prints a complete factotum RSA key line containing public and private fields.

Useful for repairing keys missing `!kp`, `!kq`, or `!c2`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/rsafill.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/rsagen.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/rsagen.c

Generates a new RSA private key line for factotum. Options set bit length (`-b`, default 1024) and extra attrs (`-t`). It loops until the modulus has exactly the requested bit length.

Outputs `proto=rsa`, optional tag attrs, `size`, public exponent, private exponent, modulus, primes, and CRT fields.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/rsagen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/secstore/SConn.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/secstore/SConn.c

Implements secstore’s framed secure connection abstraction. Before session secret setup, records are length-prefixed plaintext. After `SC_secret`, records include SHA1 integrity over secret, plaintext, and sequence number, then RC4 encryption over digest and payload.

`newSConn` wraps an fd and installs read/write/free/secret methods. `readstr` implements secstore’s in-band error convention where messages starting with `!` become errors; `writerr` sends such error messages.

This is the full version used by secstore commands and daemon, while factotum embeds a local copy.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/secstore/SConn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/secstore/SConn.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/secstore/SConn.h

Declares `SConn`, `Maxmsg`, secure-connection callbacks, constructor, in-band error helpers, and memory helper prototypes.

Documents that `secret(conn, bytes, dir)` derives direction-specific digest/encryption keys, with `dir=0` for client and `dir=1` for server.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/secstore/SConn.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/secstore/aescbc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/secstore/aescbc.c

Standalone encrypt/decrypt tool for secstore-compatible AES-CBC files. It supports password from console, fd 3 (`-i`), or nvram config (`-n`), and encryption mode (`-e`).

Version 2 format writes header `AES CBC SHA1  2\n`, unpredictable IV, encrypted random first block, AES-CBC ciphertext, and HMAC-SHA1 authentication keyed by MD5 of the AES key. Decryption also supports an older compatibility format with trailing `XXXXXXXXXXXXXXXX`.

Used for emergency decryption/encryption of secstore files outside the network client.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/secstore/aescbc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/secstore/dirls.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/secstore/dirls.c

Builds secstore directory listings. It reads a directory, sorts entries by name, and formats each regular readable file with aligned name, size, mtime, and base64 SHA1 digest.

`sha1file` streams file contents to compute digests. `dirls` returns a heap-allocated listing string consumed by `secstored` for `GET .`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/secstore/dirls.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/secstore/pak.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/secstore/pak.c

Implements secstore’s PAK password-authenticated key exchange. It defines fixed group parameters, derives `H(passphrase)` and inverse `Hi`, and uses SHA1-based confirmation hashes for server, client, and session keys.

`PAKclient` sends client identity and `m=g^x H`, verifies server `mu` and `k`, sends `k'`, and installs the session secret into `SConn`. `PAKserver` parses the first message, loads the user `PW`, computes `mu=g^y`, verifies client proof, updates failure counters, and installs the server-side session secret.

The code supports a zero-knowledge existence probe: if client `m` is zero, server reports account existence without authenticating.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/secstore/pak.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/secstore/password.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/secstore/password.c

Manages secstore account files under `/adm/secstore/who`. `getPW` parses expiration, disabled/STA flags, failed counters, comments, and `PAK-Hi`; it falls back to a `FICTITIOUS` account for nonexistent users to reduce account enumeration.

It rejects expired, disabled, or temporarily locked accounts unless `dead_or_alive` is set. Accounts with at least 10 failures are locked for five minutes based on mtime, then reset.

`putPW` rewrites account metadata and `PAK-Hi`; `freePW` releases all dynamic fields and mpints.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/secstore/password.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/secstore/secchk.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/secstore/secchk.c

Small diagnostic wrapper for `secureidcheck`. It opens auth/local ndb databases, prints current `user`, checks the provided PIN+SecurID response, and prints the returned result.

Used to test RADIUS/SecurID integration from the secstore context.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/secstore/secchk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/secstore/secstore.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/secstore/secstore.c

Implements the secstore network client. It logs in with PAK, handles optional STA, and supports get (`-g`), factotum-line get (`-G`), put (`-p`), remove (`-r`), password change (`-c`), server override, user override, stdin password, nvram password, and verbose mode.

File contents are encrypted client-side with AES-CBC using a key derived from the secstore password; the wire is also protected by `SConn`. `getfile` decrypts and authenticates the trailing sentinel, optionally returning file data in memory. `putfile` encrypts local/memory data, sends size, IV, ciphertext, and sentinel.

`chpasswd` sends a new `PAK-Hi`, downloads each file, decrypts with old password, and reuploads encrypted under the new password. The command carefully streams `-G` output line by line for `/mnt/factotum/ctl`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/secstore/secstore.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/secstore/secstore.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/secstore/secstore.h

Shared secstore definitions. It declares log name, storage root `/adm/secstore`, maximum file size, password status bits `Enabled` and `STA`, and the `PW` account structure.

Also declares account management, password prompting, filename validation, and PAK client/server APIs.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/secstore/secstore.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/secstore/secstored.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/secstore/secstored.c

Implements the secstore daemon. It announces by default on `tcp!*!5356`, forks per connection, performs PAK authentication, optionally enforces STA/SecurID, sends `OK`, and then serves commands until `BYE`.

Supported commands are `GET file`, `GET .` for directory listing, `PUT file`, `RM file`, and `CHPASS`. All filenames are passed through `validatefile`, and data is stored under `/adm/secstore/store/<user>/`.

The daemon logs client operations and remote address, has a 30-minute child alarm, supports verbose foreground behavior, custom server name, custom net mount point, and forced STA mode.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/secstore/secstored.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/secstore/secuser.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/secstore/secuser.c

Interactive secstore account administration tool. It ensures secstore directories exist, creates or edits a `PW` account, prompts for password, expiration date, enabled/disabled state, STA requirement, and comments.

New passwords are converted to `PAK-Hi`; existing accounts can keep their current password by entering an empty password. New accounts also create `/adm/secstore/store/<user>`.

Writes changes through `putPW` and logs `CHANGELOGIN`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/secstore/secuser.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/secstore/util.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/secstore/util.c

Shared secstore utility functions. `emalloc`, `erealloc`, and `estrdup` are fatal-on-failure helpers. `getpassm` reads hidden console input in raw mode while keeping console fds open for ssh-environment reliability.

`validatefile` rejects nil/empty names, `..`, overly long names, control characters, and `/`, logging illegal names to the secstore log.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/secstore/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/secureidcheck.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/secureidcheck.c

Implements SecurID validation through RADIUS (RFC 2138). It builds Access-Request packets, hides the user password/token with MD5(shared secret + authenticator), sends UDP requests to configured `lra-radius` hosts, validates response authenticators, and interprets accept/reject/challenge codes.

Configuration comes from ndb: RADIUS shared secret, optional uid-to-rid mapping, and radius server IPs. It adds NAS-IP-Address based on local IPv4 interface and logs outcomes to `auth`.

Limitations are documented in the file header: UDP loss and one-use token semantics make retry and timeout choices inherently flawed.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/secureidcheck.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/status -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/status

Rc script that reports Plan 9 and network key status for a user. It checks `/mnt/keys/<user>` and `/mnt/netkeys/<user>`, reads `status` and `expire`, formats expiration with `date`, and prints metadata from `/adm/keys.who` or `/adm/netkeys.who`.

For network keys it also runs `auth/printnetkey`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/status -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/uniq.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/uniq.c

Deduplicates a pipe-delimited account metadata file by username. It keeps the last line seen for each name, sorts records by name, and rewrites the file only if duplicates caused changes.

Used for maintaining `who`-style metadata files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/uniq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/userpasswd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/userpasswd.c

Retrieves username/password credentials from factotum using `auth_getuserpasswd` with `proto=pass` and the supplied format string. It includes a compatibility fallback using nil key function for older factotum behavior.

Prints user and password on separate lines.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/userpasswd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/warning.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/warning.c

Sends expiration warning mail for Plan 9 and/or Securenet key databases. It scans mounted key directories, checks `expire` and `warnings`, sends one warning about two weeks before expiration and another about one week before, then updates the warning counter.

Recipients are extracted from `<...>` addresses in the associated `who` file; if none are found, it mails the user directly and also mails `netkeys`. It forks `/bin/upas/send` in a `none` namespace and can include `/adm/warn.<keysdir>` message text.

Supports `-p`, `-n`, and debug mode.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/warning.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/wrkey.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/wrkey.c

Tiny utility that calls `readnvram(&safe, NVwrite)` to write/update nvram authentication data through the standard prompt path.

Exits fatally if nvram write fails.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/wrkey.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/8prefix.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/8prefix.c

Object-file rewriting tool for Plan 9 8c `.8` files. It pre-resolves and prefixes external/global symbol names so linked objects cannot access them directly; it can optionally leave `main` unchanged with `-m`.

It parses 8.out object records, builds a symbol table keyed by name/version, marks global symbols found in `AGLOBL`, `AINIT`, `ADATA`, and `ATEXT`, rewrites `ANAME`/`ASIGNAME` records with prefixed names, and writes back in place.

This is architecture-specific to 386/8c object format and depends on `/sys/src/cmd/8c/8.out.h`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/8prefix.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/9pcon.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/9pcon.c

Interactive 9P connection exerciser. It connects to a service file, a shell command (`-c`), or a network address (`-n`), then forks: one process watches and prints incoming Fcalls; the other reads command lines and sends T-messages.

Supports manual construction of `Tversion`, `Tauth`, `Tflush`, `Tattach`, `Twalk`, `Topen`, `Tcreate`, `Tread`, `Twrite`, `Tclunk`, `Tremove`, `Tstat`, `Twstat`, plus `nexttag`.

Useful for debugging 9P servers by sending arbitrary protocol messages and observing formatted responses.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/9pcon.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/accupoint.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/accupoint.c

Mouse-event filter for AccuPoint devices. It converts buttons 4 and 5 into simulated button 2 behavior for Plan 9 mouse streams.

Button 4 is treated as press-and-hold button 2 with timeout-based release; button 5 generates a quick button-2 click and suppresses bounce. The program reads and writes standard Plan 9 mouse event records on stdin/stdout and uses alarm notifications for release timing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aux/accupoint.c -->