# Group Research: group_1626_plan9_sources_os_plan9_plan9_sys_src_cmd_unix_drawterm_libsec_tlsha_2f78aa0ceca4

Scope: `Docs/research_subset_a.md` includes `sources/os/plan9/plan9`. All listed files were read completely. This group covers drawterm TLS/X.509/secstore/auth plumbing, machine-dependent drawterm support, legacy Plan 9 DES/netkey tooling, and u9fs authentication plus 9P wire conversion.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/tlshand.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/tlshand.c

Implements TLS 1.0 / SSL3 handshake orchestration for drawterm over Plan 9's `#a/tls` record-layer device. Public entry points `tlsServer` and `tlsClient` create a TLS channel, bind an existing fd to it, open the hand/data files, run the handshake, then return the data fd.

Major pieces:
- `TlsConnection`, `Msg`, `TlsSec`, `Bytes`, and `Ints` model handshake state, variable-length vectors, selected algorithms, randoms, transcript hashes, and security material.
- `tlsServer2` handles server handshake: receives ClientHello, chooses cipher/compressor, sends ServerHello/Certificate/ServerHelloDone, receives RSA ClientKeyExchange, installs record secrets, verifies Finished, sends Finished.
- `tlsClient2` sends ClientHello, receives server messages, extracts certificate, performs RSA key exchange, installs secrets, and validates server Finished.
- `msgSend`, `msgRecv`, `tlsReadN`, `msgClear`, and `msgPrint` encode/decode handshake records, including compatibility handling for SSL2-format ClientHello.
- Cipher negotiation is restricted to enabled kernel TLS algorithms from `#a/tls/encalgs` and `#a/tls/hashalgs`; built-in suites are RC4-MD5, RC4-SHA1, and 3DES-SHA1.
- Security code implements TLS PRF, SSL3 PRF, Finished verification, master-secret/key expansion, PKCS#1 RSA encryption/decryption, and factotum-backed server private-key use.

Important dependencies:
- `#a/tls` control/hand/data files provide the record protocol and symmetric crypto.
- `X509toRSApub` extracts RSA public keys from certificates.
- `/mnt/factotum/rpc` signs/decrypts with the server private key.
- `md5`, `sha1`, HMAC helpers, `rsaencrypt`, and mpint routines come from Plan 9 libsec/libmp.

Notable behavior and risks:
- No client certificate support is implemented; server-side `TLSconn.cert` is cleared after handshake.
- Only RSA key exchange is supported; DHE suites are enumerated but not implemented.
- TLS version support is SSL3 and TLS 1.0 only.
- `serverMasterSecret` deliberately continues with random premaster data on RSA padding/version failure to reduce oracle behavior.
- `tlsConnectionFree` assumes a non-nil connection and clears/frees it; callers only pass allocated connections in normal paths.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/tlshand.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/x509.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/x509.c

Provides a self-contained BER/ASN.1 encoder/decoder plus X.509 certificate parsing and RSA key/certificate helpers used by drawterm TLS.

Major pieces:
- ASN.1 core types: `Elem`, `Tag`, `Value`, `Bytes`, `Ints`, `Bits`, and `Elist`.
- Decoding path: `decode`, `ber_decode`, `tag_decode`, `length_decode`, `value_decode`, `octet_decode`, and `seq_decode`.
- Encoding path: `encode`, `enc`, `val_enc`, `uint7_enc`, and `int_enc`.
- Helpers identify expected ASN.1 shapes: `is_seq`, `is_set`, `is_int`, `is_bigint`, `is_bitstring`, `is_octetstring`, `is_oid`, `is_string`, and `is_time`.
- X.509 parsing uses `decode_cert`, `parse_name`, and `parse_alg` to extract serial, issuer, validity, subject, subject public key, signature algorithm, and signature.
- RSA helpers decode public/private keys (`decode_rsapubkey`, `decode_rsaprivkey`, `asn1toRSApriv`), convert ASN.1 INTEGERs to mpints, and verify PKCS#1-padded signatures.
- Public APIs include `X509toRSApub`, `X509verify`, `X509gen`, `X509req`, `asn1dump`, and `X509dump`.

Important dependencies:
- Plan 9 mpint/RSA APIs (`RSApub`, `RSApriv`, `mptobe`, `betomp`, `mpexp`, `rsadecrypt`).
- Libsec digest functions `md5` and `sha1`.

Notable behavior and risks:
- The ASN.1 implementation is partial and tuned for certificate/key use, not a complete DER/BER framework.
- Certificate verification only verifies a signature against a supplied RSA public key; it does not implement chain validation, time checks, revocation, or hostname matching.
- Certificate/request generation uses MD5-based signatures in this legacy code.
- `X509toRSApub` optionally returns only the first CN-like subject component by truncating at a comma.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/x509.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/main.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/main.c

Bootstraps drawterm's hosted Plan 9 environment. It sets `eve`, verifies critical C type sizes with `sizebug`, initializes OS/proc/print/screen subsystems, resets and initializes channel devices, installs quote formatting, binds core devices into `/dev`, `/net`, and `/`, opens `/dev/cons` as fd 0/1/2, then calls `cpumain`.

Also provides credential helpers:
- `getkey` prompts for `<user>@<dom> password` using `readcons`.
- `findkey` scans `secstorebuf` for `key proto=p9sk1 dom=<dom> user=... !password=...` entries and returns the matching user/password.

Notable behavior:
- Assumes 32-bit `long`/`ulong`, which is explicitly asserted as a drawterm portability requirement.
- `findkey` skips overlong secstore lines and clears its stack buffer before returning a copied password.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-386/Makefile -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-386/Makefile

Builds `../libmachdep.a` for POSIX i386 drawterm. Object files are `getcallerpc.$O`, `md5block.$O`, `sha1block.$O`, and `tas.$O`.

Rules:
- C files compile with `$(CC) $(CFLAGS)`.
- Assembly files assemble with `$(AS) -o`.
- `md5block.s` and `sha1block.s` are generated from `.spp` files via `gcc -E -`.

Notable role: this architecture uses hand-generated assembly hash blocks and x86 test-and-set.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-386/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-386/getcallerpc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-386/getcallerpc.c

Defines `getcallerpc(void *a)` for i386-style stack frames by returning `((uintptr*)a)[-1]`.

Purpose: expose the saved caller program counter expected by Plan 9 libc/debugging code.

Assumption: caller passes an address positioned so the previous pointer-width slot contains the return address.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-386/getcallerpc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-386/md5block.s -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-386/md5block.s

Generated i386 assembly implementation of `__md5block`. It processes 64-byte MD5 blocks, maintaining the four MD5 state words and applying all four MD5 rounds with constants and rotate counts expanded inline.

Key behavior:
- Saves/restores callee-saved registers.
- Iterates from input pointer to end pointer in 64-byte steps.
- Adds transformed `a/b/c/d` values back into the digest state.
- Uses little-endian 32-bit block words directly from memory.

Notable role: architecture-specific performance path for MD5 in drawterm/libsec.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-386/md5block.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-386/sha1block.s -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-386/sha1block.s

Generated i386 assembly implementation of `__sha1block`. It processes SHA-1 64-byte blocks, expands the 80-word schedule on the stack, applies all SHA-1 rounds, and folds results into the five-word state.

Key behavior:
- Converts input words with byte swaps to SHA-1 big-endian order.
- Uses unrolled groups for the four SHA-1 round functions/constants.
- Saves/restores i386 callee-saved registers.

Notable role: architecture-specific SHA-1 acceleration for drawterm/libsec.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-386/sha1block.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-386/tas.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-386/tas.c

Implements `tas(long *x)` with i386 inline assembly using `xchgl` to atomically exchange `1` into `*x`.

Behavior:
- Returns the previous value when it is `0` or `1`.
- Prints `canlock: corrupted` and returns locked (`1`) for unexpected values.

Role: machine-dependent primitive for Plan 9 spin locks on POSIX i386.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-386/tas.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-amd64/Makefile -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-amd64/Makefile

Builds `../libmachdep.a` for POSIX amd64 drawterm from `getcallerpc`, portable C `md5block`, portable C `sha1block`, and `tas`.

Unlike i386, this Makefile has only a C compilation rule and does not generate assembly hash blocks.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-amd64/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-amd64/getcallerpc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-amd64/getcallerpc.c

Defines `getcallerpc(void *a)` by returning `((uintptr*)a)[-1]`.

This is the same pointer-width stack-slot approach used by several drawterm architecture ports.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-amd64/getcallerpc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-amd64/md5block.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-amd64/md5block.c

Portable C implementation of `_md5block`. It implements the MD5 compression function over one or more 64-byte blocks.

Key elements:
- Contains RFC1321-derived MD5 constants in `md5tab`.
- `decode` converts byte input into little-endian 32-bit words.
- `_md5block` performs the four MD5 rounds and accumulates into the caller-provided state.

Duplication note: this file is byte-identical to the `md5block.c` copies under `posix-arm`, `posix-mips`, `posix-port`, `posix-power`, and `posix-sun4u`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-amd64/md5block.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-amd64/sha1block.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-amd64/sha1block.c

Portable C implementation of `_sha1block`. It processes one or more 64-byte SHA-1 blocks, builds an 80-word message schedule, applies the four SHA-1 round functions/constants, and accumulates into the five-word state.

Duplication note: this file is byte-identical to the `sha1block.c` copies under `posix-arm`, `posix-mips`, `posix-port`, `posix-power`, and `posix-sun4u`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-amd64/sha1block.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-amd64/tas.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-amd64/tas.c

Implements `tas(long *x)` with amd64 inline assembly using `xchgl` through `%rcx`.

Behavior mirrors the i386 implementation:
- Atomically writes `1`.
- Returns previous `0` or `1`.
- Treats other values as corrupted lock state and returns locked.

Role: drawterm spin-lock primitive for POSIX amd64.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-amd64/tas.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-arm/Makefile -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-arm/Makefile

Builds `../libmachdep.a` for POSIX ARM drawterm from `getcallerpc`, portable C MD5/SHA1 block implementations, and ARM `tas`.

Rules support both C and assembly, plus `.spp` preprocessing through `cpp`, though this directory's listed hash block files are C.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-arm/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-arm/getcallerpc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-arm/getcallerpc.c

Defines `getcallerpc(void *a)` as `((uintptr*)a)[-1]`.

Role: stack-based caller-PC recovery for ARM drawterm builds.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-arm/getcallerpc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-arm/md5block.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-arm/md5block.c

Portable C `_md5block` implementation. It is byte-identical to `posix-amd64/md5block.c`.

Purpose: MD5 compression for ARM drawterm/libsec builds where no architecture-specific MD5 assembly is used.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-arm/md5block.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-arm/sha1block.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-arm/sha1block.c

Portable C `_sha1block` implementation. It is byte-identical to `posix-amd64/sha1block.c`.

Purpose: SHA-1 compression for ARM drawterm/libsec builds.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-arm/sha1block.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-arm/tas.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-arm/tas.c

Implements ARM `tas(long *x)`.

Behavior:
- On `ARMv5`, uses `swp`.
- Otherwise uses `ldrex`/`strex` loop to atomically store `1`.
- Returns previous `0` or `1`; reports corrupted lock values and returns locked for anything else.

Role: ARM spin-lock primitive for drawterm.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-arm/tas.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-factotum.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-factotum.c

POSIX support for user and factotum discovery.

Functions:
- `getuser` returns the passwd database name for `getuid`, or `"none"`.
- `nsfromdisplay` derives a namespace path from `$DISPLAY`, canonicalizing `:0.0` to `:0`.
- `getns` uses `$NAMESPACE` or the display-derived namespace.
- `dialfactotum` connects to the Unix-domain socket `<namespace>/factotum` and returns it as a Plan 9 fd via `lfdfd`.

Notable behavior:
- Undefines POSIX wrappers for `socket`, `connect`, `getenv`, and `access`.
- Intended for hosted drawterm integration with plan9port-style factotum sockets.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-factotum.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-mips/Makefile -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-mips/Makefile

Builds `../libmachdep.a` for POSIX MIPS drawterm from `getcallerpc`, portable C MD5/SHA1 blocks, and assembly `tas.s`.

Rules:
- C via `$(CC) $(CFLAGS)`.
- Assembly via `$(AS) $(ASFLAGS) -o`.
- `.spp` files can be preprocessed with `cpp`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-mips/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-mips/getcallerpc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-mips/getcallerpc.c

Defines `getcallerpc(void *a)` returning `((ulong*)a)[-1]`.

Difference from most other ports: returns `ulong` rather than `uintptr`, matching local MIPS type conventions in this tree.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-mips/getcallerpc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-mips/md5block.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-mips/md5block.c

Portable C `_md5block` implementation. It is byte-identical to `posix-amd64/md5block.c`.

Purpose: MD5 compression for MIPS drawterm/libsec builds.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-mips/md5block.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-mips/sha1block.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-mips/sha1block.c

Portable C `_sha1block` implementation. It is byte-identical to `posix-amd64/sha1block.c`.

Purpose: SHA-1 compression for MIPS drawterm/libsec builds.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-mips/sha1block.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-mips/tas.s -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-mips/tas.s

MIPS assembly implementation of `tas`.

Behavior:
- Uses `ll`/`sc` loop to atomically store sentinel value `12345` into `*a0`.
- Repeats if store-conditional fails.
- Returns the previous value in `v0`.

Role: MIPS atomic test-and-set primitive for drawterm locking.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-mips/tas.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-port/Makefile -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-port/Makefile

Builds a portable POSIX `../libmachdep.a` from `getcallerpc`, `md5block`, and `sha1block`.

Notably omits `tas.$O`, so this port does not provide an architecture-specific atomic test-and-set in the listed machine-dependent archive.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-port/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-port/getcallerpc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-port/getcallerpc.c

Portable fallback `getcallerpc(void *a)` implementation.

Behavior:
- Ignores `a`.
- Returns `0`.

Role: safe fallback when caller-PC recovery is unavailable or unsupported.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-port/getcallerpc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-port/md5block.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-port/md5block.c

Portable C `_md5block` implementation. It is byte-identical to `posix-amd64/md5block.c`.

Purpose: generic MD5 compression for the portable drawterm machine-dependent library.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-port/md5block.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-port/sha1block.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-port/sha1block.c

Portable C `_sha1block` implementation. It is byte-identical to `posix-amd64/sha1block.c`.

Purpose: generic SHA-1 compression for the portable drawterm machine-dependent library.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-port/sha1block.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-power/Makefile -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-power/Makefile

Builds `../libmachdep.a` for POSIX PowerPC drawterm from `getcallerpc`, portable C MD5/SHA1 blocks, and PowerPC `tas`.

This Makefile is byte-identical to `posix-arm/Makefile`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-power/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-power/getcallerpc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-power/getcallerpc.c

Defines `getcallerpc(void *a)` as `((uintptr*)a)[-1]`.

Role: caller-PC recovery for PowerPC drawterm builds.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-power/getcallerpc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-power/md5block.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-power/md5block.c

Portable C `_md5block` implementation. It is byte-identical to `posix-amd64/md5block.c`.

Purpose: MD5 compression for PowerPC drawterm/libsec builds.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-power/md5block.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-power/sha1block.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-power/sha1block.c

Portable C `_sha1block` implementation. It is byte-identical to `posix-amd64/sha1block.c`.

Purpose: SHA-1 compression for PowerPC drawterm/libsec builds.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-power/sha1block.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-power/tas.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-power/tas.c

PowerPC inline assembly implementation of `tas`.

Behavior:
- Uses `sync`, `lwarx`, and `stwcx.` reservation sequence.
- Stores sentinel `0xdeaddead` only when the old value is zero.
- Returns `0` for acquired and `1` for already locked sentinel.
- Reports unexpected values as corrupted.

Notes:
- Contains comments about GCC 2.95.2 and a cache-flush workaround for a 603x issue.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-power/tas.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-sun4u/Makefile -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-sun4u/Makefile

Builds `../libmachdep.a` for POSIX SPARC/sun4u drawterm from `getcallerpc`, portable C MD5/SHA1 blocks, and assembly `tas.s`.

Rules support C, assembly, and `.spp` preprocessing via `cpp`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-sun4u/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-sun4u/getcallerpc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-sun4u/getcallerpc.c

Defines `getcallerpc(void *a)` returning `((ulong*)a)[-1]`.

Role: caller-PC recovery for sun4u drawterm builds.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-sun4u/getcallerpc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-sun4u/md5block.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-sun4u/md5block.c

Portable C `_md5block` implementation. It is byte-identical to `posix-amd64/md5block.c`.

Purpose: MD5 compression for sun4u drawterm/libsec builds.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-sun4u/md5block.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-sun4u/sha1block.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-sun4u/sha1block.c

Portable C `_sha1block` implementation. It is byte-identical to `posix-amd64/sha1block.c`.

Purpose: SHA-1 compression for sun4u drawterm/libsec builds.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-sun4u/sha1block.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-sun4u/tas.s -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-sun4u/tas.s

SPARC assembly implementation of `tas`.

Behavior:
- Exports `tas`.
- Uses `ldstub [%o0], %o0` in the return delay slot.
- Returns the old byte value while atomically setting the target byte.

Role: sun4u atomic lock primitive.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-sun4u/tas.s -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/readcons.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/readcons.c

Implements console prompting and small allocation helpers for drawterm.

Functions:
- `erealloc` and `estrdup` abort with `sysfatal` on allocation failure.
- `estrappend` appends formatted text to a dynamically allocated string.
- `readcons(prompt, def, raw)` prompts on `/dev/cons`, optionally enables raw mode via `/dev/consctl`, reads one byte at a time, handles newline, delete, backspace, and `^U`, and returns the entered string or default.

Notable behavior:
- Raw mode is used for password-like input; it writes a newline and turns raw mode off when input completes.
- Delete (`0x7f`) cancels and returns nil.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/readcons.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/resource.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/resource.h

Windows resource header generated by Microsoft Developer Studio for `drawterm.rc`.

Defines:
- `IDI_ICON1` as resource id `101`.
- Default AP Studio values guarded by `APSTUDIO_INVOKED`.

Role: Win32 build resource metadata for drawterm icon resources.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/resource.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/secstore.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/secstore.c

Compact drawterm copy of secstore client code, enough to check for and fetch a boot-time `factotum` file.

Major pieces:
- `secdial` resolves `$auth`/authserver naming and dials TCP port 5356.
- `havesecstore` sends a minimal secstore PAK probe and interprets account-existence responses.
- `SConn`/`SS` implement a delimited connection that can switch to SHA1/RC4 authenticated encryption using `SC_secret`, `SC_read`, and `SC_write`.
- `getfile` requests `GET factotum`, receives encrypted file chunks, derives an AES-CBC key from the password, decrypts, and verifies the trailing `XXXXXXXXXXXXXXXX` check block.
- PAK support includes fixed group parameters, `longhash`, `PAK_Hi`, `shorthash`, and `PAKclient`.
- `secstorefetch` prompts or accepts a password, performs PAK, handles optional STA/SecurID challenge, fetches and decrypts the file, sends `BYE`, and returns the file contents.

Important dependencies:
- Plan 9 networking/dialing, mpint arithmetic, SHA1/HMAC, RC4, AES-CBC, `readcons`, and drawterm globals such as `authserver`.

Notable behavior and risks:
- Max fetched file size is capped at 10 MiB.
- The encrypted channel uses legacy RC4/SHA1 after PAK.
- The secstore file encryption path uses AES-CBC plus a fixed check trailer.
- `emalloc` is `mallocz` without explicit failure handling in this file.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/secstore.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/win32-386/Makefile -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/win32-386/Makefile

Builds `../libmachdep.a` for Win32 i386 drawterm from `getcallerpc`, `md5block`, `sha1block`, and `tas`.

This Makefile is byte-identical to `posix-arm/Makefile` and uses generic C/assembly rules plus `.spp` preprocessing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/win32-386/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/win32-386/getcallerpc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/win32-386/getcallerpc.c

Defines `getcallerpc(void *a)` as `((uintptr*)a)[-1]`.

Role: caller-PC recovery for Win32 i386 drawterm builds.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/win32-386/getcallerpc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/win32-386/tas.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/win32-386/tas.c

Implements Win32 i386 `tas(long *x)` with the same `xchgl` inline assembly pattern as `posix-386/tas.c`.

Behavior:
- Atomically stores `1`.
- Returns prior `0` or `1`.
- Logs corrupted values and returns locked for unexpected state.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/win32-386/tas.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/win32-factotum.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/win32-factotum.c

Minimal Win32 factotum/user support.

Functions:
- `getuser` returns `$USER`.
- `dialfactotum` always returns `-1`.

Role: placeholder for platforms without a Unix-domain factotum service.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/win32-factotum.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/netkey.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/netkey.c

Standalone legacy Plan 9 netkey challenge-response utility with embedded DES implementation.

Major pieces:
- Re-declares relevant Plan 9 auth constants and ticket structures locally.
- Implements DES block cipher tables, key setup, initial/final permutations, and encrypt/decrypt routines.
- `passtokey` derives a 7-byte DES key from a password using Plan 9's historical password-to-key algorithm.
- `netcrypt` encrypts an 8-byte challenge and formats the first four encrypted bytes as hex response.
- `main` prompts locally for a password, then repeatedly prompts for challenges and prints responses.

Notable behavior:
- Intended to be run directly on the local processor, not over a network window.
- Uses old DES-based Plan 9 authentication compatible response generation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/netkey.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/authnone.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/authnone.c

Defines the `authnone` backend for u9fs.

Behavior:
- `noneauth` returns an error saying no authentication is required.
- `noneattach` succeeds unconditionally.

Role: authentication policy where clients attach without an auth file exchange.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/authnone.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/authp9any.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/authp9any.c

Implements 4th Edition `p9any` / `p9sk1` authentication for u9fs, based on older Plan 9 auth code.

Major pieces:
- Defines ticket, ticket request, and authenticator wire structures.
- Provides local DES encrypt/decrypt wrappers and password-to-key conversion.
- Conversion helpers serialize/deserialize ticket requests, tickets, and authenticators.
- `p9anyinit` reads a key file, defaulting to `/etc/u9fs.key`, expecting three lines: password, auth id, auth domain.
- `AuthSession` tracks per-auth-fid state: protocol negotiation, challenge, ticket request, ticket, and final establishment.
- `p9anyauth`, `p9anyread`, `p9anywrite`, `p9anyattach`, and `p9anyclunk` implement the 9P auth fid lifecycle.
- Exports `Auth authp9any`.

State flow:
- Server advertises `p9sk1@authdom`.
- Client selects `p9sk1 authdom`.
- Client sends challenge.
- Server sends encrypted ticket request.
- Client sends ticket plus authenticator.
- Server verifies ticket, challenge, and authenticator, then returns server authenticator and marks session established.
- Attach succeeds only when uname/aname match the established auth session.

Notable behavior:
- Uses DES-era p9sk1 auth.
- Clears some secret/session memory on clunk.
- Depends on external `block_cipher`, `key_setup`, `randombytes`, fid helpers, and u9fs global `autharg`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/authp9any.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/authrhosts.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/authrhosts.c

Defines Berkeley rhosts-style u9fs authentication.

Behavior:
- `rhostsauth` reports that no auth file exchange is required.
- `rhostsattach` calls `ruserok(remotehostname, 0, rx->uname, rx->uname)` and succeeds only if the host/user is trusted.

Notable comment: the file explicitly calls this weak and only reasonable behind a trusted firewall.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/authrhosts.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/convD2M.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/convD2M.c

Serializes a Plan 9 `Dir` structure into 9P stat message format.

Functions:
- `sizeD2M` computes required bytes from fixed stat size plus four strings: name, uid, gid, muid.
- `convD2M` writes size, type, dev, qid, mode, times, length, and the four counted strings.

Notable behavior:
- If the buffer is too small, it writes the size field first and returns `BIT16SZ` so callers can learn the required size.
- Returns `0` on malformed/internal mismatch or bounds failure.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/convD2M.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/convM2D.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/convM2D.c

Parses 9P stat message bytes into a `Dir`.

Functions:
- `statcheck` validates that four counted strings fit exactly within the supplied stat buffer.
- `convM2D` reads fixed stat fields and the four strings; if `strs` is provided, copies strings there and points `Dir` fields into it, otherwise assigns a static empty string.

Notable behavior:
- Bounds checks string count/data extents against the end of the supplied buffer.
- Ignores the leading size field while parsing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/convM2D.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/convM2S.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/convM2S.c

Parses 9P wire messages into an `Fcall`.

Major helpers:
- `gstring` reads a counted string, shifts bytes down over the length field, appends NUL, and returns an in-buffer string pointer.
- `gqid` reads a serialized `Qid`.

`convM2S` behavior:
- Validates size/type/tag framing.
- Switches across T/R message types including version, flush, auth, attach, walk, open, create, read, write, clunk, remove, stat, wstat, error, and replies.
- Bounds-checks fixed fields, counted data, string extents, stat payloads, qid arrays, and MAXWELEM counts.
- Returns the message size only if parsing consumes exactly the declared size.

Notable behavior:
- Contains commented-out older/session auth message variants.
- Mutates the input buffer when converting strings to NUL-terminated in-place strings.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/convM2S.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/convS2M.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/convS2M.c

Serializes an `Fcall` into 9P wire format.

Major helpers:
- `pstring` writes a counted string.
- `pqid` writes a serialized `Qid`.
- `stringsz` and `sizeS2M` compute serialized message size.

`convS2M` behavior:
- Computes exact size, rejects unknown message types and undersized buffers.
- Writes size, type, tag, and type-specific fields for T/R 9P messages.
- Handles counted strings, qids, walk arrays, read/write data, stat buffers, and auth qids.
- Enforces `MAXWELEM` for walk names/qids.
- Returns serialized size only if the write pointer matches the computed size.

Notable behavior:
- Contains commented-out older/session auth message variants.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/convS2M.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/cygwin.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/cygwin.c

Cygwin compatibility shims for u9fs.

Functions:
- `pread` and `pwrite` emulate positional I/O with `lseek`, preserving/restoring the original file offset and `errno`.
- `setreuid` maps requested real/effective uid changes to `setuid`/`seteuid`.
- `setregid` maps requested real/effective gid changes to `setgid`/`setegid`.

Notable issue:
- `setreuid` and `setregid` have no explicit success return at the end, despite returning `int`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/cygwin.c -->