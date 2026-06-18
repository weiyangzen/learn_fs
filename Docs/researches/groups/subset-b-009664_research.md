<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/spnego-wrapper.c -->
# sources/user-network-fs/libsmb2/lib/spnego-wrapper.c

Purpose: Implements libsmb2's SPNEGO/GSS-API ASN.1 BER token wrapping and unwrapping for SMB authentication, including NTLMSSP and optional Kerberos mechanism negotiation.

Important APIs, types, and functions: Defines static OIDs for GSS-SPNEGO, Kerberos, Microsoft Kerberos, and NTLMSSP; `oid_compare`; wrapper creators `smb2_spnego_create_negotiate_reply_blob`, `smb2_spnego_wrap_gssapi`, `smb2_spnego_wrap_ntlmssp_challenge`, `smb2_spnego_wrap_ntlmssp_auth`, and `smb2_spnego_wrap_authenticate_result`; and parsers `smb2_spnego_unwrap_targ`, `smb2_spnego_unwrap_gssapi`, and `smb2_spnego_unwrap_blob`.

Control flow: The wrapping functions allocate a BER output buffer, emit nested application/context/sequence nodes, reserve length fields, copy mechanism tokens where needed, then patch lengths. The unwrap path peeks at the first byte, recognizes raw NTLMSSP, application GSS blobs, or context-tagged SPNEGO target tokens, then decodes OIDs, mechanism flags, negotiation result, and response token pointers.

State and persistence behavior: No persistent state is stored. Returned blobs are heap allocated for the caller to free. Unwrapped tokens are pointers into the caller-supplied input buffer. Errors are stored on `struct smb2_context` unless suppressed.

Dependencies and integration points: Depends on libsmb2 private context/error handling and `asn1-ber` helpers. It is used by SMB session setup authentication paths and must agree with NTLMSSP/Kerberos code about mechanism flags from `spnego-wrapper.h`.

Risks: The buffer sizing is heuristic (`256 + 4 * token_len`, `64 + 2 * token_len`) and relies on ASN.1 helpers respecting `dst_size`. Parser macros use minimum lengths that can reject unusual but valid encodings. `smb2_spnego_unwrap_targ` accepts `mechanisms` without a NULL guard in the negResult branch. A typo in error text says `spengo`.

Test signals: Indirectly exercised by authentication tests and `ntlmssp_generate_blob.c`; no dedicated SPNEGO malformed-input unit test is present in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/spnego-wrapper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/spnego-wrapper.h -->
# sources/user-network-fs/libsmb2/lib/spnego-wrapper.h

Purpose: Declares the private SPNEGO wrapper interface used by libsmb2 authentication code.

Important APIs, types, and functions: Exports `SPNEGO_MECHANISM_KRB5` and `SPNEGO_MECHANISM_NTLMSSP` bit flags plus prototypes for negotiate, NTLMSSP challenge/auth wrapping, authenticate result wrapping, and GSS/SPNEGO blob unwrapping.

Control flow: Header-only declaration layer; callers include it and invoke the C implementation based on whether they need to produce a SPNEGO token or parse one from a server/client.

State and persistence behavior: No runtime state. It establishes the ownership contract implicitly: wrapper outputs are returned through `void **`, parser outputs point into input buffers.

Dependencies and integration points: Depends on `struct smb2_context`, `uint8_t`, and `uint32_t` from surrounding libsmb2 headers. Integrated by session setup and authentication implementation files.

Risks: The include guard is misspelled `SPEGNO_WRAPPER_H`, which is harmless but easy to propagate. Lack of explicit ownership comments can cause leaks or invalid frees by new callers.

Test signals: Compile coverage when SPNEGO implementation is built; no direct header-specific test.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/spnego-wrapper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/sync.c -->
# sources/user-network-fs/libsmb2/lib/sync.c

Purpose: Provides the synchronous public libsmb2 API by blocking on the asynchronous PDU API and servicing the SMB socket until callbacks complete.

Important APIs, types, and functions: Central helper `wait_for_reply` polls `smb2_get_fd` with `smb2_which_events`, calls `smb2_timeout_pdus` and `smb2_service`, and observes `sync_cb_data`. Synchronous wrappers include share connect/disconnect, open/close, directory open, read/write/pread/pwrite, mkdir/rmdir/unlink, stat/fstat/statvfs, rename, truncate/ftruncate, readlink, echo, notify_change, and share_enum.

Control flow: Each wrapper allocates or reuses a `sync_cb_data`, starts the matching async operation, waits, maps callback status/pointer to the synchronous return value, then frees the callback data or transfers ownership to the returned object where required. Callback variants handle shutdown/cancelled cases and command-data pointers.

State and persistence behavior: State is transient per call, except `smb2->connect_cb_data` is reused for connect/disconnect. Some async PDUs own and free callback data through destructor arguments. Returned handles, directories, notify results, and share enum replies outlive the sync call and must be freed by caller-specific APIs.

Dependencies and integration points: Depends on libsmb2 raw async APIs, poll, timeout handling, private socket fields, and callback conventions. Utilities such as `smb2-cp` and `smb2-ls` rely on these wrappers.

Risks: Several wait-failure branches set `SMB2_STATUS_CANCELLED` and return without freeing local callback data, relying on later async cancellation behavior; this is subtle and leak-prone if cancellation does not occur. `smb2_echo` returns `-ENOMEM` for not connected. Blocking calls cannot be composed inside an external event loop without tying up the caller thread.

Test signals: Covered by shell tests for ls, mkdir, cp, cat, socket-error injection, valgrind, and cancellation paths in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/sync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/timestamps.c -->
# sources/user-network-fs/libsmb2/lib/timestamps.c

Purpose: Converts timestamps between libsmb2 timeval form and Windows FILETIME units used by SMB2 metadata.

Important APIs, types, and functions: Exports `smb2_timeval_to_win` and `smb2_win_to_timeval`.

Control flow: Conversion is direct arithmetic: Unix seconds are scaled by 10,000,000, microseconds by 10, and the Windows epoch offset `116444736000000000` is added or subtracted.

State and persistence behavior: Stateless pure conversion functions. No allocation or persistence.

Dependencies and integration points: Depends on `struct smb2_timeval` from libsmb2 public/private headers. Used by metadata encoding and decoding paths.

Risks: No range checks are performed. Values before the Windows epoch or extreme future values can underflow/overflow unsigned arithmetic when represented as `uint64_t`.

Test signals: No direct test in this subset; metadata tests and directory/stat paths provide indirect coverage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/timestamps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/unicode.c -->
# sources/user-network-fs/libsmb2/lib/unicode.c

Purpose: Implements UTF-8 validation plus conversion between UTF-8 and SMB-compatible UTF-16LE strings.

Important APIs, types, and functions: Internal helpers `l1`, `validate_utf8_cp`, `validate_utf8_str`, and `utf16_size`; public functions `smb2_utf8_to_utf16` and `smb2_utf16_to_utf8`.

Control flow: UTF-8 to UTF-16 first validates and counts code units, allocates `struct smb2_utf16`, then replays decoding while writing little-endian code units and surrogate pairs. UTF-16 to UTF-8 computes output size while replacing malformed surrogate sequences, allocates a NUL-terminated string, then encodes each code unit/pair.

State and persistence behavior: Allocates returned strings/structures for callers. It does not retain state. Invalid UTF-8 returns NULL; invalid UTF-16 is converted with replacement characters.

Dependencies and integration points: Depends on portable endian macros and libsmb2 private UTF-16 type. Integrated with path, filename, and DCE/RPC text handling.

Risks: `validate_utf8_cp` advances through continuation bytes without an explicit input-end parameter, relying on NUL termination; truncated multibyte data can read past the logical character. Output length uses `int`, so extremely long names could overflow length arithmetic.

Test signals: Indirect coverage through DCE/RPC UTF-16 coder tests and SMB path operations; no direct fuzz or invalid-sequence unit test in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/unicode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/usha.c -->
# sources/user-network-fs/libsmb2/lib/usha.c

Purpose: Provides a unified dispatch layer over enabled SHA implementations from RFC 4634 style code.

Important APIs, types, and functions: Exports `USHAReset`, `USHAInput`, `USHAFinalBits`, `USHAResult`, `USHABlockSize`, `USHAHashSize`, and `USHAHashSizeBits` over `USHAContext` and `enum SHAversion`.

Control flow: Each function switches on the selected SHA version in the context or parameter and forwards to SHA1, SHA224, SHA256, SHA384, or SHA512 routines depending on compile-time feature macros. Unsupported versions return `shaBadParam`; NULL contexts return `shaNull` for context-taking functions.

State and persistence behavior: State lives in the caller-provided `USHAContext`; this file only selects the concrete algorithm context inside the union.

Dependencies and integration points: Depends on `sha.h` and compile-time `USE_SHA*` macros. Used by cryptographic code that wants algorithm-neutral SHA handling.

Risks: Default size queries return SHA512 sizes for unknown algorithms rather than an error, which can hide invalid enum use. Builds with only SHA256 enabled still expose generic names that may surprise callers expecting all algorithms.

Test signals: Indirect cryptographic coverage from signing/encryption tests; no USHA-specific vector test in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/usha.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/libsmb2.pc.in -->
# sources/user-network-fs/libsmb2/libsmb2.pc.in

Purpose: Pkg-config template describing how downstream projects compile and link against libsmb2.

Important APIs, types, and functions: Defines `prefix`, `exec_prefix`, `libdir`, `includedir`, package metadata, `Libs: -L${libdir} -lsmb2`, and `Cflags: -I${includedir}`.

Control flow: Autotools substitutes install paths and version fields, then installs the resulting `.pc` file for pkg-config consumers.

State and persistence behavior: No runtime state. Installed metadata persists in the target pkg-config directory.

Dependencies and integration points: Integrated with build/install packaging and downstream build systems. It assumes headers are visible directly from `${includedir}`.

Risks: `Requires` is empty, so private dependencies needed for static linking may not be advertised. Include path must match installed header layout from the package.

Test signals: Validated by packaging/install checks rather than runtime tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/libsmb2.pc.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/packaging/RPM/libsmb2.spec.in -->
# sources/user-network-fs/libsmb2/packaging/RPM/libsmb2.spec.in

Purpose: RPM spec template for building runtime and development libsmb2 packages.

Important APIs, types, and functions: Defines package metadata, source tarball, Autotools build recipe, install/clean phases, runtime `%files`, `devel` subpackage files, and changelog.

Control flow: RPM prep unpacks the tarball, build phase regenerates Autotools files, optionally uses ccache, runs `%configure`, then `make`; install phase uses `DESTDIR` and removes stale `.old` files.

State and persistence behavior: Persists package metadata and installed artifacts into RPM build roots. No application runtime state.

Dependencies and integration points: Depends on rpmbuild macros, Autotools, libtool, ccache optionally, and the source tree's install targets. Integrates with `makerpms.sh`.

Risks: Spec regenerates build system during package build, which can make builds sensitive to local tool versions. Devel file list is explicit and can drift when public headers change. License text is old-style and may not satisfy modern SPDX conventions.

Test signals: Package-build validation and changelog history are the main signals; no spec-specific automated test here.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/packaging/RPM/libsmb2.spec.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/packaging/RPM/makerpms.sh -->
# sources/user-network-fs/libsmb2/packaging/RPM/makerpms.sh

Purpose: Automates creation of source tarballs and RPM builds from a tagged libsmb2 git checkout.

Important APIs, types, and functions: Uses `git describe` to derive `VERSION`, rpm macro expansion for spec/source directories, optional gzip `--rsyncable`, generated spec substitution, tarball creation, and `rpmbuild` invocation.

Control flow: The script validates the tag prefix, maps exact tags to release versions and non-exact descriptions to `.devel` versions, stages sources/spec files into RPM directories, and runs the package build with optional extra configure arguments.

State and persistence behavior: Writes tarballs and spec files into the user's RPM build tree. It does not modify source files other than generated packaging outputs outside the checkout.

Dependencies and integration points: Depends on git tags, rpm/rpmbuild, tar/gzip, sed, and the RPM spec template. Intended for release engineering rather than normal library runtime.

Risks: Fails hard when not on a `libsmb2-*` describe result. Uses backticks and unquoted expansions in several places, so unusual paths may break. Reproducibility depends on local toolchain and RPM macro configuration.

Test signals: No direct test; successful RPM generation is the acceptance signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/packaging/RPM/makerpms.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/Makefile.am -->
# sources/user-network-fs/libsmb2/tests/Makefile.am

Purpose: Defines the libsmb2 test programs, test scripts, helper preload library, and check-time wiring for Automake.

Important APIs, types, and functions: Sets include paths and warning flags, lists `check_PROGRAMS`, `TESTS`, `EXTRA_PROGRAMS = ld_sockerr`, source assignments, `ld_sockerr.so` build command, and script installation through `bin_SCRIPTS`.

Control flow: Automake builds helper binaries, creates an LD_PRELOAD shared object from `ld_sockerr.c`, and runs the shell tests as the check suite.

State and persistence behavior: No runtime persistence except generated binaries and `ld_sockerr.so` in the build tree.

Dependencies and integration points: Integrates tests with libsmb2 library, libtool, shell scripts, and the utils directory. It is the hub for the test files in this subset.

Risks: Manual `gcc -shared` command may bypass normal Automake portability flags. Test scripts require `TESTURL` and a live SMB server, so default `make check` is environment-dependent.

Test signals: The listed `TESTS` provide the suite's direct execution signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/aes128ccm-test.c -->
# sources/user-network-fs/libsmb2/tests/aes128ccm-test.c

Purpose: Standalone AES-128-CCM known-vector smoke test for libsmb2 encryption support.

Important APIs, types, and functions: Defines `test_1`, `test_2`, and `main`, calling `aes128ccm_encrypt` and `aes128ccm_decrypt` with fixed key, nonce, AAD, plaintext, tag length, and expected buffers.

Control flow: Each test copies plaintext to a work buffer, encrypts in place with tag appended, prints expected/got bytes, decrypts, and exits with code 10 on decrypt failure or plaintext mismatch.

State and persistence behavior: All state is stack/local buffers. No files or network state.

Dependencies and integration points: Depends on `lib/aes128ccm.h`; integrated through test build rules.

Risks: The code prints expected ciphertext but does not actually `memcmp` encrypted bytes against `exp`, so encryption regressions that still decrypt round-trip may pass. Exit codes are coarse.

Test signals: Directly run by the test suite when included in Automake check programs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/aes128ccm-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/functions.sh -->
# sources/user-network-fs/libsmb2/tests/functions.sh

Purpose: Small shared shell helper for libsmb2 test scripts.

Important APIs, types, and functions: Defines `failure()` to print `TEST FAILED` and exit with status 1.

Control flow: Scripts source this file and call `failure` after commands that should not fail, or after commands that unexpectedly succeed.

State and persistence behavior: No persistent state.

Dependencies and integration points: Integrated by all shell tests via `. ./functions.sh`.

Risks: Only provides a generic failure path; it does not preserve command output or line numbers, which can make failures harder to diagnose.

Test signals: Every shell test in this subset uses it as the failure signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/functions.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/ld_sockerr.c -->
# sources/user-network-fs/libsmb2/tests/ld_sockerr.c

Purpose: LD_PRELOAD helper that injects socket read failures into libsmb2 tests by interposing `readv`.

Important APIs, types, and functions: Defines global `readv_close` and replacement `readv` that resolves the real function with `dlsym(RTLD_NEXT)`, reads `READV_CLOSE`, increments a call counter, writes garbage and returns `-1`/`EBADF` on the selected call.

Control flow: On first call it initializes the real `readv` pointer and target failure index. Subsequent calls pass through until the configured call count, then simulate a broken socket.

State and persistence behavior: State is process-local static `call_idx`, function pointer, and global target index. No persistence across processes.

Dependencies and integration points: Built into `ld_sockerr.so` by `tests/Makefile.am` and used by socket-error shell tests through `LD_PRELOAD`.

Risks: Interposing `readv` is platform-sensitive and can affect non-SMB file descriptors in the process. Writing garbage to the fd before failing may trigger behavior different from a pure disconnect.

Test signals: Covered by ls/cp/cat socket-error tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/ld_sockerr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/metastat-0202-censored.c -->
# sources/user-network-fs/libsmb2/tests/metastat-0202-censored.c

Purpose: Concurrency test program that queues multiple SMB2 stat requests on one connection, aimed at SMB 2.0.2 credit/overdraw behavior.

Important APIs, types, and functions: Defines `struct op`, `struct cbwrap`, `stat_cb`, `service_loop`, `usage`, and `main`. Uses `smb2_stat_async`, `smb2_service`, URL parsing, password option, and a pending counter.

Control flow: The program parses a base SMB URL plus filenames, connects to the share, queues all stat operations, polls until callbacks decrement `pending`, then reports failures.

State and persistence behavior: State is arrays of per-operation status/stat buffers and callback wrappers allocated per queued request. Network session state lives in libsmb2 context.

Dependencies and integration points: Integrated with `test_0400_overdrawn_0202.sh`, which runs several instances concurrently against discovered filenames.

Risks: Requires a live SMB server and valid URL. Pending counter mutation is single-threaded through the event loop, but callbacks allocate/free wrappers per request and can leak only if requests never complete before process exit.

Test signals: Direct test signal is successful completion under concurrent shell orchestration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/metastat-0202-censored.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/ntlmssp_generate_blob.c -->
# sources/user-network-fs/libsmb2/tests/ntlmssp_generate_blob.c

Purpose: Utility/test program that generates NTLMSSP negotiate/session blobs for inspection or regression comparison.

Important APIs, types, and functions: Main initializes an SMB2 context, accepts command-line/user parameters, calls NTLMSSP generation helpers, and prints binary/token output in a formatted form.

Control flow: Control is linear: parse arguments, create context, generate authentication blob, dump result, clean up, and exit on errors.

State and persistence behavior: Only transient heap/context state. No persistent files unless caller redirects output.

Dependencies and integration points: Depends on libsmb2 NTLMSSP/private authentication APIs and is useful for validating SPNEGO/NTLM integration.

Risks: As a generator, it can drift from wire expectations if no golden output comparison is enforced. It may expose sensitive test credentials if run with real passwords and logs captured.

Test signals: Compile/run coverage is available through the test build; no shell script in this subset compares exact blob bytes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/ntlmssp_generate_blob.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/prog_cat.c -->
# sources/user-network-fs/libsmb2/tests/prog_cat.c

Purpose: Asynchronous SMB file reader used by cat-related integration tests.

Important APIs, types, and functions: Defines callbacks for disconnect, close, read, open, connect, plus `usage` and `main`. Uses `smb2_connect_share_async`, `smb2_open_async`, `smb2_pread_async`, `smb2_close_async`, and event-loop servicing.

Control flow: After connecting, it opens the URL path read-only, reads chunks at increasing offsets until a zero-length read, writes data to stdout, closes, disconnects, and exits when `is_finished` is set.

State and persistence behavior: Global `is_finished`, 256 KiB buffer, and offset track one transfer. SMB context/URL/handle lifetimes are cleaned at process end.

Dependencies and integration points: Used by `test_0300_cat_basic.sh`, valgrind variant, socket-error variant, and as a model for cancellation test.

Risks: Uses globals, so it supports one operation at a time. Error handling prints messages but returns `rc` initialized to 0 in several failure paths, which may reduce test sensitivity if scripts only check exit status.

Test signals: Covered by basic, valgrind, and socket-error cat shell tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/prog_cat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/prog_cat_cancel.c -->
# sources/user-network-fs/libsmb2/tests/prog_cat_cancel.c

Purpose: Variant of the async cat test that cancels an in-flight read PDU to exercise cancellation handling.

Important APIs, types, and functions: Shares the cat callback structure and adds an open/read cancellation callback path that invokes libsmb2 PDU cancellation before normal close/disconnect.

Control flow: Connects and opens the file, starts a read, cancels the selected PDU path, then services the event loop until callbacks close/disconnect or mark completion.

State and persistence behavior: Uses global completion flag, buffer, offset, and transient SMB handle/PDU state. No persistence.

Dependencies and integration points: Integrated with `test_0310_cancel_pdu.sh` and sync/async cancellation behavior in libsmb2.

Risks: Cancellation races are sensitive to server speed and event-loop timing. As with `prog_cat`, weak exit status propagation can hide some error paths.

Test signals: Directly exercised by the cancel PDU shell test.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/prog_cat_cancel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/prog_ls.c -->
# sources/user-network-fs/libsmb2/tests/prog_ls.c

Purpose: Directory listing integration test program with optional malloc/calloc failure injection.

Important APIs, types, and functions: Defines interposed `malloc` and `calloc` that fail when `MALLOC_FAIL` or `CALLOC_FAIL` matches the call count, then `usage` and `main` using synchronous libsmb2 connect/opendir/readdir/closedir/disconnect.

Control flow: Parses URL, connects with signing enabled, opens the directory, iterates entries and prints metadata, then cleans up. Allocation wrappers allow shell tests to sweep failure points.

State and persistence behavior: Process-local allocation counters and failure indices are static/global. SMB directory state is owned by libsmb2 and freed by closedir/context destruction.

Dependencies and integration points: Used by basic ls, valgrind, socket-error, and malloc-error shell tests.

Risks: Overriding libc allocation functions is fragile and can fail allocations in unrelated library startup code. The test relies on a live SMB share and specific nonexistent directory behavior.

Test signals: Strong coverage from four ls shell tests including valgrind, LD_PRELOAD socket errors, and ltrace-derived allocation counts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/prog_ls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/prog_mkdir.c -->
# sources/user-network-fs/libsmb2/tests/prog_mkdir.c

Purpose: Small synchronous helper that creates one SMB directory for integration tests.

Important APIs, types, and functions: Defines `usage` and `main`, using URL parse, context init, signing, `smb2_connect_share`, `smb2_mkdir`, disconnect, URL/context cleanup.

Control flow: The command connects to the share identified by the URL, calls mkdir on the URL path, and exits nonzero on setup or operation failure.

State and persistence behavior: No persistent local state; remote directory creation is the intended persistent side effect until paired with rmdir.

Dependencies and integration points: Used by mkdir tests and setup/cleanup in ls tests.

Risks: Requires a writable SMB share. If cleanup tests fail later, remote test directories can remain.

Test signals: Covered by `test_0200_mkdir.sh`, `test_0201_mkdir_valgrind.sh`, and ls setup flows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/prog_mkdir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/prog_rmdir.c -->
# sources/user-network-fs/libsmb2/tests/prog_rmdir.c

Purpose: Small synchronous helper that removes one SMB directory for integration tests.

Important APIs, types, and functions: Defines `usage` and `main`, using URL parse, context init, signing, `smb2_connect_share`, `smb2_rmdir`, disconnect, and cleanup.

Control flow: Connects to the share, removes the URL path, then returns status for shell scripts.

State and persistence behavior: No local persistence; remote directory removal is the persistent side effect.

Dependencies and integration points: Used by mkdir tests and ls tests for setup/cleanup.

Risks: Requires permissions and an empty target directory. Cleanup calls in scripts sometimes ignore failure, so stale test state can affect later tests.

Test signals: Covered by mkdir and ls shell tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/prog_rmdir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/smb2-dcerpc-coder-test.c -->
# sources/user-network-fs/libsmb2/tests/smb2-dcerpc-coder-test.c

Purpose: Offline coder regression test for libsmb2 DCE/RPC NDR encoding and decoding.

Important APIs, types, and functions: Defines `test_dcerpc_coder`, comparison helpers for UTF-16 and SRVSVC share structures, concrete tests for NDR32 little/big endian and NDR64 little endian, and `main` creating SMB2/DCE contexts.

Control flow: Each test encodes a request structure to a fixed buffer, checks offset and byte-for-byte expected output, normalizes fake unique pointer markers, decodes into a fresh structure, and compares semantic fields.

State and persistence behavior: Uses stack fixtures and allocated decode buffers. DCE/RPC context is transient and no network calls are made.

Dependencies and integration points: Depends on libsmb2 DCE/RPC, LSA, SRVSVC headers and coder internals `ndr_set_tctx`/`ndr_set_endian`. Integrated by `test_900_dcerpc.sh`.

Risks: Large embedded byte arrays are brittle but valuable; any legitimate encoding change needs fixture updates. Coverage is focused on selected structures, not all DCE/RPC coders.

Test signals: Directly run by `test_900_dcerpc.sh` and gives strong byte-level regression signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/smb2-dcerpc-coder-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0100_ls_basic.sh -->
# sources/user-network-fs/libsmb2/tests/test_0100_ls_basic.sh

Purpose: Basic shell integration test for directory listing success and failure cases.

Important APIs, types, and functions: Sources `functions.sh`; invokes `prog_ls`, `prog_mkdir`, and `prog_rmdir` against `${TESTURL}`.

Control flow: Lists the share root, ensures listing a nonexistent directory fails, creates `testdir`, verifies listing succeeds, then removes it.

State and persistence behavior: Persists a remote `testdir` briefly. No local persistent state.

Dependencies and integration points: Depends on `TESTURL`, helper binaries, and SMB server permissions.

Risks: Cleanup is best-effort; if the script aborts before rmdir, remote state can remain. Assumes `${TESTURL}/testdir` is safe to create/delete.

Test signals: Direct pass/fail shell test.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0100_ls_basic.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0101_ls_basic_valgrind.sh -->
# sources/user-network-fs/libsmb2/tests/test_0101_ls_basic_valgrind.sh

Purpose: Valgrind variant of the basic ls integration test.

Important APIs, types, and functions: Runs `prog_ls` under `libtool --mode=execute valgrind --leak-check=full --error-exitcode=77` for root, nonexistent, and existing directory cases.

Control flow: Same logical flow as the basic ls test, but wraps listing commands in valgrind and treats expected nonexistent-directory failure specially.

State and persistence behavior: Creates/removes remote `testdir`; valgrind output is redirected away except on selected paths.

Dependencies and integration points: Depends on valgrind, libtool wrapper, test helpers, and SMB server.

Risks: Valgrind availability and platform support affect test portability. Redirected logs can hide diagnostic detail on CI failure.

Test signals: Memory-leak/error signal through valgrind exit code 77.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0101_ls_basic_valgrind.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0102_ls_basic_socket_error.sh -->
# sources/user-network-fs/libsmb2/tests/test_0102_ls_basic_socket_error.sh

Purpose: Fault-injection ls test that closes the SMB socket at successive `readv` calls.

Important APIs, types, and functions: Uses `ld_sockerr.so` through `LD_PRELOAD` and loops `READV_CLOSE` from 1 to `NUM_CALLS` while running `prog_ls` under valgrind.

Control flow: For each injected failure point, the helper interposes `readv`; the script accepts process completion without invoking `failure`, aiming to expose crashes/leaks under broken sessions.

State and persistence behavior: No persistent local state. Remote state is only listing operations.

Dependencies and integration points: Depends on `ld_sockerr.so`, valgrind, ltrace-derived `NUM_CALLS`, and SMB server behavior.

Risks: If `NUM_CALLS` is inaccurate, parts of the read path are not exercised. The script may not assert that failures occurred, only that the program tolerated them.

Test signals: Socket-error resilience signal across multiple read points.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0102_ls_basic_socket_error.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0103_ls_basic_valgrind_malloc_error.sh -->
# sources/user-network-fs/libsmb2/tests/test_0103_ls_basic_valgrind_malloc_error.sh

Purpose: Malloc/calloc failure-injection test for `prog_ls`.

Important APIs, types, and functions: Uses ltrace to count allocation calls, then loops `MALLOC_FAIL` and `CALLOC_FAIL` indices under valgrind with error exit code 77.

Control flow: It runs `prog_ls` repeatedly while the program's interposed allocation wrappers fail one allocation site at a time.

State and persistence behavior: No remote mutation beyond listing. Process-local environment controls injected allocation failures.

Dependencies and integration points: Depends on ltrace, valgrind, libtool, and the allocation interposition in `prog_ls.c`.

Risks: Ltrace output format and allocator behavior vary by platform. It accepts many command failures, so it mainly catches crashes/leaks rather than semantic success.

Test signals: Memory-failure robustness signal for directory listing path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0103_ls_basic_valgrind_malloc_error.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0200_mkdir.sh -->
# sources/user-network-fs/libsmb2/tests/test_0200_mkdir.sh

Purpose: Basic create/remove directory integration test.

Important APIs, types, and functions: Calls `prog_mkdir` and `prog_rmdir` for `${TESTURL}/testdir` with shared `failure` handling.

Control flow: Creates a remote directory, then removes it.

State and persistence behavior: Remote `testdir` exists between the two operations.

Dependencies and integration points: Depends on writable SMB share and helper programs.

Risks: Can leave remote state if rmdir is not reached. Assumes fixed name does not collide with user data.

Test signals: Direct pass/fail mkdir/rmdir signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0200_mkdir.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0201_mkdir_valgrind.sh -->
# sources/user-network-fs/libsmb2/tests/test_0201_mkdir_valgrind.sh

Purpose: Valgrind variant of mkdir/rmdir integration test.

Important APIs, types, and functions: Runs `prog_mkdir` and `prog_rmdir` under libtool/valgrind with leak checking and error exit code 1.

Control flow: Creates and removes `${TESTURL}/testdir`, treating valgrind findings as failures.

State and persistence behavior: Remote directory side effect is temporary.

Dependencies and integration points: Depends on valgrind/libtool, writable SMB share, and helper programs.

Risks: Valgrind can be slow and environment-sensitive. Fixed remote name can collide.

Test signals: Memory-safety signal for mkdir/rmdir sync paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0201_mkdir_valgrind.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0210_cp_basic.sh -->
# sources/user-network-fs/libsmb2/tests/test_0210_cp_basic.sh

Purpose: Basic copy integration test covering local-to-SMB and SMB-to-local directions.

Important APIs, types, and functions: Uses `../utils/smb2-cp`, `cmp`, local files `testfile`/`testfile2`, and `${TESTURL}/testfile`.

Control flow: Creates a local file, copies it to the share, copies it back, compares contents, then verifies copying a nonexistent SMB file fails.

State and persistence behavior: Persists local temporary files and a remote test file unless cleaned externally; script removes `testfile2` at start only.

Dependencies and integration points: Depends on `smb2-cp`, writable SMB share, and standard `cmp`.

Risks: Remote `testfile` may be overwritten and is not removed here. Fixed names can collide with existing data.

Test signals: Direct copy correctness and negative-path signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0210_cp_basic.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0211_cp_valgrind.sh -->
# sources/user-network-fs/libsmb2/tests/test_0211_cp_valgrind.sh

Purpose: Valgrind version of the copy integration test.

Important APIs, types, and functions: Wraps `../utils/smb2-cp` with libtool/valgrind for upload, download, and nonexistent source checks.

Control flow: Same flow as basic copy, with leak/error detection and a final `cmp`.

State and persistence behavior: Creates local temporary files and a remote test file.

Dependencies and integration points: Depends on valgrind, libtool, `smb2-cp`, and SMB write permissions.

Risks: Valgrind output for the expected failure is redirected to `valgrind.out`; remote file cleanup is absent.

Test signals: Memory-safety and copy correctness signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0211_cp_valgrind.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0212_cp_valgrind_socket_error.sh -->
# sources/user-network-fs/libsmb2/tests/test_0212_cp_valgrind_socket_error.sh

Purpose: Socket-error fault-injection test for SMB copy upload and download paths.

Important APIs, types, and functions: Uses `LD_PRELOAD=./ld_sockerr.so`, `READV_CLOSE` loop, valgrind, and `../utils/smb2-cp`.

Control flow: Creates a local file, repeatedly copies to SMB with injected read failures, then repeatedly copies from SMB to local with injected failures.

State and persistence behavior: Local `testfile`/`testfile2` and remote `testfile` are touched. Injection state is per process environment.

Dependencies and integration points: Depends on ld_sockerr, valgrind/libtool, SMB server, and `NUM_CALLS` breadth.

Risks: The script does not verify every injected copy fails or succeeds in a specific way; it mainly catches crashes/leaks. Remote file must exist for download phase.

Test signals: Fault-tolerance signal for copy paths under socket failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0212_cp_valgrind_socket_error.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0300_cat_basic.sh -->
# sources/user-network-fs/libsmb2/tests/test_0300_cat_basic.sh

Purpose: Basic file-read integration test for async cat helper.

Important APIs, types, and functions: Runs `./prog_cat "${TESTURL}/CAT"` and uses shared `failure`.

Control flow: Reads a known remote file named `CAT` and discards output.

State and persistence behavior: No local persistence. Remote file must preexist.

Dependencies and integration points: Depends on SMB share fixture containing `CAT`.

Risks: Fixture-dependent and does not compare content, only successful read completion.

Test signals: Direct async read/cat pass/fail signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0300_cat_basic.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0301_cat_valgrind.sh -->
# sources/user-network-fs/libsmb2/tests/test_0301_cat_valgrind.sh

Purpose: Valgrind variant of the cat integration test.

Important APIs, types, and functions: Runs `prog_cat` under libtool/valgrind with leak checking and error exit code 1.

Control flow: Reads `${TESTURL}/CAT` and discards output.

State and persistence behavior: No persistent state.

Dependencies and integration points: Depends on valgrind/libtool and remote `CAT` fixture.

Risks: No content assertion; only success and memory-safety are checked.

Test signals: Memory-safety signal for async open/read/close/disconnect path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0301_cat_valgrind.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0302_cat_valgrind_socket_error.sh -->
# sources/user-network-fs/libsmb2/tests/test_0302_cat_valgrind_socket_error.sh

Purpose: Socket-error fault-injection test for async cat.

Important APIs, types, and functions: Loops `READV_CLOSE` values under `LD_PRELOAD=./ld_sockerr.so` and valgrind while running `prog_cat`.

Control flow: Each iteration injects a readv failure at a different call index during read of `${TESTURL}/CAT`.

State and persistence behavior: No persistent state beyond per-process injection variables.

Dependencies and integration points: Depends on ld_sockerr, valgrind/libtool, and remote `CAT` fixture.

Risks: May miss paths if `NUM_CALLS` is too low/high. It checks tolerance to failures more than semantic error codes.

Test signals: Crash/leak resilience signal for async read under socket failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0302_cat_valgrind_socket_error.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0310_cancel_pdu.sh -->
# sources/user-network-fs/libsmb2/tests/test_0310_cancel_pdu.sh

Purpose: Integration test for cancelling an in-flight SMB2 PDU.

Important APIs, types, and functions: Runs `./prog_cat_cancel "${TESTURL}/CAT"`.

Control flow: Starts the cancellation-capable cat helper and expects it to complete without failure.

State and persistence behavior: No persistent local or remote state.

Dependencies and integration points: Depends on `prog_cat_cancel` and remote `CAT` fixture.

Risks: Timing-sensitive because the PDU must still be in flight for meaningful cancellation coverage.

Test signals: Direct cancellation path signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0310_cancel_pdu.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0400_overdrawn_0202.sh -->
# sources/user-network-fs/libsmb2/tests/test_0400_overdrawn_0202.sh

Purpose: Stress test for SMB 2.0.2 credit handling by issuing many parallel stat operations.

Important APIs, types, and functions: Uses `../utils/smb2-ls` to discover a filename and runs `metastat-0202-censored` concurrently in loops.

Control flow: Discovers a file in the share, starts multiple background metastat processes with repeated filename arguments, waits for all PIDs, and fails if any process exits nonzero.

State and persistence behavior: No intended persistent state. Uses shell arrays of background PIDs.

Dependencies and integration points: Depends on live SMB 2.0.2-capable server behavior, `smb2-ls`, and metastat helper.

Risks: Discovery parses the first token from `smb2-ls`, which can be brittle. High concurrency can be environment-sensitive.

Test signals: Concurrent stat success is the direct stress signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0400_overdrawn_0202.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_900_dcerpc.sh -->
# sources/user-network-fs/libsmb2/tests/test_900_dcerpc.sh

Purpose: Runs the offline DCE/RPC coder regression test.

Important APIs, types, and functions: Invokes `./smb2-dcerpc-coder-test || failure`.

Control flow: Linear shell wrapper around the compiled coder test.

State and persistence behavior: No persistent state.

Dependencies and integration points: Depends on the coder test binary and shared failure helper.

Risks: Only covers fixtures embedded in the C test; does not exercise network DCE/RPC.

Test signals: Direct byte-level DCE/RPC codec regression signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_900_dcerpc.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/utils/Makefile.am -->
# sources/user-network-fs/libsmb2/utils/Makefile.am

Purpose: Automake rules for installing libsmb2 command-line utilities.

Important APIs, types, and functions: Sets include paths, warning flags, `bin_PROGRAMS = smb2-ls smb2-cp`, per-program sources, and links both tools with `../lib/libsmb2.la`.

Control flow: Automake compiles the utility sources and links them against the in-tree libsmb2 library.

State and persistence behavior: No runtime state; build outputs are binaries in the build/install tree.

Dependencies and integration points: Integrates utils with the library and tests that call `../utils/smb2-cp` and `../utils/smb2-ls`.

Risks: Only two utilities are listed, so new tools must be added explicitly. Include path layout must match source tree headers.

Test signals: Build success and shell tests provide signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/utils/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/utils/smb2-cp.c -->
# sources/user-network-fs/libsmb2/utils/smb2-cp.c

Purpose: Command-line copy utility that copies between local files and SMB URLs in either direction.

Important APIs, types, and functions: Defines `struct file_context`, `usage`, `free_file_context`, `fstat_file`, `file_pread`, `file_pwrite`, `open_file`, global 1 MiB buffer, and `main`.

Control flow: Each operand is opened as local or SMB based on `smb://` prefix. The source is statted, then a loop reads chunks with pread semantics and writes them to the destination until source size is copied.

State and persistence behavior: Maintains per-file context with local fd, SMB context, URL, and SMB file handle. Remote destination is created/truncated when opened for write.

Dependencies and integration points: Depends on synchronous libsmb2 APIs, POSIX file APIs, URL parser, and platform socket init for Windows/AROS. Used by cp tests.

Risks: Local `read`/`write` calls do not handle short writes robustly beyond advancing by written count from read result. `st_blocks` calculation for SMB metadata uses modulo instead of division, likely wrong but not copy-critical. Remote overwrite is unconditional for destination.

Test signals: Covered by basic, valgrind, and socket-error copy tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/utils/smb2-cp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/utils/smb2-ls.c -->
# sources/user-network-fs/libsmb2/utils/smb2-ls.c

Purpose: Command-line SMB directory listing utility using synchronous libsmb2 APIs.

Important APIs, types, and functions: Defines `usage` and `main`; uses URL parsing, `smb2_connect_share`, `smb2_opendir`, `smb2_readdir`, `smb2_readlink`, and cleanup calls.

Control flow: Connects to the share, opens the URL path as a directory, prints each entry name/type/size/mtime, resolves link targets, then closes/disconnects.

State and persistence behavior: Transient context, URL, directory handle, and temporary link strings. No persistence.

Dependencies and integration points: Depends on libsmb2 sync API and is used by tests, including filename discovery for the credit stress test.

Risks: Output format is human-oriented and scripts parse it with simple tools, making changes risky. Link target buffer is fixed at 256 bytes.

Test signals: Exercised by tests indirectly and useful as a manual integration tool.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/utils/smb2-ls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/Makefile.am -->
# sources/user-network-fs/libtirpc/Makefile.am

Purpose: Top-level Automake file for libtirpc source, headers, pkg-config metadata, and subdirectories.

Important APIs, types, and functions: Defines `SUBDIRS = src man doc`, `ACLOCAL_AMFLAGS`, private `noinst_HEADERS`, installed `nobase_include_HEADERS`, conditional GSS headers, `pkgconfig_DATA`, and clean/distclean files.

Control flow: Automake recurses into subdirectories, installs public tirpc headers preserving paths, and installs `libtirpc.pc`.

State and persistence behavior: No runtime state; controls installed headers and generated build artifacts.

Dependencies and integration points: Driven by `configure.ac` conditionals, especially `GSS`. Integrates source, man, doc, and pkg-config outputs.

Risks: Header lists can drift from source. Conditional GSS headers must match library symbols and configure checks.

Test signals: Build/install success is the main signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/autogen.sh -->
# sources/user-network-fs/libtirpc/autogen.sh

Purpose: Bootstrap script for regenerating libtirpc Autotools files from a clean source checkout.

Important APIs, types, and functions: Removes generated files/directories, supports `clean` mode, then runs `aclocal`, `libtoolize --force --copy`, `autoheader`, `automake --add-missing --copy --gnu`, and `autoconf`.

Control flow: First deletes known generated files plus all `Makefile.in` and `Makefile`, then exits if requested or recreates the build system.

State and persistence behavior: Mutates the source tree by removing and regenerating build files.

Dependencies and integration points: Depends on Autotools/libtool. Used by developers and packaging workflows.

Risks: Deletes all `Makefile` files under the tree, which is expected for bootstrap but destructive if local generated build state matters. `set -e` stops on first tool failure.

Test signals: Successful bootstrap and subsequent configure/build are the signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/autogen.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/configure.ac -->
# sources/user-network-fs/libtirpc/configure.ac

Purpose: Autoconf configuration script for libtirpc feature detection, conditionals, symbol lists, and generated files.

Important APIs, types, and functions: Defines package version 1.3.7, compiler/libtool setup, `LT_VERSION_INFO`, GSSAPI detection, `--enable/disable` flags for gssapi/authdes/ipv6/rpcdb/symvers, symbol substitutions, OS-specific linker flags, header/function/type checks, and output files.

Control flow: Configure evaluates requested features, errors when mandatory GSS dependencies are missing, tests version-script support, populates conditional symbol lists, probes networking constants, and emits Makefiles, version map, config header, and pkg-config file.

State and persistence behavior: Persists results in generated `config.h`, Makefiles, `src/libtirpc.map`, and `libtirpc.pc`.

Dependencies and integration points: Integrates all Automake files and optional source inclusion in `src/Makefile.am`. Depends on krb5-config for GSS and compiler/linker feature probes.

Risks: Defaults enable GSS and IPv6, so minimal systems must pass disable flags. Symbol lists must stay synchronized with implemented APIs. Some feature checks use build OS rather than host, which can matter for cross-compilation.

Test signals: Configure-time checks and successful builds with feature combinations are signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/configure.ac -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/doc/Makefile.am -->
# sources/user-network-fs/libtirpc/doc/Makefile.am

Purpose: Automake rules for installing libtirpc documentation files.

Important APIs, types, and functions: Lists `new_api` and conditionally `bindresvport.blacklist` when IPv6 is disabled, plus `EXTRA_DIST`.

Control flow: Automake includes docs in distributions and installs configured doc data.

State and persistence behavior: No runtime state.

Dependencies and integration points: Depends on `INET6` conditional from configure.

Risks: Conditional documentation install can surprise packagers expecting a stable doc file set.

Test signals: Build/distcheck signals only.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/doc/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/libtirpc.pc.in -->
# sources/user-network-fs/libtirpc/libtirpc.pc.in

Purpose: Pkg-config template for libtirpc consumers.

Important APIs, types, and functions: Defines install paths, name/description/version, `Libs: -L${libdir} -ltirpc`, `Libs.private: @PTHREAD_LIBS@`, and `Cflags: -I${includedir}/tirpc`.

Control flow: Configure substitutes package version and pthread flags; install places the `.pc` file.

State and persistence behavior: No runtime state; installed metadata persists for downstream builds.

Dependencies and integration points: Integrated with top-level Automake pkgconfig install and downstream pkg-config users.

Risks: `Requires` is empty and only pthread appears private; optional GSS/private dependencies may need careful static-link handling depending on build configuration.

Test signals: Validated by downstream configure/pkg-config usage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/libtirpc.pc.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/man/Makefile.am -->
# sources/user-network-fs/libtirpc/man/Makefile.am

Purpose: Automake rules for libtirpc manual page installation and distribution.

Important APIs, types, and functions: Defines `dist_man_MANS`, conditional GSS man pages, and extra distributed man pages.

Control flow: Automake installs base man pages and adds GSS-specific pages when configured.

State and persistence behavior: No runtime state.

Dependencies and integration points: Depends on `GSS` conditional from configure and manpage source files.

Risks: Manual page list can drift from installed APIs; conditional docs must match optional features.

Test signals: Dist/install checks provide signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/man/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/Makefile.am -->
# sources/user-network-fs/libtirpc/src/Makefile.am

Purpose: Automake rules for building the libtirpc shared library and optional source sets.

Important APIs, types, and functions: Defines include flags, `lib_LTLIBRARIES = libtirpc.la`, LDFLAGS/versioning, version-map generation, base source list, conditional AUTH_DES, XDR, SYMVERS, GSS, RPCDB, and key/netname sources.

Control flow: Build generates `libtirpc.map`, compiles base RPC/auth/client/server/XDR sources, appends optional groups based on configure conditionals, and links with GSS libs when enabled.

State and persistence behavior: No runtime persistence; build artifacts include library, map, and objects.

Dependencies and integration points: Driven by configure conditionals. Integrates all authentication files in this subset into the library.

Risks: Conditional source inclusion must match public headers and symbol map. `libtirpc_la_CFLAGS` assignment under GSS can override rather than append other flags if not managed carefully.

Test signals: Successful builds across optional feature combinations are the primary signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/auth_des.c -->
# sources/user-network-fs/libtirpc/src/auth_des.c

Purpose: Client-side AUTH_DES implementation for Secure RPC using DES-encrypted timestamp credentials.

Important APIs, types, and functions: Exports `authdes_seccreate` and `authdes_pk_seccreate`; implements auth ops `authdes_marshal`, `authdes_validate`, `authdes_refresh`, `authdes_destroy`, wrapping passthrough, and static op-vector initialization. Private state lives in `struct ad_private`.

Control flow: Creation resolves or accepts the server public key, gets the client netname, allocates private fields, creates or accepts a conversation key, sets AUTH_DES ops, then refreshes credentials. Marshal timestamps, applies time offset, encrypts timestamp/window, writes credential/verifier XDR. Validate decrypts server verifier and switches to nickname credentials. Refresh optionally syncs time and encrypts the session key with the server public key.

State and persistence behavior: Persistent per-AUTH state includes names, server key, conversation key, nickname, credential/verifier structs, time sync cache, and optional timehost endpoint strings. Destroy frees allocated private fields and AUTH.

Dependencies and integration points: Depends on keyserv/publickey APIs, DES crypt functions, XDR authdes coders, `__rpc_get_time_offset`, syslog/debug, and libtirpc auth ops locks. Built only when AUTH_DES is enabled.

Risks: AUTH_DES is legacy cryptography. Public key copy into fixed 1024-byte buffer lacks explicit length cap. Time synchronization and nickname state are subtle and can fail open by disabling sync. Error paths must avoid leaks across many allocated fields.

Test signals: No direct unit test in this subset; compile coverage when AUTH_DES is enabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/auth_des.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/auth_gss.c -->
# sources/user-network-fs/libtirpc/src/auth_gss.c

Purpose: Client-side RPCSEC_GSS authentication implementation for libtirpc.

Important APIs, types, and functions: Exports `authgss_create`, `authgss_create_default`, private-data get/free, `authgss_service`, `rpc_gss_seccreate`, `rpc_gss_set_defaults`, `rpc_gss_max_data_length`, and `is_authgss_client`. Implements auth ops for marshal, validate, refresh/context negotiation, destroy, wrap, and unwrap over `struct rpc_gss_data`.

Control flow: Creation imports/duplicates service names, sets RPCSEC_GSS init credentials, temporarily installs the AUTH on the CLIENT, and runs refresh. Refresh loops over `gss_init_sec_context` and NULLPROC exchanges until established, validating the final verifier. Marshal encodes credentials and MICs the RPC header for data calls. Validate verifies response MICs. Wrap/unwrap delegate to `xdr_rpc_gss_data` for integrity/privacy.

State and persistence behavior: Per-AUTH state includes GSS context, context handle buffer, service/qop/credential tuple, sequence number/window, saved wire verifier, channel bindings, client pointer, and refcount protected by a mutex. Destroy sends RPCSEC_GSS_DESTROY when established, releases GSS buffers/names/context, and frees state when refcount reaches zero.

Dependencies and integration points: Depends on GSSAPI, RPC client calls, rpc_gss utility mapping/error functions, authgss XDR protocol helpers, and libtirpc debug/ref locks. Included when GSS is enabled.

Risks: Context negotiation modifies `clnt->cl_auth` temporarily and must restore it. Failure paths inside `_rpc_gss_refresh` can destroy `auth` while callers still hold local variables. Sequence/QOP verification is security-critical. Saved verifier allocation must be freed on all context-destroy paths.

Test signals: No direct test here; configure/build with GSS and downstream RPCSEC_GSS clients are signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/auth_gss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/auth_none.c -->
# sources/user-network-fs/libtirpc/src/auth_none.c

Purpose: Implements singleton AUTH_NONE credentials for unauthenticated RPC calls.

Important APIs, types, and functions: Exports `authnone_create`; implements marshal, no-op verifier, validate, refresh, destroy, wrap/unwrap, and static op-vector setup.

Control flow: First call allocates singleton private storage, initializes null credential/verifier, pre-marshals both opaque auth records into a fixed buffer, and returns the singleton AUTH. Marshal copies the cached bytes into the target XDR stream.

State and persistence behavior: Global singleton `authnone_private` persists for process lifetime; destroy is intentionally no-op. Mutexes protect initialization and cached marshal access.

Dependencies and integration points: Depends on XDR opaque auth, `_null_auth`, and libtirpc mutex globals.

Risks: Singleton lifetime means memory is intentionally never freed, which is normal but can appear as a leak. `authnone_refresh` always false, so callers must handle auth refresh failure correctly.

Test signals: Indirectly exercised by RPC clients using default/no auth; no direct test in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/auth_none.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/auth_time.c -->
# sources/user-network-fs/libtirpc/src/auth_time.c

Purpose: Private helper for AUTH_DES clock synchronization against rpcbind or inet time service.

Important APIs, types, and functions: Implements `__rpc_get_time_offset` plus helpers `alarm_hndler`, `uaddr_to_sockaddr`, `free_eps`, and `get_server`.

Control flow: If no cached universal address exists, it constructs/selects TCP or UDP endpoints. It converts universal addresses to IPv4 socket addresses, tries RPCBPROC_GETTIME over rpcbind, falls back to port 37 time service over UDP/TCP with timeout/alarm handling, then computes server-minus-client seconds and caches the universal address.

State and persistence behavior: Returns time delta in caller-provided `timeval`; may allocate and cache `*uaddr`. Temporarily changes SIGALRM handler and opens sockets/client handles.

Dependencies and integration points: Used by `auth_des.c` refresh. Depends on RPC client APIs, rpcbind protocol, sockets, NIS endpoint structures, and IPv4 universal address formatting.

Risks: IPv4-only parsing and string formatting limit transport support. The function changes process SIGALRM handling, which is risky in threaded programs. There is a likely rounding bug using `tv.tv_sec > 500000` instead of microseconds. Network time service fallback is legacy.

Test signals: No direct test; only AUTH_DES time sync users exercise it.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/auth_time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/auth_unix.c -->
# sources/user-network-fs/libtirpc/src/auth_unix.c

Purpose: Implements AUTH_UNIX/AUTH_SYS style RPC client credentials.

Important APIs, types, and functions: Exports `authunix_create` and `authunix_create_default`; implements auth ops, shorthand credential validation, refresh, destroy, and `marshal_new_auth` cache generation.

Control flow: Creation serializes machine name, uid, gid, groups, and current time into an opaque AUTH_UNIX credential, stores original credential, then pre-marshals credential/verifier. Default creation queries hostname/euid/egid/groups with retry for group-list growth. Validate accepts AUTH_SHORT verifiers and switches to shorthand credentials. Refresh falls back from shorthand to original credentials and updates timestamp.

State and persistence behavior: Per-AUTH private `audata` stores original credential, shorthand credential, fault count, and pre-marshaled bytes. Destroy frees credential buffers and AUTH.

Dependencies and integration points: Depends on POSIX identity/group calls, XDR authunix parms, `_null_auth`, and auth ops locks. Core source in libtirpc build.

Risks: AUTH_UNIX is unauthenticated and easily spoofed. Group list truncates to `NGRPS`. Cached marshaling must be refreshed whenever credentials change. Warning text in `marshal_new_auth` names `auth_none.c`, likely copy/paste.

Test signals: Indirectly exercised by normal RPC clients; no direct unit test in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/auth_unix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/authdes_prot.c -->
# sources/user-network-fs/libtirpc/src/authdes_prot.c

Purpose: XDR serialization routines for AUTH_DES credential and verifier structures.

Important APIs, types, and functions: Exports `xdr_authdes_cred` and `xdr_authdes_verf`.

Control flow: Credential encoding first serializes the name-kind enum, then switches between full-name form (name, key, window) and nickname form. Verifier encoding serializes encrypted timestamp and integer union field.

State and persistence behavior: No retained state. XDR_DECODE may allocate strings through XDR helpers according to normal XDR ownership rules.

Dependencies and integration points: Used by `auth_des.c` marshal/validate and included with AUTH_DES support.

Risks: K&R-style definitions are legacy but valid in this codebase. Correct max lengths and opaque sizes are security-relevant because credentials cross trust boundaries.

Test signals: Compile coverage with AUTH_DES; no direct codec fixture in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/authdes_prot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/authgss_prot.c -->
# sources/user-network-fs/libtirpc/src/authgss_prot.c

Purpose: XDR and GSS helper routines for RPCSEC_GSS credentials, init tokens, and protected data bodies.

Important APIs, types, and functions: Exports `xdr_rpc_gss_buf`, `xdr_rpc_gss_cred`, `xdr_rpc_gss_init_args`, `xdr_rpc_gss_init_res`, `xdr_rpc_gss_wrap_data`, `xdr_rpc_gss_unwrap_data`, `xdr_rpc_gss_data`, and debug helpers `gss_log_debug`, `gss_log_status`, `gss_log_hexdump`.

Control flow: Encode paths serialize GSS buffers and credentials, or marshal sequence+payload then compute MIC for integrity or wrap/encrypt for privacy. Decode paths read integrity/privacy bodies, verify MIC/QOP or unwrap confidentiality, decode sequence+payload from a memory XDR stream, and check sequence number.

State and persistence behavior: No persistent module state except debug globals from libtirpc. GSS buffers decoded by XDR/GSS helpers require normal release/free handling by callers.

Dependencies and integration points: Used by `auth_gss.c` for RPCSEC_GSS init and per-call wrap/unwrap. Depends on GSSAPI and XDR.

Risks: Slack-based max sizes are permissive and must not allow unbounded allocation on hostile inputs; decode uses `(u_int)-1` for some buffers. Sequence and QOP checks are security-critical. Debug hexdumps can expose sensitive token data when high debug logging is enabled.

Test signals: No direct unit test in this subset; covered by GSS-enabled builds and RPCSEC_GSS integration clients.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/authgss_prot.c -->
