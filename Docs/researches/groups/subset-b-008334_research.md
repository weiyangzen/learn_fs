# subset-b-008334 research

Grouped source-tree-aligned research for the assigned gocryptfs security/integrity files. Each section is wrapped for deterministic reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/contentenc/offsets.go -->
# sources/security-integrity/gocryptfs/internal/contentenc/offsets.go

- Purpose: Maps plaintext offsets, ciphertext offsets, block numbers, and logical file sizes for encrypted content blocks. It is the arithmetic layer that keeps header bytes and per-block authentication overhead out of the plaintext view.
- Important APIs/types/functions: `func (be *ContentEnc) PlainOffToBlockNo(plainOffset uint64) uint64`, `func (be *ContentEnc) CipherOffToBlockNo(cipherOffset uint64) uint64`, `func (be *ContentEnc) BlockNoToCipherOff(blockNo uint64) uint64`, `func (be *ContentEnc) BlockNoToPlainOff(blockNo uint64) uint64`, `func (be *ContentEnc) CipherSizeToPlainSize(cipherSize uint64) uint64`, `func (be *ContentEnc) PlainSizeToCipherSize(plainSize uint64) uint64`, `func (be *ContentEnc) PlainOffToCipherOff(plainOff uint64) uint64`, `func (be *ContentEnc) ExplodePlainRange(offset uint64, length uint64) []IntraBlock`, `func (be *ContentEnc) ExplodeCipherRange(offset uint64, length uint64) []IntraBlock`, `func (be *ContentEnc) BlockOverhead() uint64`, `func MinUint64(x uint64, y uint64) uint64`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; transforms data through encryption/decryption boundaries; treats invalid internal invariants as fatal/panic conditions. Source size is 4868 bytes across 154 lines, read as part of this work item.
- Dependencies and integration points: standard library: log; external/internal modules: github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/contentenc/offsets.go` and the declarations listed above.
- Risks and review notes: main risk is compatibility drift because nearby packages depend on these small constants/helpers.
- Test signals: Nearby test signal: `sources/security-integrity/gocryptfs/internal/contentenc/offsets_test.go` covers related behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/contentenc/offsets.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/contentenc/offsets_test.go -->
# sources/security-integrity/gocryptfs/internal/contentenc/offsets_test.go

- Purpose: Exercises size and offset conversion monotonicity over a small range, printing boundary points where ciphertext/header overhead changes the mapping.
- Important APIs/types/functions: `func TestSizeToSize(t *testing.T)`.
- Control flow and state: transforms data through encryption/decryption boundaries; is non-persistent test/benchmark code. Source size is 1436 bytes across 54 lines, read as part of this work item.
- Dependencies and integration points: standard library: fmt, testing; external/internal modules: github.com/rfjakob/gocryptfs/v2/internal/cryptocore. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/contentenc/offsets_test.go` and the declarations listed above.
- Risks and review notes: test/helper code can mask regressions if expected constants or environment assumptions drift.
- Test signals: Direct test/benchmark declarations: TestSizeToSize.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/contentenc/offsets_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/cryptocore/cryptocore.go -->
# sources/security-integrity/gocryptfs/internal/cryptocore/cryptocore.go

- Purpose: Constructs the low-level crypto core: filename EME, content AEAD backend selection, HKDF key separation, nonce generator setup, and best-effort key wiping.
- Important APIs/types/functions: `type AEADTypeEnum struct`, `type CryptoCore struct`, `type wiper interface`, `const (`, `var BackendOpenSSL = AEADTypeEnum"AES-GCM-256", "OpenSSL", 16}`, `var BackendGoGCM = AEADTypeEnum"AES-GCM-256", "Go", 16}`, `var BackendAESSIV = AEADTypeEnum"AES-SIV-512", "Go", siv_aead.NonceSize}`, `var BackendXChaCha20Poly1305 = AEADTypeEnum"XChaCha20-Poly1305", "Go", chacha20poly1305.NonceSizeX}`, `var BackendXChaCha20Poly1305OpenSSL = AEADTypeEnum"XChaCha20-Poly1305", "OpenSSL", chacha20poly1305.NonceSizeX}`, `func (a AEADTypeEnum) String() string`, `func New(key []byte, aeadType AEADTypeEnum, IVBitLen int, useHKDF bool) *CryptoCore`, `func (c *CryptoCore) Wipe()`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; transforms data through encryption/decryption boundaries; treats invalid internal invariants as fatal/panic conditions. Source size is 7264 bytes across 230 lines, read as part of this work item.
- Dependencies and integration points: standard library: crypto/aes, crypto/cipher, crypto/sha512, log, runtime; external/internal modules: golang.org/x/crypto/chacha20poly1305, github.com/rfjakob/eme, github.com/rfjakob/gocryptfs/v2/internal/siv_aead, github.com/rfjakob/gocryptfs/v2/internal/stupidgcm, github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/cryptocore/cryptocore.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable.
- Test signals: Nearby test signal: `sources/security-integrity/gocryptfs/internal/cryptocore/cryptocore_test.go` covers related behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/cryptocore/cryptocore.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/cryptocore/cryptocore_test.go -->
# sources/security-integrity/gocryptfs/internal/cryptocore/cryptocore_test.go

- Purpose: Test coverage for sources/security-integrity/gocryptfs/internal/cryptocore, centered on TestCryptoCoreNew, TestNewPanic. It records expected compatibility, error, and boundary behavior for the implementation files nearby.
- Important APIs/types/functions: `func TestCryptoCoreNew(t *testing.T)`, `func TestNewPanic(t *testing.T)`.
- Control flow and state: treats invalid internal invariants as fatal/panic conditions; is non-persistent test/benchmark code. Source size is 812 bytes across 42 lines, read as part of this work item.
- Dependencies and integration points: standard library: testing; external/internal modules: github.com/rfjakob/gocryptfs/v2/internal/stupidgcm. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/cryptocore/cryptocore_test.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable; test/helper code can mask regressions if expected constants or environment assumptions drift.
- Test signals: Direct test/benchmark declarations: TestCryptoCoreNew, TestNewPanic.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/cryptocore/cryptocore_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/cryptocore/hkdf.go -->
# sources/security-integrity/gocryptfs/internal/cryptocore/hkdf.go

- Purpose: Provides HKDF-SHA256 domain-separated key derivation for filename, GCM, SIV, and XChaCha20-Poly1305 uses.
- Important APIs/types/functions: `const (`, `func hkdfDerive(masterkey []byte, info string, outLen int) []byte`.
- Control flow and state: transforms data through encryption/decryption boundaries; treats invalid internal invariants as fatal/panic conditions. Source size is 845 bytes across 28 lines, read as part of this work item.
- Dependencies and integration points: standard library: crypto/hkdf, crypto/sha256, log. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/cryptocore/hkdf.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable.
- Test signals: Nearby test signal: `sources/security-integrity/gocryptfs/internal/cryptocore/hkdf_test.go` covers related behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/cryptocore/hkdf.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/cryptocore/hkdf_test.go -->
# sources/security-integrity/gocryptfs/internal/cryptocore/hkdf_test.go

- Purpose: Test coverage for sources/security-integrity/gocryptfs/internal/cryptocore, centered on TestHkdfDerive. It records expected compatibility, error, and boundary behavior for the implementation files nearby.
- Important APIs/types/functions: `type hkdfTestCase struct`, `func TestHkdfDerive(t *testing.T)`.
- Control flow and state: transforms data through encryption/decryption boundaries; is non-persistent test/benchmark code. Source size is 1467 bytes across 47 lines, read as part of this work item.
- Dependencies and integration points: standard library: bytes, encoding/hex, testing. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/cryptocore/hkdf_test.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable; test/helper code can mask regressions if expected constants or environment assumptions drift.
- Test signals: Direct test/benchmark declarations: TestHkdfDerive.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/cryptocore/hkdf_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/cryptocore/nonce.go -->
# sources/security-integrity/gocryptfs/internal/cryptocore/nonce.go

- Purpose: Provides secure random byte and uint64 helpers plus nonce generation backed by the package-level prefetcher.
- Important APIs/types/functions: `type nonceGenerator struct`, `func RandBytes(n int) []byte`, `func RandUint64() uint64`, `func (n *nonceGenerator) Get() []byte`.
- Control flow and state: treats invalid internal invariants as fatal/panic conditions. Source size is 738 bytes across 35 lines, read as part of this work item.
- Dependencies and integration points: standard library: crypto/rand, encoding/binary, log. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/cryptocore/nonce.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/cryptocore/nonce.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/cryptocore/randprefetch.go -->
# sources/security-integrity/gocryptfs/internal/cryptocore/randprefetch.go

- Purpose: Maintains a background random-byte prefetch buffer so frequent nonce generation does not synchronously hit crypto/rand for every nonce.
- Important APIs/types/functions: `type randPrefetcherT struct`, `const prefetchN = 512`, `var randPrefetcher randPrefetcherT`, `func init()`, `func (r *randPrefetcherT) read(want int) (out []byte)`, `func (r *randPrefetcherT) refillWorker()`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; treats invalid internal invariants as fatal/panic conditions. Source size is 1150 bytes across 56 lines, read as part of this work item.
- Dependencies and integration points: standard library: bytes, log, sync. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/cryptocore/randprefetch.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable; shared mutable state needs race-free registration, cleanup, and bounded resource use.
- Test signals: Nearby test signal: `sources/security-integrity/gocryptfs/internal/cryptocore/randprefetch_test.go` covers related behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/cryptocore/randprefetch.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/cryptocore/randprefetch_test.go -->
# sources/security-integrity/gocryptfs/internal/cryptocore/randprefetch_test.go

- Purpose: Test coverage for sources/security-integrity/gocryptfs/internal/cryptocore, centered on TestRandPrefetch, BenchmarkRandPrefetch. It records expected compatibility, error, and boundary behavior for the implementation files nearby.
- Important APIs/types/functions: `func TestRandPrefetch(t *testing.T)`, `func BenchmarkRandPrefetch(b *testing.B)`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; is non-persistent test/benchmark code. Source size is 964 bytes across 49 lines, read as part of this work item.
- Dependencies and integration points: standard library: bytes, compress/flate, runtime, sync, testing. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/cryptocore/randprefetch_test.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable; shared mutable state needs race-free registration, cleanup, and bounded resource use; test/helper code can mask regressions if expected constants or environment assumptions drift.
- Test signals: Direct test/benchmark declarations: TestRandPrefetch, BenchmarkRandPrefetch.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/cryptocore/randprefetch_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/cryptocore/randsize_test.go -->
# sources/security-integrity/gocryptfs/internal/cryptocore/randsize_test.go

- Purpose: Test coverage for sources/security-integrity/gocryptfs/internal/cryptocore, centered on BenchmarkUrandomBlocksize. It records expected compatibility, error, and boundary behavior for the implementation files nearby.
- Important APIs/types/functions: `func BenchmarkUrandomBlocksize(b *testing.B)`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; is non-persistent test/benchmark code. Source size is 1391 bytes across 42 lines, read as part of this work item.
- Dependencies and integration points: standard library: fmt, testing. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/cryptocore/randsize_test.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable; test/helper code can mask regressions if expected constants or environment assumptions drift.
- Test signals: Direct test/benchmark declarations: BenchmarkUrandomBlocksize.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/cryptocore/randsize_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/ctlsocksrv/ctlsock_listen.go -->
# sources/security-integrity/gocryptfs/internal/ctlsocksrv/ctlsock_listen.go

- Purpose: Creates a Unix control-socket listener and safely removes only stale orphan socket files before binding.
- Important APIs/types/functions: `func cleanupOrphanedSocket(path string)`, `func Listen(path string) (net.Listener, error)`.
- Control flow and state: is mostly stateless helper or interface assertion code. Source size is 977 bytes across 45 lines, read as part of this work item.
- Dependencies and integration points: standard library: errors, io/fs, net, os, syscall, time; external/internal modules: github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/ctlsocksrv/ctlsock_listen.go` and the declarations listed above.
- Risks and review notes: main risk is compatibility drift because nearby packages depend on these small constants/helpers.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/ctlsocksrv/ctlsock_listen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/ctlsocksrv/ctlsock_serve.go -->
# sources/security-integrity/gocryptfs/internal/ctlsocksrv/ctlsock_serve.go

- Purpose: Implements the JSON request/response protocol for the control socket and dispatches path encryption/decryption to the mounted frontend.
- Important APIs/types/functions: `type Interface interface`, `type ctlSockHandler struct`, `const ReadBufSize = 5000`, `func Serve(sock net.Listener, fs Interface)`, `func (ch *ctlSockHandler) acceptLoop()`, `func (ch *ctlSockHandler) handleConnection(conn *net.UnixConn)`, `func (ch *ctlSockHandler) handleRequest(in *ctlsock.RequestStruct, conn *net.UnixConn)`, `func sendResponse(conn *net.UnixConn, err error, result string, warnText string)`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; transforms data through encryption/decryption boundaries; treats invalid internal invariants as fatal/panic conditions. Source size is 4660 bytes across 164 lines, read as part of this work item.
- Dependencies and integration points: standard library: encoding/json, errors, fmt, io, net, os, syscall; external/internal modules: github.com/rfjakob/gocryptfs/v2/ctlsock, github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/ctlsocksrv/ctlsock_serve.go` and the declarations listed above.
- Risks and review notes: main risk is compatibility drift because nearby packages depend on these small constants/helpers.
- Test signals: Contains inline test/benchmark hooks or comments; package-level tests should be run for validation.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/ctlsocksrv/ctlsock_serve.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/ctlsocksrv/sanitize.go -->
# sources/security-integrity/gocryptfs/internal/ctlsocksrv/sanitize.go

- Purpose: Canonicalizes user-supplied control-socket paths for FUSE-relative use and rejects traversal above the mount root.
- Important APIs/types/functions: `func SanitizePath(path string) string`.
- Control flow and state: is mostly stateless helper or interface assertion code. Source size is 651 bytes across 34 lines, read as part of this work item.
- Dependencies and integration points: standard library: path/filepath, strings. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/ctlsocksrv/sanitize.go` and the declarations listed above.
- Risks and review notes: main risk is compatibility drift because nearby packages depend on these small constants/helpers.
- Test signals: Nearby test signal: `sources/security-integrity/gocryptfs/internal/ctlsocksrv/sanitize_test.go` covers related behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/ctlsocksrv/sanitize.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/ctlsocksrv/sanitize_test.go -->
# sources/security-integrity/gocryptfs/internal/ctlsocksrv/sanitize_test.go

- Purpose: Test coverage for sources/security-integrity/gocryptfs/internal/ctlsocksrv, centered on TestSanitizePath. It records expected compatibility, error, and boundary behavior for the implementation files nearby.
- Important APIs/types/functions: `func TestSanitizePath(t *testing.T)`.
- Control flow and state: is non-persistent test/benchmark code. Source size is 520 bytes across 31 lines, read as part of this work item.
- Dependencies and integration points: standard library: testing. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/ctlsocksrv/sanitize_test.go` and the declarations listed above.
- Risks and review notes: test/helper code can mask regressions if expected constants or environment assumptions drift.
- Test signals: Direct test/benchmark declarations: TestSanitizePath.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/ctlsocksrv/sanitize_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/ensurefds012/ensurefds012.go -->
# sources/security-integrity/gocryptfs/internal/ensurefds012/ensurefds012.go

- Purpose: Runs at package initialization to guarantee file descriptors 0, 1, and 2 are open by duplicating /dev/null if necessary.
- Important APIs/types/functions: `func init()`.
- Control flow and state: can terminate the process on unrecoverable setup or external command errors. Source size is 1461 bytes across 52 lines, read as part of this work item.
- Dependencies and integration points: standard library: os, syscall; external/internal modules: github.com/rfjakob/gocryptfs/v2/internal/exitcodes. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/ensurefds012/ensurefds012.go` and the declarations listed above.
- Risks and review notes: main risk is compatibility drift because nearby packages depend on these small constants/helpers.
- Test signals: Contains inline test/benchmark hooks or comments; package-level tests should be run for validation.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/ensurefds012/ensurefds012.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/exitcodes/exitcodes.go -->
# sources/security-integrity/gocryptfs/internal/exitcodes/exitcodes.go

- Purpose: Centralizes stable process exit codes and a small typed error wrapper that carries an exit status.
- Important APIs/types/functions: `type Err struct`, `const (`, `func NewErr(msg string, code int) Err`, `func Exit(err error)`.
- Control flow and state: transforms data through encryption/decryption boundaries; treats invalid internal invariants as fatal/panic conditions; can terminate the process on unrecoverable setup or external command errors. Source size is 3052 bytes across 100 lines, read as part of this work item.
- Dependencies and integration points: standard library: errors, os. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/exitcodes/exitcodes.go` and the declarations listed above.
- Risks and review notes: main risk is compatibility drift because nearby packages depend on these small constants/helpers.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/exitcodes/exitcodes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fido2/fido2.go -->
# sources/security-integrity/gocryptfs/internal/fido2/fido2.go

- Purpose: Wraps external libfido2 command-line tools to register credentials and derive HMAC secrets for token-assisted unlocking.
- Important APIs/types/functions: `type fidoCommand int`, `const (`, `const relyingPartyID = "gocryptfs"`, `func (fc fidoCommand) String() string`, `func callFidoCommand(command fidoCommand, assertOptions []string, device string, stdin []string) ([]string, error)`, `func Register(device string, userName string) (credentialID []byte)`, `func Secret(device string, assertOptions []string, credentialID []byte, salt []byte) (secret []byte)`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; treats invalid internal invariants as fatal/panic conditions; can terminate the process on unrecoverable setup or external command errors. Source size is 3358 bytes across 124 lines, read as part of this work item.
- Dependencies and integration points: standard library: bytes, encoding/base64, fmt, io, os, os/exec, strings; external/internal modules: github.com/rfjakob/gocryptfs/v2/internal/cryptocore, github.com/rfjakob/gocryptfs/v2/internal/exitcodes, github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fido2/fido2.go` and the declarations listed above.
- Risks and review notes: secret input handling must avoid truncation surprises, command injection assumptions, and accidental logging of sensitive material.
- Test signals: Contains inline test/benchmark hooks or comments; package-level tests should be run for validation.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fido2/fido2.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/args.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend/args.go

- Purpose: Defines the forward/reverse frontend configuration surface passed from main into FUSE operations.
- Important APIs/types/functions: `type Args struct`.
- Control flow and state: participates in directory-IV based name encryption state; handles long-name sidecar metadata and cleanup; transforms data through encryption/decryption boundaries; maps extended attributes between plaintext API names and backing storage names. Source size is 2293 bytes across 57 lines, read as part of this work item.
- Dependencies and integration points: external/internal modules: github.com/hanwen/go-fuse/v2/fuse. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend/args.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points; xattr behavior differs by platform and must preserve ACL passthrough plus encrypted user attributes.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/args.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/ctlsock_interface.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend/ctlsock_interface.go

- Purpose: Implements control-socket path translation for forward mode by walking encrypted directories level by level with diriv-aware name transforms.
- Important APIs/types/functions: `var _ ctlsocksrv.Interface = &RootNode} // Verify that interface is implemented.`, `func (rn *RootNode) EncryptPath(plainPath string) (cipherPath string, err error)`, `func (rn *RootNode) DecryptPath(cipherPath string) (plainPath string, err error)`.
- Control flow and state: participates in directory-IV based name encryption state; handles long-name sidecar metadata and cleanup; transforms data through encryption/decryption boundaries. Source size is 3048 bytes across 113 lines, read as part of this work item.
- Dependencies and integration points: standard library: path, path/filepath, strings, syscall; external/internal modules: github.com/rfjakob/gocryptfs/v2/internal/ctlsocksrv, github.com/rfjakob/gocryptfs/v2/internal/nametransform, github.com/rfjakob/gocryptfs/v2/internal/syscallcompat, github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend/ctlsock_interface.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/ctlsock_interface.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/dircache.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend/dircache.go

- Purpose: Caches opened directory file descriptors and directory IVs to reduce repeated open/read-diriv work in forward-mode path preparation.
- Important APIs/types/functions: `type dirCacheEntry struct`, `type dirCache struct`, `const (`, `func (e *dirCacheEntry) Clear()`, `func (d *dirCache) Clear()`, `func (d *dirCache) Store(node *Node, fd int, iv []byte)`, `func (d *dirCache) Lookup(node *Node) (fd int, iv []byte)`, `func (d *dirCache) expireThread()`, `func (d *dirCache) stats()`, `func (d *dirCache) dbg(format string, a ...interface`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; participates in directory-IV based name encryption state; treats invalid internal invariants as fatal/panic conditions. Source size is 4388 bytes across 183 lines, read as part of this work item.
- Dependencies and integration points: standard library: fmt, log, sync, syscall, time; external/internal modules: github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend/dircache.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points; shared mutable state needs race-free registration, cleanup, and bounded resource use.
- Test signals: Contains inline test/benchmark hooks or comments; package-level tests should be run for validation.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/dircache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/file.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend/file.go

- Purpose: Implements encrypted forward-mode file-handle operations: header creation, file-ID caching, block decrypt/read, read-modify-write encrypt/write, release, flush, fsync, and getattr.
- Important APIs/types/functions: `type File struct`, `func NewFile(fd int, cName string, rn *RootNode) (f *File, st *syscall.Stat_t, errno syscall.Errno)`, `func (f *File) intFd() int`, `func (f *File) readFileID() ([]byte, error)`, `func (f *File) createHeader() (fileID []byte, err error)`, `func (f *File) doRead(dst []byte, off uint64, length uint64) ([]byte, syscall.Errno)`, `func (f *File) Read(ctx context.Context, buf []byte, off int64) (resultData fuse.ReadResult, errno syscall.Errno)`, `func (f *File) doWrite(data []byte, off int64) (uint32, syscall.Errno)`, `func (f *File) isConsecutiveWrite(off int64) bool`, `func (f *File) Write(ctx context.Context, data []byte, off int64) (uint32, syscall.Errno)`, `func (f *File) Release(ctx context.Context) syscall.Errno`, `func (f *File) Flush(ctx context.Context) syscall.Errno` (2 more declarations in file).
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; transforms data through encryption/decryption boundaries; treats invalid internal invariants as fatal/panic conditions. Source size is 14721 bytes across 449 lines, read as part of this work item.
- Dependencies and integration points: standard library: bytes, context, encoding/hex, fmt, io, log, math, os, sync, syscall; external/internal modules: github.com/hanwen/go-fuse/v2/fs, github.com/hanwen/go-fuse/v2/fuse, github.com/rfjakob/gocryptfs/v2/internal/contentenc, github.com/rfjakob/gocryptfs/v2/internal/inomap, github.com/rfjakob/gocryptfs/v2/internal/openfiletable, github.com/rfjakob/gocryptfs/v2/internal/syscallcompat, github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend/file.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points.
- Test signals: Contains inline test/benchmark hooks or comments; package-level tests should be run for validation.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/file.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/file_allocate_truncate.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend/file_allocate_truncate.go

- Purpose: Implements FUSE fallocate and truncate over encrypted block geometry, including header creation, size translation, hole allocation, and partial-block preservation.
- Important APIs/types/functions: `const FALLOC_DEFAULT = 0x00`, `const FALLOC_FL_KEEP_SIZE = 0x01`, `var allocateWarnOnce sync.Once`, `func (f *File) Allocate(ctx context.Context, off uint64, sz uint64, mode uint32) syscall.Errno`, `func (f *File) truncate(newSize uint64) (errno syscall.Errno)`, `func (f *File) statPlainSize() (uint64, error)`, `func (f *File) truncateGrowFile(oldPlainSz uint64, newPlainSz uint64) syscall.Errno`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; transforms data through encryption/decryption boundaries; treats invalid internal invariants as fatal/panic conditions. Source size is 7119 bytes across 219 lines, read as part of this work item.
- Dependencies and integration points: standard library: context, log, sync, syscall; external/internal modules: github.com/hanwen/go-fuse/v2/fs, github.com/rfjakob/gocryptfs/v2/internal/syscallcompat, github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend/file_allocate_truncate.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/file_allocate_truncate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/file_api_check.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend/file_api_check.go

- Purpose: Implementation file in sources/security-integrity/gocryptfs/internal/fusefrontend covering the file_api_check.go slice of that package.
- Important APIs/types/functions: `var _ = (fs.FileGetattrer)((*File)(nil))`, `var _ = (fs.FileSetattrer)((*File)(nil))`, `var _ = (fs.FileReleaser)((*File)(nil))`, `var _ = (fs.FileReader)((*File)(nil))`, `var _ = (fs.FileWriter)((*File)(nil))`, `var _ = (fs.FileFsyncer)((*File)(nil))`, `var _ = (fs.FileFlusher)((*File)(nil))`, `var _ = (fs.FileAllocater)((*File)(nil))`, `var _ = (fs.FileLseeker)((*File)(nil))`, `var _ = (fs.FileGetlker)((*File)(nil))`, `var _ = (fs.FileSetlker)((*File)(nil))`, `var _ = (fs.FileSetlkwer)((*File)(nil))`.
- Control flow and state: is mostly stateless helper or interface assertion code. Source size is 613 bytes across 23 lines, read as part of this work item.
- Dependencies and integration points: external/internal modules: github.com/hanwen/go-fuse/v2/fs. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend/file_api_check.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/file_api_check.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/file_dir_ops.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend/file_dir_ops.go

- Purpose: Implements directory file-handle operations for forward mode, including encrypted readdir name filtering/decryption and dir stream lifecycle.
- Important APIs/types/functions: `type DirHandle struct`, `var _ = (fs.FileReleasedirer)((*File)(nil))`, `var _ = (fs.FileSeekdirer)((*File)(nil))`, `var _ = (fs.FileFsyncdirer)((*File)(nil))`, `var _ = (fs.FileReaddirenter)((*File)(nil))`, `func (n *Node) OpendirHandle(ctx context.Context, flags uint32) (fh fs.FileHandle, fuseFlags uint32, errno syscall.Errno)`, `func (f *File) Releasedir(ctx context.Context, flags uint32)`, `func (f *File) Seekdir(ctx context.Context, off uint64) syscall.Errno`, `func (f *File) Fsyncdir(ctx context.Context, flags uint32) syscall.Errno`, `func (f *File) Readdirent(ctx context.Context) (entry *fuse.DirEntry, errno syscall.Errno)`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; participates in directory-IV based name encryption state; handles long-name sidecar metadata and cleanup; transforms data through encryption/decryption boundaries. Source size is 4457 bytes across 178 lines, read as part of this work item.
- Dependencies and integration points: standard library: context, syscall; external/internal modules: github.com/hanwen/go-fuse/v2/fs, github.com/hanwen/go-fuse/v2/fuse, github.com/rfjakob/gocryptfs/v2/internal/configfile, github.com/rfjakob/gocryptfs/v2/internal/nametransform, github.com/rfjakob/gocryptfs/v2/internal/syscallcompat, github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend/file_dir_ops.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/file_dir_ops.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/file_holes.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend/file_holes.go

- Purpose: Handles sparse-file behavior, zero padding before holes, and SEEK_DATA/SEEK_HOLE translation between plaintext and ciphertext block layouts.
- Important APIs/types/functions: `func (f *File) writePadHole(targetOff int64) syscall.Errno`, `func (f *File) zeroPad(plainSize uint64) syscall.Errno`, `func (f *File) Lseek(ctx context.Context, off uint64, whence uint32) (uint64, syscall.Errno)`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; transforms data through encryption/decryption boundaries. Source size is 4529 bytes across 129 lines, read as part of this work item.
- Dependencies and integration points: standard library: context, runtime, syscall; external/internal modules: github.com/hanwen/go-fuse/v2/fs, github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend/file_holes.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points.
- Test signals: Contains inline test/benchmark hooks or comments; package-level tests should be run for validation.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/file_holes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/file_setattr.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend/file_setattr.go

- Purpose: Applies chmod/chown/timestamps/truncate through an open encrypted file handle while holding content locks.
- Important APIs/types/functions: `func (f *File) Setattr(ctx context.Context, in *fuse.SetAttrIn, out *fuse.AttrOut) (errno syscall.Errno)`, `func (f *File) setAttr(ctx context.Context, in *fuse.SetAttrIn) (errno syscall.Errno)`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths. Source size is 1631 bytes across 86 lines, read as part of this work item.
- Dependencies and integration points: standard library: context, syscall; external/internal modules: github.com/hanwen/go-fuse/v2/fs, github.com/hanwen/go-fuse/v2/fuse, github.com/rfjakob/gocryptfs/v2/internal/syscallcompat, github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend/file_setattr.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/file_setattr.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/node.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend/node.go

- Purpose: Implements most forward-mode node operations for lookup, stat, unlink, symlink, hardlink, rename, mknod, setattr, statfs, readlink, and fsync using symlink-safe *at calls.
- Important APIs/types/functions: `type Node struct`, `func (n *Node) Lookup(ctx context.Context, name string, out *fuse.EntryOut) (ch *fs.Inode, errno syscall.Errno)`, `func (n *Node) Getattr(ctx context.Context, f fs.FileHandle, out *fuse.AttrOut) (errno syscall.Errno)`, `func (n *Node) Access(ctx context.Context, mode uint32) syscall.Errno`, `func (n *Node) Unlink(ctx context.Context, name string) (errno syscall.Errno)`, `func (n *Node) Readlink(ctx context.Context) (out []byte, errno syscall.Errno)`, `func (n *Node) Setattr(ctx context.Context, f fs.FileHandle, in *fuse.SetAttrIn, out *fuse.AttrOut) (errno syscall.Errno)`, `func (n *Node) Statfs(ctx context.Context, out *fuse.StatfsOut) syscall.Errno`, `func (n *Node) Mknod(ctx context.Context, name string, mode, rdev uint32, out *fuse.EntryOut) (inode *fs.Inode, errno syscall.E...`, `func (n *Node) Link(ctx context.Context, target fs.InodeEmbedder, name string, out *fuse.EntryOut) (inode *fs.Inode, errno sysc...`, `func (n *Node) Symlink(ctx context.Context, target, name string, out *fuse.EntryOut) (inode *fs.Inode, errno syscall.Errno)`, `func rejectRenameFlags(flags uint32) syscall.Errno` (2 more declarations in file).
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; participates in directory-IV based name encryption state; handles long-name sidecar metadata and cleanup; transforms data through encryption/decryption boundaries. Source size is 14819 bytes across 536 lines, read as part of this work item.
- Dependencies and integration points: standard library: context, syscall; external/internal modules: golang.org/x/sys/unix, github.com/hanwen/go-fuse/v2/fs, github.com/hanwen/go-fuse/v2/fuse, github.com/rfjakob/gocryptfs/v2/internal/nametransform, github.com/rfjakob/gocryptfs/v2/internal/syscallcompat, github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend/node.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points.
- Test signals: Contains inline test/benchmark hooks or comments; package-level tests should be run for validation.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/node.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/node_api_check.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend/node_api_check.go

- Purpose: Implementation file in sources/security-integrity/gocryptfs/internal/fusefrontend covering the node_api_check.go slice of that package.
- Important APIs/types/functions: `var _ = (fs.NodeGetattrer)((*Node)(nil))`, `var _ = (fs.NodeLookuper)((*Node)(nil))`, `var _ = (fs.NodeCreater)((*Node)(nil))`, `var _ = (fs.NodeMkdirer)((*Node)(nil))`, `var _ = (fs.NodeRmdirer)((*Node)(nil))`, `var _ = (fs.NodeUnlinker)((*Node)(nil))`, `var _ = (fs.NodeReadlinker)((*Node)(nil))`, `var _ = (fs.NodeOpener)((*Node)(nil))`, `var _ = (fs.NodeOpendirer)((*Node)(nil))`, `var _ = (fs.NodeSetattrer)((*Node)(nil))`, `var _ = (fs.NodeStatfser)((*Node)(nil))`, `var _ = (fs.NodeMknoder)((*Node)(nil))` (8 more declarations in file).
- Control flow and state: maps extended attributes between plaintext API names and backing storage names. Source size is 954 bytes across 31 lines, read as part of this work item.
- Dependencies and integration points: external/internal modules: github.com/hanwen/go-fuse/v2/fs. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend/node_api_check.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points; xattr behavior differs by platform and must preserve ACL passthrough plus encrypted user attributes.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/node_api_check.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/node_dir_ops.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend/node_dir_ops.go

- Purpose: Implements forward-mode mkdir/rmdir/opendir, including diriv creation/removal choreography, long-name sidecars, permission workarounds, and empty-directory handling.
- Important APIs/types/functions: `const dsStoreName = ".DS_Store"`, `func haveDsstore(entries []fuse.DirEntry) bool`, `func (n *Node) mkdirWithIv(dirfd int, cName string, mode uint32, context *fuse.Context) error`, `func (n *Node) Mkdir(ctx context.Context, name string, mode uint32, out *fuse.EntryOut) (*fs.Inode, syscall.Errno)`, `func (n *Node) Rmdir(ctx context.Context, name string) (code syscall.Errno)`, `func (n *Node) Opendir(ctx context.Context) (errno syscall.Errno)`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; participates in directory-IV based name encryption state; handles long-name sidecar metadata and cleanup. Source size is 9315 bytes across 308 lines, read as part of this work item.
- Dependencies and integration points: standard library: context, fmt, io, runtime, syscall; external/internal modules: golang.org/x/sys/unix, github.com/hanwen/go-fuse/v2/fs, github.com/hanwen/go-fuse/v2/fuse, github.com/rfjakob/gocryptfs/v2/internal/cryptocore, github.com/rfjakob/gocryptfs/v2/internal/nametransform, github.com/rfjakob/gocryptfs/v2/internal/syscallcompat, github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend/node_dir_ops.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/node_dir_ops.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/node_helpers.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend/node_helpers.go

- Purpose: Provides shared forward-mode helpers for context extraction, node casting, symlink target decryption, size translation, path lookup, and stable child inode creation.
- Important APIs/types/functions: `func toFuseCtx(ctx context.Context) (ctx2 *fuse.Context)`, `func toNode(op fs.InodeEmbedder) *Node`, `func (n *Node) readlink(dirfd int, cName string) (out []byte, errno syscall.Errno)`, `func (n *Node) translateSize(dirfd int, cName string, out *fuse.Attr)`, `func (n *Node) Path() string`, `func (n *Node) rootNode() *RootNode`, `func (n *Node) newChild(ctx context.Context, st *syscall.Stat_t, out *fuse.EntryOut) *fs.Inode`.
- Control flow and state: transforms data through encryption/decryption boundaries. Source size is 2972 bytes across 105 lines, read as part of this work item.
- Dependencies and integration points: standard library: context, syscall; external/internal modules: github.com/hanwen/go-fuse/v2/fs, github.com/hanwen/go-fuse/v2/fuse, github.com/rfjakob/gocryptfs/v2/internal/syscallcompat, github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend/node_helpers.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points.
- Test signals: Contains inline test/benchmark hooks or comments; package-level tests should be run for validation.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/node_helpers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/node_open_create.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend/node_open_create.go

- Purpose: Implements forward-mode open/create flag rewriting, write-only permission workaround integration, long-name sidecar creation, and file-handle construction.
- Important APIs/types/functions: `func mangleOpenCreateFlags(flags uint32) (newFlags int)`, `func (n *Node) Open(ctx context.Context, flags uint32) (fh fs.FileHandle, fuseFlags uint32, errno syscall.Errno)`, `func (n *Node) Create(ctx context.Context, name string, flags uint32, mode uint32, out *fuse.EntryOut) (inode *fs.Inode, fh fs....`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; handles long-name sidecar metadata and cleanup. Source size is 4548 bytes across 140 lines, read as part of this work item.
- Dependencies and integration points: standard library: context, os, syscall; external/internal modules: github.com/hanwen/go-fuse/v2/fs, github.com/hanwen/go-fuse/v2/fuse, github.com/rfjakob/gocryptfs/v2/internal/nametransform, github.com/rfjakob/gocryptfs/v2/internal/syscallcompat, github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend/node_open_create.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points.
- Test signals: Contains inline test/benchmark hooks or comments; package-level tests should be run for validation.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/node_open_create.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/node_prepare_syscall.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend/node_prepare_syscall.go

- Purpose: Centralizes forward-mode conversion from plaintext child names to backing directory fd plus ciphertext name for symlink-safe *at syscalls.
- Important APIs/types/functions: `func (n *Node) prepareAtSyscall(child string) (dirfd int, cName string, errno syscall.Errno)`, `func (n *Node) prepareAtSyscallMyself() (dirfd int, cName string, errno syscall.Errno)`.
- Control flow and state: uses descriptor-relative syscalls to avoid path races and symlink traversal; participates in directory-IV based name encryption state; handles long-name sidecar metadata and cleanup; transforms data through encryption/decryption boundaries. Source size is 2950 bytes across 119 lines, read as part of this work item.
- Dependencies and integration points: standard library: syscall; external/internal modules: github.com/rfjakob/gocryptfs/v2/internal/tlog, github.com/hanwen/go-fuse/v2/fs, github.com/rfjakob/gocryptfs/v2/internal/syscallcompat. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend/node_prepare_syscall.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/node_prepare_syscall.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/node_xattr.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend/node_xattr.go

- Purpose: Implements frontend xattr policy: optional no-xattr mode, capability suppression, ACL passthrough, encrypted xattr names/values, and list filtering.
- Important APIs/types/functions: `var xattrStorePrefix = "user.gocryptfs."`, `var xattrCapability = "security.capability"`, `func isAcl(attr string) bool`, `func (n *Node) Getxattr(ctx context.Context, attr string, dest []byte) (uint32, syscall.Errno)`, `func (n *Node) Setxattr(ctx context.Context, attr string, data []byte, flags uint32) syscall.Errno`, `func (n *Node) Removexattr(ctx context.Context, attr string) syscall.Errno`, `func (n *Node) Listxattr(ctx context.Context, dest []byte) (uint32, syscall.Errno)`.
- Control flow and state: transforms data through encryption/decryption boundaries; maps extended attributes between plaintext API names and backing storage names. Source size is 4835 bytes across 172 lines, read as part of this work item.
- Dependencies and integration points: standard library: bytes, context, strings, syscall; external/internal modules: github.com/hanwen/go-fuse/v2/fuse, github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend/node_xattr.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points; xattr behavior differs by platform and must preserve ACL passthrough plus encrypted user attributes.
- Test signals: Contains inline test/benchmark hooks or comments; package-level tests should be run for validation.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/node_xattr.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/node_xattr_darwin.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend/node_xattr_darwin.go

- Purpose: Implementation file in sources/security-integrity/gocryptfs/internal/fusefrontend covering the node_xattr_darwin.go slice of that package.
- Important APIs/types/functions: `const noSuchAttributeError = syscall.ENOATTR`, `func filterXattrSetFlags(flags int) int`, `func (n *Node) getXAttr(cAttr string) (out []byte, errno syscall.Errno)`, `func (n *Node) setXAttr(context *fuse.Context, cAttr string, cData []byte, flags uint32) (errno syscall.Errno)`, `func (n *Node) removeXAttr(cAttr string) (errno syscall.Errno)`, `func (n *Node) listXAttr() (out []string, errno syscall.Errno)`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; maps extended attributes between plaintext API names and backing storage names. Source size is 3029 bytes across 111 lines, read as part of this work item.
- Dependencies and integration points: standard library: syscall; external/internal modules: golang.org/x/sys/unix, github.com/hanwen/go-fuse/v2/fs, github.com/hanwen/go-fuse/v2/fuse, github.com/rfjakob/gocryptfs/v2/internal/syscallcompat. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend/node_xattr_darwin.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points; xattr behavior differs by platform and must preserve ACL passthrough plus encrypted user attributes.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/node_xattr_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/node_xattr_freebsd.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend/node_xattr_freebsd.go

- Purpose: Implementation file in sources/security-integrity/gocryptfs/internal/fusefrontend covering the node_xattr_freebsd.go slice of that package.
- Important APIs/types/functions: `const noSuchAttributeError = unix.ENOATTR`, `func filterXattrSetFlags(flags int) int`, `func (n *Node) getXAttr(cAttr string) (out []byte, errno unix.Errno)`, `func (n *Node) setXAttr(context *fuse.Context, cAttr string, cData []byte, flags uint32) (errno unix.Errno)`, `func (n *Node) removeXAttr(cAttr string) (errno unix.Errno)`, `func (n *Node) listXAttr() (out []string, errno unix.Errno)`.
- Control flow and state: maps extended attributes between plaintext API names and backing storage names. Source size is 657 bytes across 34 lines, read as part of this work item.
- Dependencies and integration points: external/internal modules: golang.org/x/sys/unix, github.com/hanwen/go-fuse/v2/fuse. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend/node_xattr_freebsd.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points; xattr behavior differs by platform and must preserve ACL passthrough plus encrypted user attributes.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/node_xattr_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/node_xattr_linux.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend/node_xattr_linux.go

- Purpose: Implementation file in sources/security-integrity/gocryptfs/internal/fusefrontend covering the node_xattr_linux.go slice of that package.
- Important APIs/types/functions: `const noSuchAttributeError = syscall.ENODATA`, `func filterXattrSetFlags(flags int) int`, `func (n *Node) getXAttr(cAttr string) (out []byte, errno syscall.Errno)`, `func (n *Node) setXAttr(context *fuse.Context, cAttr string, cData []byte, flags uint32) (errno syscall.Errno)`, `func (n *Node) removeXAttr(cAttr string) (errno syscall.Errno)`, `func (n *Node) listXAttr() (out []string, errno syscall.Errno)`.
- Control flow and state: maps extended attributes between plaintext API names and backing storage names. Source size is 1783 bytes across 74 lines, read as part of this work item.
- Dependencies and integration points: standard library: fmt, syscall; external/internal modules: golang.org/x/sys/unix, github.com/hanwen/go-fuse/v2/fs, github.com/hanwen/go-fuse/v2/fuse, github.com/rfjakob/gocryptfs/v2/internal/syscallcompat. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend/node_xattr_linux.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points; xattr behavior differs by platform and must preserve ACL passthrough plus encrypted user attributes.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/node_xattr_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/prepare_syscall_test.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend/prepare_syscall_test.go

- Purpose: Test coverage for sources/security-integrity/gocryptfs/internal/fusefrontend, centered on TestPrepareAtSyscall, TestPrepareAtSyscallPlaintextnames. It records expected compatibility, error, and boundary behavior for the implementation files nearby.
- Important APIs/types/functions: `func TestPrepareAtSyscall(t *testing.T)`, `func TestPrepareAtSyscallPlaintextnames(t *testing.T)`.
- Control flow and state: transforms data through encryption/decryption boundaries; treats invalid internal invariants as fatal/panic conditions; is non-persistent test/benchmark code. Source size is 3762 bytes across 174 lines, read as part of this work item.
- Dependencies and integration points: standard library: context, strings, syscall, testing; external/internal modules: golang.org/x/sys/unix, github.com/hanwen/go-fuse/v2/fuse, github.com/rfjakob/gocryptfs/v2/internal/syscallcompat, github.com/rfjakob/gocryptfs/v2/tests/test_helpers. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend/prepare_syscall_test.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points; test/helper code can mask regressions if expected constants or environment assumptions drift.
- Test signals: Direct test/benchmark declarations: TestPrepareAtSyscall, TestPrepareAtSyscallPlaintextnames.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/prepare_syscall_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/root_node.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend/root_node.go

- Purpose: Defines the forward-mode root node and shared state for name/content transforms, inode mapping, diriv locks, directory cache, quirks, corruption reporting, symlink/xattr crypto, and owner/filter policy.
- Important APIs/types/functions: `type RootNode struct`, `func NewRootNode(args Args, c *contentenc.ContentEnc, n *nametransform.NameTransform) *RootNode`, `func (rn *RootNode) AfterUnmount()`, `func (rn *RootNode) reportMitigatedCorruption(item string)`, `func (rn *RootNode) isFiltered(child string) bool`, `func (rn *RootNode) decryptSymlinkTarget(cData64 string) (string, error)`, `func (rn *RootNode) openWriteOnlyFile(dirfd int, cName string, newFlags int) (rwFd int, err error)`, `func (rn *RootNode) encryptSymlinkTarget(data string) (cData64 string)`, `func (rn *RootNode) encryptXattrValue(data []byte) (cData []byte)`, `func (rn *RootNode) decryptXattrValue(cData []byte) (data []byte, err error)`, `func (rn *RootNode) encryptXattrName(attr string) (string, error)`, `func (rn *RootNode) decryptXattrName(cAttr string) (attr string, err error)` (1 more declarations in file).
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; participates in directory-IV based name encryption state; handles long-name sidecar metadata and cleanup; transforms data through encryption/decryption boundaries; maps extended attributes between plaintext API names and backing storage names. Source size is 9452 bytes across 284 lines, read as part of this work item.
- Dependencies and integration points: standard library: strings, sync, sync/atomic, syscall, time; external/internal modules: github.com/rfjakob/gocryptfs/v2/internal/configfile, github.com/rfjakob/gocryptfs/v2/internal/contentenc, github.com/rfjakob/gocryptfs/v2/internal/inomap, github.com/rfjakob/gocryptfs/v2/internal/nametransform, github.com/rfjakob/gocryptfs/v2/internal/syscallcompat, github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend/root_node.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points; xattr behavior differs by platform and must preserve ACL passthrough plus encrypted user attributes.
- Test signals: Contains inline test/benchmark hooks or comments; package-level tests should be run for validation.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/root_node.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/xattr_unit_test.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend/xattr_unit_test.go

- Purpose: Test coverage for sources/security-integrity/gocryptfs/internal/fusefrontend, centered on TestEncryptDecryptXattrName. It records expected compatibility, error, and boundary behavior for the implementation files nearby.
- Important APIs/types/functions: `func newTestFS(args Args) *RootNode`, `func TestEncryptDecryptXattrName(t *testing.T)`.
- Control flow and state: transforms data through encryption/decryption boundaries; maps extended attributes between plaintext API names and backing storage names; treats invalid internal invariants as fatal/panic conditions; is non-persistent test/benchmark code. Source size is 1224 bytes across 46 lines, read as part of this work item.
- Dependencies and integration points: standard library: testing, time; external/internal modules: github.com/hanwen/go-fuse/v2/fs, github.com/rfjakob/gocryptfs/v2/internal/contentenc, github.com/rfjakob/gocryptfs/v2/internal/cryptocore, github.com/rfjakob/gocryptfs/v2/internal/nametransform. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend/xattr_unit_test.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points; xattr behavior differs by platform and must preserve ACL passthrough plus encrypted user attributes; test/helper code can mask regressions if expected constants or environment assumptions drift.
- Test signals: Direct test/benchmark declarations: TestEncryptDecryptXattrName.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend/xattr_unit_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/ctlsock_interface.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/ctlsock_interface.go

- Purpose: Implements reverse-mode control-socket path translation between plaintext source paths and synthesized ciphertext paths.
- Important APIs/types/functions: `var _ ctlsocksrv.Interface = &RootNode}`, `func (rn *RootNode) EncryptPath(plainPath string) (string, error)`, `func (rn *RootNode) DecryptPath(cipherPath string) (string, error)`.
- Control flow and state: participates in directory-IV based name encryption state; handles long-name sidecar metadata and cleanup; transforms data through encryption/decryption boundaries. Source size is 1169 bytes across 42 lines, read as part of this work item.
- Dependencies and integration points: standard library: path/filepath, strings; external/internal modules: golang.org/x/sys/unix, github.com/rfjakob/gocryptfs/v2/internal/ctlsocksrv. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/ctlsock_interface.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/ctlsock_interface.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/excluder.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/excluder.go

- Purpose: Builds reverse-mode exclusion matchers from direct patterns and pattern files, normalizing root-relative excludes.
- Important APIs/types/functions: `func prepareExcluder(args fusefrontend.Args) *ignore.GitIgnore`, `func getExclusionPatterns(args fusefrontend.Args) []string`, `func getLines(file string) ([]string, error)`.
- Control flow and state: treats invalid internal invariants as fatal/panic conditions; can terminate the process on unrecoverable setup or external command errors. Source size is 1686 bytes across 58 lines, read as part of this work item.
- Dependencies and integration points: standard library: log, os, strings; external/internal modules: github.com/rfjakob/gocryptfs/v2/internal/exitcodes, github.com/rfjakob/gocryptfs/v2/internal/fusefrontend, github.com/rfjakob/gocryptfs/v2/internal/tlog, github.com/sabhiram/go-gitignore. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/excluder.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points.
- Test signals: Nearby test signal: `sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/excluder_test.go` covers related behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/excluder.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/excluder_test.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/excluder_test.go

- Purpose: Test coverage for sources/security-integrity/gocryptfs/internal/fusefrontend_reverse, centered on TestShouldPrefixExcludeValuesWithSlash, TestShouldReadExcludePatternsFromFiles, TestShouldReturnFalseIfThereAreNoExclusions. It records expected compatibility, error, and boundary behavior for the implementation files nearby.
- Important APIs/types/functions: `func TestShouldPrefixExcludeValuesWithSlash(t *testing.T)`, `func TestShouldReadExcludePatternsFromFiles(t *testing.T)`, `func TestShouldReturnFalseIfThereAreNoExclusions(t *testing.T)`.
- Control flow and state: treats invalid internal invariants as fatal/panic conditions; is non-persistent test/benchmark code. Source size is 1739 bytes across 66 lines, read as part of this work item.
- Dependencies and integration points: standard library: os, reflect, testing; external/internal modules: github.com/rfjakob/gocryptfs/v2/internal/fusefrontend. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/excluder_test.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points; test/helper code can mask regressions if expected constants or environment assumptions drift.
- Test signals: Direct test/benchmark declarations: TestShouldPrefixExcludeValuesWithSlash, TestShouldReadExcludePatternsFromFiles, TestShouldReturnFalseIfThereAreNoExclusions.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/excluder_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/file.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/file.go

- Purpose: Implements reverse-mode file reads by synthesizing ciphertext from plaintext backing file data at requested ciphertext offsets.
- Important APIs/types/functions: `type File struct`, `func (f *File) Read(ctx context.Context, buf []byte, ioff int64) (resultData fuse.ReadResult, errno syscall.Errno)`, `func (f *File) Release(context.Context) syscall.Errno`, `func (f *File) Lseek(ctx context.Context, off uint64, whence uint32) (uint64, syscall.Errno)`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; transforms data through encryption/decryption boundaries. Source size is 1946 bytes across 82 lines, read as part of this work item.
- Dependencies and integration points: standard library: bytes, context, os, syscall; external/internal modules: github.com/hanwen/go-fuse/v2/fs, github.com/hanwen/go-fuse/v2/fuse, github.com/rfjakob/gocryptfs/v2/internal/contentenc. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/file.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/file.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/file_api_check.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/file_api_check.go

- Purpose: Implementation file in sources/security-integrity/gocryptfs/internal/fusefrontend_reverse covering the file_api_check.go slice of that package.
- Important APIs/types/functions: `var _ = (fs.FileReader)((*File)(nil))`, `var _ = (fs.FileReleaser)((*File)(nil))`, `var _ = (fs.FileLseeker)((*File)(nil))`, `var _ = (fs.FileGetattrer)((*File)(nil))`, `var _ = (fs.FileGetlker)((*File)(nil))`, `var _ = (fs.FileSetlker)((*File)(nil))`, `var _ = (fs.FileSetlkwer)((*File)(nil))`, `var _ = (fs.FileSetattrer)((*File)(nil))`, `var _ = (fs.FileWriter)((*File)(nil))`, `var _ = (fs.FileFsyncer)((*File)(nil))`, `var _ = (fs.FileFlusher)((*File)(nil))`, `var _ = (fs.FileAllocater)((*File)(nil))`.
- Control flow and state: is mostly stateless helper or interface assertion code. Source size is 688 bytes across 26 lines, read as part of this work item.
- Dependencies and integration points: external/internal modules: github.com/hanwen/go-fuse/v2/fs. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/file_api_check.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/file_api_check.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/file_helpers.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/file_helpers.go

- Purpose: Contains reverse-mode block encryption and backing plaintext read helpers, including deterministic per-path IV/file-ID derivation.
- Important APIs/types/functions: `var inodeTable sync.Map`, `func (rf *File) encryptBlocks(plaintext []byte, firstBlockNo uint64, fileID []byte, block0IV []byte) []byte`, `func (f *File) readBackingFile(off uint64, length uint64) (out []byte, err error)`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; transforms data through encryption/decryption boundaries. Source size is 2010 bytes across 63 lines, read as part of this work item.
- Dependencies and integration points: standard library: bytes, io, sync; external/internal modules: github.com/rfjakob/gocryptfs/v2/internal/contentenc, github.com/rfjakob/gocryptfs/v2/internal/pathiv, github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/file_helpers.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/file_helpers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/node.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/node.go

- Purpose: Implements reverse-mode lookup/getattr/readlink/open/statfs against a plaintext backing tree while exposing encrypted names and ciphertext sizes.
- Important APIs/types/functions: `type Node struct`, `func (n *Node) Lookup(ctx context.Context, cName string, out *fuse.EntryOut) (ch *fs.Inode, errno syscall.Errno)`, `func (n *Node) Getattr(ctx context.Context, f fs.FileHandle, out *fuse.AttrOut) (errno syscall.Errno)`, `func (n *Node) Readlink(ctx context.Context) (out []byte, errno syscall.Errno)`, `func (n *Node) Open(ctx context.Context, flags uint32) (fh fs.FileHandle, fuseFlags uint32, errno syscall.Errno)`, `func (n *Node) Statfs(ctx context.Context, out *fuse.StatfsOut) syscall.Errno`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; participates in directory-IV based name encryption state; handles long-name sidecar metadata and cleanup; transforms data through encryption/decryption boundaries. Source size is 6254 bytes across 223 lines, read as part of this work item.
- Dependencies and integration points: standard library: context, fmt, os, path/filepath, syscall; external/internal modules: golang.org/x/sys/unix, github.com/hanwen/go-fuse/v2/fs, github.com/hanwen/go-fuse/v2/fuse, github.com/rfjakob/gocryptfs/v2/internal/contentenc, github.com/rfjakob/gocryptfs/v2/internal/pathiv, github.com/rfjakob/gocryptfs/v2/internal/syscallcompat, github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/node.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points.
- Test signals: Contains inline test/benchmark hooks or comments; package-level tests should be run for validation.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/node.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/node_api_check.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/node_api_check.go

- Purpose: Implementation file in sources/security-integrity/gocryptfs/internal/fusefrontend_reverse covering the node_api_check.go slice of that package.
- Important APIs/types/functions: `var _ = (fs.NodeGetattrer)((*Node)(nil))`, `var _ = (fs.NodeLookuper)((*Node)(nil))`, `var _ = (fs.NodeReaddirer)((*Node)(nil))`, `var _ = (fs.NodeReadlinker)((*Node)(nil))`, `var _ = (fs.NodeOpener)((*Node)(nil))`, `var _ = (fs.NodeStatfser)((*Node)(nil))`, `var _ = (fs.NodeGetxattrer)((*Node)(nil))`, `var _ = (fs.NodeListxattrer)((*Node)(nil))`, `var _ = (fs.NodeOpendirer)((*Node)(nil))`, `var _ = (fs.NodeMknoder)((*Node)(nil))`, `var _ = (fs.NodeCreater)((*Node)(nil))`, `var _ = (fs.NodeMkdirer)((*Node)(nil))` (9 more declarations in file).
- Control flow and state: maps extended attributes between plaintext API names and backing storage names. Source size is 1070 bytes across 35 lines, read as part of this work item.
- Dependencies and integration points: external/internal modules: github.com/hanwen/go-fuse/v2/fs. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/node_api_check.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points; xattr behavior differs by platform and must preserve ACL passthrough plus encrypted user attributes.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/node_api_check.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/node_dir_ops.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/node_dir_ops.go

- Purpose: Implements reverse-mode readdir by reading plaintext entries, filtering exclusions, and synthesizing encrypted directory entries plus virtual metadata files.
- Important APIs/types/functions: `func (n *Node) Readdir(ctx context.Context) (stream fs.DirStream, errno syscall.Errno)`, `func (n *Node) readdirPlaintextnames(entries []fuse.DirEntry) (stream fs.DirStream, errno syscall.Errno)`.
- Control flow and state: participates in directory-IV based name encryption state; handles long-name sidecar metadata and cleanup; transforms data through encryption/decryption boundaries. Source size is 3764 bytes across 119 lines, read as part of this work item.
- Dependencies and integration points: standard library: context, fmt, syscall; external/internal modules: golang.org/x/sys/unix, github.com/hanwen/go-fuse/v2/fs, github.com/hanwen/go-fuse/v2/fuse, github.com/rfjakob/gocryptfs/v2/internal/configfile, github.com/rfjakob/gocryptfs/v2/internal/cryptocore, github.com/rfjakob/gocryptfs/v2/internal/nametransform, github.com/rfjakob/gocryptfs/v2/internal/syscallcompat, github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/node_dir_ops.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/node_dir_ops.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/node_helpers.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/node_helpers.go

- Purpose: Provides reverse-mode path preparation, size translation, virtual metadata lookup, symlink encryption, and child inode creation helpers.
- Important APIs/types/functions: `type dirfdPlus struct`, `const (`, `func (n *Node) translateSize(dirfd int, cName string, pName string, out *fuse.Attr)`, `func (n *Node) Path() string`, `func (n *Node) rootNode() *RootNode`, `func (n *Node) prepareAtSyscall(child string) (d *dirfdPlus, errno syscall.Errno)`, `func (n *Node) newChild(ctx context.Context, st *syscall.Stat_t, out *fuse.EntryOut) *fs.Inode`, `func (n *Node) isRoot() bool`, `func (n *Node) lookupLongnameName(ctx context.Context, nameFile string, out *fuse.EntryOut) (ch *fs.Inode, errno syscall.Errno)`, `func (n *Node) lookupDiriv(ctx context.Context, out *fuse.EntryOut) (ch *fs.Inode, errno syscall.Errno)`, `func (n *Node) lookupConf(ctx context.Context, out *fuse.EntryOut) (ch *fs.Inode, errno syscall.Errno)`, `func (n *Node) readlink(dirfd int, cName string, pName string) (out []byte, errno syscall.Errno)`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; uses descriptor-relative syscalls to avoid path races and symlink traversal; participates in directory-IV based name encryption state; handles long-name sidecar metadata and cleanup; transforms data through encryption/decryption boundaries; treats invalid internal invariants as fatal/panic conditions. Source size is 6939 bytes across 238 lines, read as part of this work item.
- Dependencies and integration points: standard library: context, log, path/filepath, syscall; external/internal modules: golang.org/x/sys/unix, github.com/hanwen/go-fuse/v2/fs, github.com/hanwen/go-fuse/v2/fuse, github.com/rfjakob/gocryptfs/v2/internal/configfile, github.com/rfjakob/gocryptfs/v2/internal/pathiv, github.com/rfjakob/gocryptfs/v2/internal/syscallcompat. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/node_helpers.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points.
- Test signals: Contains inline test/benchmark hooks or comments; package-level tests should be run for validation.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/node_helpers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/node_xattr.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/node_xattr.go

- Purpose: Synthesizes reverse-mode encrypted xattr reads and xattr name listings from plaintext backing xattrs.
- Important APIs/types/functions: `var xattrStorePrefix = "user.gocryptfs."`, `func isAcl(attr string) bool`, `func (n *Node) Getxattr(ctx context.Context, attr string, dest []byte) (uint32, syscall.Errno)`, `func (n *Node) Listxattr(ctx context.Context, dest []byte) (uint32, syscall.Errno)`.
- Control flow and state: transforms data through encryption/decryption boundaries; maps extended attributes between plaintext API names and backing storage names. Source size is 2359 bytes across 90 lines, read as part of this work item.
- Dependencies and integration points: standard library: bytes, context, syscall; external/internal modules: github.com/rfjakob/gocryptfs/v2/internal/pathiv. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/node_xattr.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points; xattr behavior differs by platform and must preserve ACL passthrough plus encrypted user attributes.
- Test signals: Contains inline test/benchmark hooks or comments; package-level tests should be run for validation.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/node_xattr.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/node_xattr_darwin.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/node_xattr_darwin.go

- Purpose: Implementation file in sources/security-integrity/gocryptfs/internal/fusefrontend_reverse covering the node_xattr_darwin.go slice of that package.
- Important APIs/types/functions: `const noSuchAttributeError = syscall.ENOATTR`, `func (n *Node) getXAttr(cAttr string) (out []byte, errno syscall.Errno)`, `func (n *Node) listXAttr() (out []string, errno syscall.Errno)`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; maps extended attributes between plaintext API names and backing storage names. Source size is 1275 bytes across 56 lines, read as part of this work item.
- Dependencies and integration points: standard library: syscall; external/internal modules: github.com/hanwen/go-fuse/v2/fs, github.com/rfjakob/gocryptfs/v2/internal/syscallcompat. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/node_xattr_darwin.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points; xattr behavior differs by platform and must preserve ACL passthrough plus encrypted user attributes.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/node_xattr_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/node_xattr_freebsd.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/node_xattr_freebsd.go

- Purpose: Implementation file in sources/security-integrity/gocryptfs/internal/fusefrontend_reverse covering the node_xattr_freebsd.go slice of that package.
- Important APIs/types/functions: `const noSuchAttributeError = unix.ENOATTR`, `func (n *Node) getXAttr(cAttr string) (out []byte, errno unix.Errno)`, `func (n *Node) listXAttr() (out []string, errno unix.Errno)`.
- Control flow and state: maps extended attributes between plaintext API names and backing storage names. Source size is 324 bytes across 18 lines, read as part of this work item.
- Dependencies and integration points: external/internal modules: golang.org/x/sys/unix. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/node_xattr_freebsd.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points; xattr behavior differs by platform and must preserve ACL passthrough plus encrypted user attributes.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/node_xattr_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/node_xattr_linux.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/node_xattr_linux.go

- Purpose: Implementation file in sources/security-integrity/gocryptfs/internal/fusefrontend_reverse covering the node_xattr_linux.go slice of that package.
- Important APIs/types/functions: `const noSuchAttributeError = syscall.ENODATA`, `func (n *Node) getXAttr(cAttr string) (out []byte, errno syscall.Errno)`, `func (n *Node) listXAttr() (out []string, errno syscall.Errno)`.
- Control flow and state: maps extended attributes between plaintext API names and backing storage names. Source size is 976 bytes across 44 lines, read as part of this work item.
- Dependencies and integration points: standard library: fmt, syscall; external/internal modules: github.com/hanwen/go-fuse/v2/fs, github.com/rfjakob/gocryptfs/v2/internal/syscallcompat. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/node_xattr_linux.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points; xattr behavior differs by platform and must preserve ACL passthrough plus encrypted user attributes.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/node_xattr_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/root_node.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/root_node.go

- Purpose: Defines reverse-mode root state, exclusion logic, long-name lookup helpers, stable inode generation, and encrypted xattr helpers.
- Important APIs/types/functions: `type RootNode struct`, `func NewRootNode(args fusefrontend.Args, c *contentenc.ContentEnc, n *nametransform.NameTransform) *RootNode`, `func (rn *RootNode) findLongnameParent(fd int, diriv []byte, longname string) (pName string, cFullName string, errno syscall.Er...`, `func (rn *RootNode) isExcludedPlain(pPath string) bool`, `func (rn *RootNode) excludeDirEntries(d *dirfdPlus, entries []fuse.DirEntry) (filtered []fuse.DirEntry)`, `func (rn *RootNode) uniqueStableAttr(mode uint32, ino uint64) fs.StableAttr`, `func (rn *RootNode) RootIno() uint64`, `func (rn *RootNode) encryptXattrValue(data []byte, nonce []byte) (cData []byte)`, `func (rn *RootNode) encryptXattrName(attr string) (string, error)`, `func (rn *RootNode) decryptXattrName(cAttr string) (attr string, err error)`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; participates in directory-IV based name encryption state; handles long-name sidecar metadata and cleanup; transforms data through encryption/decryption boundaries; maps extended attributes between plaintext API names and backing storage names; treats invalid internal invariants as fatal/panic conditions; can terminate the process on unrecoverable setup or external command errors. Source size is 7339 bytes across 222 lines, read as part of this work item.
- Dependencies and integration points: standard library: log, os, path/filepath, strings, sync/atomic, syscall; external/internal modules: golang.org/x/sys/unix, github.com/hanwen/go-fuse/v2/fs, github.com/hanwen/go-fuse/v2/fuse, github.com/rfjakob/gocryptfs/v2/internal/configfile, github.com/rfjakob/gocryptfs/v2/internal/contentenc, github.com/rfjakob/gocryptfs/v2/internal/exitcodes, github.com/rfjakob/gocryptfs/v2/internal/fusefrontend, github.com/rfjakob/gocryptfs/v2/internal/inomap, github.com/rfjakob/gocryptfs/v2/internal/nametransform, github.com/rfjakob/gocryptfs/v2/internal/syscallcompat, github.com/rfjakob/gocryptfs/v2/internal/tlog, github.com/sabhiram/go-gitignore. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/root_node.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points; xattr behavior differs by platform and must preserve ACL passthrough plus encrypted user attributes.
- Test signals: Contains inline test/benchmark hooks or comments; package-level tests should be run for validation.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/root_node.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/rpath.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/rpath.go

- Purpose: Decrypts reverse-mode ciphertext paths back to plaintext paths, derives deterministic directory IVs, and opens plaintext backing directories safely.
- Important APIs/types/functions: `func (rfs *RootNode) rDecryptName(cName string, dirIV []byte, pDir string) (pName string, err error)`, `func (rn *RootNode) decryptPath(cPath string) (string, error)`, `func (rn *RootNode) deriveDirIV(cPath string) []byte`, `func (rn *RootNode) openBackingDir(cPath string) (dirfd int, pPath string, err error)`.
- Control flow and state: participates in directory-IV based name encryption state; handles long-name sidecar metadata and cleanup; transforms data through encryption/decryption boundaries; treats invalid internal invariants as fatal/panic conditions. Source size is 4105 bytes across 124 lines, read as part of this work item.
- Dependencies and integration points: standard library: encoding/base64, log, path/filepath, strings, syscall; external/internal modules: github.com/rfjakob/gocryptfs/v2/internal/nametransform, github.com/rfjakob/gocryptfs/v2/internal/pathiv, github.com/rfjakob/gocryptfs/v2/internal/syscallcompat, github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/rpath.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/rpath.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/virtualconf.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/virtualconf.go

- Purpose: Provides read-only virtual access to a generated reverse-mode config file.
- Important APIs/types/functions: `type VirtualConfNode struct`, `type VirtualConfFile struct`, `var _ = (fs.NodeOpener)((*VirtualConfNode)(nil))`, `var _ = (fs.NodeGetattrer)((*VirtualConfNode)(nil))`, `var _ = (fs.FileReader)((*VirtualConfFile)(nil))`, `var _ = (fs.FileReleaser)((*VirtualConfFile)(nil))`, `func (n *VirtualConfNode) rootNode() *RootNode`, `func (n *VirtualConfNode) Open(ctx context.Context, flags uint32) (fh fs.FileHandle, fuseFlags uint32, errno syscall.Errno)`, `func (n *VirtualConfNode) Getattr(ctx context.Context, fh fs.FileHandle, out *fuse.AttrOut) syscall.Errno`, `func (f *VirtualConfFile) Read(ctx context.Context, buf []byte, off int64) (res fuse.ReadResult, errno syscall.Errno)`, `func (f *VirtualConfFile) Release(ctx context.Context) syscall.Errno`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths. Source size is 1709 bytes across 76 lines, read as part of this work item.
- Dependencies and integration points: standard library: context, sync, syscall; external/internal modules: github.com/hanwen/go-fuse/v2/fs, github.com/hanwen/go-fuse/v2/fuse. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/virtualconf.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/virtualconf.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/virtualnode.go -->
# sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/virtualnode.go

- Purpose: Provides in-memory virtual nodes for synthesized diriv and long-name metadata files in reverse mode.
- Important APIs/types/functions: `type fileType int`, `type VirtualMemNode struct`, `const (`, `const (`, `func (n *Node) lookupFileType(cName string) fileType`, `func (n *Node) newVirtualMemNode(content []byte, parentStat *syscall.Stat_t, inoTag uint8) (vf *VirtualMemNode, errno syscall.E...`, `func (f *VirtualMemNode) Open(ctx context.Context, flags uint32) (fh fs.FileHandle, fuseFlags uint32, errno syscall.Errno)`, `func (f *VirtualMemNode) Getattr(ctx context.Context, fh fs.FileHandle, out *fuse.AttrOut) syscall.Errno`, `func (f *VirtualMemNode) Read(ctx context.Context, fh fs.FileHandle, dest []byte, off int64) (fuse.ReadResult, syscall.Errno)`.
- Control flow and state: participates in directory-IV based name encryption state; handles long-name sidecar metadata and cleanup; treats invalid internal invariants as fatal/panic conditions. Source size is 4365 bytes across 138 lines, read as part of this work item.
- Dependencies and integration points: standard library: context, log, syscall; external/internal modules: github.com/hanwen/go-fuse/v2/fs, github.com/hanwen/go-fuse/v2/fuse, github.com/rfjakob/gocryptfs/v2/internal/configfile, github.com/rfjakob/gocryptfs/v2/internal/inomap, github.com/rfjakob/gocryptfs/v2/internal/nametransform. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/virtualnode.go` and the declarations listed above.
- Risks and review notes: FUSE/syscall code is race-prone; fd ownership, symlink safety, and errno translation are primary review points.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/fusefrontend_reverse/virtualnode.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/inomap/inomap.go -->
# sources/security-integrity/gocryptfs/internal/inomap/inomap.go

- Purpose: Maps backing filesystem device/inode pairs to stable FUSE inode numbers, spilling uncommon devices into a separate namespace when needed.
- Important APIs/types/functions: `type InoMap struct`, `const (`, `var spillWarn sync.Once`, `func New(rootDev uint64) *InoMap`, `func (m *InoMap) NextSpillIno() (out uint64)`, `func (m *InoMap) spill(in QIno) (out uint64)`, `func (m *InoMap) Translate(in QIno) (out uint64)`, `func (m *InoMap) TranslateStat(st *syscall.Stat_t)`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; handles long-name sidecar metadata and cleanup; treats invalid internal invariants as fatal/panic conditions. Source size is 3645 bytes across 132 lines, read as part of this work item.
- Dependencies and integration points: standard library: log, math, sync, sync/atomic, syscall; external/internal modules: github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/inomap/inomap.go` and the declarations listed above.
- Risks and review notes: shared mutable state needs race-free registration, cleanup, and bounded resource use.
- Test signals: Nearby test signal: `sources/security-integrity/gocryptfs/internal/inomap/inomap_test.go` covers related behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/inomap/inomap.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/inomap/inomap_test.go -->
# sources/security-integrity/gocryptfs/internal/inomap/inomap_test.go

- Purpose: Test coverage for sources/security-integrity/gocryptfs/internal/inomap, centered on TestTranslate, TestTranslateStress, TestSpill, TestUniqueness, BenchmarkTranslateSingleDev, BenchmarkTranslateManyDevs. It records expected compatibility, error, and boundary behavior for the implementation files nearby.
- Important APIs/types/functions: `const (`, `func TestTranslate(t *testing.T)`, `func TestTranslateStress(t *testing.T)`, `func TestSpill(t *testing.T)`, `func TestUniqueness(t *testing.T)`, `func BenchmarkTranslateSingleDev(b *testing.B)`, `func BenchmarkTranslateManyDevs(b *testing.B)`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; handles long-name sidecar metadata and cleanup; treats invalid internal invariants as fatal/panic conditions; is non-persistent test/benchmark code. Source size is 3231 bytes across 169 lines, read as part of this work item.
- Dependencies and integration points: standard library: sync, testing. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/inomap/inomap_test.go` and the declarations listed above.
- Risks and review notes: shared mutable state needs race-free registration, cleanup, and bounded resource use; test/helper code can mask regressions if expected constants or environment assumptions drift.
- Test signals: Direct test/benchmark declarations: TestTranslate, TestTranslateStress, TestSpill, TestUniqueness, BenchmarkTranslateSingleDev, BenchmarkTranslateManyDevs.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/inomap/inomap_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/inomap/qino.go -->
# sources/security-integrity/gocryptfs/internal/inomap/qino.go

- Purpose: Defines qualified inode identities consisting of namespace data and inode number, including construction from syscall stat data.
- Important APIs/types/functions: `type namespaceData struct`, `type QIno struct`, `func NewQIno(dev uint64, tag uint8, ino uint64) QIno`, `func QInoFromStat(st *syscall.Stat_t) QIno`.
- Control flow and state: is mostly stateless helper or interface assertion code. Source size is 1067 bytes across 44 lines, read as part of this work item.
- Dependencies and integration points: standard library: syscall. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/inomap/qino.go` and the declarations listed above.
- Risks and review notes: shared mutable state needs race-free registration, cleanup, and bounded resource use.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/inomap/qino.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/nametransform/badname.go -->
# sources/security-integrity/gocryptfs/internal/nametransform/badname.go

- Purpose: Handles badname compatibility by searching for matching ciphertext names when plaintext names contain legacy or ambiguous encodings.
- Important APIs/types/functions: `const (`, `func (be *NameTransform) EncryptAndHashBadName(name string, iv []byte, dirfd int) (cName string, err error)`, `func (n *NameTransform) decryptBadname(cipherName string, iv []byte) (string, error)`, `func (n *NameTransform) HaveBadnamePatterns() bool`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; handles long-name sidecar metadata and cleanup; transforms data through encryption/decryption boundaries. Source size is 3084 bytes across 92 lines, read as part of this work item.
- Dependencies and integration points: standard library: crypto/aes, path/filepath, strings, syscall; external/internal modules: golang.org/x/sys/unix, github.com/rfjakob/gocryptfs/v2/internal/syscallcompat. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/nametransform/badname.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/nametransform/badname.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/nametransform/diriv.go -->
# sources/security-integrity/gocryptfs/internal/nametransform/diriv.go

- Purpose: Reads and writes per-directory IV files, validating length and all-zero corruption cases.
- Important APIs/types/functions: `const (`, `var allZeroDirIV = make([]byte, DirIVLen)`, `func (n *NameTransform) ReadDirIVAt(dirfd int) (iv []byte, err error)`, `func fdReadDirIV(fd *os.File) (iv []byte, err error)`, `func WriteDirIVAt(dirfd int) error`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; participates in directory-IV based name encryption state. Source size is 3157 bytes across 99 lines, read as part of this work item.
- Dependencies and integration points: standard library: bytes, fmt, io, os, syscall; external/internal modules: github.com/rfjakob/gocryptfs/v2/internal/cryptocore, github.com/rfjakob/gocryptfs/v2/internal/syscallcompat, github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/nametransform/diriv.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable.
- Test signals: Contains inline test/benchmark hooks or comments; package-level tests should be run for validation.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/nametransform/diriv.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/nametransform/longnames.go -->
# sources/security-integrity/gocryptfs/internal/nametransform/longnames.go

- Purpose: Implements long filename hashing, sidecar naming, sidecar reads/deletes/writes, and long-name classification.
- Important APIs/types/functions: `const (`, `const (`, `func (n *NameTransform) HashLongName(name string) string`, `func NameType(cName string) int`, `func IsLongContent(cName string) bool`, `func RemoveLongNameSuffix(cName string) string`, `func ReadLongNameAt(dirfd int, cName string) (string, error)`, `func DeleteLongNameAt(dirfd int, hashName string) error`, `func (n *NameTransform) WriteLongNameAt(dirfd int, hashName string, plainName string) (err error)`.
- Control flow and state: participates in directory-IV based name encryption state; handles long-name sidecar metadata and cleanup; transforms data through encryption/decryption boundaries. Source size is 5183 bytes across 169 lines, read as part of this work item.
- Dependencies and integration points: standard library: crypto/sha256, fmt, io, os, path/filepath, strings, syscall; external/internal modules: github.com/rfjakob/gocryptfs/v2/internal/syscallcompat, github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/nametransform/longnames.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable.
- Test signals: Nearby test signal: `sources/security-integrity/gocryptfs/internal/nametransform/longnames_test.go` covers related behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/nametransform/longnames.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/nametransform/longnames_test.go -->
# sources/security-integrity/gocryptfs/internal/nametransform/longnames_test.go

- Purpose: Test coverage for sources/security-integrity/gocryptfs/internal/nametransform, centered on TestIsLongName, TestRemoveLongNameSuffix, TestLongNameMax. It records expected compatibility, error, and boundary behavior for the implementation files nearby.
- Important APIs/types/functions: `func TestIsLongName(t *testing.T)`, `func TestRemoveLongNameSuffix(t *testing.T)`, `func newLognamesTestInstance(longNameMax uint8) *NameTransform`, `func TestLongNameMax(t *testing.T)`.
- Control flow and state: handles long-name sidecar metadata and cleanup; transforms data through encryption/decryption boundaries; is non-persistent test/benchmark code. Source size is 1944 bytes across 72 lines, read as part of this work item.
- Dependencies and integration points: standard library: strings, testing; external/internal modules: github.com/rfjakob/gocryptfs/v2/internal/contentenc, github.com/rfjakob/gocryptfs/v2/internal/cryptocore. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/nametransform/longnames_test.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable; test/helper code can mask regressions if expected constants or environment assumptions drift.
- Test signals: Direct test/benchmark declarations: TestIsLongName, TestRemoveLongNameSuffix, TestLongNameMax.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/nametransform/longnames_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/nametransform/names.go -->
# sources/security-integrity/gocryptfs/internal/nametransform/names.go

- Purpose: Implements filename encryption/decryption using EME, padding, base64/raw64 encoding, NFC normalization, long-name hashing, and validation.
- Important APIs/types/functions: `type NameTransform struct`, `const (`, `func New(e *eme.EMECipher, longNames bool, longNameMax uint8, raw64 bool, badname []string, deterministicNames bool) *NameTrans...`, `func (n *NameTransform) DecryptName(cipherName string, iv []byte) (plainName string, err error)`, `func (n *NameTransform) decryptName(cipherName string, iv []byte) (string, error)`, `func (n *NameTransform) EncryptName(plainName string, iv []byte) (cipherName64 string, err error)`, `func (n *NameTransform) encryptName(plainName string, iv []byte) (cipherName64 string)`, `func (be *NameTransform) EncryptAndHashName(name string, iv []byte) (string, error)`, `func (n *NameTransform) B64EncodeToString(src []byte) string`, `func (n *NameTransform) B64DecodeString(s string) ([]byte, error)`, `func Dir(path string) string`, `func (n *NameTransform) GetLongNameMax() int`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; handles long-name sidecar metadata and cleanup; transforms data through encryption/decryption boundaries; maps extended attributes between plaintext API names and backing storage names. Source size is 6742 bytes across 215 lines, read as part of this work item.
- Dependencies and integration points: standard library: crypto/aes, encoding/base64, errors, math, path/filepath, runtime, strings, syscall; external/internal modules: golang.org/x/text/unicode/norm, github.com/rfjakob/eme, github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/nametransform/names.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable; xattr behavior differs by platform and must preserve ACL passthrough plus encrypted user attributes.
- Test signals: Nearby test signal: `sources/security-integrity/gocryptfs/internal/nametransform/names_test.go` covers related behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/nametransform/names.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/nametransform/names_test.go -->
# sources/security-integrity/gocryptfs/internal/nametransform/names_test.go

- Purpose: Test coverage for sources/security-integrity/gocryptfs/internal/nametransform, centered on TestPad16, TestUnpad16Garbage, TestIsValidName, TestIsValidXattrName. It records expected compatibility, error, and boundary behavior for the implementation files nearby.
- Important APIs/types/functions: `func TestPad16(t *testing.T)`, `func TestUnpad16Garbage(t *testing.T)`, `func TestIsValidName(t *testing.T)`, `func TestIsValidXattrName(t *testing.T)`.
- Control flow and state: maps extended attributes between plaintext API names and backing storage names; is non-persistent test/benchmark code. Source size is 2103 bytes across 101 lines, read as part of this work item.
- Dependencies and integration points: standard library: bytes, strings, testing. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/nametransform/names_test.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable; xattr behavior differs by platform and must preserve ACL passthrough plus encrypted user attributes; test/helper code can mask regressions if expected constants or environment assumptions drift.
- Test signals: Direct test/benchmark declarations: TestPad16, TestUnpad16Garbage, TestIsValidName, TestIsValidXattrName.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/nametransform/names_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/nametransform/nfc_test.go -->
# sources/security-integrity/gocryptfs/internal/nametransform/nfc_test.go

- Purpose: Test coverage for sources/security-integrity/gocryptfs/internal/nametransform, centered on TestNFD2NFC. It records expected compatibility, error, and boundary behavior for the implementation files nearby.
- Important APIs/types/functions: `func TestNFD2NFC(t *testing.T)`.
- Control flow and state: participates in directory-IV based name encryption state; transforms data through encryption/decryption boundaries; is non-persistent test/benchmark code. Source size is 793 bytes across 30 lines, read as part of this work item.
- Dependencies and integration points: standard library: strconv, testing; external/internal modules: golang.org/x/text/unicode/norm. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/nametransform/nfc_test.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable; test/helper code can mask regressions if expected constants or environment assumptions drift.
- Test signals: Direct test/benchmark declarations: TestNFD2NFC.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/nametransform/nfc_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/nametransform/pad16.go -->
# sources/security-integrity/gocryptfs/internal/nametransform/pad16.go

- Purpose: Pads arbitrary names to AES block boundaries and removes padding during decryption with corruption checks.
- Important APIs/types/functions: `func pad16(orig []byte) (padded []byte)`, `func unPad16(padded []byte) ([]byte, error)`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; treats invalid internal invariants as fatal/panic conditions. Source size is 1686 bytes across 65 lines, read as part of this work item.
- Dependencies and integration points: standard library: crypto/aes, errors, fmt, log. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/nametransform/pad16.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/nametransform/pad16.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/nametransform/perms.go -->
# sources/security-integrity/gocryptfs/internal/nametransform/perms.go

- Purpose: Documents and defines permission constants for internal diriv and long-name metadata files.
- Important APIs/types/functions: `const (`.
- Control flow and state: participates in directory-IV based name encryption state; handles long-name sidecar metadata and cleanup; transforms data through encryption/decryption boundaries. Source size is 912 bytes across 27 lines, read as part of this work item.
- Dependencies and integration points: No Go imports; dependencies are shell/make tooling or package-local constants only. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/nametransform/perms.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/nametransform/perms.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/nametransform/valid.go -->
# sources/security-integrity/gocryptfs/internal/nametransform/valid.go

- Purpose: Validates plaintext file names against empty, slash-containing, dot, and dot-dot forms.
- Important APIs/types/functions: `func IsValidName(name string) error`.
- Control flow and state: is mostly stateless helper or interface assertion code. Source size is 739 bytes across 28 lines, read as part of this work item.
- Dependencies and integration points: standard library: fmt, strings. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/nametransform/valid.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/nametransform/valid.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/nametransform/xattr.go -->
# sources/security-integrity/gocryptfs/internal/nametransform/xattr.go

- Purpose: Encrypts and decrypts xattr names using a fixed xattr-name IV and validates xattr namespace restrictions.
- Important APIs/types/functions: `var xattrNameIV = []byte("xattr_name_iv_xx")`, `func isValidXattrName(name string) error`, `func (n *NameTransform) EncryptXattrName(plainName string) (cipherName64 string, err error)`, `func (n *NameTransform) DecryptXattrName(cipherName string) (plainName string, err error)`.
- Control flow and state: transforms data through encryption/decryption boundaries; maps extended attributes between plaintext API names and backing storage names. Source size is 1493 bytes across 48 lines, read as part of this work item.
- Dependencies and integration points: standard library: fmt, strings, syscall; external/internal modules: github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/nametransform/xattr.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable; xattr behavior differs by platform and must preserve ACL passthrough plus encrypted user attributes.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/nametransform/xattr.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/openfiletable/open_file_table.go -->
# sources/security-integrity/gocryptfs/internal/openfiletable/open_file_table.go

- Purpose: Tracks open backing files by qualified inode, preserving per-file content locks, file-ID cache, and write operation counters across handles.
- Important APIs/types/functions: `type table struct`, `type Entry struct`, `type countingMutex struct`, `var t table`, `func init()`, `func Register(qi inomap.QIno) *Entry`, `func Unregister(qi inomap.QIno)`, `func (c *countingMutex) Lock()`, `func WriteOpCount() uint64`, `func CountOpenFiles() int`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths. Source size is 2891 bytes across 104 lines, read as part of this work item.
- Dependencies and integration points: standard library: sync, sync/atomic; external/internal modules: github.com/rfjakob/gocryptfs/v2/internal/inomap. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/openfiletable/open_file_table.go` and the declarations listed above.
- Risks and review notes: shared mutable state needs race-free registration, cleanup, and bounded resource use.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/openfiletable/open_file_table.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/pathiv/pathiv.go -->
# sources/security-integrity/gocryptfs/internal/pathiv/pathiv.go

- Purpose: Derives deterministic IV material from paths for reverse mode file content, block IVs, directory IVs, symlinks, and xattrs.
- Important APIs/types/functions: `type Purpose string`, `type FileIVs struct`, `const (`, `func Derive(path string, purpose Purpose) []byte`, `func DeriveFile(path string) (fileIVs FileIVs)`, `func BlockIV(block0iv []byte, blockNo uint64) []byte`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; participates in directory-IV based name encryption state; transforms data through encryption/decryption boundaries; maps extended attributes between plaintext API names and backing storage names. Source size is 1892 bytes across 60 lines, read as part of this work item.
- Dependencies and integration points: standard library: crypto/sha256, encoding/binary; external/internal modules: github.com/rfjakob/gocryptfs/v2/internal/nametransform. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/pathiv/pathiv.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable; xattr behavior differs by platform and must preserve ACL passthrough plus encrypted user attributes.
- Test signals: Nearby test signal: `sources/security-integrity/gocryptfs/internal/pathiv/pathiv_test.go` covers related behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/pathiv/pathiv.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/pathiv/pathiv_test.go -->
# sources/security-integrity/gocryptfs/internal/pathiv/pathiv_test.go

- Purpose: Test coverage for sources/security-integrity/gocryptfs/internal/pathiv, centered on TestBlockIV. It records expected compatibility, error, and boundary behavior for the implementation files nearby.
- Important APIs/types/functions: `func TestBlockIV(t *testing.T)`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; is non-persistent test/benchmark code. Source size is 801 bytes across 29 lines, read as part of this work item.
- Dependencies and integration points: standard library: bytes, encoding/hex, testing. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/pathiv/pathiv_test.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable; test/helper code can mask regressions if expected constants or environment assumptions drift.
- Test signals: Direct test/benchmark declarations: TestBlockIV.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/pathiv/pathiv_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/readpassword/extpass_test.go -->
# sources/security-integrity/gocryptfs/internal/readpassword/extpass_test.go

- Purpose: Test coverage for sources/security-integrity/gocryptfs/internal/readpassword, centered on TestMain, TestExtpass, TestOnceExtpass, TestOnceExtpass2, TestOnceExtpass3, TestOnceExtpassSpaces, TestTwiceExtpass, TestExtpassEmpty. It records expected compatibility, error, and boundary behavior for the implementation files nearby.
- Important APIs/types/functions: `func TestMain(m *testing.M)`, `func TestExtpass(t *testing.T)`, `func TestOnceExtpass(t *testing.T)`, `func TestOnceExtpass2(t *testing.T)`, `func TestOnceExtpass3(t *testing.T)`, `func TestOnceExtpassSpaces(t *testing.T)`, `func TestTwiceExtpass(t *testing.T)`, `func TestExtpassEmpty(t *testing.T)`.
- Control flow and state: treats invalid internal invariants as fatal/panic conditions; can terminate the process on unrecoverable setup or external command errors; is non-persistent test/benchmark code. Source size is 1827 bytes across 91 lines, read as part of this work item.
- Dependencies and integration points: standard library: os, testing; external/internal modules: github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/readpassword/extpass_test.go` and the declarations listed above.
- Risks and review notes: secret input handling must avoid truncation surprises, command injection assumptions, and accidental logging of sensitive material; test/helper code can mask regressions if expected constants or environment assumptions drift.
- Test signals: Direct test/benchmark declarations: TestMain, TestExtpass, TestOnceExtpass, TestOnceExtpass2, TestOnceExtpass3, TestOnceExtpassSpaces, TestTwiceExtpass, TestExtpassEmpty.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/readpassword/extpass_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/readpassword/passfile.go -->
# sources/security-integrity/gocryptfs/internal/readpassword/passfile.go

- Purpose: Reads password material from one or more files, using only the first newline-delimited line from each passfile.
- Important APIs/types/functions: `func readPassFileConcatenate(passfileSlice []string) (result []byte, err error)`, `func readPassFile(passfile string) ([]byte, error)`.
- Control flow and state: treats invalid internal invariants as fatal/panic conditions. Source size is 1598 bytes across 53 lines, read as part of this work item.
- Dependencies and integration points: standard library: bytes, fmt, os; external/internal modules: github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/readpassword/passfile.go` and the declarations listed above.
- Risks and review notes: secret input handling must avoid truncation surprises, command injection assumptions, and accidental logging of sensitive material.
- Test signals: Nearby test signal: `sources/security-integrity/gocryptfs/internal/readpassword/passfile_test.go` covers related behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/readpassword/passfile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/readpassword/passfile_test.go -->
# sources/security-integrity/gocryptfs/internal/readpassword/passfile_test.go

- Purpose: Test coverage for sources/security-integrity/gocryptfs/internal/readpassword, centered on TestPassfile, TestPassfileEmpty, TestPassfileNewline, TestPassfileEmptyFirstLine, TestPassFileConcatenate. It records expected compatibility, error, and boundary behavior for the implementation files nearby.
- Important APIs/types/functions: `func TestPassfile(t *testing.T)`, `func TestPassfileEmpty(t *testing.T)`, `func TestPassfileNewline(t *testing.T)`, `func TestPassfileEmptyFirstLine(t *testing.T)`, `func TestPassFileConcatenate(t *testing.T)`.
- Control flow and state: treats invalid internal invariants as fatal/panic conditions; is non-persistent test/benchmark code. Source size is 1945 bytes across 77 lines, read as part of this work item.
- Dependencies and integration points: standard library: testing. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/readpassword/passfile_test.go` and the declarations listed above.
- Risks and review notes: secret input handling must avoid truncation surprises, command injection assumptions, and accidental logging of sensitive material; test/helper code can mask regressions if expected constants or environment assumptions drift.
- Test signals: Direct test/benchmark declarations: TestPassfile, TestPassfileEmpty, TestPassfileNewline, TestPassfileEmptyFirstLine, TestPassFileConcatenate.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/readpassword/passfile_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/readpassword/read.go -->
# sources/security-integrity/gocryptfs/internal/readpassword/read.go

- Purpose: Implements password acquisition from passfiles, terminal, stdin, or external commands, with once/twice confirmation flows.
- Important APIs/types/functions: `const (`, `func Once(extpass []string, passfile []string, prompt string) ([]byte, error)`, `func Twice(extpass []string, passfile []string) ([]byte, error)`, `func readPasswordTerminal(prompt string) ([]byte, error)`, `func readPasswordStdin(prompt string) ([]byte, error)`, `func readPasswordExtpass(extpass []string) ([]byte, error)`, `func readLineUnbuffered(r io.Reader) (l []byte, err error)`.
- Control flow and state: treats invalid internal invariants as fatal/panic conditions. Source size is 4321 bytes across 168 lines, read as part of this work item.
- Dependencies and integration points: standard library: bytes, fmt, io, os, os/exec, strings; external/internal modules: golang.org/x/term, github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/readpassword/read.go` and the declarations listed above.
- Risks and review notes: secret input handling must avoid truncation surprises, command injection assumptions, and accidental logging of sensitive material.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/readpassword/read.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/readpassword/stdin_test.go -->
# sources/security-integrity/gocryptfs/internal/readpassword/stdin_test.go

- Purpose: Test coverage for sources/security-integrity/gocryptfs/internal/readpassword, centered on TestStdin, TestStdinEof, TestStdinEmpty. It records expected compatibility, error, and boundary behavior for the implementation files nearby.
- Important APIs/types/functions: `func TestStdin(t *testing.T)`, `func TestStdinEof(t *testing.T)`, `func TestStdinEmpty(t *testing.T)`.
- Control flow and state: treats invalid internal invariants as fatal/panic conditions; can terminate the process on unrecoverable setup or external command errors; is non-persistent test/benchmark code. Source size is 2621 bytes across 120 lines, read as part of this work item.
- Dependencies and integration points: standard library: fmt, os, os/exec, testing. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/readpassword/stdin_test.go` and the declarations listed above.
- Risks and review notes: secret input handling must avoid truncation surprises, command injection assumptions, and accidental logging of sensitive material; test/helper code can mask regressions if expected constants or environment assumptions drift.
- Test signals: Direct test/benchmark declarations: TestStdin, TestStdinEof, TestStdinEmpty.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/readpassword/stdin_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/siv_aead/benchmark.bash -->
# sources/security-integrity/gocryptfs/internal/siv_aead/benchmark.bash

- Purpose: Small benchmark wrapper script that runs the package benchmark from the correct directory and delegates to the shared benchmark entry point.
- Important APIs/types/functions: No Go declarations; behavior is defined by the script/build commands in the file.
- Control flow and state: is non-persistent test/benchmark code. Source size is 80 bytes across 8 lines, read as part of this work item.
- Dependencies and integration points: No Go imports; dependencies are shell/make tooling or package-local constants only. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/siv_aead/benchmark.bash` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable; test/helper code can mask regressions if expected constants or environment assumptions drift.
- Test signals: Contains inline test/benchmark hooks or comments; package-level tests should be run for validation.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/siv_aead/benchmark.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/siv_aead/correctness_test.go -->
# sources/security-integrity/gocryptfs/internal/siv_aead/correctness_test.go

- Purpose: Test coverage for sources/security-integrity/gocryptfs/internal/siv_aead, centered on TestKeyLens, TestK32, TestK64. It records expected compatibility, error, and boundary behavior for the implementation files nearby.
- Important APIs/types/functions: `func TestKeyLens(t *testing.T)`, `func TestK32(t *testing.T)`, `func TestK64(t *testing.T)`.
- Control flow and state: transforms data through encryption/decryption boundaries; treats invalid internal invariants as fatal/panic conditions; is non-persistent test/benchmark code. Source size is 4044 bytes across 149 lines, read as part of this work item.
- Dependencies and integration points: standard library: bytes, encoding/hex, testing; external/internal modules: github.com/aperturerobotics/jacobsa-crypto/siv. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/siv_aead/correctness_test.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable; test/helper code can mask regressions if expected constants or environment assumptions drift.
- Test signals: Direct test/benchmark declarations: TestKeyLens, TestK32, TestK64.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/siv_aead/correctness_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/siv_aead/performance_test.go -->
# sources/security-integrity/gocryptfs/internal/siv_aead/performance_test.go

- Purpose: Test coverage for sources/security-integrity/gocryptfs/internal/siv_aead, centered on test cases. It records expected compatibility, error, and boundary behavior for the implementation files nearby.
- Important APIs/types/functions: No Go declarations; behavior is defined by the script/build commands in the file.
- Control flow and state: transforms data through encryption/decryption boundaries; is non-persistent test/benchmark code. Source size is 17 bytes across 2 lines, read as part of this work item.
- Dependencies and integration points: No Go imports; dependencies are shell/make tooling or package-local constants only. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/siv_aead/performance_test.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable; test/helper code can mask regressions if expected constants or environment assumptions drift.
- Test signals: Test file with table or scenario assertions but no standard Test declaration was extracted; inspect manually if this changes.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/siv_aead/performance_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/siv_aead/siv_aead.go -->
# sources/security-integrity/gocryptfs/internal/siv_aead/siv_aead.go

- Purpose: Adapts the jacobsa AES-SIV implementation to Go cipher.AEAD with gocryptfs nonce, overhead, seal/open, and wipe semantics.
- Important APIs/types/functions: `type sivAead struct`, `const (`, `var _ cipher.AEAD = &sivAead}`, `func New(key []byte) cipher.AEAD`, `func new2(keyIn []byte) cipher.AEAD`, `func (s *sivAead) NonceSize() int`, `func (s *sivAead) Overhead() int`, `func (s *sivAead) Seal(dst, nonce, plaintext, authData []byte) []byte`, `func (s *sivAead) Open(dst, nonce, ciphertext, authData []byte) ([]byte, error)`, `func (s *sivAead) Wipe()`.
- Control flow and state: transforms data through encryption/decryption boundaries; treats invalid internal invariants as fatal/panic conditions. Source size is 2879 bytes across 103 lines, read as part of this work item.
- Dependencies and integration points: standard library: crypto/cipher, log; external/internal modules: github.com/aperturerobotics/jacobsa-crypto/siv. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/siv_aead/siv_aead.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/siv_aead/siv_aead.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/speed/benchmark.bash -->
# sources/security-integrity/gocryptfs/internal/speed/benchmark.bash

- Purpose: Small benchmark wrapper script that runs the package benchmark from the correct directory and delegates to the shared benchmark entry point.
- Important APIs/types/functions: No Go declarations; behavior is defined by the script/build commands in the file.
- Control flow and state: is non-persistent test/benchmark code. Source size is 69 bytes across 8 lines, read as part of this work item.
- Dependencies and integration points: No Go imports; dependencies are shell/make tooling or package-local constants only. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/speed/benchmark.bash` and the declarations listed above.
- Risks and review notes: test/helper code can mask regressions if expected constants or environment assumptions drift.
- Test signals: Contains inline test/benchmark hooks or comments; package-level tests should be run for validation.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/speed/benchmark.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/speed/cpuinfo.go -->
# sources/security-integrity/gocryptfs/internal/speed/cpuinfo.go

- Purpose: Extracts a Linux CPU model string for speed benchmark reporting, with runtime fallback on non-Linux systems.
- Important APIs/types/functions: `func cpuModelName() string`.
- Control flow and state: is mostly stateless helper or interface assertion code. Source size is 1112 bytes across 55 lines, read as part of this work item.
- Dependencies and integration points: standard library: io, os, runtime, strings. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/speed/cpuinfo.go` and the declarations listed above.
- Risks and review notes: main risk is compatibility drift because nearby packages depend on these small constants/helpers.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/speed/cpuinfo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/speed/speed.go -->
# sources/security-integrity/gocryptfs/internal/speed/speed.go

- Purpose: Runs comparative AEAD benchmarks for OpenSSL/Go AES-GCM, AES-SIV, XChaCha20-Poly1305, and block-size variants.
- Important APIs/types/functions: `const adLen = 24`, `const gocryptfsBlockSize = 4096`, `func Run()`, `func mbPerSec(r testing.BenchmarkResult) float64`, `func randBytes(n int) []byte`, `func bEncrypt(b *testing.B, c cipher.AEAD)`, `func bEncryptBlockSize(b *testing.B, c cipher.AEAD, blockSize int)`, `func bDecrypt(b *testing.B, c cipher.AEAD)`, `func bStupidGCM(b *testing.B)`, `func bGoGCM(b *testing.B)`, `func bGoGCMBlockSize(b *testing.B, blockSize int)`, `func bAESSIV(b *testing.B)` (2 more declarations in file).
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; handles long-name sidecar metadata and cleanup; transforms data through encryption/decryption boundaries; treats invalid internal invariants as fatal/panic conditions. Source size is 4554 bytes across 171 lines, read as part of this work item.
- Dependencies and integration points: standard library: crypto/aes, crypto/cipher, crypto/rand, fmt, log, testing; external/internal modules: golang.org/x/crypto/chacha20poly1305, github.com/rfjakob/gocryptfs/v2/internal/cryptocore, github.com/rfjakob/gocryptfs/v2/internal/siv_aead, github.com/rfjakob/gocryptfs/v2/internal/stupidgcm. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/speed/speed.go` and the declarations listed above.
- Risks and review notes: main risk is compatibility drift because nearby packages depend on these small constants/helpers.
- Test signals: Nearby test signal: `sources/security-integrity/gocryptfs/internal/speed/speed_test.go` covers related behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/speed/speed.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/speed/speed_test.go -->
# sources/security-integrity/gocryptfs/internal/speed/speed_test.go

- Purpose: Test coverage for sources/security-integrity/gocryptfs/internal/speed, centered on BenchmarkStupidGCM, BenchmarkStupidGCMDecrypt, BenchmarkGoGCM, BenchmarkGoGCMBlockSize, BenchmarkGoGCMDecrypt, BenchmarkAESSIV, BenchmarkAESSIVDecrypt, BenchmarkXchacha. It records expected compatibility, error, and boundary behavior for the implementation files nearby.
- Important APIs/types/functions: `func BenchmarkStupidGCM(b *testing.B)`, `func BenchmarkStupidGCMDecrypt(b *testing.B)`, `func BenchmarkGoGCM(b *testing.B)`, `func BenchmarkGoGCMBlockSize(b *testing.B)`, `func BenchmarkGoGCMDecrypt(b *testing.B)`, `func BenchmarkAESSIV(b *testing.B)`, `func BenchmarkAESSIVDecrypt(b *testing.B)`, `func BenchmarkXchacha(b *testing.B)`, `func BenchmarkXchachaDecrypt(b *testing.B)`, `func BenchmarkStupidXchacha(b *testing.B)`, `func BenchmarkStupidXchachaDecrypt(b *testing.B)`, `func BenchmarkStupidChacha(b *testing.B)` (1 more declarations in file).
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; transforms data through encryption/decryption boundaries; treats invalid internal invariants as fatal/panic conditions; is non-persistent test/benchmark code. Source size is 2056 bytes across 93 lines, read as part of this work item.
- Dependencies and integration points: standard library: crypto/aes, crypto/cipher, fmt, testing; external/internal modules: golang.org/x/crypto/chacha20poly1305, github.com/rfjakob/gocryptfs/v2/internal/siv_aead, github.com/rfjakob/gocryptfs/v2/internal/stupidgcm. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/speed/speed_test.go` and the declarations listed above.
- Risks and review notes: test/helper code can mask regressions if expected constants or environment assumptions drift.
- Test signals: Direct test/benchmark declarations: BenchmarkStupidGCM, BenchmarkStupidGCMDecrypt, BenchmarkGoGCM, BenchmarkGoGCMBlockSize, BenchmarkGoGCMDecrypt, BenchmarkAESSIV, BenchmarkAESSIVDecrypt, BenchmarkXchacha, BenchmarkXchachaDecrypt, BenchmarkStupidXchacha, BenchmarkStupidXchachaDecrypt, BenchmarkStupidChacha.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/speed/speed_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/Makefile -->
# sources/security-integrity/gocryptfs/internal/stupidgcm/Makefile

- Purpose: Build/test helper for the package, checking multiple OpenSSL and without-OpenSSL build modes plus C compiler warning coverage.
- Important APIs/types/functions: No Go declarations; behavior is defined by the script/build commands in the file.
- Control flow and state: is mostly stateless helper or interface assertion code. Source size is 452 bytes across 19 lines, read as part of this work item.
- Dependencies and integration points: No Go imports; dependencies are shell/make tooling or package-local constants only. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/stupidgcm/Makefile` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable; test/helper code can mask regressions if expected constants or environment assumptions drift.
- Test signals: Contains inline test/benchmark hooks or comments; package-level tests should be run for validation.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/autherr.go -->
# sources/security-integrity/gocryptfs/internal/stupidgcm/autherr.go

- Purpose: Defines the shared authentication failure error for OpenSSL-backed AEAD wrappers.
- Important APIs/types/functions: `var ErrAuth = fmt.Errorf("stupidgcm: message authentication failed")`.
- Control flow and state: is mostly stateless helper or interface assertion code. Source size is 168 bytes across 9 lines, read as part of this work item.
- Dependencies and integration points: standard library: fmt. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/stupidgcm/autherr.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/autherr.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/benchmark.bash -->
# sources/security-integrity/gocryptfs/internal/stupidgcm/benchmark.bash

- Purpose: Small benchmark wrapper script that runs the package benchmark from the correct directory and delegates to the shared benchmark entry point.
- Important APIs/types/functions: No Go declarations; behavior is defined by the script/build commands in the file.
- Control flow and state: is non-persistent test/benchmark code. Source size is 50 bytes across 4 lines, read as part of this work item.
- Dependencies and integration points: No Go imports; dependencies are shell/make tooling or package-local constants only. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/stupidgcm/benchmark.bash` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable; test/helper code can mask regressions if expected constants or environment assumptions drift.
- Test signals: Contains inline test/benchmark hooks or comments; package-level tests should be run for validation.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/benchmark.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/chacha.go -->
# sources/security-integrity/gocryptfs/internal/stupidgcm/chacha.go

- Purpose: Constructs an OpenSSL EVP-backed ChaCha20-Poly1305 AEAD wrapper, verifying the cipher is available at init.
- Important APIs/types/functions: `type stupidChacha20poly1305 struct`, `var _ cipher.AEAD = &stupidChacha20poly1305}`, `var _EVP_chacha20_poly1305 *C.EVP_CIPHER`, `func init()`, `func NewChacha20poly1305(key []byte) cipher.AEAD`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; transforms data through encryption/decryption boundaries; treats invalid internal invariants as fatal/panic conditions. Source size is 1465 bytes across 55 lines, read as part of this work item.
- Dependencies and integration points: standard library: crypto/cipher, log; external/internal modules: golang.org/x/crypto/chacha20poly1305. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/stupidgcm/chacha.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable.
- Test signals: Nearby test signal: `sources/security-integrity/gocryptfs/internal/stupidgcm/chacha_test.go` covers related behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/chacha.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/chacha_test.go -->
# sources/security-integrity/gocryptfs/internal/stupidgcm/chacha_test.go

- Purpose: Test coverage for sources/security-integrity/gocryptfs/internal/stupidgcm, centered on TestStupidChacha20poly1305. It records expected compatibility, error, and boundary behavior for the implementation files nearby.
- Important APIs/types/functions: `func TestStupidChacha20poly1305(t *testing.T)`.
- Control flow and state: transforms data through encryption/decryption boundaries; treats invalid internal invariants as fatal/panic conditions; is non-persistent test/benchmark code. Source size is 321 bytes across 21 lines, read as part of this work item.
- Dependencies and integration points: standard library: testing; external/internal modules: golang.org/x/crypto/chacha20poly1305. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/stupidgcm/chacha_test.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable; test/helper code can mask regressions if expected constants or environment assumptions drift.
- Test signals: Direct test/benchmark declarations: TestStupidChacha20poly1305.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/chacha_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/cipher_suites.go -->
# sources/security-integrity/gocryptfs/internal/stupidgcm/cipher_suites.go

- Purpose: Reports CPU/OpenSSL cipher-suite capability flags used to choose or display accelerated implementations.
- Important APIs/types/functions: `var (`.
- Control flow and state: transforms data through encryption/decryption boundaries. Source size is 756 bytes across 29 lines, read as part of this work item.
- Dependencies and integration points: standard library: runtime; external/internal modules: golang.org/x/sys/cpu. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/stupidgcm/cipher_suites.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/cipher_suites.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/common.go -->
# sources/security-integrity/gocryptfs/internal/stupidgcm/common.go

- Purpose: Implements common OpenSSL AEAD methods for nonce/tag sizing, seal/open dispatch through C helpers, and key wiping state.
- Important APIs/types/functions: `type stupidAEADCommon struct`, `func (c *stupidAEADCommon) Overhead() int`, `func (c *stupidAEADCommon) NonceSize() int`, `func (c *stupidAEADCommon) Seal(dst, iv, in, authData []byte) []byte`, `func (c *stupidAEADCommon) Open(dst, iv, in, authData []byte) ([]byte, error)`, `func (c *stupidAEADCommon) Wipe()`, `func (c *stupidAEADCommon) Wiped() bool`.
- Control flow and state: transforms data through encryption/decryption boundaries; treats invalid internal invariants as fatal/panic conditions. Source size is 1554 bytes across 71 lines, read as part of this work item.
- Dependencies and integration points: standard library: log. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/stupidgcm/common.go` and the declarations listed above.
- Risks and review notes: crypto behavior is on-disk-format sensitive; key derivation, nonce length, padding, and authentication failures must remain stable.
- Test signals: Nearby test signal: `sources/security-integrity/gocryptfs/internal/stupidgcm/common_test.go` covers related behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/stupidgcm/common.go -->
