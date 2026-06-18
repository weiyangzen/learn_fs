# subset-b-009359 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/xutimes.c -->
# sources/test-tools/strace/tests/xutimes.c

Purpose: `xutimes.c` is a strace decoder test template for `utimes`-family syscalls, parameterized by `TEST_SYSCALL_NR`, `TEST_SYSCALL_STR`, and `TEST_STRUCT`. It drives the raw syscall with crafted pathname and timeval pointers, then prints the exact expected strace rendering.

Important APIs and control flow: `print_tv` formats `TEST_STRUCT` timestamp pairs with `zero_extend_signed_to_ull` and `print_time_t_usec`; `k_utimes` calls `syscall(TEST_SYSCALL_NR, pathname, times)` and stores `sprintrc(rc)` in file-static `errstr`; `main` allocates tail-guarded path and timeval storage, tests NULL, empty, valid, unterminated, inaccessible, invalid high-bit, out-of-range, invalid-usec, and valid timeval cases, then prints the synthetic trace lines.

State and persistence: state is only process-local test memory plus file-static `errstr`; no durable state is written. The test intentionally mutates the filename terminator and timeval contents between syscall attempts.

Dependencies and integration: depends on the strace test harness for `tail_memdup`, `TAIL_ALLOC_OBJECT_CONST_ARR`, `kernel_ulong_t`, `sprintrc`, `F8ILL_KULONG_SUPPORTED`, and time formatting helpers. It is compiled multiple ways by defining the syscall and struct macros.

Risks and test signals: correctness depends on exact kernel errno behavior, pointer fault layout, ABI-width extension, and timeval signedness. Strong signals are matching expected output for bad pointers, invalid microseconds, and printed decoded timestamps across native and compat ABIs.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/xutimes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/zeroargc.c -->
# sources/test-tools/strace/tests/zeroargc.c

Purpose: small strace test helper that executes a target program with `argc == 0`, allowing execve/argv edge-case tracing.

Important APIs and control flow: `main` requires at least one operand, treats `av[1]` as the executable path, overwrites `av[1]` with NULL, then calls `execve(path, av + 1, av + 2)`. On failure it reports through `perror_msg_and_fail`.

State and persistence: mutates only its inherited argument vector and then replaces the process image; no durable state.

Dependencies and integration: includes `tests.h` for harness diagnostics and standard `execve`. It is used by tests that need a real process image launched with an empty argv vector and controlled environment tail.

Risks and test signals: platform kernels/libcs may vary in tolerance for zero-argc exec. A successful test signal is that the target image sees no argv entries; failure output must preserve the target path for diagnosis.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/zeroargc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/.github/FUNDING.yml -->
# sources/test-tools/stress-ng/.github/FUNDING.yml

Purpose: GitHub funding metadata for the stress-ng project.

Important APIs and control flow: declarative YAML keys advertise GitHub Sponsors, Patreon, Ko-fi, and Liberapay identifiers. There is no executable control flow.

State and persistence: persisted as repository metadata consumed by GitHub UI.

Dependencies and integration: integrated only with GitHub's funding badge/sidebar handling.

Risks and test signals: risk is stale or mistyped sponsor identifiers. Test signal is GitHub rendering the expected funding links.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/.github/FUNDING.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/.github/workflows/ci-builds.yml -->
# sources/test-tools/stress-ng/.github/workflows/ci-builds.yml

Purpose: manually triggered GitHub Actions build matrix for stress-ng across Ubuntu GCC, Ubuntu clang/static analyzer, Ubuntu arm64, FreeBSD cross-build, macOS universal flags, and Cygwin.

Important APIs and control flow: `workflow_dispatch` inputs select platform substrings, optional package lists, make options, and quick-check options. Each job gates with `contains(github.event.inputs.platforms, ...)`, installs dependencies, checks out source, builds with `make`, runs `./stress-ng --version`, runs a short stress-ng check where native execution is possible, and uploads artifacts.

State and persistence: persists artifacts for 30 days; otherwise state is CI workspace-only.

Dependencies and integration: uses `actions/checkout@v4`, `actions/upload-artifact@v4`, `scan-build`, a smartmontools FreeBSD cross container, macOS toolchains, and `cygwin/cygwin-install-action`.

Risks and test signals: substring gating can unintentionally select platforms if names overlap; optional package input is shell-interpolated; Cygwin safe-directory handling is brittle. Signals are successful builds, analyzer report artifact, binary artifact upload, and quick check output.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/.github/workflows/ci-builds.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/.github/workflows/container-image-edge.yml -->
# sources/test-tools/stress-ng/.github/workflows/container-image-edge.yml

Purpose: builds and publishes multi-architecture edge container images on pushes to `master` and daily schedule, then scans the `latest` image.

Important APIs and control flow: the build job derives a lowercase image repository, checks out code, sets up QEMU/buildx, logs into GHCR and DockerHub, derives metadata, prints environment/limits, builds and pushes tags for SHA and `latest` across amd64, s390x, ppc64le, and arm64. The scan job runs Trivy and uploads SARIF.

State and persistence: publishes registry images and SARIF security scan results.

Dependencies and integration: uses Docker actions v2/v3/v4-era actions, GHCR package permissions, DockerHub secrets, Trivy, and CodeQL SARIF upload.

Risks and test signals: secrets are required for DockerHub; action versions are older; Trivy scans only GHCR `latest`; daily overwrite of `latest` means mutable deployment state. Signals are pushed image tags and uploaded SARIF.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/.github/workflows/container-image-edge.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/.github/workflows/container-image-stable.yml -->
# sources/test-tools/stress-ng/.github/workflows/container-image-stable.yml

Purpose: release-triggered workflow that publishes stable stress-ng container images.

Important APIs and control flow: on published release, it lowercases the repository name, checks out code, configures QEMU/buildx, authenticates to GHCR and DockerHub, computes Docker metadata, prints limits, and pushes SHA and `latest` tags for four Linux architectures.

State and persistence: creates long-lived registry tags tied to release commits and also overwrites `latest`.

Dependencies and integration: depends on GitHub Packages write permission, DockerHub credentials, and `docker/build-push-action`.

Risks and test signals: release publication can overwrite `latest`; no vulnerability scan is included unlike edge workflow; action versions are older. Signals are successful multi-platform manifest creation and registry push.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/.github/workflows/container-image-stable.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/.travis.yml -->
# sources/test-tools/stress-ng/.travis.yml

Purpose: legacy Travis CI recipe for Ubuntu focal builds with pedantic and verbose flags.

Important APIs and control flow: installs build-essential and numerous optional development libraries with `|| true`, then runs `make -j2 PEDANTIC=$PEDANTIC VERBOSE=$VERBOSE`.

State and persistence: CI workspace only; no artifacts declared.

Dependencies and integration: depends on Travis `language: c`, focal image, apt, and stress-ng Makefile feature detection.

Risks and test signals: YAML matrix syntax appears unusual (`- env` without colon) and optional installs can mask missing dependency coverage. Signal is a pedantic verbose build completing under Travis.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/.travis.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/Dockerfile -->
# sources/test-tools/stress-ng/Dockerfile

Purpose: multi-stage Debian 12 container build for a static stress-ng binary and minimal runtime image.

Important APIs and control flow: build stage installs compiler and optional libraries, adds repository as `stress-ng`, regenerates config, performs a static verbose parallel build, strips the binary, installs into `install-root`, then runtime stage copies that root and sets `ENTRYPOINT` to `/usr/bin/stress-ng` with `--help` default.

State and persistence: apt package cache and build outputs are transient to the build stage; installed binary/man/job assets persist in the final image.

Dependencies and integration: integrates with Makefile `Makefile.config`, `STATIC=1`, `DESTDIR` install, and container-image workflows.

Risks and test signals: `ADD .` can include unwanted context files; no apt cache cleanup in build stage is harmless for final size but affects build cache; static build depends on all static libs being available. Signal is an executable final image that prints stress-ng help.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/Makefile -->
# sources/test-tools/stress-ng/Makefile

Purpose: central stress-ng build, generation, packaging, installation, and test harness.

Important APIs and control flow: detects compiler family, kernel, architecture machine, and supported flags; applies optimization, hardening, sanitizer, LTO, static, small-build, pedantic, and verbose controls; enumerates headers, generated headers, core sources, generated core sources, and hundreds of stressor sources; generates `config.h`, `core-config.c`, `personality.h`, `io-uring.h`, `git-commit-id.h`, AppArmor data, and perf-event headers; compiles objects, links with C or C++ depending on Eigen support, and provides clean/test/dist/install/uninstall targets.

State and persistence: creates build artifacts (`*.o`, `stress-ng`, generated headers, config files, tarball, man gzip, PDF), installs under `DESTDIR`, and removes them through clean targets.

Dependencies and integration: relies on `Makefile.config`, `Makefile.machine`, compiler probes, optional libraries discovered in `config.h`, shell tools (`grep`, `sed`, `awk`, `od`, `gzip`, `tar`), AppArmor parser, git, and Debian test scripts.

Risks and test signals: large explicit source lists are easy to desynchronize; compiler probing via shell can be slow and environment-sensitive; generated headers introduce ordering dependencies; shell interpolation in flags requires trusted build inputs. Signals are `make`, `make config.h`, generated header freshness, quick/lite/slow/verify tests, and CI artifacts.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-affinity.c -->
# sources/test-tools/stress-ng/core-affinity.c

Purpose: CPU affinity parsing, application, migration, and usable-CPU enumeration for stress-ng.

Important APIs and control flow: `stress_affinity_parse_cpu` accepts comma tokens for numeric ranges, `odd`, `even`, `all`, `random`, and Linux topology selectors (`packageN`, `clusterN`, `dieN`, `coreN`); `stress_topology_set_get` reads sysfs topology CPU lists and deduplicates CPU sets; `stress_affinity_cpu_set` applies parsed affinity; `stress_affinity_change_cpu` changes worker CPU when `OPT_FLAGS_CHANGE_CPU` is set; `stress_affinity_cpus_get/free` allocates and releases usable CPU arrays.

State and persistence: stores the last applied process CPU set in file-static `stress_affinity_cpu_set_val`; changes kernel scheduler affinity for the current process but writes no files.

Dependencies and integration: gated by `sched_getaffinity`, `sched_setaffinity`, `cpu_set_t`, `/sys/devices/system/cpu`, random MWC helpers, global `g_opt_flags`, and CPU count helpers.

Risks and test signals: exits the process on invalid user input; assumes topology files exist and fit parser expectations; CPU_SETSIZE can truncate very large CPU numbers. Signals include parsing edge cases, topology selectors, affinity changes, and fallback behavior when affinity is unsupported.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-affinity.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-affinity.h -->
# sources/test-tools/stress-ng/core-affinity.h

Purpose: public affinity API declarations.

Important APIs and control flow: exposes CPU affinity setting, optional parser for `cpu_set_t`, CPU migration, usable CPU list allocation, and free helpers.

State and persistence: no state in the header; callers must free arrays returned by `stress_affinity_cpus_get`.

Dependencies and integration: includes `config.h` and relies on `stress_args_t`, `cpu_set_t`, `uint32_t`, and `bool` from the wider stress-ng include graph.

Risks and test signals: prototypes are conditionally visible for `HAVE_CPU_SET_T`; mismatched feature macros between translation units would break builds. Signal is successful compilation on affinity and non-affinity platforms.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-affinity.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-arch.c -->
# sources/test-tools/stress-ng/core-arch.c

Purpose: maps compile-time architecture macros to a human-readable architecture string.

Important APIs and control flow: `stress_arch_get` is a preprocessor `#if/#elif` chain returning strings such as `ARM`, `RISC-V`, `x86-64`, or `unknown`.

State and persistence: stateless.

Dependencies and integration: depends on `core-arch.h` architecture detection macros and is used in build/runtime reporting.

Risks and test signals: string accuracy depends on macro detection order; new architectures need both header macro and string branch. Signal is expected buildinfo/runtime architecture output.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-arch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-arch.h -->
# sources/test-tools/stress-ng/core-arch.h

Purpose: central compile-time architecture and endian detection header.

Important APIs and control flow: defines `STRESS_ARCH_*`, `STRESS_ARCH_LE/BE`, `STRESS_ARCH_X86`, opcode sizes and masks, and declares `stress_arch_get`. It also disables `HAVE_SIGALTSTACK` on HPPA.

State and persistence: compile-time macro state only.

Dependencies and integration: included by architecture assembly wrappers, CPU probes, cache helpers, and opcode generation.

Risks and test signals: detection relies on compiler predefined macros; ordering matters for PPC64 before PPC and x86 variants. Signal is correct conditional compilation on every supported architecture.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-arch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-asm-arm.h -->
# sources/test-tools/stress-ng/core-asm-arm.h

Purpose: ARM/AArch64 inline assembly wrappers for prefetch, yield, and memory barrier instructions.

Important APIs and control flow: conditionally defines `stress_asm_arm_prfm_*`, `stress_asm_arm_yield`, and `stress_asm_arm_dmb_sy` only when ARM architecture and feature probes are present.

State and persistence: no persistent state; operations affect CPU pipeline/cache ordering.

Dependencies and integration: relies on `core-arch.h`, `core-attribute.h`, and `HAVE_ASM_ARM_*` generated config macros.

Risks and test signals: invalid feature detection can cause assembler failures or illegal instructions. Signal is per-architecture compilation and successful stressors using prefetch/barrier helpers.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-asm-arm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-asm-generic.h -->
# sources/test-tools/stress-ng/core-asm-generic.h

Purpose: generic inline assembly no-op and compiler memory barrier helpers.

Important APIs and control flow: `stress_asm_nop` emits target no-op, with KVX bundle syntax and OpenRISC fallback; `stress_asm_mb` emits a compiler memory clobber; `stress_asm_nothing` emits empty asm.

State and persistence: none.

Dependencies and integration: included by stressors needing minimal instruction/pipeline effects; controlled by config macros.

Risks and test signals: assembly syntax must match target compiler; no-op semantics are intentionally minimal. Signal is compilation across supported compilers and expected use in microbenchmarks.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-asm-generic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-asm-loong64.h -->
# sources/test-tools/stress-ng/core-asm-loong64.h

Purpose: LoongArch64 inline wrappers for time counter, data barrier, and CPU config instructions.

Important APIs and control flow: provides `stress_asm_loong64_rdtime`, `stress_asm_loong64_dbar`, and `stress_asm_loong64_cpucfg` when corresponding feature macros exist.

State and persistence: no durable state; reads CPU state and applies memory ordering.

Dependencies and integration: depends on Loong64 architecture detection and generated assembler capability macros.

Risks and test signals: incorrect endian/assembler feature assumptions can break builds or runtime. Signal is Loong64-specific compile and stressor execution.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-asm-loong64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-asm-openrisc.h -->
# sources/test-tools/stress-ng/core-asm-openrisc.h

Purpose: OpenRISC synchronization instruction wrappers.

Important APIs and control flow: conditionally exposes `stress_asm_openrisc_msync` and `stress_asm_openrisc_psync` under `STRESS_ARCH_OR1K`.

State and persistence: no state; affects memory/pipeline synchronization.

Dependencies and integration: used by cache/memory fence shims and architecture-specific stressors.

Risks and test signals: requires correct assembler support macros. Signal is OpenRISC build coverage.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-asm-openrisc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-asm-ppc64.h -->
# sources/test-tools/stress-ng/core-asm-ppc64.h

Purpose: PowerPC/PPC64 inline wrappers for random number, cache, sync, and thread-priority hint instructions.

Important APIs and control flow: defines register-prefix handling for Apple/non-Apple assemblers; exposes PPC64 `darn`, `dcbst`, `dcbt`, `dcbtst`, `icbi`, `msync`, and PPC/PPC64 yield/mdoio/mdoom hint wrappers.

State and persistence: no durable state; instructions may flush/invalidate cache lines, sync memory, or influence hardware scheduling hints.

Dependencies and integration: used by cache flush/fence helpers and stressors needing PPC-specific instructions; gated by `STRESS_ARCH_PPC*` and `HAVE_ASM_PPC*` macros.

Risks and test signals: inline assembly constraints are architecture/compiler sensitive, especially register prefixes. Signal is successful PPC and PPC64 compilation plus stressor runtime coverage.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-asm-ppc64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-asm-ret.c -->
# sources/test-tools/stress-ng/core-asm-ret.c

Purpose: provides architecture-specific raw return-instruction opcode bytes for generated executable-code stressors.

Important APIs and control flow: initializes global `stress_ret_opcode` with stride, length, assembler mnemonic, and up to 8 opcode bytes based on architecture and endian macros; `stress_asm_ret_supported` returns success when bytes are available or logs unsupported architecture.

State and persistence: immutable global constant; no runtime mutation.

Dependencies and integration: depends on `core-arch.h` and `core-asm-ret.h`; consumed by stressors that synthesize callable return stubs.

Risks and test signals: wrong opcodes or endian variants can crash generated code; unsupported architectures return length zero. Signals are architecture-specific generated-call tests and graceful unsupported messages.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-asm-ret.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-asm-ret.h -->
# sources/test-tools/stress-ng/core-asm-ret.h

Purpose: declares the return-opcode data structure and support check.

Important APIs and control flow: defines `stress_ret_opcode_t`, `stress_ret_func_t`, global `stress_ret_opcode`, and `stress_asm_ret_supported`.

State and persistence: no header state; consumers read the global opcode constant from `core-asm-ret.c`.

Dependencies and integration: integrates generated executable code stressors with architecture opcode selection.

Risks and test signals: consumers must respect `len` and `stride` and call support checks. Signal is compile-time ABI compatibility and runtime code-generation tests.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-asm-ret.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-asm-riscv.h -->
# sources/test-tools/stress-ng/core-asm-riscv.h

Purpose: RISC-V inline wrappers for time, fences, pause, cache block operations, and Linux hardware probing.

Important APIs and control flow: defines CBO instruction encoding helpers, `rdtime`, `fence`, `fence.i`, encoded pause, optional `cbo.zero/flush/clean`, and Linux `riscv_hwprobe` helpers for Zicbom support and cache block size.

State and persistence: no persistent state; `riscv_hwprobe` reads kernel/hardware feature state and uses current affinity mask.

Dependencies and integration: depends on RISC-V architecture macros, optional `<asm/hwprobe.h>`, `syscall`, `sched_getaffinity`, and generated assembler macros.

Risks and test signals: manually encoded instructions must track ISA encoding and endian handling; hwprobe availability varies by kernel. Signals are RISC-V builds and feature-gated stressor behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-asm-riscv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-asm-s390.h -->
# sources/test-tools/stress-ng/core-asm-s390.h

Purpose: s390 timestamp clock helper.

Important APIs and control flow: `stress_asm_s390_stck` emits `stck` and returns the 64-bit tick value under `STRESS_ARCH_S390`.

State and persistence: stateless hardware read.

Dependencies and integration: used by time/cycle-sensitive stressors on s390.

Risks and test signals: assembler constraint correctness is the key portability risk. Signal is s390 compilation and timestamp-based stressor sanity.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-asm-s390.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-asm-sparc.h -->
# sources/test-tools/stress-ng/core-asm-sparc.h

Purpose: SPARC tick and memory barrier wrappers.

Important APIs and control flow: conditionally defines `stress_asm_sparc_tick` and `stress_asm_sparc_membar`.

State and persistence: no durable state; reads hardware tick and enforces store-load ordering.

Dependencies and integration: used by timing and cache/memory fence paths.

Risks and test signals: feature macros must reflect assembler and CPU support. Signal is SPARC build and runtime coverage for fence/tick users.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-asm-sparc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-asm-x86.h -->
# sources/test-tools/stress-ng/core-asm-x86.h

Purpose: x86 inline assembly layer for CPUID, timing, random, cache, fence, wait, prefetch, direct-store, and flags instructions.

Important APIs and control flow: provides PIC-safe `stress_asm_x86_cpuid`, locked add, pause/serialize, `rdtsc/rdtscp`, retry-loop `rdrand/rdseed`, `tpause/umwait/umonitor`, cache flush/demote/writeback/prefetch instructions, fences, `movdiri`, and `lahf`.

State and persistence: no persistent state; some helpers busy-wait until hardware random instructions report carry success and others affect cache or low-power wait behavior.

Dependencies and integration: heavily consumed by `core-cpu.c`, `core-cpu-cache.c`, config checks, and x86 stressors; gated by architecture, compiler, and `HAVE_ASM_X86_*` macros.

Risks and test signals: inline asm constraints, PIC `%ebx` preservation, illegal instruction hazards, and infinite wait on faulty RNG flags are key risks. Signals are x86 32/64 builds, CPUID feature tests, config LAHF check, and cache flush stressors.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-asm-x86.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-attribute.h -->
# sources/test-tools/stress-ng/core-attribute.h

Purpose: compiler attribute portability layer.

Important APIs and control flow: maps feature/version probes to macros such as `WARN_UNUSED`, `NORETURN`, `WEAK`, `PACKED`, `ALWAYS_INLINE`, `NOINLINE`, `OPTIMIZE*`, `ALIGNED`, `SECTION`, `CONST`, `PURE`, `MLOCKED_TEXT`, `FORMAT`, and `RETURNS_NONNULL`.

State and persistence: compile-time only.

Dependencies and integration: included by most low-level headers to express compiler hints without hard-coding GCC/Clang behavior.

Risks and test signals: version macro mistakes can cause unsupported attributes or missed optimization/safety diagnostics. Signal is clean compilation across GCC, Clang, ICC, PCC, musl-gcc, and platform targets.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-attribute.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-bitops.h -->
# sources/test-tools/stress-ng/core-bitops.h

Purpose: inline bit-manipulation primitives with builtin fallbacks.

Important APIs and control flow: provides reverse-bit functions for 8/16/32/64, byte swap, popcount, parity, and next-power-of-two helpers. Builtins are preferred when available; otherwise portable bit-twiddling implementations are used.

State and persistence: pure/stateless inline computations.

Dependencies and integration: used by stressors and helpers needing deterministic bit operations; depends on `core-attribute.h` and builtin feature macros.

Risks and test signals: `stress_bitops_nextpwr2(0)` wraps through unsigned arithmetic; fallback correctness depends on width assumptions. Signals are unit-style stressor self-checks and compiler warnings under pedantic builds.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-bitops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-builtin.h -->
# sources/test-tools/stress-ng/core-builtin.h

Purpose: broad portability shim that maps memory, complex math, scalar math, special functions, and rotate operations to compiler builtins, libc functions, intrinsics, or fallback expressions.

Important APIs and control flow: defines `shim_mem*`, `shim_strdup`, complex constructors, wrappers for pow/log/exp/trig/hyperbolic/Bessel/round/fabs/sqrt/fma families across float/double/long double and complex variants, plus rotate-left/right helpers for 8/16/32/64/128-bit values.

State and persistence: stateless macro/inline layer.

Dependencies and integration: included by core and stressor files to smooth compiler/libc differences; optionally includes `<x86intrin.h>`.

Risks and test signals: fallback math can have different precision/domain behavior from libc builtins; rotate helpers assume nonzero valid bit counts; macro wrappers can evaluate arguments in normal function-call form but still hide type conversions. Signals are successful builds against libcs missing long-double/complex functions and math stressor verification.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-builtin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-capabilities.c -->
# sources/test-tools/stress-ng/core-capabilities.c

Purpose: Linux capability/root privilege checking and capability dropping.

Important APIs and control flow: `stress_check_root` checks `geteuid` and Cygwin administrator groups; `stress_capabilities_getset` round-trips current capability sets; `stress_capabilities_check` checks requested permitted capability or root fallback; `stress_capabilities_drop` clears inheritable/permitted/effective capability bits through `capset` and enables `PR_SET_NO_NEW_PRIVS` when supported.

State and persistence: mutates current process credentials/capability state; no file persistence.

Dependencies and integration: uses Linux capability syscalls/headers, `prctl`, Cygwin `getgroups`, and stress-ng logging.

Risks and test signals: dropping capabilities is irreversible for the process; fallback-to-root semantics can over-approximate capabilities on non-Linux. Signals are privileged/unprivileged stressor gating and post-drop inability to regain privileges.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-capabilities.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-capabilities.h -->
# sources/test-tools/stress-ng/core-capabilities.h

Purpose: maps Linux capability constants to stress-ng `SHIM_CAP_*` names with root fallback.

Important APIs and control flow: defines `SHIM_CAP_IS_ROOT`, many POSIX/Linux capability aliases, and declares getset/check/drop functions. Missing capability macros map to `SHIM_CAP_IS_ROOT`.

State and persistence: compile-time mapping only.

Dependencies and integration: centralizes privilege checks for stressors requiring raw I/O, network admin, BPF, perf, sys_admin, and related permissions.

Risks and test signals: fallback to root may be coarser than actual platform permission model; new Linux capabilities require updates. Signal is correct compile on older headers and proper stressor skip/permission behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-capabilities.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-clocks.h -->
# sources/test-tools/stress-ng/core-clocks.h

Purpose: clock identifier compatibility header.

Important APIs and control flow: includes `<time.h>` and defines Linux `CLOCK_AUX` as 16 when absent.

State and persistence: compile-time only.

Dependencies and integration: used by clock-related stressors/helpers that need `CLOCK_AUX` even on older headers.

Risks and test signals: hard-coded clock IDs can diverge on unusual platforms. Signal is compilation and runtime handling of unsupported clocks.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-clocks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-clocksource.c -->
# sources/test-tools/stress-ng/core-clocksource.c

Purpose: warns once when Linux is using HPET clocksource because it may distort benchmarking.

Important APIs and control flow: `stress_clocksource_check` scans `/sys/devices/system/clocksource/clocksource*/current_clocksource`, lowercases contents, and logs a warning if the value starts with `hpet`; a static `warned` latch prevents repeated warnings.

State and persistence: process-local one-time warning flag; reads sysfs but does not write it.

Dependencies and integration: uses directory traversal, `stress_fs_file_read`, and logging; called from runtime configuration/performance checks.

Risks and test signals: assumes sysfs clocksource layout; warning can be skipped after first detection. Signal is a single warning on HPET systems and silence otherwise.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-clocksource.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-clocksource.h -->
# sources/test-tools/stress-ng/core-clocksource.h

Purpose: declares the clocksource performance check.

Important APIs and control flow: exposes `stress_clocksource_check`.

State and persistence: no header state.

Dependencies and integration: included by runtime code that wants to warn about HPET.

Risks and test signals: minimal; signal is successful linkage with `core-clocksource.c`.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-clocksource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-config-check.c -->
# sources/test-tools/stress-ng/core-config-check.c

Purpose: runtime system-configuration sanity checks and performance warnings.

Important APIs and control flow: when metrics are enabled on Linux, reads scheduler autogroup, CPU boost/turbo, and per-CPU scaling governors; always checks memory/swap pressure and suggests `--oom-avoid` when low; on x86-64, validates `lahf_lm` CPUID by installing a SIGILL handler and executing `lahf`.

State and persistence: reads `/proc`/`/sys`, installs/restores a signal handler temporarily, and uses a volatile flag for SIGILL detection. It does not persist settings.

Dependencies and integration: depends on global `g_opt_flags`, memory limit helpers, signal helpers, x86 asm/cpu helpers, terminal ioctl, and logging.

Risks and test signals: warnings are advisory and Linux-specific; signal-handler probing must restore prior handler; reading governors can race CPU hotplug. Signals are expected notes under powersave/low-memory/disabled boost and no crash on Rosetta-like LAHF mismatch.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-config-check.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-config-check.h -->
# sources/test-tools/stress-ng/core-config-check.h

Purpose: declares `stress_config_check`.

Important APIs and control flow: single runtime check entry point.

State and persistence: no header state.

Dependencies and integration: used by main runtime startup/config paths.

Risks and test signals: minimal; signal is successful linkage and invocation.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-config-check.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-cpu-cache.c -->
# sources/test-tools/stress-ng/core-cpu-cache.c

Purpose: discovers CPU cache topology/sizes and exposes cache query and flush helpers.

Important APIs and control flow: query path tries Linux sysfs cache indexes, auxv, x86 CPUID, and architecture fallbacks for SPARC, M68K, SH4, Alpha, RISC-V, OR1K, and Apple sysctl. Public helpers allocate full CPU cache details, find max cache level, retrieve cache by level/type, compute LLC or level sizes, free all allocations, and flush data cache using `clflushopt`, `clflush`, `__builtin___clear_cache`, or `shim_cacheflush`.

State and persistence: returns dynamically allocated cache structures owned by callers; reads sysfs/proc/device-tree/sysctl/CPUID but writes no durable state.

Dependencies and integration: depends on architecture headers, x86 asm, CPU feature checks, `stress_fs_*`, `scandir`, `getauxval`, sysctl helpers, and cache type structs from the header.

Risks and test signals: comments note an assumption of one data cache per CPU cache level; fallback data may be approximate; CPU hotplug and offline CPUs can affect discovery; allocation failures degrade to zero data. Signals are correct LLC/line-size values, leak-free `stress_cpu_cache_free`, and functioning cache flush paths.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-cpu-cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-cpu-cache.h -->
# sources/test-tools/stress-ng/core-cpu-cache.h

Purpose: cache data model, cache query API, cache flush shim, prefetch shim, and memory-fence shim declarations.

Important APIs and control flow: defines `stress_cpu_cache_type_t`, `stress_cpu_cache_t`, per-CPU and CPU-list structures, query/free/flush prototypes, `SHIM_ICACHE/DCACHE`, lazy x86 `shim_clflush`, prefetch fallback, and `shim_mfence` selecting OR1K/RISC-V/x86/PPC64/SPARC or `__sync_synchronize`.

State and persistence: static `shim_clflush_func` lazily switches from selector to real/no-op function in each translation unit including the header.

Dependencies and integration: pulls in architecture assembly headers and `core-cpu.h`; widely used by memory/cache stressors.

Risks and test signals: header-level static function pointer means per-translation-unit lazy state; fence selection depends on include-time macros. Signals are compile coverage and stressors observing expected cache/fence behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-cpu-cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-cpu-freq.c -->
# sources/test-tools/stress-ng/core-cpu-freq.c

Purpose: obtains average/min/max CPU frequency in GHz across supported platforms.

Important APIs and control flow: Linux scans `/sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq` and converts kHz to GHz; FreeBSD reads `dev.cpu.N.freq`; Apple reads `hw.cpufrequency`; OpenBSD reads `HW_CPUSPEED`; unsupported platforms zero all outputs.

State and persistence: reads kernel/sysctl state only.

Dependencies and integration: uses dirent scanning, sysctl helpers, CPU count helpers, and conversion constants.

Risks and test signals: current frequency can be unavailable, stale, or per-policy rather than per-core; Linux frees scan entries while iterating and handles no data by zeroing. Signals are nonzero plausible GHz on systems exposing frequency and zeros otherwise.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-cpu-freq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-cpu-freq.h -->
# sources/test-tools/stress-ng/core-cpu-freq.h

Purpose: declares `stress_cpu_freq_get`.

Important APIs and control flow: caller supplies output pointers for average, min, and max GHz.

State and persistence: no header state.

Dependencies and integration: used by metrics/buildinfo paths that report CPU frequency.

Risks and test signals: callers must pass valid pointers. Signal is successful linkage with platform implementation.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-cpu-freq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-cpu.c -->
# sources/test-tools/stress-ng/core-cpu.c

Purpose: x86 CPU identification, feature probing, DTLB sizing, and floating-point subnormal mode control.

Important APIs and control flow: `stress_cpu_is_x86` caches vendor/hypervisor CPUID detection; `STRESS_CPU_X86_HAS` generates per-feature cached CPUID helpers for clflush, waitpkg, rdseed, syscall, SSE, AVX/VNNI/AVX512, movdiri, serialize, and others; DTLB helpers decode CPUID descriptors/subleaves and may iterate CPUs by setting affinity; FP helpers toggle SSE DAZ/FTZ bits in MXCSR.

State and persistence: many function-local static caches store CPUID results; DTLB probing can temporarily mutate process affinity; FP helpers mutate current thread floating-point control state.

Dependencies and integration: depends on `core-arch.h`, `core-asm-x86.h`, `core-builtin.h`, scheduler affinity, and compiler intrinsics.

Risks and test signals: CPUID leaf assumptions vary on virtual/old CPUs; DTLB helper restores affinity to CPU 0 rather than the original mask; subnormal toggles affect IEEE behavior. Signals are feature-gated stressors using safe instruction paths and CPU feature reporting correctness.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-cpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-cpu.h -->
# sources/test-tools/stress-ng/core-cpu.h

Purpose: declares CPU feature, DTLB, and floating-point mode helpers.

Important APIs and control flow: exposes x86 feature booleans, DTLB entry query, and subnormal enable/disable functions.

State and persistence: no header state, but implementations cache and mutate CPU/FP state as documented in `core-cpu.c`.

Dependencies and integration: included by cache, x86 stressors, and config checks.

Risks and test signals: consumers must gate instruction use with the matching helper. Signal is compile/link and absence of illegal-instruction failures when used correctly.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-cpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-cpuidle.c -->
# sources/test-tools/stress-ng/core-cpuidle.c

Purpose: discovers CPU idle C-states, samples residency counters, and reports per-stressor idle residency.

Important APIs and control flow: `stress_cpuidle_init` scans Linux `/sys/devices/system/cpu/cpu*/cpuidle/state*`, builds a sorted unique linked list, and inserts C0/BUSY if needed; begin/end readers aggregate per-state `time` counters and wall-time samples; `stress_cpuidle_dump` computes percentages per stressor instance and emits text/YAML; `stress_cpuidle_log_info` logs discovered states.

State and persistence: owns process-global linked list `cpu_cstate_list` and length; begin/end mutate caller stats. Reads sysfs only.

Dependencies and integration: depends on stressor stats structures, YAML logging, time helpers, and Linux cpuidle sysfs.

Risks and test signals: counter units/availability vary; CPU hotplug can change state sets after init; residency over 100% is clamped as inaccurate. Signals are discovered C-state logging, sane YAML output, and no leaks after `stress_cpuidle_free`.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-cpuidle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-cpuidle.h -->
# sources/test-tools/stress-ng/core-cpuidle.h

Purpose: C-state data structure and cpuidle API declarations.

Important APIs and control flow: defines linked-list node `cpu_cstate_t` and exposes init/free/log/head/read/dump functions.

State and persistence: no header-owned state; implementation owns global list.

Dependencies and integration: uses `stress_cstate_stats_t`, `stress_list_item_t`, and `FILE` from stress-ng headers.

Risks and test signals: callers must initialize before reading/dumping and free at shutdown. Signal is correct lifecycle use in stress-ng metrics paths.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-cpuidle.h -->
