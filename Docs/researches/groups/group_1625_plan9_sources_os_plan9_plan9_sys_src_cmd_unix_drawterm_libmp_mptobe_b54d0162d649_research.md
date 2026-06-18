# Group Research: group_1625_plan9_sources_os_plan9_plan9_sys_src_cmd_unix_drawterm_libmp_mptobe_b54d0162d649

Scope checked against `Docs/research_subset_a.md`: `sources/os/plan9/plan9` is included in subset A. All listed files were read completely; byte/line counts were verified against the workspace.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mptobe.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mptobe.c

Implements `mptobe(mpint *b, uchar *p, uint n, uchar **pp)`, exporting a Plan 9 `mpint` magnitude to a big-endian byte array. It includes `os.h`, `<mp.h>`, and `dat.h`, and operates directly on `mpint->top`, `mpint->p[]`, `Dbytes`, and `Dbits`.

The function allocates `(b->top+1)*Dbytes` when `p == nil`, optionally returns the buffer via `pp`, zero-fills the caller/allocation buffer, and suppresses leading zero bytes while scanning limbs from most significant to least significant. It returns the number of bytes written, or `-1` on allocation failure or insufficient caller-supplied space.

Important behavior: zero is special-cased to require at least one output byte and returns `1`, while nonzero values also guarantee at least one byte. The sign is not encoded; this is a magnitude serialization helper for higher-level crypto/integer code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mptobe.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mptoi.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mptoi.c

Provides signed `int` conversion helpers `itomp(int i, mpint *b)` and `mptoi(mpint *b)`. The file assumes `mpdigit` is at least as large as `int`, resets destination values with `mpassign(mpzero, b)`, and writes the integer magnitude into the first limb.

`itomp` allocates when needed, sets `top = 1` for nonzero inputs, stores negative inputs as positive magnitude with `sign = -1`, and otherwise stores the unsigned magnitude directly.

`mptoi` is saturating: positive values larger than `MAXINT` or requiring more than one limb return `MAXINT`; negative values larger than `MININT` magnitude or requiring more than one limb return `MININT`. It depends on the `MAXINT`/`MININT` macros from `dat.h`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mptoi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mptole.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mptole.c

Implements `mptole(mpint *b, uchar *p, uint n, uchar **pp)`, exporting an `mpint` magnitude to a little-endian byte array. It includes `os.h`, `<mp.h>`, and `dat.h`.

When no output buffer is supplied, it allocates `(b->top+1)*Dbytes`; when `pp` is non-nil it returns the selected buffer. The function zero-fills the whole output span, writes complete low limbs byte by byte, and trims high zero bytes from the most significant limb.

Return value is bytes written or `-1` for allocation/buffer failure. Notable quirk: for `b->top == 0`, it returns `0` if at least one byte of space exists, unlike `mptobe`, which returns `1` for zero. The sign is not serialized.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mptole.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mptoui.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mptoui.c

Defines unsigned `uint` conversion helpers `uitomp(uint i, mpint *b)` and `mptoui(mpint *b)`. It assumes `mpdigit` can hold a `uint` and uses the same `mpassign(mpzero, b)` reset pattern as the signed conversion file.

`uitomp` allocates a destination if needed, marks nonzero values with `top = 1`, and stores the value in the first limb.

`mptoui` clamps negative inputs to `0` and clamps values needing more than one limb or exceeding `MAXUINT` to `MAXUINT`. Since `MAXUINT` is the full `uint` range, the overflow path mainly guards multi-limb values.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mptoui.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mptouv.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mptouv.c

Provides unsigned `uvlong` conversion helpers `uvtomp(uvlong v, mpint *b)` and `mptouv(mpint *b)`. `VLDIGITS` is computed as `sizeof(vlong)/sizeof(mpdigit)`, and the code assumes a `vlong` is an integral number of `mpdigit`s.

`uvtomp` ensures enough space for all native long limbs, clears the destination, then emits low-to-high `mpdigit` chunks until `v` becomes zero. `mptouv` normalizes the input, returns `0` for empty magnitude, returns `MAXVLONG` when too many limbs are present, and reconstructs a native value by shifting each limb to its native offset.

The function ignores negative sign for normal in-range values; it treats the stored magnitude as unsigned. Overflow handling uses `MAXVLONG` rather than `MAXUVLONG`, which is a compatibility/convention detail worth preserving.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mptouv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mptov.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mptov.c

Provides signed `vlong` conversion helpers `vtomp(vlong v, mpint *b)` and `mptov(mpint *b)`. It mirrors `mptouv.c` but preserves sign in `vtomp` and saturates signed output in `mptov`.

`vtomp` allocates or resizes for `VLDIGITS`, clears the destination, records `sign = -1` for negative inputs, converts the absolute value into low-to-high limbs, and sets `top` to the number of emitted limbs.

`mptov` normalizes the input, returns `MAXVLONG` or `MINVLONG` on too many limbs depending on sign, reconstructs the magnitude, then clamps to signed bounds. Negative in-range values are returned as `-(vlong)v`; values beyond `MINVLONG` magnitude clamp to `MINVLONG`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mptov.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpvecadd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpvecadd.c

Implements low-level limb-vector addition `mpvecadd(mpdigit *a, int alen, mpdigit *b, int blen, mpdigit *sum)`. The documented precondition is `alen >= blen`, and `sum` must have room for `alen + 1` digits.

The routine first adds overlapping limbs from `a` and `b` with carry detection based on unsigned wraparound, then propagates carry across the remaining high limbs of `a`. It stores a final carry digit at `sum[alen]`.

This is magnitude-only arithmetic used by higher-level `mpint` operations. It does not normalize or allocate; callers are responsible for sizes, aliasing safety, and sign semantics.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpvecadd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpveccmp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpveccmp.c

Implements `mpveccmp(mpdigit *a, int alen, mpdigit *b, int blen)`, comparing two little-endian limb vectors as unsigned magnitudes.

It first trims effective high zero limbs from the longer vector, then walks equal-length vectors from high limb to low limb. The subtraction/wraparound test distinguishes `a[alen] < b[alen]` without requiring a wider type.

Return values follow normal compare semantics: `1` if `a > b`, `-1` if `a < b`, and `0` if magnitudes match. No allocation, normalization, or sign handling occurs here.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpveccmp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpvecdigmuladd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpvecdigmuladd.c

Contains single-digit multiply helpers for limb-vector arithmetic: static `mpdigmul`, public `mpvecdigmuladd`, and public `mpvecdigmulsub`. It splits an `mpdigit` into high and low half-digits using `LO` and `HI` macros to compute a two-limb product without requiring a wider native type.

`mpvecdigmuladd(b, n, m, p)` adds `m * b[0:n-1]` into `p[0:n]`, carrying through the extra digit. `mpvecdigmulsub(b, n, m, p)` subtracts the same product from `p[0:n]` and returns `1` for nonnegative final subtraction or `-1` when the high digit underflows.

The file is central to multiplication/division-style `mpint` internals. Preconditions require `p` to have room for `n+1` digits; the code mutates `p` in place and does not normalize.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpvecdigmuladd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpvecsub.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpvecsub.c

Implements `mpvecsub(mpdigit *a, int alen, mpdigit *b, int blen, mpdigit *diff)`, subtracting limb vector `b` from `a`. The documented preconditions are `a >= b`, `alen >= blen`, and `diff` has at least `alen` digits.

The overlapping range subtracts each `b` limb and incoming borrow from `a`, using unsigned comparisons to detect borrow propagation. Remaining high limbs of `a` are copied through with borrow subtraction.

This is magnitude-only, low-level arithmetic. It assumes the caller has already compared magnitudes and arranged sign/result normalization at the `mpint` layer.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpvecsub.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/os.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/os.h

Minimal portability header for this `libmp` directory. It includes Plan 9 compatibility headers `<u.h>` and `<libc.h>`.

No declarations or local macros are defined here; source files use it to bring in base integer types, memory functions, allocation, and Plan 9 libc conventions before including `<mp.h>` and local internals.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/os.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/strtomp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/strtomp.c

Implements `strtomp(char *a, char **pp, int base, mpint *b)`, parsing ASCII strings into `mpint` values for bases 10, 16, 32, and 64. It includes `os.h`, `<mp.h>`, `<libsec.h>`, and `dat.h`.

A static table initializer builds lookup arrays for base64, base32, hex, and decimal. Hex parsing packs nibbles directly into little-endian limbs. Decimal parsing consumes up to 9 digits at a time in native arithmetic, multiplying the accumulated `mpint` by powers of 10 and adding each chunk. Base64 and base32 scan valid alphabet spans, decode with `dec64`/`dec32`, and import the result with `betomp`.

`strtomp` skips spaces/tabs, accepts repeated `-` signs by multiplying sign by `-1`, defaults unsupported bases to base 16, normalizes the result, sets the sign, and optionally returns the parse end pointer. If no digits are parsed, it returns `nil`.

Notable detail: `from32` scans using `tab.t64` rather than `tab.t32` before calling `dec32`; as read, that widens the accepted scan set and may stop incorrectly for base32-only validation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/strtomp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/Makefile -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/Makefile

Builds `libsec.a` for drawterm. It sets `ROOT=..`, includes `../Make.config`, defines `LIB=libsec.a`, and lists object files for AES, Blowfish, PEM decode, DES modes, DSA, ElGamal, random/prime generation, HMAC, MD4/MD5/SHA1, RC4, RSA, and small-prime support.

The default target builds the static archive by running `$(AR) r $(LIB) $(OFILES)` followed by `$(RANLIB) $(LIB)`. The generic compile rule maps `%.$O` from `%.c` via `$(CC) $(CFLAGS) $*.c`.

Test/helper files present in the directory, such as `egtest.c`, `hmactest.c`, `md4test.c`, `primetest.c`, `rsatest.c`, `readcert.c`, `thumb.c`, and block files like `md5block.c`/`sha1block.c`, are not all represented in this object list. The archive composition is therefore narrower than the directory contents.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/aes.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/aes.c

Table-driven AES/Rijndael implementation including key setup, single-block encryption/decryption, and CBC mode entry points exposed through `libsec.h`. It includes `<u.h>`, `<libc.h>`, and `<libsec.h>`.

The file defines Rijndael T-tables (`Te0`-`Te4`, `Td0`-`Td4`) and round constants, plus static helpers `rijndaelKeySetupEnc`, `rijndaelKeySetupDec`, `rijndaelKeySetup`, `rijndaelEncrypt`, and `rijndaelDecrypt`. It supports 128-, 192-, and 256-bit keys through the standard 10/12/14 AES round counts.

Public API behavior is via `setupAESstate`, `aesCBCencrypt`, and `aesCBCdecrypt`. `setupAESstate` records the raw key, key length, expanded encryption/decryption schedules, round count, optional IV, and a setup marker. CBC encryption XORs plaintext blocks with the IV/ciphertext chain before block encryption; CBC decryption preserves ciphertext as the next IV before XORing decrypted blocks.

The implementation is portable C with conditional unaligned/little-endian load macros and optional intermediate-value KAT helpers behind preprocessor guards. It mutates the supplied buffer and AES state IV in place.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/aes.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/blowfish.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/blowfish.c

Implements Blowfish setup and ECB/CBC encryption/decryption. It includes `os.h`, `<mp.h>`, and `<libsec.h>`, though the core is block-cipher code over `BFstate`.

The file contains the standard Blowfish initial P-box and S-box constants, static `bfencrypt`/`bfdecrypt` block transforms, and public `setupBFstate`, `bfCBCencrypt`, `bfCBCdecrypt`, `bfECBencrypt`, and `bfECBdecrypt`.

`setupBFstate` copies the key and IV, initializes state tables from the constants, XORs key material into the P-box, and repeatedly encrypts zero blocks to generate the final P-box/S-box state. ECB and CBC functions operate in place on 8-byte blocks, with CBC chaining through `s->ivec`.

The functions support partial trailing buffers by encrypting a keystream-like block and XORing the remaining bytes, preserving compatibility with the surrounding Plan 9 cryptographic conventions rather than enforcing strict block multiples.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/blowfish.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/decodepem.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/decodepem.c

Defines `decodepem(char *s, char *type, int *len)`, extracting and base64-decoding a named PEM section. It includes `<u.h>`, `<libc.h>`, `<mp.h>`, and `<libsec.h>`.

The parser searches line by line for `-----BEGIN <type>-----\n`, then searches for the matching `-----END <type>-----\n`. It tolerates garbage before and after the selected section but expects exact newline-terminated delimiters.

It allocates a decoded buffer sized from the base64 span, calls `dec64`, stores the decoded length through `len`, and returns the allocated DER bytes. On malformed delimiters, allocation failure, or bad base64, it returns `nil` and sets `werrstr`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/decodepem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/des.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/des.c

Core DES implementation. It includes `os.h` and `<libsec.h>`, defines static DES S/P-box combination tables, key compression tables, rotation schedule, and parity conversion data.

Public functions are `block_cipher`, `triple_block_cipher`, `des_key_setup`, `des56to64`, `des64to56`, and `key_setup`. `block_cipher` performs DES over one 8-byte block using a 32-word expanded key and a decrypt/encrypt direction flag. `triple_block_cipher` sequences three DES operations using the bit-encoded E/D ordering constants from `libsec.h`.

`des_key_setup` accepts an 8-byte DES key and fills the 32-word expanded schedule. `key_setup` is a compatibility wrapper for 7-byte keys, converting through `des56to64`; `des64to56` reverses that format conversion.

The file provides the primitive operations used by the CBC/ECB mode wrappers and by the X9.17-style random generator in `genrandom.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/des.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/des3CBC.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/des3CBC.c

Implements 3DES CBC mode: `des3CBCencrypt` and `des3CBCdecrypt`. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

Encryption XORs each full 8-byte plaintext block with the current IV, applies `triple_block_cipher(..., DES3EDE)`, stores the ciphertext block back into the IV, and advances in place. Decryption saves the current ciphertext block, applies `triple_block_cipher(..., DES3DED)`, XORs with the previous IV, and updates the IV to the saved ciphertext.

For trailing non-8-byte data, it encrypts the IV and XORs the remaining bytes. Comments state that decryptors must be fed buffers of the same size as encryptors because of this partial-block convention.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/des3CBC.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/des3ECB.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/des3ECB.c

Implements 3DES ECB mode: `des3ECBencrypt` and `des3ECBdecrypt`. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

Full 8-byte blocks are transformed in place with `triple_block_cipher`, using EDE for encryption and DED for decryption. For trailing bytes, the code initializes a temporary block to bytes `0..7`, encrypts it with EDE, and XORs the remaining input bytes with that result.

The file comments explicitly call the partial-block behavior dangerous but retained for compatibility with older cryptlib behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/des3ECB.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/desCBC.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/desCBC.c

Implements single-DES CBC mode: `desCBCencrypt` and `desCBCdecrypt`. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

Encryption XORs each full block with `s->ivec`, encrypts with `block_cipher(..., 0)`, and updates the IV to the ciphertext. Decryption saves ciphertext, decrypts with `block_cipher(..., 1)`, XORs with the previous IV, and then installs the saved ciphertext as the new IV.

Like the 3DES CBC wrapper, trailing partial blocks are processed by encrypting the IV and XORing the remaining bytes. The code warns that decryptors must receive the same buffer sizes as encryptors for compatibility.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/desCBC.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/desECB.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/desECB.c

Implements single-DES ECB mode: `desECBencrypt` and `desECBdecrypt`. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

Full 8-byte blocks are transformed in place using `block_cipher`, with direction `0` for encryption and `1` for decryption. Partial trailing data is XORed with an encrypted deterministic temporary block containing bytes `0..7`.

The file’s comment notes uncertainty and risk around the non-multiple-of-8 behavior, retained only to match older cryptlib compatibility.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/desECB.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/desmodes.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/desmodes.c

Provides DES state initialization wrappers `setupDESstate` and `setupDES3state`. It includes `os.h` and `<libsec.h>`.

`setupDESstate` zeroes the state, copies the 8-byte key, expands it with `des_key_setup`, copies an optional IV, and sets `setup = 0xdeadbeef`. `setupDES3state` repeats the same pattern for three 8-byte keys and three expanded schedules.

The file documents that these routines use the 64-bit DES key format; older 56-bit key compatibility lives in `des.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/desmodes.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/dsaalloc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/dsaalloc.c

Defines DSA allocation/free helpers: `dsapuballoc`, `dsapubfree`, `dsaprivalloc`, `dsaprivfree`, `dsasigalloc`, and `dsasigfree`. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

Allocators use `mallocz(sizeof(*obj), 1)` and call `sysfatal` on allocation failure. Free helpers release nested `mpint` members for public keys, private keys, and signatures.

Notable ownership detail: unlike the RSA and ElGamal free helpers in nearby files, these DSA free functions free nested `mpint`s but do not call `free(dsa)` on the containing struct. This may be intentional legacy convention or a leak/inconsistency relative to the other key types.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/dsaalloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/dsagen.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/dsagen.c

Implements `dsagen(DSApub *opub)`, generating a DSA private key. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

If an existing public parameter set is supplied, it copies `p` and `q`; otherwise it allocates them and calls `DSAprimes`. It then computes a generator `alpha` by selecting random `g`, reducing it modulo `p`, and exponentiating by `(p-1)/q` until the result is not one.

The secret is generated randomly, reduced modulo `p`, and the public key is `alpha^secret mod p`. Temporary `mpint`s are freed before return, and the resulting `DSApriv` owns copied/generated parameters, `alpha`, public key, and secret.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/dsagen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/dsaprimes.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/dsaprimes.c

Implements `DSAprimes(mpint *q, mpint *p, uchar seed[SHA1dlen])`, following the NIST DSA prime generation algorithm as described in Handbook of Applied Cryptography. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

The routine generates a 160-bit `q` using SHA1 over a random seed and incremented seed, forces high/low bits, and tests probable primality. It then constructs 1024-bit `p` candidates so that `q` divides `p-1`, retrying up to 4096 inner attempts before starting over.

Helper functions `Hrand` and `Hincr` operate on 20-byte little-endian seed arrays. `Hrand` uses `fastrand`; primality checks use `probably_prime`. If the caller supplies `seed`, the selected seed is copied out for reproducibility/audit.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/dsaprimes.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/dsaprivtopub.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/dsaprivtopub.c

Defines `dsaprivtopub(DSApriv *priv)`, copying the public part of a DSA private key. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

The function allocates a `DSApub`, then deep-copies `p`, `q`, `alpha`, and `key` from `priv->pub`. The returned public key owns its copies.

No validation is performed; the function assumes `priv` and all public members are initialized.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/dsaprivtopub.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/dsasign.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/dsasign.c

Implements `dsasign(DSApriv *priv, mpint *m)`. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

The signer computes `q-1`, repeatedly chooses a random `k` in the DSA range with an inverse modulo `q`, makes the inverse positive, computes `r = (alpha^k mod p) mod q`, and computes `s = k^-1 * (m + secret*r) mod q`.

It returns a newly allocated `DSAsig` owning `r` and `s`, while freeing temporary `qm1`, `k`, and `kinv`. The message `m` is treated as an `mpint` already prepared by the caller, not hashed inside this function.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/dsasign.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/dsaverify.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/dsaverify.c

Implements `dsaverify(DSApub *pub, DSAsig *sig, mpint *m)`. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

The verifier rejects negative or out-of-range `r`/`s`, computes `s^-1 mod q`, then computes `u1 = m*s^-1 mod q` and `u2 = r*s^-1 mod q`. It verifies whether `((alpha^u1 * key^u2) mod p) mod q` equals `r`.

Return convention is `0` for success and `-1` for failure. All temporary `mpint`s are freed through the `out` path.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/dsaverify.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/egalloc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/egalloc.c

Defines ElGamal allocation/free helpers: `egpuballoc`, `egpubfree`, `egprivalloc`, `egprivfree`, `egsigalloc`, and `egsigfree`. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

Allocators use zeroing allocation and `sysfatal` on failure. Free functions release nested `mpint` fields for public keys, private keys, and signatures.

Like `dsaalloc.c`, these free functions do not call `free` on the containing `EGpub`, `EGpriv`, or `EGsig` structs, unlike the RSA free helpers. That ownership pattern should be noted by callers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/egalloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/egdecrypt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/egdecrypt.c

Implements `egdecrypt(EGpriv *priv, mpint *in, mpint *out)`. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

The ciphertext is packed as `gamma << shift + delta`, where `shift` is derived from the modulus significant-bit count rounded to a digit boundary. Decryption extracts `gamma` and `delta`, computes `gamma^secret mod p`, inverts that value modulo `p`, multiplies by `delta`, and reduces modulo `p`.

The function allocates `out` if nil, uses temporary `gamma` and `delta`, frees them, and returns the plaintext magnitude in `out`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/egdecrypt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/egencrypt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/egencrypt.c

Implements `egencrypt(EGpub *pub, mpint *in, mpint *out)`. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

The intended algorithm reduces the message modulo `p`, selects random ephemeral `k`, computes `gamma = alpha^k mod p`, computes `delta = message * key^k mod p`, and packs `gamma` and `delta` into one `mpint` using a digit-aligned shift.

Important as-read issue: `pm1` is allocated but never initialized to `p-1` before the loop checks `mpcmp(k, pm1) < 0`. Since `pm1` remains zero, the range condition for positive `k` cannot succeed, making this loop appear non-terminating. The rest of the function frees temporaries and returns `out` if the loop is ever exited.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/egencrypt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/eggen.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/eggen.c

Implements `eggen(int nlen, int rounds)`, generating an ElGamal private key. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

The function allocates an `EGpriv`, initializes public `p`, `alpha`, `key`, and private `secret`, then calls `gensafeprime` to produce a safe prime modulus and generator. It chooses a random `nlen-1` bit secret and computes `key = alpha^secret mod p`.

Returned ownership is held by the allocated `EGpriv`; callers free nested fields through `egprivfree`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/eggen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/egprivtopub.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/egprivtopub.c

Defines `egprivtopub(EGpriv *priv)`, deep-copying public ElGamal fields. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

The function allocates an `EGpub`, then copies `p`, `alpha`, and `key` from the private key’s embedded public structure. It returns nil only if allocation unexpectedly returns nil, though `egpuballoc` itself calls `sysfatal` on failure.

No validation is done; initialized input is assumed.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/egprivtopub.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/egsign.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/egsign.c

Implements `egsign(EGpriv *priv, mpint *m)`, an ElGamal signature routine. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

It computes `p-1`, repeatedly selects an invertible random `k` in the allowed range, computes `r = alpha^k mod p`, and computes `s = k^-1 * (m - secret*r) mod (p-1)`. The inverse is normalized positive with `mpmod`.

It returns an allocated `EGsig` owning `r` and `s`, and frees `pm1`, `k`, and `kinv`. The caller supplies the already-hashed/prepared message as an `mpint`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/egsign.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/egtest.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/egtest.c

Small ElGamal decryption test program with `main`. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

The test constructs a fixed private key with small values (`p=2357`, `alpha=2`, public key `1185`, secret `1751`), expected message `2035`, and a packed ciphertext made from fixed `gamma=1430` and `delta=697`.

It calls `egdecrypt` and prints an error if the recovered message differs from the expected value. This is a diagnostic/test file, not part of the static `libsec.a` object list in the Makefile.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/egtest.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/egverify.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/egverify.c

Implements `egverify(EGpub *pub, EGsig *sig, mpint *m)`. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

The verifier checks `1 <= r < p`, computes `key^r * r^s mod p`, computes `alpha^m mod p`, and compares the two values. It returns `0` on success and `-1` on failure.

Temporary `mpint`s for both sides of the verification equation are allocated and freed locally.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/egverify.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/fastrand.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/fastrand.c

Defines `fastrand(void)`, a convenience random `ulong` generator. It includes `<u.h>`, `<libc.h>`, and `<libsec.h>`.

The function fills a local `ulong x` with `genrandom` and returns it. The file comment describes this as using the X9.17 random number generator, faster than `truerand` but less random.

The implementation delegates all state and entropy handling to `genrandom.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/fastrand.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/genprime.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/genprime.c

Implements `genprime(mpint *p, int n, int accuracy)`, generating an `n`-bit probable prime. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

The function sizes `p`, fills `(n+7)/8` random bytes with `genrandom`, sets `top`, forces the high bit for exact bit length, masks excess high bits, and forces the low bit to make the candidate odd.

It then increments by two until `probably_prime(p, accuracy)` succeeds. It mutates the caller-supplied `mpint` and does not allocate a return value.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/genprime.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/genrandom.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/genrandom.c

Implements `genrandom(uchar *p, int n)` using a DES3-backed ANSI X9.17-style generator. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

A static `State` holds a `QLock`, seeded flag, 64-bit seed, and `DES3state`. `X917init` builds a 3DES key from repeated `truerand()` calls, initializes the DES3 state, warms the generator with 128 bytes, and marks it seeded.

`X917` encrypts the current `nsec()` timestamp to derive `I`, then repeatedly computes output blocks from `E_k(I ^ seed)` and updates `seed` with `E_k(output ^ I)`. `genrandom` serializes access with `qlock`/`qunlock`, initializes once, and fills the requested buffer.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/genrandom.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/gensafeprime.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/gensafeprime.c

Implements `gensafeprime(mpint *p, mpint *alpha, int n, int accuracy)`. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

The function repeatedly generates an `(n-1)`-bit prime `q`, sets `p = 2*q + 1`, and tests `p` for probable primality. Once a safe prime is found, it searches for a generator `alpha` of `Z*_p` by rejecting candidates where `alpha^2 mod p == 1` or `alpha^q mod p == 1`.

Temporary `q` and `b` values are freed before return. The result is stored in caller-owned `p` and `alpha`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/gensafeprime.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/genstrongprime.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/genstrongprime.c

Implements `genstrongprime(mpint *p, int n, int accuracy)` using Gordon’s strong-prime algorithm. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

The function enforces a minimum size of 64 bits, generates auxiliary primes `s` and `t`, finds a prime `r = 2*i*t + 1`, computes an initial `p0 = 2*(s^(r-2) mod r)*s - 1`, then searches by adding multiples of `2*r*s` until `p` passes `probably_prime`.

It allocates and frees temporary `mpint`s for `s`, `t`, `r`, and `i`, mutating the caller-supplied `p` with the final strong prime.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/genstrongprime.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/hmac.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/hmac.c

Implements RFC 2104-style HMAC wrappers for SHA1 and MD5. It includes `os.h` and `<libsec.h>`.

The static helper `hmac_x` accepts a digest function pointer, digest length, message chunk, key, output digest pointer, and optional digest state. It builds the inner pad on first call, streams data through the digest function, and on final call computes the outer digest over the outer pad plus inner digest.

Public wrappers are `hmac_sha1` and `hmac_md5`. The implementation rejects keys longer than 64 bytes instead of hashing them down, so callers must pre-process long HMAC keys if RFC-compatible long-key behavior is needed.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/hmac.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/hmactest.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/hmactest.c

Small HMAC-MD5 test program. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

The test uses key `"Jefe"` and data `"what do ya want for nothing?"`, computes `hmac_md5`, prints the hexadecimal digest, then prints the expected digest `750c783e6ab0b503eaa86e310a5db738`.

This file is a diagnostic vector check and is not listed in `libsec/Makefile`’s `OFILES`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/hmactest.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/md4.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/md4.c

Implements MD4 hashing from Stinson’s description. It includes `os.h` and `<libsec.h>`.

The file defines MD4 rotation constants, a 48-entry round table, static `md4block`, `encode`, and `decode` helpers, and public `md4(uchar *p, ulong len, uchar *digest, MD4state *s)`. The state machine supports streaming: when `digest == nil`, partial input is retained in `s->buf`; when `digest` is supplied, the function pads, appends bit length, finalizes, writes the digest, and frees malloced state.

The block function processes 64-byte blocks over MD4’s three rounds and updates four state words. Output encoding is little-endian, matching MD4 convention.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/md4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/md4test.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/md4test.c

MD4 test program. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

The file defines standard MD4 test input strings, from the empty string through the long numeric sequence. `main` hashes each string with `md4`, then prints each digest byte in hex.

It is a standalone diagnostic program and is not included in the `libsec.a` object list.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/md4test.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/md5.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/md5.c

Implements the MD5 streaming front end and finalization logic. It includes `os.h` and `<libsec.h>`, carries the RSA Data Security MD5 notice, and declares external `_md5block`.

Public `md5(uchar *p, ulong len, uchar *digest, MD5state *s)` allocates and seeds state when needed, fills pending partial blocks, processes full 64-byte blocks via `_md5block`, and either returns state for continued streaming or finalizes with MD5 padding and little-endian length.

The static `encode` helper writes 32-bit words to bytes in little-endian order. The compression function itself is split into `md5block.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/md5.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/md5block.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/md5block.c

Contains the MD5 compression function `_md5block(uchar *p, ulong len, u32int *s)`. It includes `os.h` and `<libsec.h>`.

The file defines MD5 logical functions, rotate constants, and the per-round transformation macros. `_md5block` decodes each 64-byte input block into sixteen 32-bit little-endian words, runs the four MD5 rounds, and accumulates the result into the caller’s four-word state.

This file is the hot compression core used by `md5.c`; it does not manage padding, streaming state, or digest output.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/md5block.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/md5pickle.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/md5pickle.c

Implements serialization helpers for an in-progress MD5 state: `md5pickle` and `md5unpickle`. It includes `os.h` and `<libsec.h>`.

`md5pickle` allocates a text buffer, prints the four MD5 state words as fixed-width hex fields, then base64-encodes the buffered partial block. `md5unpickle` parses those four words, decodes the base64 buffer into `s->buf`, and marks the returned state as malloced and seeded.

Important limitation: the pickle does not serialize `s->len`; only state words and partial buffer length are reconstructed. That may be sufficient for the original caller convention but is not a full generic MD5 checkpoint.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/md5pickle.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/nfastrand.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/nfastrand.c

Defines `nfastrand(ulong n)`, producing an unbiased-ish random value in `[0, n)`. It includes `<u.h>`, `<libc.h>`, and `<libsec.h>`.

The function sets `Maxrand` to `2^31 - 1`, aborts if `n > Maxrand`, computes the largest multiple of `n` not exceeding `Maxrand`, and rejects `fastrand()` results outside that range before returning `r % n`.

There is no explicit guard for `n == 0`; callers must avoid zero to prevent modulo/division errors.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/nfastrand.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/os.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/os.h

Minimal portability header for `libsec`. It includes `<u.h>` and `<libc.h>`.

No local declarations or macros are defined here. Source files include it to obtain Plan 9-style base types, libc functions, synchronization primitives, and allocation/error APIs.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/os.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/primetest.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/primetest.c

Standalone primality/DSA-prime test program. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

`main` installs the mp formatter, constructs known composite and prime examples, checks `probably_prime`, then calls `DSAprimes` and prints generated `q` and `p`. The bottom of the file includes commented example output checked with Maple, including seed, `q`, `p`, and related large values.

This is a diagnostic executable source, not part of the `libsec.a` Makefile object list.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/primetest.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/prng.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/prng.c

Defines `prng(uchar *p, int n)`, a simple buffer filler using libc `rand()`. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

The function iterates over the output buffer and assigns each byte from `rand()`. It is explicitly described as “just use the libc prng”.

This routine is used by `probably_prime.c` for Miller-Rabin witness selection, while cryptographic random generation elsewhere uses `genrandom`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/prng.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/probably_prime.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/probably_prime.c

Implements Miller-Rabin probable-prime testing in `probably_prime(mpint *n, int nrep)`. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

The function rejects negative candidates with `sysfatal`, handles small/even cases, runs `smallprimetest`, performs a Fermat check `2^n mod n == 2`, then decomposes `n-1` into `q * 2^k` and performs `nrep` Miller-Rabin repetitions.

Witnesses are generated with `mprand(nbits, prng, nil)`, reduced modulo `n-1`, and skipped if `<= 1`. Return value is `1` for probable prime and `0` for composite, with the comment giving error probability below `1/4^nrep`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/probably_prime.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/rc4.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/rc4.c

Implements RC4 key scheduling and stream operations. It includes `os.h` and `<libsec.h>`.

`setupRC4state` initializes the 256-byte permutation and performs the key-scheduling algorithm over the supplied key bytes. `rc4` applies the PRGA to XOR keystream into a buffer in place and updates `x`/`y` indices in the state.

`rc4skip` advances the PRGA without emitting bytes. `rc4back` reverses the PRGA state by undoing swaps and index movement for a requested number of bytes, allowing the stream position to move backward.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/rc4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/readcert.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/readcert.c

Provides certificate-file loading helper `readcert(char *filename, int *pcertlen)`. It includes `<u.h>`, `<libc.h>`, `<mp.h>`, and `<libsec.h>`.

A static `readfile` opens a file, obtains its length with `dirfstat`, allocates a NUL-terminated buffer, reads the full file with `readn`, and returns the string. `readcert` then calls `decodepem(pem, "CERTIFICATE", pcertlen)` and returns the decoded DER bytes.

Errors set `werrstr` for read or parse failure. One edge detail: if `dirfstat` fails, `readfile` returns without closing the already-open fd.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/readcert.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/rsaalloc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/rsaalloc.c

Defines RSA allocation/free helpers: `rsapuballoc`, `rsapubfree`, `rsaprivalloc`, and `rsaprivfree`. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

Allocators use `mallocz` and terminate with `sysfatal` on allocation failure. `rsapubfree` frees public exponent and modulus, then frees the struct. `rsaprivfree` frees public fields, private exponent, prime factors, CRT exponents, CRT coefficient, and the struct.

This file has complete container ownership cleanup, unlike the DSA/ElGamal free helpers nearby.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/rsaalloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/rsadecrypt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/rsadecrypt.c

Implements `rsadecrypt(RSApriv *rsa, mpint *in, mpint *out)` using Garner’s CRT algorithm. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

The input is reduced modulo `p` and `q`, exponentiated with precomputed `kp` and `kq`, then recombined as `v1 + p * ((v2 - v1) * c2 mod q)`, where `c2` is the inverse of `p` modulo `q`.

The function allocates `out` if nil, uses two temporary `mpint`s, frees them, and returns the decrypted value.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/rsadecrypt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/rsaencrypt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/rsaencrypt.c

Defines `rsaencrypt(RSApub *rsa, mpint *in, mpint *out)`. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

The function allocates `out` if nil and computes `in^ek mod n` with `mpexp`. It returns the output `mpint`.

There is no padding, range checking, or encoding logic in this primitive; callers are responsible for using it safely.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/rsaencrypt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/rsafill.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/rsafill.c

Implements `rsafill(mpint *n, mpint *e, mpint *d, mpint *p, mpint *q)`, constructing an `RSApriv` from supplied key parameters. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

The function verifies `p` and `q` are probably prime, verifies `n == p*q`, and verifies `e*d == 1 mod (p-1)*(q-1)`. On failure it sets `werrstr`, frees local temporaries where needed, and returns nil.

For valid parameters it computes CRT coefficient `c2 = p^-1 mod q`, computes `kp = d mod (p-1)` and `kq = d mod (q-1)`, allocates an `RSApriv`, deep-copies public/private core values, installs CRT fields, and returns the key.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/rsafill.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/rsagen.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/rsagen.c

Implements `rsagen(int nlen, int elen, int rounds)`, generating an RSA private key. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

A static `genrand` creates a random `elen`-bit public exponent candidate with the top bit set. `rsagen` generates two strong primes, computes `n = p*q` and `phi = (p-1)*(q-1)`, then increments `e` until `gcd(e, phi) == 1` and computes `d = e^-1 mod phi`.

It also precomputes CRT coefficient `c2 = p^-1 mod q` and CRT exponents `kp`, `kq`, then returns an allocated `RSApriv` owning all key components.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/rsagen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/rsaprivtopub.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/rsaprivtopub.c

Defines `rsaprivtopub(RSApriv *priv)`, deep-copying an RSA public key from a private key. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

The function allocates an `RSApub`, copies modulus `n` and public exponent `ek`, and returns the new key. The returned key owns its `mpint` copies and should be released with `rsapubfree`.

No validation is performed.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/rsaprivtopub.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/rsatest.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/rsatest.c

Standalone RSA test and timing program. It includes `os.h`, `<mp.h>`, `<libsec.h>`, and `<bio.h>`.

`main` generates a 1024-bit RSA key, encrypts a fixed hex plaintext, times ten CRT decryptions versus ten raw `mpexp` private exponentiations, compares results, then enters an interactive loop reading lines, converting them to little-endian `mpint`s, encrypting/decrypting, printing intermediate values, and writing recovered bytes.

This file exercises RSA behavior and performance but is not included in the static library object list.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/rsatest.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/sha1.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/sha1.c

Implements the SHA1 streaming front end and finalization logic. It includes `os.h` and `<libsec.h>`, and declares external `_sha1block`.

Public `sha1(uchar *p, ulong len, uchar *digest, SHA1state *s)` allocates/seeds state, fills partial blocks, processes full 64-byte blocks through `_sha1block`, and either returns state for streaming or finalizes with SHA1 padding and a big-endian bit length.

The static `encode` helper writes 32-bit state words in big-endian order. The compression rounds are split into `sha1block.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/sha1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/sha1block.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/sha1block.c

Contains the SHA1 compression function `_sha1block(uchar *p, ulong len, u32int *s)`. It includes `os.h`.

The file expands each 64-byte block into the SHA1 message schedule, runs the 80 SHA1 rounds with the standard round functions/constants, and accumulates into the five-word state supplied by the caller.

It performs only block compression; initialization, padding, length encoding, and digest output are handled by `sha1.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/sha1block.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/sha1pickle.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/sha1pickle.c

Implements serialization helpers for in-progress SHA1 state: `sha1pickle` and `sha1unpickle`. It includes `os.h` and `<libsec.h>`.

`sha1pickle` allocates text, prints the five SHA1 state words as fixed-width hex fields, then base64-encodes the buffered partial block. `sha1unpickle` parses the five state words, decodes the base64 partial buffer, and marks the returned state as malloced and seeded.

As with `md5pickle.c`, the serialized form does not include the total byte count `len`, so it is not a complete generic checkpoint unless surrounding protocol state supplies the missing length.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/sha1pickle.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/smallprimes.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/smallprimes.c

Defines a global `ulong smallprimes[1000]` table. It includes `os.h`.

The table is the first 1000 small prime numbers, used as shared prime data by other `libsec` code. This file contains data only: no functions, allocation, or control flow.

Its Makefile entry includes it in `libsec.a`, making the symbol available to code that declares the table externally.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/smallprimes.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/smallprimetest.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/smallprimetest.c

Implements trial division by a static table of small primes in `smallprimetest(mpint *p)`. It includes `os.h`, `<mp.h>`, and `<libsec.h>`.

The file embeds a large static `ulong smallprimes[]` list ending at `104729`. Static helper `divides(mpint *dividend, ulong divisor)` performs long division over `mpint` limbs using `mpdigdiv` to determine whether the divisor divides the candidate.

`smallprimetest` iterates the table, stops early when the candidate is a single limb not larger than the current small prime, and returns `-1` if divisible by a small prime or `0` otherwise. It is used as a fast composite filter before Miller-Rabin in `probably_prime.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/smallprimetest.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/thumb.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/thumb.c

Implements thumbprint table loading/checking for X.509 SHA1 fingerprints. It includes `<u.h>`, `<libc.h>`, `<bio.h>`, `<auth.h>`, `<mp.h>`, and `<libsec.h>`.

The table has `1<<10` buckets. `okThumbprint` hashes the first two digest bytes to choose a bucket and checks linked-list entries for a matching `SHA1dlen` digest. `freeThumbprints` frees all dynamically allocated list nodes and the table.

Static `loadThumbprints` reads a thumbprint file with `Biobuf`, supports recursive `#include` lines, accepts records beginning with `x509 sha1=...`, decodes hex SHA1 values with `dec16`, and skips entries present in an optional CRL table. `initThumbprints` optionally loads a CRL table first, then loads accepted thumbprints and returns the table.

This file is certificate trust-list support code and is not listed in the `libsec.a` Makefile object list.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libsec/thumb.c -->