# Group Research: group_1235_netbsd_src_sources_os_bsd_netbsd_src_lib_librumpuser_rumpuser_pth_c_2d3ccc1cb796

Scope verified against `Docs/research_subset_a.md`. All listed source files were read completely in manifest order.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_pth.c -->
# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_pth.c

## Purpose
Implements the pthread-backed rumpuser threading and synchronization layer used by rump kernels on hosts with POSIX threads.

## Main Interfaces
Provides `rumpuser_thread_create`, `rumpuser_thread_exit`, `rumpuser_thread_join`, mutex APIs, rwlock APIs, condition-variable APIs, `rumpuser_curlwpop`, `rumpuser_curlwp`, and `rumpuser__thrinit`.

## Control Flow And State
Thread creation configures joinable or detached pthread attributes, retries `pthread_create` on `EAGAIN`, and optionally sets thread names via platform-specific `pthread_setname_np` variants. Joinable threads allocate a `pthread_t` cookie that is freed after successful join.

Mutexes wrap `pthread_mutex_t` with error-checking attributes, explicit lock alignment, rump-kernel lock flags, and a tracked `struct lwp *owner` for kernel mutexes. Non-spin mutex acquisition uses `KLOCK_WRAP` around blocking pthread lock calls, while spin-style entry uses the nowrap path.

Rwlocks wrap `pthread_rwlock_t` and track reader count, writer LWP, and downgrade-in-progress state. Writer acquisition loops around `rw_setwriter()` to avoid returning a writer lock while another holder is downgrading. Reader counts use native atomics on NetBSD/Apple/Android and a pthread spinlock elsewhere.

Condition variables track waiter counts and carefully unschedule/reschedule rump kernel CPU context around `pthread_cond_wait`. The spin-mutex CV reschedule path releases the pthread mutex before reacquiring kernel scheduling context to avoid lock-order deadlock.

Current LWP identity is stored in pthread thread-local storage. The active implementation stores the raw `struct lwp *`; an `#if 0` alternate list-backed validator remains as test/debug scaffolding.

## Dependencies
Depends on pthreads, `aligned_alloc`, `nanosleep`, `clock_gettime`, atomic support where available, rumpuser public/internal headers, and rump kernel scheduling hooks such as `rumpkern_sched` and `rumpkern_unsched`.

## Risks And Notes
The rwlock downgrade protocol is subtle: writers may briefly acquire the underlying pthread lock but must not return to the caller while `downgrade` is set. CV waits depend on precise mutex owner bookkeeping around pthread wait unlock/relock behavior. Timed waits use `CLOCK_REALTIME`, so wall-clock changes can affect timeout behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_pth.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_pth_dummy.c -->
# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_pth_dummy.c

## Purpose
Provides a dummy, single-thread-oriented rumpuser threading backend for builds where real threads are unavailable.

## Main Interfaces
Exports the same rumpuser thread, mutex, rwlock, condition-variable, and current-LWP APIs as `rumpuser_pth.c`, but with simplified in-memory counters and no real blocking synchronization.

## Control Flow And State
`rumpuser_thread_create` and `rumpuser_thread_exit` print an error and abort, making real thread use unsupported. `rumpuser_thread_join` is a no-op success path.

Mutexes are heap-allocated structs with a recursion-like integer count and owner pointer. Entry increments the count and stores the global `curlwp`; exit asserts the count is positive and clears ownership at zero.

Rwlocks use one integer: positive means writer, negative means reader count. Writer entry asserts exclusive ownership, reader entry asserts no writer, downgrade changes `1` to `-1`, and tryupgrade succeeds only when the value is exactly `-1`.

Condition variables do not actually wait or wake. Timed wait just calls `nanosleep` for the requested relative interval and returns success. Waiter reporting always returns zero.

Current LWP identity is one global `struct lwp *curlwp`, set and cleared by `rumpuser_curlwpop`.

## Dependencies
Uses libc allocation, assertions, `nanosleep`, and rumpuser headers. It does not depend on pthreads.

## Risks And Notes
This backend is not thread-safe and intentionally aborts on thread creation. It is useful only for configurations that never require concurrent host threads. CV wait semantics are placeholders and cannot model wakeup races or scheduling behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_pth_dummy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_random.c -->
# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_random.c

## Purpose
Provides rumpuser random-byte acquisition for rump kernel consumers.

## Main Interfaces
Exports `rumpuser__random_init()` and `rumpuser_getrandom()`.

## Control Flow And State
When `HAVE_ARC4RANDOM_BUF` is available, initialization is a no-op and `rumpuser_getrandom` fills the buffer with `arc4random_buf`. Otherwise initialization opens `/dev/urandom` read-only into a static file descriptor and `rumpuser_getrandom` reads from it.

Each call caps output to `random_maxread`, currently 32 bytes, and returns the number of bytes actually provided through `retp`. The `flags` argument is accepted but ignored.

## Dependencies
Uses `arc4random_buf` when available, or host `open`/`read` on `/dev/urandom`. Uses rumpuser error-return conventions through `ET`.

## Risks And Notes
The non-arc4random path requires successful initialization before use and keeps a process-global descriptor. Short reads are reported via `retp` without an internal retry loop. The fixed 32-byte cap means callers must loop for larger requests.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_random.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_sigtrans.c -->
# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_sigtrans.c

## Purpose
Translates rump kernel signal numbers to host signal constants.

## Main Interfaces
Exports `rumpuser__sig_rump2host(int)`.

## Control Flow And State
The function is a switch over NetBSD-style signal numbers 0 through 32. Each case is guarded by the corresponding host `SIG*` macro. Signal 20 maps to `SIGCHLD` or `SIGCLD` depending on availability. Unknown or unavailable signals return `-1`.

There is no mutable state.

## Dependencies
Depends on host `<signal.h>` signal macro definitions.

## Risks And Notes
The mapping assumes NetBSD numeric signal assignments on the rump side. Host platforms with missing or differently named signals may return `-1` for otherwise valid rump signals.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_sigtrans.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_sp.c -->
# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_sp.c

## Purpose
Implements the server side of rump sysproxy: a socket RPC bridge that lets a remote client issue rump-kernel syscalls and memory-copy requests through a host socket connection.

## Main Interfaces
Exports `rumpuser_sp_init`, `rumpuser_sp_fini`, `rumpuser_sp_copyin`, `rumpuser_sp_copyinstr`, `rumpuser_sp_copyout`, `rumpuser_sp_copyoutstr`, `rumpuser_sp_anonmmap`, and `rumpuser_sp_raise`.

## Control Flow And State
The file includes `sp_common.c` directly for shared protocol framing and socket helpers. Global server state includes a pollfd array, parallel `spclient` array, disconnect counter, shutdown flag, worker limits, and protocol banner.

`rumpuser_sp_init` parses a `tcp://` or `unix://` URL, creates/binds/listens on a socket, builds a `RUMPSP-0.4-...` banner, and launches a detached `spserver` thread. The server initializes client slots, polls the listener and clients, accepts connections, sends the banner, and reads framed requests.

Client handshakes support new guest creation, fork attachment via one-time prefork auth tokens, and exec handshakes. Prefork uses random 128-bit auth tokens and a global list protected by `pfmtx`.

Syscall and exec requests are bounced to detached worker threads. Workers call rump hypervisor hooks to create LWPs, execute syscalls, release LWPs, or drain/notify exec. Worker pool state is controlled by `sbamtx`, `sbacv`, `nworker`, `idleworker`, and `nwork`.

Copyin/copyinstr and anonymous mmap are synchronous request/response operations sent from the server back to the client. Copyout and signal raise are asynchronous outbound requests. These paths unschedule the rump kernel before blocking on socket I/O and reschedule afterward.

Disconnect handling marks clients dying, wakes waiters, releases main LWPs unless exec owns them, resets per-connection fields, closes fds, and notifies the main loop through `signaldisco`.

## Dependencies
Depends on pthreads, sockets, `poll`, fcntl nonblocking mode, rump hypervisor callbacks, `rumpuser_getrandom`, and shared protocol definitions from `sp_common.c`.

## Risks And Notes
The protocol is explicitly ABI-dependent; client and server must agree on C layouts and pointer-sized fields. Blocking sends are noted as problematic for the main thread. The prefork and exec paths rely on careful refcount and LWP ownership ordering to avoid using released process contexts. URL parsing and socket cleanup are delegated to the shared common file.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_sp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpuser/sp_common.c -->
# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/sp_common.c

## Purpose
Defines common rump sysproxy protocol structures, framing, send/response-wait helpers, and URL parsing used by sysproxy client/server code via direct `#include`.

## Main Interfaces
Provides static helpers and types for `rsp_hdr`, copy data, syscall responses, fork handshakes, `respwait`, `spclient`, `readframe`, `dosend`, wait-list management, send locking, error mapping, and `parseurl`.

## Control Flow And State
Protocol classes are request, response, and error. Request types include handshake, syscall, copyin/copyout, anonymous mmap, prefork, and raise. Handshake types distinguish guest, auth, fork, and exec.

`dosend` writes an iovec frame with `sendmsg`, handles partial sends by advancing the iovec, polls for output readiness after partial progress, maps `EPIPE`/zero sends to `ENOTCONN`, and uses `MSG_NOSIGNAL`.

Response waits are stored in a per-client TAILQ keyed by request number. `putwait` allocates a request number, inserts a waiter, and reserves the send path; `kickwaiter` finds a matching response frame, transfers the frame body to the waiter, maps protocol errors to errno, and signals the waiter.

`readframe` incrementally reads the fixed header and variable body from a nonblocking socket. Body buffers are allocated with one extra zero byte so string-like bodies are always NUL-terminated.

URL support includes IPv4 TCP and Unix-domain sockets. `tcp_parse` accepts `host:port`, `*`, or `0` for wildcard server bind; client-side wildcard is rejected. `unix_parse` stores absolute cleanup paths for relative socket names when possible. `tcp6` is present but returns `EOPNOTSUPP`.

## Dependencies
Uses sockets, Unix-domain sockets, poll/read/sendmsg, pthread condition variables, queue macros, inet parsing, and optional HOSTOPS overrides for host I/O functions.

## Risks And Notes
Frames trust `rsp_len` enough to allocate body memory after checking only for `>= HDRSZ`; malformed large lengths can force allocation failure/disconnect. Wire data contains host pointers and native scalar layouts, so it is not a portable network protocol. Send-lock state is per client and must be released on every wait/send failure path.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpuser/sp_common.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpvfs/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/librumpvfs/Makefile

## Purpose
Builds the `librumpvfs` rump VFS library by delegating to the rump kernel makefile fragment.

## Key Elements
Sets `NOFULLRELRO=yes`, defines `RUMPTOP=${.CURDIR}/../../sys/rump`, adds a dependency library on `librump`, sets `WARNS=3`, and includes `${RUMPTOP}/librump/rumpvfs/Makefile.rumpvfs`.

## Dependencies
Depends on NetBSD make infrastructure, `bsd.lib.mk` indirectly through the included rump makefile, and the source tree under `sys/rump`.

## Risks And Notes
The file is intentionally thin; most build behavior is inherited. The warning level is capped because kernel code is not ready for stricter sign-compare warnings.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/librumpvfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libskey/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libskey/Makefile

## Purpose
Builds the S/Key one-time-password library.

## Key Elements
Defines `LIB=skey`, source files `skeylogin.c skeysubr.c put.c`, installs `skey.h` to `/usr/include`, enables fortified authentication build defaults via `USE_FORT?=yes`, and installs `skey.3` with MLINK aliases for the public APIs.

## Dependencies
Uses NetBSD `bsd.lib.mk` and the local S/Key implementation files.

## Risks And Notes
The public API surface is driven by the installed header and manpage aliases. Hash and database behavior lives in the C sources, not the makefile.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libskey/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libskey/put.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libskey/put.c

## Purpose
Implements S/Key binary-to-English OTP encoding and English-to-binary decoding using the standard 2048-word dictionary.

## Main Interfaces
Exports `btoe`, `etob`, and `put8`.

## Control Flow And State
The file contains `Wp[2048][4]`, a sorted dictionary of one- to four-character uppercase words. Each word represents an 11-bit value.

`btoe` copies an 8-byte key into a 9-byte working buffer, computes two parity bits by summing 2-bit chunks across the 64-bit key, stores parity in the high bits of the ninth byte, extracts six 11-bit values, and emits six dictionary words separated by spaces.

`etob` copies input to a bounded local buffer, tokenizes exactly six space-separated words, validates word length, normalizes lower-case and common digit substitutions (`1` to `L`, `0` to `O`, `5` to `S`), searches the appropriate dictionary range, inserts each 11-bit value into a bit buffer, checks parity, and copies the first 8 bytes to the caller.

`put8` formats an 8-byte key as four groups of uppercase hex byte pairs.

Internal helpers perform dictionary binary search, bit insertion/extraction across byte boundaries, and word standardization.

## Dependencies
Uses C string/ctype/assert APIs and public constants from `skey.h`.

## Risks And Notes
The encoder assumes the output buffer is large enough for six words and spaces. `etob` truncates/copies input into 36 bytes, matching expected OTP word form but rejecting longer malformed input. The dictionary order is part of the binary-search contract and must not be casually reordered.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libskey/put.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libskey/skey.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libskey/skey.h

## Purpose
Defines the public S/Key API, state structures, and size limits.

## Main Interfaces
Defines `struct skey` for server-side keyfile scanning and `struct mc` for client-side challenge scanning. Declares APIs for challenge lookup, verification, key generation/format conversion, password reading, authentication, algorithm selection, key iteration, and key disabling.

## Key Constants
Defines maximum sequence number, password length bounds, seed length, challenge length, hash-name length, binary key size, and the bogus-challenge random-file path.

## Dependencies
Includes `<stdio.h>` for `FILE *`.

## Risks And Notes
`struct skey` stores pointers into its internal `buf`, so callers must not expect `logname`, `seed`, or `val` to remain valid after another scan overwrites the buffer. Several APIs use static or caller-provided buffers rather than allocated ownership.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libskey/skey.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libskey/skeylogin.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libskey/skeylogin.c

## Purpose
Implements S/Key challenge lookup, response verification, authentication prompting, keyfile iteration, and key disabling.

## Main Interfaces
Exports `getskeyprompt`, `skeychallenge`, `skeylookup`, `skeygetnext`, `skeyverify`, `skey_haskey`, `skey_keyinfo`, `skey_passcheck`, `skey_authenticate`, and `skeyzero`.

## Control Flow And State
`openSkey` opens `_PATH_SKEYKEYS` read/write if present and forces mode `0600`. Lookup scans records, skipping comments, parsing optional hash algorithm, sequence, seed, and value, then seeks back to the matching record start. If no algorithm is present, MD4 is assumed.

Challenge helpers format `otp-<algorithm> <sequence-1> <seed>` using bounded hash and seed widths. `getskeyprompt` also strips high bits from the username before lookup.

`skeyverify` converts a response from English words or hex to an 8-byte key, applies one hash iteration, locks the keyfile with `flock`, rereads the original record to avoid stale challenge reuse, compares against the stored key, then rewrites the same record with the new key and decremented sequence number. MD4 records omit the algorithm name to preserve legacy fixed record length; other algorithms include it.

`skey_authenticate` prints a challenge, reads a response, verifies it, warns when fewer than five logins remain, and returns success/failure. Optional fake-challenge code can synthesize prompts for nonexistent users when compiled in. `skeyzero` comments out the current keyfile record by writing `#` at its start.

## Dependencies
Uses key conversion/hash helpers from `skeysubr.c` and `put.c`, `_PATH_SKEYKEYS`, `flock`, stdio file positioning, local time formatting, optional SHA1 fake-challenge support, and terminal input helpers.

## Risks And Notes
Correctness depends on rewriting records without changing their effective fixed-width layout. The keyfile lock is acquired only during verification/update, so lookup data must be reread after locking. Some error paths close `keyfile`, but lock-failure returns without closing it. The code uses legacy MD4 by default unless records specify another supported algorithm.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libskey/skeylogin.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libskey/skeysubr.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libskey/skeysubr.c

## Purpose
Implements S/Key hash/key derivation, one-way key iteration, hex conversion, terminal password reading, and small string utilities.

## Main Interfaces
Exports `keycrunch`, `f`, `rip`, `readpass`, `readskey`, `atob8`, `btoa8`, `htoi`, `skipspace`, `backspace`, `sevenbit`, `skey_set_algorithm`, and `skey_get_algorithm`.

## Control Flow And State
A global `skey_hash_type` indexes an algorithm table. Supported active algorithms are MD4, MD5, and SHA1; RMD160 code is present but disabled.

`keycrunch` lowercases the seed, concatenates seed and password, masks input to seven bits, hashes it, and folds the digest to the 64-bit S/Key binary key. MD4/MD5 fold 128 bits by XORing digest halves. SHA1 folds 160 bits and manually emits little-endian bytes as required by RFC 2289.

`f` applies one in-place one-way hash iteration to an 8-byte key using the selected algorithm.

Input helpers disable terminal echo for secret password reads, restore echo on normal completion or SIGINT, strip trailing CR/LF, and seven-bit-clean input. OTP reads leave echo enabled.

Conversion helpers parse or emit 16 hex nibbles with optional whitespace on input. `backspace` removes backspaced characters from a string.

## Dependencies
Uses NetBSD MD4/MD5/SHA1/RMD160 headers, termios, signals, ctype, and public constants from `skey.h`.

## Risks And Notes
The selected hash algorithm is global process state, so concurrent users or nested calls can interfere. The terminal echo helper stores static termios state and is not reentrant. SHA1 uses internal `SHA1_CTX.state` after `SHA1Final(NULL, &sha)`, binding behavior to this SHA1 implementation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libskey/skeysubr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libtelnet/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libtelnet/Makefile

## Purpose
Builds NetBSD's private telnet protocol support library.

## Key Elements
Defines `LIBISPRIVATE=yes`, `LIB=telnet`, base sources `auth.c encrypt.c genget.c getent.c misc.c`, enables `HAS_CGETENT`, includes the source directory, and builds DES encryption support via `enc_des.c` with `ENCRYPTION`, `AUTHENTICATION`, and `DES_ENCRYPTION`.

Kerberos support adds `kerberos5.c` when `USE_KERBEROS != no`. PAM support adds SRA sources `sra.c pk.c` when `USE_PAM != no`. Selected files suppress pointer-sign warnings.

## Dependencies
Uses NetBSD make infrastructure, telnet headers, DES, optional Kerberos, and optional PAM/OpenSSL BIGNUM support.

## Risks And Notes
Authentication and encryption are compiled in by default here. SRA is tied to PAM availability in this build logic.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libtelnet/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libtelnet/auth-proto.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libtelnet/auth-proto.h

## Purpose
Declares libtelnet authentication dispatcher and method-specific function prototypes.

## Main Interfaces
When `AUTHENTICATION` is enabled, declares authenticator lookup, initialization, command/status toggles, negotiation send/receive handlers, completion/wait helpers, debug/printsub helpers, and optional Kerberos V5 and SRA method entry points.

## Dependencies
Depends on `Authenticator` being defined by `auth.h` before inclusion and on telnet authentication compile-time feature macros such as `KRB5` and `SRA`.

## Risks And Notes
This header is feature-macro driven. Consumers only see method declarations for authentication backends compiled into the library.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libtelnet/auth-proto.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libtelnet/auth.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libtelnet/auth.c

## Purpose
Implements Telnet Authentication option negotiation and dispatch across compiled authenticator methods.

## Main Interfaces
Exports authenticator lookup, init, enable/disable/status/debug commands, authentication request/send/is/reply/name handling, completion state, wait logic, and suboption formatting.

## Control Flow And State
The `authenticators[]` table lists supported methods in priority order: Kerberos V5 mutual/one-way when compiled, then SRA when compiled. Global state tracks local name, server/client role, supported and disabled type masks, current authentication attempt, final authenticated method, and user validity level.

Server-side `auth_request` sends `TELQUAL_SEND` with all locally supported and not-disabled method/type pairs. Client-side `auth_send` stores the remote offered list, scans it in order, finds a matching local authenticator, and calls its `send` function. If none work, it sends `AUTHTYPE_NULL` and marks authentication rejected.

`auth_is` handles server-side `TELQUAL_IS` payloads by dispatching to a method `is` handler. `auth_reply` handles client-side replies. `auth_name` records the login name for encryption/auth modules. `auth_sendname` emits a TELQUAL_NAME suboption with IAC escaping.

`auth_wait` spins the telnet application until authentication completes or a 30-second alarm fires, then asks the selected authenticator to finalize status if available.

## Dependencies
Uses `<arpa/telnet.h>` auth constants, `telnet_net_write`, `telnet_spin`, `printsub`, method implementations, and `auth_encrypt_user`.

## Risks And Notes
Global state makes the dispatcher connection-oriented rather than instance-safe. `auth_send` has delicate pointer logic for saved offer lists and retry. The wait path uses process `SIGALRM`, which can interfere with applications using alarms.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libtelnet/auth.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libtelnet/auth.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libtelnet/auth.h

## Purpose
Defines the telnet authentication method interface and result levels.

## Main Interfaces
Defines authentication status constants from reject through valid. Defines `Authenticator`, a method table with type, way, init/send/is/reply/status/printsub function pointers. Includes `auth-proto.h`.

## Other Definitions
Defines credential forwarding option flags and declares `auth_debug_mode`.

## Dependencies
Depends on telnet authentication constants from the including context and method implementations matching the function pointer signatures.

## Risks And Notes
The `Authenticator` structure is the central ABI between the generic auth dispatcher and Kerberos/SRA backends.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libtelnet/auth.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libtelnet/enc-proto.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libtelnet/enc-proto.h

## Purpose
Declares libtelnet encryption negotiation APIs and DES mode backend hooks.

## Main Interfaces
When `ENCRYPTION` is enabled, declares encryption lookup, init, command handlers, support/is/reply/start/end/keyid negotiation functions, auto mode toggles, status/printsub helpers, and imported application hooks.

Also declares DES CFB64 and OFB64 backend functions for encryption, decryption, initialization, negotiation, session-key setup, key-id handling, and suboption printing.

## Dependencies
Depends on `Encryptions` and `Session_Key` from `encrypt.h` and compile-time `ENCRYPTION`.

## Risks And Notes
This is a macro-gated declaration surface. DES-specific prototypes are always present under `ENCRYPTION` in this header, while actual definitions require DES/authentication compile flags.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libtelnet/enc-proto.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libtelnet/enc_des.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libtelnet/enc_des.c

## Purpose
Implements Telnet ENCRYPT DES_CFB64 and DES_OFB64 methods.

## Main Interfaces
Exports `cfb64_*` and `ofb64_*` init/start/is/reply/session/keyid/printsub/encrypt/decrypt functions plus shared `fb64_*` helpers.

## Control Flow And State
Two global `struct fb` instances hold DES session key, key schedule, negotiation state, key-id state, temporary IV/feed data, and per-direction stream state.

Start negotiation for encryption sends a generated DES-encrypted IV as an `ENCRYPT_IS <type> FB64_IV` suboption once a valid session key exists. Decryption-side `fb64_is` accepts the IV, initializes the decrypt stream, and replies `FB64_IV_OK` or `FB64_IV_BAD`. Encryption-side `fb64_reply` initializes its stream after `IV_OK` and sends the default zero key id.

Session-key setup accepts only `SK_DES`, installs the DES key into both directions, initializes the DES random generator once, builds the key schedule, and restarts negotiation if start was waiting for a key.

Key-id handling accepts only a one-byte zero key id. CFB64 stores ciphertext feedback; OFB64 advances the DES output feedback stream independently of ciphertext. Decrypt functions support a special `data == -1` one-byte backup convention.

## Dependencies
Depends on telnet ENCRYPT constants, DES APIs, `encrypt_send_keyid`, `telnet_net_write`, `printsub`, and `printd`.

## Risks And Notes
DES and 64-bit feedback modes are legacy cryptography. Negotiation state is global and not per-session-safe. `ofb64_init` appears to assign `str_flagshift` through the CFB array rather than the OFB array; the field is not otherwise used in this file, but the assignment is suspicious.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libtelnet/enc_des.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libtelnet/encrypt.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libtelnet/encrypt.c

## Purpose
Implements Telnet ENCRYPT option negotiation, command handling, key-id exchange, and activation of selected encryption/decryption methods.

## Main Interfaces
Exports global function pointers `encrypt_output` and `decrypt_input`, encryption command handlers, support/is/reply/start/end/keyid handlers, session-key distribution, auto mode controls, wait logic, and printsub helpers.

## Control Flow And State
The `encryptions[]` table currently contains DES_CFB64 and DES_OFB64 when DES encryption is compiled. Global masks track local support, disabled support, and remote support for each direction. Additional globals track current encrypt/decrypt modes, verbosity/debug flags, autoencrypt/autodecrypt, session-key availability, role, and display name.

`encrypt_init` resets negotiation state, builds an ENCRYPT SUPPORT suboption listing enabled decryption types, and initializes each backend. Command functions enable/disable/type/start/stop input and output directions, using `genget` for type lookup.

`encrypt_support` records remote decrypt capabilities and selects a usable output encryption type. `encrypt_is` and `encrypt_reply` dispatch initial method negotiation to backend hooks and optionally auto-start. `encrypt_start` installs the active decrypt input callback after receiving ENCRYPT START.

Key-id handling keeps separate direction records, calls backend key-id validators, and sends escaped key-id suboptions. `encrypt_start_output` emits ENCRYPT START, calls `net_encrypt` to flush/ring-encrypt correctly, then installs the output encrypt callback. `encrypt_send_end` clears output encryption after emitting ENCRYPT END.

## Dependencies
Uses telnet ENCRYPT constants, DES backends, generic command lookup from `misc.h`, and application-provided `telnet_net_write`, `net_encrypt`, `telnet_spin`, and `printsub`.

## Risks And Notes
State is global, not per connection. Auto-start behavior depends on session key arrival and remote support masks. Output mode switches are sensitive to telnet ring ordering: the code intentionally encrypts pending output in the old mode before installing the new callback.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libtelnet/encrypt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libtelnet/encrypt.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libtelnet/encrypt.h

## Purpose
Defines the telnet encryption method interface and shared encryption types.

## Main Interfaces
When `ENCRYPTION` is enabled, defines direction constants, DES block/schedule aliases, `VALIDKEY`, `SAMEKEY`, `Session_Key`, and `Encryptions`, the backend method table for output/input/init/start/is/reply/session/keyid/printsub.

Includes `enc-proto.h` and declares global active callbacks `decrypt_input` and `encrypt_output`.

## Dependencies
Depends on DES type names from `<des.h>` or equivalent include order, telnet encryption constants, and compile-time `ENCRYPTION`.

## Risks And Notes
The encryption ABI is callback-table based. Session keys are raw pointer/length pairs and ownership is not encoded in the type.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libtelnet/encrypt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libtelnet/forward.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libtelnet/forward.c

## Purpose
Provides Kerberos credential forwarding storage support when Kerberos is compiled.

## Main Interfaces
Defines `rd_and_store_for_creds` under `KERBEROS` or `KRB5`.

## Control Flow And State
The function decodes forwarded credentials with `krb5_rd_cred`, creates a FILE credential cache path under `/tmp/krb5cc_p<pid>`, sets `KRB5_ENV_CCNAME`, resolves and initializes the cache for the ticket client, and stores the first forwarded credential.

## Dependencies
Depends on Kerberos 5 internals/APIs, process id, environment variables, and ticket/auth-context objects.

## Risks And Notes
The credential cache path is predictable and process-id based. The file is conditionally compiled and is separate from the main `kerberos5.c` forwarding implementation used elsewhere in this group.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libtelnet/forward.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libtelnet/genget.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libtelnet/genget.c

## Purpose
Implements generic case-insensitive prefix lookup for command/type tables.

## Main Interfaces
Exports `isprefix`, `genget`, and `Ambiguous`.

## Control Flow And State
`isprefix` returns zero for no match, negative length for exact match, and positive prefix length for partial match. `genget` walks a table where the first field is a name pointer and entries are separated by caller-provided struct length. It returns exact match immediately, a unique prefix match if found, an internal ambiguous sentinel for multiple prefix matches, or null for no match. `Ambiguous` checks for that sentinel.

## Dependencies
Uses ctype and declarations from `misc.h`.

## Risks And Notes
The table layout contract is implicit: the first field must be a `char *` compatible name. The ambiguous sentinel is a static address, not a real table entry.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libtelnet/genget.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libtelnet/getent.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libtelnet/getent.c

## Purpose
Wraps terminal capability lookup for telnet code.

## Main Interfaces
Defines `getent(char *, char *)` and, outside Solaris builds, `getstr(char *, char **)`.

## Control Flow And State
With `HAS_CGETENT`, `getent` queries `/etc/gettytab` using `cgetent` and stores the returned entry in a static `area`. `getstr` retrieves string capabilities from that entry using `cgetstr`. Without `HAS_CGETENT`, both functions return failure/null.

## Dependencies
Uses libc capability database APIs when enabled and application prototypes from `misc-proto.h`.

## Risks And Notes
The static `area` is shared process state. The first `getent` argument is unused in the cgetent implementation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libtelnet/getent.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libtelnet/kerberos5.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libtelnet/kerberos5.c

## Purpose
Implements Telnet Authentication Kerberos V5, including optional mutual authentication, DES session-key export to telnet encryption, and credential forwarding.

## Main Interfaces
Exports `kerberos5_init`, `kerberos5_send`, `kerberos5_is`, `kerberos5_reply`, `kerberos5_status`, `kerberos5_printsub`, and `kerberos5_forward` when `KRB5` is enabled.

## Control Flow And State
Global state includes Kerberos context, auth context, AP-REQ data, accepted ticket, forwarding flags, and a telnet suboption buffer. `Data` emits Kerberos auth suboptions with IAC escaping.

Client send obtains the default credential cache, initializes an auth context bound to the telnet socket, requests a host service AP-REQ for `RemoteHostName` with a checksum over auth type/way, sends TELQUAL_NAME, then sends `KRB_AUTH`.

Server `kerberos5_is` receives `KRB_AUTH`, initializes an auth context, builds the host service principal, verifies the AP-REQ and checksum, obtains the remote subkey or session key, optionally sends AP-REP for mutual authentication, checks `krb5_kuserok` for the requested user, sends accept/reject, and passes DES session keys to the encryption layer when compatible.

Forwarded credentials are accepted via `KRB_FORWARD`, written into a FILE credential cache for the target user under `/tmp/krb5cc_<uid>`, and acknowledged or rejected. Client-side `kerberos5_forward` builds TGT forwarding credentials and sends them after authentication if forwarding flags request it.

Reply handling accepts/rejects client auth, verifies mutual AP-REP before accepting mutual mode, installs the local DES session key for encryption, and processes forwarding acknowledgments.

## Dependencies
Depends on Kerberos 5 APIs, telnet auth/encrypt/misc layers, passwd database, `/tmp` credential caches, `krb5_kuserok`, and external telnet socket descriptor `net`.

## Risks And Notes
The code is built around legacy DES telnet encryption interop and exports DES session keys only for DES key types. Credential-cache paths are predictable and require correct ownership changes. Global Kerberos/auth state is not per-connection-safe.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libtelnet/kerberos5.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libtelnet/key-proto.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libtelnet/key-proto.h

## Purpose
Declares key-stream helper functions historically used by telnet DES encryption support.

## Main Interfaces
Declares `key_file_exists`, `key_lookup`, `key_stream_init`, and `key_stream`.

## Dependencies
Depends on `Block` from `encrypt.h`.

## Risks And Notes
Only declarations are present in this file. The functions are not implemented by the files in this grouped batch, so consumers depend on another object or conditional build path.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libtelnet/key-proto.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libtelnet/misc-proto.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libtelnet/misc-proto.h

## Purpose
Declares shared libtelnet glue APIs and application callbacks.

## Main Interfaces
Declares libtelnet helpers `auth_encrypt_init`, `auth_encrypt_user`, `auth_encrypt_connect`, and `printd`.

Declares application-provided callbacks: `telnet_net_write`, `net_encrypt`, `telnet_spin`, `telnet_getenv`, and `telnet_gets`.

## Dependencies
Feature users include authentication, encryption, Kerberos, SRA, and miscellaneous code.

## Risks And Notes
The library relies on the embedding telnet client/server to provide network write, event spin, environment, and input functions. This header is the boundary between libtelnet and the application.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libtelnet/misc-proto.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libtelnet/misc.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libtelnet/misc.c

## Purpose
Implements small shared state and glue between libtelnet authentication/encryption modules and the embedding application.

## Main Interfaces
Exports `auth_encrypt_init`, `auth_encrypt_user`, `auth_encrypt_connect`, and `printd`.

## Control Flow And State
Stores global `RemoteHostName`, `LocalHostName`, `UserNameRequested`, and `ConnectedCount`. Initialization sets local/remote names, initializes authentication and encryption subsystems when compiled, and clears any previous requested username. `auth_encrypt_user` replaces the requested username with a duplicated string. `auth_encrypt_connect` is currently empty. `printd` prints up to 16 bytes as hex for debug output.

## Dependencies
Depends on `auth.h`, `encrypt.h`, `misc.h`, and libc allocation/printing.

## Risks And Notes
Username and host state are global and single-connection oriented. `auth_encrypt_user` does not report allocation failure; a failed `strdup` leaves `UserNameRequested` null.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libtelnet/misc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libtelnet/misc.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libtelnet/misc.h

## Purpose
Declares shared libtelnet global state and generic lookup helpers.

## Main Interfaces
Declares external globals for requested username, local/remote host names, connected count, and reserved-port flag. Declares `isprefix`, `genget`, and `Ambiguous`, then includes `misc-proto.h`.

## Dependencies
Uses `__BEGIN_DECLS`/`__END_DECLS` from system C definitions and the app/lib glue prototypes from `misc-proto.h`.

## Risks And Notes
This header exposes mutable global connection state as extern variables, reinforcing the library’s single-session design.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libtelnet/misc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libtelnet/pk.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libtelnet/pk.c

## Purpose
Implements SRA public-key helper routines: key generation, shared-key derivation, and DES-CBC hex encoding/decoding.

## Main Interfaces
Exports `genkeys`, `common_key`, `pk_encode`, and `pk_decode`.

## Control Flow And State
`genkeys` creates a random secret exponent from `arc4random`, reduces it modulo a fixed 192-bit modulus, computes public key `PROOT^secret mod modulus`, converts secret/public BIGNUMs to fixed-width hex strings, and zero-pads them via `adjust`.

`common_key` parses local secret, peer public key, and fixed modulus, computes the Diffie-Hellman shared value, extracts a middle 64-bit DES key and upper 128-bit IDEA key, and sets DES odd parity.

`pk_encode` DES-CBC encrypts a NUL-padded string with zero IV, rounds length to an 8-byte boundary, and emits uppercase hex. `pk_decode` parses hex pairs, DES-CBC decrypts with zero IV, and NUL-terminates the output.

## Dependencies
Uses OpenSSL BIGNUM APIs, DES APIs, `arc4random`, and constants/types from `pk.h`.

## Risks And Notes
The fixed 192-bit modulus and DES-CBC wrapping are legacy and weak by modern standards. `pk_encode` and `pk_decode` use 256-byte local buffers and rely on callers passing bounded strings. BIGNUM hex strings returned by `BN_bn2hex` are not freed in `genkeys`, causing small leaks on key generation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libtelnet/pk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libtelnet/pk.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libtelnet/pk.h

## Purpose
Defines SRA public-key constants, DES/IDEA key buffers, and public-key helper prototypes.

## Main Interfaces
Defines `DesData`, `IdeaData`, DES encrypt/decrypt direction constants, fixed hex modulus, key sizes, primitive root, and prototypes for `genkeys`, `common_key`, `pk_encode`, and `pk_decode`.

## Dependencies
Depends on DES key schedule type names.

## Risks And Notes
The cryptographic parameters are fixed and small by modern standards: 192-bit public-key exchange and DES-derived session keys.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libtelnet/pk.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libtelnet/sra.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libtelnet/sra.c

## Purpose
Implements Telnet SRA secure remote authentication using a public-key exchange, DES-protected username/password exchange, and PAM or password-file verification.

## Main Interfaces
Exports `sra_init`, `sra_send`, `sra_is`, `sra_reply`, `sra_status`, and `sra_printsub` when `SRA` and `ENCRYPTION` are enabled.

## Control Flow And State
Global buffers store local public/secret keys, peer public key, plaintext/encrypted username/password, password prompts, DES common key, IDEA key, and SRA validity state.

`sra_init` sets TELQUAL direction by role, allocates fixed-size buffers, resets password state, and generates a public/secret key pair. Client `sra_send` starts negotiation by sending its public key.

Server `sra_is` handles client suboptions. On `SRA_KEY`, it replies with the server public key, stores the client public key, and derives the common key. On `SRA_USER`, it decrypts the username, records it, optionally primes PAM to obtain a password prompt, encrypts the prompt, and sends `SRA_CONTINUE`. On `SRA_PASS`, it decrypts the password, checks it via PAM or fallback password validation, accepts and installs a DES session key on success, or sends another encrypted prompt on failure.

Client `sra_reply` derives the common key after receiving server public key, prompts for username, encrypts and sends it, decrypts password prompts, reads password without echo through `telnet_gets`, sends encrypted password, retries username after failed password, and installs the DES session key on accept.

PAM support uses a custom conversation that supplies already-collected username/password and captures password prompt text. Without PAM, fallback validation checks secure root terminal policy, password database lookup, shell presence, and `crypt`.

## Dependencies
Depends on telnet auth/encrypt/misc layers, `pk.c` helpers, DES session-key integration, PAM or password database/tty security APIs, `telnet_gets`, and global terminal line name.

## Risks And Notes
SRA uses legacy 192-bit DH-like exchange plus DES and should be considered historical. Global buffers make it non-reentrant. The server keeps prompting after failed password attempts without an obvious local retry limit. PAM can rewrite the username to a template user, and the code updates libtelnet state after successful authentication.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libtelnet/sra.c -->