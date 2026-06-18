# subset-b-007936 research

Grouped research report for the OpenSSL-backed XRootD crypto implementation files in `sources/distributed-fs/xrootd/src/XrdCrypto`. Each section is source-tree aligned and intended for deterministic splitting into the mapped per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslAux.cc -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslAux.cc

## Purpose
Implements OpenSSL utility functions exported through `XrdCryptosslAux.hh`: PBKDF2 key derivation, X.509 certificate and chain verification, PEM bucket/file import/export, TLS peer certificate stack import, ASN.1 time conversion, and OpenSSL `X509_NAME` formatting. This is the glue layer that lets the generic `XrdCrypto` interfaces move OpenSSL objects through XRootD chains, buckets, files, and TLS contexts.

## Important APIs, types, and functions
- Global `sslTrace` is the shared trace sink used by `XrdCryptosslTrace.hh`; `gErrVerifyChain` is a static verification error latch used by chain verification.
- `XrdCryptosslKDFunLen()` returns the default PBKDF2 output length `kSslKDFunDefLen`.
- `XrdCryptosslKDFun()` derives keys with `PKCS5_PBKDF2_HMAC_SHA1`, defaulting to 10,000 iterations and allowing a salt prefix of the form `$$<iterations>$<salt>`.
- `XrdCryptosslX509VerifyCert()` verifies one certificate with another certificate's public key through `X509_verify`.
- `XrdCryptosslX509VerifyChain()` builds an `X509_STORE`, inserts the chain's CA certificate, builds a STACK for the rest, and calls `X509_verify_cert`.
- `XrdCryptosslX509ExportChain()`, `XrdCryptosslX509ToFile()`, and `XrdCryptosslX509ChainToFile()` serialize certificates and optional private keys to an `XrdSutBucket` or PEM file.
- `XrdCryptosslX509ParseFile()`, `XrdCryptosslX509ParseBucket()`, and `XrdCryptosslX509ParseStack()` ingest PEM files, serialized buckets, or `XrdTlsPeerCerts` into an `XrdCryptoX509Chain`.
- `XrdCryptosslASN1toUTC()` converts OpenSSL `ASN1_TIME` UTCTime or GeneralizedTime to epoch seconds.
- `XrdCryptosslNameOneLine()` converts an `X509_NAME` into XRootD's slash-delimited name string.

## Control flow
Key derivation first normalizes the output length, then scans the salt for an iteration override before calling OpenSSL PBKDF2. Chain verification expects a chain with a CA first, inserts that CA into a newly allocated store, pushes remaining certs into a stack, initializes an `X509_STORE_CTX` with the first non-CA cert as target, and verifies. Export paths reorder certificate chains, write the end certificate first, optionally write its private key, then walk issuer-to-subject links until reaching a CA or self-signed certificate. Parse paths read all PEM certificates first, then rewind or open a separate key file to look for a private key and attach it to the matching non-CA certificate by comparing public/private `EVP_PKEY`s. Bucket parsing follows the same two-pass pattern through a memory BIO. TLS stack parsing imports the peer certificate and then the peer chain, manually incrementing OpenSSL refcounts for chain certificates because ownership expectations differ between `SSL_get_peer_chain` and `XrdCryptosslX509`.

## State and persistence behavior
The file does not own durable state except files it writes. `XrdCryptosslX509ChainToFile()` opens the destination with `fopen("w")`, locks the descriptor with `XrdSutFileLocker`, sets permissions to `0600`, and writes proxy-style PEM content. Bucket exports allocate `XrdSutBucket` objects that copy BIO contents via `SetBuf`. Imported OpenSSL objects are handed to `XrdCryptosslX509` wrappers, which then own and later free them. `gErrVerifyChain` is process-global mutable state and is only meaningful around chain verification.

## Dependencies and integration points
Depends on OpenSSL PEM/BIO/X509/EVP APIs, `XrdCryptoX509Chain`, `XrdCryptosslX509`, `XrdCryptosslRSA`, `XrdSutBucket`, `XrdSutFileLocker`, `XrdTlsPeerCerts`, `XrdOucString`, and tracing macros. It is reached directly through `XrdCryptosslFactory` hook accessors and indirectly by certificate, CRL, and request classes for time and name parsing. OpenSSL 3 compatibility appears in public-key comparison via `EVP_PKEY_eq`; older versions use `EVP_PKEY_cmp`.

## Risks and edge cases
Several error paths return without freeing all intermediate OpenSSL allocations, especially in early returns after store/stack/context setup; leak tests should cover failures. `XrdCryptosslX509VerifyCB()` appears inverted: it sets `gErrVerifyChain = 1` when `ok != 0`, and `XrdCryptosslX509VerifyChain()` installs a null callback rather than this function, so reported error codes may be weak. `XrdCryptosslKDFun()` assumes `salt` and `slen` are valid before `memchr(salt+1, ...)`. `XrdCryptosslX509ExportChain()` dereferences `c->PKI()` when `withprivatekey` is true without checking `k`. `XrdCryptosslX509ParseFile(FILE*,...)` calls `fclose(fcer)` on one allocation-failure path even though the caller is documented as owning the FILE. `XrdCryptosslASN1toUTC()` parses raw ASN.1 data and adjusts via `XrdCryptoTZCorr`; date/timezone boundary tests are important.

## Test signals
Useful tests include PBKDF2 known vectors with default and salt-encoded iteration counts; certificate chain verification for valid, wrong issuer, missing CA, and out-of-order chains; PEM chain export/import with and without private key; file output permission and locking behavior; bucket round trips; TLS peer stack refcount ownership under ASAN; ASN.1 UTCTime and GeneralizedTime conversion around 1950/2050 boundaries; and OpenSSL 1.1/3.x key comparison behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslAux.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslAux.hh -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslAux.hh

## Purpose
Declares the OpenSSL auxiliary API used by the cryptossl factory, certificate implementation, CRL implementation, request implementation, and GSI proxy helper implementation. It is the public bridge between generic XRootD crypto abstractions and OpenSSL-specific utility functions.

## Important APIs, types, and functions
- Declares PBKDF2 hooks `XrdCryptosslKDFunLen()` and `XrdCryptosslKDFun()`, with default length macro `kSslKDFunDefLen`.
- Declares X.509 verification, chain export, chain-to-file, parse-file, parse-bucket, and parse-stack APIs.
- Exposes C-linkage helpers `XrdCryptosslX509ToFile()` and the FILE-based `XrdCryptosslX509ParseFile()` overload for external callers needing C ABI symbols.
- Declares ASN.1-to-UTC and `X509_NAME` formatting helpers.
- Declares proxy certificate helpers such as `XrdCryptosslProxyCertInfo()`, `XrdCryptosslSetPathLenConstraint()`, `XrdCryptosslX509CreateProxy()`, request creation/signing, GSI3 proxy checking, and VOMS attribute extraction.
- Defines tracing bit masks `sslTRACE_*` and proxy manipulation error codes `kErrPX_*`.

## Control flow
This header does not implement control flow, but it defines how `XrdCryptosslFactory` wires function pointers into the generic `XrdCryptoFactory` interface. Most certificate helpers are implemented in `XrdCryptosslAux.cc`; proxy/VOMS helpers declared here are implemented in `XrdCryptosslgsiAux.cc`, which is outside this work item but part of the same module.

## State and persistence behavior
The header declares no persistent objects. Its APIs imply file persistence through certificate chain export and proxy creation functions, and memory persistence through returned `XrdSutBucket`, `XrdCryptoX509Req`, `XrdCryptoX509`, and `XrdCryptoRSA` pointers owned by callers.

## Dependencies and integration points
Includes generic `XrdCryptoAux.hh`, `XrdCryptoFactory.hh`, `XrdCryptoX509Chain.hh`, and OpenSSL `asn1.h`. It forward-declares `XrdTlsPeerCerts` so TLS stack parsing can be exposed without pulling TLS internals into every include. Factory methods in `XrdCryptosslFactory.cc` return pointers to these functions.

## Risks and edge cases
Because this header exposes implementation-specific OpenSSL function signatures, ABI changes or OpenSSL type changes can ripple across the cryptossl plugin. The C-linkage functions require careful signature stability. The proxy helper declarations live here while implementations live in a differently named GSI auxiliary file, so build-system omissions can produce link failures only when those hooks are used.

## Test signals
Compile/link tests should verify every declared factory hook resolves. ABI-facing callers should exercise the FILE overloads. Proxy creation and VOMS tests should include the separate GSI implementation file because this header alone can give a misleading picture of coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslAux.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslCipher.cc -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslCipher.cc

## Purpose
Implements `XrdCryptosslCipher`, the OpenSSL EVP-backed symmetric cipher and Diffie-Hellman key agreement implementation for XRootD. It supports local random-key ciphers, imported ciphers, serialized bucket round trips, DH public key exchange, IV management, and encrypt/decrypt buffer sizing.

## Important APIs, types, and functions
- `getFixedDHParams()` returns a process-static OpenSSL `EVP_PKEY` containing hardcoded 3072-bit DH parameters.
- `XrdCheckDH()` validates DH parameters, skipping expensive checks when the fixed parameters match.
- Constructors initialize ciphers from a type/length, from explicit key+IV, from `XrdSutBucket`, or for DH key agreement.
- `Finalize()` completes DH key agreement using a peer public buffer and initializes the symmetric cipher key from the derived secret.
- `Public()` exports DH parameters plus public key hex between `---BPUB---` and `---EPUB---` markers.
- `AsBucket()` serializes type, IV, key bytes, and optional DH p/g/pub/priv bignums into a `kXRS_cipher` bucket.
- `SetIV()`, `RefreshIV()`, and `GenerateIV()` manage IV state.
- `Encrypt()`, `Decrypt()`, and internal `EncDec()` run `EVP_CipherUpdate` and `EVP_CipherFinal_ex`.
- `EncOutLength()`, `DecOutLength()`, and `MaxIVLength()` provide caller buffer sizing hints.

## Control flow
Normal cipher construction resolves the requested cipher name, defaulting to `bf-cbc`, generates random key material with `XrdSutRndm::GetBuffer`, creates an `EVP_CIPHER_CTX`, optionally sets a non-default key length, stores the selected key in the base-class buffer, and generates a fresh IV. Import construction copies caller-provided key and IV, initializes the EVP context, and records whether default key length is used. Bucket construction parses a custom binary layout of seven `kXR_int32` lengths followed by type, IV, key, and DH bignum hex strings, reconstructing the DH key via OpenSSL 3 `OSSL_PARAM` APIs or legacy DH APIs. DH construction without a peer generates a key pair using fixed parameters; with a peer it parses the peer's exported parameters/public key, generates a local key pair, derives a shared secret, and uses that as symmetric key material. `Finalize()` repeats the peer-public parsing and derive flow for objects that already hold local DH state. Encryption/decryption reinitializes the EVP context for every operation with the current key and IV, then performs update/final.

## State and persistence behavior
The class stores mutable `fIV`, IV length, `cipher`, `ctx`, optional DH key `fDH`, default-length flag, and validity flag. Key bytes and type live in the inherited `XrdCryptoCipher` buffer/type storage. Serialized buckets persist sensitive material: they may include symmetric key bytes and DH private key bignums. `Public()` returns a caller-owned heap buffer. `RefreshIV()` returns the internal IV pointer, not a copy. The fixed DH parameter object is a process-static OpenSSL allocation intended to live for process lifetime.

## Dependencies and integration points
Depends on OpenSSL EVP, DH, PEM, BIO, and OpenSSL 3 provider parameter APIs; `XrdSutRndm` for random keys/IVs; `XrdSutBucket` via the base interface; and cryptossl trace macros. `XrdCryptosslFactory` constructs this class for all cipher factory methods and exposes padding support. The DH public export format is a private protocol consumed by the same class on the peer side.

## Risks and edge cases
The default cipher is Blowfish CBC (`bf-cbc`), a legacy algorithm; security-sensitive callers should request modern ciphers if available. `strcpy(cipnam,t)` is bounded only after copying, so cipher names longer than 63 bytes can overflow before `cipnam[63]=0`. Bucket parsing increments `cur` twice after IV copy, which can desynchronize subsequent reads. `AsBucket()` assumes `fDH` is present when extracting DH bignums; a valid non-DH symmetric cipher may dereference a null `fDH`. Serialized buckets contain private material in cleartext and need transport/storage controls. Some BIO and OpenSSL allocation failure paths leak partially allocated resources or continue after null parameter-builder pointers. `Finalize()` frees `ctx` on invalid results but assumes `ctx` was created by the DH constructor. IV generation always uses `EVP_MAX_IV_LENGTH`, not the selected cipher's actual IV length.

## Test signals
Tests should round-trip supported ciphers through constructor, explicit import, and bucket serialization; validate long cipher names under ASAN; verify DH public exchange between two objects with padded and unpadded derivation; compare behavior under OpenSSL 1.1 and 3.x; test `AsBucket()` on non-DH ciphers; check encryption/decryption with refreshed IVs; and fuzz malformed bucket lengths/public key markers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslCipher.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslCipher.hh -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslCipher.hh

## Purpose
Declares `XrdCryptosslCipher`, the OpenSSL implementation of the generic `XrdCryptoCipher` interface. It defines the object state and public methods used for symmetric encryption, IV handling, serialization, and DH key agreement.

## Important APIs, types, and functions
- Private state includes `fIV`, `lIV`, `cipher`, `ctx`, `fDH`, `deflength`, and `valid`.
- Constructors support generated ciphers, imported key/IV ciphers, bucket-imported ciphers, DH key agreement, and copy construction.
- `Finalize()` completes DH agreement after receiving a peer public key.
- `Cleanup()` releases DH temporary state.
- `IsSupported()` queries OpenSSL cipher availability.
- `EncOutLength()`, `DecOutLength()`, `Public()`, `AsBucket()`, `IV()`, `IsDefaultLength()`, and `MaxIVLength()` expose metadata and serialization.
- `SetIV()`, `Encrypt()`, `Decrypt()`, and `RefreshIV()` mutate/use cipher state.

## Control flow
The header defines the operational contract used by the implementation: construct to set valid state, optionally exchange public DH buffers and finalize, then call encrypt/decrypt with caller-sized buffers. The static support check lets the factory reject unsupported algorithms before object creation.

## State and persistence behavior
Instances hold OpenSSL contexts and keys. The `IV()` accessor and `RefreshIV()` expose internal IV memory, so callers must not free or mutate it unexpectedly. `AsBucket()` creates persistent transport state for the cipher; because private key bytes can be serialized by the implementation, buckets must be treated as secrets.

## Dependencies and integration points
Inherits from `XrdCryptoCipher` and includes OpenSSL `evp.h` and `dh.h`. It is constructed only through `XrdCryptosslFactory` in normal plugin use, but the class is also visible to nearby implementation files and tests.

## Risks and edge cases
The class exposes raw pointers for IV and public buffers, so ownership conventions must be documented and tested. The header's private helper `PrintPublic()` is debug-only but still part of class shape. The commented-out `kDHMINBITS` notes historical dynamic DH generation; reviewers should look at the implementation before re-enabling any dynamic parameter generation.

## Test signals
Interface tests should verify `IsValid()` after all constructors, `Public()` ownership/length behavior, IV length reporting, copy construction, and factory downcast assumptions in `XrdCryptosslFactory::Cipher(const XrdCryptoCipher&)`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslCipher.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslFactory.cc -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslFactory.cc

## Purpose
Implements the cryptossl plugin factory, initializing OpenSSL/TLS support and exposing OpenSSL-backed implementations for ciphers, message digests, RSA keys, X.509 certificates, CRLs, requests, chain helpers, and proxy/VOMS helpers through the generic `XrdCryptoFactory` API.

## Important APIs, types, and functions
- Static `Logger` and `eDest` back the cryptossl trace destination.
- `XrdCryptosslFactory::XrdCryptosslFactory()` calls `XrdTlsContext::Init()` and seeds OpenSSL RAND with `XrdSutRndm` bytes.
- `SetTrace()` creates/updates global `sslTrace` and maps `sslTRACE_*` flags to the trace mask.
- Constructor families return `XrdCryptosslCipher`, `XrdCryptosslMsgDigest`, `XrdCryptosslRSA`, `XrdCryptosslX509`, `XrdCryptosslX509Crl`, and `XrdCryptosslX509Req` after validity checks.
- Hook accessors return function pointers from `XrdCryptosslAux.cc` and `XrdCryptosslgsiAux.cc`.
- `XrdVERSIONINFO(XrdCryptosslFactoryObject,cryptossl)` and `extern "C" XrdCryptosslFactoryObject()` provide plugin entry/version symbols.

## Control flow
The factory singleton is lazily instantiated in `XrdCryptosslFactoryObject()`. Its constructor initializes TLS/OpenSSL process state and aborts on initialization failure. Each creation method allocates a concrete implementation, checks the relevant validity signal (`IsValid()` or `Opaque()`), returns the object on success, or deletes it and returns null on failure. Hook methods are simple function-pointer returns and let higher-level XRootD code invoke auxiliary operations without linking to concrete classes.

## State and persistence behavior
The factory is a static process-lifetime singleton. `SetTrace()` lazily allocates global `sslTrace`; it is not freed in this file. Factory-created objects own their OpenSSL state individually. The constructor seeds OpenSSL's process-global random state.

## Dependencies and integration points
Includes every cryptossl concrete header, OpenSSL `rand.h`/`ssl.h`, `XrdTlsContext`, `XrdSutRndm`, XRootD logging/tracing, and version macros. The factory object is the external plugin boundary and is identified as provider `"ssl"` with ID `1`.

## Risks and edge cases
The factory uses C-style downcasts in copy constructors (`*((XrdCryptosslCipher *)&c)` and RSA equivalent), so passing a non-cryptossl implementation through this factory is undefined behavior. The factory aborts the process if `XrdTlsContext::Init()` fails. `DebugON` is defined in the header, not here, which can cause multiple-definition risks if included in multiple translation units. Trace state is global and not synchronized beyond pointer assignment.

## Test signals
Plugin loading tests should verify `XrdCryptosslFactoryObject()` returns a stable singleton and version symbol. Factory tests should cover valid/invalid algorithm names, all constructor overloads, failure cleanup, trace mask mapping, and hook function pointer non-nullness. Cross-provider copy calls should be guarded or tested for expected rejection if the generic API allows them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslFactory.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslFactory.hh -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslFactory.hh

## Purpose
Declares `XrdCryptosslFactory`, the concrete `XrdCryptoFactory` subclass for the OpenSSL provider. It is the main API surface through which the rest of XRootD requests cryptographic objects and helper hooks.

## Important APIs, types, and functions
- Defines `XrdCryptosslFactoryID` as `1` and declares provider class `XrdCryptosslFactory`.
- Declares trace control, KDF hook retrieval, cipher constructors, digest constructors, RSA constructors, X.509/CRL/request constructors, chain helper hooks, and proxy helper hooks.
- Defines `DebugON = 1` at header scope.

## Control flow
No implementation control flow exists in the header, but the method set mirrors the virtual factory contract. The implementation returns concrete objects or function pointers matching these declarations.

## State and persistence behavior
Instances inherit provider name/ID state from `XrdCryptoFactory`. The header itself declares no members. `DebugON` at header scope creates global state in every translation unit that includes it unless build/link behavior hides it.

## Dependencies and integration points
Includes `XrdCryptoFactory.hh` and `XrdSysPthread.hh`. It is consumed by the factory implementation and plugin loader-facing code. The hook return types are defined in the generic crypto factory headers.

## Risks and edge cases
The non-`extern` `int DebugON = 1;` in a header is a notable ODR/link risk in C++ and may rely on historical compiler/linker behavior. Broad virtual API exposure means any signature mismatch with generic factory typedefs breaks plugin integration.

## Test signals
Build tests with modern compilers and `-fno-common`-style strictness should catch multiple-definition problems. Interface tests should instantiate the factory via plugin symbol and ensure every declared virtual override is callable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslFactory.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslMsgDigest.cc -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslMsgDigest.cc

## Purpose
Implements `XrdCryptosslMsgDigest`, an OpenSSL EVP message digest wrapper for the generic `XrdCryptoMsgDigest` interface. It supports digest algorithm lookup, incremental update, finalization into the inherited buffer, and reset.

## Important APIs, types, and functions
- Constructor initializes type and calls `Init()`.
- Destructor finalizes any valid digest context and destroys `mdctx`.
- `IsSupported()` checks `EVP_get_digestbyname`.
- `Init()` selects the requested digest or default `sha256`, allocates an `EVP_MD_CTX`, and initializes it.
- `Reset()` finalizes/discards current state, clears the output buffer, destroys the old context, and reinitializes.
- `Update()` calls `EVP_DigestUpdate`.
- `Final()` calls `EVP_DigestFinal_ex`, stores the result in the base buffer, and emits debug output.

## Control flow
Construction sets the digest type to null, then `Init()` chooses caller type or default. Updates are accepted when `Type()` is set. Finalization stores the digest bytes in the inherited buffer for later access such as hex string conversion. Reset finalizes the existing context even if the caller never asked for the digest, then recreates a new context.

## State and persistence behavior
The object owns `EVP_MD_CTX *mdctx`, a `valid` flag, and inherited type/output buffer state. No durable persistence exists. The digest result persists in the object's base buffer after `Final()` until reset/destruction.

## Dependencies and integration points
Depends on OpenSSL EVP digest APIs, `XrdCryptoMsgDigest`, generic crypto helpers, and trace macros. `XrdCryptosslFactory` constructs this class and uses `IsSupported()`.

## Risks and edge cases
`Update()` checks `Type()` rather than `valid` or `mdctx`, so a failed `Init()` that left a type string could lead to use of a null/destroyed context. `Init()` does not check `EVP_MD_CTX_create()` before `EVP_DigestInit_ex`. Destructor and reset both call finalization to discard state, which can fail silently or mutate OpenSSL error state. The error message in `Init()` has a typo but also uses `PRINT` rather than returning structured error details.

## Test signals
Tests should compare SHA-256 and other algorithm outputs to known vectors, validate unsupported digest handling, call `Update()` and `Final()` in invalid states under ASAN, reset between algorithms, and verify factory support queries match construction results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslMsgDigest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslMsgDigest.hh -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslMsgDigest.hh

## Purpose
Declares the OpenSSL implementation of `XrdCryptoMsgDigest`, providing the small object interface for digest support checks, reset/update/final operations, and validity.

## Important APIs, types, and functions
- Private `valid` flag and `EVP_MD_CTX *mdctx` hold OpenSSL digest state.
- `Init()` is a private helper for constructor and reset.
- Public constructor/destructor, `IsValid()`, static `IsSupported()`, `Reset()`, `Update()`, and `Final()` implement the generic digest contract.

## Control flow
The header exposes the standard incremental digest lifecycle: construct or reset, update with one or more buffers, and finalize to populate inherited output state.

## State and persistence behavior
Digest state is in memory only. The class owns its OpenSSL context and inherited digest result buffer.

## Dependencies and integration points
Includes OpenSSL `evp.h` and `XrdCryptoMsgDigest.hh`. It is instantiated by `XrdCryptosslFactory` and used wherever generic `XrdCryptoMsgDigest` pointers are consumed.

## Risks and edge cases
Raw context ownership means copy behavior is intentionally absent; accidental copying by value would be unsafe if ever introduced. Validity is exposed but callers still need to observe return codes from `Update()` and `Final()`.

## Test signals
Header-level tests should include construction through the factory, `IsSupported()` for known and invalid digest names, and compile checks that consumers can use only the generic base methods where intended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslMsgDigest.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslRSA.cc -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslRSA.cc

## Purpose
Implements `XrdCryptosslRSA`, the OpenSSL EVP-backed RSA key wrapper. It handles key generation, public/private PEM import/export, copy construction, output size calculation, and RSA encryption/decryption/signature-recovery style operations.

## Important APIs, types, and functions
- `XrdCheckRSA()` validates an `EVP_PKEY` with `EVP_PKEY_check`.
- Constructor `(bits, exp)` generates a key pair with minimum/default bit handling and odd exponent enforcement.
- Constructor `(pub,lpub)` imports a PEM public key.
- Constructor `(EVP_PKEY*, check)` adopts an existing key and marks it complete or public depending on validation mode.
- Copy constructor clones through PEM serialization, preserving public-only or private key status.
- `ImportPublic()` and `ImportPrivate()` parse PEM from memory BIOs.
- `GetPublen()`, `ExportPublic()`, `GetPrilen()`, and `ExportPrivate()` size and write PEM buffers.
- `EncryptPublic()`/`DecryptPrivate()` use RSA OAEP padding.
- `EncryptPrivate()`/`DecryptPublic()` use PKCS#1 padding through `EVP_PKEY_sign` and `EVP_PKEY_verify_recover`.
- `GetOutlen()` computes encrypted output capacity based on OAEP payload limits.

## Control flow
Key generation creates a BIGNUM exponent, initializes an RSA keygen context, sets key bits and exponent, generates `fEVP`, then validates the key before marking status complete. Public/private import writes caller bytes into a BIO and reads the corresponding PEM key. Copy construction detects whether the original has a private exponent, writes either public or private PEM to a BIO, and reads it back into a fresh `EVP_PKEY`. Encryption methods validate buffers, create an operation-specific `EVP_PKEY_CTX`, set padding, split input into RSA-sized chunks, and append each encrypted/decrypted block into caller output.

## State and persistence behavior
The object owns `EVP_PKEY *fEVP` and cached exported public/private PEM lengths (`publen`, `prilen`). It stores status in the inherited `XrdCryptoRSA` state. Export methods write PEM into caller-owned buffers and null-terminate. No file persistence occurs in this file, but exported private PEM is sensitive data.

## Dependencies and integration points
Depends on OpenSSL EVP/BIO/PEM/ERR APIs, OpenSSL 3 `core_names.h` for private exponent detection, trace macros, and `XrdCryptoRSA` constants/status. Certificates wrap public keys with `XrdCryptosslRSA(EVP_PKEY*, false)` and attach private keys through this class. The factory exposes all constructors.

## Risks and edge cases
Default constructor does not initialize `fEVP` to null before generation; if early allocation fails, destructor could see indeterminate state unless base construction or compiler behavior masks it. `ImportPrivate()` passes `&fEVP` to `PEM_read_bio_PrivateKey` while a public key may already be stored, requiring careful OpenSSL ownership semantics. Export methods ignore the caller-provided length parameter and assume sufficient space. `GetOutlen()` divides by `EVP_PKEY_size(fEVP)-42`; invalid or very small keys can break this. Encryption loops have non-obvious truncation conditions and may silently return partial data after logging. Private-key "encryption" is signature-like and uses PKCS#1 v1.5 padding; callers should not treat it as confidentiality.

## Test signals
Tests should cover key generation at below-minimum/default/custom sizes, odd/even exponents, public/private PEM round trips, copy of public-only and complete keys, invalid PEM import, OAEP encrypt/decrypt over multi-block input, private/public recover paths, too-small output buffers, ASAN/UBSAN early-failure construction, and OpenSSL 3 private exponent detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslRSA.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslRSA.hh -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslRSA.hh

## Purpose
Declares `XrdCryptosslRSA`, the OpenSSL concrete implementation of the generic RSA interface.

## Important APIs, types, and functions
- Private state includes `EVP_PKEY *fEVP`, `publen`, and `prilen`.
- Constructors cover generated keys, imported public PEM, adopted `EVP_PKEY`, and copy construction.
- `Opaque()` exposes the underlying `EVP_PKEY`.
- Export/import and encryption/decryption methods implement the `XrdCryptoRSA` contract.

## Control flow
The header defines a lifecycle where keys are generated or imported, optionally completed with private material, exported as PEM, and used for RSA operations. `Opaque()` is the bridge used by certificate code and OpenSSL helper code.

## State and persistence behavior
Instances own an OpenSSL key pointer. Export methods expose public and private key material into caller buffers; `Opaque()` exposes internal ownership-sensitive state.

## Dependencies and integration points
Inherits from `XrdCryptoRSA` and includes OpenSSL `evp.h`. It is used by certificates for `PKI()` objects and by the factory for RSA construction.

## Risks and edge cases
The raw `Opaque()` pointer makes ownership conventions critical: some constructors adopt `EVP_PKEY*`, and callers must not double-free. Export length cache invalidation must remain correct after imports.

## Test signals
Compile and runtime tests should verify key ownership with certificate wrappers, status transitions from public to complete, and generic-interface calls through `XrdCryptoRSA *`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslRSA.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslTrace.hh -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslTrace.hh

## Purpose
Defines tracing macros for the cryptossl implementation and declares the global `sslTrace` pointer used by source files in this plugin.

## Important APIs, types, and functions
- `QTRACE(act)` checks whether `sslTrace` is set and whether the requested `cryptoTRACE_*` bit is enabled.
- `PRINT(y)`, `TRACE(act,x)`, `DEBUG(y)`, and `EPNAME(x)` wrap `XrdOucTrace` logging and endpoint names when `NODEBUG` is not defined.
- Under `NODEBUG`, macros compile to empty definitions.
- Declares `extern XrdOucTrace *sslTrace`.

## Control flow
At runtime, implementation files set an endpoint with `EPNAME`, then call `DEBUG`, `TRACE`, or `PRINT`. The macros route messages through `sslTrace->Beg(epname)`, stream to `std::cerr`, and call `sslTrace->End()`. `SetTrace()` in the factory configures the pointer and mask.

## State and persistence behavior
The header declares a process-global trace pointer; the definition is in `XrdCryptosslAux.cc`. Logging is transient except for whatever backend the `XrdSysError` logger writes to.

## Dependencies and integration points
Includes `XrdOucTrace.hh`, `XrdCryptoAux.hh`, and in debug builds `XrdSysHeaders.hh`. It relies on `cryptoTRACE_*` masks from generic crypto headers while the factory maps `sslTRACE_*` flags.

## Risks and edge cases
Macros assume an `epname` symbol exists for `PRINT`, so callers should use `EPNAME` in functions that log. In non-debug builds, `QTRACE(x)` expands to nothing, which may be unsafe if used in expression contexts. Global trace pointer access is not synchronized.

## Test signals
Build tests should cover debug and `NODEBUG` configurations. Runtime trace tests should call factory `SetTrace()` with notify/debug/dump masks and verify representative messages do not crash when `sslTrace` is null.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslTrace.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslX509.cc -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslX509.cc

## Purpose
Implements `XrdCryptosslX509`, the OpenSSL-backed X.509 certificate wrapper. It loads certificates from files, buckets, or existing `X509*`, exposes subject/issuer/hash/serial/validity metadata, classifies certificate type, manages public/private key association, serializes certificates, verifies signatures, dumps extensions, and matches DNS SANs for host certificates.

## Important APIs, types, and functions
- Constructors load from certificate/key files, `XrdSutBucket`, or adopted `X509 *`.
- `CertType()` classifies initialized certs as EEC, CA, proxy, unknown, and detects RFC/GSI3/legacy proxy variants.
- `SetPKI()` adopts a consistent private/public `EVP_PKEY` into the certificate's `XrdCryptosslRSA`.
- `NotBefore()` and `NotAfter()` lazily convert OpenSSL validity times.
- `Subject()`, `Issuer()`, `SubjectHash()`, and `IssuerHash()` lazily cache names and default/old hashes.
- `SerialNumber()` and `SerialNumberString()` expose serial in integer and hex string form.
- `GetExtension()` finds an extension by short name or OID text.
- `Export()` serializes the certificate to a `kXRS_x509` bucket.
- `Verify()` verifies this certificate with a reference certificate public key.
- `DumpExtensions()`, `FillUnknownExt()`, and `Asn1PrintInfo()` provide recursive ASN.1 debug dumping.
- `MatchesSAN()` checks DNS subject alternative names against a requested FQDN.

## Control flow
The file constructor validates file presence, opens with `open`/`fdopen`, reads PEM certificate, caches source path, parses subject/issuer/type, then optionally reads a private key file after enforcing that it is regular and not group/world writable beyond allowed `0640`. If no private key is attached, it wraps the certificate public key as a public-only RSA object. Bucket and raw-X509 constructors deserialize/adopt, then follow the same metadata and public-key initialization. Certificate type detection first checks `basicConstraints` for CA, then detects proxy naming where issuer equals subject without final CN, then parses `proxyCertInfo` or calls `XrdCryptosslX509CheckProxy3`, falling back to legacy CN names `proxy` and `limited proxy`. Metadata getters are lazy and cache strings/time values. SAN matching obtains `subjectAltName`, requires an EEC cert, iterates DNS names only, validates IA5 type, length, and absence of embedded NULs, then calls the inherited/shared hostname matcher.

## State and persistence behavior
The object owns `X509 *cert`, optional serialized `XrdSutBucket *bucket`, and `XrdCryptoRSA *pki`. It caches validity times, subject/issuer strings, old and new hashes, source filename, and proxy type. Destructor frees the certificate and key but does not visibly free `bucket`, so repeated `Export()` cache ownership should be reviewed. File constructor reads from disk but does not write. `Export()` creates and caches a bucket from memory BIO contents.

## Dependencies and integration points
Depends on OpenSSL X509/X509v3/BIO/EVP/PEM APIs, `XrdCryptosslRSA`, `XrdCryptosslAux` utilities, GSI proxy checker declared in aux and implemented elsewhere, trace macros, and generic `XrdCryptoX509`. It is constructed by the factory, by chain parsers in `XrdCryptosslAux.cc`, and by TLS peer stack import.

## Risks and edge cases
Private key consistency is checked only by creating an RSA wrapper around the key; it does not compare the private key to the certificate public key in the file constructor, unlike chain parse helper flows. `BitStrength()` calls `X509_get_pubkey(cert)` without freeing the returned `EVP_PKEY`, causing a leak on each call. `MatchesSAN()` returns false without freeing `gens` when the certificate type is not EEC. Several BIO error paths return without freeing BIOs. `SerialNumber()` converts arbitrary-size serials through decimal string to `strtoll`, which can overflow. Proxy type parsing depends on slash-formatted subject strings. `Export()` caches and returns an owned bucket pointer with ambiguous caller ownership.

## Test signals
Tests should load EEC, CA, RFC proxy, GSI3 proxy, and legacy proxy certificates; check private key permission rejection; verify key/cert mismatch behavior; exercise subject/issuer hash old/default values; export/import bucket round trips; SAN matching for exact, wildcard, embedded NUL, overlong, non-DNS, non-EEC, and absent-SAN cases; run leak checks around `BitStrength()`, `MatchesSAN()`, and export error paths; and verify serial overflow handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslX509.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslX509.hh -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslX509.hh

## Purpose
Declares `XrdCryptosslX509`, the OpenSSL concrete implementation of `XrdCryptoX509`.

## Important APIs, types, and functions
- Constructors support loading from certificate/key paths, serialized buckets, and existing `X509 *`.
- Public methods expose opaque OpenSSL data, extension dumping, PKI access/mutation, bucket export, source file, proxy type, bit strength, serials, validity, subject/issuer names and hashes, SAN matching, extension lookup, and signature verification.
- Private members store `X509 *cert`, cached validity/name/hash/source/bucket/key/proxy state, ASN.1 dump helpers, and static proxy type names.

## Control flow
The header defines the full certificate wrapper contract used by the factory, chain helpers, CRL helpers, and proxy code. The implementation lazily fills most metadata through the public getters.

## State and persistence behavior
Objects own an OpenSSL certificate and RSA wrapper, cache computed metadata, and may cache an exported bucket. `Opaque()` exposes the raw `X509 *` for OpenSSL calls elsewhere.

## Dependencies and integration points
Includes `XrdCryptoX509.hh` plus OpenSSL X509v3/BIO/EVP headers. It is the central OpenSSL certificate type used by chain parsing, verification, CRL verification, and proxy helper code.

## Risks and edge cases
Raw opaque pointer access and constructor adoption of `X509 *` require exact ownership discipline. Cached strings can become stale only if the underlying cert were mutated through `Opaque()`, which the interface permits. `PKI()` exposes mutable key wrapper state.

## Test signals
Compile tests should verify base-class polymorphism and OpenSSL type availability. Runtime tests should cover each constructor, `Opaque()` interop with OpenSSL verification, lazy getter idempotence, and ownership on copied/up-refed certificates from TLS stacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslX509.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslX509Crl.cc -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslX509Crl.cc

## Purpose
Implements `XrdCryptosslX509Crl`, the OpenSSL-backed certificate revocation list wrapper. It loads CRLs from files, FILE handles, or CA certificate distribution-point URIs, caches revoked serials, exposes validity/issuer metadata, verifies CRL signatures, checks revocation, writes CRLs to files, and dumps diagnostic information.

## Important APIs, types, and functions
- Constructors call `Init()`, `Init(FILE*)`, or parse a CA certificate's `crlDistributionPoints` extension and call `InitFromURI()`.
- `Init()` opens local CRL files and delegates to FILE-based initialization.
- `InitFromURI()` downloads a CRL with `wget`, detects PEM/DER, optionally runs `openssl crl -inform DER`, loads the resulting PEM, and removes temporary files.
- `ToFile()` writes PEM CRL content.
- `GetFileType()` detects PEM versus DER by scanning the first non-empty line.
- `hasCriticalExtension()` checks for critical CRL extensions.
- `LoadCache()` iterates revoked entries and stores serials in an `XrdSutCache`.
- `LastUpdate()`, `NextUpdate()`, `Issuer()`, and `IssuerHash()` lazily cache metadata.
- `Verify()` checks the CRL signature against a CA certificate key.
- `IsRevoked()` overloads check integer or string serial numbers against the cache and revocation time.
- `Dump()` logs a human-readable CRL summary.

## Control flow
Local load opens the CRL file, reads a PEM `X509_CRL`, stores the source path, computes issuer, and loads the revocation cache. CA-based construction extracts `crlDistributionPoints`, prints it to a BIO, tokenizes for `URI:` entries, and tries each URI until one initializes. URI initialization builds a temp path under `TMPDIR` or `/tmp`, shell-executes `wget`, checks file type, optionally shell-executes OpenSSL conversion for DER, loads the PEM, then unlinks temporary files. Revocation checks warn on expired CRLs, look up the serial tag in the cache, and compare the requested time to the cached revocation time.

## State and persistence behavior
The object owns `X509_CRL *crl`, cached last/next update times, issuer hashes, source file path, CRL URI, count of revoked certificates, and an `XrdSutCache` of serial entries. URI loads persist temporary files briefly in `TMPDIR` or `/tmp` and remove them after load/conversion. `ToFile()` persists PEM content to a caller-owned FILE.

## Dependencies and integration points
Depends on OpenSSL X509_CRL/PEM/BN APIs, `XrdCryptosslAux` for ASN.1 time and name conversion, `XrdCryptosslRSA`, `XrdSutCache`, tracing, shell tools `wget` and `openssl`, and CA certificate extension lookup from `XrdCryptoX509`. The factory constructs CRLs directly from file/URI option or CA certificate.

## Risks and edge cases
`InitFromURI()` builds shell commands by concatenating URI and file paths without quoting, creating command-injection and whitespace/path risks if URI input is untrusted. It relies on external `wget` and `openssl` availability. `LoadCache()` sets `cent->mtime` to the revocation time and then immediately overwrites `cent->mtime = kCE_ok`; this appears to lose revocation time and likely should set `cent->status`, making `IsRevoked()` unreliable. Integer serial lookup uses lowercase `%x`, while `LoadCache()` stores `BN_bn2hex` uppercase strings, causing mismatch. `Verify()` does not free `X509_get_pubkey()` result. `hasCriticalExtension()` assumes `crl` is non-null. Error paths around BIO and malloc allocation are sparse.

## Test signals
Tests should load PEM and DER CRLs, verify against correct/wrong CA certs, exercise CA distribution point URI parsing with safe local fixtures, check temp cleanup, validate critical extension detection, test revoked serial lookup with upper/lowercase and integer/string paths, assert revocation time semantics, run without `wget`/`openssl`, and include command-injection regression tests if URI input can come from certificates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslX509Crl.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslX509Crl.hh -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslX509Crl.hh

## Purpose
Declares `XrdCryptosslX509Crl`, the OpenSSL implementation of `XrdCryptoX509Crl`.

## Important APIs, types, and functions
- Constructors support file path with option, FILE handle, and CA certificate distribution-point discovery.
- Public methods expose validity, opaque CRL pointer, dump/source metadata, update times, issuer names/hashes, revocation checks, signature verification, PEM output, and critical-extension detection.
- Private helpers handle file-type detection, cache loading, file/FILE initialization, and URI initialization.
- Private state stores `X509_CRL *crl`, cached times, issuer strings/hashes, source/URI strings, revoked count, and `XrdSutCache`.

## Control flow
The header defines a CRL lifecycle of construction/loading, metadata access, revocation lookup, optional verification, and optional file output.

## State and persistence behavior
Objects own a CRL and an in-memory cache. URI initialization and `ToFile()` can touch the filesystem through implementation methods. `Opaque()` exposes the raw `X509_CRL *`.

## Dependencies and integration points
Includes OpenSSL X509v3, `XrdSutCache`, and generic `XrdCryptoX509Crl`. It forward-declares `XrdCryptoX509` for CA-based construction and verification.

## Risks and edge cases
Raw `Opaque()` exposes mutable internal CRL state. Cache correctness is central to `IsRevoked()` behavior. The constructor overload with `opt` implies file/URI selection but the enum/meaning is not self-documenting in this header.

## Test signals
Interface tests should cover all constructor overloads, null/invalid CRL behavior for every getter, `Opaque()` interop with OpenSSL, and FILE-based construction without double-closing caller handles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslX509Crl.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslX509Req.cc -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslX509Req.cc

## Purpose
Implements `XrdCryptosslX509Req`, the OpenSSL-backed certificate signing request wrapper. It imports requests from serialized buckets or existing `X509_REQ *`, exposes subject and subject hashes, looks up requested extensions, serializes requests, and verifies request signatures.

## Important APIs, types, and functions
- Bucket constructor reads PEM request content from an `XrdSutBucket` via memory BIO.
- Raw constructor adopts an `X509_REQ *`.
- Destructor frees the request and key wrapper.
- `Subject()` formats and caches request subject.
- `SubjectHash()` returns default or old OpenSSL hash of the subject name.
- `GetExtension()` searches CSR extensions by OpenSSL short name or OID text.
- `Export()` serializes the request into a `kXRS_x509_req` bucket.
- `Verify()` calls `X509_REQ_verify()` with the CSR public key.

## Control flow
Both constructors initialize empty caches, validate input, set `creq`, compute subject, extract the public key with `X509_REQ_get_pubkey`, and wrap it in a public-only `XrdCryptosslRSA`. Extension lookup gets the CSR extension stack, selects NID or text matching mode, and scans until a match. Export writes the request PEM to a memory BIO, copies it into a cached bucket, and returns it. Verification obtains the request public key and checks the CSR signature.

## State and persistence behavior
The object owns `X509_REQ *creq`, cached subject/hash strings, optional cached export bucket, and public key wrapper `pki`. No direct file persistence exists. `Export()` caches the bucket for repeated calls; destructor frees `creq` and `pki` but does not visibly free `bucket`.

## Dependencies and integration points
Depends on OpenSSL X509_REQ/BIO/PEM/X509v3 APIs, `XrdCryptosslRSA`, `XrdCryptosslAux` name formatting, and trace macros. The factory constructs this class from buckets, while proxy creation/signing helpers in `XrdCryptosslgsiAux.cc` create and consume request objects.

## Risks and edge cases
Bucket constructor error paths leak the memory BIO on write/read failures. `GetExtension()` does not free the stack returned by `X509_REQ_get_extensions()`, which OpenSSL expects callers to free. `Verify()` calls `X509_REQ_get_pubkey(creq)` without freeing the returned key. Export error paths can leak BIOs. Cached bucket ownership is ambiguous and likely leaked in the destructor.

## Test signals
Tests should import/export CSR buckets, verify valid and tampered CSR signatures, search extensions by short name and numeric OID, run leak checks around extension lookup and verification, test null/empty bucket behavior, and exercise repeated `Export()` calls for ownership/caching semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslX509Req.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslX509Req.hh -->
# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslX509Req.hh

## Purpose
Declares `XrdCryptosslX509Req`, the OpenSSL implementation of `XrdCryptoX509Req` for certificate signing requests.

## Important APIs, types, and functions
- Constructors support serialized buckets and existing `X509_REQ *`.
- Public methods expose opaque CSR pointer, public key wrapper, bucket export, subject, subject hash, extension lookup, and signature verification.
- Private state stores `X509_REQ *creq`, cached subject/hash strings, cached bucket, and `XrdCryptoRSA *pki`.

## Control flow
The header defines a CSR lifecycle of import/adoption, metadata lookup, optional extension access, export, and signature verification.

## State and persistence behavior
Objects own an OpenSSL CSR and RSA wrapper and may cache an export bucket. `Opaque()` exposes raw CSR state to proxy signing helpers and other OpenSSL code.

## Dependencies and integration points
Includes `XrdCryptoX509Req.hh`, OpenSSL X509v3, and BIO headers. It integrates with the factory and proxy creation/signing helpers.

## Risks and edge cases
Raw pointer ownership is central: adopted `X509_REQ *` is freed by this object, and callers using `Opaque()` must not mutate/free it unexpectedly. Cached bucket lifetime is not explicit in the API.

## Test signals
Compile and runtime tests should cover generic base pointer use, ownership of adopted requests, bucket export/import idempotence, and `PKI()` status for public-only request keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslX509Req.hh -->
