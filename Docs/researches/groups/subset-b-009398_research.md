# subset-b-009398 Research

Grouped research report for syzkaller executor FlatBuffers helpers, Android seccomp policy headers, common executor platform glue, and KVM support. Each section is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/util.h -->
## sources/test-tools/syzkaller/executor/_include/flatbuffers/util.h

Purpose: This vendored FlatBuffers utility header provides locale-aware and locale-independent helpers used by parsing, text generation, filesystem access, UTF-8 handling, path manipulation, and identifier case conversion. It is a declaration-heavy header with inline numeric and string routines plus prototypes implemented elsewhere in the FlatBuffers support library.

Important APIs and types: ASCII helpers include `check_ascii_range`, `is_alpha`, `is_digit`, `is_xdigit`, `is_alnum`, `CharToUpper`, and `CharToLower`. Numeric helpers include `NumToString`, `FloatToString`, `IntToStringHex`, `StringToIntegerImpl`, `StringToFloatImpl`, `StringToNumber`, `StringToInt`, and `StringToUInt`; specializations handle `char`, `float`, `double`, `int64_t`, and `uint64_t`. File and path integration is exposed through `LoadFileFunction`, `FileExistsFunction`, `SetLoadFileFunction`, `SetFileExistsFunction`, `FileExists`, `DirExists`, `LoadFile`, `SaveFile`, `StripExtension`, `GetExtension`, `StripPath`, `StripFileName`, `StripPrefix`, `ConCatPathFileName`, `PosixPath`, `EnsureDirExists`, `AbsolutePath`, and `RelativeToRootPath`. Text helpers include `ToUTF8`, `FromUTF8`, `WordWrap`, `EscapeString`, `BufferToHexText`, `RemoveStringQuotes`, `SetGlobalTestLocale`, `ReadEnvironmentVariable`, `Case`, and `ConvertCase`.

Control flow and state: Numeric parsing funnels through `strtoval_impl`, with optional `ClassicLocale` use when `FLATBUFFERS_LOCALE_INDEPENDENT` is enabled. Integer parsing first detects explicit hex prefixes and otherwise forces decimal, preventing `strtoll(..., base=0)` from treating leading-zero strings as octal. `EscapeString` scans bytes, emits JSON escapes, validates UTF-8 through `FromUTF8`, optionally emits raw UTF-8, or returns `false` for non-UTF-8 data when not allowed. The header itself has no persistent storage except the locale singleton and globally replaceable file callback hooks declared here.

Dependencies and integration points: It depends on `flatbuffers/base.h`, `flatbuffers/stl_emulation.h`, C locale/errno functions, and either iostream formatting or `snprintf` under `FLATBUFFERS_PREFER_PRINTF`. Generated FlatBuffers code and tools use this header for JSON/text conversion and portable utility behavior.

Risks and test signals: The highest-risk areas are numeric overflow/underflow, unsigned negative parsing, locale-dependent float conversion, UTF-8 shortest-form validation, and `EscapeString` behavior for corrupted serialized strings. Good tests exercise decimal-vs-hex parsing, leading zeros, `-0` for unsigned, NaN/Inf strings, surrogate and overlong UTF-8 rejection, path separator normalization, callback replacement, and both printf and stream formatting builds.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/vector.h -->
## sources/test-tools/syzkaller/executor/_include/flatbuffers/vector.h

Purpose: This FlatBuffers runtime header defines read-only and mutable views over vector data already serialized inside a FlatBuffer. It does not own storage; it interprets a length-prefixed byte region and delegates element access through `IndirectHelper`.

Important APIs and types: `VectorIterator` and `VectorReverseIterator` provide random-access-style traversal while returning values through FlatBuffers indirection semantics. `Vector<T, SizeT>` exposes `size`, deprecated `Length`, `Get`, `operator[]`, `GetEnum`, `GetAs`, `GetAsString`, `GetStructFromOffset`, iterators, `Mutate`, `MutateOffset`, `GetMutableObject`, raw `Data`, typed `data`, `LookupByKey`, and `MutableLookupByKey`. `Vector64` aliases a 64-bit length/offset variant. `make_span` and `make_bytes_span` create `flatbuffers::span` views for observable scalar vectors. `VectorOfAny`, `VectorCast`, and `VectorLength` support reflection and nullable vectors.

Control flow and state: `Vector::size` reads `length_` through `EndianScalar`. Element access asserts bounds and calls `IndirectHelper<T>::Read(Data(), i)`, so scalar, struct, string, table, and offset vectors share one surface. Lookup uses `std::bsearch` over serialized elements and compares keys with generated `KeyCompareWithValue`. Mutation writes scalar values or relative offsets back into the backing buffer; no capacity changes are possible.

Dependencies and integration points: It depends on `flatbuffers/base.h`, `flatbuffers/buffer.h`, `flatbuffers/stl_emulation.h`, `IndirectHelper`, endian helpers, generated table key comparators, and generated accessors. It is consumed by generated FlatBuffers code and by `verifier.h` for vector validation.

Risks and test signals: The class assumes the underlying buffer is valid and aligned; safety relies on verifier use before access. Mutation risks include wrong offset arithmetic, mutating non-scalar data through `Mutate`, and exposing spans only when endian-safe. Tests should cover scalar vectors, vectors of offsets, reverse iteration, sorted-key lookup, nullable `make_span`, 64-bit vectors, and mutations followed by verification.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/vector.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/vector_downward.h -->
## sources/test-tools/syzkaller/executor/_include/flatbuffers/vector_downward.h

Purpose: This FlatBuffers builder support class implements a byte vector that grows from high addresses toward low addresses, matching FlatBuffers backward serialization. It also reserves the low-address side as a scratch area so temporary builder state can share the same allocation.

Important APIs and types: `vector_downward<SizeT>` owns or borrows an `Allocator` and exposes `reset`, `clear`, `clear_scratch`, `clear_allocator`, `clear_buffer`, `release_raw`, `release`, `ensure_space`, `make_space`, `get_custom_allocator`, `offset`, `size`, `unused_buffer_size`, `scratch_size`, `capacity`, `data`, `scratch_data`, `scratch_end`, `data_at`, `push`, `push_small`, `scratch_push_small`, `fill`, `fill_big`, `pop`, `scratch_pop`, `swap`, and `swap_allocator`.

Control flow and state: The object tracks `buf_`, `cur_`, `scratch_`, `reserved_`, `size_`, `initial_size_`, `max_size_`, `buffer_minalign_`, and allocator ownership. Writes to the serialized buffer call `make_space`, which ensures capacity, decrements `cur_`, and increments `size_`. Scratch writes grow upward from `buf_`. If unused space cannot satisfy a request, `reallocate` grows by max(request, half old capacity or initial size), rounds to minimum alignment, and calls `ReallocateDownward` to preserve both downward data and scratch contents.

Dependencies and integration points: It depends on `flatbuffers/base.h`, `default_allocator.h`, `detached_buffer.h`, allocator helpers, and `FLATBUFFERS_MAX_BUFFER_SIZE`. It is used by FlatBuffer builders to assemble final buffers and hand them off as `DetachedBuffer`.

Risks and test signals: Critical invariants are `buf_ <= scratch_ <= cur_ <= buf_ + reserved_`, maximum-size enforcement, ownership transfer in `release`, and preserving scratch/data during reallocation. Tests should cover empty release, move construction/assignment, custom allocator ownership, large growth, scratch collision, alignment rounding, and `pop`/`scratch_pop` balance.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/vector_downward.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/verifier.h -->
## sources/test-tools/syzkaller/executor/_include/flatbuffers/verifier.h

Purpose: This FlatBuffers runtime header verifies that an untrusted FlatBuffer is within bounds, aligned, structurally sane, and not too deeply nested before generated accessors interpret it.

Important APIs and types: `Verifier::Options` configures `max_depth`, `max_tables`, `check_alignment`, `check_nested_flatbuffers`, `max_size`, and debug assertion behavior. `Verifier` exposes `Check`, range `Verify`, `VerifyAlignment`, typed `Verify<T>`, `VerifyFromPointer`, `VerifyFieldStruct`, `VerifyField`, `VerifyTable`, vector overloads of `VerifyVector`, `VerifyString`, `VerifyVectorOrString`, `VerifyVectorOfStrings`, `VerifyVectorOfTables`, `VerifyTableStart`, `VerifyBufferFromStart`, `VerifyNestedFlatBuffer`, `VerifyBuffer`, `VerifySizePrefixedBuffer`, `VerifyOffset`, `VerifyComplexity`, `EndTable`, `GetComputedSize`, and FlexBuffers reuse tracker accessors.

Control flow and state: Verification is fail-fast through `Check`. Range validation uses `elem_len < size_ && elem <= size_ - elem_len` to avoid overflow while ensuring in-buffer access. Table verification checks the signed vtable offset, validates vtable size and alignment, increments complexity counters, and relies on generated `T::Verify` to walk fields. Nested buffers instantiate a child verifier with the same options. Optional tracking records an upper bound for computed size.

Dependencies and integration points: It depends on FlatBuffers scalar, offset, vector, identifier, and generated table verification APIs. Generated code calls it for root buffers, tables, vectors, strings, unions, and nested buffers.

Risks and test signals: Risks concentrate around integer overflow in vector byte-size calculations, signed-to-unsigned offset checks, recursion accounting, null pointer handling, and string terminator validation. Tests should cover malformed offsets, self-referential offsets, truncated strings, invalid vtables, nested buffer opt-out, 64-bit offsets, alignment disabled/enabled, and maximum table/depth limits.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/verifier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/android/android_seccomp.h -->
## sources/test-tools/syzkaller/executor/android/android_seccomp.h

Purpose: This header assembles generated Android seccomp BPF policy arrays into an installable executor filter. It selects architecture-specific app and system policies and prepends syzkaller-specific architecture validation.

Important APIs and types: Compile-time `GOARCH_*` selects `PRIMARY_ARCH`, `primary_app_filter`, `primary_app_filter_size`, `system_filter`, `system_filter_size`, and `kFilterMaxSize`. `Filter` stores a bounded `sock_filter` array plus count. Helpers are `push_back`, `Disallow`, `ExamineSyscall`, `ValidateArchitecture`, `install_filter`, `set_seccomp_filter`, and `set_app_seccomp_filter`. Account modes are `SCFS_RestrictedApp` and `SCFS_SystemAccount`.

Control flow and state: `set_app_seccomp_filter` chooses the system account policy for `SCFS_SystemAccount`, otherwise the app policy. `set_seccomp_filter` initializes an empty `Filter`, emits BPF to validate `seccomp_data.arch`, loads the syscall number, appends the selected generated policy, appends a final trap rule, and calls `prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, ...)`. The only persistent state is the installed kernel seccomp filter; after installation it constrains the current process and descendants.

Dependencies and integration points: It depends on Linux seccomp, BPF, audit architecture constants, `prctl`, `failmsg`, and the generated Android policy headers. It is used by Android sandbox setup in the syzkaller executor/csource path.

Risks and test signals: Policy staleness is explicit because headers are generated by Android’s `genseccomp.py` and must be refreshed periodically. Size accounting must match worst-case appended instructions, and `PR_SET_NO_NEW_PRIVS` or `CAP_SYS_ADMIN` must be present. Tests should compile each architecture, verify `kFilterMaxSize` is sufficient, install app/system filters in an Android-capable environment, and check denied syscalls trap rather than silently allow.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/android/android_seccomp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/android/arm64_app_policy.h -->
## sources/test-tools/syzkaller/executor/android/arm64_app_policy.h

Purpose: This generated Android BPF policy defines the allowed syscall set for restricted app accounts on AArch64. It is included by `android_seccomp.h` when `GOARCH_arm64` is selected.

Important APIs and types: It exports `const struct sock_filter arm64_app_filter[]` and `arm64_app_filter_size`. The array is a decision tree of `BPF_JUMP` range/equality checks over syscall numbers followed by `BPF_STMT(BPF_RET|BPF_K, SECCOMP_RET_ALLOW)` for allowed paths; the wrapper appends a trap fallback.

Control flow and state: The filter assumes the syscall number is already loaded into the BPF accumulator by `ExamineSyscall`. The generated tree uses `BPF_JGE` ranges and occasional `BPF_JEQ` fast paths for important syscalls such as futex and ioctl. Comments document contiguous allowed syscall names for each range. The header has no mutable state.

Dependencies and integration points: It depends on Linux classic BPF macros and Android’s generated syscall policy source. `android_seccomp.h` adds architecture validation and installation.

Risks and test signals: Since syscall numbers and Android policy evolve, stale generated content can deny required libc/runtime calls or allow calls Android no longer permits. App policy includes process, file, memory, signal, socket, and newer pidfd/syscall ranges through the generated tree. Tests should compare against current Android bionic generation, install on arm64, validate pthread/futex/ioctl paths, and confirm non-listed syscalls hit the appended trap.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/android/arm64_app_policy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/android/arm64_system_policy.h -->
## sources/test-tools/syzkaller/executor/android/arm64_system_policy.h

Purpose: This generated Android BPF policy defines the allowed syscall set for system-account execution on AArch64. It is smaller than the app policy source file but includes privileged/system ranges needed by Android system processes.

Important APIs and types: It exports `const struct sock_filter arm64_system_filter[]` and `arm64_system_filter_size`. The filter is a BPF syscall-number decision tree ending in allow for matched ranges.

Control flow and state: The wrapper loads the syscall number first; this policy then branches through generated `BPF_JGE` and `BPF_JEQ` checks. Its comments show allowed ranges including mount/chroot/accounting/module/syslog/reboot/set*id and clock/time operations that differ from restricted app policy. No local state is modified.

Dependencies and integration points: It integrates only through `android_seccomp.h`, which chooses it when `set_app_seccomp_filter(SCFS_SystemAccount)` is called on arm64 and adds arch validation/trap behavior.

Risks and test signals: The security boundary is entirely encoded in generated jump offsets; manual edits are high risk. Test signals include BPF verifier acceptance, parity with Android bionic generation, exercising representative system-only syscalls, and ensuring app-vs-system selection does not swap filters.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/android/arm64_system_policy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/android/arm_app_policy.h -->
## sources/test-tools/syzkaller/executor/android/arm_app_policy.h

Purpose: This generated Android BPF policy defines the restricted app syscall allowlist for 32-bit ARM. It supports Android sandboxing for `GOARCH_arm`.

Important APIs and types: It exports `const struct sock_filter arm_app_filter[]` and `arm_app_filter_size`. The filter contains a larger 32-bit syscall-number decision tree than arm64 because ARM exposes legacy syscall numbers and ABI-specific calls.

Control flow and state: After `android_seccomp.h` loads `seccomp_data.nr`, this filter compares numeric syscall ranges with `BPF_JGE` and specific equality checks such as futex and ioctl. The comments list allowed legacy and modern calls, including old 32-bit file/stat variants, socket operations, scheduler/timer calls, xattr, epoll, pidfd, clone3, close_range, and process_madvise ranges. It contains no writable state.

Dependencies and integration points: It relies on classic BPF macros and the Android-generated syscall list. The wrapper provides architecture validation for `AUDIT_ARCH_ARM`, final trap behavior, and installation.

Risks and test signals: 32-bit ARM policy is especially sensitive to legacy syscall numbering and Android bionic generator changes. Tests should compile for ARM, compare generated output against Android source, cover pthread creation requirements, and validate representative legacy syscalls plus a denied syscall path.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/android/arm_app_policy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/android/arm_system_policy.h -->
## sources/test-tools/syzkaller/executor/android/arm_system_policy.h

Purpose: This generated Android BPF policy defines the system-account syscall allowlist for 32-bit ARM. It is selected for `GOARCH_arm` when the Android seccomp account is system.

Important APIs and types: It exports `const struct sock_filter arm_system_filter[]` and `arm_system_filter_size`. The policy is a classic BPF decision tree over syscall numbers.

Control flow and state: The generated code permits broader privileged ranges than app policy, including mount/chroot/accounting/reboot/module/time/setuid/setgid-related calls while preserving the generated trap fallback through the wrapper. It performs no architecture validation itself and stores no runtime state.

Dependencies and integration points: `android_seccomp.h` includes this file, chooses it for `SCFS_SystemAccount`, adds architecture checks for `AUDIT_ARCH_ARM`, and installs the combined filter with `prctl`.

Risks and test signals: Risks include stale Android policy generation, jump offset corruption, and divergence from arm app policy where system-only allowances are expected. Tests should include BPF load/install on ARM, comparison with current `genseccomp.py` output, and probes for both system-allowed and denied syscalls.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/android/arm_system_policy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/android/x86_64_app_policy.h -->
## sources/test-tools/syzkaller/executor/android/x86_64_app_policy.h

Purpose: This generated Android BPF policy defines the restricted app syscall allowlist for x86_64 Android executor builds.

Important APIs and types: It exports `const struct sock_filter x86_64_app_filter[]` and `x86_64_app_filter_size`. The decision tree allows selected x86_64 syscall numbers and ends in an allow return for matched paths.

Control flow and state: The wrapper loads the syscall number and this policy applies range/equality checks. Comments show app-allowed groups such as read/write/open/close, mmap/mprotect, signal/timer/scheduler, sockets, xattr, epoll, process_vm, seccomp, bpf, pidfd, clone3, close_range, and process_madvise. The policy itself has no mutable state.

Dependencies and integration points: It is included by `android_seccomp.h` under `GOARCH_amd64`, paired with `AUDIT_ARCH_X86_64`, and installed through the common filter assembly path.

Risks and test signals: x86_64 app policy includes additional pthread-related syscalls noted in the wrapper, so stale generation can break executor threading. Tests should verify `clone3`, robust-list behavior, futex, ioctl, and denial behavior, and compare against Android bionic generation for x86_64.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/android/x86_64_app_policy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/android/x86_64_system_policy.h -->
## sources/test-tools/syzkaller/executor/android/x86_64_system_policy.h

Purpose: This generated Android BPF policy defines the system-account syscall allowlist for x86_64 Android executor builds.

Important APIs and types: It exports `const struct sock_filter x86_64_system_filter[]` and `x86_64_system_filter_size`, consumed by `android_seccomp.h`.

Control flow and state: The filter executes after syscall number load and uses generated branch offsets to permit system-account ranges. Compared with app policy it includes privileged system operations such as module, syslog, reboot, mount/chroot-style groups where Android’s system policy allows them. There is no local persistence.

Dependencies and integration points: It depends on BPF/seccomp definitions and the outer wrapper for architecture validation, final trap, and installation.

Risks and test signals: Main risks are policy drift and accidental mismatch between x86_64 app/system arrays. Tests should include architecture-specific compilation, filter installation, representative system-only syscall probes, and generated-output diffing against Android bionic.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/android/x86_64_system_policy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/android/x86_app_policy.h -->
## sources/test-tools/syzkaller/executor/android/x86_app_policy.h

Purpose: This generated Android BPF policy defines the restricted app syscall allowlist for 32-bit x86 (`GOARCH_386`) executor builds.

Important APIs and types: It exports `const struct sock_filter x86_app_filter[]` and `x86_app_filter_size`. The filter is a classic BPF syscall decision tree with comments mapping numeric ranges to syscall names.

Control flow and state: `android_seccomp.h` loads `seccomp_data.nr`, then this tree handles legacy i386 syscall numbering including `socketcall`, old stat/file operations, xattr, epoll, pidfd, clone3, close_range, and process_madvise ranges. Matching paths return `SECCOMP_RET_ALLOW`; the wrapper appends trap on fallthrough. No state is stored.

Dependencies and integration points: It is selected under `GOARCH_386` and paired with `AUDIT_ARCH_I386` by the Android seccomp wrapper.

Risks and test signals: The 32-bit x86 ABI has many legacy multiplexed or obsolete syscalls, so policy drift can produce surprising executor failures. Tests should cover i386 compilation, BPF verifier acceptance, `socketcall` behavior, pthread requirements, and negative probes for denied syscalls.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/android/x86_app_policy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/android/x86_system_policy.h -->
## sources/test-tools/syzkaller/executor/android/x86_system_policy.h

Purpose: This generated Android BPF policy defines the system-account syscall allowlist for 32-bit x86 executor builds.

Important APIs and types: It exports `const struct sock_filter x86_system_filter[]` and `x86_system_filter_size`.

Control flow and state: The policy runs after syscall-number load and branches through generated `BPF_JGE` ranges and equality checks. It permits a broader i386 system syscall set than the restricted app policy, including privileged system-management ranges, while relying on the outer wrapper to trap unmatched syscalls. It has no mutable state.

Dependencies and integration points: It integrates through `android_seccomp.h` for `GOARCH_386` and `SCFS_SystemAccount`, with architecture validation and `prctl` installation handled there.

Risks and test signals: Risks include stale generated syscall ranges, wrong branch offsets, and accidental differences from Android’s canonical policy. Tests should compare with generated Android bionic output, compile on i386, install in an Android-like environment, and probe system-only and denied syscalls.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/android/x86_system_policy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common.h -->
## sources/test-tools/syzkaller/executor/common.h

Purpose: This shared syzkaller executor/csource header is the central generated-program scaffold. It provides common portability definitions, crash recovery, timing, temporary directory handling, threading, checksum helpers, OS-specific inclusion, pseudo-syscall glue, execution loops, fork-server supervision, and standalone csource `main`.

Important APIs and types: Key globals and macros include `procid`, `clone_ongoing`, `skip_segv`, `segv_env`, and `NONFAILING`. Common helpers include `doexit`, `doexit_thread`, `segv_handler`, `install_segv_handler`, `kill_and_wait`, `sleep_ms`, `current_time_ms`, `use_temporary_dir`, `remove_dir`, fault-injection stubs, `thread_start`, `event_t` operations for BSD/test platforms, `BITMASK`, `STORE_BY_BITMASK`, `csum_inet_*`, and `syz_execute_func`. Execution machinery includes `thread_t`, `thr`, threaded `execute_one`/`loop`, fork-server `loop`, csource `execute_call`/`execute_one`/`loop`, and `main`.

Control flow and state: Compile-time `SYZ_*`, `GOOS_*`, and generated placeholders strip unused code and inject syscall bodies. In executor mode, `loop` optionally replies to the parent, receives execute requests, creates per-iteration working directories, forks test children, runs setup hooks, executes generated calls, watches progress through output counters, kills hung children, removes directories, checks leaks, and replies. In csource mode `main` performs setup, optional multi-process forking, temp-dir/sandbox entry, and calls generated syscall bodies.

Dependencies and integration points: It includes OS-specific headers such as `common_linux.h`, `common_bsd.h`, `common_fuchsia.h`, `common_test.h`, or `common_windows.h`, plus optional `common_ext.h`. It depends on executor-provided `fail`, `exitf`, `debug`, pipe constants, output data, request types, snapshot hooks, and generated placeholders.

Risks and test signals: Risks include signal recovery masking real corruption, watchdog timeouts causing flakes, fork-server cleanup failures, threaded event races, platform macro precedence, and generated placeholder misuse. Tests should include csource generation for threaded/repeat/sandbox combinations, executor protocol tests, crash recovery around `NONFAILING`, temp-dir cleanup on BSD, checksum vectors, and timeout behavior for hung children and glob requests.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_bsd.h -->
## sources/test-tools/syzkaller/executor/common_bsd.h

Purpose: This shared syzkaller header supplies BSD and Darwin platform support for executor/csource builds, including USB setup on NetBSD, fault injection on NetBSD, tun/tap network injection, TCP resource extraction, and setuid/none sandbox entry.

Important APIs and types: NetBSD-specific APIs include `setup_usb`, `setup_fault`, `inject_fault`, and `fault_injected`. Network helpers include `tunfd`, `vsnprintf_check`, `snprintf_check`, `execute_command`, `initialize_tun`, `syz_emit_ethernet`, `read_tun`, `tcp_resources`, and `syz_extract_tcp_res`. Sandbox helpers include `sandbox_common`, `do_sandbox_none`, `wait_for_loop`, and `do_sandbox_setuid`.

Control flow and state: `initialize_tun` derives a tap device/interface from `procid`, recreates or opens it, remaps it to fd 200, configures MAC/IPv4/IPv6 addresses, and seeds ARP/NDP entries using shell commands with an explicit PATH. `syz_emit_ethernet` writes raw packets to `tunfd`; `syz_extract_tcp_res` reads one packet, parses Ethernet plus IPv4/IPv6 TCP headers, and writes adjusted seq/ack values to the caller buffer. `sandbox_common` sets session and resource limits; setuid sandbox forks, drops to `nobody`, and runs `loop`.

Dependencies and integration points: It depends on BSD libc, `ifconfig`, `arp`, `ndp`, tap/tun devices, NetBSD `/dev/fault`, `common_usb_netbsd.h`, executor flags such as `flag_net_injection`, and the common loop from `common.h`.

Risks and test signals: Risks include host command availability, tap driver loading, fd collision assumptions, packet parser truncation, malformed IPv6 extension headers, privilege requirements, and shell command failure behavior. Tests should cover NetBSD fault ioctls, FreeBSD tap module fallback, network injection with multiple `procid` values, TCP extraction for IPv4/IPv6, and setuid sandbox privilege drop.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_bsd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_ext.h -->
## sources/test-tools/syzkaller/executor/common_ext.h

Purpose: This extension-point header is intentionally mostly empty. It lets downstream or non-mainline syzkaller users add pseudo-syscalls and setup hooks without changing the main executor templates.

Important APIs and types: The file documents expected extension conventions: pseudo-syscalls should start with `syz_ext_`; defining `SYZ_HAVE_SETUP_EXT` with `void setup_ext()` adds VM-level setup; defining `SYZ_HAVE_SETUP_EXT_TEST` with `void setup_ext_test()` adds per-test-process setup.

Control flow and state: There is no executable code or persistent state in the default file. `common.h` includes it unless `SYZ_TEST_COMMON_EXT_EXAMPLE` selects the example implementation. If macros are defined by a modified copy, `common.h` calls `setup_ext()` during csource `main` setup and `setup_ext_test()` in forked test children.

Dependencies and integration points: The header is included by both executor and C reproducers. It depends on the surrounding generated executor symbols only when an extension implementation uses them.

Risks and test signals: The main risk is that extensions run in privileged setup paths and can silently alter executor behavior across all generated programs. Tests should verify default builds remain no-op, extension pseudo-syscalls are stripped/included according to `SYZ_*` defines, and setup hooks are called at the documented lifecycle points.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_ext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_ext_example.h -->
## sources/test-tools/syzkaller/executor/common_ext_example.h

Purpose: This test-only extension implementation demonstrates how `common_ext.h` hooks are wired into generated executor/csource builds.

Important APIs and types: It defines `SYZ_HAVE_SETUP_EXT`, `setup_ext`, `SYZ_HAVE_SETUP_EXT_TEST`, and `setup_ext_test`. `setup_ext` logs a debug message. `setup_ext_test` writes an eight-byte marker to `SYZ_DATA_OFFSET + 0x1234`.

Control flow and state: When `SYZ_TEST_COMMON_EXT_EXAMPLE` is enabled, `common.h` includes this header instead of the empty extension header. The global setup hook runs during VM/program setup. The test hook runs inside each test process before executing the generated program. The only persistent effect is the marker written into syzkaller’s data area for test verification.

Dependencies and integration points: It depends on `debug`, `memcpy`, and `SYZ_DATA_OFFSET` from the surrounding executor template. It is referenced by tests such as `TestCommonExt` through the marker write noted in the comment.

Risks and test signals: This file is deliberately simple, but it exercises a high-risk extension mechanism. Tests should confirm both hooks are called once at the expected stages, the marker bytes are present in the data mapping, and normal builds do not include this example unless the test macro is set.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_ext_example.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_fuchsia.h -->
## sources/test-tools/syzkaller/executor/common_fuchsia.h

Purpose: This shared syzkaller header supplies Fuchsia-specific executor/csource primitives: exception-based non-failing memory access, simple event synchronization, Zircon handle pseudo-syscalls, VMAR mapping, future-time generation, and no-sandbox entry.

Important APIs and types: Crash recovery uses thread-local `skip_segv`, `segv_env`, `segv_handler`, `update_exception_thread_regs`, `ex_handler`, `install_segv_handler`, and `NONFAILING`. Threading uses a spin-based `event_t` with `event_init`, `event_reset`, `event_set`, `event_wait`, `event_isset`, and `event_timedwait`. Pseudo-syscalls include `syz_mmap`, `syz_process_self`, `syz_thread_self`, `syz_vmar_root_self`, `syz_job_default`, and `syz_future_time`. Sandbox integration exposes `do_sandbox_none`, and `CAST` works around incompatible function-pointer calls in generated C.

Control flow and state: Fuchsia faults are handled by a process exception channel. The handler thread waits for exceptions, reads exception info, rewrites the faulting thread’s instruction pointer to `segv_handler`, marks the exception handled, and lets `NONFAILING` longjmp or exit depending on `skip_segv`. `syz_mmap` creates a VMO, maps it at a requested root-VMAR-relative address with overwrite/read/write flags, closes the VMO, and returns the Zircon status.

Dependencies and integration points: It depends on Zircon syscalls, fdio, pthreads, and common executor functions (`debug`, `failmsg`, `doexit`, `current_time_ms`, `loop`). `common.h` includes it for `GOOS_fuchsia`.

Risks and test signals: Risks include exception-channel lifetime, rewriting registers for unsupported architectures, spin-wait CPU cost, VMAR address calculation, and handle values being returned as integer pseudo-syscall results. Tests should cover amd64/arm64 exception recovery, `NONFAILING` success/failure, `syz_mmap` fixed-address mapping, event timeouts, and handle pseudo-syscall validity.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_fuchsia.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_kvm.h -->
## sources/test-tools/syzkaller/executor/common_kvm.h

Purpose: This shared KVM header provides architecture-neutral syzkaller KVM helpers used by SYZOS guest support and KVM pseudo-syscalls.

Important APIs and types: It includes `common_kvm_syzos.h` and `kvm.h`, declares `extern char* __start_guest`, defines `executor_fn_guest_addr`, and implements `syz_kvm_assert_syzos_kvm_exit`. In executor C++ builds, a template overload restricts `executor_fn_guest_addr` to guest-address-space function pointers.

Control flow and state: `executor_fn_guest_addr` converts a host-linked guest function address into the runtime guest physical/virtual address by subtracting `&__start_guest` and adding `SYZOS_ADDR_EXECUTOR_CODE`; volatile temporaries prevent unwanted constant materialization. `syz_kvm_assert_syzos_kvm_exit` validates that a `struct kvm_run` exists and that `exit_reason` equals the expected value, returning `-1` with `EINVAL` or `EDOM` on failure and optionally printing debug details in csource mode.

Dependencies and integration points: It is included by architecture-specific KVM headers such as `common_kvm_amd64.h`. It depends on KVM UAPI structures, SYZOS linker symbols, errno, and generated pseudo-syscall gating macros.

Risks and test signals: Risks include incorrect guest address relocation if linker symbols or `SYZOS_ADDR_EXECUTOR_CODE` drift, and assertion helpers being compiled differently between executor and csource. Tests should validate guest function address translation against installed executor-code memory and assert helpers for matching, mismatching, and null `kvm_run` inputs.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_kvm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_kvm_386.h -->
## sources/test-tools/syzkaller/executor/common_kvm_386.h

Purpose: This 386 KVM header is a stub implementation for SYZOS/KVM pseudo-syscalls on 32-bit x86 builds.

Important APIs and types: It conditionally defines no-op versions of `syz_kvm_setup_syzos_vm`, `syz_kvm_add_vcpu`, `syz_kvm_assert_syzos_uexit`, `syz_kvm_assert_syzos_kvm_exit`, and `syz_kvm_setup_cpu`.

Control flow and state: Every function immediately returns `0` regardless of input. No KVM ioctls are issued, no VM/VCPU state is created, and no memory is touched. Compile-time `SYZ_EXECUTOR` or generated syscall-number macros control whether each stub is present.

Dependencies and integration points: It exists so common generated KVM pseudo-syscall names can compile for 386 even though the substantive implementation lives in amd64-specific support. It depends only on surrounding typedefs/macros from the executor environment.

Risks and test signals: The main risk is semantic mismatch: a caller might treat success return values as real KVM setup even though nothing happened. Tests should confirm 386 builds compile, KVM pseudo-syscalls are either not generated for unsupported targets or documented as inert, and no downstream path dereferences a stub “VM” result as a real object.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_kvm_386.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_kvm_amd64.h -->
## sources/test-tools/syzkaller/executor/common_kvm_amd64.h

Purpose: This large amd64 KVM header implements syzkaller’s KVM and SYZOS pseudo-syscalls for x86_64. It builds guest memory layouts, segment tables, page tables, IDTs, TSS structures, CPUID state, user-code installation, VCPU creation, and assertion helpers for guest exits.

Important APIs and types: Data structures include `tss16`, `tss32`, `tss64`, `kvm_syz_vm`, `kvm_text`, `kvm_opt`, `page_alloc_t`, `gdt_entry`, and `addr_size`. Core helpers include `fill_segment_descriptor`, `fill_segment_descriptor_dword`, `setup_syscall_msrs`, `setup_32bit_idt`, `setup_64bit_idt`, `gpa_to_hva`, `syzos_setup_idt`, `pg_alloc`, `get_host_pte_ptr`, `map_4k_page`, `setup_pg_table`, `setup_gdt_64`, `get_cpuid`, `setup_gdt_ldt_pg`, `setup_cpuid`, `reset_cpu_regs`, `install_user_code`, `alloc_guest_mem`, `vm_set_user_memory_region`, `install_syzos_code`, and `setup_vm`. Pseudo-syscalls include `syz_kvm_setup_cpu`, `syz_kvm_setup_syzos_vm`, `syz_kvm_add_vcpu`, and `syz_kvm_assert_syzos_uexit`.

Control flow and state: `syz_kvm_setup_cpu` is the legacy flexible CPU setup path: it maps 24 pages, configures SMRAM, builds GDT/LDT/IDT/TSS entries for 16/32/64-bit, VM86, CPL3, SMM, paging, and VMX cases, copies fuzzer-supplied text with optional assembly prefixes, applies up to two control-register/segment/VMWRITE options, then sets KVM sregs/regs. The newer SYZOS path starts with `syz_kvm_setup_syzos_vm`, which reserves the first page for `kvm_syz_vm`, allocates regions from the provided host memory, installs read-only executor guest code, records boot args, and registers KVM memory slots. `syz_kvm_add_vcpu` creates a VCPU, installs per-CPU user code, configures 64-bit GDT/page tables/IDT, CPUID, registers, and records text sizes in the globals page.

Dependencies and integration points: It depends on `/dev/kvm`, KVM ioctls, `common_kvm.h`, `common_kvm_amd64_syzos.h`, `kvm.h`, generated assembly blobs from `kvm_amd64.S.h`, SYZOS memory constants, executor guest linker symbols, and host CPU CPUID behavior.

Risks and test signals: This is high-risk low-level code. Risks include unchecked ioctl failures in helper paths, page-table pool exhaustion, guest physical to host virtual translation gaps, KVM memory slot overlap, stale Intel/AMD control-bit assumptions, SMM/VMX setup drift, fuzzer-controlled text/options producing invalid CPU state, and 32/64-bit descriptor encoding mistakes. Tests should include KVM smoke tests for `syz_kvm_setup_cpu` modes, SYZOS VM setup with memory-region validation, multiple VCPU creation up to `KVM_MAX_VCPU`, guest exit assertion success/failure, AMD vs Intel CPUID branches, dirty-log/read-only region behavior, and csource diagnostics for mismatched exits.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/common_kvm_amd64.h -->
