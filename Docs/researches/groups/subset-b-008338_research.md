# Group Research: subset-b-008338

This grouped report covers the requested source files only. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/src/evmctl.c -->
# sources/security-integrity/ima-evm-utils/src/evmctl.c

## Purpose
`evmctl.c` implements the `evmctl` command-line utility for Linux IMA/EVM workflows. It signs and verifies EVM metadata signatures, IMA file signatures and hashes, imports public keys into kernel keyrings, writes IMA xattrs from signature files, recursively fixes or clears IMA/EVM xattrs, signs precomputed hashes including fs-verity digests, verifies IMA measurement lists against TPM PCRs, and calculates boot aggregate digests.

## Important APIs, Types, And Functions
The CLI is organized around `struct command cmds[]`, `struct option opts[]`, and `main()` option parsing. Global state captures selected hash/key/signature behavior: `g_hash_algo`, `imaevm_params.keyfile`, `g_keypass`, `sigflags`, `g_signature_version`, xattr namespace names, EVM metadata overrides, PCR file options, and OpenSSL engine/provider access.

Core file/xattr functions include `hash_ima()`, `sign_ima()`, `sign_evm()`, `verify_ima()`, `verify_evm()`, `setxattr_ima()`, `calc_evm_hash()`, and `calc_evm_hmac()`. Recursive traversal is handled by `do_cmd()`, `get_file_type()`, `find()`, `ima_fix()`, and `ima_clear()`. Measurement handling is centered on `struct template_entry`, `ima_measurement()`, `ima_ng_show()`, `extend_tpm_banks()`, `compare_tpm_banks()`, and `cmd_ima_bootaggr()`.

## Control Flow
`main()` initializes OpenSSL, parses global options, configures optional PKCS#11 engine/provider access, then dispatches by command name through `call_command()`. Signing commands calculate a digest from file data or EVM metadata, call libimaevm signing routines, prepend the xattr type where needed, and either print/write `.sig` files or set `security.ima`/`security.evm` xattrs. Verification commands load one or more X.509 public keys, recover the signature hash algorithm, recompute the relevant digest, and call libimaevm verification.

IMA measurement replay reads a binary measurement list record by record, reconstructs per-bank PCR extends, optionally verifies template hashes and template signatures, and compares recalculated banks to TPM/sysfs/user-supplied PCR values after each entry. Boot aggregate calculation reads either live PCRs or a TPM 1.2 BIOS event log, hashes PCRs 0-7 for SHA1 or 0-9 for other banks, and prints `<algo>:<digest>` lines.

## State And Persistence
Persistent effects are direct and security-sensitive: xattrs are written or removed, `.sig` sidecar files may be created, kernel keyrings may receive public keys, and request results depend on live TPM/sysfs state. `find()` changes process working directory during recursion and restores via `chdir("..")`, so relative paths and errors during recursion are important. Global option state is process-local but widely shared across handlers.

## Dependencies And Integration Points
The file integrates libimaevm, OpenSSL EVP/HMAC/RSA/X.509, Linux xattrs, keyutils, filesystem `FS_IOC_GETVERSION`, TPM PCR helpers via `pcr.h`, `blkid` through `popen()`, and Linux IMA/EVM xattr conventions. Compile-time gates control deprecated signature-v1, OpenSSL engine/provider, and debug-only HMAC command support.

## Risks
The EVM digest format is sensitive to metadata width, inode/generation/UUID portability flags, xattr ordering, and optional override strings. Several parsers use fixed-size buffers and assertions; malformed signature/hash input or unexpected xattr sizes can fail hard. `find()` ignores callback return values for child recursion in some paths and relies on `dirent.d_type`, which can be `DT_UNKNOWN` on some filesystems. The measurement parser exits on some malformed records, mixes endianness assumptions with binary log data, and supports only known template layouts. PKCS#11 usage requires key IDs and provider/engine setup, otherwise signing fails late.

## Test Signals
Relevant tests are declared in `tests/Makefile.am` and `tests/kernel/Makefile.am`: `ima_hash.test`, `sign_verify.test`, `boot_aggregate.test`, `ima_policy_check.test`, plus kernel tests for fs-verity, portable signatures, mmap checks, EVM HMAC, non-action rule flags, and creds checks. `functions.sh`, `gen-keys.sh`, `softhsm_setup`, and install helper scripts provide key material, PKCS#11, TPM, OpenSSL, and fs-verity prerequisites.
<!-- END_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/src/evmctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/src/imaevm.h -->
# sources/security-integrity/ima-evm-utils/src/imaevm.h

## Purpose
`imaevm.h` is the public and internal contract for libimaevm and `evmctl`. It defines IMA/EVM xattr types, signature formats, digest/key algorithm identifiers, metadata hash layouts, global library parameters, OpenSSL access wrappers, and the exported signing, verification, hash, key-loading, key-id, and signature-v3 APIs.

## Important APIs, Types, And Functions
Important constants include `DEFAULT_HASH_ALGO`, `DATA_SIZE`, `MAX_DIGEST_SIZE`, `MAX_SIGNATURE_SIZE`, `MAX_TEMPLATE_SIZE`, `NUM_PCRS`, and `DEFAULT_PCR`. `enum evm_ima_xattr_type` maps xattr payload types such as IMA digest, EVM HMAC, IMA/EVM digital signatures, portable signatures, and fs-verity signatures. `struct h_misc`, `h_misc_32`, and `h_misc_64` encode EVM metadata hash trailers.

Signature structures include deprecated `struct signature_hdr` for v1 and `struct signature_v2_hdr` for v2/v3 asymmetric signatures. `struct libimaevm_params` holds process-wide defaults. `struct imaevm_ossl_access` abstracts OpenSSL engine/provider handles. Exported modern APIs include `ima_calc_hash2()`, `imaevm_signhash()`, `imaevm_verify_hash()`, `ima_verify_signature2()`, `imaevm_init_public_keys()`, `imaevm_free_public_keys()`, `imaevm_hash_algo_from_sig()`, `imaevm_hash_algo_by_id()`, `calc_hash_sigv3()`, and `imaevm_create_sigv3()`.

## Control Flow
The header does not execute control flow, but it shapes caller behavior. Callers choose xattr type, hash algorithm, key files, signature flags, and OpenSSL access mode, then call library routines that fill or validate binary signature buffers matching these packed structs.

## State And Persistence
`imaevm_params` is a global mutable configuration object shared by the library and CLI. Its fields can alter default hash algorithm, key file, password, key ID, X.509 behavior, engine, and HMAC key path. The packed structs define persistent on-disk/in-xattr ABI and must remain kernel-compatible.

## Dependencies And Integration Points
The header depends on Linux `fs.h`, syslog, OpenSSL RSA/provider/engine types, and kernel hash enum compatibility through `hash_info.h` consumers. It is consumed by both CLI code and external libimaevm users, with deprecated wrappers kept for ABI/API continuity.

## Risks
Packed ABI changes would break existing xattrs and kernel interoperability. `MAX_SIGNATURE_SIZE` is sized for ML-DSA-87 and affects template limits; callers must still pass adequate buffers. Global mutable parameters are convenient but make thread safety and concurrent independent signing contexts risky. Deprecated v1 interfaces remain available under compatibility macros but should be avoided.

## Test Signals
Coverage is indirect through signing, verification, hash, and measurement tests. `gen-keys.sh` exercises RSA, EC, GOST, SM2, and ML-DSA paths when available; kernel tests validate signatures that the kernel must accept.
<!-- END_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/src/imaevm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/src/libimaevm.c -->
# sources/security-integrity/ima-evm-utils/src/libimaevm.c

## Purpose
`libimaevm.c` implements the reusable IMA/EVM cryptographic library. It calculates file hashes, loads public and private keys, derives key IDs, creates and verifies IMA/EVM signature formats v1/v2/v3, handles X.509 SKID extraction, supports PKCS#11 via OpenSSL engine/provider abstractions, and initializes OpenSSL algorithms.

## Important APIs, Types, And Functions
Hashing starts with `ima_calc_hash2()` and `add_file_hash()`. Public key APIs include `read_pub_pkey()`, `read_pub_key()`, `imaevm_init_public_keys()`, `imaevm_free_public_keys()`, and key lookup via `find_keyid()`. Signing APIs include `imaevm_signhash()`, `sign_hash_v2()`, optional `sign_hash_v1()`, and `imaevm_create_sigv3()`. Verification APIs include `imaevm_verify_hash()`, `ima_verify_signature2()`, `verify_hash_v2()`, `verify_hash_v3()`, and optional v1 verification. Key ID helpers are `calc_keyid_v1()`, `calc_keyid_v2()`, `read_keyid_from_cert()`, and `imaevm_read_keyid()`.

OpenSSL access is abstracted by `read_priv_pkey()`, `read_priv_pkey_engine()`, `read_priv_pkey_provider()`, and `check_ossl_access()`. On OpenSSL 3.5+, ML-DSA message signing and verification use `create_sigv3_mldsa()` and `verify_mldsa()`.

## Control Flow
Signing reads a private key, builds a signature header, selects the digest algorithm, derives or overrides the key ID, initializes an EVP signing context, signs either the supplied digest or a sigv3-derived `ima_file_id` digest, and returns the binary header plus signature. Sigv3 first binds xattr type, hash algorithm, and file hash into a compact `ima_file_id`; for ML-DSA it signs the message form directly.

Verification validates xattr type and signature version, extracts the hash algorithm and key ID, finds the public key, configures EVP verification, and validates either the raw file digest or the sigv3 derived digest. Public key initialization accepts comma/space/tab-separated certificate paths and builds a linked list of `public_key_entry` objects.

## State And Persistence
`imaevm_params` stores global defaults. `g_public_keys` supports deprecated global-key APIs. Signature buffers and key IDs are persistent ABI data written by callers into xattrs or keyrings. `find_keyid()` mutates the public-key list by appending placeholder entries for unknown key IDs, which affects repeated diagnostics.

## Dependencies And Integration Points
The library depends on OpenSSL EVP, X.509, PEM, provider/store/UI, optional engine APIs, Linux byte-order macros, and kernel-compatible hash names. It is the central integration point for `evmctl`, tests, and external libimaevm consumers.

## Risks
Cryptographic behavior depends heavily on OpenSSL version and compile-time options. PKCS#11 URIs require explicit nonzero key IDs. Sigv2 refuses key types that do not sign hashes, while sigv3 adds direct ML-DSA message signing under OpenSSL 3.5+. Buffer sizes are conservative for common RSA but sigv2 uses a 1024-byte internal payload limit, so large non-ML-DSA signatures can fail. Global params and deprecated globals are not naturally thread-safe.

## Test Signals
`sign_verify.test`, `ima_hash.test`, `gen-keys.sh`, and `softhsm_setup` exercise hash/sign/verify, X.509 SKID, PKCS#11, and algorithm variants. Kernel tests validate that portable and fs-verity signatures interoperate with live IMA appraisal.
<!-- END_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/src/libimaevm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/src/pcr.h -->
# sources/security-integrity/ima-evm-utils/src/pcr.h

## Purpose
`pcr.h` defines the minimal backend-neutral contract used by `evmctl` to read TPM 2.0 PCR values.

## Important APIs, Types, And Functions
It declares `tpm2_pcr_supported()` and `tpm2_pcr_read(const char *algo_name, uint32_t pcr_handle, uint8_t *hwpcr, int len, char **errmsg)`. Implementations live in IBM TSS, Intel ESAPI, and `tsspcrread` command backends.

## Control Flow
`evmctl` first calls `tpm2_pcr_supported()` before attempting live userspace PCR reads. It then calls `tpm2_pcr_read()` for each supported hash bank and PCR index.

## State And Persistence
The interface is stateless. Implementations may cache paths or allocate error strings, but callers own `errmsg` cleanup when set.

## Dependencies And Integration Points
The contract bridges `evmctl.c` measurement verification and whichever TPM backend was selected at build time.

## Risks
All backends must agree on return codes, digest lengths, algorithm names, and `errmsg` allocation semantics. A mismatch can make measurement verification silently skip banks or produce confusing diagnostics.

## Test Signals
Signals come from `boot_aggregate.test`, `ima_measurement` command coverage, and optional TPM/swtpm setup helpers.
<!-- END_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/src/pcr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/src/pcr_ibmtss.c -->
# sources/security-integrity/ima-evm-utils/src/pcr_ibmtss.c

## Purpose
`pcr_ibmtss.c` implements the `pcr.h` interface using IBM TSS library APIs. It reads one TPM 2.0 PCR at a time for the requested hash bank and copies the binary digest into the caller buffer.

## Important APIs, Types, And Functions
`tpm2_pcr_supported()` reports IBM TSS availability. `Algorithm_Map` maps `sha1`, `sha256`, `sha384`, and `sha512` strings to TCG algorithm IDs. `algorithm_string_to_algid()` validates algorithm names. `tpm2_pcr_read()` constructs `PCR_Read_In`, creates a `TSS_CONTEXT`, executes `TPM_CC_PCR_Read`, validates the returned digest count and size, and copies the digest.

## Control Flow
The read path converts the algorithm, creates the TSS context, selects one PCR bit in a three-byte PCR selection, calls `TSS_Execute()`, checks for an allocated bank and matching digest length, then deletes the context regardless of success.

## State And Persistence
No persistent state is stored. `errmsg` may be allocated with `asprintf()` on validation failures. The TPM device state is read-only from this module's perspective.

## Dependencies And Integration Points
It depends on `ibmtss/tss.h`, OpenSSL SHA headers for digest constants, `utils.h`, and libimaevm logging. `evmctl` uses this backend during measurement and boot aggregate commands when compiled with IBM TSS support.

## Risks
Unsupported algorithms return `TPM_ALG_ERROR`. The function validates only returned digest length/count, not the returned selection structure. A non-null `tss_context` is passed to `TSS_Delete()` even after early failures, relying on the library handling null safely. Error text is not produced for every TSS failure path.

## Test Signals
`install-tss.sh` and `install-swtpm.sh` provide CI setup for IBM TSS and software TPM paths. Boot aggregate and measurement list tests are the main behavioral checks.
<!-- END_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/src/pcr_ibmtss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/src/pcr_tss.c -->
# sources/security-integrity/ima-evm-utils/src/pcr_tss.c

## Purpose
`pcr_tss.c` implements the `pcr.h` interface using Intel TSS2 ESAPI. It reads a selected TPM 2.0 PCR and verifies that the TPM returned exactly the requested selection and digest size.

## Important APIs, Types, And Functions
`tpm2_pcr_supported()` logs the selected TSS2 library. `algo_to_tss2()` maps string names to `TPM2_ALG_*`. `pcr_selections_match()` compares TPM selection structures. `tpm2_set_errmsg()` formats TSS2 errors, optionally using `Tss2_RC_Decode()`. `tpm2_pcr_read()` initializes ESAPI, calls `Esys_PCR_Read()`, validates selection and digest count/size, copies the digest, and frees ESAPI allocations.

## Control Flow
The function builds a single-bank, single-PCR selection, initializes `ESYS_CONTEXT`, performs an unauthenticated PCR read, finalizes the context, validates the output selection, then returns the digest or an allocated error string.

## State And Persistence
The module holds no persistent state. It allocates and frees ESAPI-returned structures for each read.

## Dependencies And Integration Points
It depends on `tss2/tss2_esys.h` and optionally `tss2/tss2_rc.h`. It is an interchangeable PCR backend for `evmctl` measurement verification.

## Risks
The ABI version is hard-coded, which can matter with older or newer TSS2 stacks. Error formatting writes through `errmsg`; callers must free allocated text. The backend returns failure for any selection mismatch, which is appropriate but can expose TPM/library quirks.

## Test Signals
Measurement and boot aggregate commands exercise it when built with ESAPI. A TPM simulator or hardware TPM is required for live end-to-end validation.
<!-- END_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/src/pcr_tss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/src/pcr_tsspcrread.c -->
# sources/security-integrity/ima-evm-utils/src/pcr_tsspcrread.c

## Purpose
`pcr_tsspcrread.c` implements the `pcr.h` interface by locating and invoking the external IBM TSS `tsspcrread` command.

## Important APIs, Types, And Functions
`tpm2_pcr_supported()` uses `get_cmd_path()` to resolve `tsspcrread` into a static `path` buffer. `tpm2_pcr_read()` builds a command line with `-halg`, `-ha`, and `-ns`, reads one output line through `popen()`, converts hex to binary with `hex2bin()`, and returns command failure output through `errmsg`.

## Control Flow
Support probing must run before reads so `path` is populated. Each PCR read shells out, captures the first line, closes the process, treats short successful output as an unallocated bank, and converts the line into the requested digest length.

## State And Persistence
The static `path` buffer is process state. No disk state is modified. The external command reads TPM state.

## Dependencies And Integration Points
This backend depends on `PATH`, `tsspcrread`, shell command execution through `popen()`, `utils.c`, and libimaevm logging. It is a fallback-style integration where direct library linkage is not used.

## Risks
The command line is constructed with algorithm and PCR values controlled by program options; algorithm names are expected to be trusted internal values. Output parsing assumes one hex line and does not strongly validate exact length before `hex2bin()`. Forking for every PCR is slower than library backends.

## Test Signals
`boot_aggregate.test` and measurement verification can exercise this backend when `tsspcrread` is installed. `get_cmd_path()` behavior is independently relevant.
<!-- END_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/src/pcr_tsspcrread.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/src/utils.c -->
# sources/security-integrity/ima-evm-utils/src/utils.c

## Purpose
`utils.c` provides small utility routines shared by TPM and CLI code: executable lookup in `PATH`, single-hex-character conversion, and hex-string-to-binary decoding.

## Important APIs, Types, And Functions
`get_cmd_path()` scans `$PATH` and writes the first readable regular-file match for a program into a caller buffer. `hex_to_bin()` maps ASCII hex digits to nibbles. `hex2bin()` decodes a requested number of bytes from hex text into a destination buffer, skipping single spaces between bytes.

## Control Flow
`get_cmd_path()` iterates colon-separated path elements, expanding empty elements to `.`, appending the program name with a slash if needed, and returning once `file_exist()` confirms readability and regular-file type. `hex2bin()` loops over `count` bytes and stops with `-1` on invalid nibbles.

## State And Persistence
The file is stateless. It reads environment state via `PATH` and filesystem metadata through `access()`/`stat()`.

## Dependencies And Integration Points
`pcr_tsspcrread.c` uses `get_cmd_path()`. `evmctl.c` and TPM backends use `hex2bin()` for PCR files, UUID/xattr parsing, and command output conversion.

## Risks
`get_cmd_path()` uses readable regular files rather than executability, so it may accept non-executable files. It relies on careful buffer-length checks around `snprintf()`. `hex2bin()` does not skip arbitrary whitespace and assumes the caller provides enough source characters and destination space.

## Test Signals
Coverage is indirect through PCR command lookup, PCR file parsing, hash/sign input parsing, and xattr override tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/src/utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/src/utils.h -->
# sources/security-integrity/ima-evm-utils/src/utils.h

## Purpose
`utils.h` declares the shared utility functions used by ima-evm-utils source files.

## Important APIs, Types, And Functions
It includes `ctype.h` and `sys/types.h`, then declares `get_cmd_path()`, `hex_to_bin()`, and `hex2bin()`.

## Control Flow
There is no runtime control flow in the header. It exposes utility contracts for command lookup and hex decoding.

## State And Persistence
The header itself is stateless. Implementations read process environment and input buffers.

## Dependencies And Integration Points
It is included by `utils.c`, TPM backends, and code paths needing hex conversion. It keeps utility prototypes separate from libimaevm's larger ABI header.

## Risks
The header does not document buffer ownership or exact parse semantics, so callers must know that `hex2bin()` returns `-1` on invalid hex and that `get_cmd_path()` writes into caller-owned storage.

## Test Signals
Indirect coverage comes from the same code paths as `utils.c`.
<!-- END_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/src/utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/tests/Makefile.am -->
# sources/security-integrity/ima-evm-utils/tests/Makefile.am

## Purpose
This automake fragment defines the top-level ima-evm-utils test scripts, optional kernel-test subdirectory, cleanup behavior, log display helper, shellcheck target, and key cleanup hook.

## Important APIs, Types, And Functions
It populates `check_SCRIPTS` and `TESTS`, adds `kernel` to `SUBDIRS` when `KERNEL_TESTS` is enabled, and declares `ima_hash.test`, `sign_verify.test`, `boot_aggregate.test`, and `ima_policy_check.test`. Phony targets include `check_logs`, `shellcheck`, and `distclean-keys`.

## Control Flow
Automake runs scripts listed in `TESTS`. `check_logs` prints selected log tails for long hash/sign logs and full logs for others, then delegates to the kernel subdir. Cleanup removes generated signatures/output text and calls `gen-keys.sh clean`.

## State And Persistence
Generated test artifacts include `.txt`, `.out`, `.sig`, `.sig2`, and key material created by `gen-keys.sh`. Distclean removes generated keys and CA config.

## Dependencies And Integration Points
The file integrates tests with automake and shellcheck, and conditionally includes kernel-level tests that require a suitable kernel/securityfs environment.

## Risks
`check_logs` always calls `make -C kernel $@`, so builds without generated kernel makefiles or with disabled subdirs may need automake context. Test scripts depend on system capabilities such as xattrs, OpenSSL algorithms, TPM helpers, and IMA policy access.

## Test Signals
This file is itself the test signal inventory for top-level userspace functionality.
<!-- END_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/tests/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/tests/functions.sh -->
# sources/security-integrity/ima-evm-utils/tests/functions.sh

## Purpose
`functions.sh` is the shared Bash test harness for ima-evm-utils. It provides automake-compatible pass/fail/skip accounting, wrappers for positive and negative tests, `evmctl` execution, xattr extraction/assertion, OpenSSL engine setup, SoftHSM setup/teardown, and optional UML-style test environment initialization/cleanup.

## Important APIs, Types, And Functions
Key functions include `expect_pass()`, `expect_fail()`, `expect_pass_if()`, `expect_fail_if()`, `_evmctl_run()`, `_extract_xattr()`, `_test_xattr()`, `_enable_gost_engine()`, `_report_exit_and_cleanup()`, `_softhsm_setup()`, `_softhsm_teardown()`, `_run_env()`, `_exit_env()`, `_init_env()`, and `_cleanup_env()`. Exit code constants match automake: `OK=0`, `FAIL=1`, `SKIP=77`, with `HARDFAIL=99`.

## Control Flow
Tests call `expect_pass` or `expect_fail`, which enforce non-nesting, filter by `TST_LIST`, record outcomes, and optionally exit early. `_evmctl_run()` executes `evmctl` with verbosity/engine settings, captures output to a temporary file, classifies hard command failures, and prints diagnostics depending on expected outcome and verbosity. Environment helpers set up mounts and shutdown behavior when running as PID 1 in a test VM.

## State And Persistence
Global counters and mode flags track test state. Temporary output files are deleted after each command. `WORKDIR`, SoftHSM config directories, mounted filesystems, and generated key/token state are cleaned by helper functions when tests cooperate.

## Dependencies And Integration Points
The harness depends on Bash, automake exit code conventions, `getfattr`, `xxd`, OpenSSL, optional GOST engine, SoftHSM, GnuTLS `p11tool`, and kernel filesystems for environment tests.

## Risks
The script uses global variables heavily, so tests must reset or avoid collisions. `_evmctl_run()` builds a command string and executes it unquoted through `$cmd`, which is convenient for option injection but sensitive to paths with spaces. VM cleanup can call `poweroff -f` when running in test environment mode.

## Test Signals
All userspace and kernel shell tests report through this harness; failures here affect every test's classification and diagnostics.
<!-- END_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/tests/functions.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/tests/gen-keys.sh -->
# sources/security-integrity/ima-evm-utils/tests/gen-keys.sh

## Purpose
`gen-keys.sh` generates test private keys, public keys, and DER certificates used by signing and verification tests.

## Important APIs, Types, And Functions
The script creates `test-ca.conf`, then generates RSA keys/certs including a custom SKID variant, EC keys for `prime256v1` and `secp384r1`, GOST EC-RDSA keys for several paramsets, optional SM2 keys using `/opt/openssl3/bin/openssl`, and optional ML-DSA keys if the local OpenSSL supports `mldsa44`.

## Control Flow
With `clean`, it removes generated configuration and key/cert/pub files. With `force` or stale/missing outputs, it regenerates material. The `log()` helper echoes and evaluates OpenSSL commands. Algorithm blocks are guarded by tool availability and output existence.

## State And Persistence
Generated files are left in the tests directory for reuse and removed only by explicit clean/distclean. For the RSA SKID case, the script appends PEM certificate text to the private key to test combined key/cert handling.

## Dependencies And Integration Points
It depends on OpenSSL command-line behavior and the local `../src` path. Test scripts consume the generated `.key`, `.cer`, and `.pub` files to cover libimaevm signing and verification across algorithms.

## Risks
Algorithm availability varies by OpenSSL version and provider/engine configuration, making some generated key sets optional. `eval` in `log()` assumes controlled command strings. Long-lived generated keys are test-only and should not be confused with production keys.

## Test Signals
The breadth of generated algorithms provides direct coverage for RSA, EC, GOST, SM2, SKID-derived key IDs, and post-quantum ML-DSA paths when supported.
<!-- END_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/tests/gen-keys.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/tests/ima_policy_check.awk -->
# sources/security-integrity/ima-evm-utils/tests/ima_policy_check.awk

## Purpose
`ima_policy_check.awk` checks whether a proposed IMA policy rule is invalid, overlaps with the currently loaded policy, or already exists. It is used by tests before loading new policy rules to avoid interference.

## Important APIs, Types, And Functions
The script encodes known action keys, policy keyword keys, and option keys. It returns a bitmask: `1` invalid new rule, `2` overlapping rule, and `4` same rule exists. It normalizes `FILE_MMAP` to `MMAP_CHECK` and `PATH_CHECK` to `FILE_CHECK`.

## Control Flow
The first nonempty input line is treated as the new rule; subsequent lines are existing rules. Each rule is parsed into key/value/operator arrays. Invalid keys or non-action first tokens cause immediate invalid-rule exit. Existing rules are compared by action compatibility, shared keywords, value/operator equality, unsupported interval operators, and `^` modifiers.

## State And Persistence
All state is in AWK arrays during one invocation. No files are modified.

## Dependencies And Integration Points
`functions_kernel.sh` pipes the new rule plus `/sys/kernel/security/ima/policy` into this script before signing and loading a temporary policy file.

## Risks
The script intentionally does not understand `<`/`>` interval disjointness and treats `^` modifiers as potentially overlapping. It also cannot prove non-overlap based only on different `func` values because one operation can trigger multiple IMA hooks. These conservative choices can skip or warn on safe combinations.

## Test Signals
`ima_policy_check.test` should cover invalid, overlapping, and duplicate-rule detection. Kernel tests rely on this script to prevent cross-test policy contamination.
<!-- END_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/tests/ima_policy_check.awk -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/tests/install-fsverity.sh -->
# sources/security-integrity/ima-evm-utils/tests/install-fsverity.sh

## Purpose
This helper installs `fsverity-utils` from source for tests that need fs-verity digest/signature tooling.

## Important APIs, Types, And Functions
It runs `git clone https://git.kernel.org/pub/scm/fs/fsverity/fsverity-utils.git`, builds with `CC=gcc make -j$(nproc)`, and returns to the parent directory.

## Control Flow
The script is linear: clone, `cd`, build, `cd ..`.

## State And Persistence
It creates an `fsverity-utils` source/build directory in the current working directory. It does not install into a system prefix or clean up after itself.

## Dependencies And Integration Points
It depends on network access, Git, GCC, Make, and CPU count via `nproc`. Kernel fs-verity tests and `sign_hash --veritysig` workflows benefit from the built utilities.

## Risks
The script tracks the remote default branch rather than a pinned revision, so results can change over time. It lacks `set -e`, so some failures may continue until `cd` or make errors surface.

## Test Signals
Successful build enables fs-verity-related kernel tests and sigv3/fs-verity digest signing paths.
<!-- END_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/tests/install-fsverity.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/tests/install-mount-idmapped.sh -->
# sources/security-integrity/ima-evm-utils/tests/install-mount-idmapped.sh

## Purpose
This helper builds Christian Brauner's `mount-idmapped` test utility for idmapped-mount related kernel tests.

## Important APIs, Types, And Functions
It clones `https://github.com/brauner/mount-idmapped.git` and compiles `mount-idmapped.c` into a local `mount-idmapped` binary with `gcc`.

## Control Flow
The script is linear: clone, enter directory, compile, return.

## State And Persistence
It creates a `mount-idmapped` directory and binary in the current working tree. No cleanup or installation is performed.

## Dependencies And Integration Points
It depends on Git and GCC. Kernel tests that need idmapped mounts can use the resulting binary.

## Risks
The remote repository is not pinned. The script lacks `set -e` and does not verify kernel support or required capabilities.

## Test Signals
Presence of the built binary is a prerequisite signal for idmapped mount test coverage.
<!-- END_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/tests/install-mount-idmapped.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/tests/install-openssl3.sh -->
# sources/security-integrity/ima-evm-utils/tests/install-openssl3.sh

## Purpose
This helper builds and installs a selected OpenSSL 3 release under `/opt/openssl3` for tests requiring newer OpenSSL features.

## Important APIs, Types, And Functions
It requires `COMPILE_SSL`, downloads the matching GitHub tag tarball, extracts it, optionally sets 32-bit flags when `VARIANT=i386`, configures OpenSSL with `no-engine no-dynamic-engine`, builds, and runs `sudo make install_sw`.

## Control Flow
The script uses `set -ex`, fails if `COMPILE_SSL` is unset, performs build/install, then removes the tarball and source directory.

## State And Persistence
Persistent effects include `/opt/openssl3` binaries and libraries installed with sudo. Temporary source and tarball artifacts are removed after installation.

## Dependencies And Integration Points
It depends on network access, `wget`, `tar`, compiler toolchain, Perl/OpenSSL build system, `sudo`, and optional 32-bit build support. `gen-keys.sh` uses `/opt/openssl3/bin/openssl` for SM2 when present.

## Risks
Downloads use `--no-check-certificate`, weakening transport verification. Installation mutates system state. Build output depends on the provided tag and host toolchain.

## Test Signals
Successful install expands coverage for OpenSSL 3-only algorithms and compatibility behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/tests/install-openssl3.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/tests/install-swtpm.sh -->
# sources/security-integrity/ima-evm-utils/tests/install-swtpm.sh

## Purpose
This helper builds and installs IBM's software TPM server for TPM-dependent tests.

## Important APIs, Types, And Functions
It clones `https://github.com/kgoldman/ibmswtpm2`, builds under `ibmswtpm2/src`, and copies `tpm_server` to `/usr/local/bin/`, using `sudo` only when necessary.

## Control Flow
With `bash -ex`, it selects `SUDO` based on write permission to `/usr/local/bin`, clones, builds, copies, and returns.

## State And Persistence
It creates an `ibmswtpm2` source tree and installs `tpm_server` into `/usr/local/bin`.

## Dependencies And Integration Points
It depends on Git, Make, compiler tools, and permissions for `/usr/local/bin`. TPM PCR tests can use the installed simulator with IBM TSS.

## Risks
The cloned source is unpinned. The script does not clean the source tree after install. System installation can overwrite an existing `tpm_server`.

## Test Signals
Presence of `/usr/local/bin/tpm_server` enables software TPM-backed boot aggregate and measurement tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/tests/install-swtpm.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/tests/install-tss.sh -->
# sources/security-integrity/ima-evm-utils/tests/install-tss.sh

## Purpose
This helper builds and installs IBM TSS for TPM 2.0 PCR-reading test support.

## Important APIs, Types, And Functions
It clones `https://github.com/kgoldman/ibmtss`, runs `autoreconf -i`, configures with `--disable-tpm-1.2 --disable-hwtpm`, builds, installs with sudo, then removes the source tree.

## Control Flow
The script uses `set -ex` and stops on failed commands.

## State And Persistence
It installs IBM TSS libraries/tools into the system prefix selected by the upstream configure script. The cloned `ibmtss` directory is removed afterward.

## Dependencies And Integration Points
It depends on Git, autotools, compiler tools, Make, and sudo. `pcr_ibmtss.c` and `pcr_tsspcrread.c` test paths rely on IBM TSS components.

## Risks
The remote branch is unpinned. System installation can affect other TPM tooling. Hardware TPM is disabled in configure, which is appropriate for simulator-focused CI but not full hardware testing.

## Test Signals
Successful installation provides TPM library/tool support for measurement and boot aggregate tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/tests/install-tss.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/tests/kernel/Makefile.am -->
# sources/security-integrity/ima-evm-utils/tests/kernel/Makefile.am

## Purpose
This automake fragment defines kernel-facing ima-evm-utils tests and a small C helper program.

## Important APIs, Types, And Functions
When `KERNEL_TESTS` is enabled, `TESTS` is set to `check_SCRIPTS`. Listed scripts include `fsverity.test`, `portable_signatures.test`, `mmap_check.test`, `evm_hmac.test`, `non_action_rule_flags.test`, and `creds_check.test`. `check_PROGRAMS := test_mmap` builds the mmap helper.

## Control Flow
Automake builds `test_mmap` and runs the script tests. `check_logs` prints full logs. Cleanup removes generated text/output/signature artifacts and delegates key cleanup to `../gen-keys.sh clean`.

## State And Persistence
Tests may create xattrs, temporary files, signed policy files, and generated keys. The makefile cleanup removes only local generated artifacts.

## Dependencies And Integration Points
It integrates the top-level test harness with kernel securityfs, IMA/EVM policy, keyrings, fs-verity, and mmap behavior.

## Risks
Kernel tests require privileged operations and suitable kernel config. Running them on a host with an existing IMA policy can be disruptive unless policy overlap checks work correctly.

## Test Signals
This file declares the kernel-level validation surface for portable signatures, fs-verity signatures, HMAC, policy rule flags, creds, and mmap hooks.
<!-- END_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/tests/kernel/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/tests/kernel/functions_kernel.sh -->
# sources/security-integrity/ima-evm-utils/tests/kernel/functions_kernel.sh

## Purpose
`functions_kernel.sh` extends the shared test harness with helpers for live-kernel IMA policy loading, xattr extraction, private key discovery/conversion, and public key loading into kernel keyrings.

## Important APIs, Types, And Functions
`get_xattr()` reads a named xattr in hex or text form. `check_load_ima_rule()` validates a proposed policy rule with `ima_policy_check.awk`, signs a temporary policy file with `evmctl sign -o -a sha256 --imasig`, and writes it to `/sys/kernel/security/ima/policy`. `get_private_key()` finds or copies/converts a kernel signing key. `load_public_key()` converts a certificate to DER and adds it to a selected keyring with `keyctl padd asymmetric`.

## Control Flow
The script sets `PATH` to include source and test directories, sources `../functions.sh`, and exposes helper functions. Policy loading is conservative: invalid rules hard-fail; overlapping rules warn outside test environments but hard-fail inside `TST_ENV`; duplicate rules are treated as success.

## State And Persistence
It can add IMA policy rules, create temporary signed policy files, copy key material, and add asymmetric keys to kernel keyrings. These effects may persist for the boot/session.

## Dependencies And Integration Points
It depends on `getfattr`, `awk`, `evmctl`, `openssl`, `keyctl`, securityfs, and accessible kernel signing key/certificate paths or explicit `TST_KEY_PATH`/`TST_CERT_PATH`.

## Risks
Policy loading is irreversible for the running kernel and can affect later tests. Key discovery supports several host paths but skips when unavailable. The helper assumes policy files must be signed before loading.

## Test Signals
All kernel tests that need signed policy updates or appraisal key setup depend on this file.
<!-- END_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/tests/kernel/functions_kernel.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/tests/kernel/test_mmap.c -->
# sources/security-integrity/ima-evm-utils/tests/kernel/test_mmap.c

## Purpose
`test_mmap.c` is a small helper program for testing IMA `MMAP_CHECK` and `MMAP_CHECK_REQPROT` hooks under different mmap and mprotect scenarios.

## Important APIs, Types, And Functions
`main()` accepts a file path and optional mode: `read_implies_exec`, `exec_on_writable`, `exec*`, or `mprotect`. It uses `personality(READ_IMPLIES_EXEC)`, `stat()`, `open()`, `mmap()`, `mprotect()`, and `munmap()`. Return codes distinguish setup errors (`1`) from expected test-condition denials (`2`).

## Control Flow
The program validates the file, optionally sets personality, optionally creates a writable shared mapping, opens the file read-only, maps it with `PROT_READ` and optionally `PROT_EXEC`, handles expected denial cases, optionally calls `mprotect(PROT_EXEC)`, unmaps, and exits with the classification code.

## State And Persistence
It does not persist data, but may temporarily create mappings and alter process personality. It opens the target file read-only except for the writable mapping scenario.

## Dependencies And Integration Points
Kernel tests use it to trigger IMA mmap hooks and check whether policy/appraisal blocks execution mapping as expected.

## Risks
Behavior is kernel-policy dependent. `personality(READ_IMPLIES_EXEC)` affects the current process only. File size zero or unusual files may affect mmap behavior.

## Test Signals
The helper's exit code is the primary signal for `mmap_check.test`: `0` for allowed mapping, `2` for expected policy denial, `1` for setup failure.
<!-- END_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/tests/kernel/test_mmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/tests/softhsm_setup -->
# sources/security-integrity/ima-evm-utils/tests/softhsm_setup

## Purpose
`softhsm_setup` creates, queries, and tears down a temporary SoftHSM token for PKCS#11 signing tests.

## Important APIs, Types, And Functions
Commands are `setup`, `getkeyuri`, `getpubkey`, and `teardown`. Functions include `setup_softhsm()`, `teardown_softhsm()`, `_getkeyuri_softhsm()`, `getkeyuri_softhsm()`, `getpubkey_softhsm()`, `usage()`, and `main()`. It uses `softhsm2-util` and `p11tool` to initialize a token named `swtpm-test` and generate/export an RSA key.

## Control Flow
Startup checks for required tools and SoftHSM version. Setup creates or backs up SoftHSM config, initializes a token if needed, generates a private key with either modern `--generate-privkey=rsa` or older `--generate-rsa`, then prints a `keyuri:` line with PIN value. Teardown deletes the token, restores config backups, and removes token directories.

## State And Persistence
It writes `softhsm2.conf`, token storage under `SOFTHSM_SETUP_CONFIGDIR`, and on macOS may temporarily replace `/etc/gnutls/pkcs11.conf`. PINs default to `1234` but can be overridden.

## Dependencies And Integration Points
`functions.sh` calls it through `_softhsm_setup()` and `_softhsm_teardown()`. It depends on `p11tool`, `softhsm2-util`, optional sudo on macOS, and GnuTLS PKCS#11 configuration.

## Risks
Config backup/restore must be correct to avoid disturbing user SoftHSM/GnuTLS state. The printed URI includes a PIN value for test convenience. Setup is sensitive to output parsing from external tools.

## Test Signals
Successful `setup` prints `keyuri: ...`, enabling PKCS#11 key tests for engine/provider code paths.
<!-- END_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/tests/softhsm_setup -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/Makefile -->
# sources/security-integrity/keyutils/Makefile

## Purpose
The keyutils top-level `Makefile` builds the keyutils library, command-line tools, DNS resolver helper, C++ header syntax check, install targets, tests, cleanup, tarball generation, and RPM packaging.

## Important APIs, Types, And Functions
Major variables include `VERSION`, `APIVERSION`, `ARLIB`, `DEVELLIB`, `SONAME`, `LIBNAME`, `LIBDIR`, `USRLIBDIR`, `NO_ARLIB`, `NO_SOLIB`, and `NO_GLIBC_KEYERR`. Targets build `libkeyutils.a`, `libkeyutils.so.*`, `keyctl`, `request-key`, `key.dns_resolver`, `cxx.stamp`, install artifacts, tests, tarballs, SRPM/RPMs, and `show_vars`.

## Control Flow
Version data is derived from `keyutils.spec` and `version.lds`. Architecture/libdir defaults are inferred from system binaries. Conditional blocks build static/shared libraries unless disabled. Programs link against the locally built library. Install targets copy binaries, libraries, config, pkg-config data, headers, man pages, and symlinks into `DESTDIR` paths.

## State And Persistence
Build artifacts include libraries, object files, binaries, pkg-config files, symlinks, tarballs, and RPM build directories. Install mutates the destination filesystem with keyutils tools and configuration.

## Dependencies And Integration Points
It depends on GCC/G++, binutils, Make, sed, grep, ldd, file, rpmspec/rpmbuild for packaging, `libresolv` for `key.dns_resolver`, and the local version script. It installs `/sbin/key.dns_resolver` and request-key configuration used by kernel key request callouts.

## Risks
Libdir and word-size inference are host-specific. `CFLAGS :=` at the top can override environment expectations unless passed by make origin logic later. Install symlinks are absolute-ish through `$(LIBDIR)` and `$(USRLIBDIR)` choices, so packaging paths need review.

## Test Signals
`make test` delegates to `tests run`; `cxx.stamp` checks public header C++ syntax; `-Wall -Werror` makes compiler warnings fail the build.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/dns.afsdb.c -->
# sources/security-integrity/keyutils/dns.afsdb.c

## Purpose
`dns.afsdb.c` extends `key.dns_resolver` with AFS volume-location DNS support. It resolves AFSDB or RFC 5864 SRV records for a cell into address payloads that can instantiate a kernel `dns_resolver` key for kAFS.

## Important APIs, Types, And Functions
`afsdb_hosts_to_addrs()` parses AFSDB records, deduplicates VL server names, resolves them with `dns_resolver()`, and tracks minimum TTL. `srv_hosts_to_addrs()` does the same for `_afs3-vlserver._udp.<cell>` SRV records, adding `+port` suffixes. `dns_query_AFSDB()` and `dns_query_VL_SRV()` issue resolver queries and parse DNS responses. `afs_instantiate()` sets key timeout, appends a terminating NUL payload segment, dumps payload, and calls `keyctl_instantiate_iov()`. `afs_look_up_VL_servers()` selects address-family mask options, tries SRV first, falls back to AFSDB, and instantiates.

## Control Flow
The public entry point is `afs_look_up_VL_servers(cell, options)`. It constrains `mask` for `ipv4` or `ipv6`, queries SRV records first, falls back to AFSDB on failure, then calls the no-return instantiation path. Record parsing walks answer sections, expands compressed target names, ignores duplicates, resolves targets to addresses, and records the minimum TTL.

## State And Persistence
The file modifies globals from `key.dns_resolver.c`: `mask`, `payload`, `payload_index`, `key_expiry`, `key`, and `debug_mode`. In non-debug mode it sets kernel key timeout and instantiates the key payload.

## Dependencies And Integration Points
It depends on libresolv nameser APIs, `getaddrinfo()` through shared `dns_resolver()`, and keyutils key instantiation. It is compiled into `key.dns_resolver` by the Makefile.

## Risks
`vllist` is capped by `MAX_VLS` but the code does not explicitly stop before exceeding the array if DNS returns many unique records. Some allocated host strings are not freed after successful use because the process exits soon after instantiation. `strcmp(options, ...)` assumes non-null options from the caller.

## Test Signals
Testing requires debug-mode invocations or request-key integration with controlled DNS records. Useful signals are payload contents, TTL selection, duplicate suppression, SRV fallback to AFSDB, and IPv4/IPv6 option handling.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/dns.afsdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/key.dns.h -->
# sources/security-integrity/keyutils/key.dns.h

## Purpose
`key.dns.h` is the shared header for the keyutils DNS resolver helper and its AFSDB/SRV support module.

## Important APIs, Types, And Functions
It includes resolver, networking, syslog, keyutils, and standard C headers. It defines address-family and payload constants: `MAX_VLS`, `INET_IP4_ONLY`, `INET_IP6_ONLY`, `INET_ALL`, `ONE_ADDR_ONLY`, and `N_PAYLOAD`. It declares shared globals `key`, `debug_mode`, `mask`, `key_expiry`, `payload`, and `payload_index`, plus logging/error APIs, payload helpers, `dns_resolver()`, and `afs_look_up_VL_servers()`.

## Control Flow
No runtime control flow exists in the header. It documents the cross-file calling pattern: `key.dns_resolver.c` owns main, shared state, generic A/AAAA resolution, and error handling; `dns.afsdb.c` owns AFS-specific lookup and instantiation.

## State And Persistence
The declared globals carry request state for one resolver process and ultimately determine kernel key payload and timeout.

## Dependencies And Integration Points
It ties together libresolv, keyutils, syslog, sockets, and DNS helper source files. The Makefile compiles both C files into one helper.

## Risks
Global shared state makes the helper simple but not reusable as a library or thread-safe component. Constants cap payload segments and VL servers; callers must handle overflow behavior indirectly.

## Test Signals
Any DNS helper test should validate global state transitions by inspecting debug payload output or instantiated key contents.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/key.dns.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/keyutils/key.dns_resolver.c -->
# sources/security-integrity/keyutils/key.dns_resolver.c

## Purpose
`key.dns_resolver.c` implements the `key.dns_resolver` userspace helper for Linux request-key DNS resolution. It reads a kernel key request or debug-mode description, resolves A/AAAA or AFSDB-style names, builds a comma-separated payload, sets key timeout, and instantiates or rejects the kernel key.

## Important APIs, Types, And Functions
Logging/error functions are `error()`, `_error()`, `warning()`, `info()`, `_nsError()`, `nsError()`, and `debug()`. Payload functions are `append_address_to_payload()` and `dump_payload()`. Resolver logic is in `dns_resolver()` and `dns_query_a_or_aaaa()`. Configuration is handled by `read_config()` and `config_dumper()`. `main()` parses options, reads key description/callout info, validates key type, dispatches query type, and exits via no-return query helpers.

## Control Flow
Startup parses `-c`, `-D`, `--dump-config`, `-v`, and `-V`, then reads configuration. In normal mode it expects a key serial, describes the key with `keyctl_describe_alloc()`, and reads callout info from `KEY_SPEC_REQKEY_AUTH_KEY`. In debug mode it accepts a description and callout info directly. Descriptions without `type:name` go through A/AAAA resolution; `a:` and `aaaa:` dispatch to the same A/AAAA resolver; `afsdb:` dispatches to `afs_look_up_VL_servers()`.

`dns_query_a_or_aaaa()` parses options such as `ipv4`, `ipv6`, and `list`, calls `dns_resolver()`, rejects empty/no-data results, appends a terminating NUL segment, and instantiates the key. `dns_resolver()` calls `getaddrinfo()`, filters by `mask`, converts addresses with `inet_ntop()`, optionally appends a port suffix, deduplicates through `append_address_to_payload()`, and honors `ONE_ADDR_ONLY`.

## State And Persistence
Global state includes `key`, `verbose`, `debug_mode`, `mask`, `key_expiry`, `payload`, and `payload_index`. Non-debug success calls `keyctl_set_timeout()` and `keyctl_instantiate_iov()`. DNS failures call `keyctl_reject()` with short timeout mapping; fatal helper errors call `keyctl_negate()`.

## Dependencies And Integration Points
The helper depends on keyutils APIs, libresolv/h_errno behavior, `getaddrinfo()`, syslog, `/etc/keyutils/key.dns_resolver.conf`, `/etc/request-key.conf` integration, and `dns.afsdb.c` for AFS lookups. It is installed by the Makefile as `/sbin/key.dns_resolver`.

## Risks
`append_address_to_payload()` silently stops when `N_PAYLOAD` is near exhaustion. Address string buffers leave room for IPv6 plus port suffix, but port formatting assumptions come from AFS SRV code. Config parsing is strict and exits on malformed explicit config. Debug and normal modes have different input trust boundaries. `--config` is declared with no argument in `long_options` despite `-c` requiring one, which is a CLI parsing risk for long-form config use.

## Test Signals
Useful tests cover debug-mode A/AAAA lookup, option parsing, list versus single-address payloads, IPv4/IPv6 filtering, config default TTL parsing and dump, unsupported query rejection, key description parsing, and AFSDB/SRV dispatch. Integration tests require request-key and kernel keyring behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/keyutils/key.dns_resolver.c -->
