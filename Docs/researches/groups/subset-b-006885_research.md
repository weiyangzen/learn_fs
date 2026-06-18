# subset-b-006885 research

Grouped research for the requested kselftest sources under `sources/distributed-fs/ceph-client/tools/testing/selftests/`. Each section is bounded for reconciliation into the source-tree-aligned per-file report path.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/seccomp/seccomp_bpf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/seccomp/seccomp_bpf.c

## Purpose
Large kselftest harness for Linux seccomp classic-BPF behavior. It validates strict mode, filter mode, BPF return action semantics, filter stacking precedence, ptrace/seccomp interactions, thread synchronization, seccomp user notifications, notification fd operations, and uprobe/uretprobe interaction on supported architectures. It is intentionally broad because seccomp behavior is ABI-facing and must stay compatible across libc and kernel header versions.

## Important APIs, types, and functions
The file wraps raw `seccomp()` when libc lacks it and supplies compatibility definitions for `SECCOMP_RET_*`, `SECCOMP_FILTER_FLAG_*`, `struct seccomp_notif`, `struct seccomp_notif_resp`, `struct seccomp_notif_addfd`, `struct seccomp_metadata`, and arch syscall numbers. BPF programs are represented with `struct sock_filter` and `struct sock_fprog`. Important helpers include `filecmp()` over `kcmp()`, `kill_thread_or_group()`, ptrace fixture helpers `start_tracer()`, `setup_trace_fixture()`, `teardown_trace_fixture()`, arch register helpers `get_syscall()`, `change_syscall_nr()`, `change_syscall_ret()`, `user_notif_syscall()`, proc parsers `get_nth()`, `get_proc_stat()`, and `get_proc_syscall()`.

## Control flow
The file is organized as kselftest harness `TEST`, `TEST_SIGNAL`, `FIXTURE`, and `TEST_F` cases. Early tests validate basic mode entry, `NO_NEW_PRIVS`, empty/oversized filters, and kill/errno/trap actions. The precedence fixture installs multiple filters in different orders and confirms action priority is independent of installation order except for action data. Trace tests fork a tracer, attach with `PTRACE_O_TRACESECCOMP` or `PTRACE_SYSCALL`, modify syscall numbers/returns, and verify redirected, faked, skipped, or killed syscalls. TSYNC tests start sibling threads with optional diverged filter trees and validate synchronized installation, failure TID reporting, `TSYNC_ESRCH`, and dead thread-leader behavior. User notification tests install `SECCOMP_RET_USER_NOTIF` filters, receive and send notification ioctls, inject fds with `SECCOMP_IOCTL_NOTIF_ADDFD`, validate pid namespace reporting, signal interruption, listener shutdown, FIFO ordering, and wait-killable behavior. Final uprobe tests optionally attach perf uprobes to local functions and verify seccomp filters around the internal uprobe syscalls.

## State and persistence
Most state is per-process test state: installed seccomp filters are irreversible for the task, so tests isolate destructive cases in harness signal tests, forks, or fixtures. Shared state includes pipes, socketpairs, pthread condition variables, semaphores, listener fds, forked children, and global variables such as `tracer_running` and `handled`. No persistent files are written by the test, but it reads `/proc/<pid>/stat`, `/proc/<pid>/syscall`, `/proc/self/maps`, `/sys/bus/event_source/devices/uprobe/*`, and may depend on open fd identity.

## Dependencies and integration points
Integrates with `kselftest_harness.h`, clone3 selftest helpers, Linux seccomp, ptrace, BPF, perf event, capability, pthread, signal, namespace, and procfs APIs. Some tests require root or capabilities (`CAP_SYS_ADMIN`, checkpoint/restore ptrace metadata), kernel options such as `CONFIG_SECCOMP_FILTER`, `CONFIG_KCMP`, `CONFIG_PID_NS`, `CONFIG_CHECKPOINT_RESTORE`, and arch support for ptrace register access and uprobe syscall numbers.

## Risks
The file intentionally kills threads/processes and installs irreversible filters, so incorrect isolation can terminate a test process early. Several checks are timing-sensitive around signals, process states, notification wakeups, and poll timeouts. Architecture register abstractions are fragile when syscall ABI details change. User notification tests depend on exact errno semantics and kernel cleanup timing. Some loops spin until process state changes and can be flaky on overloaded systems.

## Test signals
Pass signals come from harness assertions, expected `SIGSYS`/`SIGKILL` terminations, exact errno values such as `EACCES`, `EINVAL`, `EFAULT`, `EOPNOTSUPP`, `ENOENT`, `EMFILE`, and child exit status checks. Skip signals cover missing kernel features, missing clone3, missing namespaces, missing root/capabilities, missing uprobe support, and unsupported ptrace metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/seccomp/seccomp_bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sgx/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/sgx/Makefile

## Purpose
Builds the x86_64 SGX selftest host binary and test enclave image. It gates the build with `../x86/check_cc.sh` so SGX tests are only generated when a 64-bit x86 program can be compiled.

## Important APIs, types, and functions
Defines `TEST_CUSTOM_PROGS := $(OUTPUT)/test_sgx` and `TEST_FILES := $(OUTPUT)/test_encl.elf`. Host objects are `main.o`, `load.o`, `sigstruct.o`, `call.o`, and `sign_key.o`, linked with `-lcrypto` and no executable stack. The enclave is built from `test_encl.c` and `test_encl_bootstrap.S` using freestanding static PIE flags and linker script `test_encl.lds`.

## Control flow
When `CAN_BUILD_X86_64` is true, `all` builds both the host runner and enclave ELF. Individual object rules compile host/enclave sources into `$(OUTPUT)`. `OBJCOPY` defaults to cross objcopy but is not directly used in the visible rules.

## State and persistence
Writes only build outputs under `$(OUTPUT)` and lists them in `EXTRA_CLEAN`. It does not persist runtime state.

## Dependencies and integration points
Uses kselftest `../lib.mk`, kernel headers via `tools/include`, OpenSSL libcrypto, x86 compiler checks, and SGX linker assets in the same directory.

## Risks
The freestanding enclave flags and `-Werror` make the build sensitive to compiler and OpenSSL deprecation warnings; `sigstruct.c` locally suppresses OpenSSL 3 deprecation warnings. Cross-compile environments need a matching x86_64 toolchain.

## Test signals
Successful build produces `test_sgx` and `test_encl.elf`; unsupported architecture produces no SGX test binary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sgx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sgx/call.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/sgx/call.S

## Purpose
Provides `sgx_enter_enclave`, an assembly wrapper around the vDSO `__vdso_sgx_enter_enclave` entry point that preserves callee-saved registers for unclobbered-call tests.

## Important APIs, types, and functions
Exports global symbol `sgx_enter_enclave`. It references `vdso_sgx_enter_enclave` through RIP-relative addressing and follows the x86_64 calling convention plus the SGX vDSO extra stack arguments.

## Control flow
The wrapper pushes `r15`, `r14`, `r13`, `r12`, and `rbx`, prepares two stack slots expected by the vDSO call path, calls the function pointer, then restores stack and registers before returning.

## State and persistence
No persistent state. Runtime state is the user register frame and stack frame around the vDSO call.

## Dependencies and integration points
Linked into `test_sgx` and used by `ENCL_CALL(..., clobbered=false)` in `main.c`. Requires `main.c` to resolve `vdso_sgx_enter_enclave`.

## Risks
Any ABI mismatch with the vDSO prototype or stack layout can corrupt register state or mis-enter the enclave. The wrapper is x86_64-specific.

## Test signals
The `unclobbered_vdso` tests verify this path by entering the enclave, writing a magic value, reading it back, and expecting clean `EEXIT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sgx/call.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sgx/defines.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/sgx/defines.h

## Purpose
Shared SGX selftest definitions for page sizing, compiler attributes, kernel SGX UAPI inclusion, and host/enclave operation payloads.

## Important APIs, types, and functions
Defines `PAGE_SIZE`, `PAGE_MASK`, `__aligned`, `__packed`, `__used`, and `__section`. Includes SGX architecture and UAPI headers. `enum encl_op_type` enumerates operations executed inside the enclave: buffer get/put, arbitrary address get/put, no-op, `EACCEPT`, `EMODPE`, and TCS initialization. The `struct encl_op_*` payloads share `struct encl_op_header`.

## Control flow
This header has no executable flow; `main.c` populates operation structs and `test_encl.c` dispatches by `header.type`.

## State and persistence
Operation structures carry transient command state across enclave entry. `ret` in `struct encl_op_eaccept` is written by enclave code and read by host tests.

## Dependencies and integration points
Central contract between host test code, enclave C code, and assembly bootstrap. It also imports kernel SGX constants such as page types and ENCLU function encodings.

## Risks
The host/enclave ABI depends on exact struct layout and 64-bit fields. Header path depth is tied to this Linux source tree layout.

## Test signals
Every SGX runtime test indirectly validates these definitions when operation dispatch succeeds and expected magic values or ENCLU return codes are observed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sgx/defines.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sgx/load.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/sgx/load.c

## Purpose
Loads the test enclave ELF, prepares SGX segment metadata, creates an enclave through `/dev/sgx_enclave`, adds pages, and initializes the enclave with a generated signature.

## Important APIs, types, and functions
`encl_delete()` releases enclave mappings, binary mapping, fd, heap, and segment table. `encl_map_bin()` maps `test_encl.elf`. `encl_ioc_create()` issues `SGX_IOC_ENCLAVE_CREATE`. `encl_ioc_add_pages()` issues `SGX_IOC_ENCLAVE_ADD_PAGES` with `SGX_PAGE_MEASURE` when needed. `encl_get_entry()` scans ELF `SHT_SYMTAB`/`SHT_STRTAB` for a symbol value. `encl_load()` parses program headers into `struct encl_segment` entries and appends an anonymous heap segment. `encl_map_area()` reserves an aligned power-of-two enclave virtual range. `encl_build()` creates, adds, and initializes the enclave with `SGX_IOC_ENCLAVE_INIT`.

## Control flow
`encl_load()` opens `/dev/sgx_enclave`, sanity-checks readable and executable mappings of the device, maps the enclave ELF, counts `PT_LOAD` segments plus a heap, translates ELF flags to VMA protections and SGX SECINFO flags, computes source size, and rounds enclave size up to a power of two. `encl_build()` maps an aligned address window, creates SECS, adds all segments before userspace VMAs are mapped, then initializes using `encl->sigstruct`.

## State and persistence
All state is contained in `struct encl`: device fd, ELF mapping, segment table, source and enclave sizes, base address, SECS, and SIGSTRUCT. Kernel enclave state persists only for the lifetime of the fd/mappings and is cleaned by `encl_delete()`.

## Dependencies and integration points
Depends on ELF layout produced by the SGX Makefile and linker script, Linux SGX UAPI ioctls, `main.h` structures, and `sigstruct.c` populating `encl->sigstruct` before `encl_build()`.

## Risks
Segment parsing assumes the first RW `PT_LOAD` is TCS and computes offsets from a shared source base. Device `PROT_EXEC` mapping fails on noexec `/dev`, and the diagnostic explicitly points to remounting. Partial cleanup paths must avoid double-closing fd 0, since `encl->fd` is treated as truthy.

## Test signals
Failures print device, ELF, mmap, or ioctl errors. Higher-level SGX tests fail at setup if load, measure, build, or vDSO symbol resolution does not complete.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sgx/load.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sgx/main.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/sgx/main.c

## Purpose
Host-side SGX selftest runner. It builds and enters a small test enclave, validates vDSO entry behavior, TCS selection, PTE and EPCM permission transitions, SGX2 page augmentation/removal/type changes, and error reporting through `struct sgx_enclave_run`.

## Important APIs, types, and functions
Key helpers include vDSO dynamic table/symbol functions (`vdso_get_dyntab()`, `vdso_get_dyn()`, `vdso_get_symtab()`, `vdso_symtab_get()`), SGX2/EPC helpers (`sgx2_supported()`, `get_total_epc_mem()`), enclave offset helpers (`encl_get_tcs_offset()`, `encl_get_data_offset()`), and `setup_test_encl()`. The `ENCL_CALL` macro chooses preserved-register wrapper or raw vDSO call; `EXPECT_EEXIT` validates clean enclave exits. Tests use Linux SGX ioctls `SGX_IOC_ENCLAVE_RESTRICT_PERMISSIONS`, `SGX_IOC_ENCLAVE_MODIFY_TYPES`, and `SGX_IOC_ENCLAVE_REMOVE_PAGES`.

## Control flow
Every test initializes an enclave with `setup_test_encl()`, which loads, measures, builds, maps each segment with its intended protection, and discovers `__vdso_sgx_enter_enclave`. Basic tests write/read magic values through enclave operations and exercise clobbered versus unclobbered vDSO calls. Permission tests first prove normal access, then change PTE or EPCM permissions and expect specific page fault vectors/error codes before restoring access by `mprotect()` or enclave-side `EMODPE`. Augmentation tests map unused enclave address space, trigger or preemptively accept EAUG pages via enclave `EACCEPT`, and verify read/write. TCS creation adds stack/TCS/SSA pages, initializes a TCS page inside the enclave, changes its type to TCS, enters through it, then removes/reuses pages. Removal tests validate correct failure without `EACCEPT`, invalid access after trim, invalid access after accept without final removal, and successful removal of an untouched page.

## State and persistence
`FIXTURE(enclave)` owns `struct encl` and `struct sgx_enclave_run`. Enclave memory, SGX page types, pending/modified/trim states, exception fields, and selected TCS are runtime state. No persistent disk state is written beyond build artifacts; the test maps `/proc/self/maps` only for diagnostics in setup failure.

## Dependencies and integration points
Depends on `load.c`, `sigstruct.c`, `call.S`, `test_encl.elf`, Linux SGX vDSO, `/dev/sgx_enclave`, CPUID SGX leaves, SGX2 hardware and kernel ioctl support for dynamic tests, and `kselftest_harness.h`.

## Risks
SGX tests are hardware-, firmware-, kernel-, and mount-policy-sensitive. Oversubscription/removal can take a long time and has a 900-second timeout. The tests rely on exact SGX page fault error codes, enclave size power-of-two rules, and fixed segment ordering. Dynamic page flows must use a second TCS after AEX in some cases to repair state safely.

## Test signals
Expected pass signals include clean `EEXIT`, zero exception fields, exact magic value round trips, ioctl counts equal to requested lengths, and specific page fault vectors/error codes such as `14`, `0x7`, `0x8007`, and `0x8005`. Skip signals cover missing SGX2, unsupported ioctls (`ENOTTY`), unsupported hardware (`ENODEV`), and kernels without initialized-enclave page addition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sgx/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sgx/main.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/sgx/main.h

## Purpose
Declares shared host-side SGX data structures and function prototypes used across enclave loading, measuring, building, signing, and entry.

## Important APIs, types, and functions
`struct encl_segment` records source pointer, enclave offset, size, VMA protections, SGX flags, and measurement participation. `struct encl` owns the SGX fd, mapped binary, source/enclave sizing, base address, segment table, SECS, and SIGSTRUCT. Prototypes expose `encl_delete()`, `encl_load()`, `encl_measure()`, `encl_build()`, `encl_get_entry()`, and `sgx_enter_enclave()`. It also exports the embedded signing key range.

## Control flow
This header has no runtime flow but defines the object passed from `load.c` to `sigstruct.c` and `main.c`.

## State and persistence
`struct encl` is the central in-memory state container for one test enclave lifetime.

## Dependencies and integration points
Includes SGX UAPI types through `defines.h`; integrates assembly symbols from `sign_key.S` and `call.S`.

## Risks
Struct fields mix file offsets, sizes, pointers, and enclave virtual addresses; wrong units or truncation would break SGX ioctls. `off_t encl_base` stores an address and therefore assumes sufficient width.

## Test signals
All SGX tests validate this contract indirectly through setup and cleanup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sgx/main.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sgx/sign_key.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/sgx/sign_key.S

## Purpose
Embeds the PEM private signing key into the host test binary as read-only data for SIGSTRUCT generation.

## Important APIs, types, and functions
Defines global symbols `sign_key` and `sign_key_end` around `.incbin "sign_key.pem"`.

## Control flow
No executable control flow.

## State and persistence
The key bytes are immutable `.rodata` in `test_sgx`. `sigstruct.c` computes the range length from the two symbols.

## Dependencies and integration points
Consumed by `gen_sign_key()` in `sigstruct.c`; requires `sign_key.pem` to be available at assembly time.

## Risks
Missing or malformed PEM breaks enclave measurement/signing. The key is a test key and should not be treated as production secret material.

## Test signals
OpenSSL PEM parsing failure causes SGX setup failure before enclave initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sgx/sign_key.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sgx/sigstruct.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/sgx/sigstruct.c

## Purpose
Computes SGX enclave measurement (`MRENCLAVE`) and populates a test `sgx_sigstruct` signed by the embedded RSA key.

## Important APIs, types, and functions
OpenSSL helpers allocate and free `q1q2_ctx`, reverse byte order, calculate Q1/Q2 values for SGX signature verification, drain crypto errors, and parse the RSA key from `sign_key`. Measurement helpers model ECREATE, EADD, and EEXTEND records using `mrenclave_ecreate()`, `mrenclave_eadd()`, `mrenclave_eextend()`, and `mrenclave_segment()`. Public entry `encl_measure()` fills SIGSTRUCT headers, attributes, modulus, mrenclave, signature, q1, and q2.

## Control flow
`encl_measure()` clears the sigstruct, seeds SGX header constants, loads the RSA key, initializes SHA256 measurement, commits ECREATE based on source size, iterates all enclave segments and pages, extends measured pages, finalizes `mrenclave`, hashes the header/body payload, signs it with RSA/SHA256, calculates Q1/Q2, and converts signature/modulus from big-endian to little-endian SGX layout.

## State and persistence
State is transient OpenSSL `BIGNUM`, `BN_CTX`, `EVP_MD_CTX`, `RSA`, digest buffers, and the output `encl->sigstruct`. No files are written.

## Dependencies and integration points
Depends on OpenSSL legacy RSA APIs, SGX UAPI struct layouts, the embedded key from `sign_key.S`, and segment metadata from `load.c`.

## Risks
OpenSSL 3 deprecations are suppressed; future API removal could break build. Measurement correctness depends on 64-byte record sizes, page iteration, byte-order conversions, and exact SGX struct packing. Unmeasured heap pages are intentionally added but skipped for EEXTEND.

## Test signals
Any crypto, measurement, signing, Q1/Q2, or digest-size failure makes `setup_test_encl()` fail, causing SGX tests to abort with initialization diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sgx/sigstruct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sgx/test_encl.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/sgx/test_encl.c

## Purpose
Implements the code that runs inside the test enclave. It is a tiny freestanding command dispatcher used by host SGX tests to read/write enclave memory and execute SGX2 ENCLU operations.

## Important APIs, types, and functions
Defines a page-aligned initialized `encl_buffer`, ENCLU function IDs, and operation handlers: `do_encl_emodpe()`, `do_encl_eaccept()`, `do_encl_init_tcs_page()`, buffer/address get/put helpers, and no-op. Freestanding local `memcpy()` and `memset()` avoid libc. `encl_body()` dispatches through `encl_op_array`.

## Control flow
On entry, `encl_body()` receives an operation pointer, checks that the operation type is in range, and calls the matching handler. Memory handlers copy magic values between operation structs and enclave memory. `EACCEPT` and `EMODPE` build `sgx_secinfo` and call ENCLU helpers. TCS initialization writes the TCS page fields needed for dynamic TCS tests.

## State and persistence
The static `encl_buffer` persists for the life of the enclave and is used for host-visible round trips. Handlers mutate operation structs and target enclave pages.

## Dependencies and integration points
Compiled into `test_encl.elf` with `test_encl_bootstrap.S`; uses operation layouts from `defines.h` and ENCLU helpers from kernel SGX headers.

## Risks
Freestanding code has no runtime safety net. Host-provided addresses are trusted, so invalid operations intentionally produce enclave exceptions observed by host tests. TCS layout writes must match SGX hardware expectations.

## Test signals
Host tests observe successful magic value round trips, `eaccept_op.ret == 0`, clean `EEXIT`, or expected exception fields after invalid memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sgx/test_encl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sgx/test_encl_bootstrap.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/sgx/test_encl_bootstrap.S

## Purpose
Defines the enclave TCS pages, SSA pages, stacks, entry sequence, dynamic TCS entry, and EEXIT path for the SGX test enclave.

## Important APIs, types, and functions
Uses raw ENCLU encoding. Defines `.tcs` data for two initial TCS pages, `encl_entry`, `encl_dyn_entry`, `encl_entry_core`, SSA storage, and two stacks. Calls C function `encl_body`.

## Control flow
On enclave entry, the bootstrap derives the stack address from the TCS base in `rbx`, switches to the enclave stack, saves the caller return address after EENTER, calls `encl_body`, restores the caller stack, loads the EEXIT target into `rbx`, and executes ENCLU[EEXIT]. `encl_dyn_entry` supports dynamically created TCS pages whose stack is directly before the TCS.

## State and persistence
TCS, SSA, and stack pages are enclave pages initialized in the ELF and then measured/loaded by host code. Runtime stack and SSA state persist within enclave memory.

## Dependencies and integration points
Linked into `test_encl.elf` and relied on by `main.c` TCS tests and `test_encl.c` handlers.

## Risks
Bootstrap intentionally omits production-grade register cleansing and ABI initialization. TCS field offsets, stack derivation, and ENCLU register conventions must remain exact.

## Test signals
`tcs_entry` validates both initial TCS pages; `tcs_create` validates the dynamic entry path after creating a new TCS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sgx/test_encl_bootstrap.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/signal/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/signal/Makefile

## Purpose
Builds signal selftest programs `mangle_uc_sigmask` and `sas`.

## Important APIs, types, and functions
Sets `CFLAGS = -Wall`, appends two `TEST_GEN_PROGS`, and includes `../lib.mk`.

## Control flow
The kselftest build system compiles each listed C file into a generated test program.

## State and persistence
Only build artifacts under `$(OUTPUT)` are produced.

## Dependencies and integration points
Integrates with common kselftest `lib.mk` and the local C sources.

## Risks
Simple Makefile; risk is mainly missing compiler warnings due to non-`-Werror` behavior or architecture-specific stack pointer header support.

## Test signals
Successful build emits two runnable signal tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/signal/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/signal/current_stack_pointer.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/signal/current_stack_pointer.h

## Purpose
Provides a portable `sp` register variable for reading the current stack pointer in signal tests.

## Important APIs, types, and functions
Declares `register unsigned long sp asm("...")` for alpha, arm, aarch64, csky, m68k, mips, riscv, i386, loongarch64, powerpc, s390x, sh, x86_64, and xtensa.

## Control flow
Preprocessor architecture selection chooses the correct register name or emits a compile-time error.

## State and persistence
No persisted state; `sp` reflects the current execution stack pointer when read.

## Dependencies and integration points
Used by `sas.c` to confirm a signal handler is executing on the alternate signal stack.

## Risks
Unsupported architectures fail compilation until a register mapping is added. Compiler behavior for global register variables is architecture-sensitive.

## Test signals
`sas.c` fails if `sp` is not within the expected altstack address range during `SIGUSR1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/signal/current_stack_pointer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/signal/mangle_uc_sigmask.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/signal/mangle_uc_sigmask.c

## Purpose
Tests signal mask semantics around delivered versus blocked signals and verifies that editing `ucontext_t.uc_sigmask` inside a handler updates the thread's blocked signal mask after handler return.

## Important APIs, types, and functions
Uses `sigaction()`, `raise()`, `sigismember()`, `sigaddset()`, `sigprocmask()`, and kselftest output helpers. Handlers are `handler_usr()`, `handler_segv()`, and `handler_verify_ucontext()`.

## Control flow
`main()` installs a `SIGUSR1` handler that blocks `SIGSEGV`, installs a `SIGSEGV` handler, raises `SIGUSR1`, and checks seven planned results. `handler_usr()` raises `SIGSEGV` and nested `SIGUSR1` signals while proving they are blocked until handler return, checks the interrupted-context mask is initially empty for those signals, then adds `SIGUSR2` to `uc_sigmask`. Later `handler_verify_ucontext()` confirms `SIGUSR2` is blocked in the saved context and cannot be delivered. `sigprocmask()` finally confirms `SIGUSR2` is in the live blocked set.

## State and persistence
Global `cnt` tracks recursive `SIGUSR1` delivery. Signal masks are process/thread state modified by kernel signal return from the mangled ucontext.

## Dependencies and integration points
Depends on POSIX signals, `ucontext_t`, and `kselftest.h`.

## Risks
Standard signals are not queued, which is intentionally tested and can be confusing when interpreting recursion count. Incorrect handler flags or masks can terminate the process.

## Test signals
Seven kselftest results cover SIGSEGV delivery, SIGUSR1 recursion count, ucontext mask contents, `SIGUSR2` blocking, and final blocked-mask verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/signal/mangle_uc_sigmask.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/signal/sas.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/signal/sas.c

## Purpose
Tests `sigaltstack(SS_ONSTACK | SS_AUTODISARM)` behavior and verifies `swapcontext()` can be used safely from a signal handler without reusing/corrupting the altstack.

## Important APIs, types, and functions
Uses `sigaltstack()`, `sigaction()`, `mmap(MAP_STACK)`, `getauxval(AT_MINSIGSTKSZ)`, `getcontext()`, `makecontext()`, `swapcontext()`, `setcontext()`, `raise()`, and the `sp` register from `current_stack_pointer.h`. Signal handlers are `my_usr1()` and `my_usr2()`; `switch_fn()` runs on a user context stack.

## Control flow
`main()` sizes and maps an altstack, confirms initial disabled state, enables `SS_AUTODISARM`, builds a user context, and raises `SIGUSR1`. `my_usr1()` verifies the stack pointer is on the signal stack, plants sentinel data, confirms `sigaltstack()` reports disabled while in the handler, then swaps to `uc`. `switch_fn()` raises `SIGUSR2`, whose handler searches for and would corrupt reused stack data, then returns to the saved signal context. After handler completion, `main()` verifies the altstack is back to `SS_AUTODISARM`.

## State and persistence
Global stack pointers, sizes, and contexts hold the alternate stack and user stack for one process lifetime. Sentinel data on the altstack is the corruption detector.

## Dependencies and integration points
Depends on architecture stack pointer mapping, auxv `AT_MINSIGSTKSZ`, POSIX ucontext APIs, and kselftest.

## Risks
If kernel lacks `SS_AUTODISARM`, the test skips after one planned result. ucontext APIs are deprecated on some libc targets but still used for this kernel behavior test. Stack size and pointer checks are architecture-sensitive.

## Test signals
Expected pass results: initial altstack disabled, altstack disabled inside handler due to autodisarm, and altstack still `SS_AUTODISARM` after signal. Failures include stack pointer outside altstack or sentinel corruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/signal/sas.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/size/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/size/Makefile

## Purpose
Builds the minimal `get_size` runtime memory selftest as a static freestanding program without startup files.

## Important APIs, types, and functions
Sets `CFLAGS := -static -ffreestanding -nostartfiles -s`, declares `TEST_GEN_PROGS := get_size`, and includes `../lib.mk`.

## Control flow
The kselftest build system compiles `get_size.c` with no normal C runtime startup.

## State and persistence
Only build artifacts are produced.

## Dependencies and integration points
Depends on compiler/linker support for freestanding static binaries and the `_start` symbol in `get_size.c`.

## Risks
Some libc/toolchain combinations may not support this minimal static linking mode.

## Test signals
Successful build produces a small `get_size` program suitable for low-perturbation memory reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/size/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/size/get_size.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/size/get_size.c

## Purpose
Minimal TAP-emitting program that reports runtime system memory use while avoiding libc startup and heavy dependencies.

## Important APIs, types, and functions
Implements raw-print helpers `print()`, `num_to_str()`, `print_num()`, and `print_k_value()`. Entry point is `_start()`, which uses only `syscall(SYS_sysinfo)`, `syscall(SYS_write)`, and `syscall(SYS_exit)`.

## Control flow
`_start()` prints TAP header, calls `sysinfo()`, reports failure as `not ok 1` if unavailable, otherwise computes used memory as `totalram - freeram - bufferram`, prints total/free/buffer/in-use values in KiB, prints `1..1`, and exits.

## State and persistence
No persistent state. Uses stack/local buffers and the kernel-provided `struct sysinfo`.

## Dependencies and integration points
Depends on syscall numbers provided by libc headers but not libc runtime initialization. Integrated as a kselftest generated program.

## Risks
The file warns that syscall failures may crash on some libc implementations because `errno` TLS is not initialized without startup files. Memory accounting intentionally ignores cache complexities.

## Test signals
Pass is `ok 1 get runtime memory use` followed by diagnostic memory report. Failure is `not ok 1` with reason `could not get sysinfo`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/size/get_size.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sparc64/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/sparc64/Makefile

## Purpose
Top-level sparc64 selftest Makefile that only builds/runs on sparc64 and delegates to the `drivers` subdirectory.

## Important APIs, types, and functions
Normalizes `ARCH` by mapping `x86_64` to `x86`. Non-sparc64 defines a silent `nothing` target. On sparc64 it sets `SUBDIRS := drivers` and `TEST_PROGS := run.sh`.

## Control flow
The sparc64 branch includes `../lib.mk`, loops through subdirectories to build into `$(OUTPUT)/<subdir>`, copies subdir test scripts, and overrides install/clean rules to recurse.

## State and persistence
Writes build outputs in per-subdir output directories and installs tests under `$(INSTALL_PATH)`.

## Dependencies and integration points
Integrates sparc64-specific driver tests with kselftest and `drivers/Makefile`.

## Risks
The custom shell loop assumes subdir scripts follow `<subdir>_test.sh`. Non-sparc64 silently does nothing, so missing tests on cross builds may be expected.

## Test signals
On sparc64, successful build creates `drivers/adi-test` and `run.sh` executes the drivers test script.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sparc64/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sparc64/drivers/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/sparc64/drivers/Makefile

## Purpose
Builds the sparc64 ADI privileged driver selftest binary and registers its wrapper script.

## Important APIs, types, and functions
Sets include path `-I.`, `CFLAGS` with warnings, optimization, and debug info, `TEST_GEN_FILES := adi-test`, and `TEST_PROGS := drivers_test.sh`.

## Control flow
The custom `$(OUTPUT)/adi-test: adi-test.c` target is handed to kselftest `../../lib.mk` for build/install orchestration.

## State and persistence
Only build outputs are produced.

## Dependencies and integration points
Depends on `adi-test.c`, local `kselftest.h` include path, and the parent sparc64 Makefile.

## Risks
Only meaningful on sparc64 with the ADI driver available.

## Test signals
Build emits `adi-test`; runtime wrapper reports skip/ok/fail around module loading and binary execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sparc64/drivers/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sparc64/drivers/adi-test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/sparc64/drivers/adi-test.c

## Purpose
Functional selftest for the sparc64 privileged ADI driver exposed as `/dev/adi`. It verifies ADI version tag read/write and seek behavior over physical memory tag offsets.

## Important APIs, types, and functions
Helpers include debug/stat collection (`debug_print()`, `update_stats()`, `print_stats()`), `/proc/iomem` parsing in `build_memory_map()`, timing with `RDTICK`, IO wrappers `read_adi()`, `pread_adi()`, `write_adi()`, `pwrite_adi()`, `seek_adi()`, random tag generation via tick modulo 16, and eight test functions stored in `tests[]`.

## Control flow
`main()` builds a RAM range map, opens `/dev/adi`, then runs each test and reports pass/fail through kselftest. Tests write random ADI version bytes at offsets derived from physical addresses divided by `ADI_BLKSZ`, then read back and compare. Coverage includes aligned one-byte, 4096-byte, 10327-byte, unaligned 12541-byte, lseek semantics, and read/write variants for one byte, 9434 bytes, and 14963 bytes.

## State and persistence
Global RAM range arrays capture up to five System RAM ranges from `/proc/iomem`. Stats accumulate syscall counts, total tick measurements, and bytes. ADI version tags are written through `/dev/adi` to system state but are test-scoped.

## Dependencies and integration points
Requires sparc64 ADI support, `/dev/adi`, readable `/proc/iomem`, and kselftest helpers. `drivers_test.sh` handles module loading before invoking it.

## Risks
`MAX_RANGES_SUPPORTED` is fixed at five with no visible bounds check while parsing `/proc/iomem`. Partial read/write wrappers loop until full size but do not handle zero-length progress. Tests choose physical offsets near RAM range starts/ends and assume they are valid for ADI driver operations.

## Test signals
Each test emits kselftest pass/fail. Final process exits fail if any test failed, otherwise exits pass. Debug stats can be printed when debug bits are enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sparc64/drivers/adi-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sparc64/drivers/drivers_test.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/sparc64/drivers/drivers_test.sh

## Purpose
Wrapper script that loads the sparc64 ADI kernel module when needed, runs `adi-test`, and unloads the module.

## Important APIs, types, and functions
Defines `SRC_TREE=../../../../`, `test_run()`, uses `insmod`, `/sbin/modprobe -q -n`, `/sbin/modprobe -q`, `./adi-test`, and `rmmod`.

## Control flow
If a built `drivers/char/adi.ko` exists in the source tree, it tries `insmod`; otherwise it checks module availability by dry-run modprobe, reports skip if missing, reports ok/fail for modprobe, runs `adi-test`, then removes `adi`.

## State and persistence
Transiently loads and unloads the `adi` kernel module. Tracks script return code in `rc`.

## Dependencies and integration points
Called by `sparc64/run.sh` and installed as the drivers test program. Requires module tools and root-like permissions to load modules.

## Risks
The script runs `adi-test` even after printing skip for missing module, which may fail if `/dev/adi` is unavailable. It suppresses module load/unload errors to `/dev/null` in some paths.

## Test signals
Prints `adi: [SKIP]`, `adi: ok`, or `adi: [FAIL]`; final exit code reflects module load failure but not explicitly the `adi-test` result unless the shell exits due to failure behavior outside this script.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sparc64/drivers/drivers_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sparc64/run.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/sparc64/run.sh

## Purpose
Tiny top-level runner for sparc64 selftests.

## Important APIs, types, and functions
Executes `(cd drivers; ./drivers_test.sh)`.

## Control flow
Changes into the `drivers` subdirectory in a subshell and runs the driver wrapper.

## State and persistence
No state beyond the child script's module and test side effects.

## Dependencies and integration points
Registered as `TEST_PROGS` by the sparc64 Makefile.

## Risks
No SPDX line and no explicit error handling; exit status is the subshell/script status.

## Test signals
All visible test signals come from `drivers_test.sh` and `adi-test`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sparc64/run.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/splice/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/splice/Makefile

## Purpose
Builds splice selftest helpers and registers shell tests for default and short splice reads.

## Important APIs, types, and functions
Declares `TEST_PROGS := default_file_splice_read.sh short_splice_read.sh` and `TEST_GEN_PROGS_EXTENDED := default_file_splice_read splice_read`.

## Control flow
`../lib.mk` builds helper binaries and runs shell scripts as kselftests.

## State and persistence
Only build outputs are produced.

## Dependencies and integration points
Integrated with kselftest common rules and the local C helpers/scripts.

## Risks
Runtime tests depend on procfs, sysfs, and a test module being available.

## Test signals
Successful build creates both helper binaries; shell scripts provide pass/fail exit codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/splice/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/splice/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/splice/config

## Purpose
Declares kernel config dependency for splice selftests.

## Important APIs, types, and functions
Contains `CONFIG_TEST_LKM=m`, requesting the test loadable kernel module.

## Control flow
No executable flow.

## State and persistence
No runtime state.

## Dependencies and integration points
Consumed by kselftest config tooling to identify kernel module requirements.

## Risks
If the module is not built or loadable, sysfs splice checks in `short_splice_read.sh` may fail or skip indirectly.

## Test signals
Presence of the config line signals the expected test module requirement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/splice/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/splice/default_file_splice_read.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/splice/default_file_splice_read.c

## Purpose
Minimal helper that invokes a huge `splice()` from stdin to stdout to test default file splice-read behavior.

## Important APIs, types, and functions
`main()` calls `splice(0, 0, 1, 0, 1 << 30, 0)` and returns zero.

## Control flow
No argument parsing; it simply tries to splice up to 1 GiB from fd 0 to fd 1.

## State and persistence
No persistent state.

## Dependencies and integration points
Called by `default_file_splice_read.sh` with stdin redirected from `/dev/null`.

## Risks
Return value is ignored; the paired script detects leaked output by counting stdout bytes.

## Test signals
Expected behavior with `/dev/null` is zero bytes emitted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/splice/default_file_splice_read.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/splice/default_file_splice_read.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/splice/default_file_splice_read.sh

## Purpose
Checks that splicing from `/dev/null` through the default file splice path does not leak data.

## Important APIs, types, and functions
Runs `./default_file_splice_read </dev/null | wc -c` and compares the count to zero.

## Control flow
If byte count is `0`, exits success. Otherwise prints a leak message and exits failure.

## State and persistence
No persistent state.

## Dependencies and integration points
Depends on the helper binary and standard `wc`.

## Risks
Assumes current directory contains the built helper.

## Test signals
Exit 0 means no leaked output; failure prints `default_file_splice_read broken: leaked <n>`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/splice/default_file_splice_read.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/splice/short_splice_read.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/splice/short_splice_read.sh

## Purpose
Regression test for splice handling on procfs/sysfs pseudo-files, including short reads and removed fallback behavior.

## Important APIs, types, and functions
Defines `expect_success()`, `expect_failure()`, `do_splice()`, and `test_splice()`. Uses helper `splice_read`, `cat`, `grep`, `cut`, and `modprobe test_module`.

## Control flow
`test_splice()` reads a file normally, derives full content and first two characters, then compares helper-spliced 4096-byte and 2-byte reads. The script expects splice failure for `/proc/<pid>/limits` and `/proc/<pid>/comm`, success for selected `/proc/sys/*` files, loads `test_module` if needed, and expects success for sysfs attribute and binary attribute files under `/sys/module/test_module`.

## State and persistence
Maintains aggregate `ret`; may load `test_module`. No files are written.

## Dependencies and integration points
Requires procfs, sysfs, `test_module`, and the `splice_read` helper built by the Makefile.

## Risks
The comments mention historical behavior changes after splice fallback removal; expectations are specific to current kernel behavior. File contents can change during comparison, especially proc/sys values. Requires module loading for sysfs checks.

## Test signals
Each case reports `ok` or `FAIL` to stderr; final exit is the accumulated failure count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/splice/short_splice_read.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/splice/splice_read.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/splice/splice_read.c

## Purpose
Helper program that splices bytes from an input file to stdout for shell-level splice tests.

## Important APIs, types, and functions
`main()` uses `open()`, optional `fstat()`, `atol()`, `splice()`, and standard error reporting.

## Control flow
Requires at least an input path. If byte count is supplied, uses it; otherwise uses file size after rejecting sizes above `INT_MAX`. Calls `splice(fd, NULL, STDOUT_FILENO, NULL, size, 0)` and returns failure on open/stat/splice errors or short splice.

## State and persistence
No persistent state; opens the input file and writes to stdout.

## Dependencies and integration points
Used by `short_splice_read.sh` to compare pseudo-file splice output with normal reads.

## Risks
`atol()` provides weak input validation. For pseudo-files, `st_size` may be zero, so tests usually pass explicit byte counts. Short splice behavior is treated as failure.

## Test signals
Exit 0 with stdout matching expected content is success; perror output and nonzero exit indicate helper failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/splice/splice_read.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/static_keys/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/static_keys/Makefile

## Purpose
Registers the static keys module selftest script while avoiding accidental run on plain `make`.

## Important APIs, types, and functions
Defines empty `all:` target, `TEST_PROGS := test_static_keys.sh`, and includes `../lib.mk`.

## Control flow
No binaries are built; kselftest runs the script when requested.

## State and persistence
No build artifacts from this Makefile.

## Dependencies and integration points
Uses kselftest `lib.mk` and the static key kernel test modules declared in config.

## Risks
The comment notes arg-less `make` should not trigger `run_tests`.

## Test signals
Runtime signals come from `test_static_keys.sh`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/static_keys/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/static_keys/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/static_keys/config

## Purpose
Declares the kernel module dependency for static key tests.

## Important APIs, types, and functions
Contains `CONFIG_TEST_STATIC_KEYS=m`.

## Control flow
No executable flow.

## State and persistence
No runtime state.

## Dependencies and integration points
Consumed by kselftest config tooling so `test_static_key_base` and `test_static_keys` modules are available.

## Risks
Missing modules make the script skip or fail.

## Test signals
The config line signals that module selftests should be built as modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/static_keys/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/static_keys/test_static_keys.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/static_keys/test_static_keys.sh

## Purpose
Loads kernel static key test modules and reports whether module selftests pass.

## Important APIs, types, and functions
Uses kselftest skip code `4`, `/sbin/modprobe -q -n` for availability checks, real `modprobe` loads, and `modprobe -r` cleanup.

## Control flow
Dry-runs `test_static_key_base` and `test_static_keys`, skipping if either is unavailable. Loads base module first, then test module. On success prints `static_keys: ok` and removes both modules. On failure prints `[FAIL]`, removes the base if needed, and exits failure for base-load failure.

## State and persistence
Temporarily loads kernel modules and unloads them. No files are written.

## Dependencies and integration points
Requires module utilities and kernel modules produced by `CONFIG_TEST_STATIC_KEYS=m`.

## Risks
The inner test module load failure path prints fail and removes base but does not explicitly `exit 1`, so final shell status depends on the last command. Module cleanup may fail silently because `-q` is used.

## Test signals
Skip messages for missing modules, `static_keys: ok` on success, `[FAIL]` on load failure, and skip/failure exit codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/static_keys/test_static_keys.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sync/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/sync/Makefile

## Purpose
Builds the sw_sync selftest executable from a custom object set.

## Important APIs, types, and functions
Sets pthread-capable CFLAGS/LDFLAGS, includes `../lib.mk`, defines `TEST_CUSTOM_PROGS := $(OUTPUT)/sync_test`, core objects `sync_test.o sync.o`, and test objects for allocation, fence, merge, wait, and stress scenarios.

## Control flow
`all` builds `sync_test`; object pattern rules compile core sources with full `CFLAGS` and test objects with default compile flags; final link combines all objects with pthread flags. `EXTRA_CLEAN` removes binary and objects.

## State and persistence
Only build outputs under `$(OUTPUT)`.

## Dependencies and integration points
Depends on other sync selftest C files not in this work item, kernel headers via `$(KHDR_INCLUDES)`, pthreads, and staging sw_sync config.

## Risks
The test object compile rule omits explicit `$(CFLAGS)`, unlike core object rule, so include/warning options may differ for test modules.

## Test signals
Successful build emits `sync_test`, which lib.mk runs/installs as a custom test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sync/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sync/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/sync/config

## Purpose
Declares kernel options required for sw_sync selftests.

## Important APIs, types, and functions
Contains `CONFIG_STAGING=y` and `CONFIG_SW_SYNC=y`.

## Control flow
No executable flow.

## State and persistence
No runtime state.

## Dependencies and integration points
Consumed by kselftest config tooling so the staging sw_sync driver is enabled.

## Risks
Without these options the built userspace tests cannot exercise `/dev/sw_sync` behavior.

## Test signals
The config entries identify the kernel support expected before running sync tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sync/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sync/sw_sync.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/sync/sw_sync.h

## Purpose
Header declaring the userspace abstraction for Android-style software sync timelines and fences used by sync selftests.

## Important APIs, types, and functions
Declares timeline functions `sw_sync_timeline_create()`, `sw_sync_timeline_is_valid()`, `sw_sync_timeline_inc()`, `sw_sync_timeline_destroy()` and fence functions `sw_sync_fence_create()`, `sw_sync_fence_is_valid()`, `sw_sync_fence_destroy()`.

## Control flow
No executable flow; implementation is in other sync sources.

## State and persistence
The API manages file descriptors for timelines and fences; this header only declares ownership boundaries.

## Dependencies and integration points
Included by sync allocation/fence/merge/wait/stress tests and their implementation files.

## Risks
The header notes sw_sync is intended for testing, not production kernels. Callers must destroy fds to avoid leaks.

## Test signals
Tests use validity helpers and fd creation/destruction paths declared here to report sync behavior success or failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sync/sw_sync.h -->
