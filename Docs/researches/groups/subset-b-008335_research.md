# subset-b-008335 Research

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/common_test.go -->
# sources/security-integrity/gocryptfs/internal/stupidgcm/common_test.go

Purpose: Regression tests for the OpenSSL-backed AEAD implementations, comparing them with Go reference ciphers and checking tamper, buffer, concurrency, malformed-input, and key-wipe behavior.

Important APIs and types: build tags: cgo && !without_openssl; package `stupidgcm`; functions/tests `testCiphers`, `testEncryptDecrypt`, `testConcurrency`, `testInplaceSeal`, `testInplaceOpen`, `testCorruption`, `testOpenAllZero`, `testWipe`, `randBytes`, `BenchmarkCCall`; key imports `bytes`, `crypto/cipher`, `crypto/rand`, `encoding/hex`, `log`, `sync`, `testing`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. The subsystem deliberately exposes a narrow AEAD contract: fixed key/nonce/tag sizes, panic-on-programmer-error validation, and `ErrAuth` for corrupted ciphertext. Key material is copied into package-owned storage and wipe methods try to zero it, but Go memory copies remain a best-effort limitation.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `bytes`, `crypto/cipher`, `crypto/rand`, `encoding/hex`, `log`, `sync`, `testing`

Risks: panic paths are intentional for programmer errors but must not be reachable from untrusted malformed ciphertext except where tests expect ordinary errors.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/common_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/doc.go -->
# sources/security-integrity/gocryptfs/internal/stupidgcm/doc.go

Purpose: Package documentation for the OpenSSL-backed AEAD compatibility layer used by gocryptfs when OpenSSL crypto is selected.

Important APIs and types: package `stupidgcm`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. The subsystem deliberately exposes a narrow AEAD contract: fixed key/nonce/tag sizes, panic-on-programmer-error validation, and `ErrAuth` for corrupted ciphertext. The OpenSSL path crosses cgo into EVP contexts, making buffer length checks, NULL handling for empty slices, and context cleanup important.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: nearby gocryptfs packages, platform syscalls, OpenSSL/go-fuse, or test helpers as implied by the file path.

Risks: panic paths are intentional for programmer errors but must not be reachable from untrusted malformed ciphertext except where tests expect ordinary errors.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/gcm.go -->
# sources/security-integrity/gocryptfs/internal/stupidgcm/gcm.go

Purpose: OpenSSL-backed AEAD implementation code for AES-GCM, ChaCha20-Poly1305, or XChaCha20-Poly1305.

Important APIs and types: build tags: cgo && !without_openssl; package `stupidgcm`; types `stupidGCM`; functions/tests `NewAES256GCM`; key imports `crypto/cipher`, `log`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. The subsystem deliberately exposes a narrow AEAD contract: fixed key/nonce/tag sizes, panic-on-programmer-error validation, and `ErrAuth` for corrupted ciphertext. The OpenSSL path crosses cgo into EVP contexts, making buffer length checks, NULL handling for empty slices, and context cleanup important.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `crypto/cipher`, `log`

Risks: main risk is drift between this file and the subsystem contracts it supports.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/gcm.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/gcm_test.go -->
# sources/security-integrity/gocryptfs/internal/stupidgcm/gcm_test.go

Purpose: Regression tests for the OpenSSL-backed AEAD implementations, comparing them with Go reference ciphers and checking tamper, buffer, concurrency, malformed-input, and key-wipe behavior.

Important APIs and types: build tags: cgo && !without_openssl; package `stupidgcm`; functions/tests `TestStupidGCM`; key imports `crypto/aes`, `crypto/cipher`, `testing`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. The subsystem deliberately exposes a narrow AEAD contract: fixed key/nonce/tag sizes, panic-on-programmer-error validation, and `ErrAuth` for corrupted ciphertext.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `crypto/aes`, `crypto/cipher`, `testing`

Risks: main risk is drift between this file and the subsystem contracts it supports.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/gcm_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/locking.go -->
# sources/security-integrity/gocryptfs/internal/stupidgcm/locking.go

Purpose: OpenSSL-backed AEAD implementation code for AES-GCM, ChaCha20-Poly1305, or XChaCha20-Poly1305.

Important APIs and types: build tags: cgo && !without_openssl; package `stupidgcm`; functions/tests `init`; key imports `C`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. The subsystem deliberately exposes a narrow AEAD contract: fixed key/nonce/tag sizes, panic-on-programmer-error validation, and `ErrAuth` for corrupted ciphertext.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `C`

Risks: panic paths are intentional for programmer errors but must not be reachable from untrusted malformed ciphertext except where tests expect ordinary errors.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/locking.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/openssl.go -->
# sources/security-integrity/gocryptfs/internal/stupidgcm/openssl.go

Purpose: OpenSSL-backed AEAD implementation code for AES-GCM, ChaCha20-Poly1305, or XChaCha20-Poly1305.

Important APIs and types: build tags: cgo && !without_openssl; package `stupidgcm`; functions/tests `openSSLSeal`, `openSSLOpen`, `slicePointerOrNull`, `noopCFunction`; key imports `fmt`, `log`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. The subsystem deliberately exposes a narrow AEAD contract: fixed key/nonce/tag sizes, panic-on-programmer-error validation, and `ErrAuth` for corrupted ciphertext. The OpenSSL path crosses cgo into EVP contexts, making buffer length checks, NULL handling for empty slices, and context cleanup important. Key material is copied into package-owned storage and wipe methods try to zero it, but Go memory copies remain a best-effort limitation.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `fmt`, `log`

Risks: main risk is drift between this file and the subsystem contracts it supports.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/openssl.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/openssl_aead.c -->
# sources/security-integrity/gocryptfs/internal/stupidgcm/openssl_aead.c

Purpose: C/OpenSSL EVP bridge for authenticated encryption and decryption used behind the Go `cipher.AEAD` wrappers.

Important APIs and types: C functions/declarations `panic`, `openssl_aead_seal`, `openssl_aead_open`, `noop_c_function`. Uses OpenSSL EVP raw buffer ABI.

Control flow: Go cgo wrappers call these C routines with explicit pointers and lengths. The EVP path allocates a context, initializes cipher/key/IV/AAD, processes plaintext or ciphertext, handles the 16-byte tag, and returns length or authentication failure. The subsystem deliberately exposes a narrow AEAD contract: fixed key/nonce/tag sizes, panic-on-programmer-error validation, and `ErrAuth` for corrupted ciphertext. The OpenSSL path crosses cgo into EVP contexts, making buffer length checks, NULL handling for empty slices, and context cleanup important.

State and persistence behavior: No repository persistence. Runtime state is OpenSSL `EVP_CIPHER_CTX` scratch state plus caller-owned buffers; freeing contexts and validating lengths are the key invariants.

Dependencies and integration points: nearby gocryptfs packages, platform syscalls, OpenSSL/go-fuse, or test helpers as implied by the file path.

Risks: panic paths are intentional for programmer errors but must not be reachable from untrusted malformed ciphertext except where tests expect ordinary errors.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/openssl_aead.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/openssl_aead.h -->
# sources/security-integrity/gocryptfs/internal/stupidgcm/openssl_aead.h

Purpose: C/OpenSSL EVP bridge for authenticated encryption and decryption used behind the Go `cipher.AEAD` wrappers.

Important APIs and types: C functions/declarations `openssl_aead_seal`, `openssl_aead_open`, `noop_c_function`. Uses OpenSSL EVP raw buffer ABI.

Control flow: Go cgo wrappers call these C routines with explicit pointers and lengths. The EVP path allocates a context, initializes cipher/key/IV/AAD, processes plaintext or ciphertext, handles the 16-byte tag, and returns length or authentication failure. The subsystem deliberately exposes a narrow AEAD contract: fixed key/nonce/tag sizes, panic-on-programmer-error validation, and `ErrAuth` for corrupted ciphertext. The OpenSSL path crosses cgo into EVP contexts, making buffer length checks, NULL handling for empty slices, and context cleanup important.

State and persistence behavior: No repository persistence. Runtime state is OpenSSL `EVP_CIPHER_CTX` scratch state plus caller-owned buffers; freeing contexts and validating lengths are the key invariants.

Dependencies and integration points: nearby gocryptfs packages, platform syscalls, OpenSSL/go-fuse, or test helpers as implied by the file path.

Risks: main risk is drift between this file and the subsystem contracts it supports.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/openssl_aead.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/prefer.go -->
# sources/security-integrity/gocryptfs/internal/stupidgcm/prefer.go

Purpose: Backend-preference heuristics deciding when OpenSSL crypto should be preferred over Go crypto on this platform.

Important APIs and types: package `stupidgcm`; functions/tests `PreferOpenSSLAES256GCM`, `PreferOpenSSLXchacha20poly1305`, `HasAESGCMHardwareSupport`; key imports `runtime`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. The subsystem deliberately exposes a narrow AEAD contract: fixed key/nonce/tag sizes, panic-on-programmer-error validation, and `ErrAuth` for corrupted ciphertext.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `runtime`

Risks: some checks are timing-sensitive.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/prefer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/without_openssl.go -->
# sources/security-integrity/gocryptfs/internal/stupidgcm/without_openssl.go

Purpose: No-cgo/no-OpenSSL fallback API that prevents accidental OpenSSL backend use in builds compiled without OpenSSL support.

Important APIs and types: build tags: !cgo || without_openssl; package `stupidgcm`; functions/tests `errExit`, `NewAES256GCM`, `NewChacha20poly1305`, `NewXchacha20poly1305`; key imports `fmt`, `os`, `crypto/cipher`, `github.com/rfjakob/gocryptfs/v2/internal/exitcodes`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. The subsystem deliberately exposes a narrow AEAD contract: fixed key/nonce/tag sizes, panic-on-programmer-error validation, and `ErrAuth` for corrupted ciphertext.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `fmt`, `os`, `crypto/cipher`, `github.com/rfjakob/gocryptfs/v2/internal/exitcodes`

Risks: main risk is drift between this file and the subsystem contracts it supports.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/without_openssl.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/xchacha.go -->
# sources/security-integrity/gocryptfs/internal/stupidgcm/xchacha.go

Purpose: OpenSSL-backed AEAD implementation code for AES-GCM, ChaCha20-Poly1305, or XChaCha20-Poly1305.

Important APIs and types: build tags: cgo && !without_openssl; package `stupidgcm`; types `stupidXchacha20poly1305`; functions/tests `NewXchacha20poly1305`, `NonceSize`, `Overhead`, `Seal`, `Open`, `Wipe`; key imports `crypto/cipher`, `errors`, `log`, `golang.org/x/crypto/chacha20`, `golang.org/x/crypto/chacha20poly1305`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. The subsystem deliberately exposes a narrow AEAD contract: fixed key/nonce/tag sizes, panic-on-programmer-error validation, and `ErrAuth` for corrupted ciphertext. Key material is copied into package-owned storage and wipe methods try to zero it, but Go memory copies remain a best-effort limitation.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `crypto/cipher`, `errors`, `log`, `golang.org/x/crypto/chacha20`, `golang.org/x/crypto/chacha20poly1305`

Risks: main risk is drift between this file and the subsystem contracts it supports.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/xchacha.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/xchacha_test.go -->
# sources/security-integrity/gocryptfs/internal/stupidgcm/xchacha_test.go

Purpose: Regression tests for the OpenSSL-backed AEAD implementations, comparing them with Go reference ciphers and checking tamper, buffer, concurrency, malformed-input, and key-wipe behavior.

Important APIs and types: build tags: cgo && !without_openssl; package `stupidgcm`; functions/tests `TestStupidXchacha20poly1305`; key imports `testing`, `golang.org/x/crypto/chacha20poly1305`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. The subsystem deliberately exposes a narrow AEAD contract: fixed key/nonce/tag sizes, panic-on-programmer-error validation, and `ErrAuth` for corrupted ciphertext.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `testing`, `golang.org/x/crypto/chacha20poly1305`

Risks: main risk is drift between this file and the subsystem contracts it supports.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/xchacha_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/asuser.go -->
# sources/security-integrity/gocryptfs/internal/syscallcompat/asuser.go

Purpose: Portable and security-conscious syscall wrapper code or tests for dirfd-relative operations, no-follow behavior, credentials, xattrs, directory reads, rename flags, EINTR handling, and platform differences.

Important APIs and types: package `syscallcompat`; functions/tests `OpenatUser`, `MknodatUser`, `SymlinkatUser`, `MkdiratUser`; key imports `golang.org/x/sys/unix`, `github.com/hanwen/go-fuse/v2/fuse`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. The subsystem centralizes syscall details so higher-level FUSE code can use safer defaults such as `O_CLOEXEC`, no-follow lookup, EINTR retry, and platform-specific fallbacks. Credential changes are especially sensitive: Linux uses raw per-thread syscalls and locked OS threads to avoid process-wide UID/GID changes.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `golang.org/x/sys/unix`, `github.com/hanwen/go-fuse/v2/fuse`

Risks: platform syscall semantics and kernel/FUSE differences can change behavior.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/asuser.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/asuser_darwin.go -->
# sources/security-integrity/gocryptfs/internal/syscallcompat/asuser_darwin.go

Purpose: Portable and security-conscious syscall wrapper code or tests for dirfd-relative operations, no-follow behavior, credentials, xattrs, directory reads, rename flags, EINTR handling, and platform differences.

Important APIs and types: package `syscallcompat`; functions/tests `asUser`, `pthread_setugid_np`; key imports `runtime`, `syscall`, `github.com/hanwen/go-fuse/v2/fuse`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. The subsystem centralizes syscall details so higher-level FUSE code can use safer defaults such as `O_CLOEXEC`, no-follow lookup, EINTR retry, and platform-specific fallbacks. Credential changes are especially sensitive: Linux uses raw per-thread syscalls and locked OS threads to avoid process-wide UID/GID changes.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `runtime`, `syscall`, `github.com/hanwen/go-fuse/v2/fuse`

Risks: platform syscall semantics and kernel/FUSE differences can change behavior; some checks are timing-sensitive.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/asuser_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/asuser_freebsd.go -->
# sources/security-integrity/gocryptfs/internal/syscallcompat/asuser_freebsd.go

Purpose: Portable and security-conscious syscall wrapper code or tests for dirfd-relative operations, no-follow behavior, credentials, xattrs, directory reads, rename flags, EINTR handling, and platform differences.

Important APIs and types: package `syscallcompat`; functions/tests `asUser`; key imports `golang.org/x/sys/unix`, `github.com/hanwen/go-fuse/v2/fuse`, `github.com/rfjakob/gocryptfs/v2/internal/tlog`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. The subsystem centralizes syscall details so higher-level FUSE code can use safer defaults such as `O_CLOEXEC`, no-follow lookup, EINTR retry, and platform-specific fallbacks. Credential changes are especially sensitive: Linux uses raw per-thread syscalls and locked OS threads to avoid process-wide UID/GID changes.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `golang.org/x/sys/unix`, `github.com/hanwen/go-fuse/v2/fuse`, `github.com/rfjakob/gocryptfs/v2/internal/tlog`

Risks: platform syscall semantics and kernel/FUSE differences can change behavior.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/asuser_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/asuser_linux.go -->
# sources/security-integrity/gocryptfs/internal/syscallcompat/asuser_linux.go

Purpose: Portable and security-conscious syscall wrapper code or tests for dirfd-relative operations, no-follow behavior, credentials, xattrs, directory reads, rename flags, EINTR handling, and platform differences.

Important APIs and types: package `syscallcompat`; functions/tests `asUser`, `getSupplementaryGroups`; key imports `fmt`, `os`, `runtime`, `strconv`, `strings`, `github.com/hanwen/go-fuse/v2/fuse`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. The subsystem centralizes syscall details so higher-level FUSE code can use safer defaults such as `O_CLOEXEC`, no-follow lookup, EINTR retry, and platform-specific fallbacks. Credential changes are especially sensitive: Linux uses raw per-thread syscalls and locked OS threads to avoid process-wide UID/GID changes.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `fmt`, `os`, `runtime`, `strconv`, `strings`, `github.com/hanwen/go-fuse/v2/fuse`

Risks: platform syscall semantics and kernel/FUSE differences can change behavior; some checks are timing-sensitive.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/asuser_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/eintr.go -->
# sources/security-integrity/gocryptfs/internal/syscallcompat/eintr.go

Purpose: Portable and security-conscious syscall wrapper code or tests for dirfd-relative operations, no-follow behavior, credentials, xattrs, directory reads, rename flags, EINTR handling, and platform differences.

Important APIs and types: package `syscallcompat`; functions/tests `retryEINTR`, `retryEINTR2`, `Open`, `Renameat`, `Unlinkat`, `Flush`; key imports `syscall`, `golang.org/x/sys/unix`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. The subsystem centralizes syscall details so higher-level FUSE code can use safer defaults such as `O_CLOEXEC`, no-follow lookup, EINTR retry, and platform-specific fallbacks.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `syscall`, `golang.org/x/sys/unix`

Risks: platform syscall semantics and kernel/FUSE differences can change behavior.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/eintr.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/emulate.go -->
# sources/security-integrity/gocryptfs/internal/syscallcompat/emulate.go

Purpose: Portable and security-conscious syscall wrapper code or tests for dirfd-relative operations, no-follow behavior, credentials, xattrs, directory reads, rename flags, EINTR handling, and platform differences.

Important APIs and types: build tags: !freebsd; package `syscallcompat`; functions/tests `emulateMknodat`; key imports `path/filepath`, `sync`, `syscall`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. The subsystem centralizes syscall details so higher-level FUSE code can use safer defaults such as `O_CLOEXEC`, no-follow lookup, EINTR retry, and platform-specific fallbacks.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `path/filepath`, `sync`, `syscall`

Risks: platform syscall semantics and kernel/FUSE differences can change behavior.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/emulate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/emulate_test.go -->
# sources/security-integrity/gocryptfs/internal/syscallcompat/emulate_test.go

Purpose: Portable and security-conscious syscall wrapper code or tests for dirfd-relative operations, no-follow behavior, credentials, xattrs, directory reads, rename flags, EINTR handling, and platform differences.

Important APIs and types: build tags: !freebsd; package `syscallcompat`; functions/tests `TestEmulateMknodat`; key imports `os`, `testing`, `golang.org/x/sys/unix`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. The subsystem centralizes syscall details so higher-level FUSE code can use safer defaults such as `O_CLOEXEC`, no-follow lookup, EINTR retry, and platform-specific fallbacks.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `os`, `testing`, `golang.org/x/sys/unix`

Risks: platform syscall semantics and kernel/FUSE differences can change behavior.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/emulate_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/getdents_linux.go -->
# sources/security-integrity/gocryptfs/internal/syscallcompat/getdents_linux.go

Purpose: Portable and security-conscious syscall wrapper code or tests for dirfd-relative operations, no-follow behavior, credentials, xattrs, directory reads, rename flags, EINTR handling, and platform differences.

Important APIs and types: build tags: linux; package `syscallcompat`; functions/tests `getdents`, `getdentsName`, `dtUnknownWarn`, `convertDType`; constants `sizeofDirent`, `maxReclen`; key imports `bytes`, `sync`, `syscall`, `unsafe`, `golang.org/x/sys/unix`, `github.com/hanwen/go-fuse/v2/fuse`, `github.com/rfjakob/gocryptfs/v2/internal/tlog`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. The subsystem centralizes syscall details so higher-level FUSE code can use safer defaults such as `O_CLOEXEC`, no-follow lookup, EINTR retry, and platform-specific fallbacks. Directory entry conversion must handle dot entries, deleted-in-flight names, unknown d_type values, and corrupt dirent lengths without crashing the mount.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `bytes`, `sync`, `syscall`, `unsafe`, `golang.org/x/sys/unix`, `github.com/hanwen/go-fuse/v2/fuse`, `github.com/rfjakob/gocryptfs/v2/internal/tlog`

Risks: platform syscall semantics and kernel/FUSE differences can change behavior; some checks are timing-sensitive.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/getdents_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/getdents_other.go -->
# sources/security-integrity/gocryptfs/internal/syscallcompat/getdents_other.go

Purpose: Portable and security-conscious syscall wrapper code or tests for dirfd-relative operations, no-follow behavior, credentials, xattrs, directory reads, rename flags, EINTR handling, and platform differences.

Important APIs and types: package `syscallcompat`; functions/tests `fillDirEntries`, `emulateGetdents`; key imports `os`, `syscall`, `golang.org/x/sys/unix`, `github.com/hanwen/go-fuse/v2/fuse`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. The subsystem centralizes syscall details so higher-level FUSE code can use safer defaults such as `O_CLOEXEC`, no-follow lookup, EINTR retry, and platform-specific fallbacks. Directory entry conversion must handle dot entries, deleted-in-flight names, unknown d_type values, and corrupt dirent lengths without crashing the mount.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `os`, `syscall`, `golang.org/x/sys/unix`, `github.com/hanwen/go-fuse/v2/fuse`

Risks: platform syscall semantics and kernel/FUSE differences can change behavior.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/getdents_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/getdents_test.go -->
# sources/security-integrity/gocryptfs/internal/syscallcompat/getdents_test.go

Purpose: Portable and security-conscious syscall wrapper code or tests for dirfd-relative operations, no-follow behavior, credentials, xattrs, directory reads, rename flags, EINTR handling, and platform differences.

Important APIs and types: build tags: linux; package `syscallcompat`; functions/tests `TestGetdents`, `skipOnGccGo`, `testGetdents`; key imports `os`, `runtime`, `strings`, `syscall`, `testing`, `golang.org/x/sys/unix`, `github.com/hanwen/go-fuse/v2/fuse`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. The subsystem centralizes syscall details so higher-level FUSE code can use safer defaults such as `O_CLOEXEC`, no-follow lookup, EINTR retry, and platform-specific fallbacks. Directory entry conversion must handle dot entries, deleted-in-flight names, unknown d_type values, and corrupt dirent lengths without crashing the mount.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `os`, `runtime`, `strings`, `syscall`, `testing`, `golang.org/x/sys/unix`, `github.com/hanwen/go-fuse/v2/fuse`

Risks: platform syscall semantics and kernel/FUSE differences can change behavior; some checks are timing-sensitive.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/getdents_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/helpers.go -->
# sources/security-integrity/gocryptfs/internal/syscallcompat/helpers.go

Purpose: Portable and security-conscious syscall wrapper code or tests for dirfd-relative operations, no-follow behavior, credentials, xattrs, directory reads, rename flags, EINTR handling, and platform differences.

Important APIs and types: package `syscallcompat`; functions/tests `IsENOSPC`; key imports `os`, `syscall`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. The subsystem centralizes syscall details so higher-level FUSE code can use safer defaults such as `O_CLOEXEC`, no-follow lookup, EINTR retry, and platform-specific fallbacks.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `os`, `syscall`

Risks: platform syscall semantics and kernel/FUSE differences can change behavior.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/helpers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/main_test.go -->
# sources/security-integrity/gocryptfs/internal/syscallcompat/main_test.go

Purpose: Portable and security-conscious syscall wrapper code or tests for dirfd-relative operations, no-follow behavior, credentials, xattrs, directory reads, rename flags, EINTR handling, and platform differences.

Important APIs and types: package `syscallcompat`; functions/tests `TestMain`; key imports `fmt`, `os`, `testing`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. The subsystem centralizes syscall details so higher-level FUSE code can use safer defaults such as `O_CLOEXEC`, no-follow lookup, EINTR retry, and platform-specific fallbacks.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `fmt`, `os`, `testing`

Risks: platform syscall semantics and kernel/FUSE differences can change behavior.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/open_nofollow.go -->
# sources/security-integrity/gocryptfs/internal/syscallcompat/open_nofollow.go

Purpose: Portable and security-conscious syscall wrapper code or tests for dirfd-relative operations, no-follow behavior, credentials, xattrs, directory reads, rename flags, EINTR handling, and platform differences.

Important APIs and types: package `syscallcompat`; functions/tests `OpenDirNofollow`; key imports `path/filepath`, `strings`, `syscall`, `github.com/rfjakob/gocryptfs/v2/internal/tlog`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. The subsystem centralizes syscall details so higher-level FUSE code can use safer defaults such as `O_CLOEXEC`, no-follow lookup, EINTR retry, and platform-specific fallbacks.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `path/filepath`, `strings`, `syscall`, `github.com/rfjakob/gocryptfs/v2/internal/tlog`

Risks: platform syscall semantics and kernel/FUSE differences can change behavior.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/open_nofollow.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/open_nofollow_test.go -->
# sources/security-integrity/gocryptfs/internal/syscallcompat/open_nofollow_test.go

Purpose: Portable and security-conscious syscall wrapper code or tests for dirfd-relative operations, no-follow behavior, credentials, xattrs, directory reads, rename flags, EINTR handling, and platform differences.

Important APIs and types: package `syscallcompat`; functions/tests `TestOpenNofollow`; key imports `os`, `syscall`, `testing`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. The subsystem centralizes syscall details so higher-level FUSE code can use safer defaults such as `O_CLOEXEC`, no-follow lookup, EINTR retry, and platform-specific fallbacks.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `os`, `syscall`, `testing`

Risks: platform syscall semantics and kernel/FUSE differences can change behavior.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/open_nofollow_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/quirks.go -->
# sources/security-integrity/gocryptfs/internal/syscallcompat/quirks.go

Purpose: Portable and security-conscious syscall wrapper code or tests for dirfd-relative operations, no-follow behavior, credentials, xattrs, directory reads, rename flags, EINTR handling, and platform differences.

Important APIs and types: package `syscallcompat`; functions/tests `LogQuirk`; key imports `github.com/rfjakob/gocryptfs/v2/internal/tlog`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. The subsystem centralizes syscall details so higher-level FUSE code can use safer defaults such as `O_CLOEXEC`, no-follow lookup, EINTR retry, and platform-specific fallbacks.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `github.com/rfjakob/gocryptfs/v2/internal/tlog`

Risks: platform syscall semantics and kernel/FUSE differences can change behavior.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/quirks.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/quirks_darwin.go -->
# sources/security-integrity/gocryptfs/internal/syscallcompat/quirks_darwin.go

Purpose: Portable and security-conscious syscall wrapper code or tests for dirfd-relative operations, no-follow behavior, credentials, xattrs, directory reads, rename flags, EINTR handling, and platform differences.

Important APIs and types: package `syscallcompat`; functions/tests `DetectQuirks`; key imports `golang.org/x/sys/unix`, `github.com/rfjakob/gocryptfs/v2/internal/tlog`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. The subsystem centralizes syscall details so higher-level FUSE code can use safer defaults such as `O_CLOEXEC`, no-follow lookup, EINTR retry, and platform-specific fallbacks.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `golang.org/x/sys/unix`, `github.com/rfjakob/gocryptfs/v2/internal/tlog`

Risks: platform syscall semantics and kernel/FUSE differences can change behavior.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/quirks_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/quirks_freebsd.go -->
# sources/security-integrity/gocryptfs/internal/syscallcompat/quirks_freebsd.go

Purpose: Portable and security-conscious syscall wrapper code or tests for dirfd-relative operations, no-follow behavior, credentials, xattrs, directory reads, rename flags, EINTR handling, and platform differences.

Important APIs and types: package `syscallcompat`; functions/tests `DetectQuirks`; key imports `golang.org/x/sys/unix`, `github.com/rfjakob/gocryptfs/v2/internal/tlog`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. The subsystem centralizes syscall details so higher-level FUSE code can use safer defaults such as `O_CLOEXEC`, no-follow lookup, EINTR retry, and platform-specific fallbacks.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `golang.org/x/sys/unix`, `github.com/rfjakob/gocryptfs/v2/internal/tlog`

Risks: platform syscall semantics and kernel/FUSE differences can change behavior.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/quirks_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/quirks_linux.go -->
# sources/security-integrity/gocryptfs/internal/syscallcompat/quirks_linux.go

Purpose: Portable and security-conscious syscall wrapper code or tests for dirfd-relative operations, no-follow behavior, credentials, xattrs, directory reads, rename flags, EINTR handling, and platform differences.

Important APIs and types: package `syscallcompat`; functions/tests `dirHasNoCow`, `DetectQuirks`; constants `FS_NOCOW_FL`; key imports `syscall`, `golang.org/x/sys/unix`, `github.com/rfjakob/gocryptfs/v2/internal/tlog`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. The subsystem centralizes syscall details so higher-level FUSE code can use safer defaults such as `O_CLOEXEC`, no-follow lookup, EINTR retry, and platform-specific fallbacks.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `syscall`, `golang.org/x/sys/unix`, `github.com/rfjakob/gocryptfs/v2/internal/tlog`

Risks: platform syscall semantics and kernel/FUSE differences can change behavior.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/quirks_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/rename_exchange_test.go -->
# sources/security-integrity/gocryptfs/internal/syscallcompat/rename_exchange_test.go

Purpose: Portable and security-conscious syscall wrapper code or tests for dirfd-relative operations, no-follow behavior, credentials, xattrs, directory reads, rename flags, EINTR handling, and platform differences.

Important APIs and types: package `syscallcompat`; functions/tests `TestRenameExchange`; key imports `os`, `path/filepath`, `testing`, `golang.org/x/sys/unix`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. The subsystem centralizes syscall details so higher-level FUSE code can use safer defaults such as `O_CLOEXEC`, no-follow lookup, EINTR retry, and platform-specific fallbacks.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `os`, `path/filepath`, `testing`, `golang.org/x/sys/unix`

Risks: platform syscall semantics and kernel/FUSE differences can change behavior.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/rename_exchange_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/sys_common.go -->
# sources/security-integrity/gocryptfs/internal/syscallcompat/sys_common.go

Purpose: Portable and security-conscious syscall wrapper code or tests for dirfd-relative operations, no-follow behavior, credentials, xattrs, directory reads, rename flags, EINTR handling, and platform differences.

Important APIs and types: package `syscallcompat`; functions/tests `Readlinkat`, `Faccessat`, `Openat`, `Fchownat`, `Fstatat`, `Fstatat2`, `Fgetxattr`, `Lgetxattr`, `getxattrSmartBuf`, `Flistxattr`, `Llistxattr`, `listxattrSmartBuf`, `parseListxattrBlob`; constants `PATH_MAX`, `XATTR_SIZE_MAX`, `GETXATTR_BUFSZ_BIG`, `GETXATTR_BUFSZ_SMALL`; key imports `bytes`, `syscall`, `golang.org/x/sys/unix`, `github.com/rfjakob/gocryptfs/v2/internal/tlog`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. The subsystem centralizes syscall details so higher-level FUSE code can use safer defaults such as `O_CLOEXEC`, no-follow lookup, EINTR retry, and platform-specific fallbacks. Extended attribute helpers normalize Linux/macOS buffer sizing differences and avoid ERANGE retry loops by converting oversize values to overflow errors.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `bytes`, `syscall`, `golang.org/x/sys/unix`, `github.com/rfjakob/gocryptfs/v2/internal/tlog`

Risks: platform syscall semantics and kernel/FUSE differences can change behavior.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/sys_common.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/sys_common_test.go -->
# sources/security-integrity/gocryptfs/internal/syscallcompat/sys_common_test.go

Purpose: Portable and security-conscious syscall wrapper code or tests for dirfd-relative operations, no-follow behavior, credentials, xattrs, directory reads, rename flags, EINTR handling, and platform differences.

Important APIs and types: package `syscallcompat`; functions/tests `TestReadlinkat`, `TestOpenat`, `TestRenameat`, `TestUnlinkat`, `TestFchmodatNofollow`, `symlinkCheckMode`, `TestSymlinkat`, `TestMkdirat`, `TestFstatat`, `BenchmarkLgetxattr`; key imports `bytes`, `os`, `runtime`, `syscall`, `testing`, `golang.org/x/sys/unix`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. The subsystem centralizes syscall details so higher-level FUSE code can use safer defaults such as `O_CLOEXEC`, no-follow lookup, EINTR retry, and platform-specific fallbacks. Extended attribute helpers normalize Linux/macOS buffer sizing differences and avoid ERANGE retry loops by converting oversize values to overflow errors.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `bytes`, `os`, `runtime`, `syscall`, `testing`, `golang.org/x/sys/unix`

Risks: platform syscall semantics and kernel/FUSE differences can change behavior; some checks are timing-sensitive.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/sys_common_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/sys_darwin.go -->
# sources/security-integrity/gocryptfs/internal/syscallcompat/sys_darwin.go

Purpose: Portable and security-conscious syscall wrapper code or tests for dirfd-relative operations, no-follow behavior, credentials, xattrs, directory reads, rename flags, EINTR handling, and platform differences.

Important APIs and types: package `syscallcompat`; types `attrList`; functions/tests `fsetattrlist`, `setattrlist`, `EnospcPrealloc`, `Fallocate`, `Dup3`, `Mknodat`, `FchmodatNofollow`, `timesToAttrList`, `FutimesNano`, `UtimesNanoAtNofollow`, `Getdents`, `GetdentsSpecial`, `Renameat2`; key imports `log`, `path/filepath`, `syscall`, `time`, `unsafe`, `golang.org/x/sys/unix`, `github.com/hanwen/go-fuse/v2/fuse`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. The subsystem centralizes syscall details so higher-level FUSE code can use safer defaults such as `O_CLOEXEC`, no-follow lookup, EINTR retry, and platform-specific fallbacks. Directory entry conversion must handle dot entries, deleted-in-flight names, unknown d_type values, and corrupt dirent lengths without crashing the mount. Preallocation behavior protects against ENOSPC-induced ciphertext corruption on Linux but is weaker or unavailable on Darwin/FreeBSD and quirky filesystems.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `log`, `path/filepath`, `syscall`, `time`, `unsafe`, `golang.org/x/sys/unix`, `github.com/hanwen/go-fuse/v2/fuse`

Risks: platform syscall semantics and kernel/FUSE differences can change behavior; some checks are timing-sensitive.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/sys_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/sys_freebsd.go -->
# sources/security-integrity/gocryptfs/internal/syscallcompat/sys_freebsd.go

Purpose: Portable and security-conscious syscall wrapper code or tests for dirfd-relative operations, no-follow behavior, credentials, xattrs, directory reads, rename flags, EINTR handling, and platform differences.

Important APIs and types: package `syscallcompat`; functions/tests `EnospcPrealloc`, `Fallocate`, `Mknodat`, `Dup3`, `FchmodatNofollow`, `LsetxattrUser`, `timesToTimespec`, `FutimesNano`, `UtimesNanoAtNofollow`, `Getdents`, `GetdentsSpecial`, `Renameat2`; key imports `time`, `golang.org/x/sys/unix`, `github.com/hanwen/go-fuse/v2/fuse`, `github.com/rfjakob/gocryptfs/v2/internal/tlog`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. The subsystem centralizes syscall details so higher-level FUSE code can use safer defaults such as `O_CLOEXEC`, no-follow lookup, EINTR retry, and platform-specific fallbacks. Credential changes are especially sensitive: Linux uses raw per-thread syscalls and locked OS threads to avoid process-wide UID/GID changes. Directory entry conversion must handle dot entries, deleted-in-flight names, unknown d_type values, and corrupt dirent lengths without crashing the mount. Extended attribute helpers normalize Linux/macOS buffer sizing differences and avoid ERANGE retry loops by converting oversize values to overflow errors. Preallocation behavior protects against ENOSPC-induced ciphertext corruption on Linux but is weaker or unavailable on Darwin/FreeBSD and quirky filesystems.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `time`, `golang.org/x/sys/unix`, `github.com/hanwen/go-fuse/v2/fuse`, `github.com/rfjakob/gocryptfs/v2/internal/tlog`

Risks: platform syscall semantics and kernel/FUSE differences can change behavior; some checks are timing-sensitive.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/sys_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/sys_linux.go -->
# sources/security-integrity/gocryptfs/internal/syscallcompat/sys_linux.go

Purpose: Portable and security-conscious syscall wrapper code or tests for dirfd-relative operations, no-follow behavior, credentials, xattrs, directory reads, rename flags, EINTR handling, and platform differences.

Important APIs and types: package `syscallcompat`; functions/tests `EnospcPrealloc`, `Fallocate`, `Mknodat`, `Dup3`, `FchmodatNofollow`, `LsetxattrUser`, `timesToTimespec`, `FutimesNano`, `UtimesNanoAtNofollow`, `Getdents`, `GetdentsSpecial`, `Renameat2`; key imports `fmt`, `sync`, `syscall`, `time`, `golang.org/x/sys/unix`, `github.com/hanwen/go-fuse/v2/fuse`, `github.com/rfjakob/gocryptfs/v2/internal/tlog`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. The subsystem centralizes syscall details so higher-level FUSE code can use safer defaults such as `O_CLOEXEC`, no-follow lookup, EINTR retry, and platform-specific fallbacks. Credential changes are especially sensitive: Linux uses raw per-thread syscalls and locked OS threads to avoid process-wide UID/GID changes. Directory entry conversion must handle dot entries, deleted-in-flight names, unknown d_type values, and corrupt dirent lengths without crashing the mount. Extended attribute helpers normalize Linux/macOS buffer sizing differences and avoid ERANGE retry loops by converting oversize values to overflow errors. Preallocation behavior protects against ENOSPC-induced ciphertext corruption on Linux but is weaker or unavailable on Darwin/FreeBSD and quirky filesystems.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `fmt`, `sync`, `syscall`, `time`, `golang.org/x/sys/unix`, `github.com/hanwen/go-fuse/v2/fuse`, `github.com/rfjakob/gocryptfs/v2/internal/tlog`

Risks: platform syscall semantics and kernel/FUSE differences can change behavior; some checks are timing-sensitive.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/sys_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/thread_credentials_linux.go -->
# sources/security-integrity/gocryptfs/internal/syscallcompat/thread_credentials_linux.go

Purpose: Portable and security-conscious syscall wrapper code or tests for dirfd-relative operations, no-follow behavior, credentials, xattrs, directory reads, rename flags, EINTR handling, and platform differences.

Important APIs and types: build tags: linux; package `syscallcompat`; functions/tests `Setgroups`, `SetgroupsPanic`, `SetregidPanic`, `SetreuidPanic`; key imports `log`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. The subsystem centralizes syscall details so higher-level FUSE code can use safer defaults such as `O_CLOEXEC`, no-follow lookup, EINTR retry, and platform-specific fallbacks. Credential changes are especially sensitive: Linux uses raw per-thread syscalls and locked OS threads to avoid process-wide UID/GID changes.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `log`

Risks: panic paths are intentional for programmer errors but must not be reachable from untrusted malformed ciphertext except where tests expect ordinary errors; platform syscall semantics and kernel/FUSE differences can change behavior.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/thread_credentials_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/thread_credentials_linux_32.go -->
# sources/security-integrity/gocryptfs/internal/syscallcompat/thread_credentials_linux_32.go

Purpose: Portable and security-conscious syscall wrapper code or tests for dirfd-relative operations, no-follow behavior, credentials, xattrs, directory reads, rename flags, EINTR handling, and platform differences.

Important APIs and types: build tags: (linux && 386) || (linux && arm); package `syscallcompat`; functions/tests `Setreuid`, `Setregid`, `setgroups`; key imports `unsafe`, `golang.org/x/sys/unix`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. The subsystem centralizes syscall details so higher-level FUSE code can use safer defaults such as `O_CLOEXEC`, no-follow lookup, EINTR retry, and platform-specific fallbacks. Credential changes are especially sensitive: Linux uses raw per-thread syscalls and locked OS threads to avoid process-wide UID/GID changes.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `unsafe`, `golang.org/x/sys/unix`

Risks: platform syscall semantics and kernel/FUSE differences can change behavior.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/thread_credentials_linux_32.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/thread_credentials_linux_other.go -->
# sources/security-integrity/gocryptfs/internal/syscallcompat/thread_credentials_linux_other.go

Purpose: Portable and security-conscious syscall wrapper code or tests for dirfd-relative operations, no-follow behavior, credentials, xattrs, directory reads, rename flags, EINTR handling, and platform differences.

Important APIs and types: build tags: !((linux && 386) || (linux && arm)); package `syscallcompat`; functions/tests `Setreuid`, `Setregid`, `setgroups`; key imports `unsafe`, `golang.org/x/sys/unix`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. The subsystem centralizes syscall details so higher-level FUSE code can use safer defaults such as `O_CLOEXEC`, no-follow lookup, EINTR retry, and platform-specific fallbacks. Credential changes are especially sensitive: Linux uses raw per-thread syscalls and locked OS threads to avoid process-wide UID/GID changes.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `unsafe`, `golang.org/x/sys/unix`

Risks: platform syscall semantics and kernel/FUSE differences can change behavior.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/thread_credentials_linux_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/unix2syscall.go -->
# sources/security-integrity/gocryptfs/internal/syscallcompat/unix2syscall.go

Purpose: Portable and security-conscious syscall wrapper code or tests for dirfd-relative operations, no-follow behavior, credentials, xattrs, directory reads, rename flags, EINTR handling, and platform differences.

Important APIs and types: build tags: darwin || freebsd; package `syscallcompat`; functions/tests `Unix2syscall`; key imports `syscall`, `golang.org/x/sys/unix`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. The subsystem centralizes syscall details so higher-level FUSE code can use safer defaults such as `O_CLOEXEC`, no-follow lookup, EINTR retry, and platform-specific fallbacks.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `syscall`, `golang.org/x/sys/unix`

Risks: platform syscall semantics and kernel/FUSE differences can change behavior.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/unix2syscall.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/unix2syscall_linux.go -->
# sources/security-integrity/gocryptfs/internal/syscallcompat/unix2syscall_linux.go

Purpose: Portable and security-conscious syscall wrapper code or tests for dirfd-relative operations, no-follow behavior, credentials, xattrs, directory reads, rename flags, EINTR handling, and platform differences.

Important APIs and types: package `syscallcompat`; functions/tests `Unix2syscall`; key imports `syscall`, `golang.org/x/sys/unix`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. The subsystem centralizes syscall details so higher-level FUSE code can use safer defaults such as `O_CLOEXEC`, no-follow lookup, EINTR retry, and platform-specific fallbacks.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `syscall`, `golang.org/x/sys/unix`

Risks: platform syscall semantics and kernel/FUSE differences can change behavior.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/syscallcompat/unix2syscall_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/tlog/log.go -->
# sources/security-integrity/gocryptfs/internal/tlog/log.go

Purpose: Toggled logging support or tests for gocryptfs user-facing, debug, warning, fatal, color, and syslog output.

Important APIs and types: package `tlog`; types `toggledLogger`; functions/tests `JSONDump`, `trimNewline`, `Printf`, `Println`, `init`, `SwitchToSyslog`, `SwitchLoggerToSyslog`, `PrintMasterkeyReminder`; key imports `encoding/hex`, `encoding/json`, `fmt`, `log`, `log/syslog`, `os`, `golang.org/x/term`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `encoding/hex`, `encoding/json`, `fmt`, `log`, `log/syslog`, `os`, `golang.org/x/term`

Risks: panic paths are intentional for programmer errors but must not be reachable from untrusted malformed ciphertext except where tests expect ordinary errors.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/tlog/log.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/tlog/tlog_test.go -->
# sources/security-integrity/gocryptfs/internal/tlog/tlog_test.go

Purpose: Toggled logging support or tests for gocryptfs user-facing, debug, warning, fatal, color, and syslog output.

Important APIs and types: package `tlog`; functions/tests `TestTrimNewline`; key imports `testing`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `testing`

Risks: main risk is drift between this file and the subsystem contracts it supports.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/tlog/tlog_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/main.go -->
# sources/security-integrity/gocryptfs/main.go

Purpose: Main CLI entry point that parses options, loads/decrypts configuration, selects operations, and dispatches mount/init/passwd/info/fsck/speed behavior.

Important APIs and types: package `main`; functions/tests `loadConfig`, `changePassword`, `main`; key imports `log`, `os`, `path/filepath`, `runtime`, `strconv`, `strings`, `github.com/hanwen/go-fuse/v2/fuse`, `github.com/rfjakob/gocryptfs/v2/internal/configfile`, `github.com/rfjakob/gocryptfs/v2/internal/contentenc`, `github.com/rfjakob/gocryptfs/v2/internal/exitcodes`, `github.com/rfjakob/gocryptfs/v2/internal/fido2`, `github.com/rfjakob/gocryptfs/v2/internal/readpassword`, `github.com/rfjakob/gocryptfs/v2/internal/speed`, `github.com/rfjakob/gocryptfs/v2/internal/tlog`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. The CLI enforces exactly one operation flag, resolves config paths before loading secrets, and wipes password/master-key byte slices after use on a best-effort basis. Reverse mode tests and fixtures protect deterministic encrypted-view behavior and the AES-SIV requirement for safe reverse mounts.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `log`, `os`, `path/filepath`, `runtime`, `strconv`, `strings`, `github.com/hanwen/go-fuse/v2/fuse`, `github.com/rfjakob/gocryptfs/v2/internal/configfile`, `github.com/rfjakob/gocryptfs/v2/internal/contentenc`, `github.com/rfjakob/gocryptfs/v2/internal/exitcodes`, `github.com/rfjakob/gocryptfs/v2/internal/fido2`, `github.com/rfjakob/gocryptfs/v2/internal/readpassword`, `github.com/rfjakob/gocryptfs/v2/internal/speed`, `github.com/rfjakob/gocryptfs/v2/internal/tlog`

Risks: panic paths are intentional for programmer errors but must not be reachable from untrusted malformed ciphertext except where tests expect ordinary errors; some checks are timing-sensitive.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/masterkey.go -->
# sources/security-integrity/gocryptfs/masterkey.go

Purpose: Explicit master-key handling for recovery and test modes, including command-line, stdin, and all-zero key sources.

Important APIs and types: package `main`; functions/tests `unhexMasterKey`, `handleArgsMasterkey`; key imports `encoding/hex`, `os`, `strings`, `github.com/rfjakob/gocryptfs/v2/internal/cryptocore`, `github.com/rfjakob/gocryptfs/v2/internal/exitcodes`, `github.com/rfjakob/gocryptfs/v2/internal/readpassword`, `github.com/rfjakob/gocryptfs/v2/internal/tlog`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `encoding/hex`, `os`, `strings`, `github.com/rfjakob/gocryptfs/v2/internal/cryptocore`, `github.com/rfjakob/gocryptfs/v2/internal/exitcodes`, `github.com/rfjakob/gocryptfs/v2/internal/readpassword`, `github.com/rfjakob/gocryptfs/v2/internal/tlog`

Risks: main risk is drift between this file and the subsystem contracts it supports.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/masterkey.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/mount.go -->
# sources/security-integrity/gocryptfs/mount.go

Purpose: Mount lifecycle implementation that validates paths, initializes crypto/name transforms and FUSE frontends, configures go-fuse, handles daemonization, control sockets, idle unmount, and signal cleanup.

Important APIs and types: package `main`; types `AfterUnmounter`, `RootInoer`; functions/tests `doMount`, `idleMonitor`, `setOpenFileLimit`, `initFuseFrontend`, `initGoFuse`, `haveFusermount2`, `handleSigint`, `unmount`, `isReadOnlyFilesystem`; constants `checksDuringTimeoutPeriod`; key imports `bytes`, `log`, `log/syslog`, `math`, `os`, `os/exec`, `os/signal`, `path`, `path/filepath`, `runtime`, `runtime/debug`, `strings`, `syscall`, `time`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. Security-sensitive policy is concentrated here: reverse mode requires AES-SIV, recursive/shadow mounts are rejected, force-owner implies allow_other, and read-only backing filesystems force read-only mounts. Control-socket behavior matters because path encryption/decryption is exposed over a local IPC surface and malformed paths must warn rather than panic. Reverse mode tests and fixtures protect deterministic encrypted-view behavior and the AES-SIV requirement for safe reverse mounts. HKDF flags are compatibility-critical because content and name key derivation changes must not be silently ignored.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `bytes`, `log`, `log/syslog`, `math`, `os`, `os/exec`, `os/signal`, `path`, `path/filepath`, `runtime`, `runtime/debug`, `strings`, `syscall`, `time`, `golang.org/x/crypto/chacha20poly1305`

Risks: platform syscall semantics and kernel/FUSE differences can change behavior; some checks are timing-sensitive.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/mount.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/package-release-tarballs.bash -->
# sources/security-integrity/gocryptfs/package-release-tarballs.bash

Purpose: Shell utility in the shell harness area for testing, benchmarking, profiling, packaging, or cleanup.

Important APIs and types: Shell entry points `git_archive_extra`, `package_source`, `package_static_binary`, `signing_hint`. External commands observed: gocryptfs, dd, tar, rm, git archive, go mod vendor.

Control flow: The script runs in strict shell mode where present, prepares paths or validates arguments, invokes gocryptfs or filesystem utilities, and relies on exit status for success/failure.

State and persistence behavior: May create temporary directories, lock files, mounts, release tarballs, profile files, benchmark data, or downloaded tarballs; cleanup is handled by traps or later harness steps when present.

Dependencies and integration points: `gocryptfs`, `dd`, `tar`, `rm`, `git archive`, `go mod vendor`

Risks: scripts are environment-sensitive and can leave mounts or temporary files if interrupted before cleanup.

Test signals: Signal is successful script completion and expected command output/artifacts; several scripts are manual benchmark/profile helpers rather than deterministic tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/package-release-tarballs.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/profiling.go -->
# sources/security-integrity/gocryptfs/profiling.go

Purpose: CPU, memory, and execution-trace profile setup used by CLI profiling flags.

Important APIs and types: package `main`; functions/tests `setupCpuprofile`, `setupMemprofile`, `setupTrace`; key imports `os`, `runtime/pprof`, `runtime/trace`, `time`, `github.com/rfjakob/gocryptfs/v2/internal/exitcodes`, `github.com/rfjakob/gocryptfs/v2/internal/tlog`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `os`, `runtime/pprof`, `runtime/trace`, `time`, `github.com/rfjakob/gocryptfs/v2/internal/exitcodes`, `github.com/rfjakob/gocryptfs/v2/internal/tlog`

Risks: some checks are timing-sensitive.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/profiling.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/profiling/ls.bash -->
# sources/security-integrity/gocryptfs/profiling/ls.bash

Purpose: Shell utility in the profiling area for testing, benchmarking, profiling, packaging, or cleanup.

Important APIs and types: Shell entry points script main body. External commands observed: gocryptfs, fusermount, tar, ls, rm, cp.

Control flow: The script runs in strict shell mode where present, prepares paths or validates arguments, invokes gocryptfs or filesystem utilities, and relies on exit status for success/failure.

State and persistence behavior: May create temporary directories, lock files, mounts, release tarballs, profile files, benchmark data, or downloaded tarballs; cleanup is handled by traps or later harness steps when present.

Dependencies and integration points: `gocryptfs`, `fusermount`, `tar`, `ls`, `rm`, `cp`

Risks: scripts are environment-sensitive and can leave mounts or temporary files if interrupted before cleanup.

Test signals: Signal is successful script completion and expected command output/artifacts; several scripts are manual benchmark/profile helpers rather than deterministic tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/profiling/ls.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/profiling/streaming-read.bash -->
# sources/security-integrity/gocryptfs/profiling/streaming-read.bash

Purpose: Shell utility in the profiling area for testing, benchmarking, profiling, packaging, or cleanup.

Important APIs and types: Shell entry points script main body. External commands observed: gocryptfs, fusermount, dd, rm, cp.

Control flow: The script runs in strict shell mode where present, prepares paths or validates arguments, invokes gocryptfs or filesystem utilities, and relies on exit status for success/failure.

State and persistence behavior: May create temporary directories, lock files, mounts, release tarballs, profile files, benchmark data, or downloaded tarballs; cleanup is handled by traps or later harness steps when present.

Dependencies and integration points: `gocryptfs`, `fusermount`, `dd`, `rm`, `cp`

Risks: scripts are environment-sensitive and can leave mounts or temporary files if interrupted before cleanup.

Test signals: Signal is successful script completion and expected command output/artifacts; several scripts are manual benchmark/profile helpers rather than deterministic tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/profiling/streaming-read.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/profiling/streaming-write.bash -->
# sources/security-integrity/gocryptfs/profiling/streaming-write.bash

Purpose: Shell utility in the profiling area for testing, benchmarking, profiling, packaging, or cleanup.

Important APIs and types: Shell entry points script main body. External commands observed: gocryptfs, fusermount, dd, rm, cp.

Control flow: The script runs in strict shell mode where present, prepares paths or validates arguments, invokes gocryptfs or filesystem utilities, and relies on exit status for success/failure.

State and persistence behavior: May create temporary directories, lock files, mounts, release tarballs, profile files, benchmark data, or downloaded tarballs; cleanup is handled by traps or later harness steps when present.

Dependencies and integration points: `gocryptfs`, `fusermount`, `dd`, `rm`, `cp`

Risks: scripts are environment-sensitive and can leave mounts or temporary files if interrupted before cleanup.

Test signals: Signal is successful script completion and expected command output/artifacts; several scripts are manual benchmark/profile helpers rather than deterministic tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/profiling/streaming-write.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/profiling/tar-extract.bash -->
# sources/security-integrity/gocryptfs/profiling/tar-extract.bash

Purpose: Shell utility in the profiling area for testing, benchmarking, profiling, packaging, or cleanup.

Important APIs and types: Shell entry points script main body. External commands observed: gocryptfs, fusermount, tar, rm, cp.

Control flow: The script runs in strict shell mode where present, prepares paths or validates arguments, invokes gocryptfs or filesystem utilities, and relies on exit status for success/failure.

State and persistence behavior: May create temporary directories, lock files, mounts, release tarballs, profile files, benchmark data, or downloaded tarballs; cleanup is handled by traps or later harness steps when present.

Dependencies and integration points: `gocryptfs`, `fusermount`, `tar`, `rm`, `cp`

Risks: scripts are environment-sensitive and can leave mounts or temporary files if interrupted before cleanup.

Test signals: Signal is successful script completion and expected command output/artifacts; several scripts are manual benchmark/profile helpers rather than deterministic tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/profiling/tar-extract.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/profiling/tinyfiles.bash -->
# sources/security-integrity/gocryptfs/profiling/tinyfiles.bash

Purpose: Shell utility in the profiling area for testing, benchmarking, profiling, packaging, or cleanup.

Important APIs and types: Shell entry points script main body. External commands observed: gocryptfs, shellcheck, fusermount, dd, tar, rm, cp.

Control flow: The script runs in strict shell mode where present, prepares paths or validates arguments, invokes gocryptfs or filesystem utilities, and relies on exit status for success/failure. Reverse mode tests and fixtures protect deterministic encrypted-view behavior and the AES-SIV requirement for safe reverse mounts.

State and persistence behavior: May create temporary directories, lock files, mounts, release tarballs, profile files, benchmark data, or downloaded tarballs; cleanup is handled by traps or later harness steps when present.

Dependencies and integration points: `gocryptfs`, `shellcheck`, `fusermount`, `dd`, `tar`, `rm`, `cp`

Risks: scripts are environment-sensitive and can leave mounts or temporary files if interrupted before cleanup.

Test signals: Signal is successful script completion and expected command output/artifacts; several scripts are manual benchmark/profile helpers rather than deterministic tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/profiling/tinyfiles.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/profiling/write-trace.bash -->
# sources/security-integrity/gocryptfs/profiling/write-trace.bash

Purpose: Shell utility in the profiling area for testing, benchmarking, profiling, packaging, or cleanup.

Important APIs and types: Shell entry points script main body. External commands observed: gocryptfs, fusermount, dd, rm.

Control flow: The script runs in strict shell mode where present, prepares paths or validates arguments, invokes gocryptfs or filesystem utilities, and relies on exit status for success/failure.

State and persistence behavior: May create temporary directories, lock files, mounts, release tarballs, profile files, benchmark data, or downloaded tarballs; cleanup is handled by traps or later harness steps when present.

Dependencies and integration points: `gocryptfs`, `fusermount`, `dd`, `rm`

Risks: scripts are environment-sensitive and can leave mounts or temporary files if interrupted before cleanup.

Test signals: Signal is successful script completion and expected command output/artifacts; several scripts are manual benchmark/profile helpers rather than deterministic tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/profiling/write-trace.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/race.go -->
# sources/security-integrity/gocryptfs/race.go

Purpose: Top-level gocryptfs support source in this mapped research subset.

Important APIs and types: build tags: race; package `main`; functions/tests `init`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: nearby gocryptfs packages, platform syscalls, OpenSSL/go-fuse, or test helpers as implied by the file path.

Risks: main risk is drift between this file and the subsystem contracts it supports.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/race.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/sendusr1.go -->
# sources/security-integrity/gocryptfs/sendusr1.go

Purpose: Top-level gocryptfs support source in this mapped research subset.

Important APIs and types: package `main`; functions/tests `sendUsr1`; key imports `os`, `syscall`, `github.com/rfjakob/gocryptfs/v2/internal/tlog`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `os`, `syscall`, `github.com/rfjakob/gocryptfs/v2/internal/tlog`

Risks: platform syscall semantics and kernel/FUSE differences can change behavior.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/sendusr1.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/test-without-openssl.bash -->
# sources/security-integrity/gocryptfs/test-without-openssl.bash

Purpose: Shell utility in the shell harness area for testing, benchmarking, profiling, packaging, or cleanup.

Important APIs and types: Shell entry points script main body. External commands observed: standard shell utilities.

Control flow: The script runs in strict shell mode where present, prepares paths or validates arguments, invokes gocryptfs or filesystem utilities, and relies on exit status for success/failure.

State and persistence behavior: May create temporary directories, lock files, mounts, release tarballs, profile files, benchmark data, or downloaded tarballs; cleanup is handled by traps or later harness steps when present.

Dependencies and integration points: nearby gocryptfs packages, platform syscalls, OpenSSL/go-fuse, or test helpers as implied by the file path.

Risks: scripts are environment-sensitive and can leave mounts or temporary files if interrupted before cleanup.

Test signals: Signal is successful script completion and expected command output/artifacts; several scripts are manual benchmark/profile helpers rather than deterministic tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/test-without-openssl.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/test.bash -->
# sources/security-integrity/gocryptfs/test.bash

Purpose: Shell utility in the shell harness area for testing, benchmarking, profiling, packaging, or cleanup.

Important APIs and types: Shell entry points `unmount_leftovers`. External commands observed: gocryptfs, go test, go vet, staticcheck, shellcheck, tar, ls, rm.

Control flow: The script runs in strict shell mode where present, prepares paths or validates arguments, invokes gocryptfs or filesystem utilities, and relies on exit status for success/failure.

State and persistence behavior: May create temporary directories, lock files, mounts, release tarballs, profile files, benchmark data, or downloaded tarballs; cleanup is handled by traps or later harness steps when present.

Dependencies and integration points: `gocryptfs`, `go test`, `go vet`, `staticcheck`, `shellcheck`, `tar`, `ls`, `rm`

Risks: panic paths are intentional for programmer errors but must not be reachable from untrusted malformed ciphertext except where tests expect ordinary errors; platform syscall semantics and kernel/FUSE differences can change behavior; scripts are environment-sensitive and can leave mounts or temporary files if interrupted before cleanup.

Test signals: Signal is successful script completion and expected command output/artifacts; several scripts are manual benchmark/profile helpers rather than deterministic tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/test.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/canonical-benchmarks.bash -->
# sources/security-integrity/gocryptfs/tests/canonical-benchmarks.bash

Purpose: Shell utility in the shell harness area for testing, benchmarking, profiling, packaging, or cleanup.

Important APIs and types: Shell entry points script main body. External commands observed: gocryptfs, dd, tar, md5sum, ls, rm.

Control flow: The script runs in strict shell mode where present, prepares paths or validates arguments, invokes gocryptfs or filesystem utilities, and relies on exit status for success/failure.

State and persistence behavior: May create temporary directories, lock files, mounts, release tarballs, profile files, benchmark data, or downloaded tarballs; cleanup is handled by traps or later harness steps when present.

Dependencies and integration points: `gocryptfs`, `dd`, `tar`, `md5sum`, `ls`, `rm`

Risks: scripts are environment-sensitive and can leave mounts or temporary files if interrupted before cleanup.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/canonical-benchmarks.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/cli/cli_test.go -->
# sources/security-integrity/gocryptfs/tests/cli/cli_test.go

Purpose: Integration or regression test file in the cli tests suite.

Important APIs and types: package `cli`; functions/tests `TestMain`, `TestInit`, `TestInitFilePerms`, `TestInitDevRandom`, `TestInitAessiv`, `TestInitReverse`, `TestInitMasterkey`, `testPasswd`, `TestPasswd`, `cp`, `TestPasswdMasterkey`, `TestPasswdMasterkeyStdin`, `TestPasswdReverse`, `TestPasswdScryptn`, `TestInitConfig`, `TestRo`, `TestNonempty`, `TestNofail`, `TestShadows`, `TestMountPasswordIncorrect`, `TestMountPasswordEmpty`, `TestPasswdPasswordIncorrect`, `TestMountBackground`, `TestMultipleOperationFlags`, `TestNoexec`, `TestMissingOArg`, `TestExcludeForward`, `TestConfigPipe`, `TestComma`, `TestIdle`, `TestNotIdle`, `TestSymlinkedCipherdir`, `TestBadname`, `TestPassfile`, `TestPassfileX2`; key imports `bytes`, `encoding/hex`, `errors`, `fmt`, `os`, `os/exec`, `strconv`, `strings`, `sync`, `syscall`, `testing`, `time`, `github.com/rfjakob/gocryptfs/v2/internal/configfile`, `github.com/rfjakob/gocryptfs/v2/internal/exitcodes`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. Control-socket behavior matters because path encryption/decryption is exposed over a local IPC surface and malformed paths must warn rather than panic. Reverse mode tests and fixtures protect deterministic encrypted-view behavior and the AES-SIV requirement for safe reverse mounts.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `bytes`, `encoding/hex`, `errors`, `fmt`, `os`, `os/exec`, `strconv`, `strings`, `sync`, `syscall`, `testing`, `time`, `github.com/rfjakob/gocryptfs/v2/internal/configfile`, `github.com/rfjakob/gocryptfs/v2/internal/exitcodes`, `github.com/rfjakob/gocryptfs/v2/internal/nametransform`

Risks: panic paths are intentional for programmer errors but must not be reachable from untrusted malformed ciphertext except where tests expect ordinary errors; platform syscall semantics and kernel/FUSE differences can change behavior; some checks are timing-sensitive.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/cli/cli_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/cli/directmount_test.go -->
# sources/security-integrity/gocryptfs/tests/cli/directmount_test.go

Purpose: Integration or regression test file in the cli tests suite.

Important APIs and types: package `cli`; functions/tests `TestDirectMount`; key imports `fmt`, `os`, `strings`, `testing`, `github.com/moby/sys/mountinfo`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `fmt`, `os`, `strings`, `testing`, `github.com/moby/sys/mountinfo`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Risks: platform syscall semantics and kernel/FUSE differences can change behavior.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/cli/directmount_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/cli/longnamemax_test.go -->
# sources/security-integrity/gocryptfs/tests/cli/longnamemax_test.go

Purpose: Integration or regression test file in the cli tests suite.

Important APIs and types: package `cli`; functions/tests `TestLongnamemax100`, `TestLongnamemax100Reverse`; key imports `fmt`, `os`, `path/filepath`, `strings`, `syscall`, `testing`, `github.com/rfjakob/gocryptfs/v2/internal/configfile`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. Reverse mode tests and fixtures protect deterministic encrypted-view behavior and the AES-SIV requirement for safe reverse mounts.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `fmt`, `os`, `path/filepath`, `strings`, `syscall`, `testing`, `github.com/rfjakob/gocryptfs/v2/internal/configfile`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Risks: platform syscall semantics and kernel/FUSE differences can change behavior.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/cli/longnamemax_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/cli/xchacha_test.go -->
# sources/security-integrity/gocryptfs/tests/cli/xchacha_test.go

Purpose: Integration or regression test file in the cli tests suite.

Important APIs and types: package `cli`; functions/tests `TestInitXchacha`, `TestXchacha`; key imports `fmt`, `os`, `syscall`, `testing`, `github.com/rfjakob/gocryptfs/v2/internal/configfile`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. HKDF flags are compatibility-critical because content and name key derivation changes must not be silently ignored.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `fmt`, `os`, `syscall`, `testing`, `github.com/rfjakob/gocryptfs/v2/internal/configfile`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Risks: platform syscall semantics and kernel/FUSE differences can change behavior.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/cli/xchacha_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/cli/zerokey_test.go -->
# sources/security-integrity/gocryptfs/tests/cli/zerokey_test.go

Purpose: Integration or regression test file in the cli tests suite.

Important APIs and types: package `cli`; functions/tests `TestZerokey`; key imports `os`, `os/exec`, `testing`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `os`, `os/exec`, `testing`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Risks: main risk is drift between this file and the subsystem contracts it supports.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/cli/zerokey_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/cluster/cluster_test.go -->
# sources/security-integrity/gocryptfs/tests/cluster/cluster_test.go

Purpose: Integration or regression test file in the cluster tests suite.

Important APIs and types: package `cluster_test`; functions/tests `TestClusterConcurrentRW`; key imports `bytes`, `math/rand`, `os`, `sync`, `testing`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `bytes`, `math/rand`, `os`, `sync`, `testing`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Risks: panic paths are intentional for programmer errors but must not be reachable from untrusted malformed ciphertext except where tests expect ordinary errors.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/cluster/cluster_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/defaults/acl_test.go -->
# sources/security-integrity/gocryptfs/tests/defaults/acl_test.go

Purpose: Integration or regression test file in the defaults tests suite.

Important APIs and types: package `defaults`; functions/tests `TestCpA`, `getfacl`, `TestAcl543`, `TestXattrOverflow`; key imports `math/rand`, `os`, `os/exec`, `path/filepath`, `syscall`, `testing`, `golang.org/x/sys/unix`, `github.com/pkg/xattr`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `math/rand`, `os`, `os/exec`, `path/filepath`, `syscall`, `testing`, `golang.org/x/sys/unix`, `github.com/pkg/xattr`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Risks: platform syscall semantics and kernel/FUSE differences can change behavior.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/defaults/acl_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/defaults/ctlsock_test.go -->
# sources/security-integrity/gocryptfs/tests/defaults/ctlsock_test.go

Purpose: Integration or regression test file in the defaults tests suite.

Important APIs and types: package `defaults`; functions/tests `TestCtlSock`, `TestCtlSockDecrypt`, `TestCtlSockDecryptCrash`; key imports `os`, `syscall`, `testing`, `github.com/rfjakob/gocryptfs/v2/ctlsock`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. Control-socket behavior matters because path encryption/decryption is exposed over a local IPC surface and malformed paths must warn rather than panic.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `os`, `syscall`, `testing`, `github.com/rfjakob/gocryptfs/v2/ctlsock`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Risks: panic paths are intentional for programmer errors but must not be reachable from untrusted malformed ciphertext except where tests expect ordinary errors; platform syscall semantics and kernel/FUSE differences can change behavior.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/defaults/ctlsock_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/defaults/diriv_test.go -->
# sources/security-integrity/gocryptfs/tests/defaults/diriv_test.go

Purpose: Integration or regression test file in the defaults tests suite.

Important APIs and types: package `defaults`; functions/tests `TestDirIVRace`; key imports `os`, `sync`, `sync/atomic`, `syscall`, `testing`, `time`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `os`, `sync`, `sync/atomic`, `syscall`, `testing`, `time`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Risks: platform syscall semantics and kernel/FUSE differences can change behavior; some checks are timing-sensitive.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/defaults/diriv_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/defaults/getdents_linux.go -->
# sources/security-integrity/gocryptfs/tests/defaults/getdents_linux.go

Purpose: Integration or regression test file in the defaults tests suite.

Important APIs and types: package `defaults`; functions/tests `getdents`; key imports `golang.org/x/sys/unix`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `golang.org/x/sys/unix`

Risks: platform syscall semantics and kernel/FUSE differences can change behavior.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/defaults/getdents_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/defaults/getdents_other.go -->
# sources/security-integrity/gocryptfs/tests/defaults/getdents_other.go

Purpose: Integration or regression test file in the defaults tests suite.

Important APIs and types: build tags: !linux; package `defaults`; functions/tests `getdents`; key imports `golang.org/x/sys/unix`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `golang.org/x/sys/unix`

Risks: platform syscall semantics and kernel/FUSE differences can change behavior.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/defaults/getdents_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/defaults/main_test.go -->
# sources/security-integrity/gocryptfs/tests/defaults/main_test.go

Purpose: Integration or regression test file in the defaults tests suite.

Important APIs and types: package `defaults`; functions/tests `TestMain`, `Test1980Tar`, `TestOpenTruncateRead`, `TestWORead`, `TestXfs124`, `TestWrite0200File`, `TestMvWarnings`, `TestMvWarningSymlink`, `TestCpWarnings`, `TestSeekData`, `TestMd5sumMaintainers`, `TestMaxlen`, `TestFsync`, `TestForceOwner`, `TestSeekDir`; key imports `bytes`, `fmt`, `io`, `os`, `os/exec`, `path/filepath`, `runtime`, `strings`, `sync`, `syscall`, `testing`, `golang.org/x/sys/unix`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `bytes`, `fmt`, `io`, `os`, `os/exec`, `path/filepath`, `runtime`, `strings`, `sync`, `syscall`, `testing`, `golang.org/x/sys/unix`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Risks: panic paths are intentional for programmer errors but must not be reachable from untrusted malformed ciphertext except where tests expect ordinary errors; platform syscall semantics and kernel/FUSE differences can change behavior; some checks are timing-sensitive.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/defaults/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/defaults/overlayfs_test.go -->
# sources/security-integrity/gocryptfs/tests/defaults/overlayfs_test.go

Purpose: Integration or regression test file in the defaults tests suite.

Important APIs and types: build tags: linux; package `defaults`; functions/tests `TestRenameWhiteout`, `TestRenameExchange`, `TestOTmpfile`; key imports `os`, `strings`, `testing`, `golang.org/x/sys/unix`, `github.com/rfjakob/gocryptfs/v2/internal/syscallcompat`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `os`, `strings`, `testing`, `golang.org/x/sys/unix`, `github.com/rfjakob/gocryptfs/v2/internal/syscallcompat`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Risks: platform syscall semantics and kernel/FUSE differences can change behavior.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/defaults/overlayfs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/defaults/performance_test.go -->
# sources/security-integrity/gocryptfs/tests/defaults/performance_test.go

Purpose: Integration or regression test file in the defaults tests suite.

Important APIs and types: package `defaults`; functions/tests `BenchmarkStreamWrite`, `BenchmarkStreamRead`, `createFiles`, `BenchmarkCreate0B`, `BenchmarkCreate1B`, `BenchmarkCreate100B`, `BenchmarkCreate4kB`, `BenchmarkCreate10kB`; key imports `fmt`, `io`, `os`, `testing`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `fmt`, `io`, `os`, `testing`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Risks: main risk is drift between this file and the subsystem contracts it supports.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/defaults/performance_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/deterministic_names/deterministic_names_test.go -->
# sources/security-integrity/gocryptfs/tests/deterministic_names/deterministic_names_test.go

Purpose: Integration or regression test file in the deterministic names tests suite.

Important APIs and types: package `deterministic_names`; functions/tests `TestMain`, `TestDeterministicNames`; key imports `fmt`, `os`, `path/filepath`, `testing`, `github.com/rfjakob/gocryptfs/v2/internal/configfile`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `fmt`, `os`, `path/filepath`, `testing`, `github.com/rfjakob/gocryptfs/v2/internal/configfile`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Risks: main risk is drift between this file and the subsystem contracts it supports.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/deterministic_names/deterministic_names_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/dl-linux-tarball.bash -->
# sources/security-integrity/gocryptfs/tests/dl-linux-tarball.bash

Purpose: Shell utility in the shell harness area for testing, benchmarking, profiling, packaging, or cleanup.

Important APIs and types: Shell entry points script main body. External commands observed: tar, ls, curl, wget.

Control flow: The script runs in strict shell mode where present, prepares paths or validates arguments, invokes gocryptfs or filesystem utilities, and relies on exit status for success/failure.

State and persistence behavior: May create temporary directories, lock files, mounts, release tarballs, profile files, benchmark data, or downloaded tarballs; cleanup is handled by traps or later harness steps when present.

Dependencies and integration points: `tar`, `ls`, `curl`, `wget`

Risks: scripts are environment-sensitive and can leave mounts or temporary files if interrupted before cleanup.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/dl-linux-tarball.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/example_filesystems/example_filesystems_test.go -->
# sources/security-integrity/gocryptfs/tests/example_filesystems/example_filesystems_test.go

Purpose: Integration or regression test file in the example filesystem compatibility suite.

Important APIs and types: package `example_filesystems`; functions/tests `TestMain`, `TestExampleFSv04`, `TestExampleFSv05`, `TestExampleFSv06`, `TestExampleFSv06PlaintextNames`, `TestExampleFSv07`, `TestExampleFSv07PlaintextNames`, `TestExampleFSv09`, `TestExampleFSv11`, `TestExampleFSv11reverse`, `TestExampleFSv11reversePlaintextnames`, `TestExampleFSv13`, `TestExampleFSv13MasterkeyStdin`, `TestExampleFSv13reverse`, `TestExampleFSv22deterministicNames`, `TestExampleFSv22xchacha`, `TestExampleFSv22xchachaDeterministicNames`; key imports `flag`, `fmt`, `os`, `os/exec`, `syscall`, `testing`, `github.com/rfjakob/gocryptfs/v2/internal/stupidgcm`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. Reverse mode tests and fixtures protect deterministic encrypted-view behavior and the AES-SIV requirement for safe reverse mounts. HKDF flags are compatibility-critical because content and name key derivation changes must not be silently ignored.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `flag`, `fmt`, `os`, `os/exec`, `syscall`, `testing`, `github.com/rfjakob/gocryptfs/v2/internal/stupidgcm`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Risks: panic paths are intentional for programmer errors but must not be reachable from untrusted malformed ciphertext except where tests expect ordinary errors; platform syscall semantics and kernel/FUSE differences can change behavior.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/example_filesystems/example_filesystems_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/example_filesystems/example_test_helpers.go -->
# sources/security-integrity/gocryptfs/tests/example_filesystems/example_test_helpers.go

Purpose: Integration or regression test file in the example filesystem compatibility suite.

Important APIs and types: package `example_filesystems`; functions/tests `checkExampleFS`, `checkExampleFSLongnames`, `checkExampleFSrw`; constants `statusTxtContent`; key imports `os`, `path/filepath`, `testing`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `os`, `path/filepath`, `testing`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Risks: main risk is drift between this file and the subsystem contracts it supports.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/example_filesystems/example_test_helpers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/example_filesystems/v0.4/gocryptfs.conf -->
# sources/security-integrity/gocryptfs/tests/example_filesystems/v0.4/gocryptfs.conf

Purpose: Historical or intentionally broken gocryptfs JSON configuration fixture used by compatibility, fsck, or HKDF sanity tests.

Important APIs and types: JSON fixture fields: Creator=absent, Version=2, Scrypt N=65536, FeatureFlags=None.

Control flow: There is no executable flow. Compatibility and fsck tests load this fixture through gocryptfs config parsing, decrypt with the known test password or master key, and compare behavior with adjacent ciphertext fixture files. This JSON fixture stores encrypted key metadata with Scrypt N=65536, Version=2, Creator=not recorded, FeatureFlags=None.

State and persistence behavior: Checked-in persistent encrypted master-key metadata and feature flags. The fixture must remain byte-compatible with the surrounding encrypted files.

Dependencies and integration points: `configfile parser`, `test password/masterkey`, `neighboring encrypted fixture files`

Risks: editing flags, salts, or encrypted key material can invalidate historical compatibility expectations.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/example_filesystems/v0.4/gocryptfs.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/example_filesystems/v0.5/gocryptfs.conf -->
# sources/security-integrity/gocryptfs/tests/example_filesystems/v0.5/gocryptfs.conf

Purpose: Historical or intentionally broken gocryptfs JSON configuration fixture used by compatibility, fsck, or HKDF sanity tests.

Important APIs and types: JSON fixture fields: Creator=absent, Version=2, Scrypt N=1024, FeatureFlags=['DirIV'].

Control flow: There is no executable flow. Compatibility and fsck tests load this fixture through gocryptfs config parsing, decrypt with the known test password or master key, and compare behavior with adjacent ciphertext fixture files. This JSON fixture stores encrypted key metadata with Scrypt N=1024, Version=2, Creator=not recorded, FeatureFlags=['DirIV'].

State and persistence behavior: Checked-in persistent encrypted master-key metadata and feature flags. The fixture must remain byte-compatible with the surrounding encrypted files.

Dependencies and integration points: `configfile parser`, `test password/masterkey`, `neighboring encrypted fixture files`

Risks: editing flags, salts, or encrypted key material can invalidate historical compatibility expectations.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/example_filesystems/v0.5/gocryptfs.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/example_filesystems/v0.6-plaintextnames/gocryptfs.conf -->
# sources/security-integrity/gocryptfs/tests/example_filesystems/v0.6-plaintextnames/gocryptfs.conf

Purpose: Historical or intentionally broken gocryptfs JSON configuration fixture used by compatibility, fsck, or HKDF sanity tests.

Important APIs and types: JSON fixture fields: Creator=absent, Version=2, Scrypt N=1024, FeatureFlags=['PlaintextNames'].

Control flow: There is no executable flow. Compatibility and fsck tests load this fixture through gocryptfs config parsing, decrypt with the known test password or master key, and compare behavior with adjacent ciphertext fixture files. This JSON fixture stores encrypted key metadata with Scrypt N=1024, Version=2, Creator=not recorded, FeatureFlags=['PlaintextNames'].

State and persistence behavior: Checked-in persistent encrypted master-key metadata and feature flags. The fixture must remain byte-compatible with the surrounding encrypted files.

Dependencies and integration points: `configfile parser`, `test password/masterkey`, `neighboring encrypted fixture files`

Risks: editing flags, salts, or encrypted key material can invalidate historical compatibility expectations.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/example_filesystems/v0.6-plaintextnames/gocryptfs.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/example_filesystems/v0.6/gocryptfs.conf -->
# sources/security-integrity/gocryptfs/tests/example_filesystems/v0.6/gocryptfs.conf

Purpose: Historical or intentionally broken gocryptfs JSON configuration fixture used by compatibility, fsck, or HKDF sanity tests.

Important APIs and types: JSON fixture fields: Creator=absent, Version=2, Scrypt N=1024, FeatureFlags=['DirIV', 'EMENames'].

Control flow: There is no executable flow. Compatibility and fsck tests load this fixture through gocryptfs config parsing, decrypt with the known test password or master key, and compare behavior with adjacent ciphertext fixture files. This JSON fixture stores encrypted key metadata with Scrypt N=1024, Version=2, Creator=not recorded, FeatureFlags=['DirIV', 'EMENames'].

State and persistence behavior: Checked-in persistent encrypted master-key metadata and feature flags. The fixture must remain byte-compatible with the surrounding encrypted files.

Dependencies and integration points: `configfile parser`, `test password/masterkey`, `neighboring encrypted fixture files`

Risks: editing flags, salts, or encrypted key material can invalidate historical compatibility expectations.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/example_filesystems/v0.6/gocryptfs.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/example_filesystems/v0.7-plaintextnames/gocryptfs.conf -->
# sources/security-integrity/gocryptfs/tests/example_filesystems/v0.7-plaintextnames/gocryptfs.conf

Purpose: Historical or intentionally broken gocryptfs JSON configuration fixture used by compatibility, fsck, or HKDF sanity tests.

Important APIs and types: JSON fixture fields: Creator=absent, Version=2, Scrypt N=1024, FeatureFlags=['GCMIV128', 'PlaintextNames'].

Control flow: There is no executable flow. Compatibility and fsck tests load this fixture through gocryptfs config parsing, decrypt with the known test password or master key, and compare behavior with adjacent ciphertext fixture files. This JSON fixture stores encrypted key metadata with Scrypt N=1024, Version=2, Creator=not recorded, FeatureFlags=['GCMIV128', 'PlaintextNames'].

State and persistence behavior: Checked-in persistent encrypted master-key metadata and feature flags. The fixture must remain byte-compatible with the surrounding encrypted files.

Dependencies and integration points: `configfile parser`, `test password/masterkey`, `neighboring encrypted fixture files`

Risks: editing flags, salts, or encrypted key material can invalidate historical compatibility expectations.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/example_filesystems/v0.7-plaintextnames/gocryptfs.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/example_filesystems/v0.7/gocryptfs.conf -->
# sources/security-integrity/gocryptfs/tests/example_filesystems/v0.7/gocryptfs.conf

Purpose: Historical or intentionally broken gocryptfs JSON configuration fixture used by compatibility, fsck, or HKDF sanity tests.

Important APIs and types: JSON fixture fields: Creator=absent, Version=2, Scrypt N=1024, FeatureFlags=['GCMIV128', 'DirIV', 'EMENames'].

Control flow: There is no executable flow. Compatibility and fsck tests load this fixture through gocryptfs config parsing, decrypt with the known test password or master key, and compare behavior with adjacent ciphertext fixture files. This JSON fixture stores encrypted key metadata with Scrypt N=1024, Version=2, Creator=not recorded, FeatureFlags=['GCMIV128', 'DirIV', 'EMENames'].

State and persistence behavior: Checked-in persistent encrypted master-key metadata and feature flags. The fixture must remain byte-compatible with the surrounding encrypted files.

Dependencies and integration points: `configfile parser`, `test password/masterkey`, `neighboring encrypted fixture files`

Risks: editing flags, salts, or encrypted key material can invalidate historical compatibility expectations.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/example_filesystems/v0.7/gocryptfs.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/example_filesystems/v0.9/gocryptfs.conf -->
# sources/security-integrity/gocryptfs/tests/example_filesystems/v0.9/gocryptfs.conf

Purpose: Historical or intentionally broken gocryptfs JSON configuration fixture used by compatibility, fsck, or HKDF sanity tests.

Important APIs and types: JSON fixture fields: Creator=absent, Version=2, Scrypt N=1024, FeatureFlags=['GCMIV128', 'DirIV', 'EMENames', 'LongNames'].

Control flow: There is no executable flow. Compatibility and fsck tests load this fixture through gocryptfs config parsing, decrypt with the known test password or master key, and compare behavior with adjacent ciphertext fixture files. This JSON fixture stores encrypted key metadata with Scrypt N=1024, Version=2, Creator=not recorded, FeatureFlags=['GCMIV128', 'DirIV', 'EMENames', 'LongNames'].

State and persistence behavior: Checked-in persistent encrypted master-key metadata and feature flags. The fixture must remain byte-compatible with the surrounding encrypted files.

Dependencies and integration points: `configfile parser`, `test password/masterkey`, `neighboring encrypted fixture files`

Risks: editing flags, salts, or encrypted key material can invalidate historical compatibility expectations.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/example_filesystems/v0.9/gocryptfs.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/example_filesystems/v1.1-aessiv/gocryptfs.conf -->
# sources/security-integrity/gocryptfs/tests/example_filesystems/v1.1-aessiv/gocryptfs.conf

Purpose: Historical or intentionally broken gocryptfs JSON configuration fixture used by compatibility, fsck, or HKDF sanity tests.

Important APIs and types: JSON fixture fields: Creator=gocryptfs v1.1-beta1-33-gf054353-dirty, Version=2, Scrypt N=1024, FeatureFlags=['GCMIV128', 'DirIV', 'EMENames', 'LongNames', 'AESSIV'].

Control flow: There is no executable flow. Compatibility and fsck tests load this fixture through gocryptfs config parsing, decrypt with the known test password or master key, and compare behavior with adjacent ciphertext fixture files. This JSON fixture stores encrypted key metadata with Scrypt N=1024, Version=2, Creator=gocryptfs v1.1-beta1-33-gf054353-dirty, FeatureFlags=['GCMIV128', 'DirIV', 'EMENames', 'LongNames', 'AESSIV'].

State and persistence behavior: Checked-in persistent encrypted master-key metadata and feature flags. The fixture must remain byte-compatible with the surrounding encrypted files.

Dependencies and integration points: `configfile parser`, `test password/masterkey`, `neighboring encrypted fixture files`

Risks: editing flags, salts, or encrypted key material can invalidate historical compatibility expectations.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/example_filesystems/v1.1-aessiv/gocryptfs.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/example_filesystems/v1.1-reverse-plaintextnames/.gocryptfs.reverse.conf -->
# sources/security-integrity/gocryptfs/tests/example_filesystems/v1.1-reverse-plaintextnames/.gocryptfs.reverse.conf

Purpose: Historical or intentionally broken gocryptfs JSON configuration fixture used by compatibility, fsck, or HKDF sanity tests.

Important APIs and types: JSON fixture fields: Creator=gocryptfs v1.1-beta1-33-gf054353-dirty, Version=2, Scrypt N=1024, FeatureFlags=['GCMIV128', 'PlaintextNames', 'AESSIV'].

Control flow: There is no executable flow. Compatibility and fsck tests load this fixture through gocryptfs config parsing, decrypt with the known test password or master key, and compare behavior with adjacent ciphertext fixture files. Reverse mode tests and fixtures protect deterministic encrypted-view behavior and the AES-SIV requirement for safe reverse mounts. This JSON fixture stores encrypted key metadata with Scrypt N=1024, Version=2, Creator=gocryptfs v1.1-beta1-33-gf054353-dirty, FeatureFlags=['GCMIV128', 'PlaintextNames', 'AESSIV'].

State and persistence behavior: Checked-in persistent encrypted master-key metadata and feature flags. The fixture must remain byte-compatible with the surrounding encrypted files.

Dependencies and integration points: `configfile parser`, `test password/masterkey`, `neighboring encrypted fixture files`

Risks: editing flags, salts, or encrypted key material can invalidate historical compatibility expectations.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/example_filesystems/v1.1-reverse-plaintextnames/.gocryptfs.reverse.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/example_filesystems/v1.1-reverse/.gocryptfs.reverse.conf -->
# sources/security-integrity/gocryptfs/tests/example_filesystems/v1.1-reverse/.gocryptfs.reverse.conf

Purpose: Historical or intentionally broken gocryptfs JSON configuration fixture used by compatibility, fsck, or HKDF sanity tests.

Important APIs and types: JSON fixture fields: Creator=gocryptfs v1.1-beta1-33-gf054353-dirty, Version=2, Scrypt N=1024, FeatureFlags=['GCMIV128', 'DirIV', 'EMENames', 'LongNames', 'AESSIV'].

Control flow: There is no executable flow. Compatibility and fsck tests load this fixture through gocryptfs config parsing, decrypt with the known test password or master key, and compare behavior with adjacent ciphertext fixture files. Reverse mode tests and fixtures protect deterministic encrypted-view behavior and the AES-SIV requirement for safe reverse mounts. This JSON fixture stores encrypted key metadata with Scrypt N=1024, Version=2, Creator=gocryptfs v1.1-beta1-33-gf054353-dirty, FeatureFlags=['GCMIV128', 'DirIV', 'EMENames', 'LongNames', 'AESSIV'].

State and persistence behavior: Checked-in persistent encrypted master-key metadata and feature flags. The fixture must remain byte-compatible with the surrounding encrypted files.

Dependencies and integration points: `configfile parser`, `test password/masterkey`, `neighboring encrypted fixture files`

Risks: editing flags, salts, or encrypted key material can invalidate historical compatibility expectations.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/example_filesystems/v1.1-reverse/.gocryptfs.reverse.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/example_filesystems/v1.3-reverse/.gocryptfs.reverse.conf -->
# sources/security-integrity/gocryptfs/tests/example_filesystems/v1.3-reverse/.gocryptfs.reverse.conf

Purpose: Historical or intentionally broken gocryptfs JSON configuration fixture used by compatibility, fsck, or HKDF sanity tests.

Important APIs and types: JSON fixture fields: Creator=gocryptfs v1.3, Version=2, Scrypt N=65536, FeatureFlags=['GCMIV128', 'HKDF', 'DirIV', 'EMENames', 'LongNames', 'Raw64', 'AESSIV'].

Control flow: There is no executable flow. Compatibility and fsck tests load this fixture through gocryptfs config parsing, decrypt with the known test password or master key, and compare behavior with adjacent ciphertext fixture files. Reverse mode tests and fixtures protect deterministic encrypted-view behavior and the AES-SIV requirement for safe reverse mounts. HKDF flags are compatibility-critical because content and name key derivation changes must not be silently ignored. This JSON fixture stores encrypted key metadata with Scrypt N=65536, Version=2, Creator=gocryptfs v1.3, FeatureFlags=['GCMIV128', 'HKDF', 'DirIV', 'EMENames', 'LongNames', 'Raw64', 'AESSIV'].

State and persistence behavior: Checked-in persistent encrypted master-key metadata and feature flags. The fixture must remain byte-compatible with the surrounding encrypted files.

Dependencies and integration points: `configfile parser`, `test password/masterkey`, `neighboring encrypted fixture files`

Risks: editing flags, salts, or encrypted key material can invalidate historical compatibility expectations.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/example_filesystems/v1.3-reverse/.gocryptfs.reverse.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/example_filesystems/v1.3/gocryptfs.conf -->
# sources/security-integrity/gocryptfs/tests/example_filesystems/v1.3/gocryptfs.conf

Purpose: Historical or intentionally broken gocryptfs JSON configuration fixture used by compatibility, fsck, or HKDF sanity tests.

Important APIs and types: JSON fixture fields: Creator=gocryptfs v1.2.1-23-gd78a8d1-dirty, Version=2, Scrypt N=1024, FeatureFlags=['GCMIV128', 'DirIV', 'EMENames', 'LongNames', 'Raw64', 'HKDF'].

Control flow: There is no executable flow. Compatibility and fsck tests load this fixture through gocryptfs config parsing, decrypt with the known test password or master key, and compare behavior with adjacent ciphertext fixture files. HKDF flags are compatibility-critical because content and name key derivation changes must not be silently ignored. This JSON fixture stores encrypted key metadata with Scrypt N=1024, Version=2, Creator=gocryptfs v1.2.1-23-gd78a8d1-dirty, FeatureFlags=['GCMIV128', 'DirIV', 'EMENames', 'LongNames', 'Raw64', 'HKDF'].

State and persistence behavior: Checked-in persistent encrypted master-key metadata and feature flags. The fixture must remain byte-compatible with the surrounding encrypted files.

Dependencies and integration points: `configfile parser`, `test password/masterkey`, `neighboring encrypted fixture files`

Risks: editing flags, salts, or encrypted key material can invalidate historical compatibility expectations.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/example_filesystems/v1.3/gocryptfs.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/example_filesystems/v2.2-deterministic-names/gocryptfs.conf -->
# sources/security-integrity/gocryptfs/tests/example_filesystems/v2.2-deterministic-names/gocryptfs.conf

Purpose: Historical or intentionally broken gocryptfs JSON configuration fixture used by compatibility, fsck, or HKDF sanity tests.

Important APIs and types: JSON fixture fields: Creator=gocryptfs v2.1-27-gabaa129-dirty.xchacha, Version=2, Scrypt N=1024, FeatureFlags=['HKDF', 'GCMIV128', 'EMENames', 'LongNames', 'Raw64'].

Control flow: There is no executable flow. Compatibility and fsck tests load this fixture through gocryptfs config parsing, decrypt with the known test password or master key, and compare behavior with adjacent ciphertext fixture files. HKDF flags are compatibility-critical because content and name key derivation changes must not be silently ignored. This JSON fixture stores encrypted key metadata with Scrypt N=1024, Version=2, Creator=gocryptfs v2.1-27-gabaa129-dirty.xchacha, FeatureFlags=['HKDF', 'GCMIV128', 'EMENames', 'LongNames', 'Raw64'].

State and persistence behavior: Checked-in persistent encrypted master-key metadata and feature flags. The fixture must remain byte-compatible with the surrounding encrypted files.

Dependencies and integration points: `configfile parser`, `test password/masterkey`, `neighboring encrypted fixture files`

Risks: editing flags, salts, or encrypted key material can invalidate historical compatibility expectations.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/example_filesystems/v2.2-deterministic-names/gocryptfs.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/example_filesystems/v2.2-xchacha-deterministic-names/gocryptfs.conf -->
# sources/security-integrity/gocryptfs/tests/example_filesystems/v2.2-xchacha-deterministic-names/gocryptfs.conf

Purpose: Historical or intentionally broken gocryptfs JSON configuration fixture used by compatibility, fsck, or HKDF sanity tests.

Important APIs and types: JSON fixture fields: Creator=gocryptfs v2.1-27-gabaa129-dirty.xchacha, Version=2, Scrypt N=1024, FeatureFlags=['HKDF', 'XChaCha20Poly1305', 'EMENames', 'LongNames', 'Raw64'].

Control flow: There is no executable flow. Compatibility and fsck tests load this fixture through gocryptfs config parsing, decrypt with the known test password or master key, and compare behavior with adjacent ciphertext fixture files. HKDF flags are compatibility-critical because content and name key derivation changes must not be silently ignored. This JSON fixture stores encrypted key metadata with Scrypt N=1024, Version=2, Creator=gocryptfs v2.1-27-gabaa129-dirty.xchacha, FeatureFlags=['HKDF', 'XChaCha20Poly1305', 'EMENames', 'LongNames', 'Raw64'].

State and persistence behavior: Checked-in persistent encrypted master-key metadata and feature flags. The fixture must remain byte-compatible with the surrounding encrypted files.

Dependencies and integration points: `configfile parser`, `test password/masterkey`, `neighboring encrypted fixture files`

Risks: editing flags, salts, or encrypted key material can invalidate historical compatibility expectations.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/example_filesystems/v2.2-xchacha-deterministic-names/gocryptfs.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/example_filesystems/v2.2-xchacha/gocryptfs.conf -->
# sources/security-integrity/gocryptfs/tests/example_filesystems/v2.2-xchacha/gocryptfs.conf

Purpose: Historical or intentionally broken gocryptfs JSON configuration fixture used by compatibility, fsck, or HKDF sanity tests.

Important APIs and types: JSON fixture fields: Creator=gocryptfs v2.1-27-gabaa129-dirty.xchacha, Version=2, Scrypt N=1024, FeatureFlags=['HKDF', 'XChaCha20Poly1305', 'DirIV', 'EMENames', 'LongNames', 'Raw64'].

Control flow: There is no executable flow. Compatibility and fsck tests load this fixture through gocryptfs config parsing, decrypt with the known test password or master key, and compare behavior with adjacent ciphertext fixture files. HKDF flags are compatibility-critical because content and name key derivation changes must not be silently ignored. This JSON fixture stores encrypted key metadata with Scrypt N=1024, Version=2, Creator=gocryptfs v2.1-27-gabaa129-dirty.xchacha, FeatureFlags=['HKDF', 'XChaCha20Poly1305', 'DirIV', 'EMENames', 'LongNames', 'Raw64'].

State and persistence behavior: Checked-in persistent encrypted master-key metadata and feature flags. The fixture must remain byte-compatible with the surrounding encrypted files.

Dependencies and integration points: `configfile parser`, `test password/masterkey`, `neighboring encrypted fixture files`

Risks: editing flags, salts, or encrypted key material can invalidate historical compatibility expectations.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/example_filesystems/v2.2-xchacha/gocryptfs.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/fsck/broken_fs_v1.4/gocryptfs.conf -->
# sources/security-integrity/gocryptfs/tests/fsck/broken_fs_v1.4/gocryptfs.conf

Purpose: Historical or intentionally broken gocryptfs JSON configuration fixture used by compatibility, fsck, or HKDF sanity tests.

Important APIs and types: JSON fixture fields: Creator=gocryptfs v1.4.4-13-ga4f3a7d-dirty, Version=2, Scrypt N=65536, FeatureFlags=['GCMIV128', 'HKDF', 'DirIV', 'EMENames', 'LongNames', 'Raw64'].

Control flow: There is no executable flow. Compatibility and fsck tests load this fixture through gocryptfs config parsing, decrypt with the known test password or master key, and compare behavior with adjacent ciphertext fixture files. HKDF flags are compatibility-critical because content and name key derivation changes must not be silently ignored. This JSON fixture stores encrypted key metadata with Scrypt N=65536, Version=2, Creator=gocryptfs v1.4.4-13-ga4f3a7d-dirty, FeatureFlags=['GCMIV128', 'HKDF', 'DirIV', 'EMENames', 'LongNames', 'Raw64'].

State and persistence behavior: Checked-in persistent encrypted master-key metadata and feature flags. The fixture must remain byte-compatible with the surrounding encrypted files.

Dependencies and integration points: `configfile parser`, `test password/masterkey`, `neighboring encrypted fixture files`

Risks: editing flags, salts, or encrypted key material can invalidate historical compatibility expectations.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/fsck/broken_fs_v1.4/gocryptfs.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/fsck/fsck_test.go -->
# sources/security-integrity/gocryptfs/tests/fsck/fsck_test.go

Purpose: Integration or regression test file in the fsck tests suite.

Important APIs and types: package `fsck`; functions/tests `dec64`, `TestBrokenFsV14`, `TestMalleableBase64`, `TestExampleFses`, `TestTerabyteFile`; key imports `encoding/base64`, `os`, `os/exec`, `runtime`, `strings`, `syscall`, `testing`, `time`, `github.com/pkg/xattr`, `github.com/rfjakob/gocryptfs/v2/internal/exitcodes`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `encoding/base64`, `os`, `os/exec`, `runtime`, `strings`, `syscall`, `testing`, `time`, `github.com/pkg/xattr`, `github.com/rfjakob/gocryptfs/v2/internal/exitcodes`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Risks: panic paths are intentional for programmer errors but must not be reachable from untrusted malformed ciphertext except where tests expect ordinary errors; platform syscall semantics and kernel/FUSE differences can change behavior; some checks are timing-sensitive.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/fsck/fsck_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/fsck/malleable_base64/gocryptfs.conf -->
# sources/security-integrity/gocryptfs/tests/fsck/malleable_base64/gocryptfs.conf

Purpose: Historical or intentionally broken gocryptfs JSON configuration fixture used by compatibility, fsck, or HKDF sanity tests.

Important APIs and types: JSON fixture fields: Creator=gocryptfs v2.4.0-dirty, Version=2, Scrypt N=1024, FeatureFlags=['HKDF', 'GCMIV128', 'DirIV', 'EMENames', 'LongNames', 'Raw64'].

Control flow: There is no executable flow. Compatibility and fsck tests load this fixture through gocryptfs config parsing, decrypt with the known test password or master key, and compare behavior with adjacent ciphertext fixture files. HKDF flags are compatibility-critical because content and name key derivation changes must not be silently ignored. This JSON fixture stores encrypted key metadata with Scrypt N=1024, Version=2, Creator=gocryptfs v2.4.0-dirty, FeatureFlags=['HKDF', 'GCMIV128', 'DirIV', 'EMENames', 'LongNames', 'Raw64'].

State and persistence behavior: Checked-in persistent encrypted master-key metadata and feature flags. The fixture must remain byte-compatible with the surrounding encrypted files.

Dependencies and integration points: `configfile parser`, `test password/masterkey`, `neighboring encrypted fixture files`

Risks: editing flags, salts, or encrypted key material can invalidate historical compatibility expectations.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/fsck/malleable_base64/gocryptfs.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/fuse-unmount.bash -->
# sources/security-integrity/gocryptfs/tests/fuse-unmount.bash

Purpose: Shell utility in the shell harness area for testing, benchmarking, profiling, packaging, or cleanup.

Important APIs and types: Shell entry points `fuse-unmount`. External commands observed: fusermount, umount, dd, ls, rm.

Control flow: The script runs in strict shell mode where present, prepares paths or validates arguments, invokes gocryptfs or filesystem utilities, and relies on exit status for success/failure.

State and persistence behavior: May create temporary directories, lock files, mounts, release tarballs, profile files, benchmark data, or downloaded tarballs; cleanup is handled by traps or later harness steps when present.

Dependencies and integration points: `fusermount`, `umount`, `dd`, `ls`, `rm`

Risks: scripts are environment-sensitive and can leave mounts or temporary files if interrupted before cleanup.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/fuse-unmount.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/hkdf_sanity/broken_content/gocryptfs.conf -->
# sources/security-integrity/gocryptfs/tests/hkdf_sanity/broken_content/gocryptfs.conf

Purpose: Historical or intentionally broken gocryptfs JSON configuration fixture used by compatibility, fsck, or HKDF sanity tests.

Important APIs and types: JSON fixture fields: Creator=gocryptfs v1.2.1-32-g14038a1-dirty, Version=2, Scrypt N=1024, FeatureFlags=['GCMIV128', 'HKDF', 'PlaintextNames'].

Control flow: There is no executable flow. Compatibility and fsck tests load this fixture through gocryptfs config parsing, decrypt with the known test password or master key, and compare behavior with adjacent ciphertext fixture files. HKDF flags are compatibility-critical because content and name key derivation changes must not be silently ignored. This JSON fixture stores encrypted key metadata with Scrypt N=1024, Version=2, Creator=gocryptfs v1.2.1-32-g14038a1-dirty, FeatureFlags=['GCMIV128', 'HKDF', 'PlaintextNames'].

State and persistence behavior: Checked-in persistent encrypted master-key metadata and feature flags. The fixture must remain byte-compatible with the surrounding encrypted files.

Dependencies and integration points: `configfile parser`, `test password/masterkey`, `neighboring encrypted fixture files`

Risks: editing flags, salts, or encrypted key material can invalidate historical compatibility expectations.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/hkdf_sanity/broken_content/gocryptfs.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/hkdf_sanity/broken_names/gocryptfs.conf -->
# sources/security-integrity/gocryptfs/tests/hkdf_sanity/broken_names/gocryptfs.conf

Purpose: Historical or intentionally broken gocryptfs JSON configuration fixture used by compatibility, fsck, or HKDF sanity tests.

Important APIs and types: JSON fixture fields: Creator=gocryptfs v1.2.1-32-g14038a1-dirty, Version=2, Scrypt N=1024, FeatureFlags=['GCMIV128', 'HKDF', 'DirIV', 'EMENames', 'LongNames', 'Raw64'].

Control flow: There is no executable flow. Compatibility and fsck tests load this fixture through gocryptfs config parsing, decrypt with the known test password or master key, and compare behavior with adjacent ciphertext fixture files. HKDF flags are compatibility-critical because content and name key derivation changes must not be silently ignored. This JSON fixture stores encrypted key metadata with Scrypt N=1024, Version=2, Creator=gocryptfs v1.2.1-32-g14038a1-dirty, FeatureFlags=['GCMIV128', 'HKDF', 'DirIV', 'EMENames', 'LongNames', 'Raw64'].

State and persistence behavior: Checked-in persistent encrypted master-key metadata and feature flags. The fixture must remain byte-compatible with the surrounding encrypted files.

Dependencies and integration points: `configfile parser`, `test password/masterkey`, `neighboring encrypted fixture files`

Risks: editing flags, salts, or encrypted key material can invalidate historical compatibility expectations.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/hkdf_sanity/broken_names/gocryptfs.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/hkdf_sanity/sanity_test.go -->
# sources/security-integrity/gocryptfs/tests/hkdf_sanity/sanity_test.go

Purpose: Integration or regression test file in the hkdf sanity tests suite.

Important APIs and types: package `hkdf_sanity`; functions/tests `TestBrokenContent`, `TestBrokenNames`; key imports `os`, `testing`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. HKDF flags are compatibility-critical because content and name key derivation changes must not be silently ignored.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `os`, `testing`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Risks: panic paths are intentional for programmer errors but must not be reachable from untrusted malformed ciphertext except where tests expect ordinary errors.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/hkdf_sanity/sanity_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/issue893.sh -->
# sources/security-integrity/gocryptfs/tests/issue893.sh

Purpose: Shell utility in the shell harness area for testing, benchmarking, profiling, packaging, or cleanup.

Important APIs and types: Shell entry points `work`. External commands observed: gocryptfs, rm.

Control flow: The script runs in strict shell mode where present, prepares paths or validates arguments, invokes gocryptfs or filesystem utilities, and relies on exit status for success/failure.

State and persistence behavior: May create temporary directories, lock files, mounts, release tarballs, profile files, benchmark data, or downloaded tarballs; cleanup is handled by traps or later harness steps when present.

Dependencies and integration points: `gocryptfs`, `rm`

Risks: scripts are environment-sensitive and can leave mounts or temporary files if interrupted before cleanup.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/issue893.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/len2elen.sh -->
# sources/security-integrity/gocryptfs/tests/len2elen.sh

Purpose: Shell utility in the shell harness area for testing, benchmarking, profiling, packaging, or cleanup.

Important APIs and types: Shell entry points script main body. External commands observed: gocryptfs, ls, rm.

Control flow: The script runs in strict shell mode where present, prepares paths or validates arguments, invokes gocryptfs or filesystem utilities, and relies on exit status for success/failure.

State and persistence behavior: May create temporary directories, lock files, mounts, release tarballs, profile files, benchmark data, or downloaded tarballs; cleanup is handled by traps or later harness steps when present.

Dependencies and integration points: `gocryptfs`, `ls`, `rm`

Risks: scripts are environment-sensitive and can leave mounts or temporary files if interrupted before cleanup.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/len2elen.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/matrix/atime_darwin+freebsd.go -->
# sources/security-integrity/gocryptfs/tests/matrix/atime_darwin+freebsd.go

Purpose: Integration or regression test file in the matrix tests suite.

Important APIs and types: build tags: darwin || freebsd; package `matrix`; functions/tests `extractAtimeMtime`; key imports `syscall`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `syscall`

Risks: platform syscall semantics and kernel/FUSE differences can change behavior.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/matrix/atime_darwin+freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/matrix/atime_linux.go -->
# sources/security-integrity/gocryptfs/tests/matrix/atime_linux.go

Purpose: Integration or regression test file in the matrix tests suite.

Important APIs and types: package `matrix`; functions/tests `extractAtimeMtime`; key imports `syscall`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `syscall`

Risks: platform syscall semantics and kernel/FUSE differences can change behavior.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/matrix/atime_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/matrix/concurrency_test.go -->
# sources/security-integrity/gocryptfs/tests/matrix/concurrency_test.go

Purpose: Integration or regression test file in the matrix tests suite.

Important APIs and types: package `matrix`; functions/tests `TestConcurrentReadWrite`, `TestConcurrentReadCreate`, `TestInoReuse`; key imports `bytes`, `io`, `log`, `os`, `sync`, `syscall`, `testing`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `bytes`, `io`, `log`, `os`, `sync`, `syscall`, `testing`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Risks: platform syscall semantics and kernel/FUSE differences can change behavior.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/matrix/concurrency_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/matrix/dir_test.go -->
# sources/security-integrity/gocryptfs/tests/matrix/dir_test.go

Purpose: Integration or regression test file in the matrix tests suite.

Important APIs and types: package `matrix`; functions/tests `TestMkdirRmdir`, `TestDirOverwrite`, `TestRmdirPerms`, `TestHaveDotdot`, `Test555Dir`; key imports `fmt`, `os`, `os/exec`, `syscall`, `testing`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `fmt`, `os`, `os/exec`, `syscall`, `testing`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Risks: platform syscall semantics and kernel/FUSE differences can change behavior.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/matrix/dir_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/matrix/fallocate_test.go -->
# sources/security-integrity/gocryptfs/tests/matrix/fallocate_test.go

Purpose: Integration or regression test file in the matrix tests suite.

Important APIs and types: package `matrix`; functions/tests `isWellKnownFS`, `TestFallocate`; constants `FALLOC_DEFAULT`, `FALLOC_FL_KEEP_SIZE`; key imports `os`, `runtime`, `syscall`, `testing`, `github.com/rfjakob/gocryptfs/v2/internal/syscallcompat`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. Preallocation behavior protects against ENOSPC-induced ciphertext corruption on Linux but is weaker or unavailable on Darwin/FreeBSD and quirky filesystems.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `os`, `runtime`, `syscall`, `testing`, `github.com/rfjakob/gocryptfs/v2/internal/syscallcompat`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Risks: panic paths are intentional for programmer errors but must not be reachable from untrusted malformed ciphertext except where tests expect ordinary errors; platform syscall semantics and kernel/FUSE differences can change behavior; some checks are timing-sensitive.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/matrix/fallocate_test.go -->
