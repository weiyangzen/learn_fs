# Research: subset-b-009222

This grouped report covers fio client/configuration/cgroup helpers, CI shell helpers, and checksum/hash primitives. Each source section is bounded by the required reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/cconv.c -->
## sources/test-tools/fio/cconv.c

Purpose: serializes and deserializes `struct thread_options` across fio's client/server protocol using `struct thread_options_pack` and little-endian wire encoding. It exists because thread options contain host pointers, strings, floats, arrays, and variable-length verify/buffer patterns that cannot be sent as a raw structure.

Important APIs and flow: `thread_options_pack_size()` computes the packed size including pattern tails. `convert_thread_options_to_net()` copies scalar fields, string fields, directional arrays, bssplit/zone_split arrays, FDP fields, floating-point union values, and pattern bytes into the packed form. `convert_thread_options_to_cpu()` reverses that mapping, allocating strings and split arrays and validating pattern byte counts against `MAX_PATTERN_SIZE` and the received `top_sz`. `fio_test_cconv()` performs a round-trip pack/unpack/pack comparison with representative verify and buffer patterns.

State and persistence: no persistent storage is used, but CPU conversion allocates heap-owned strings and arrays in `thread_options`; `free_thread_options_to_cpu()` releases those allocations for the conversion test path. The packed object embeds variable data after the fixed structure through `top->patterns`.

Dependencies and integration: depends on `thread_options.h`, endian helpers, `log_err()`, and fio floating-point conversion helpers. It integrates directly with `client.c` when sending `FIO_NET_CMD_UPDATE_JOB` and with server-side job loading/update paths.

Risks and test signals: this is a manually maintained field map, so new `thread_options` fields can silently fail to travel over the network unless both conversion directions and tests are updated. Allocation failures for split arrays are not deeply checked. The strongest local signal is `fio_test_cconv()`, but its own comment says coverage is incomplete.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/cconv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/cgroup.c -->
## sources/test-tools/fio/cgroup.c

Purpose: creates, joins, and cleans fio per-job blkio cgroups when cgroup support is compiled in. It supports legacy cgroup v1 blkio mounts and unified cgroup v2 mounts.

Important APIs and flow: `find_cgroup_mnt()` scans `/proc/mounts` with `getmntent_r()` for a cgroup mount carrying `blkio` options or for a `cgroup2` mount. `cgroup_setup()` lazily finds the mount, builds the job cgroup path from `td->o.cgroup` or job name, creates the directory, records newly created cgroups in a shared list, optionally writes `blkio.weight` for v1, and moves `td->pid` into `tasks` or `cgroup.procs`. `cgroup_shutdown()` moves the pid back to the root cgroup and frees the mount record. `cgroup_kill()` removes tracked cgroup directories unless `cgroup_nodelete` was set.

State and persistence: state lives in a process-global semaphore `lock`, a caller-owned `flist_head` of `struct cgroup_member`, and filesystem directories/files under the mounted cgroup hierarchy. Constructor/destructor functions initialize and remove the semaphore.

Dependencies and integration: uses `fio.h`, `flist`, `smalloc`, `td_verror()`, and Linux mount/cgroup filesystem conventions. It integrates with job setup/shutdown code through `cgroup_setup()` and `cgroup_shutdown()`.

Risks and test signals: behavior depends on process permissions and cgroup mount shape. cgroup v2 rejects `cgroup_weight` with an error, and there is a typo in that error text. Path construction validates overflow, but filesystem races and pre-existing directories affect cleanup ownership. Test signals require Linux cgroup environments; failures surface through `td_verror()` and log messages.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/cgroup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/cgroup.h -->
## sources/test-tools/fio/cgroup.h

Purpose: declares the cgroup integration boundary and provides no-op/error stubs when fio is built without `FIO_HAVE_CGROUPS`.

Important APIs and types: under cgroup support it defines `struct cgroup_mnt { char *path; bool cgroup2; }` and declares `cgroup_setup()`, `cgroup_shutdown()`, and `cgroup_kill()`. Without support it forward-declares `struct cgroup_mnt`, makes `cgroup_setup()` report `EINVAL` through `td_verror()`, and turns shutdown/kill into empty inline functions.

Control flow and state: the header lets callers compile a single code path regardless of cgroup availability. Runtime state is intentionally opaque outside the mount path/type pair.

Dependencies and integration: consumers need `struct thread_data` and `struct flist_head` visible from surrounding fio headers. The header is included by job lifecycle code and by `cgroup.c`.

Risks and test signals: stub behavior means unsupported builds fail only when cgroup setup is requested, not at parse time. Test coverage should include both configured and unconfigured builds to catch accidental reliance on `struct cgroup_mnt` internals.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/cgroup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/ci/actions-build.sh -->
## sources/test-tools/fio/ci/actions-build.sh

Purpose: GitHub Actions build entrypoint for fio. It normalizes CI target OS/architecture, selects target-specific configure flags, runs `./configure`, and builds with parallel `make`.

Important flow: `main()` sources `ci/common.sh`, sets `extra_cflags="-Werror"`, calls `set_ci_target_os`, and switches on `CI_TARGET_BUILD/CI_TARGET_OS`. Android configures the NDK toolchain and `UNAME=Android`; Linux/Ubuntu x86_64 enables CUDA, libiscsi, and libnbd; i686 Linux-style builds add `-m32`; Windows disables native tuning, optionally selects 32-bit Windows, and disables TLS for MSYS2 64-bit. It appends `--extra-cflags` and uses `nproc` or macOS `sysctl` for job count.

State and persistence: it mutates environment variables such as `UNAME`, `PATH`, `LIBS`, `LDFLAGS`, and local configure arguments. It produces fio build outputs through `configure` and `make`.

Dependencies and integration: depends on CI-provided `CI_TARGET_BUILD`, `CI_TARGET_ARCH`, `CI_TARGET_OS`, the Android NDK installed by `actions-install.sh`, and tools installed by platform package steps.

Risks and test signals: `set -eu` catches unset variables except branches that intentionally test empty values. Build matrix changes can break case matching. Test signal is the full configure output and `make` result in CI; platform-specific flags should be checked against install script package coverage.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/ci/actions-build.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/ci/actions-full-test.sh -->
## sources/test-tools/fio/ci/actions-full-test.sh

Purpose: runs fio's longer CI test lane and documentation build.

Important flow: `main()` exits early for Android builds, exports `PYTHONUNBUFFERED=TRUE`, builds a skip list for long tests that are unsuitable in CI (`6`, `1007`, `1008`, and `1018` because `null_blk` modules cannot be loaded), and adds debug mode. In `build-containers`, it additionally skips io_uring-heavy or command-priority-sensitive cases and overrides test `1021` to use `psync,libaio`. It then runs `python3 t/run-fio-tests.py -c` with the computed arguments and builds docs via `make -C doc html`.

State and persistence: it writes test artifacts/logs through the fio test runner and generated HTML under `doc`. It does not maintain its own state.

Dependencies and integration: depends on Python, SciPy/statsmodels/Sphinx packages installed by `actions-install.sh`, make, and the fio test suite under `t/`.

Risks and test signals: skip lists encode CI environment assumptions; if runners gain or lose capabilities the list can hide regressions or introduce false failures. The main signal is the Python test runner exit status plus documentation build success.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/ci/actions-full-test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/ci/actions-install.sh -->
## sources/test-tools/fio/ci/actions-install.sh

Purpose: installs platform-specific fio build and test dependencies in GitHub Actions environments.

Important APIs and flow: `_sudo()` runs commands with sudo when available. `install_ubuntu()` optimizes dpkg behavior, selects base packages, handles i686 multiarch, adds x86_64 engines and CUDA dependencies, and adds container/QEMU-specific packages. `install_fedora()` and RHEL clone helpers install DNF packages and enable required repositories for Oracle, Alma, and Rocky. `install_macos()` uses Homebrew and pip; `install_windows()` installs Python packages; Android downloads and unzips NDK r24. `main()` derives `CI_TARGET_OS` with `set_ci_target_os`, dispatches to `install_${CI_TARGET_OS}`, and prints Python path/version.

State and persistence: mutates host package databases, may add dpkg architecture/repository state, installs Python packages, and downloads Android NDK into the fio tree.

Dependencies and integration: sourced `common.sh` supplies target detection. Build and test scripts assume this script has installed compilers, libraries, headers, docs tools, and Python dependencies.

Risks and test signals: package names and repositories are distribution-version sensitive. `EXTRA_PKGS` is expanded into arrays and can affect shell word handling. Network/package mirror failures are common external risks. Successful subsequent `actions-build.sh`, smoke, and full-test lanes are the validation signal.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/ci/actions-install.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/ci/actions-smoke-test.sh -->
## sources/test-tools/fio/ci/actions-smoke-test.sh

Purpose: minimal CI smoke-test entrypoint.

Important flow: `main()` returns immediately for Android builds, prints a status line, and runs `make test` for all other targets. It uses `set -eu` to fail on command errors and unset variables.

State and persistence: no private state; generated state is whatever `make test` produces in the build tree.

Dependencies and integration: depends on the Makefile produced by `configure`, a completed build, and platform dependencies from `actions-install.sh`. Android is skipped because the build is cross-compiled or otherwise not runnable in this lane.

Risks and test signals: because it is intentionally small, it only catches basic build/test failures. `CI_TARGET_BUILD` must be present under `set -u`; the workflow must set it before invoking the script.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/ci/actions-smoke-test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/ci/common.sh -->
## sources/test-tools/fio/ci/common.sh

Purpose: shared Bash helper for CI target detection.

Important API and flow: `set_ci_target_os()` preserves existing `CI_TARGET_OS` and `CI_TARGET_ARCH` when set. Otherwise it derives `CI_TARGET_OS` from `OSTYPE` (`linux`, `macos`, `windows`, `bsd`, or empty fallback) and derives `CI_TARGET_ARCH` from `uname -m`.

State and persistence: exports no files; it updates shell variables in the caller's process because it is sourced.

Dependencies and integration: used by install and build scripts to share consistent platform naming. It assumes Bash syntax (`function`, `[[ ]]`) and therefore should be sourced only by Bash scripts.

Risks and test signals: `OSTYPE` pattern coverage is coarse, especially for BSD or unusual shells. The function intentionally does not overwrite workflow-provided targets, so matrix correctness depends on GitHub Actions configuration. Build/install dispatch success is the practical test signal.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/ci/common.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/client.c -->
## sources/test-tools/fio/client.c

Purpose: implements fio's network client controller for talking to fio server backends. It manages client creation, TCP/Unix socket connection, probing, command-line/job-file transmission, event polling, PDU endian conversion, status aggregation, JSON/text output, iolog receipt, trigger handling, timeout handling, and cleanup.

Important APIs and flow: `fio_client_add()` and `fio_client_add_explicit()` create `struct fio_client` records; `fio_clients_connect()` connects all clients, installs signal handlers, probes servers, and sends command-line arguments; `fio_clients_send_ini()` sends local or remote job files; `fio_start_all_clients()` starts runs and initializes JSON output; `fio_handle_clients()` is the main poll loop. `fio_handle_client()` receives one network command and dispatches by opcode to handlers for text, disk util, thread/group stats, ETA, probe, start/stop, job update, iolog, vtrigger, sendfile, and job options. Conversion helpers translate every wire PDU field to host order before display/aggregation.

State and persistence: process-global lists track active clients, ETA requests, shared argument clients, and a fd hash. Each client stores socket fd, refs, state enum, pending reply list, option lists, sent job files, output buffer, JSON global options, ETA state, and error/signal. Received iologs are persisted as hostname-suffixed files and may be appended, truncated, or written compressed.

Dependencies and integration: depends on fio network protocol definitions in `server.h`, statistics display in `stat.h`, JSON helpers, `verify-state`, zlib when enabled, and OS sockets/poll/signals. It integrates with CLI and GUI clients via `struct client_ops`.

Risks and test signals: it has broad manual endian conversion and pointer-offset reconstruction for variable PDU payloads, so protocol changes require synchronized updates. Timeout recovery treats repeated `SEND_ETA` specially but removes clients on other timed-out replies. File transfer and iolog handling depend on trusted server-provided sizes/paths within fio's protocol assumptions. Test signals include client/server integration tests, JSON/normal/terse output comparisons, compressed-log tests, and multi-client ETA/stat aggregation runs.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/client.h -->
## sources/test-tools/fio/client.h

Purpose: public interface and state model for fio's client-side network controller.

Important APIs and types: defines client states (`Client_created` through `Client_exited`), `struct client_file`, `struct fio_client`, callback typedefs, `struct client_ops`, `struct client_eta`, address type enum, client type enum, exported lifecycle functions, option/job-file senders, reply wait/update helpers, trigger sender, and global aggregate stats (`sum_stat_clients`, `client_ts`, `client_gs`).

State and persistence: `struct fio_client` is the central mutable object: list/hash links, address union, hostname/port/fd/refs, output and JSON option state, job counters, command args, files, ETA tracking, pending replies, state/error/signal, and caller-owned `client_data`.

Dependencies and integration: includes socket headers, `lib/types.h`, and `stat.h`. Callers provide `client_ops` callbacks so CLI and GUI frontends can share transport logic while customizing output and timeout behavior.

Risks and test signals: the header exposes many fields directly, increasing coupling to `client.c` internals. Any change to client state or callbacks needs consumers rebuilt and tested against both CLI and GUI paths. Compilation of downstream users is the first signal; multi-client run behavior validates semantics.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/client.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/compiler/compiler.h -->
## sources/test-tools/fio/compiler/compiler.h

Purpose: centralizes compiler attributes and compile-time helper macros used throughout fio.

Important APIs and flow: defines `__must_check`, compile-time warning/error attributes, `fio_unused`, constructor/destructor markers `fio_init`/`fio_exit`, `fio_unlikely`, `typecheck()`, `compiletime_assert()` variants, `FIO_ARRAY_SIZE`, `FIO_FIELD_SIZE`, and portable `fio_fallthrough`.

State and persistence: no runtime state. Constructor/destructor attributes affect process initialization order for modules such as cgroup and client hash setup.

Dependencies and integration: depends on compiler support detected by `configure`, especially `CONFIG_STATIC_ASSERT`, `CONFIG_DISABLE_OPTIMIZATIONS`, and `__has_attribute`. It is included by low-level utility code such as `murmur3.c`.

Risks and test signals: compiler feature differences can change whether assertions are enforced. The fallback compile-time assertion path relies on optimizer behavior unless `_Static_assert` is available. Build coverage across GCC/Clang and optimized/unoptimized configurations is the key signal.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/compiler/compiler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/configure -->
## sources/test-tools/fio/configure

Purpose: fio's hand-written configuration script. It detects target OS/CPU/compiler/features, writes `config-host.mak` and `config-host.h`, and records probe details in `config.log`.

Important flow: the script creates temporary C/object/exe paths, installs a cleanup trap, removes old generated config files, parses many `--enable-*`/`--disable-*` options, chooses a compiler, detects target OS/CPU and endianness, then runs compile/link probes for atomics, word size, zlib, AIO variants, pthread features, fallocate/fadvise, affinity, clocks, network/socket helpers, storage engines, optional libraries, CUDA/cuFile, ISA-L, xnvme/libblkio/libnfs, valgrind, zoned block support, and compiler warnings. `output_sym()` appends both make variables and C defines. The tail emits selected `CONFIG_*` symbols, `LIBS`, `CFLAGS`, `LDFLAGS`, `CC`, install prefix, seed bucket count, and an out-of-tree forwarding Makefile when needed.

State and persistence: persistent outputs are `config-host.mak`, `config-host.h`, `config.log`, and possibly `Makefile`. It mutates shell variables as feature state and accumulates `LIBS`, `CFLAGS`, and `LDFLAGS`.

Dependencies and integration: every build consumes its generated config. CI build scripts call it with target-specific flags. Feature choices drive conditional compilation in files such as CRC acceleration, cgroups, zlib iolog support, engines, and platform helpers.

Risks and test signals: probes may pass/fail differently under cross-compilation because run tests are limited. Shell variables default lazily, so option spelling and environment values matter. Library order and package versions are fragile. Primary test signal is successful configure plus build/test across the CI matrix; `config.log` is the debugging artifact.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/configure -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/crc/crc-t10dif.h -->
## sources/test-tools/fio/crc/crc-t10dif.h

Purpose: declares the T10 DIF CRC16 function used for data integrity field checks.

Important API: `fio_crc_t10dif(unsigned short crc, const unsigned char *buffer, unsigned int len)` accepts a seed/current CRC and buffer length so callers can compute incrementally.

State and persistence: no state; pure declaration.

Dependencies and integration: implemented by `crct10dif_common.c`, either through ISA-L when configured or the local table implementation. Used by fio verification/checksum paths and CRC tests.

Risks and test signals: callers must use the correct initial seed for their protocol. ABI is intentionally small; compile and CRC vector tests validate the contract.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/crc/crc-t10dif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/crc/crc16.c -->
## sources/test-tools/fio/crc/crc16.c

Purpose: table-driven standard CRC-16 implementation with polynomial `0x8005` and initial CRC zero.

Important API and flow: exports the 256-entry `crc16_table` and `fio_crc16(const void *buffer, unsigned int len)`. The function walks bytes and applies the inline `crc16_byte()` helper from the header.

State and persistence: no mutable state; the table is constant global data.

Dependencies and integration: depends on `crc16.h`. Used by fio's verification/hash selection and the CRC benchmark/test harness.

Risks and test signals: this computes a specific reflected table variant, so callers must not assume another CRC-16 flavor. Known-answer CRC tests in `crc/test.c` are the key signal.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/crc/crc16.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/crc/crc16.h -->
## sources/test-tools/fio/crc/crc16.h

Purpose: header for fio's CRC-16 routine and byte-step helper.

Important API: declares `crc16_table`, `fio_crc16()`, and inline `crc16_byte(crc, data)` which indexes `(crc ^ data) & 0xff` and shifts the running CRC.

State and persistence: no state beyond the external constant table.

Dependencies and integration: included by `crc16.c` and any code needing byte-at-a-time CRC-16 updates.

Risks and test signals: exposing the table and byte helper makes variant coupling visible to callers. Compile coverage plus known-answer vectors validate it.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/crc/crc16.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/crc/crc32.c -->
## sources/test-tools/fio/crc/crc32.c

Purpose: POSIX-style CRC32/checksum implementation using a static 256-entry table.

Important API and flow: `fio_crc32(const void *buffer, unsigned long length)` initializes `crc` to zero, then for each byte shifts left and xors the table entry indexed by the high CRC byte mixed with input.

State and persistence: no mutable state; table is file-local constant data.

Dependencies and integration: depends on `crc32.h` and standard integer types. Used by verification/checksum selection and CRC tests.

Risks and test signals: this is not the same variant as CRC32C and uses a zero initial value; incorrect caller expectations would produce mismatches. Known-answer tests and benchmark comparisons in the CRC test harness are the main signal.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/crc/crc32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/crc/crc32.h -->
## sources/test-tools/fio/crc/crc32.h

Purpose: declaration header for fio's CRC32 routine.

Important API: `uint32_t fio_crc32(const void * const, unsigned long)` returns the CRC over a caller-provided buffer and length.

State and persistence: no state.

Dependencies and integration: includes `<inttypes.h>` and is included by checksum users and `crc32.c`.

Risks and test signals: header only exposes whole-buffer calculation, not incremental seed/state. Compile coverage and known vectors are the test signals.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/crc/crc32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/crc/crc32c-arm64.c -->
## sources/test-tools/fio/crc/crc32c-arm64.c

Purpose: ARMv8 CRC/crypto accelerated CRC32C implementation with runtime feature probing.

Important APIs and flow: defines global `crc32c_arm64_available`, `crc32c_arm64()` when `ARCH_HAVE_CRC_CRYPTO` is compiled, and `crc32c_arm64_probe()`. The accelerated path processes 1024-byte blocks using ARM CRC intrinsics and PMULL folding constants, then handles remaining 64/32/16/8-bit pieces. The probe uses `os_cpu_has(CPU_ARM64_CRC32C)` once.

State and persistence: mutable globals `crc32c_arm64_available` and private `crc32c_probed` cache CPU capability. No persistent files.

Dependencies and integration: depends on `crc32c.h`, `os_cpu_has`, `<arm_acle.h>`, and `<arm_neon.h>`. `fio_crc32c()` in the header dispatches here before Intel and software paths when available.

Risks and test signals: unaligned casts and architecture-specific intrinsics require correct compiler flags from `configure` (`ARCH_HAVE_CRC_CRYPTO`). Runtime probing must match execution CPU. CRC32C known-answer tests must be run on capable ARM64 hardware and compared with `crc32c_sw()`.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/crc/crc32c-arm64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/crc/crc32c-intel.c -->
## sources/test-tools/fio/crc/crc32c-intel.c

Purpose: Intel SSE4.2 hardware CRC32C implementation with runtime CPUID probing.

Important APIs and flow: defines `crc32c_intel_available`, `crc32c_intel()` when `ARCH_HAVE_SSE4_2` is set, and `crc32c_intel_probe()`. The function processes native word chunks with encoded CRC32 instructions and finishes byte remainders through `crc32c_intel_le_hw_byte()`. The probe checks CPUID leaf 1 ECX bit 20 once.

State and persistence: mutable globals cache availability and probed state. No files.

Dependencies and integration: depends on `crc32c.h`, `do_cpuid`, and `BITS_PER_LONG`. Header dispatch selects this path after ARM64 and before software.

Risks and test signals: inline assembly is sensitive to compiler constraints and 32/64-bit word size. It initializes CRC to `~0` like the software implementation, so hardware and software outputs should match for every vector. CI on SSE4.2-capable x86 plus forced software comparison is the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/crc/crc32c-intel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/crc/crc32c.c -->
## sources/test-tools/fio/crc/crc32c.c

Purpose: portable table-driven CRC32C (Castagnoli) fallback.

Important API and flow: `crc32c_sw(unsigned char const *data, unsigned long length)` starts with `~0`, processes each byte through `crc32c_table[(crc ^ byte) & 0xff] ^ (crc >> 8)`, and returns the running CRC. The table is generated for polynomial `0x1EDC6F41` with reflected input/output.

State and persistence: no mutable state; local constant table only.

Dependencies and integration: included through `crc32c.h`; used directly as fallback and as macro replacement when hardware paths are unavailable.

Risks and test signals: CRC32C variant must match hardware implementations exactly. Known-answer tests and cross-checking ARM/Intel/software paths are the key signals.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/crc/crc32c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/crc/crc32c.h -->
## sources/test-tools/fio/crc/crc32c.h

Purpose: dispatch header for CRC32C implementations.

Important APIs and flow: declares `crc32c_sw()`, availability globals, optional hardware functions/probes, and inline `fio_crc32c()`. The inline dispatcher checks `crc32c_arm64_available`, then `crc32c_intel_available`, then software fallback. If architecture support is not compiled, hardware names are macro-mapped to `crc32c_sw()` and probes are empty.

State and persistence: external globals hold hardware availability; no local state.

Dependencies and integration: includes fio architecture and type headers. `configure` controls `ARCH_HAVE_CRC_CRYPTO` and `ARCH_HAVE_SSE4_2` availability.

Risks and test signals: callers must ensure probe functions have run before expecting hardware dispatch. Header macro fallback makes builds portable, but can hide missing acceleration. Tests should validate both dispatch state and output equality.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/crc/crc32c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/crc/crc64.c -->
## sources/test-tools/fio/crc/crc64.c

Purpose: provides fio's generic CRC64 and NVMe CRC64 implementations.

Important APIs and flow: `fio_crc64()` uses a local table for polynomial `0x95AC9329AC4BC9B5` and initial zero, consuming bytes with right shifts. `fio_crc64_nvme()` either calls ISA-L `crc64_rocksoft_refl()` when `CONFIG_LIBISAL64` is set or uses `crc64nvmetable` with one's-complement seed/final handling for incremental NVMe CRC64.

State and persistence: no mutable state; tables are static constant data.

Dependencies and integration: includes `crc64.h`, `crc64table.h`, and optionally ISA-L `<isa-l/crc64.h>`. Used by verification/checksum paths and CRC tests.

Risks and test signals: the generic and NVMe CRC64 variants have different polynomials/initialization. ISA-L and local implementations must match. Known-answer NVMe vectors and software/ISA-L parity tests are important.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/crc/crc64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/crc/crc64.h -->
## sources/test-tools/fio/crc/crc64.h

Purpose: declaration header for fio CRC64 routines.

Important APIs: declares `fio_crc64(const unsigned char *, unsigned long)` and incremental `fio_crc64_nvme(unsigned long long crc, const void *p, unsigned int len)`.

State and persistence: no state.

Dependencies and integration: consumed by CRC users and implemented in `crc64.c`.

Risks and test signals: both functions return `unsigned long long`, so callers need consistent width assumptions. Compile and known-answer CRC64 tests validate the contract.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/crc/crc64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/crc/crc64table.h -->
## sources/test-tools/fio/crc/crc64table.h

Purpose: contains the 256-entry NVMe CRC64 lookup table used by the local `fio_crc64_nvme()` implementation.

Important content: `crc64nvmetable` is generated from the NVMe 64-bit CRC polynomial documented in `crc64.c`. It is a header-local `static const unsigned long long` table included by one implementation file.

State and persistence: no mutable state; compile-time constant data only.

Dependencies and integration: included by `crc64.c`; not intended as a broad public API.

Risks and test signals: table corruption would silently break NVMe protection-information checks. Known-answer vectors are the practical validation signal; table formatting itself has little logic to unit test.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/crc/crc64table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/crc/crc7.c -->
## sources/test-tools/fio/crc/crc7.c

Purpose: implements CRC-7 using polynomial `x^7 + x^3 + 1`.

Important API and flow: defines `crc7_syndrome_table[256]` and `fio_crc7(const unsigned char *buffer, unsigned int len)`, which iterates bytes through the inline `crc7_byte()` helper.

State and persistence: no mutable state; constant lookup table.

Dependencies and integration: depends on `crc7.h`; used by CRC selection/tests and any protocol needing CRC-7.

Risks and test signals: CRC-7 variants differ in final bit placement and seed; callers must match fio's helper convention. CRC test vectors are the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/crc/crc7.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/crc/crc7.h -->
## sources/test-tools/fio/crc/crc7.h

Purpose: header for CRC-7 table, byte-step helper, and whole-buffer function.

Important APIs: declares `crc7_syndrome_table`, inline `crc7_byte(crc, data)` using `crc7_syndrome_table[(crc << 1) ^ data]`, and `fio_crc7()`.

State and persistence: no state beyond external constant table.

Dependencies and integration: included by `crc7.c` and callers needing incremental byte updates.

Risks and test signals: inline helper exposes the exact shift/index convention. Known-answer tests should include incremental and whole-buffer use.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/crc/crc7.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/crc/crct10dif_common.c -->
## sources/test-tools/fio/crc/crct10dif_common.c

Purpose: implements T10 DIF CRC16, optionally delegating to ISA-L.

Important API and flow: when `CONFIG_LIBISAL` is configured, `fio_crc_t10dif()` calls `crc16_t10dif()`. Otherwise it defines a 256-entry table for generator polynomial `0x8bb7` and iterates bytes as `(crc << 8) ^ table[((crc >> 8) ^ byte) & 0xff]`.

State and persistence: no mutable state; table is file-local constant data.

Dependencies and integration: includes ISA-L `<isa-l/crc.h>` or local `crc-t10dif.h`. Used by fio verify/checksum code and CRC tests.

Risks and test signals: ISA-L and table paths must produce identical values for seeded/incremental calls. Known T10 DIF vectors and ISA-L parity tests validate this file.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/crc/crct10dif_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/crc/fnv.c -->
## sources/test-tools/fio/crc/fnv.c

Purpose: implements fio's 64-bit FNV-style hash over unaligned data.

Important API and flow: `fnv(const void *buf, uint32_t len, uint64_t hval)` repeatedly multiplies the current hash by `FNV_PRIME`. It xors whole `uint64_t` chunks while enough bytes remain, then builds a big-endian-ish tail value from leftover bytes and xors it before returning.

State and persistence: no state; caller supplies seed/current `hval` for incremental behavior.

Dependencies and integration: depends on `fnv.h` and integer types. Used by fio hash/checksum selection and CRC/hash tests.

Risks and test signals: whole-word casts can be sensitive to alignment and host endianness expectations; the comment explicitly optimizes for not requiring 64-bit multiples, not for canonical FNV byte order. Known fio vectors and cross-architecture tests are useful.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/crc/fnv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/crc/fnv.h -->
## sources/test-tools/fio/crc/fnv.h

Purpose: declaration header for the 64-bit FNV helper.

Important API: `uint64_t fnv(const void *, uint32_t, uint64_t)` accepts data, length, and initial/current hash value.

State and persistence: no state.

Dependencies and integration: includes `<inttypes.h>` and is consumed by checksum/hash callers.

Risks and test signals: header does not define an initial constant, so callers must choose the intended seed. Compile and known-answer hash tests validate usage.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/crc/fnv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/crc/md5.c -->
## sources/test-tools/fio/crc/md5.c

Purpose: MD5 implementation adapted from Linux kernel crypto code for fio checksums.

Important APIs and flow: `fio_md5_init()` initializes the four hash words, `fio_md5_update()` accumulates data into 64-byte blocks and calls `md5_transform()`, and `fio_md5_final()` appends MD5 padding/bit length and transforms the final block. `md5_transform()` performs all four MD5 rounds via macros from the header.

State and persistence: state lives in caller-owned `struct fio_md5_ctx`: hash storage pointer, 16-word block buffer, and byte count. No persistent files.

Dependencies and integration: depends on `md5.h` for context and round macros. Used by fio verification/checksum code and CRC/hash test harness.

Risks and test signals: `struct fio_md5_ctx` stores `hash` as a pointer, so callers must provide valid backing storage before init/update/final. Finalization writes digest words in context state rather than returning bytes. Known MD5 vectors and memory-safety tests around context allocation are the key signals.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/crc/md5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/crc/md5.h -->
## sources/test-tools/fio/crc/md5.h

Purpose: MD5 constants, round macros, context type, and public function declarations.

Important APIs and types: defines digest/block/hash sizes, Boolean functions `F1`-`F4`, `MD5STEP`, `struct fio_md5_ctx`, and `fio_md5_init/update/final()`.

State and persistence: context contains a caller-managed `uint32_t *hash`, fixed block buffer, and byte count.

Dependencies and integration: included by `md5.c` and checksum users.

Risks and test signals: pointer-based hash storage is easy to misuse compared with an inline array. Compile-time users and known-answer tests should verify context setup and digest extraction.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/crc/md5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/crc/murmur3.c -->
## sources/test-tools/fio/crc/murmur3.c

Purpose: MurmurHash3 32-bit implementation for fio non-cryptographic hashing.

Important APIs and flow: `murmurhash3()` processes 4-byte blocks with constants `c1` and `c2`, rotates/mixes the running hash, then calls `murmur3_tail()` for 1-3 leftover bytes and final avalanche `fmix32()`. `fio_fallthrough` documents intentional switch fallthrough.

State and persistence: no state; seed is passed per call.

Dependencies and integration: includes `murmur3.h` and `compiler/compiler.h`. Used by fio hash/checksum testing or data-pattern selection.

Risks and test signals: block processing casts to `uint32_t *` and uses Murmur's negative-index loop pattern, which depends on architecture alignment tolerance and endian expectations. Known Murmur3 vectors and cross-platform tests are important.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/crc/murmur3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/crc/murmur3.h -->
## sources/test-tools/fio/crc/murmur3.h

Purpose: declaration header for fio's MurmurHash3 helper.

Important API: `uint32_t murmurhash3(const void *key, uint32_t len, uint32_t seed)`.

State and persistence: no state; caller supplies seed.

Dependencies and integration: includes `<inttypes.h>` and is used by hash callers/tests.

Risks and test signals: header gives no endian/alignment caveats, so tests should cover architectures used by fio. Known-answer vectors validate behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/crc/murmur3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/crc/sha1.c -->
## sources/test-tools/fio/crc/sha1.c

Purpose: SHA-1 implementation based on Mozilla code, optimized to avoid extra context copies.

Important APIs and flow: `fio_sha1_init()` initializes five state words and size. `fio_sha1_update()` appends input into the 64-byte/16-word working buffer and calls `blk_SHA1Block()` for complete blocks. `fio_sha1_final()` appends SHA-1 padding and big-endian length using `htonl()`. `blk_SHA1Block()` performs all 80 rounds using rolling 16-word schedule macros and x86 rotate assembly where available.

State and persistence: state is caller-owned `struct fio_sha1_ctx`: state pointer `H`, working buffer `W`, and total size. No files.

Dependencies and integration: depends on `<arpa/inet.h>` and `sha1.h`. Used by fio verification/checksum and CRC/hash tests.

Risks and test signals: `H` is a pointer requiring valid external storage; update does pointer arithmetic on `void *`, relying on compiler extension behavior. Known SHA-1 vectors and sanitizer builds should validate context setup and padding.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/crc/sha1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/crc/sha1.h -->
## sources/test-tools/fio/crc/sha1.h

Purpose: SHA-1 context and function declarations.

Important APIs and types: `struct fio_sha1_ctx` contains `uint32_t *H`, `unsigned int W[16]`, and byte `size`; functions are `fio_sha1_init()`, `fio_sha1_update()`, and `fio_sha1_final()`.

State and persistence: all hash state is caller-owned. No persistence.

Dependencies and integration: includes `<inttypes.h>` and is consumed by checksum code and `sha1.c`.

Risks and test signals: pointer-backed `H` requires correct caller allocation. Compile plus known SHA-1 vectors validate the interface.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/crc/sha1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/crc/sha256.c -->
## sources/test-tools/fio/crc/sha256.c

Purpose: SHA-256 implementation for fio checksums, adapted from Linux crypto code.

Important APIs and flow: `fio_sha256_init()` seeds eight state words. `fio_sha256_update()` buffers partial blocks, transforms complete 64-byte blocks with `sha256_transform()`, and preserves leftovers. `fio_sha256_final()` computes bit length, applies padding, appends the length, and stores state words into `sctx->buf`. `sha256_transform()` builds a 64-word schedule, runs the unrolled compression rounds, updates state, and clears temporaries.

State and persistence: caller-owned `struct fio_sha256_ctx` tracks byte count, eight-word state, and digest/buffer pointer `buf`.

Dependencies and integration: depends on `../lib/bswap.h` for big-endian loads and `sha256.h`. Used by fio verify/checksum paths and tests.

Risks and test signals: `buf` is a pointer, so callers must provide enough storage for buffering and final digest writes. Final length is passed from host memory, so endian expectations should be verified. Known SHA-256 vectors and sanitizer tests are the main signal.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/crc/sha256.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/crc/sha256.h -->
## sources/test-tools/fio/crc/sha256.h

Purpose: SHA-256 context type and function declarations.

Important APIs and types: defines digest/block sizes, `struct fio_sha256_ctx { uint32_t count; uint32_t state[8]; uint8_t *buf; }`, and `fio_sha256_init/update/final()`.

State and persistence: state is entirely caller-owned; buffer pointer must be valid for update/final behavior.

Dependencies and integration: includes `<inttypes.h>`, consumed by checksum code and `sha256.c`.

Risks and test signals: pointer buffer contract is implicit. Tests should allocate context exactly as production verify code does and check known digests.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/crc/sha256.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/crc/sha3.c -->
## sources/test-tools/fio/crc/sha3.c

Purpose: SHA-3/Keccak implementation supporting SHA3-224, SHA3-256, SHA3-384, and SHA3-512.

Important APIs and flow: digest-specific init functions call `fio_sha3_init()` with the digest size, setting rate (`rsiz`) and zeroing state/buffer. `fio_sha3_update()` absorbs full rate-sized blocks by xoring little-endian words into the 25-lane state and running `keccakf()`. `fio_sha3_final()` applies SHA-3 domain padding (`0x06` and final `0x80`), runs one final permutation, converts state lanes to little endian, and copies `md_len` bytes to `sctx->sha`. `keccakf()` implements the 24 rounds of Theta, Rho/Pi, Chi, and Iota.

State and persistence: caller-owned context stores state lanes, digest size, rate, partial byte count, staging buffer, and output pointer `sha`.

Dependencies and integration: includes `../os/os.h` for `cpu_to_le64()` and `sha3.h`. Used by fio checksum/verification and CRC/hash tests.

Risks and test signals: context output pointer must be initialized by caller. The code casts buffers to `uint64_t *`, so alignment and endian behavior matter. Known SHA-3 vectors for all four digest sizes and sanitizer builds validate this path.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/crc/sha3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/crc/sha3.h -->
## sources/test-tools/fio/crc/sha3.h

Purpose: SHA-3 constants, context type, and public function declarations.

Important APIs and types: defines digest and block sizes for SHA3-224/256/384/512, `struct fio_sha3_ctx`, digest-specific init functions, `fio_sha3_update()`, and `fio_sha3_final()`.

State and persistence: context contains 25 64-bit lanes, selected digest length/rate, partial buffer, and caller-provided digest output pointer.

Dependencies and integration: includes `<inttypes.h>`, consumed by SHA-3 implementation and checksum users.

Risks and test signals: the fixed buffer is sized to `SHA3_224_BLOCK_SIZE`, the largest SHA-3 rate among supported variants; callers must initialize `sha`. Known NIST vectors should cover all variants.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/crc/sha3.h -->
