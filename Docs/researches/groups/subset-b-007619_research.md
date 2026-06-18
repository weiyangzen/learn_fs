# subset-b-007619 research

Grouped code research for LizardFS crcutil build/test helpers, RPM systemd service files, the `lizardfs-admin` command implementation, and CGI server scripts. Each section preserves the source path in its title and is bounded by reconciliation markers for source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/install-sh -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/install-sh

## Purpose
Portable Automake-style `install-sh` replacement used by the vendored crcutil package when the platform does not provide a sufficiently compatible BSD/GNU `install` program. It installs files, installs multiple files into a directory, creates directories, optionally strips binaries, sets owner/group/mode, and supports copy-on-change semantics.

## Important APIs, Types, and Functions
The script interface accepts `-c`, `-C`, `-d`, `-g GROUP`, `-m MODE`, `-o USER`, `-s`, `-t DIRECTORY`, `-T`, `--help`, and `--version`. Environment variables such as `CHGRPPROG`, `CHMODPROG`, `CHOWNPROG`, `CMPPROG`, `CPPROG`, `MKDIRPROG`, `MVPROG`, `RMPROG`, and `STRIPPROG` override tool paths. Internal shell variables build command fragments like `chgrpcmd`, `chmodcmd`, `chowncmd`, `stripcmd`, and track destination mode through `dir_arg`, `dst_arg`, and `no_target_directory`.

## Control Flow, State, and Persistence
Argument parsing separates directory creation from file installation and peels the final argument into the destination unless `-d` or `-t` already defines it. Directory creation probes whether `mkdir -p` is POSIX-compatible for the current mode/umask and falls back to stepwise prefix creation with quoted path segments. File installation copies to a temporary file in the destination directory, applies owner/group/strip/chmod, compares metadata and content under `-C`, then renames into place or unlinks/moves aside the prior destination if `mv -f` fails. Persistence is entirely filesystem side effects: created directories, installed files, mode/owner/group changes, and temporary files cleaned by traps.

## Dependencies and Integration Points
It depends on POSIX `/bin/sh`, common core utilities, `dirname` with `expr`/`sed` fallbacks, and shell traps. The crcutil Autotools-generated build can invoke it through generated Makefiles during `make install`, independent of the larger LizardFS CMake build.

## Risks and Test Signals
Risks include shell quoting edge cases, races during concurrent directory creation, platform-specific `mkdir -m -p` behavior, mode parsing through `expr`, copy-on-change relying on `ls -dlL` field positions, and temporary names colliding in hostile directories. Test signals are installs to existing and missing directories, `-d` multi-directory creation, `-T` rejection of directory targets, `-C` preserving unchanged files, owner/group/mode/strip paths, source or destination names beginning with `-`, and cleanup after interrupted installs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/install-sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/missing -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/missing

## Purpose
GNU Automake `missing` helper for crcutil. It provides diagnostic stubs for maintainer tools that may be absent on an end-user build host, allowing generated artifacts to be touched or placeholder outputs to be created when rebuilding from distribution tarballs.

## Important APIs, Types, and Functions
The command line is `missing [OPTION]... PROGRAM [ARGUMENT]...` with `--run`, `--help`, and `--version`. Recognized program families include `aclocal`, `autoconf`, `autoheader`, `autom4te`, `automake`, `bison`/`yacc`, `flex`/`lex`, `help2man`, `makeinfo`, and `tar`. It normalizes `gnu-`, `gnu`, and `g` prefixes and ignores version suffixes when dispatching.

## Control Flow, State, and Persistence
With `--run`, it first executes the requested program and exits on success; exit code `63` is treated as a likely version mismatch and falls through to emulation. Tool-specific cases print warnings explaining which maintainer package is needed, then touch expected outputs such as `aclocal.m4`, `configure`, `config.h.in`, `Makefile.in`, or manual/info files. Parser generators try to copy pre-generated `.c`/`.h` files from nearby sources or create tiny stubs. The `tar` path retries `gnutar`, `gtar`, and then plain `tar` with some nonportable flags removed. Persistent effects are touched timestamps and occasional generated stub files.

## Dependencies and Integration Points
Depends on POSIX shell plus `sed`, `touch`, `find`, `rm`, `cp`, and tar variants. It integrates with Automake-generated dependency rules for the vendored crcutil source; normal builds should rarely execute it unless source timestamps or maintainer files are modified.

## Risks and Test Signals
Risks include hiding missing maintainer dependencies by touching stale generated files, false success for generated stubs that are not semantically valid, unquoted paths in some `touch`/`sed` results, and behavior tied to obsolete Autotools conventions. Test signals include running each supported tool family with and without `--run`, timestamp updates for expected generated files, error behavior for unknown tools and `--version`, parser-generator fallback from existing generated C/H files, and tar fallback on non-GNU systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/missing -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/tests/aligned_alloc.h -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/tests/aligned_alloc.h

## Purpose
Header-only aligned memory helper for crcutil tests. It gives tests a portable way to allocate a block whose returned pointer, optionally adjusted by a field offset, satisfies a power-of-two alignment requirement.

## Important APIs, Types, and Functions
Defines `crcutil::AlignedAlloc(size_t size, size_t field_offset, size_t align, const void **allocated_mem)` and `crcutil::AlignedFree(void *aligned_memory)`. `AlignedAlloc` stores the original `new char[]` pointer immediately before the aligned pointer and optionally returns that original allocation through `allocated_mem`.

## Control Flow, State, and Persistence
Invalid alignment values are coerced to pointer-size alignment. Allocation over-allocates by `align - 1 + sizeof(*allocated_mem)`, advances past the hidden storage pointer, adjusts for `field_offset`, stores the raw pointer at index `-1`, and returns the aligned address. State is only heap memory and the hidden back-pointer; `AlignedFree` retrieves it and deletes the raw array.

## Dependencies and Integration Points
Depends on crcutil `std_headers.h` for size types and is used by crcutil unit/performance tests that need 16/128/256-byte placement for SSE and table-aligned objects.

## Risks and Test Signals
Risks include callers freeing with `delete[]` instead of `AlignedFree`, field-offset alignment misunderstandings, assumptions that `sizeof(char *)` equals the desired minimum pointer storage alignment, and overflow if enormous `size` plus padding wraps. Test signals are alignment checks for several powers of two and offsets, invalid alignment fallback, null-safe `AlignedFree`, and valgrind/ASan leak checks across repeated allocate/free cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/tests/aligned_alloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/tests/bob_jenkins_rng.h -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/tests/bob_jenkins_rng.h

## Purpose
Small deterministic pseudo-random generator used by crcutil tests to populate buffers and vary CRC inputs without external dependencies.

## Important APIs, Types, and Functions
Defines template specializations `crcutil::BobJenkinsRng<uint32>` and, when `HAVE_UINT64`, `crcutil::BobJenkinsRng<uint64>`. Each exposes `typedef value`, constructors, `Init(seed)`, and `Get()`. Non-MSVC builds define temporary `_rotl` and `_rotl64` rotation macros.

## Control Flow, State, and Persistence
`Init` seeds four internal words `a_`, `b_`, `c_`, and `d_` and discards 20 generated values to mix state. `Get` applies Bob Jenkins small PRNG rotations and additions, mutating all four state words and returning `d_`. State persists only inside each RNG object.

## Dependencies and Integration Points
Depends on crcutil `base_types.h` and platform feature macros. It is integrated by `unittest.h` for repeatable functionality and performance-test data generation.

## Risks and Test Signals
Risks are limited to deterministic test quality rather than cryptographic safety; rotation macros can evaluate arguments more than once if misused and 64-bit support is conditional. Test signals include stable sequences for fixed seeds, different sequences across seeds, 32-bit and 64-bit compilation paths, and no macro leakage after the header undefines non-MSVC rotation macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/tests/bob_jenkins_rng.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/tests/rdtsc.h -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/tests/rdtsc.h

## Purpose
Low-overhead cycle-counter abstraction used by crcutil performance tests.

## Important APIs, Types, and Functions
Defines `crcutil::Rdtsc` with static `uint64 Get()`. It uses `__rdtsc()` on MSVC x86/x64, inline `rdtsc` assembly on GCC AMD64 and i386, and returns `0` on unsupported platforms.

## Control Flow, State, and Persistence
The helper has no mutable state. On GCC i386 it captures low and high 32-bit halves separately and combines them; on GCC AMD64 it requests the low accumulator output into an `int64`, relying on the ABI/register behavior of `rdtsc`.

## Dependencies and Integration Points
Depends on crcutil `platform.h` for CPU and integer feature macros. `unittest.h` uses it to time initialization and CRC variants, reporting cycles per byte.

## Risks and Test Signals
Risks include non-serialized `rdtsc` measurements, CPU frequency migration effects, the AMD64 inline assembly not naming `edx` explicitly, unsupported platforms producing zero timings, and virtualized timers with unstable behavior. Test signals are monotonic-ish positive deltas on supported x86, graceful zero on unsupported builds, and performance tests not dividing by bogus zero-duration samples in practical runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/tests/rdtsc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/tests/set_hi_pri.c -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/tests/set_hi_pri.c

## Purpose
Optional Windows-only helper that raises the crcutil unittest process and main thread priority to reduce timing noise in performance measurements.

## Important APIs, Types, and Functions
Exports C-linkage `void SetHiPri(void)`. On `_WIN32`, it calls `SetThreadPriority(GetCurrentThread(), THREAD_PRIORITY_TIME_CRITICAL)` and `SetPriorityClass(GetCurrentProcess(), REALTIME_PRIORITY_CLASS)`. On non-Windows platforms the function is a no-op.

## Control Flow, State, and Persistence
There is no persistent application state besides process scheduler priority on Windows. The source includes MSVC warning suppressions around `windows.h` and uses an `#if 1` block selecting the most aggressive realtime priority path over a milder high-priority alternative.

## Dependencies and Integration Points
Depends on Win32 APIs when `_WIN32` is defined. `unittest.cc` declares `extern "C" void SetHiPri();` and calls it before constructing CRC verifiers.

## Risks and Test Signals
Risks are explicitly high on Windows: realtime/time-critical priority can make a machine unresponsive if tests hang. Return values are ignored, so permission failures are silent. Test signals include linking the C function into the C++ unittest binary, no-op behavior on Unix builds, and observable priority changes or harmless failure on Windows without administrator rights.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/tests/set_hi_pri.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/tests/unittest.cc -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/tests/unittest.cc

## Purpose
Main executable entry point for crcutil functionality and performance tests. It registers a matrix of CRC implementations and widths, then runs correctness checks before optional cycle-per-byte benchmarks.

## Important APIs, Types, and Functions
Defines `main(int argc, char **argv)`, conditionally detects GCC AMD64 `uint128_t`, declares `SetHiPri()`, and uses `CrcVerifier`, `CreateTest`, and `CrcVerifierFactory` from `unittest.h`. Command-line flags are `--canonical`, `--noperf`, `--perfall`, and `help`.

## Control Flow, State, and Persistence
Startup parses flags into `test_perf_main`, `test_perf_all`, and `canonical`, calls `SetHiPri`, then registers tests for 64-bit, 32-bit, 15-bit, 7-bit, SSE2 128/64/32-bit, compiler-native 128-bit, and multiple-stride generic variants. Performance defaults focus on main 32/64/128 cases; `--perfall` broadens smaller and alternate word/table combinations, while `--noperf` disables performance runs. State is in a stack `CrcVerifier`; no external persistence occurs beyond stdout/stderr reports.

## Dependencies and Integration Points
Depends on all crcutil generic/SSE/rolling CRC headers, platform feature macros, and `set_hi_pri.c`. It is the validation binary for the vendored crcutil implementation embedded under LizardFS.

## Risks and Test Signals
Risks include long runtime and high CPU/memory usage from performance tests, feature-macro mismatches for SSE2/int128 paths, `--canonical` only affecting factory-created tests that consume the flag, and exit status remaining success unless `CHECK` aborts. Test signals are successful completion with `--noperf`, expected help output, functional coverage across raw/canonical variants, performance CSV output when enabled, and conditional compilation on 32-bit, 64-bit, SSE2, and non-x86 targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/tests/unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/tests/unittest.h -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/tests/unittest.h

## Purpose
Core crcutil unittest framework. It wraps generic CRC implementations, verifies algebraic and algorithmic invariants, benchmarks algorithm variants, sorts performance results, and manages aligned placement for verifier instances.

## Important APIs, Types, and Functions
Important types are `GenericCrcTest`, `CrcVerifierInterface`, `AlgSorter`, `PerfTestState`, `RollingCrcTest`, `CrcTest`, `CrcVerifierFactoryInterface`, `CrcVerifier`, and `CrcVerifierFactory`. Key methods include `InitWithCrc32c`, `VerifyPow`, `VerifyCrcZeroes`, `VerifyChangeStartValue`, `VerifyConcatenate`, `VerifyCb`, `VerifyLCD`, `VerifyCrcOfCrc`, `VerifyDistribution`, `VerifyRollingCrc`, `TestFunctionality`, `PerfTestMeasure`, `PerfTestVariants`, `PerfTestRun`, and `TestPerformance`. `CreateTest` registers paired canonical/raw and stride variants.

## Control Flow, State, and Persistence
`CrcVerifier` stores factories, allocates one maximum-sized aligned scratch block, placement-news each test into that memory, runs all functionality tests first, then benchmarks factories marked for performance. `CrcTest::TestFunctionality` validates byte, word, blockword, multiword, SSE4 CRC32C fast path, rolling CRC, start-value transforms, concatenation, CRC-of-CRC, and distribution behavior against slower reference paths. Performance uses a 64 MiB random buffer, sizes from 4 bytes to 64 MiB, `Rdtsc::Get`, repeated trials, and `PerfTestState` to print CSV rows plus best-method summaries. State is in heap-allocated factory objects, aligned scratch memory, temporary performance buffers, and in-memory performance aggregation maps.

## Dependencies and Integration Points
Depends on crcutil `aligned_alloc.h`, `bob_jenkins_rng.h`, `crc32c_sse4.h`, `generic_crc.h`, `rdtsc.h`, `rolling_crc.h`, and `unittest_helper.h`. It bridges generic CRC templates and optional hardware CRC32C acceleration by creating a placement-new `Crc32cSSE4_Test` when degree, polynomial, stride, word size, and CPU support match.

## Risks and Test Signals
Risks include very high memory/time cost, reliance on non-serialized cycle counters, possible undefined behavior if placement-new objects require destructors that are not called, raw `new` ownership in factory arrays, platform-specific compiler workarounds, and a likely `delete[] buf` bug after the pointer has been alignment-adjusted away from `buf0` in `TestPerformance`. Test signals are `--noperf` functional success, deterministic CHECK failures on any CRC mismatch, performance CSV rows with nonzero timings on x86, ASan/UBSan around aligned allocation and buffer deletion, and conditional SSE4/int128 execution only on supported builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/tests/unittest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/tests/unittest_helper.h -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/tests/unittest_helper.h

## Purpose
Minimal assertion macro support for crcutil tests when a richer test framework is not present.

## Important APIs, Types, and Functions
Defines `DEBUG_BREAK`, `CHECK(cond)`, `CHECK_GE(a,b)`, `CHECK_NE(a,b)`, and `CHECK_EQ(a,b)` unless `CHECK` is already defined. MSVC uses `__debugbreak()`; other builds call `exit(1)` after printing.

## Control Flow, State, and Persistence
`CHECK` evaluates a condition once, prints file, line, and failed expression to stderr, flushes, and breaks/exits. There is no persistent state.

## Dependencies and Integration Points
Depends on `std_headers.h` for C stdio/exit declarations and is included by `unittest.h` throughout verifier code.

## Risks and Test Signals
Risks include abrupt process termination that bypasses cleanup, no typed comparison diagnostics beyond the expression text, and macro namespace collision if consumers already define `CHECK`. Test signals are intentional failing assertions, successful preservation of an existing `CHECK` macro, and expected debugger break behavior under MSVC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/tests/unittest_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/rpm/service-files/lizardfs-cgiserv.service -->
# sources/distributed-fs/lizardfs/rpm/service-files/lizardfs-cgiserv.service

## Purpose
Systemd unit for the LizardFS CGI server daemon, exposing the web CGI UI on a configured host and port.

## Important APIs, Types, and Functions
The unit sets `BIND_HOST=0.0.0.0`, `BIND_PORT=9425`, and `ROOT_PATH=/usr/share/mfscgi`, optionally overrides them through `EnvironmentFile=-/etc/default/%p`, and starts `/usr/sbin/lizardfs-cgiserver -H ${BIND_HOST} -P ${BIND_PORT} -R ${ROOT_PATH}` as `User=nobody`.

## Control Flow, State, and Persistence
Systemd starts it after `network.target`, keeps it in the foreground as the main service process, and restarts on abort. The service itself persists no unit-level state; runtime state is the CGI server socket and any web UI file reads.

## Dependencies and Integration Points
Integrates with `src/cgi/lizardfs-cgiserver.py.in`, installed CGI assets under `/usr/share/mfscgi`, and distribution defaults under `/etc/default/lizardfs-cgiserv`.

## Risks and Test Signals
Risks include binding to all interfaces by default, running as `nobody` with filesystem access dependent on installed asset permissions, no hardening directives, and environment-file naming tied to `%p`. Test signals are `systemctl start/status`, listening on port 9425, successful static and CGI responses, override of bind host/port/root path, and restart behavior after process abort.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/rpm/service-files/lizardfs-cgiserv.service -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/rpm/service-files/lizardfs-chunkserver.service -->
# sources/distributed-fs/lizardfs/rpm/service-files/lizardfs-chunkserver.service

## Purpose
Systemd wrapper for the LizardFS chunkserver daemon.

## Important APIs, Types, and Functions
Defines `Type=forking` with `/usr/sbin/mfschunkserver start`, `stop`, and `reload` commands. It is ordered after `network.target` and restarts on abort.

## Control Flow, State, and Persistence
Systemd delegates daemonization and PID handling to the legacy `mfschunkserver` control command. Persistent chunkserver state is outside the unit, in the daemon configuration, chunk storage paths, and runtime PID/state files maintained by the service binary.

## Dependencies and Integration Points
Integrates with packaged `/usr/sbin/mfschunkserver`, LizardFS chunkserver configuration, local disk mounts, and the master registration path.

## Risks and Test Signals
Risks include `Type=forking` correctness depending on the script/binary's daemonization behavior, no explicit dependency on mounted chunk disks, minimal systemd sandboxing, and restart-on-abort not covering clean unexpected exits. Test signals are start/stop/reload through systemd, chunkserver registration with the master, behavior when storage directories are missing, and systemd recognizing the forked process as active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/rpm/service-files/lizardfs-chunkserver.service -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/rpm/service-files/lizardfs-ha-master.service -->
# sources/distributed-fs/lizardfs/rpm/service-files/lizardfs-ha-master.service

## Purpose
Systemd unit for a LizardFS master managed by high-availability tooling, started initially as a shadow under cluster control.

## Important APIs, Types, and Functions
Uses `Type=forking`, `TimeoutSec=0`, and runs `/usr/sbin/mfsmaster -o ha-cluster-managed -o initial-personality=shadow start|stop|reload`. It has `PartOf=lizardfs-uraft.service` and is ordered after `syslog.target` and `network.target`.

## Control Flow, State, and Persistence
Systemd starts/stops the master wrapper, while `PartOf` ties lifecycle to the uRaft HA daemon. Persistent metadata state remains in LizardFS metadata files; this unit influences startup personality and HA management flags.

## Dependencies and Integration Points
Integrates with `lizardfs-uraft.service`, `/usr/sbin/mfsmaster`, and HA cluster promotion/demotion flows.

## Risks and Test Signals
Risks include split-brain if uRaft and master lifecycle ordering is wrong, indefinite start/stop waits due to `TimeoutSec=0`, and manual starts outside uRaft changing personality expectations. Test signals are paired start/stop with `lizardfs-uraft.service`, initial shadow status, promotion through HA, reload propagation, and metadata server status queries after boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/rpm/service-files/lizardfs-ha-master.service -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/rpm/service-files/lizardfs-master.service -->
# sources/distributed-fs/lizardfs/rpm/service-files/lizardfs-master.service

## Purpose
Systemd unit for a standalone LizardFS master server.

## Important APIs, Types, and Functions
Defines `Type=forking`, `TimeoutSec=0`, `/usr/sbin/mfsmaster start|stop|reload`, `Restart=no`, documentation `man:mfsmaster`, and ordering after `network.target`.

## Control Flow, State, and Persistence
Systemd invokes the legacy master control interface and does not restart it automatically. Persistent behavior is owned by `mfsmaster`: metadata files, changelogs, lock/PID files, and configured networking.

## Dependencies and Integration Points
Integrates with LizardFS metadata service configuration, metaloggers, chunkservers, clients, and admin commands that connect to the master port.

## Risks and Test Signals
Risks include no automatic restart for crashes, no explicit filesystem dependency for metadata storage, `TimeoutSec=0` hiding hung control operations, and limited hardening. Test signals are start/stop/reload, client/chunkserver registration, metadata save/load on restart, and systemd state matching the daemonized master process.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/rpm/service-files/lizardfs-master.service -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/rpm/service-files/lizardfs-metalogger.service -->
# sources/distributed-fs/lizardfs/rpm/service-files/lizardfs-metalogger.service

## Purpose
Systemd unit for the LizardFS metalogger daemon, which tails/replicates metadata changelog data from the master.

## Important APIs, Types, and Functions
Uses `Type=forking` and `/usr/sbin/mfsmetalogger start|stop|reload`, restarts on abort, and is ordered after `network.target`.

## Control Flow, State, and Persistence
The unit starts the daemonized metalogger and delegates state management to `mfsmetalogger`. Persistent state includes downloaded metadata/changelog data and daemon lock/PID files outside the unit definition.

## Dependencies and Integration Points
Integrates with master network availability and metalogger configuration. It is operationally related to disaster recovery and metadata backup workflows.

## Risks and Test Signals
Risks include no explicit dependency on the master being reachable, no filesystem mount dependency for backup storage, and restart-on-abort only handling abort-class failures. Test signals are successful master connection, metadata/changelog replication, reload of configuration, clean stop, and behavior during master outage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/rpm/service-files/lizardfs-metalogger.service -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/rpm/service-files/lizardfs-uraft.lizardfs-ha-master.service -->
# sources/distributed-fs/lizardfs/rpm/service-files/lizardfs-uraft.lizardfs-ha-master.service

## Purpose
Alternate or templated packaging copy of the HA master systemd unit used with the uRaft high-availability service.

## Important APIs, Types, and Functions
Its contents match `lizardfs-ha-master.service`: `Type=forking`, `TimeoutSec=0`, `PartOf=lizardfs-uraft.service`, and `mfsmaster -o ha-cluster-managed -o initial-personality=shadow` for start/stop/reload.

## Control Flow, State, and Persistence
Lifecycle follows systemd and uRaft coupling; master metadata persistence is owned by `mfsmaster`, while the unit only controls initial HA personality and cluster-managed mode.

## Dependencies and Integration Points
Integrates with `lizardfs-uraft.service`; the filename suggests packaging/install logic may use it as a service-specific override or renamed companion.

## Risks and Test Signals
Risks are the same as the primary HA master unit plus drift between duplicate service files. Test signals should compare installed units, start/stop under uRaft, verify initial shadow personality, and check packaging chooses the intended filename.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/rpm/service-files/lizardfs-uraft.lizardfs-ha-master.service -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/rpm/service-files/lizardfs-uraft.service -->
# sources/distributed-fs/lizardfs/rpm/service-files/lizardfs-uraft.service

## Purpose
Systemd unit for the LizardFS uRaft high-availability daemon.

## Important APIs, Types, and Functions
Declares `Requires=lizardfs-ha-master.service`, orders after `network.target` and `lizardfs-ha-master.service`, runs `/usr/sbin/lizardfs-uraft` as `User=lizardfs`, sets `PIDFile=/var/run/lizardfs-uraft.pid`, calls `/usr/sbin/lizardfs-uraft-helper demote` in `ExecStopPost`, and disables automatic restart.

## Control Flow, State, and Persistence
Systemd starts the HA master first, then starts the simple foreground uRaft service. On stop, the helper demotes the node. Persistent HA state is not defined in the unit but likely lives in uRaft configuration/state files and master personality metadata.

## Dependencies and Integration Points
Integrates tightly with `lizardfs-ha-master.service`, `lizardfs-uraft`, and `lizardfs-uraft-helper`. It controls HA promotion/demotion safety around the metadata server.

## Risks and Test Signals
Risks include reliance on `ExecStopPost` for demotion, no automatic restart for HA manager failure, PIDFile mismatch with `Type=simple`, ordering that starts master as shadow before HA quorum, and minimal systemd hardening. Test signals are quorum formation, master promotion/demotion, stop demotion behavior, failures of `lizardfs-uraft-helper`, and service state after uRaft exits unexpectedly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/rpm/service-files/lizardfs-uraft.service -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/CMakeLists.txt -->
# sources/distributed-fs/lizardfs/src/admin/CMakeLists.txt

## Purpose
CMake build definition for the `lizardfs-admin` command-line tool and its legacy `lizardfs-probe` symlink.

## Important APIs, Types, and Functions
Uses project macros `collect_sources`, `create_unittest`, and `link_unittest`. Builds `lizardfs-admin-lib` from collected admin sources, links it with `mfscommon`, builds `lizardfs-admin` from `${LIZARDFS_ADMIN_MAIN}`, and creates an `ALL` custom target `lizardfs-probe` using `ln -sf lizardfs-admin lizardfs-probe`.

## Control Flow, State, and Persistence
Configuration collects source/test lists, build creates the library and executable, test macros create a unit-test target, and install copies the executable plus generated symlink into `${BIN_SUBDIR}`. The symlink is persistent in the build tree and install tree.

## Dependencies and Integration Points
Depends on project CMake helper macros, `mfscommon`, and Unix `ln`. It integrates all `src/admin` command implementation files into one binary and preserves compatibility for callers using `lizardfs-probe`.

## Risks and Test Signals
Risks include `ln -sf` portability on non-Unix generators, source collection relying on project naming conventions, and symlink install behavior on platforms without symlink support. Test signals are successful build of `lizardfs-admin-lib`, unit target linking against `mfscommon`, installed executable, installed `lizardfs-probe` symlink, and command dispatch through both names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/chunk_health_command.cc -->
# sources/distributed-fs/lizardfs/src/admin/chunk_health_command.cc

## Purpose
Implements `lizardfs-admin chunks-health`, reporting chunk availability, replication backlog, and deletion backlog by goal.

## Important APIs, Types, and Functions
Defines static goal caches `ChunksHealthCommand::goals` and `goalNames`, option strings `--availability`, `--replication`, and `--deletion`, plus methods `name`, `supportedOptions`, `usage`, `initializeGoals`, `run`, two `printState` overloads, and `print(uint64_t)`.

## Control Flow, State, and Persistence
`run` requires master host/port, sends `cltoma::chunksHealth::build(false)`, deserializes availability and replication state from `LIZ_MATOCL_CHUNKS_HEALTH`, rejects a regular-only response, then lazily loads goal IDs/names via `listGoals`. It prints all reports by default or a filtered subset when options are provided. State persists only in process-static goal caches, which can become stale if goal definitions change during a long-running process, although this CLI normally exits after one command.

## Dependencies and Integration Points
Depends on `ServerConnection`, `protocol/cltoma.h`, `protocol/matocl.h`, `ChunksAvailabilityState`, `ChunksReplicationState`, and goal serialization from the master.

## Risks and Test Signals
Risks include static goal cache reuse, output not escaping goal names in porcelain mode, implicit trust that all goal IDs in state exist in `goalNames`, and duplicate wording typos in option descriptions. Test signals are empty and nonempty availability/replication/deletion states, goal name lookup, all report filters, porcelain/non-porcelain output, incorrect response type handling, and connection/protocol errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/chunk_health_command.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/chunk_health_command.h -->
# sources/distributed-fs/lizardfs/src/admin/chunk_health_command.h

## Purpose
Declares the `ChunksHealthCommand` admin command and its private printing/cache helpers.

## Important APIs, Types, and Functions
`ChunksHealthCommand` derives from `LizardFsProbeCommand` and overrides `name`, `supportedOptions`, `usage`, and `run`. Private members include option constants, `initializeGoals(ServerConnection&)`, `printState` helpers for `ChunksAvailabilityState` and `ChunksReplicationState`, `print(uint64_t)`, and static `goals`/`goalNames`.

## Control Flow, State, and Persistence
The header defines command object shape and process-static state but no logic. Static caches are shared by every instance in the process.

## Dependencies and Integration Points
Includes `common/chunks_availability_state.h`, `common/server_connection.h`, and `admin/lizardfs_admin_command.h`, tying this command to master protocol state and CLI dispatch.

## Risks and Test Signals
Risks include declaration drift with the `.cc` file, the unused declared `kOptionAll`, and static cache lifetime. Build coverage and CLI tests for all supported options are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/chunk_health_command.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/escape_porcelain_string.h -->
# sources/distributed-fs/lizardfs/src/admin/escape_porcelain_string.h

## Purpose
Header-only helper to make single fields safe for simple space-separated porcelain output.

## Important APIs, Types, and Functions
Defines `std::string escapePorcelainString(std::string string)`. A local `replaceAll` lambda replaces backslashes with `\\` and double quotes with `\"`.

## Control Flow, State, and Persistence
The function first escapes backslashes, then quotes, tracks whether replacements occurred, and wraps the field in double quotes if it contains a space, is empty, or required escaping. It has no state.

## Dependencies and Integration Points
Used by `list_goals_command.cc` for goal definitions in porcelain mode. It depends only on `common/platform.h` and `std::string`.

## Risks and Test Signals
Risks include no escaping for tabs/newlines or other shell/CSV-sensitive bytes, header-defined non-`inline` function causing potential ODR/link issues if included by multiple translation units, and consumers assuming a full parser exists. Test signals are covered by `escape_porcelain_string_unittest.cc` for empty, spaces, quotes, and backslashes; additional signals should cover tabs/newlines if porcelain grammar expands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/escape_porcelain_string.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/escape_porcelain_string_unittest.cc -->
# sources/distributed-fs/lizardfs/src/admin/escape_porcelain_string_unittest.cc

## Purpose
GoogleTest unit tests for porcelain string escaping.

## Important APIs, Types, and Functions
Defines `TEST(EscapePorcelainStringTests, EscapePorcelainString)` with expectations for empty strings, plain strings, goal-like punctuation, single/double/triple backslashes, quotes, surrounding slashes, and strings containing spaces.

## Control Flow, State, and Persistence
The test directly calls `escapePorcelainString` and compares exact raw-string outputs. It has no external state.

## Dependencies and Integration Points
Depends on `admin/escape_porcelain_string.h`, `common/platform.h`, and GTest. It is picked up by the admin CMake unit-test macro.

## Risks and Test Signals
The test suite is a strong signal for current quote/backslash behavior but does not cover tabs, newlines, non-ASCII, or round-trip parsing by a consumer. Any change to escaping must update both helper and tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/escape_porcelain_string_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/info_command.cc -->
# sources/distributed-fs/lizardfs/src/admin/info_command.cc

## Purpose
Implements `lizardfs-admin info`, printing high-level master statistics for a LizardFS installation.

## Important APIs, Types, and Functions
Defines `InfoCommand::name`, `supportedOptions`, `usage`, and `run`. It sends legacy packet `CLTOMA_INFO`, expects `MATOCL_INFO`, and deserializes `LizardFsStatistics`.

## Control Flow, State, and Persistence
`run` validates host/port, opens `ServerConnection`, serializes a MooseFS packet, deserializes the statistics payload, and prints either a space-separated porcelain line or a human-readable report. No state is persisted; it is a read-only snapshot.

## Dependencies and Integration Points
Depends on `human_readable_format`, `lizardfs_statistics`, `lizardfs_version`, `server_connection`, and packet serialization helpers. It integrates with master info protocol compatibility inherited from MooseFS.

## Risks and Test Signals
Risks include duplicated `chunkCopies` as deprecated regular copies, porcelain output lacking field names/versioning, and protocol structure drift. Test signals are master info response decoding, human-readable IEC/SI formatting, porcelain field count stability, zero/large statistics, and connection error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/info_command.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/info_command.h -->
# sources/distributed-fs/lizardfs/src/admin/info_command.h

## Purpose
Declares the `InfoCommand` admin command.

## Important APIs, Types, and Functions
`InfoCommand` derives from `LizardFsProbeCommand` and overrides `name`, `supportedOptions`, `usage`, and `run`.

## Control Flow, State, and Persistence
The header carries no state or logic. It provides the command contract consumed by `main.cc`.

## Dependencies and Integration Points
Includes `admin/lizardfs_admin_command.h`; implementation supplies master protocol integration.

## Risks and Test Signals
Risk is declaration/implementation drift. Build and CLI dispatch tests for the `info` command are sufficient signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/info_command.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/io_limits_status_command.cc -->
# sources/distributed-fs/lizardfs/src/admin/io_limits_status_command.cc

## Purpose
Implements `lizardfs-admin iolimits-status`, reporting current global I/O limiting configuration from the master.

## Important APIs, Types, and Functions
Defines `name`, `usage`, `supportedOptions`, `run`, `printStandard`, `printPorcelain`, `printPeriod`, and `isLimitingDisabled`. It consumes `IoGroupAndLimit` entries from `matocl::iolimitsStatus`.

## Control Flow, State, and Persistence
`run` validates host/port, sends `cltoma::iolimitsStatus::build(1)`, deserializes message/config IDs, period, accumulation window, subsystem, and group limits, then prints human or porcelain output. `isLimitingDisabled` treats limiting as disabled when there is no subsystem and no `unclassified` group. State is read-only and transient.

## Dependencies and Integration Points
Depends on `protocol/cltoma.h`, `protocol/matocl.h`, `ServerConnection`, iostream/iomanip formatting, and master-side I/O limit configuration.

## Risks and Test Signals
Risks include `printPeriod` labeling microsecond remainder as a three-digit millisecond fraction while using `period_us % 1000`, porcelain output omitting any disabled marker, and string-based detection of `unclassified`. Test signals are disabled, subsystem-only, group-only, and mixed configurations; period formatting boundaries; group limit conversion from bytes/s to KiB/s; and protocol version/message ID behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/io_limits_status_command.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/io_limits_status_command.h -->
# sources/distributed-fs/lizardfs/src/admin/io_limits_status_command.h

## Purpose
Declares the I/O limits status admin command and exposes protected formatting helpers useful for tests.

## Important APIs, Types, and Functions
`IoLimitsStatusCommand` overrides the base command methods and declares `printStandard`, `printPorcelain`, `printPeriod`, and `isLimitingDisabled`.

## Control Flow, State, and Persistence
No state is stored in the class. The header defines helper signatures that operate on deserialized status values.

## Dependencies and Integration Points
Includes `protocol/matocl.h` for `IoGroupAndLimit` and `admin/lizardfs_admin_command.h`.

## Risks and Test Signals
Risks are mainly ABI drift with the protocol type and protected helpers becoming de facto test API. Unit tests can directly cover disabled detection and period formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/io_limits_status_command.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_chunkservers_command.cc -->
# sources/distributed-fs/lizardfs/src/admin/list_chunkservers_command.cc

## Purpose
Implements `lizardfs-admin list-chunkservers`, listing connected and recently known chunkservers with capacity, chunk count, error, label, and removal metrics.

## Important APIs, Types, and Functions
Defines `name`, `supportedOptions`, `usage`, `run`, and static `getChunkserversList(masterHost, masterPort)`. It prints `ChunkserverListEntry` records and checks `kDisconnectedChunkserverVersion`.

## Control Flow, State, and Persistence
`getChunkserversList` sends `cltoma::cservList::build(true)` to the master and deserializes `LIZ_MATOCL_CSERV_LIST`. `run` formats each entry, using a special disconnected line when the version sentinel is present. State is read-only and transient.

## Dependencies and Integration Points
Depends on `NetworkAddress`, `lizardfs_version`, `human_readable_format`, `ServerConnection`, and `protocol/chunkserver_list_entry.h`. Other commands reuse `getChunkserversList`, notably `list-disks` and `ready-chunkservers-count`.

## Risks and Test Signals
Risks include porcelain labels not escaped, disconnected output using fixed zero placeholders, downstream commands relying on the helper's inclusion of disconnected entries, and protocol changes to `ChunkserverListEntry`. Test signals are connected/disconnected entries, IPv4/port formatting, labels with spaces, large capacities/errors, and reuse by disk/ready-count commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_chunkservers_command.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_chunkservers_command.h -->
# sources/distributed-fs/lizardfs/src/admin/list_chunkservers_command.h

## Purpose
Declares the chunkserver listing command and its reusable static fetch helper.

## Important APIs, Types, and Functions
`ListChunkserversCommand` overrides `name`, `supportedOptions`, `usage`, and `run`, and declares `static std::vector<ChunkserverListEntry> getChunkserversList(...)`.

## Control Flow, State, and Persistence
The header has no state. The helper declaration makes chunkserver discovery a shared integration point for other admin commands.

## Dependencies and Integration Points
Includes `common/network_address.h`, serialization macros, `protocol/chunkserver_list_entry.h`, and the base command header.

## Risks and Test Signals
Risks include broad coupling through the static helper and includes that expose protocol details to users. Build coverage of all callers and CLI tests around disconnected servers are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_chunkservers_command.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_defective_files_command.cc -->
# sources/distributed-fs/lizardfs/src/admin/list_defective_files_command.cc

## Purpose
Implements `lizardfs-admin list-defective-files`, listing files or directories with unavailable chunks, under-goal chunks, or structure errors.

## Important APIs, Types, and Functions
Defines `kDefaultEntriesLimit`, `NodeErrorFlag` bits, `flagToString`, and command methods. Supported options are `--porcelain`, `--unavailable`, `--undergoal`, `--structure-error`, and valued `--limit=`.

## Control Flow, State, and Persistence
`run` validates host/port, ORs selected error flags or defaults to all, gets an entry limit, then pages through `cltoma::listDefectiveFiles::build(flags, entry_index, entries_left)`. Responses update `entry_index` and return `DefectiveFileInfo` records until the master reports index zero or the limit is exhausted. It prints raw quoted filename plus numeric flags in porcelain mode or labeled flag text otherwise. No persistent state is changed.

## Dependencies and Integration Points
Depends on `ServerConnection`, `protocol/cltoma.h`, `protocol/matocl.h`, and the master's defective-file scan/list implementation.

## Risks and Test Signals
Risks include including `registered_admin_connection.h` without using it, direct `exit(1)` on oversized responses instead of throwing, simplistic porcelain quoting that does not escape filenames, and large limits driving repeated master work. Test signals are each flag combination, default all-flags behavior, pagination with nonzero continuation index, limit exhaustion, empty result output, malformed oversized response handling, and filenames with spaces/quotes/newlines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_defective_files_command.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_defective_files_command.h -->
# sources/distributed-fs/lizardfs/src/admin/list_defective_files_command.h

## Purpose
Declares the defective-files listing command.

## Important APIs, Types, and Functions
`ListDefectiveFilesCommand` overrides `name`, `usage`, `supportedOptions`, and `run`.

## Control Flow, State, and Persistence
No state or helper logic lives in the header.

## Dependencies and Integration Points
Includes the base admin command and `common/server_connection.h`, although the connection type is only needed in the implementation.

## Risks and Test Signals
Risks include unnecessary include coupling and declaration drift. Build tests and CLI option parsing tests are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_defective_files_command.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_disks_command.cc -->
# sources/distributed-fs/lizardfs/src/admin/list_disks_command.cc

## Purpose
Implements `lizardfs-admin list-disks`, querying every connected chunkserver for per-disk capacity, flags, error, chunk count, and optional I/O statistics.

## Important APIs, Types, and Functions
Defines formatting helpers for yes/no flags, bandwidth, operation time/count, `printStats`, `printPorcelainStats`, `printPorcelainMode`, `printNormalMode`, and command methods. It uses `DiskInfo`, `HddStatistics`, and `MooseFSVector<DiskInfo>`.

## Control Flow, State, and Persistence
`run` obtains chunkservers via `ListChunkserversCommand::getChunkserversList`, skips disconnected entries, connects directly to each chunkserver address, sends legacy `CLTOCS_HDD_LIST_V2`, deserializes `CSTOCL_HDD_LIST_V2`, and prints disk records. Verbose mode adds last-minute/hour/day read/write/fsync counters and timing. It is read-only; state is sampled from master and chunkservers.

## Dependencies and Integration Points
Depends on master chunkserver listing, direct chunkserver protocol, `DiskInfo` flags, human-readable formatting, `timeToString`, and network address conversion.

## Risks and Test Signals
Risks include sequential direct connections to all chunkservers, partial output if one chunkserver is unreachable, no escaping for disk paths in porcelain mode, write-throughput calculation combining write and fsync time, and skipped disconnected servers hiding stale disks. Test signals are chunkserver discovery, disconnected skip, disks with to-delete/damaged/scanning flags, last-error formatting, verbose statistics, direct chunkserver timeout/error behavior, and paths containing spaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_disks_command.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_disks_command.h -->
# sources/distributed-fs/lizardfs/src/admin/list_disks_command.h

## Purpose
Declares the disk listing admin command.

## Important APIs, Types, and Functions
`ListDisksCommand` overrides `name`, `supportedOptions`, `usage`, and `run`.

## Control Flow, State, and Persistence
No state is stored in the header.

## Dependencies and Integration Points
Includes only `admin/lizardfs_admin_command.h`; implementation integrates chunkserver and disk protocols.

## Risks and Test Signals
Risk is minimal declaration drift. Build and CLI dispatch tests for `list-disks` and `--verbose`/`--porcelain` are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_disks_command.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_goals_command.cc -->
# sources/distributed-fs/lizardfs/src/admin/list_goals_command.cc

## Purpose
Implements `lizardfs-admin list-goals`, showing master-defined replication/erasure goals.

## Important APIs, Types, and Functions
Defines command methods and supports `--porcelain` and `--pretty`. It uses `SerializedGoal` records and `escapePorcelainString` for goal definitions in porcelain output.

## Control Flow, State, and Persistence
`run` validates host/port, sends `cltoma::listGoals::build(true)`, deserializes `LIZ_MATOCL_LIST_GOALS`, then prints either simple tabular text, an aligned pretty table, or space-separated porcelain records of ID, name, and escaped definition. It reads master configuration only.

## Dependencies and Integration Points
Depends on goal serialization, master list-goals protocol, `ServerConnection`, and the porcelain escaping helper. Goal output is reused conceptually by chunk health and other admin tooling.

## Risks and Test Signals
Risks include `std::max_element` on an empty goal vector in `--pretty` mode, porcelain escaping applied to definition but not name, and column width using byte length rather than display width. Test signals are empty/nonempty goals, names/definitions with spaces and quotes, pretty table alignment, porcelain parseability, and protocol errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_goals_command.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_goals_command.h -->
# sources/distributed-fs/lizardfs/src/admin/list_goals_command.h

## Purpose
Declares the goal listing admin command.

## Important APIs, Types, and Functions
`ListGoalsCommand` overrides `name`, `supportedOptions`, `usage`, and `run`.

## Control Flow, State, and Persistence
The header stores no state or helpers.

## Dependencies and Integration Points
Includes `admin/lizardfs_admin_command.h`; implementation integrates the goal protocol and output escaping.

## Risks and Test Signals
Risk is declaration drift. Build and CLI output tests for all display modes are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_goals_command.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_metadataservers_command.cc -->
# sources/distributed-fs/lizardfs/src/admin/list_metadataservers_command.cc

## Purpose
Implements `lizardfs-admin list-metadataservers`, listing the active master and shadow metadata servers with status, hostname, personality, metadata version, and software version.

## Important APIs, Types, and Functions
Defines command methods and overloaded variadic `printInfo` helpers. It consumes `MetadataserverListEntry` and calls `MetadataserverStatusCommand::getStatus`.

## Control Flow, State, and Persistence
`run` resolves the supplied master host/port to numeric address, requests `cltoma::metadataserversList::build`, deserializes master version and shadow list, inserts the connected master entry at the beginning by appending then reversing, and for each server with known port opens a direct connection to query status and hostname. It prints a block per server or a porcelain sequence of values. No state is changed.

## Dependencies and Integration Points
Depends on socket resolution (`tcpresolve`), `ServerConnection`, metadata server list/status/hostname protocols, `lizardfs_version`, and `MetadataserverStatusCommand`.

## Risks and Test Signals
Risks include sequential direct queries causing the whole command to fail if one shadow is unreachable, port-zero entries yielding unknowns, porcelain output spanning multiple lines per server without explicit record separators beyond `printInfo`, and the master insertion/reverse hack. Test signals are master-only clusters, shadow connected/disconnected/port-zero entries, hostname failures, status mapping, porcelain parsing, and DNS/port resolution errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_metadataservers_command.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_metadataservers_command.h -->
# sources/distributed-fs/lizardfs/src/admin/list_metadataservers_command.h

## Purpose
Declares the metadata server listing command.

## Important APIs, Types, and Functions
`ListMetadataserversCommand` overrides `name`, `usage`, `supportedOptions`, and `run`.

## Control Flow, State, and Persistence
No runtime state is defined in the header.

## Dependencies and Integration Points
Includes the base admin command; implementation integrates metadata server list/status protocols.

## Risks and Test Signals
Risk is limited to declaration drift. Build tests and live cluster CLI tests cover it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_metadataservers_command.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_mounts_command.cc -->
# sources/distributed-fs/lizardfs/src/admin/list_mounts_command.cc

## Purpose
Implements `lizardfs-admin list-mounts`, reporting active client sessions/mounts and selected session policy flags.

## Important APIs, Types, and Functions
Defines local `OperationStats`, a serializable `MountEntry` class through `SERIALIZABLE_CLASS_*` macros, and command methods. `MountEntry` contains session ID, peer IP, version, mount info, root path, flags, root/mapall IDs, goal/trash limits, and current/hour operation stats.

## Control Flow, State, and Persistence
`run` sends legacy `CLTOMA_SESSION_LIST` with stats enabled, expects `MATOCL_SESSION_LIST`, skips the initial `uint16_t` stats count, deserializes mount entries, sorts by `sessionId`, derives booleans from `SESFLAG_*`, computes whether goal/trash limits are meaningful, and prints normal or porcelain output. Verbose output adds goal and trash-time constraints. It is read-only session-state inspection.

## Dependencies and Integration Points
Depends on MooseFS serialization macros, `MooseFsString`, `MooseFSVector`, `GoalId`, session flag constants, version formatting, IP conversion, and master session-list protocol.

## Risks and Test Signals
Risks include local serialization shape needing to match master protocol exactly, operation stats being deserialized but not printed, porcelain output not escaping mount info/path, goal/trash validity heuristics, and path/info fields containing spaces. Test signals are multiple sessions sorted by ID, every session flag, invalid/valid goal limits, trash time defaults, verbose and porcelain modes, and protocol compatibility across client versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_mounts_command.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_mounts_command.h -->
# sources/distributed-fs/lizardfs/src/admin/list_mounts_command.h

## Purpose
Declares the mount/session listing command.

## Important APIs, Types, and Functions
`ListMountsCommand` overrides `name`, `supportedOptions`, `usage`, and `run`.

## Control Flow, State, and Persistence
No state is declared in the header.

## Dependencies and Integration Points
Includes the base admin command; implementation owns the local `MountEntry` protocol model.

## Risks and Test Signals
Risk is declaration drift. Build and CLI tests with `--verbose` and `--porcelain` are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_mounts_command.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_tapeservers_command.cc -->
# sources/distributed-fs/lizardfs/src/admin/list_tapeservers_command.cc

## Purpose
Implements `lizardfs-admin list-tapeservers`, listing active tape servers known to the master.

## Important APIs, Types, and Functions
Defines command methods and consumes `TapeserverListEntry` records deserialized by `matocl::listTapeservers`.

## Control Flow, State, and Persistence
`run` validates host/port, sends `cltoma::listTapeservers::build`, receives `LIZ_MATOCL_LIST_TAPESERVERS`, and prints each tapeserver address, server name/id, version, and label in porcelain or human form. No state changes.

## Dependencies and Integration Points
Depends on `ServerConnection`, `protocol/cltoma.h`, `protocol/matocl.h`, `NetworkAddress` embedded in the entry, and version formatting.

## Risks and Test Signals
Risks include unescaped label/server fields in porcelain mode and command behavior when the feature is unsupported or no tapeservers exist. Test signals are empty and nonempty lists, labels with spaces, version formatting, and master protocol errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_tapeservers_command.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_tapeservers_command.h -->
# sources/distributed-fs/lizardfs/src/admin/list_tapeservers_command.h

## Purpose
Declares the tapeserver listing command.

## Important APIs, Types, and Functions
`ListTapeserversCommand` overrides `name`, `usage`, `supportedOptions`, and `run`.

## Control Flow, State, and Persistence
No runtime state is declared here.

## Dependencies and Integration Points
Includes `admin/lizardfs_admin_command.h`; implementation integrates tapeserver protocol.

## Risks and Test Signals
Risk is minimal declaration drift. Build and live-protocol tests cover it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_tapeservers_command.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_tasks_command.cc -->
# sources/distributed-fs/lizardfs/src/admin/list_tasks_command.cc

## Purpose
Implements `lizardfs-admin list-tasks`, listing tasks currently executed by the master.

## Important APIs, Types, and Functions
Defines command methods and uses `JobInfo` entries returned by `matocl::listTasks`.

## Control Flow, State, and Persistence
`run` validates host/port, sends `cltoma::listTasks::build(true)`, deserializes `LIZ_MATOCL_LIST_TASKS`, prints a no-task message if empty, otherwise prints each task ID in hex and its description. It is read-only.

## Dependencies and Integration Points
Depends on `ServerConnection`, `common/job_info.h`, master task-list protocol, and iostream formatting. It pairs operationally with `stop-task`.

## Risks and Test Signals
Risks include no porcelain mode, descriptions not escaped or width-limited, imported but unused registered admin connection header, and task IDs printed with width too small for larger values. Test signals are empty/nonempty task lists, large IDs, long descriptions, and consistency with `stop-task` IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_tasks_command.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_tasks_command.h -->
# sources/distributed-fs/lizardfs/src/admin/list_tasks_command.h

## Purpose
Declares the task listing command.

## Important APIs, Types, and Functions
`ListTasksCommand` overrides `name`, `usage`, and `run`; it does not declare custom supported options.

## Control Flow, State, and Persistence
No state is defined in the header.

## Dependencies and Integration Points
Includes base command and `common/server_connection.h`, though implementation handles connection details.

## Risks and Test Signals
Risks include unnecessary include coupling and lack of supported-options override. Build and command dispatch tests cover it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_tasks_command.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/lizardfs_admin_command.cc -->
# sources/distributed-fs/lizardfs/src/admin/lizardfs_admin_command.cc

## Purpose
Defines shared option-name constants for the `lizardfs-admin` command hierarchy.

## Important APIs, Types, and Functions
Initializes `LizardFsProbeCommand::kPorcelainMode`, `kPorcelainModeDescription`, and `kVerboseMode`.

## Control Flow, State, and Persistence
There is no control flow beyond static initialization of strings. The constants are read by command implementations and `main.cc` help output.

## Dependencies and Integration Points
Includes the base command header and `common/platform.h`. It centralizes the spellings `--porcelain` and `--verbose`.

## Risks and Test Signals
Risks are static initialization order only in theory and option spelling changes affecting all commands. Build/link success and CLI option parsing are the signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/lizardfs_admin_command.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/lizardfs_admin_command.h -->
# sources/distributed-fs/lizardfs/src/admin/lizardfs_admin_command.h

## Purpose
Defines the abstract base interface for all `lizardfs-admin` subcommands and the `WrongUsageException` used for CLI errors.

## Important APIs, Types, and Functions
Declares `LIZARDFS_CREATE_EXCEPTION_CLASS(WrongUsageException, Exception)`, `LizardFsProbeCommand::SupportedOptions`, static option constants, virtual destructor, pure virtual `name`, `usage`, and `run`, plus default empty `supportedOptions`.

## Control Flow, State, and Persistence
The base class has no instance state. `main.cc` allocates derived commands and dispatches through this interface.

## Dependencies and Integration Points
Depends on `common/exception.h` and `admin/options.h`. Every admin command includes this as its CLI contract.

## Risks and Test Signals
Risks include raw pointer ownership in `main.cc` despite the virtual destructor, command implementations throwing `WrongUsageException` for help, and no standardized command metadata beyond printed usage. Build coverage of all derived classes and help output are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/lizardfs_admin_command.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/magic_recalculate_metadata_checksum_command.cc -->
# sources/distributed-fs/lizardfs/src/admin/magic_recalculate_metadata_checksum_command.cc

## Purpose
Implements undocumented `magic-recalculate-metadata-checksum`, a privileged command that asks a metadata server to recalculate metadata checksum, synchronously or asynchronously.

## Important APIs, Types, and Functions
Defines command methods and supports `--async` and valued `--timeout=`. It sends `cltoma::adminRecalculateMetadataChecksum::build(async)` over `RegisteredAdminConnection`.

## Control Flow, State, and Persistence
`run` reads `--async`, computes timeout in milliseconds from seconds, creates an authenticated admin connection, sends the recalculation request, deserializes status, prints the error string to stderr, and exits nonzero on non-OK status. The operation can change server-side metadata checksum state or schedule work, but this client persists no local state.

## Dependencies and Integration Points
Depends on admin password challenge/response, `ServerConnection::kDefaultTimeout`, and master/metadataserver admin protocol. `main.cc` hides `magic-*` commands from the generic help list.

## Risks and Test Signals
Risks include no argument-count validation before `options.argument(0/1)`, timeout multiplication overflow for large values, direct `exit(1)`, and operational sensitivity of recalculating metadata checksums. Test signals are sync/async success, bad password, timeout behavior, invalid/missing arguments, server rejection status, and help hiding while still allowing explicit command usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/magic_recalculate_metadata_checksum_command.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/magic_recalculate_metadata_checksum_command.h -->
# sources/distributed-fs/lizardfs/src/admin/magic_recalculate_metadata_checksum_command.h

## Purpose
Declares the undocumented metadata checksum recalculation command.

## Important APIs, Types, and Functions
`MagicRecalculateMetadataChecksumCommand` overrides `name`, `usage`, `supportedOptions`, and `run`.

## Control Flow, State, and Persistence
The header has no state.

## Dependencies and Integration Points
Includes the base admin command. Implementation integrates authenticated admin protocol.

## Risks and Test Signals
Risk is declaration drift and the command being operationally powerful despite minimal type surface. Build and authenticated protocol tests are signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/magic_recalculate_metadata_checksum_command.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/main.cc -->
# sources/distributed-fs/lizardfs/src/admin/main.cc

## Purpose
Entry point and dispatcher for the `lizardfs-admin`/`lizardfs-probe` CLI.

## Important APIs, Types, and Functions
Defines `int main(int argc, const char **argv)`. It constructs a vector of `const LizardFsProbeCommand*` containing all command objects, builds `Options` from each command's supported options, dispatches `run`, and prints usage/help on `WrongUsageException`.

## Control Flow, State, and Persistence
Main requires a command name, shifts remaining arguments into strings, finds a matching command, and returns after successful `run`. `help` and `-h` trigger the aggregate help path. Wrong usage prints global usage plus either all non-`magic-*` commands or the specific command usage/options. Generic `Exception` prints `Error:` and returns 1. State is only process heap allocations for command objects; they are not deleted before exit.

## Dependencies and Integration Points
Includes every command header, `Options`, exception/error utilities, version/formatting includes, and protocol constants. It is the single registry where adding a new command becomes user-visible.

## Risks and Test Signals
Risks include raw `new` leaks until process exit, hidden magic command help, commands calling `exit(1)` and bypassing main's exception handling, and unsupported short options except command `-h`. Test signals are no-arg, unknown command, aggregate help, specific wrong-usage help, option parse errors, every command dispatch, and non-`Exception` failures such as `std::out_of_range` from bad command code paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/main.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/manage_locks_command.cc -->
# sources/distributed-fs/lizardfs/src/admin/manage_locks_command.cc

## Purpose
Implements `lizardfs-admin manage-locks`, a privileged command for listing or unlocking flock/POSIX file locks.

## Important APIs, Types, and Functions
Defines `parseType`, `lockTypeToString`, `processUnlock`, `processListType`, `processList`, and command methods. Options include `--active`, `--pending`, `--inode=`, `--owner=`, `--sessionid=`, `--start=`, and `--end=`.

## Control Flow, State, and Persistence
`run` requires four positional arguments: host, port, `list|unlock`, and `flock|posix|all`; it creates an authenticated `RegisteredAdminConnection`. Unlock requires `--inode`, and either both owner/sessionid or neither. It sends a broad inode unlock or a single lock-range unlock. Listing pages through `LIZ_CLTOMA_MANAGE_LOCKS_LIST_LIMIT` chunks for active and/or pending flock/POSIX locks, optionally filtered by inode, until fewer than the limit are returned. Unlock mutates master lock state; list is read-only.

## Dependencies and Integration Points
Depends on admin authentication, `master/locks.h`, `protocol/lock_info.h`, `cltoma::manageLocks*`, `matocl::manageLocks*`, and LizardFS error strings.

## Risks and Test Signals
Risks include porcelain mode still printing section headers, direct `exit(1)` on EPERM or oversized list responses, `--active` and `--pending` both set producing both categories, type parsing depending on fourth argument, and destructive broad unlock by inode when owner/sessionid are omitted. Test signals are list active/pending for flock/POSIX/all, pagination at exact limit, inode filtering, single and broad unlock, mismatched owner/session arguments, range boundaries, bad password, EPERM messaging, and porcelain parseability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/manage_locks_command.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/manage_locks_command.h -->
# sources/distributed-fs/lizardfs/src/admin/manage_locks_command.h

## Purpose
Declares the lock-management admin command.

## Important APIs, Types, and Functions
`ManageLocksCommand` overrides `name`, `usage`, `supportedOptions`, and `run`.

## Control Flow, State, and Persistence
No state lives in the header; destructive behavior is in the implementation.

## Dependencies and Integration Points
Includes the base command header. Implementation integrates master lock protocol and authentication.

## Risks and Test Signals
Risk is declaration drift and the command's privileged nature hidden behind a simple interface. Authenticated integration tests are the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/manage_locks_command.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/metadataserver_status_command.cc -->
# sources/distributed-fs/lizardfs/src/admin/metadataserver_status_command.cc

## Purpose
Implements `lizardfs-admin metadataserver-status`, reporting whether a metadata server is master or shadow and its metadata version.

## Important APIs, Types, and Functions
Defines command methods and static `MetadataserverStatusCommand::getStatus(ServerConnection&)`. It maps `LIZ_METADATASERVER_STATUS_MASTER`, `LIZ_METADATASERVER_STATUS_SHADOW_CONNECTED`, and `LIZ_METADATASERVER_STATUS_SHADOW_DISCONNECTED` to strings.

## Control Flow, State, and Persistence
`run` validates host/port, opens `ServerConnection`, calls `getStatus`, and prints three fields in porcelain or labeled form. `getStatus` sends `cltoma::metadataserverStatus::build(1)`, deserializes message ID, status, and metadata version, and returns an unknown fallback for unrecognized status. It is read-only.

## Dependencies and Integration Points
Depends on `protocol/cltoma.h`, `protocol/matocl.h`, `ServerConnection`, and status constants. `list-metadataservers` reuses `getStatus`.

## Risks and Test Signals
Risks include ignoring message ID, unknown statuses losing the raw numeric code, and direct server query failures propagating to list commands. Test signals are all known statuses, unknown status fallback, metadata version formatting, porcelain field separators, and reuse from shadow listing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/metadataserver_status_command.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/metadataserver_status_command.h -->
# sources/distributed-fs/lizardfs/src/admin/metadataserver_status_command.h

## Purpose
Declares metadata-server status reporting types and command.

## Important APIs, Types, and Functions
Defines `struct MetadataserverStatus { std::string personality; std::string serverStatus; uint64_t metadataVersion; }` and `MetadataserverStatusCommand` with overrides plus static `getStatus(ServerConnection&)`.

## Control Flow, State, and Persistence
No state is stored; the struct is a value return from protocol decoding.

## Dependencies and Integration Points
Includes `common/server_connection.h` and the base command header. The static helper is shared by `list-metadataservers`.

## Risks and Test Signals
Risks include stringly typed status/personality and helper coupling to live network connections. Build and protocol mapping tests are signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/metadataserver_status_command.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/options.cc -->
# sources/distributed-fs/lizardfs/src/admin/options.cc

## Purpose
Implements the small long-option parser used by `lizardfs-admin` subcommands.

## Important APIs, Types, and Functions
Defines `Options::Options(expectedOptions, argv)` and `Options::parseOption(arg, expecting_value, valued_option)`. Expected option strings ending in `=` are treated as valued options with the visible option name trimmed.

## Control Flow, State, and Persistence
Construction initializes `options_` and `valued_options_`, then scans argv. If the previous valued option was waiting, the current argument becomes its value even if it starts with `--`. Otherwise `--`-prefixed arguments are parsed as options; all others become positional arguments. `--name=value` is accepted only for valued options, while bare valued options set `expecting_value` and mark the option as set. Missing values and unexpected options throw `Options::ParseError`. State persists in the `Options` object for a single command invocation.

## Dependencies and Integration Points
Depends on the `Options` header and C++ maps/vectors. `main.cc` builds the expected option list from each command's `supportedOptions`.

## Risks and Test Signals
Risks include no support for short options, no `--` end-of-options marker, valued options accepting the next positional argument silently, empty values accepted through `--opt=`, parse assertion on empty argv entries, and `std::stoi` conversion exceptions escaping as generic exceptions. Test signals are flags, valued options with separate and equals syntax, unexpected options, unexpected parameter on flag, missing value, values beginning with `--`, and positional arguments after options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/options.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/options.h -->
# sources/distributed-fs/lizardfs/src/admin/options.h

## Purpose
Declares the `Options` parser/result object used by admin commands.

## Important APIs, Types, and Functions
Defines nested `ParseError`, constructor, `arguments`, `argument`, `isSet`, `getValue<T>`, `isOptionExpected`, `isOptionValued`, private `convert<T>`, and explicit specializations for string and numeric types.

## Control Flow, State, and Persistence
The object owns `options_`, `valued_options_`, and positional `arguments_`. `isSet` asserts the option was expected; `getValue` returns the default when not set or converts the stored string using the appropriate `std::sto*` function.

## Dependencies and Integration Points
Depends on project exception macros and common assertions. It is consumed by every `LizardFsProbeCommand::run` implementation.

## Risks and Test Signals
Risks include unchecked `argument(pos)` indexing, conversion exceptions not wrapped as `ParseError`, no bool/custom conversions, and assertions disappearing in release builds. Unit tests should cover typed conversions, defaults, invalid numeric strings, and out-of-range values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/options.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/promote_shadow_command.cc -->
# sources/distributed-fs/lizardfs/src/admin/promote_shadow_command.cc

## Purpose
Implements `lizardfs-admin promote-shadow`, a privileged command that promotes a HA-managed shadow metadata server to master.

## Important APIs, Types, and Functions
Defines command methods. It sends `cltoma::adminBecomeMaster::build()` and validates with a subsequent `cltoma::metadataserverStatus::build(1)`.

## Control Flow, State, and Persistence
`run` validates shadow host/port, authenticates with `RegisteredAdminConnection`, requests promotion, prints the status string, exits on non-OK, then double-checks the server reports `LIZ_METADATASERVER_STATUS_MASTER`. The server-side operation changes metadata server personality and HA state.

## Dependencies and Integration Points
Depends on admin password challenge/response, HA cluster-managed master mode, `matocl::adminBecomeMaster`, and metadataserver status protocol.

## Risks and Test Signals
Risks include operational split-brain if used outside correct HA context, direct `exit(1)`, connection reuse immediately after promotion, and limited diagnostics if the final status is not master. Test signals are successful promotion, rejection on non-HA personality, bad password, status double-check failure, and cluster behavior after promotion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/promote_shadow_command.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/promote_shadow_command.h -->
# sources/distributed-fs/lizardfs/src/admin/promote_shadow_command.h

## Purpose
Declares the shadow promotion admin command.

## Important APIs, Types, and Functions
`PromoteShadowCommand` overrides `name`, `usage`, and `run`.

## Control Flow, State, and Persistence
No header state.

## Dependencies and Integration Points
Includes `common/server_connection.h` and base command header; implementation uses authenticated admin protocol.

## Risks and Test Signals
Risks are operational rather than structural. Build and HA integration tests cover it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/promote_shadow_command.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/ready_chunkservers_count_command.cc -->
# sources/distributed-fs/lizardfs/src/admin/ready_chunkservers_count_command.cc

## Purpose
Implements `lizardfs-admin ready-chunkservers-count`, printing a simple count of chunkservers considered writable.

## Important APIs, Types, and Functions
Defines command methods and reuses `ListChunkserversCommand::getChunkserversList`.

## Control Flow, State, and Persistence
`run` requires master host/port, fetches chunkservers, counts entries whose `totalspace > 0`, and prints the count. It is read-only and has no options.

## Dependencies and Integration Points
Depends on the chunkserver listing helper and the semantics of `ChunkserverListEntry::totalspace`.

## Risks and Test Signals
Risks include treating any nonzero total space as ready even if the server is disconnected, damaged, full, labeled out, or otherwise unwritable; it also ignores available space. Test signals are connected/disconnected entries, zero/positive total space, full disks, and consistency with actual master write placement decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/ready_chunkservers_count_command.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/ready_chunkservers_count_command.h -->
# sources/distributed-fs/lizardfs/src/admin/ready_chunkservers_count_command.h

## Purpose
Declares the ready chunkserver count command.

## Important APIs, Types, and Functions
`ReadyChunkserversCountCommand` overrides `name`, `usage`, and `run`.

## Control Flow, State, and Persistence
No state is declared in the header.

## Dependencies and Integration Points
Includes the base admin command. Implementation integrates chunkserver listing.

## Risks and Test Signals
Risk is mostly semantic drift between "ready" and the count predicate. Build and helper-based tests are signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/ready_chunkservers_count_command.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/registered_admin_connection.cc -->
# sources/distributed-fs/lizardfs/src/admin/registered_admin_connection.cc

## Purpose
Implements authenticated admin connections to the master/metadataserver using an admin password challenge-response exchange.

## Important APIs, Types, and Functions
Defines local `getPassword()` and static `RegisteredAdminConnection::create(host, port, timeout)`. It uses `cltoma::adminRegister`, `matocl::adminRegisterChallenge`, `md5_challenge_response`, and `cltoma::adminRegisterResponse`.

## Control Flow, State, and Persistence
`create` allocates a `RegisteredAdminConnection`, sets timeout, requests an admin register challenge, deserializes the challenge, reads a password from stdin with echo disabled on terminals, computes an MD5 challenge response, overwrites the password string with zero bytes, sends the response, deserializes status, and throws `ConnectionException` on authentication failure. The connection remains open and kept alive for subsequent admin requests.

## Dependencies and Integration Points
Depends on `KeptAliveServerConnection`, protocol serializers, `common/md5.h`, Unix `getpass` or Windows console mode APIs, stdin behavior, and LizardFS status strings. All mutating admin commands use this factory.

## Risks and Test Signals
Risks include MD5 challenge-response strength, password data copies outside the shredded string, stdin behavior for noninteractive scripts, echo restoration errors on Windows if input fails, and direct prompting in commands that may be automated. Test signals are terminal and piped password input, bad password error, timeout propagation, challenge/response packet validation, password memory clearing best-effort, and repeated authenticated requests over the returned connection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/registered_admin_connection.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/registered_admin_connection.h -->
# sources/distributed-fs/lizardfs/src/admin/registered_admin_connection.h

## Purpose
Declares the authenticated admin connection type used by privileged `lizardfs-admin` commands.

## Important APIs, Types, and Functions
`RegisteredAdminConnection` derives from `KeptAliveServerConnection` and exposes static `create(host, port, timeout = kDefaultTimeout)`. The constructor is private so callers must authenticate through `create`.

## Control Flow, State, and Persistence
The object inherits all socket/keepalive state from `KeptAliveServerConnection`; the header only constrains construction.

## Dependencies and Integration Points
Includes `common/server_connection.h` and `<memory>`. Mutating command implementations receive `std::unique_ptr<RegisteredAdminConnection>`.

## Risks and Test Signals
Risks include inherited connection behavior being exposed without extra authorization checks after creation. Build tests and authenticated command integration cover it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/registered_admin_connection.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/reload_config_command.cc -->
# sources/distributed-fs/lizardfs/src/admin/reload_config_command.cc

## Purpose
Implements `lizardfs-admin reload-config`, a privileged synchronous request for a metadata server to reload its configuration.

## Important APIs, Types, and Functions
Defines command methods. It sends `cltoma::adminReload::build()` and expects `LIZ_MATOCL_ADMIN_RELOAD`.

## Control Flow, State, and Persistence
`run` validates host/port, authenticates, sends reload, deserializes a status byte, prints the status string, and exits nonzero on failure. Server-side state changes by rereading configuration.

## Dependencies and Integration Points
Depends on `RegisteredAdminConnection`, admin reload protocol, and LizardFS error strings.

## Risks and Test Signals
Risks include a misleading wrong-usage message saying metadataserver while usage says master, deserializing the reload response via `matocl::adminStopWithoutMetadataDump::deserialize` rather than a reload-named function, direct `exit(1)`, and operational impact of reloading live configuration. Test signals are successful reload, rejected reload, bad password, malformed response, and config change taking effect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/reload_config_command.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/reload_config_command.h -->
# sources/distributed-fs/lizardfs/src/admin/reload_config_command.h

## Purpose
Declares the reload-config admin command.

## Important APIs, Types, and Functions
`ReloadConfigCommand` overrides `name`, `usage`, and `run`.

## Control Flow, State, and Persistence
No state is declared here.

## Dependencies and Integration Points
Includes base command header. Implementation uses authenticated admin protocol.

## Risks and Test Signals
Risk is declaration drift and live configuration side effects. Build plus authenticated integration tests are signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/reload_config_command.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/save_metadata_command.cc -->
# sources/distributed-fs/lizardfs/src/admin/save_metadata_command.cc

## Purpose
Implements `lizardfs-admin save-metadata`, requesting a metadata server to save current metadata to `metadata.mfs`.

## Important APIs, Types, and Functions
Defines command methods and supports `--async`. It sends `cltoma::adminSaveMetadata::build(async)` and deserializes `matocl::adminSaveMetadata`.

## Control Flow, State, and Persistence
`run` validates host/port, determines async mode, authenticates, sends the request, prints status, and exits nonzero on failure. In synchronous mode the server is expected to report completion status; in async mode it only reports task start. Server-side metadata persistence is the core effect.

## Dependencies and Integration Points
Depends on admin authentication, save-metadata protocol, and LizardFS error strings. It interacts with task management because async saves may create background work visible to list/stop tasks.

## Risks and Test Signals
Risks include direct `exit(1)`, operational load or failure while saving metadata, async semantics depending on server task state, and no porcelain/status-code output. Test signals are sync success/failure, async start when no save is running, async failure when already in progress, bad password, and actual metadata file creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/save_metadata_command.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/save_metadata_command.h -->
# sources/distributed-fs/lizardfs/src/admin/save_metadata_command.h

## Purpose
Declares the save-metadata admin command.

## Important APIs, Types, and Functions
`SaveMetadataCommand` overrides `name`, `usage`, `supportedOptions`, and `run`.

## Control Flow, State, and Persistence
No state is defined in the header.

## Dependencies and Integration Points
Includes the base command. Implementation uses authenticated metadata persistence protocol.

## Risks and Test Signals
Risk is declaration drift and async option compatibility. Build and live save tests cover it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/save_metadata_command.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/stop_master_without_saving_metadata.cc -->
# sources/distributed-fs/lizardfs/src/admin/stop_master_without_saving_metadata.cc

## Purpose
Implements `lizardfs-admin stop-master-without-saving-metadata`, a privileged fast-stop command that intentionally avoids saving metadata first.

## Important APIs, Types, and Functions
Defines methods for `MetadataserverStopWithoutSavingMetadataCommand`. It sends `cltoma::adminStopWithoutMetadataDump::build()` and deserializes status.

## Control Flow, State, and Persistence
`run` validates metadataserver host/port, authenticates, requests stop without metadata dump, prints status, and exits nonzero on failure. The server-side effect is stopping the metadata server without writing a fresh `metadata.mfs`.

## Dependencies and Integration Points
Depends on admin authentication, stop-without-metadata-dump protocol, and LizardFS error strings. It is related to HA migration and emergency operations.

## Risks and Test Signals
Risks are high: unsaved metadata may be lost if no current changelog/metalogger recovery path exists, and direct `exit(1)` bypasses main handling. Test signals are controlled stop in a test cluster, recovery from changelog/metalogger, bad password, server rejection, and behavior across master/shadow personalities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/stop_master_without_saving_metadata.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/stop_master_without_saving_metadata.h -->
# sources/distributed-fs/lizardfs/src/admin/stop_master_without_saving_metadata.h

## Purpose
Declares the stop-without-saving-metadata admin command.

## Important APIs, Types, and Functions
`MetadataserverStopWithoutSavingMetadataCommand` overrides `name`, `usage`, and `run`.

## Control Flow, State, and Persistence
No state is defined in the header.

## Dependencies and Integration Points
Includes `common/server_connection.h` and the base command; implementation uses authenticated admin protocol.

## Risks and Test Signals
Risk is the destructive operational semantics behind a small interface. Authenticated integration tests and recovery drills are signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/stop_master_without_saving_metadata.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/stop_task_command.cc -->
# sources/distributed-fs/lizardfs/src/admin/stop_task_command.cc

## Purpose
Implements `lizardfs-admin stop-task`, cancelling a currently running master task by ID.

## Important APIs, Types, and Functions
Defines command methods. It parses the task ID with `std::stoi(..., base 0)`, sends `cltoma::stopTask::build(msgid, task_id)`, and deserializes `matocl::stopTask`.

## Control Flow, State, and Persistence
`run` requires host, port, and task ID. Invalid task ID text prints an error and returns without nonzero status. After authentication it sends cancellation request and prints success or not-found text. The server-side effect is cancellation of matching background task.

## Dependencies and Integration Points
Depends on `RegisteredAdminConnection`, task protocol, and IDs shown by `list-tasks`.

## Risks and Test Signals
Risks include invalid ID returning success status from the process, `std::out_of_range` not caught, no nonzero exit on not-found status, direct protocol message ID fixed to zero, and operational side effects of cancelling tasks like metadata saves. Test signals are decimal/hex IDs, invalid and out-of-range IDs, successful cancellation, not-found status, bad password, and consistency with `list-tasks` output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/stop_task_command.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/stop_task_command.h -->
# sources/distributed-fs/lizardfs/src/admin/stop_task_command.h

## Purpose
Declares the stop-task admin command.

## Important APIs, Types, and Functions
`StopTaskCommand` overrides `name`, `usage`, and `run`.

## Control Flow, State, and Persistence
No state is declared here.

## Dependencies and Integration Points
Includes base command and `common/server_connection.h`; implementation uses authenticated task protocol.

## Risks and Test Signals
Risk is declaration drift and cancellation side effects. Build plus task lifecycle integration tests are signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/stop_task_command.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/cgi/CMakeLists.txt -->
# sources/distributed-fs/lizardfs/src/cgi/CMakeLists.txt

## Purpose
CMake install/configuration definition for LizardFS CGI UI scripts, server wrappers, and static assets.

## Important APIs, Types, and Functions
Uses `configure_file` to generate `mfscgiserv`, `lizardfs-cgiserver`, `chart.cgi`, and `mfs.cgi` from `.in` templates. Defines `CGI_FILES`, `CGI_SCRIPTS`, and `CGI_SERVERS`, then installs static files to `${CGI_SUBDIR}`, scripts to `${CGI_SUBDIR}`, and server programs to `${SBIN_SUBDIR}`.

## Control Flow, State, and Persistence
At configure time, placeholders such as paths and protocol base values are substituted. At install time, static assets and executable scripts become persistent package files.

## Dependencies and Integration Points
Depends on project variables like `CGI_SUBDIR`, `SBIN_SUBDIR`, `CGI_PATH`, `DATA_PATH`, and `PROTO_BASE`. It integrates with RPM service units that run `lizardfs-cgiserver`.

## Risks and Test Signals
Risks include generated scripts lacking executable permissions if install mode/macros are wrong, path substitution mismatches, deprecated `mfscgiserv` still installed, and Python version assumptions. Test signals are configured script shebangs/placeholders, installed execute bits, static asset availability, `chart.cgi` protocol constants, and systemd CGI service serving the installed root.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/cgi/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/cgi/cgiserv.py.in -->
# sources/distributed-fs/lizardfs/src/cgi/cgiserv.py.in

## Purpose
Deprecated Python 2 asynchronous HTTP/CGI server template installed as `mfscgiserv`. It serves static CGI UI files and executes `.cgi` scripts from a configured root, with legacy start/stop/restart/test lockfile management.

## Important APIs, Types, and Functions
Defines global `client_handlers`, `Server`, `ClientHandler`, `HTTP`, event `loop`, lock helpers `mylock` and `wdlock`, and a main block parsing `-H`, `-P`, `-R`, `-D`, `-t`, `-f`, and `-v`. `HTTP` implements request parsing, static response generation, CGI execution with `execfile`, CGI environment setup, redirects, error responses, and logging.

## Control Flow, State, and Persistence
Main prints a deprecation warning, parses options/mode, optionally daemonizes by double-fork with a pipe to the parent, obtains an exclusive lockfile under the data path, starts a nonblocking listening socket, and enters `select` loop. Each accepted client gets a handler that accumulates incoming request bytes, checks header/body completeness, builds a response, and writes chunks until closed or reset for keepalive. Lockfiles persist process PID text; daemon mode redirects stdio to `/dev/null`.

## Dependencies and Integration Points
Depends on Python 2 modules `fcntl`, `posix`, `urlparse`, `urllib`, `cStringIO`, sockets, and filesystem permissions. Generated placeholders include `@CGI_PATH@` and `@DATA_PATH@`. It serves generated `mfs.cgi`, `chart.cgi`, and static UI assets.

## Risks and Test Signals
Risks include Python 2 end-of-life, running CGI via `execfile` in-process with shared globals/environment/stdin/stdout, simplistic HTTP parsing, possible header parsing exceptions on malformed lines, path traversal reliance on `realpath` prefix checks, persistent-connection logic only enabling keepalive on explicit `Connection: keep-alive`, lockfile/PID race behavior, and deprecation drift from the Python 3 server. Test signals are start/stop/test/restart lock behavior, foreground/daemon modes, GET/HEAD/POST static and CGI requests, forbidden traversal, unreadable/non-executable files, malformed requests, and deprecation messaging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/cgi/cgiserv.py.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/cgi/chart.cgi.in -->
# sources/distributed-fs/lizardfs/src/cgi/chart.cgi.in

## Purpose
CGI proxy that requests chart data from a LizardFS backend service and returns image or timestamp payloads to the web UI.

## Important APIs, Types, and Functions
Defines substituted `PROTO_BASE`, packet command constants `CUTOAN_CHART` and `ANTOCU_CHART`, parsed CGI fields `host`, `port`, and `id`, helpers `mysend`, `myrecv`, and `handle_error`.

## Control Flow, State, and Persistence
The script validates host, port, and chart ID; on invalid input or any exception it returns `err.gif` from `DOCUMENT_ROOT`. On success it opens a socket to the requested host/port, sends a big-endian packet header with chart ID, reads response header and payload, and emits `Content-Type` based on GIF, PNG, or `timestamp` prefix. No state is persisted.

## Dependencies and Integration Points
Depends on Python 3 `cgi`, sockets, `struct`, `DOCUMENT_ROOT`, and the LizardFS chart protocol. It is executed by the CGI server and consumed by the web UI.

## Risks and Test Signals
Risks include user-controlled host/port enabling server-side request forgery from the CGI server, blocking socket operations without explicit timeout, `sys.stdout.write(bytes)` on a text stdout in Python 3 unless the CGI server's stdout wrapper accepts bytes, deprecated `cgi` module, and returning a generic error image for all failures. Test signals are valid GIF/PNG/timestamp responses, invalid parameters, backend timeout/refusal, unexpected command/length, malformed image data, missing `err.gif`, and execution under both installed CGI server wrappers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/cgi/chart.cgi.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/cgi/lizardfs-cgiserver.py.in -->
# sources/distributed-fs/lizardfs/src/cgi/lizardfs-cgiserver.py.in

## Purpose
Python 3 asynchronous HTTP/CGI server template installed as `lizardfs-cgiserver`, replacing the deprecated Python 2 `mfscgiserv`.

## Important APIs, Types, and Functions
Defines global `CLIENT_HANDLERS`, `Server`, `ClientHandler`, event `loop`, `HTTP`, `exit_err`, `fork`, `daemonize`, and a main block parsing `-v`, `-h`, `-H`, `-P`, `-R`, `-p`, and `-u`. `HTTP` handles request parsing, static files, `.cgi` execution with `exec(compile(...))`, CGI environment setup, redirects, errors, and logging. `HTTP.StrWritableBytesIO` adapts string writes to bytes for CGI scripts.

## Control Flow, State, and Persistence
Main configures host/port/root, creates the listening server, sets logging/root, optionally daemonizes with a PID file and user drop, then enters a `select` loop. Client handlers read bytes nonblocking, detect `\r\n\r\n`, parse request line/headers, read POST body into `sys.stdin`, build static or CGI responses, and stream bytes/file chunks. Daemon mode double-forks, changes to `/`, resets umask, redirects stdio, optionally switches user/group, and writes a PID file.

## Dependencies and Integration Points
Depends on Python 3 modules `datetime`, `getopt`, `io`, `mimetypes`, `pwd`, `select`, `socket`, `urllib.parse`, and filesystem permissions. It is launched by `lizardfs-cgiserv.service` and serves the generated CGI UI root.

## Risks and Test Signals
Risks include in-process CGI execution with shared interpreter state, global `os.environ`/`sys.stdin`/`sys.stdout` mutation per request, path traversal prevention depending on byte `realpath` prefix checks, malformed headers raising and returning 500/400, keepalive handling tied to explicit `Connection: keep-alive`, daemonization changing user after opening PID file but before forking, no TLS/authentication, and no request/body size limits. Test signals are static/CGI GET/HEAD/POST, traversal attempts, non-executable CGI rejection, malformed headers, large static file streaming, pidfile/user daemonization, systemd foreground mode, KeyboardInterrupt exit, and chart.cgi byte output under the stdout wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/cgi/lizardfs-cgiserver.py.in -->
