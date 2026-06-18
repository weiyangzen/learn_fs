# subset-b-006321 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/ty.rs -->
# sources/distributed-fs/ceph-client/rust/syn/ty.rs

Purpose: defines Syn's Rust type syntax tree and the parser/printer behavior for type-position syntax. It covers arrays, slices, tuples, paths and qualified paths, references, raw pointers, bare function types, `impl Trait`, trait objects, inferred and never types, macros in type position, invisible groups, and verbatim fallback tokens.

Important APIs/types/functions: exports the non-exhaustive `Type` enum and structs `TypeArray`, `TypeBareFn`, `TypeGroup`, `TypeImplTrait`, `TypeInfer`, `TypeMacro`, `TypeNever`, `TypeParen`, `TypePath`, `TypePtr`, `TypeReference`, `TypeSlice`, `TypeTraitObject`, `TypeTuple`, `Abi`, `BareFnArg`, `BareVariadic`, and `ReturnType`. Parsing entry points include `Parse for Type`, `Type::without_plus`, `ambig_ty`, `ReturnType::without_plus`, `TypeTraitObject::without_plus`, and `TypeImplTrait::without_plus`. Printing is through `quote::ToTokens` implementations for each type node.

Control flow: `ambig_ty` drives ambiguous type parsing. It first handles transparent groups and group-qualified paths, then optional `for<...>` lifetimes, parenthesized forms, function-pointer syntax, paths and type macros, `dyn` trait objects, array/slice brackets, raw pointers, references, never type, `impl Trait`, `_`, and lifetime-started trait objects. Special paths convert into trait objects when `for` lifetimes or `+` bounds are present. Parenthesized syntax distinguishes unit tuple, one-element tuple, parenthesized type, and parenthesized trait-bound object. Bare function parsing separates regular inputs from variadics and preserves unsupported `self` spellings as verbatim.

State and persistence: no persistent runtime state. AST nodes retain token spans and delimiters for later diagnostics and printing. Parser state is limited to `ParseStream` forks and cursors; printer state is only the output `TokenStream`.

Dependencies and integration: integrates with Syn modules for attributes, expressions, generics, lifetimes, macros, paths, punctuation, tokens, verbatim extraction, groups, and errors. Feature gates split parsing and printing. Downstream procedural macros consume these AST types and must account for `Type` being non-exhaustive.

Risks: ambiguity handling around `+`, parenthesized trait bounds, transparent groups, and qualified paths is subtle and can change parse shape. `TypeTraitObject` and `TypeImplTrait` enforce at least one trait-like bound, so lifetime-only input becomes an error. `TypePtr` and `TypeReference` intentionally call `without_plus`, which affects casts and precedence. Unsupported grammar is preserved as `Type::Verbatim`, which can defer errors to later consumers.

Test signals: parser round trips for Rust type grammar, quote/to-token tests, Syn feature-matrix tests for `parsing` and `printing`, and downstream procedural macro tests that match all currently known `Type` variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/ty.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/verbatim.rs -->
# sources/distributed-fs/ceph-client/rust/syn/verbatim.rs

Purpose: reconstructs an uninterpreted `TokenStream` between two Syn parser positions for syntax that should be preserved as verbatim rather than parsed into a structured AST node.

Important APIs/types/functions: exposes crate-private `between(begin, end) -> TokenStream`. It uses `ParseStream::cursor`, `cursor.token_tree`, `cursor.group(Delimiter::None)`, `buffer::same_buffer`, and `buffer::cmp_assuming_same_buffer`.

Control flow: the function asserts both cursors belong to the same buffer, walks token trees from `begin` to `end`, and extends a new `TokenStream` with each token. If a token would cross the end boundary because of a none-delimited group, it enters that group and continues; any other boundary crossing panics.

State and persistence: no persistent state. The returned token stream is a copied representation of the source range.

Dependencies and integration: used by parsers such as `ty.rs` to preserve unmodeled syntax like unsupported type forms or special bare function argument spellings. Relies on Syn's buffer cursor invariants and `proc_macro2` token streams.

Risks: incorrect begin/end pairing can assert or panic. Transparent `Delimiter::None` handling is intentionally narrow; changes in parser transparency rules could expose boundary bugs.

Test signals: tests should exercise verbatim fallback for syntax crossing none-delimited groups, plus malformed cursor-pair debug assertions through Syn parser tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/verbatim.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/whitespace.rs -->
# sources/distributed-fs/ceph-client/rust/syn/whitespace.rs

Purpose: skips Rust whitespace and non-doc comments at the front of a string while preserving documentation comments as meaningful tokens for higher-level parsing.

Important APIs/types/functions: crate-private `skip(&str) -> &str` and helper `is_whitespace(char)`. The function recognizes line comments, nested block comments, empty block comments, ASCII whitespace, Unicode whitespace, and Rust-specific left-to-right and right-to-left marks.

Control flow: loops while the string begins with skippable content. It removes non-doc `//` comments, non-doc `/* ... */` comments with nesting, and whitespace bytes/chars. It returns an empty string for a line comment reaching EOF and returns the original suffix if a block comment is unterminated.

State and persistence: no persistent state; it only returns a slice into the caller's input.

Dependencies and integration: used by Syn scanners to normalize lookahead over lexical trivia without losing doc comments. It depends only on the standard library and Rust lexical rules.

Risks: comment classification must preserve `///`, `//!`, `/**`, and `/*!` doc comments. Unterminated block comments stop skipping so later parsing can report the real error. Unicode whitespace handling must stay aligned with rustc behavior.

Test signals: lexer tests for nested comments, doc-comment preservation, EOF comments, unterminated comments, CR/LF and tab whitespace, Unicode whitespace, and direction marks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/syn/whitespace.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/uapi/lib.rs -->
# sources/distributed-fs/ceph-client/rust/uapi/lib.rs

Purpose: provides the Rust kernel `uapi` crate containing bindgen-generated Rust bindings for selected userspace API headers.

Important APIs/types/functions: the crate is `#![no_std]`, imports `pin_init::MaybeZeroable`, declares manual aliases for blocklisted kernel scalar types `__kernel_size_t`, `__kernel_ssize_t`, and `__kernel_ptrdiff_t`, enables `cfi_encoding`, and includes generated code from `$OBJTREE/rust/uapi/uapi_generated.rs`.

Control flow: there is no runtime control flow. Compilation expands the generated binding file and applies broad lint allowances suitable for generated C FFI.

State and persistence: no runtime state. The persistent artifact is the generated Rust source in the object tree; crate contents depend on the kernel build configuration and bindgen output.

Dependencies and integration: integrates with the kernel Rust build, generated UAPI bindings, `pin_init`, and the headers listed in `uapi_helper.h`. Kernel Rust drivers use it when they need UAPI constants, structs, or ioctl definitions.

Risks: generated bindings can vary with headers and build configuration. The many lint allowances hide generated-code rough edges, so ABI correctness must be validated through bindgen and kernel header tests rather than style checks. `include!` requires `OBJTREE` to be set correctly.

Test signals: kernel Rust build with UAPI generation enabled, bindgen regeneration checks, ABI smoke tests for selected constants/struct layouts, and drivers compiling against this crate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/uapi/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/uapi/uapi_helper.h -->
# sources/distributed-fs/ceph-client/rust/uapi/uapi_helper.h

Purpose: central header input for bindgen when generating Rust UAPI bindings.

Important APIs/types/functions: includes UAPI headers for generic ioctl numbers, DRM core and device-specific DRM ioctls, Android binder, MDIO/MII, and ethtool.

Control flow: no runtime flow; preprocessor inclusion order determines what bindgen sees.

State and persistence: no state. Changes affect the generated `uapi_generated.rs` artifact consumed by the Rust `uapi` crate.

Dependencies and integration: consumed by the kernel Rust build's bindgen step and paired with `rust/uapi/lib.rs`. Header availability depends on a configured kernel source tree and installed/generated UAPI headers.

Risks: include ordering and newly added headers can introduce duplicate definitions, unsupported C constructs, or ABI drift. The file says headers are sorted alphabetically, but the current order groups DRM before Android/Linux networking, so maintainers should be deliberate when modifying it.

Test signals: successful bindgen generation, Rust crate compilation, and layout/constant checks for binder, DRM, ethtool, MDIO, MII, and ioctl bindings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/uapi/uapi_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/Kconfig -->
# sources/distributed-fs/ceph-client/samples/Kconfig

Purpose: defines the kernel configuration menu for optional sample code.

Important APIs/types/functions: top-level `menuconfig SAMPLES` gates all sample options. It declares sample configs for auxdisplay, tracing, ftrace, kobjects, kprobes, rpmsg, livepatch, configfs, connector, fanotify, hidraw, Landlock, pidfd, seccomp, timers, TSM measurements, UHID, VFIO mediated devices, binderfs, VFS, MEI, watchdog, watch_queue, coresight, kmemleak, cgroup, check-exec, hung_task, and sources Rust and DAMON sample Kconfigs. It also declares architecture-provided `HAVE_SAMPLE_FTRACE_DIRECT` symbols.

Control flow: Kconfig dependency logic controls which subdirectories and modules are buildable. Many userspace examples require `CC_CAN_LINK` and `HEADERS_INSTALL`; module samples often require `m`.

State and persistence: configuration state is stored in the kernel `.config`; this file has no runtime state.

Dependencies and integration: consumed by Kconfig and paired with `samples/Makefile`, which maps enabled configs to subdirectories. It integrates with tracing, BPF-adjacent samples indirectly, Rust sample Kconfig, and architecture feature symbols.

Risks: stale dependencies produce broken sample builds or hidden options. Samples that touch privileged kernel APIs may require exact kernel capabilities and headers. Defaulting `SAMPLE_KRETPROBES` to `m` when `SAMPLE_KPROBES` is enabled can surprise minimal module builds.

Test signals: `olddefconfig`, menuconfig visibility checks, allmodconfig/sample builds, and per-sample compile tests with headers installed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/Makefile -->
# sources/distributed-fs/ceph-client/samples/Makefile

Purpose: connects sample Kconfig symbols to kbuild subdirectories and userspace sample build directories.

Important APIs/types/functions: uses `subdir-$(CONFIG_...)` for userspace sample directories and `obj-$(CONFIG_...)` for kernel modules/directories. Always includes `vfio-mdev` with `obj-y`, and conditionally includes Rust, DAMON, ftrace, trace, coresight, kmemleak, hung_task, and TSM samples.

Control flow: kbuild expands enabled `CONFIG_*` variables into directory traversal and object build lists.

State and persistence: no runtime state; build outputs persist under the kernel object tree.

Dependencies and integration: tightly coupled to `samples/Kconfig` symbol names and each child sample Makefile. Userspace samples rely on headers and host/user compiler flags supplied by kbuild.

Risks: missing or mismatched config names silently skip samples. `obj-y += vfio-mdev/` always traverses that directory, so its local Makefile must be robust even when related config is off. User program samples need `headers_install` and suitable toolchains.

Test signals: sample directory build under representative configs, `make samples`, allmodconfig builds, and clean target behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/acrn/Makefile -->
# sources/distributed-fs/ceph-client/samples/acrn/Makefile

Purpose: builds the ACRN hypervisor sample userspace VM launcher and its tiny guest payload.

Important APIs/types/functions: declares phony `vm-sample`, links `vm-sample.o` and `payload.o`, builds `payload.o` with `$(LD) -T payload.ld` from `guest16.o`, and provides a simple `clean`.

Control flow: make compiles normal objects through implicit rules, links the executable with `$(CC)`, and links the payload with a custom linker script.

State and persistence: creates `vm-sample`, object files, and `payload.o`.

Dependencies and integration: depends on `guest16.o`, `payload.ld`, `vm-sample.c`, kernel UAPI headers for ACRN, and an environment with `CC`/`LD`.

Risks: clean uses `rm *.o vm-sample` without `-f`, so it errors if files are absent. The standalone Makefile assumes all payload inputs exist and may not inherit all kbuild hardening flags.

Test signals: standalone `make` in `samples/acrn`, successful link of `payload.o`, and running `vm-sample` only on an ACRN Service VM with `/dev/acrn_hsm`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/acrn/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/acrn/vm-sample.c -->
# sources/distributed-fs/ceph-client/samples/acrn/vm-sample.c

Purpose: userspace example that creates and runs a simple User VM through the ACRN HSM device.

Important APIs/types/functions: uses `/dev/acrn_hsm`, `ACRN_IOCTL_CREATE_VM`, `ACRN_IOCTL_SET_MEMSEG`, `ACRN_IOCTL_SET_VCPU_REGS`, `ACRN_IOCTL_CREATE_IOREQ_CLIENT`, `ACRN_IOCTL_START_VM`, `ACRN_IOCTL_ATTACH_IOREQ_CLIENT`, `ACRN_IOCTL_NOTIFY_REQUEST_FINISH`, pause/destroy ioctls, `struct acrn_vm_creation`, `acrn_vm_memmap`, `acrn_vcpu_regs`, `acrn_io_request`, and embedded `guest16` payload symbols.

Control flow: allocates aligned guest memory, opens the HSM device, creates a VM, maps a 1 MiB RAM segment, copies guest code, initializes real-mode vCPU registers, creates an IO request client, starts the VM, then loops attaching to IO requests and printing port I/O operations until SIGINT sets `is_running` false and pauses/destroys the client. Finally it destroys the VM, closes the device, and frees memory.

State and persistence: process globals track guest memory, VM ID, vCPU count, HSM FD, and shared IO request page. Guest state lives in ACRN and the allocated memory during process lifetime only.

Dependencies and integration: requires ACRN Service VM privileges, `CONFIG_ACRN_HSM`, `/dev/acrn_hsm`, Linux ACRN UAPI headers, and the assembled guest payload.

Risks: many ioctl return values are printed but not enforced before later steps, so failures can cascade. `open` failure is not checked before ioctl use. Signal handler performs ioctl calls, which are not async-signal-safe. The VM setup is intentionally minimal and only suitable as a sample.

Test signals: compile against current headers, run on an ACRN Service VM, observe VM creation/start messages and PIO logging, and verify SIGINT cleanup leaves no stale VM/client.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/acrn/vm-sample.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/auxdisplay/Makefile -->
# sources/distributed-fs/ceph-client/samples/auxdisplay/Makefile

Purpose: registers the CFAG12864B LCD framebuffer userspace example for kbuild.

Important APIs/types/functions: `userprogs-always-y += cfag12864b-example`.

Control flow: kbuild always builds the named userspace program when the auxdisplay sample directory is selected.

State and persistence: no runtime state; build output is the sample executable.

Dependencies and integration: selected by `CONFIG_SAMPLE_AUXDISPLAY` through `samples/Makefile` and built with kbuild user program rules.

Risks: the Makefile is minimal and relies entirely on default user program build rules.

Test signals: enabling `SAMPLE_AUXDISPLAY` should build `cfag12864b-example` without custom flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/auxdisplay/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/auxdisplay/cfag12864b-example.c -->
# sources/distributed-fs/ceph-client/samples/auxdisplay/cfag12864b-example.c

Purpose: userspace framebuffer demo for a 128x64 Crystalfontz CFAG12864B LCD.

Important APIs/types/functions: defines LCD geometry macros, framebuffer address/bit helpers, globals `cfag12864b_fd`, `cfag12864b_mem`, and `cfag12864b_buffer`, and functions `cfag12864b_init`, `cfag12864b_exit`, `set`, `unset`, `isset`, `not`, `fill`, `clear`, `format`, `blit`, `example`, and `main`.

Control flow: `main` opens and mmaps the framebuffer path, runs six interactive drawing examples, blits the local buffer after each one, waits for Enter, and unmaps/closes at exit. Drawing functions manipulate a packed 1-bit-per-pixel local buffer before `memcpy` transfers it to mmaped device memory.

State and persistence: state is a process-local shadow buffer plus the mmaped framebuffer. The display persists visually in hardware until overwritten, but the program stores no files.

Dependencies and integration: depends on the auxdisplay framebuffer driver exposing a compatible `/dev/fb*`, POSIX `open`, `mmap`, `munmap`, and framebuffer write permissions.

Risks: bounds checks are compiled out unless `CFAG12864B_DOCHECK` is defined. The program assumes exact device geometry and byte layout. It waits on stdin after each demo, making it unsuitable for unattended tests without input.

Test signals: run against a compatible framebuffer, visually verify point/clear/row/fill/column/invert examples, and use sanitizers or bounds-enabled builds for coordinate helper tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/auxdisplay/cfag12864b-example.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/binderfs/Makefile -->
# sources/distributed-fs/ceph-client/samples/binderfs/Makefile

Purpose: registers the Android binderfs userspace example for kbuild.

Important APIs/types/functions: `userprogs-always-y += binderfs_example` and `userccflags += -I usr/include`.

Control flow: kbuild builds `binderfs_example` whenever the binderfs sample directory is selected.

State and persistence: no runtime state; produces a userspace binary.

Dependencies and integration: selected by `CONFIG_SAMPLE_ANDROID_BINDERFS`; includes installed UAPI headers through `usr/include`.

Risks: missing headers_install output breaks compilation. The sample itself requires mount namespace and binderfs privileges at runtime.

Test signals: enable `SAMPLE_ANDROID_BINDERFS`, build samples, and verify include path resolves binder headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/binderfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/binderfs/binderfs_example.c -->
# sources/distributed-fs/ceph-client/samples/binderfs/binderfs_example.c

Purpose: demonstrates creating and removing a binder device inside a binderfs mount.

Important APIs/types/functions: uses `unshare(CLONE_NEWNS)`, `mount` with `MS_REC|MS_PRIVATE`, `mkdir`, `mount(..., "binder", ...)`, `open("/dev/binderfs/binder-control")`, `ioctl(BINDER_CTL_ADD)`, `struct binderfs_device`, and `unlink`.

Control flow: creates a private mount namespace, makes `/` private, ensures `/dev/binderfs` exists, mounts binderfs, requests a new device named `my-binder`, prints major/minor/name, unlinks the device, and exits. Mount cleanup is delegated to namespace teardown.

State and persistence: state is the private mount namespace and transient binder device. The device is unlinked explicitly; the mount disappears when the namespace exits.

Dependencies and integration: requires binderfs kernel support, Android binder UAPI headers, and enough privilege for mount namespace and binderfs mount operations.

Risks: hardcoded `/dev/binderfs` path may conflict with existing systems. `memcpy` copies the name without an explicit terminator but starts from a zeroed struct, so current usage is safe. Runtime failures exit early and rely on namespace cleanup.

Test signals: run as a privileged user on a binderfs-enabled kernel, confirm printed device allocation, and verify no persistent `/dev/binderfs/my-binder` after exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/binderfs/binderfs_example.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/Makefile -->
# sources/distributed-fs/ceph-client/samples/bpf/Makefile

Purpose: builds the kernel BPF sample suite, including userspace loaders, classic BPF-style objects, CO-RE `.bpf.c` objects, skeletons, and local libbpf/bpftool dependencies.

Important APIs/types/functions: defines `tprogs-y`, `always-y`, per-target object lists, libbpf and bpftool build locations, `verify_cmds`, `verify_target_bpf`, `vmlinux.h` generation, `syscall_nrs.h` generation, BTF probes, `CLANG_SYS_INCLUDES`, `.bpf.o` compile rules, linked skeleton generation, and legacy `.c` to BPF object pipeline through `clang | opt | llvm-dis | llc`.

Control flow: kbuild first builds libbpf and helper objects, probes LLVM/BTF capabilities, generates `vmlinux.h` when needed, compiles userspace targets with libbpf, compiles BPF programs with either direct `clang --target=bpf` for `.bpf.c` or the legacy LLVM IR pipeline for other BPF C files, and generates skeletons through bpftool for linked BPF objects.

State and persistence: build outputs include sample executables, BPF object files, generated `vmlinux.h`, generated skeleton headers, local `libbpf/` and `bpftool/` directories, `syscall_nrs.h`, and optional BTF-enriched objects.

Dependencies and integration: depends on kernel kbuild, tools/lib/bpf, tools/bpf/bpftool, LLVM tools, pahole for BTF fallback, installed headers, selftest helpers, and architecture-specific target macros.

Risks: toolchain probing is complex and environment-sensitive. Missing `vmlinux` or `VMLINUX_H` blocks CO-RE builds. System include recovery can mask distro-specific header issues. The legacy pipeline depends on LLVM tools agreeing on IR format and BPF backend support.

Test signals: `make M=samples/bpf`, clean rebuilds, cross-compile smoke tests, generated `vmlinux.h` and skeleton presence, and running representative samples such as `sockex1`, `syscall_tp`, `map_perf_test`, and `hbm`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/asm_goto_workaround.h -->
# sources/distributed-fs/ceph-client/samples/bpf/asm_goto_workaround.h

Purpose: hides kernel inline assembly constructs from the BPF sample clang compilation path.

Important APIs/types/functions: include guard, includes `linux/types.h`, defines `asm_goto_output`, maps `asm_inline` to `asm`, and overrides `volatile(...)`.

Control flow: preprocessor-only behavior; included forcibly by the BPF Makefile for legacy BPF C compilation.

State and persistence: no state.

Dependencies and integration: integrates with the BPF sample build rule that includes kernel headers under `--target=bpf` or LLVM IR compilation. It avoids unsupported assembly from headers such as arch sysreg definitions.

Risks: macro overrides are broad and only appropriate for BPF sample compilation. Using this header outside that context could change semantics or hide real compiler diagnostics.

Test signals: successful BPF sample compilation on architectures whose headers contain unsupported inline asm.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/asm_goto_workaround.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/bpf_insn.h -->
# sources/distributed-fs/ceph-client/samples/bpf/bpf_insn.h

Purpose: provides C macros for manually constructing `struct bpf_insn` instruction arrays.

Important APIs/types/functions: defines helpers for ALU64/ALU32 register and immediate ops, moves, 64-bit loads, map FD loads, absolute loads, memory loads/stores, atomic add, jumps, calls, exits, endian conversions, and raw instruction emission.

Control flow: preprocessor expands macros into compound literals used by loaders like `cookie_uid_helper_example.c` and `sock_example.c`.

State and persistence: no state; generated instruction arrays are compiled into userspace programs.

Dependencies and integration: depends on Linux BPF opcode/register definitions and `struct bpf_insn`. It supports old-style samples that do not compile C source to BPF bytecode.

Risks: manual instruction construction is easy to get wrong in offsets, register classes, and helper calling convention. Some macros encode assumptions about little fields in `struct bpf_insn`. Verifier diagnostics are the main safety net.

Test signals: successful `bpf_prog_load` of instruction arrays, verifier log checks, and exercising samples that use map FD rewrite macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/bpf_insn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/cookie_uid_helper_example.c -->
# sources/distributed-fs/ceph-client/samples/bpf/cookie_uid_helper_example.c

Purpose: demonstrates `bpf_get_socket_cookie` and `bpf_get_socket_uid` helpers for per-socket traffic accounting through a socket filter attached via iptables `xt_bpf`.

Important APIs/types/functions: defines `struct stats`, `maps_create`, `prog_load`, `prog_attach_iptables`, `print_table`, `udp_client`, `finish`, and `main`. Uses manual BPF instruction macros, `BPF_MAP_TYPE_HASH`, `BPF_PROG_TYPE_SOCKET_FILTER`, `bpf_obj_pin`, `iptables -m bpf --object-pinned`, UDP sockets, and `SO_COOKIE`.

Control flow: creates a hash map keyed by socket cookie, loads a hand-written BPF program that looks up or creates stats and atomically increments packet/byte counters, pins the program, attaches an iptables OUTPUT rule, then either prints map contents until signaled or sends loopback UDP packets and verifies per-cookie stats.

State and persistence: BPF map and program FDs live in process state. The pinned program and iptables rule can persist if not cleaned by the wrapper script; the sample closes FDs but does not remove iptables rules itself.

Dependencies and integration: requires libbpf, xt_bpf-capable iptables, BPF filesystem pinning, root privileges, and `run_cookie_uid_helper_example.sh` for setup/cleanup.

Risks: invokes `system("iptables ...")` with a path-length check but still depends on shell/iptables behavior. Cleanup is external. Manual BPF instructions and atomic map updates require verifier compatibility. The map key is `uint32_t` while socket cookies are read as `uint64_t` in the UDP client, which is sample-specific and can be confusing.

Test signals: run the wrapper with `-s` to confirm UDP cookie stats and with `-t` to observe live traffic counters; verify iptables and BPF pin cleanup after signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/cookie_uid_helper_example.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/cpustat_kern.c -->
# sources/distributed-fs/ceph-client/samples/bpf/cpustat_kern.c

Purpose: BPF tracepoint program that accumulates CPU idle-state and frequency-state residency durations.

Important APIs/types/functions: maps `my_map`, `cstate_duration`, `pstate_duration`, constants for 8 CPUs, 3 C-states, and 5 P-states, `find_cpu_pstate_idx`, tracepoint programs `bpf_prog1` for `power/cpu_idle` and `bpf_prog2` for `power/cpu_frequency`.

Control flow: tracepoint handlers look up per-CPU timestamp/state slots, compute deltas from `bpf_ktime_get_ns`, and atomically add durations to cstate or pstate duration maps. Idle entry records current pstate time; idle exit records previous cstate time. Frequency changes record previous pstate time when the CPU is not idle.

State and persistence: all state is in BPF array maps for current timestamps/state indices and accumulated durations. Maps persist while the object is loaded.

Dependencies and integration: attached and read by `cpustat_user.c`; depends on power tracepoint formats and platform-specific frequency values listed in `cpu_opps`.

Risks: constants are Hikey-specific; CPUs beyond the assumed range are ignored or risk off-by-one behavior because `ctx->cpu_id > MAX_CPU` should likely be `>=`. Atomic adds on map values are shared across event contexts. Frequency sysfs assumptions live in the user program.

Test signals: attach both tracepoints, trigger idle and frequency events, and confirm duration maps change and printed residency totals are plausible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/cpustat_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/cpustat_user.c -->
# sources/distributed-fs/ceph-client/samples/bpf/cpustat_user.c

Purpose: userspace loader and terminal display for the CPU state BPF sample.

Important APIs/types/functions: uses libbpf object/program APIs, map FDs `cstate_map_fd` and `pstate_map_fd`, `cpu_stat_update`, `cpu_stat_print`, `cpu_stat_inject_cpu_idle_event`, `cpu_stat_inject_cpu_frequency_event`, signal handler `int_exit`, and sysfs path `/sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq`.

Control flow: opens `<argv[0]>_kern.o`, finds `bpf_prog1`, loads the object, finds duration maps, attaches one program, injects idle/frequency events, then loops every five seconds reading maps and printing a screen-cleared table. Signal exit injects final events, updates/prints stats, and exits.

State and persistence: keeps latest map values in `stat_data`. BPF links and object persist until process exit or cleanup. It writes CPU frequency sysfs values as an event trigger.

Dependencies and integration: pairs with `cpustat_kern.c`, requires libbpf, power tracepoints, CPUFreq sysfs, scheduling affinity APIs, and sufficient privilege for BPF and sysfs writes.

Risks: only attaches `bpf_prog1` explicitly despite the object also containing `bpf_prog2`, depending on libbpf auto-attach behavior is not obvious. Frequency constants are platform-specific and `CPUFREQ_HIGHEST_FREQ` appears one zero larger than the documented 1.2 GHz value. Signal handler does non-async-safe work.

Test signals: run on a compatible platform, observe table updates, verify both cstate and pstate maps receive values, and test SIGINT final print behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/cpustat_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/do_hbm_test.sh -->
# sources/distributed-fs/ceph-client/samples/bpf/do_hbm_test.sh

Purpose: shell test harness for the Host Bandwidth Manager samples.

Important APIs/types/functions: orchestrates HBM BPF loader invocations, cgroup setup through the loader, traffic generation, iperf/netperf-style checks depending on environment, stats file collection, and cleanup of pinned links/cgroups.

Control flow: parses test options, starts HBM programs with rate/duration/stats flags, runs traffic workloads through the limited cgroup, waits for completion, collects `hbm.*.out` statistics and trace logs, and removes temporary state on exit.

State and persistence: creates temporary cgroups, pinned BPF links under bpffs, generated stats/log files, and background workload processes. Cleanup is required to avoid leaking cgroup or bpffs state.

Dependencies and integration: integrates with `hbm`, `hbm_out_kern.o`, `hbm_edt_kern.o`, the cgroup filesystem, bpffs, traffic tools, loopback or network interfaces, and privileged shell execution.

Risks: network and cgroup tests are environment-sensitive. Failure paths can leave pinned links or cgroups if traps do not run. Throughput expectations are hardware/NIC dependent, and work-conserving mode assumes `eth0` in the C loader.

Test signals: successful script completion, generated HBM stats files with expected rate/drop/mark fields, no leftover `/sys/fs/bpf/hbm*` pins, and no leaked test cgroups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/do_hbm_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/fds_example.c -->
# sources/distributed-fs/ceph-client/samples/bpf/fds_example.c

Purpose: demonstrates pinning and retrieving BPF map/program file descriptors from bpffs.

Important APIs/types/functions: defines mode/flag constants, `usage`, `bpf_prog_create`, `bpf_do_map`, `bpf_do_prog`, and `main`. Uses libbpf object loading, `bpf_obj_pin`, `bpf_obj_get`, map update/lookup, socket filter attach, and a tiny `BPF_PROG_TYPE_SOCKET_FILTER` instruction sequence.

Control flow: parses options selecting map or program mode and pin/get behavior. Map mode creates or retrieves a pinned map and optionally updates/reads a key/value. Program mode creates or retrieves a pinned program and can attach it to a socket.

State and persistence: bpffs paths persist pinned maps/programs beyond process lifetime. Map entries persist while the map pin exists.

Dependencies and integration: requires mounted bpffs, BPF syscall support, libbpf, root privileges, and the BPF sample build environment.

Risks: user must manage pinned object lifetime. The sample mixes demonstration flags, so invalid combinations must be caught by option handling. Program attach uses socket filter semantics and may not demonstrate all program types.

Test signals: pin a map, update a value, retrieve it in a second invocation, pin/retrieve a program, and verify cleanup by removing the bpffs files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/fds_example.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/gnu/stubs.h -->
# sources/distributed-fs/ceph-client/samples/bpf/gnu/stubs.h

Purpose: placeholder header to satisfy include resolution for BPF sample builds that encounter `<gnu/stubs.h>`.

Important APIs/types/functions: contains no declarations.

Control flow: no control flow.

State and persistence: no state.

Dependencies and integration: used as an include-path shim when compiling BPF programs in an environment where glibc stubs would otherwise be inappropriate or unavailable.

Risks: because it is empty, any code genuinely requiring glibc stub definitions would compile incorrectly; in these samples it is intended only to satisfy incidental includes.

Test signals: BPF sample compilation succeeds on systems that otherwise report missing `gnu/stubs.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/gnu/stubs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/hash_func01.h -->
# sources/distributed-fs/ceph-client/samples/bpf/hash_func01.h

Purpose: supplies a small integer hash function for BPF samples.

Important APIs/types/functions: `get16bits` macro and an inline hash routine based on 16-bit chunks with avalanche mixing.

Control flow: processes input in 4-byte chunks, handles the 0 to 3 trailing bytes through a switch, then performs final bit-mixing steps.

State and persistence: stateless; returns a hash value from caller-provided bytes and length.

Dependencies and integration: intended for inclusion in BPF C where a compact deterministic hash is needed. Uses kernel integer types and inline-friendly arithmetic.

Risks: `get16bits` may perform unaligned 16-bit loads depending on architecture/compiler behavior. It is a non-cryptographic hash and should not be used for adversarial integrity/security.

Test signals: deterministic hash values for fixed byte strings and verifier acceptance when included in BPF programs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/hash_func01.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/hbm.c -->
# sources/distributed-fs/ceph-client/samples/bpf/hbm.c

Purpose: userspace loader/controller for Host Bandwidth Management cgroup-skb BPF programs.

Important APIs/types/functions: global flags for rate, duration, stats, loopback, debug, work-conserving, no-CN, and EDT mode; `prog_load`, `run_bpf_prog`, `read_trace_pipe2`, `do_error`, `Usage`, and `main`. Uses libbpf object loading, cgroup helper APIs, `bpf_program__attach_cgroup`, `bpf_link__pin`, `queue_stats` map updates/lookups, tracefs, and `/sys/class/net/eth0/statistics/tx_bytes`.

Control flow: parses options, selects `hbm_out_kern.o` or `hbm_edt_kern.o`, loads the BPF object, finds the egress program and stats map, creates/joins `/hbmN` cgroup, initializes `queue_stats`, attaches and pins the cgroup link, sleeps or dynamically adjusts rate in work-conserving mode, writes final stats to `hbm.N.out`, optionally reads trace pipe, then destroys link/object and closes the cgroup FD.

State and persistence: creates cgroup state, pinned bpffs link `/sys/fs/bpf/hbmN`, and stats/log files. Queue state and stats live in BPF maps while loaded. Cgroup environment cleanup occurs only on error; successful runs intentionally leave pinned link state for the script or user to clean.

Dependencies and integration: pairs with `hbm_out_kern.c`, `hbm_edt_kern.c`, `hbm.h`, `hbm_kern.h`, and selftest cgroup helpers. Requires cgroup v2/BPF cgroup support, bpffs, tracefs for debug, libbpf, root privileges, and often `do_hbm_test.sh`.

Risks: work-conserving mode hardcodes `eth0`. Successful path pins links and may leave persistent state. Rate conversion multiplies by 1.024 and then by 128 in the BPF side, so units need careful interpretation. Debug trace reader loops forever after stats.

Test signals: run with `-s -t N` and verify `hbm.N.out`, check cgroup link pin existence, run `--edt` variant, validate cleanup through harness, and compare measured throughput/drop/mark rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/hbm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/hbm.h -->
# sources/distributed-fs/ceph-client/samples/bpf/hbm.h

Purpose: shared Host Bandwidth Manager data structures used by userspace and BPF programs.

Important APIs/types/functions: `struct hbm_vqueue` contains `bpf_spin_lock`, credit, rate, and last timestamp; `struct hbm_queue_stats` contains rate/config flags, packet/byte counters, marks/drops/ECN counters, timing, congestion window/RTT sums, credit sum, and return-value counters.

Control flow: no executable flow; structures define the ABI between `hbm.c` and BPF map values.

State and persistence: values are persisted in BPF cgroup storage and array maps while programs are attached.

Dependencies and integration: included by `hbm.c` and `hbm_kern.h`. Layout must be valid for both userspace C and BPF C, including `bpf_spin_lock` constraints.

Risks: struct layout changes are ABI changes for map values. Spin locks in BPF map values impose verifier and map-type restrictions. Counter widths must be sufficient for high-throughput tests.

Test signals: BPF verifier accepts map value types, userspace can update/read `queue_stats`, and stats fields match BPF-side updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/hbm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/hbm_edt_kern.c -->
# sources/distributed-fs/ceph-client/samples/bpf/hbm_edt_kern.c

Purpose: cgroup egress BPF program that enforces bandwidth using Earliest Departure Time (`skb->tstamp`) instead of token credits.

Important APIs/types/functions: `SEC("cgroup_skb/egress") int _hbm_out_cg`, `hbm_get_pkt_info`, `hbm_init_edt_vqueue`, `hbm_update_stats`, `BYTES_TO_NS`, queue storage map `queue_state`, and stats map `queue_stats`.

Control flow: retrieves stats and local cgroup queue state, skips loopback unless configured, parses packet/TCP/ECN info, initializes virtual queue, locks queue state, computes current schedule lag and send time, advances `lasttime` by packet serialization time, unlocks, writes `skb->tstamp`, updates rate if userspace changed it, marks/drops/CWRs packets based on latency thresholds, records stats, and rolls back scheduled time if dropping.

State and persistence: per-cgroup `hbm_vqueue` stores `lasttime` and rate; `queue_stats` stores configuration and counters.

Dependencies and integration: loaded by `hbm.c --edt`, requires cgroup skb egress attachment, fq/qdisc behavior honoring EDT, and helpers from `hbm_kern.h`.

Risks: correctness depends on `skb->tstamp` interpretation by the transmit path. Drop/mark thresholds are fixed constants. Concurrent updates are protected only around queue scheduling; stats use atomic adds. Very small or non-TCP flows have different drop behavior.

Test signals: EDT mode throughput tests, stats showing latency/credit values in milliseconds, verifier acceptance of spin lock and `skb->tstamp` writes, and comparison with non-EDT HBM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/hbm_edt_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/hbm_kern.h -->
# sources/distributed-fs/ceph-client/samples/bpf/hbm_kern.h

Purpose: shared kernel-side helpers, constants, maps, and packet parsing for HBM BPF programs.

Important APIs/types/functions: defines return flags `DROP_PKT`, `ALLOW_PKT`, `CWR`, thresholds for credit and EDT modes, rate conversion macros, maps `queue_state` and `queue_stats`, `struct hbm_pkt_info`, `get_tcp_info`, `hbm_get_pkt_info`, `hbm_init_vqueue`, `hbm_init_edt_vqueue`, and `hbm_update_stats`.

Control flow: helper routines extract TCP socket info and IP ECN state, initialize per-cgroup queues, and update shared stats counters based on congestion/drop/CWR/ECN decisions made by the main programs.

State and persistence: declares BPF maps that persist while programs are loaded. `queue_state` is cgroup-local storage with spin lock; `queue_stats` is an array shared with userspace.

Dependencies and integration: included by `hbm_out_kern.c` and `hbm_edt_kern.c`; depends on BPF helpers, kernel network headers, endian helpers, and `hbm.h` layout.

Risks: packet parsing reads only initial bytes and handles IPv4/IPv6 simplistically. Rate macros use fixed scaling and require userspace to supply matching units. Stats update has many optional counters and uses atomic operations that can be expensive under load.

Test signals: verifier acceptance, HBM stats consistency, TCP ECN marking observations, and tests that flip `loopback`, `no_cn`, and `stats` flags from userspace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/hbm_kern.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/hbm_out_kern.c -->
# sources/distributed-fs/ceph-client/samples/bpf/hbm_out_kern.c

Purpose: cgroup egress BPF program that enforces bandwidth with a virtual credit/token bucket.

Important APIs/types/functions: `SEC("cgroup_skb/egress") int _hbm_out_cg`, maps and helpers from `hbm_kern.h`, per-cgroup `hbm_vqueue` credit state, and queue stats updates.

Control flow: skips loopback when configured, extracts packet info, obtains local queue state, initializes if needed, locks and refreshes credits based on elapsed time, subtracts packet length, unlocks, applies rate updates from userspace, decides congestion/drop/CWR based on negative credit thresholds and packet type, attempts ECN CE marking, updates stats, restores credit if packet is dropped, and returns cgroup-skb verdict flags.

State and persistence: per-cgroup credit, timestamp, and rate live in `queue_state`; user-visible counters/config live in `queue_stats`.

Dependencies and integration: default program loaded by `hbm.c`, shares ABI with `hbm.h`, requires cgroup skb egress support and BPF spin locks.

Risks: virtual queue does not actually queue, so behavior relies on mark/drop/CWR feedback. Thresholds and `MAX_CREDIT` are fixed. Packet length excludes some link overhead. Concurrent stats updates may skew exact counters.

Test signals: run HBM at a low rate and observe drops/marks, verify `hbm.N.out` counters, and inspect TCP congestion response under ECN and non-ECN flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/hbm_out_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/ibumad_kern.c -->
# sources/distributed-fs/ceph-client/samples/bpf/ibumad_kern.c

Purpose: BPF tracepoint sample that counts InfiniBand UMAD packets by management class.

Important APIs/types/functions: declares two BPF maps for counts, `struct ib_umad_rw_args`, tracepoint handlers `on_ib_umad_read_recv`, `on_ib_umad_read_send`, and `on_ib_umad_write`, and optional `bpf_printk`.

Control flow: each tracepoint reads UMAD tracepoint arguments, derives packet class/direction, looks up or initializes counters in maps, and updates packet counts.

State and persistence: counters live in BPF maps while the program is attached.

Dependencies and integration: paired with `ibumad_user.c`; depends on `ib_umad` tracepoints and matching tracepoint format.

Risks: tracepoint structure must match kernel format. Systems without InfiniBand UMAD support will not produce data or may fail attach. Count keys/classes need to stay aligned with tracepoint semantics.

Test signals: attach on a system with UMAD activity, generate reads/writes, and verify user program dumps nonzero class counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/ibumad_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/ibumad_user.c -->
# sources/distributed-fs/ceph-client/samples/bpf/ibumad_user.c

Purpose: userspace loader and dumper for the InfiniBand UMAD BPF tracepoint sample.

Important APIs/types/functions: globals for three tracepoint links, BPF object, map FDs, `dump_counts`, `dump_all_counts`, `dump_exit`, CLI `usage`, and `main`.

Control flow: opens and loads the BPF object, attaches tracepoint programs, locates maps, then sleeps until interrupted. On interval or exit it iterates map keys and prints counts.

State and persistence: BPF links and object live during process execution; counts persist in maps until object close.

Dependencies and integration: requires libbpf, UMAD tracepoints, root/BPF privileges, and the `ibumad_kern.o` object.

Risks: no useful output on systems without UMAD traffic. Signal-triggered dump performs nontrivial work. Map layout must match kernel program.

Test signals: run with generated UMAD traffic, observe per-class counters, and confirm links are destroyed on exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/ibumad_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/lathist_kern.c -->
# sources/distributed-fs/ceph-client/samples/bpf/lathist_kern.c

Purpose: BPF kprobe sample that builds latency histograms for preemption-off sections.

Important APIs/types/functions: maps for per-CPU start timestamps and histogram slots, `log2`, `log2l`, `bpf_prog1` on `trace_preempt_off`, and `bpf_prog2` on `trace_preempt_on`.

Control flow: on preempt-off, records timestamp by CPU. On preempt-on, computes elapsed time, maps it into a log2 bucket, and increments the per-CPU histogram slot.

State and persistence: timestamps and histogram counts live in BPF maps.

Dependencies and integration: loaded by `lathist_user.c`, depends on kprobe-visible `trace_preempt_off`/`trace_preempt_on` symbols and preemption tracing support.

Risks: fixed `MAX_CPU` of 4 limits coverage. Symbol names may differ by config. Log bucket saturation can hide very high latencies.

Test signals: run under workload, observe nonzero histogram buckets per CPU, and verify attach errors on kernels without target symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/lathist_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/lathist_user.c -->
# sources/distributed-fs/ceph-client/samples/bpf/lathist_user.c

Purpose: userspace display for the preemption latency histogram BPF sample.

Important APIs/types/functions: `struct cpu_hist`, `stars`, `print_hist`, `get_data`, and `main` using libbpf program attach and map lookup APIs.

Control flow: opens and loads the kernel object, attaches programs, repeatedly reads histogram map entries, computes per-CPU maxima, and prints ASCII bar charts.

State and persistence: process-local `cpu_hist` mirrors BPF map data; BPF links live until process exit.

Dependencies and integration: pairs with `lathist_kern.c`, requires libbpf and kprobe permissions.

Risks: fixed CPU and bucket counts must match kernel side. Continuous terminal printing can obscure errors. No explicit signal cleanup path beyond process termination.

Test signals: attach successfully, induce preemption-off activity, and verify histogram bars grow.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/lathist_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/lwt_len_hist.bpf.c -->
# sources/distributed-fs/ceph-client/samples/bpf/lwt_len_hist.bpf.c

Purpose: lightweight tunnel BPF program that records packet length distribution.

Important APIs/types/functions: BPF array/hash map for histogram counts, `log2`, `log2l`, and `SEC("len_hist") int do_len_hist(struct __sk_buff *skb)`.

Control flow: handler reads `skb->len`, converts it to a log2 bucket, looks up the bucket count, increments it, and returns a pass verdict.

State and persistence: histogram counts are stored in a BPF map while the program is attached to a route/lwt hook.

Dependencies and integration: used by `lwt_len_hist_user.c` and `lwt_len_hist.sh`; requires BPF LWT support and `vmlinux.h` for CO-RE-style compilation.

Risks: bucket granularity is coarse by design. Attachment through `ip route encap bpf` is environment-dependent.

Test signals: attach via the script, send traffic over the route, and read nonzero histogram buckets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/lwt_len_hist.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/lwt_len_hist.sh -->
# sources/distributed-fs/ceph-client/samples/bpf/lwt_len_hist.sh

Purpose: setup script for the lightweight tunnel packet-length histogram sample.

Important APIs/types/functions: uses `ip` route commands to attach/detach BPF programs and invokes the user helper to display map contents.

Control flow: configures a route with BPF LWT program, triggers or expects traffic through that route, invokes the userspace map reader, and provides cleanup path for route state.

State and persistence: modifies routing table state and may pin/load BPF objects depending on invocation.

Dependencies and integration: pairs with `lwt_len_hist.bpf.c` and `lwt_len_hist_user.c`, requires iproute2 with BPF LWT support and administrative privileges.

Risks: route changes can affect host networking. Cleanup must run to restore route state. The script is sensitive to interface/address arguments.

Test signals: route attachment succeeds, traffic reaches the route, histogram output is nonzero, and cleanup removes the BPF route.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/lwt_len_hist.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/lwt_len_hist_user.c -->
# sources/distributed-fs/ceph-client/samples/bpf/lwt_len_hist_user.c

Purpose: reads and prints the packet-length histogram map for the LWT sample.

Important APIs/types/functions: `stars` helper and `main` that opens a pinned/known BPF map FD and iterates `MAX_INDEX` buckets.

Control flow: parses the map path or FD input, reads each bucket with `bpf_map_lookup_elem`, computes the maximum, and prints scaled ASCII bars.

State and persistence: no persistent state; reads map contents maintained by the attached BPF program.

Dependencies and integration: paired with `lwt_len_hist.bpf.c` and script setup, depends on libbpf/bpf syscall headers and a live histogram map.

Risks: assumes bucket count and value type match the BPF program. Output is only meaningful after traffic traverses the route.

Test signals: after LWT traffic, buckets corresponding to packet sizes show increasing counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/lwt_len_hist_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/map_perf_test.bpf.c -->
# sources/distributed-fs/ceph-client/samples/bpf/map_perf_test.bpf.c

Purpose: BPF-side workload for measuring map operation performance across map types.

Important APIs/types/functions: defines multiple maps including hash, percpu hash, lru hash, percpu lru hash, array, lpm trie, hash-of-maps, and lru hash-of-maps; syscall programs attached to getuid/geteuid/getgid and related syscalls stress update/lookup/delete paths.

Control flow: each syscall-attached program loops over keys or entries and performs map operations tailored to one test type. Some programs initialize values, some stress lookups, others exercise LRU or map-in-map behavior.

State and persistence: test maps store counters and synthetic values while the object is loaded. Map-in-map tests reference inner map FDs provided by userspace.

Dependencies and integration: controlled by `map_perf_test_user.c`; requires ksyscall BPF attachment, CO-RE/vmlinux headers, and libbpf skeleton/object loading.

Risks: benchmark results depend on CPU count, kernel map implementation, preallocation, syscall overhead, and verifier loop limits. Test programs deliberately do repeated operations and can add system overhead.

Test signals: userspace benchmark runs each selected test, map FDs are found, syscall triggers execute, and timing output is produced for enabled map types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/map_perf_test.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/map_perf_test_user.c -->
# sources/distributed-fs/ceph-client/samples/bpf/map_perf_test_user.c

Purpose: userspace benchmark driver for BPF map performance tests.

Important APIs/types/functions: time helper `time_get_ns`, enums `test_type` and `map_idx`, globals `map_fd`, `test_flags`, map sizing parameters, `check_test_flags`, `test_hash_prealloc`, `pre_test_lru_hash_lookup`, `do_test_lru`, map-in-map setup, option parsing, and benchmark loops.

Control flow: parses CLI options controlling test selection, entry counts, task count, and iterations; loads the BPF object; collects map FDs; optionally creates inner maps; forks or loops workloads; triggers attached BPF programs through syscalls; times operations; and prints per-test results.

State and persistence: uses BPF maps for benchmark state and process-local timing data. Child processes may be spawned for parallel stress. State ends when the object closes.

Dependencies and integration: pairs with `map_perf_test.bpf.c`; uses libbpf, BPF syscalls, process scheduling/fork APIs, and architecture syscall numbers.

Risks: timing is noisy and not a stable correctness metric. Large map sizes or task counts can consume significant memory/CPU. Some tests depend on CPU count up to `MAX_NR_CPUS` and map-in-map support.

Test signals: selected benchmark modes complete, timings are printed, no verifier/load failures, and repeated runs show roughly plausible relative performance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/map_perf_test_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/net_shared.h -->
# sources/distributed-fs/ceph-client/samples/bpf/net_shared.h

Purpose: provides small network protocol constants and byte-order helpers for BPF samples without pulling full userspace/kernel networking headers.

Important APIs/types/functions: defines address families, Ethernet protocol values, VLAN/MPLS-related constants, ICMPv6 protocol number, tc action codes, `IFNAMSIZ`, and `bpf_ntohs`/`bpf_htons` endian macros.

Control flow: no runtime flow; compile-time constants and macros only.

State and persistence: no state.

Dependencies and integration: included by networking BPF samples that need stable constants across kernel and userspace compile modes.

Risks: constants can become stale relative to kernel headers. Byte-order macros depend on `__BYTE_ORDER__` and only cover 16-bit conversions.

Test signals: networking samples compile without conflicting header definitions and protocol comparisons match expected packet types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/net_shared.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/offwaketime.bpf.c -->
# sources/distributed-fs/ceph-client/samples/bpf/offwaketime.bpf.c

Purpose: BPF tracing program that attributes off-CPU wait time to waker and target stack traces.

Important APIs/types/functions: `struct key_t`, `struct wokeby_t`, maps for start times, waker info, stack traces, and counts; `waker` kprobe on `try_to_wake_up`; `update_counts`; and `oncpu` handlers for sched switch or finish_task_switch depending on kernel version.

Control flow: when a task wakes another, records waker PID/name and stack. When a task is scheduled back on CPU, computes blocked delta, gathers target stack, combines waker/target identity into a key, and increments aggregate blocked time if above threshold.

State and persistence: BPF maps track last wake info, start timestamps, stack traces, and aggregate counts.

Dependencies and integration: paired with `offwaketime_user.c`; depends on scheduler tracepoints/kprobes, stack trace map support, BTF/CO-RE helpers, and kernel-version attach variants.

Risks: stack capture can fail or collide depending on `BPF_F_FAST_STACK_CMP`. Scheduler internals and probe signatures vary across kernels. High event rates can stress maps.

Test signals: run under blocking workloads, observe nonzero folded stacks and counts, and verify missing stack warnings are limited.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/offwaketime.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/offwaketime_user.c -->
# sources/distributed-fs/ceph-client/samples/bpf/offwaketime_user.c

Purpose: userspace loader and stack printer for off-wake-time tracing.

Important APIs/types/functions: map FDs, `print_ksym`, `struct key_t`, `print_stack`, `print_stacks`, signal handler `int_exit`, and `main` with libbpf load/attach.

Control flow: loads and attaches BPF programs, sleeps for a delay loop, then iterates aggregate count map and stack map to print waker and target stacks with symbol names.

State and persistence: BPF maps store counts/stacks; process uses trace helper symbol tables for printing.

Dependencies and integration: pairs with `offwaketime.bpf.c` and `trace_helpers`, requires kallsyms access, stack traces, and BPF privileges.

Risks: symbol resolution may be unavailable under restricted kallsyms settings. Stack IDs can be missing or stale. Signal handler exits directly after printing.

Test signals: run during blocked workload, confirm stack output contains waker and target frames and counts increase.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/offwaketime_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/parse_ldabs.c -->
# sources/distributed-fs/ceph-client/samples/bpf/parse_ldabs.c

Purpose: packet parser sample using legacy absolute load helpers/macros.

Important APIs/types/functions: `ip_is_fragment` and `SEC("ldabs") int handle_ingress(struct __sk_buff *skb)`. Includes `bpf_legacy.h` for `load_byte`/`load_half` style access.

Control flow: reads packet protocol/header fields through absolute loads, checks IPv4 fragmentation, and returns a classifier verdict for selected UDP traffic such as pktgen default port.

State and persistence: stateless per packet.

Dependencies and integration: built as a BPF object by the sample Makefile and usable with tc/socket parser tests.

Risks: absolute loads are legacy and less flexible than direct packet access. Header offsets must be correct and packet truncation handling depends on helper behavior.

Test signals: attach to a packet path and verify it accepts/drops or classifies expected UDP/IP packets without verifier errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/parse_ldabs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/parse_simple.c -->
# sources/distributed-fs/ceph-client/samples/bpf/parse_simple.c

Purpose: minimal direct-packet-access parser for Ethernet/IPv4/UDP traffic.

Important APIs/types/functions: local `struct eth_hdr` and `SEC("simple") int handle_ingress(struct __sk_buff *skb)`.

Control flow: computes pointers to Ethernet, IP, and UDP headers from `skb->data`, checks `data_end` bounds, validates protocol fields, and returns a packet verdict based on UDP port matching.

State and persistence: stateless per packet.

Dependencies and integration: compiled as a BPF parser sample and used by BPF sample tests comparing direct access parsing styles.

Risks: assumes no VLAN and fixed IPv4 header length. Any missing bounds check would be rejected by verifier; current simplicity limits protocol coverage.

Test signals: verifier accepts direct packet access, and pktgen/default UDP traffic exercises the expected path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/parse_simple.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/parse_varlen.c -->
# sources/distributed-fs/ceph-client/samples/bpf/parse_varlen.c

Purpose: packet parser sample handling variable-length headers such as VLAN tags, IPv4 IHL, IPv6, TCP, and UDP.

Important APIs/types/functions: helpers `tcp`, `udp`, `parse_ipv4`, `parse_ipv6`, and `SEC("varlen") int handle_ingress`. Defines protocol constants and optional debug.

Control flow: starts at Ethernet header, safely advances through one or more VLAN headers, dispatches to IPv4 or IPv6 parsing, handles fragments, computes transport offsets, validates TCP/UDP bounds, and returns verdicts based on selected port/protocol checks.

State and persistence: stateless per packet.

Dependencies and integration: uses BPF direct packet access and kernel networking headers; built by sample Makefile for parser demonstrations.

Risks: bounded parsing must satisfy the verifier, so loop/branch changes are sensitive. Protocol coverage is still sample-level, not a complete production parser. Fragmented or extension-header-heavy packets may bypass transport parsing.

Test signals: attach and send VLAN/non-VLAN IPv4/IPv6 TCP/UDP packets, confirm verifier acceptance and expected classification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/parse_varlen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/run_cookie_uid_helper_example.sh -->
# sources/distributed-fs/ceph-client/samples/bpf/run_cookie_uid_helper_example.sh

Purpose: wrapper for the cookie/UID helper sample that handles BPF filesystem pinning and iptables cleanup.

Important APIs/types/functions: invokes `cookie_uid_helper_example`, manages a pinned object path, installs/removes iptables `xt_bpf` rule, and forwards `-t` or `-s` test modes.

Control flow: prepares a pin path, runs the C sample with the chosen option, and on exit removes the iptables rule and pinned BPF object.

State and persistence: temporarily creates bpffs pins and iptables OUTPUT rules.

Dependencies and integration: requires bpffs, iptables with `-m bpf --object-pinned`, root privileges, and the compiled C sample.

Risks: cleanup depends on shell exit handling; interrupted or failed runs can leave firewall rules. Host iptables policy may affect unrelated traffic during the test.

Test signals: run both cookie and traffic modes, then verify no matching iptables rule or pinned object remains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/run_cookie_uid_helper_example.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/sampleip_kern.c -->
# sources/distributed-fs/ceph-client/samples/bpf/sampleip_kern.c

Purpose: BPF perf-event program that samples instruction pointers and counts occurrences.

Important APIs/types/functions: `MAX_IPS`, an IP-count map, and `SEC("perf_event") int do_sample(struct bpf_perf_event_data *ctx)`.

Control flow: on each perf sample, reads the instruction pointer from the perf event context, looks up the count in the map, initializes or increments it, and returns.

State and persistence: map stores sampled IP counts while attached.

Dependencies and integration: loaded by `sampleip_user.c`, attached to per-CPU perf events.

Risks: fixed maximum entries can drop unique IPs under broad workloads. Sampling frequency influences overhead and fidelity.

Test signals: run user sampler, wait for samples, and verify map contains kernel IPs with counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/sampleip_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/sampleip_user.c -->
# sources/distributed-fs/ceph-client/samples/bpf/sampleip_user.c

Purpose: userspace loader that attaches `sampleip` BPF program to perf sampling events and prints top sampled kernel IPs.

Important APIs/types/functions: `sampling_start`, `sampling_end`, `struct ipcount`, `count_cmp`, `print_ip_map`, `int_exit`, and CLI parsing in `main`. Uses `perf_event_open`, libbpf program attach to perf event FDs, and trace helper symbol lookup.

Control flow: parses frequency and duration, loads BPF object, finds map/program, opens per-CPU software/hardware perf events, attaches the BPF program, sleeps, detaches, reads the map, sorts counts, and prints symbolized IPs.

State and persistence: perf event FDs and BPF links are live during sampling; counts are in the BPF map until object close.

Dependencies and integration: pairs with `sampleip_kern.c`, depends on perf_event support, libbpf, kallsyms/trace helpers, and root or perf permissions.

Risks: high sampling frequency can add overhead. Symbolization depends on kernel symbols. CPU hotplug or large CPU counts can affect per-CPU setup.

Test signals: default run prints top IP samples after five seconds; changing frequency/duration changes count volume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/sampleip_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/sock_example.c -->
# sources/distributed-fs/ceph-client/samples/bpf/sock_example.c

Purpose: standalone socket filter example using a hand-written BPF instruction array.

Important APIs/types/functions: `test_sock`, a manual `struct bpf_insn` program, BPF map creation, socket creation, `setsockopt(SO_ATTACH_BPF)`, and map lookups for TCP/UDP/ICMP protocol counters.

Control flow: creates a map, loads a socket filter that reads IP protocol and increments map counters, opens a raw socket, attaches the program, sleeps while traffic arrives, reads counters, prints them, and exits.

State and persistence: map and program live through FDs during process lifetime; no pinned persistence.

Dependencies and integration: uses `sock_example.h` for raw socket setup, BPF syscall/libbpf helpers, and a network interface argument or default.

Risks: raw socket and BPF attach require privileges. Manual instruction offsets assume Ethernet/IP layout. Traffic must arrive during the sample interval.

Test signals: run on an active interface and observe protocol counters increasing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/sock_example.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/sock_example.h -->
# sources/distributed-fs/ceph-client/samples/bpf/sock_example.h

Purpose: shared helper for socket BPF samples to open a raw packet socket on a named interface.

Important APIs/types/functions: `open_raw_sock(const char *name)` uses `socket(PF_PACKET, SOCK_RAW|SOCK_NONBLOCK|SOCK_CLOEXEC, htons(ETH_P_ALL))`, `if_nametoindex`, `bind`, and `sockaddr_ll`.

Control flow: creates a packet socket, resolves interface index, binds to all Ethernet protocols on that interface, and returns the socket FD or exits on errors.

State and persistence: returns a live socket FD owned by the caller.

Dependencies and integration: included by `sockex*_user.c` and related socket samples; depends on Linux packet sockets and netdevice names.

Risks: helper exits the process on failure. Requires privileges and a valid interface. Nonblocking socket behavior matters for callers.

Test signals: opening on `lo` or another interface succeeds and attached socket filters receive traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/sock_example.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/sockex1_kern.c -->
# sources/distributed-fs/ceph-client/samples/bpf/sockex1_kern.c

Purpose: simple socket filter BPF program that counts packets by IPv4 protocol number.

Important APIs/types/functions: BPF map for counters and `SEC("socket1") int bpf_prog1(struct __sk_buff *skb)`.

Control flow: loads the IP protocol byte at Ethernet header plus IPv4 protocol offset, looks up a counter map entry, increments it, and returns zero/pass behavior appropriate for the sample.

State and persistence: protocol counters live in a BPF map while attached.

Dependencies and integration: loaded by `sockex1_user.c`, uses `bpf_legacy.h` absolute load helper and packet socket attachment.

Risks: assumes Ethernet plus IPv4 header offset and does not parse VLAN/IPv6. Map key is protocol byte.

Test signals: attach to interface, generate TCP/UDP/ICMP traffic, and see counters update.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/sockex1_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/sockex1_user.c -->
# sources/distributed-fs/ceph-client/samples/bpf/sockex1_user.c

Purpose: userspace loader for the first socket filter example.

Important APIs/types/functions: opens BPF object/program/map, loads program, opens raw socket with `open_raw_sock`, attaches BPF FD via `SO_ATTACH_BPF`, sleeps/loops, and reads TCP/UDP/ICMP protocol counters.

Control flow: load object, find map/program, attach to selected interface socket, periodically look up protocol keys and print counters.

State and persistence: live socket attachment and BPF map for process lifetime.

Dependencies and integration: pairs with `sockex1_kern.c` and `sock_example.h`; requires libbpf and packet socket privileges.

Risks: assumes map key protocol numbers and kernel object naming. Interface traffic must be present.

Test signals: counters increase for known traffic after attaching to an interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/sockex1_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/sockex2_kern.c -->
# sources/distributed-fs/ceph-client/samples/bpf/sockex2_kern.c

Purpose: socket filter BPF program that parses packets into flow keys and counts packets/bytes per flow.

Important APIs/types/functions: `struct flow_key_record`, VLAN/GRE helpers, `proto_ports_offset`, `ip_is_fragment`, `ipv6_addr_hash`, `parse_ip`, `parse_ipv6`, `flow_dissector`, `struct pair`, and `SEC("socket2") int bpf_prog2`.

Control flow: dissector parses Ethernet/VLAN, IPv4/IPv6, tunnels/fragments where supported, extracts protocol/addresses/ports into a flow key, and the main program increments a hash map value containing packet and byte counts.

State and persistence: flow counter hash map persists while attached.

Dependencies and integration: loaded by `sockex2_user.c`; uses BPF skb load helpers and network protocol headers.

Risks: parser supports a sample subset and hashes IPv6 addresses rather than storing full addresses. Header parsing must satisfy verifier bounds. Encapsulation support is limited.

Test signals: attach to traffic interface and observe map entries for flows with packet/byte counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/sockex2_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/sockex2_user.c -->
# sources/distributed-fs/ceph-client/samples/bpf/sockex2_user.c

Purpose: userspace loader and map dumper for flow-counting socket filter example 2.

Important APIs/types/functions: local `struct pair`, libbpf object/program/map lookup, `open_raw_sock`, socket attach, and map key iteration with `bpf_map_get_next_key`.

Control flow: loads object, attaches socket filter, sleeps or waits, then iterates flow map entries and prints packet/byte counts.

State and persistence: BPF map stores flow counters during process lifetime.

Dependencies and integration: pairs with `sockex2_kern.c`; requires interface argument and privileges.

Risks: user-side key interpretation is minimal compared with kernel-side flow key. High-cardinality traffic can fill the map.

Test signals: run during network traffic and verify flow entries are printed with nonzero counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/sockex2_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/sockex3_kern.c -->
# sources/distributed-fs/ceph-client/samples/bpf/sockex3_kern.c

Purpose: advanced socket filter flow dissector using tail calls and per-CPU scratch state.

Important APIs/types/functions: parser stage constants, `struct flow_key_record`, `struct globals`, per-CPU array for scratch state, program array for tail calls, flow stats map, `this_cpu_globals`, `update_stats`, parser helpers for IP/TCP/UDP/MPLS/VLAN, and multiple `SEC("socket...")` programs.

Control flow: main socket program initializes per-CPU globals and dispatches parsing stages through tail calls. Stages parse Ethernet, VLAN/MPLS, IPv4/IPv6, and transport headers, then update flow packet/byte counters.

State and persistence: per-CPU scratch map holds parser state during packet processing; hash map stores persistent flow counters; program array stores tail-call targets.

Dependencies and integration: loaded by `sockex3_user.c`, which must populate/locate program array and maps. Requires tail-call support and packet socket attachment.

Risks: tail-call setup is fragile; missing program array entries truncate parsing. Per-CPU scratch assumes one packet context per CPU program execution. Parser complexity increases verifier sensitivity.

Test signals: attach successfully, verify tail-call programs loaded, send mixed protocol traffic, and observe flow counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/sockex3_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/sockex3_user.c -->
# sources/distributed-fs/ceph-client/samples/bpf/sockex3_user.c

Purpose: userspace loader for the tail-call socket flow dissector sample.

Important APIs/types/functions: user-side `struct flow_key_record` and `struct pair`, BPF object/program/map FDs, program array setup, raw socket attach, and map iteration.

Control flow: loads BPF object, finds main program and maps, populates program array with parser stage FDs, attaches main program to a raw socket, waits for traffic, then dumps flow counters.

State and persistence: program array and flow hash map persist during object lifetime; socket attach persists until socket close.

Dependencies and integration: pairs with `sockex3_kern.c` and `sock_example.h`, requires libbpf, tail-call map support, and privileges.

Risks: user and kernel definitions of flow key must stay in sync. Missing parser program names or map names break tail calls. Output decoding is sample-level.

Test signals: verify all tail-call entries update successfully and flow map contains packet/byte counts after traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/sockex3_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/spintest.bpf.c -->
# sources/distributed-fs/ceph-client/samples/bpf/spintest.bpf.c

Purpose: BPF tracing sample that counts stack traces or instruction pointers around spinlock-related functions.

Important APIs/types/functions: maps for counts and stacks, macro `PROG(foo)` defining kprobe handlers, and probes for `spin_*lock*`, `*_spin_on_owner`, `_raw_spin_*lock*`, and selected hash map functions.

Control flow: each kprobe handler records `PT_REGS_IP(ctx)`, looks up a counter, initializes or increments it, and may collect stack IDs depending on map usage.

State and persistence: BPF maps hold counts and stack trace data while attached.

Dependencies and integration: loaded by `spintest_user.c`, depends on kprobe multi support for wildcard sections and trace helper symbolization.

Risks: wildcard kprobe availability varies by kernel. Probing hot spinlock paths can add overhead. Symbol names differ with config/compiler.

Test signals: attach links for all available programs, run workload, and see nonzero counts symbolized by the user program.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/spintest.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/spintest_user.c -->
# sources/distributed-fs/ceph-client/samples/bpf/spintest_user.c

Purpose: userspace loader and reporter for the spinlock tracing sample.

Important APIs/types/functions: loads BPF object, attaches each program, reads map entries, resolves symbols through `trace_helpers`, and prints counts.

Control flow: iterates BPF programs attaching them, sleeps for a requested duration or default loop, then iterates count map keys and prints symbolized IPs with counts.

State and persistence: BPF links and maps live during process execution; user state includes link array and symbol table.

Dependencies and integration: pairs with `spintest.bpf.c`, requires libbpf, kprobe permissions, and kallsyms access.

Risks: fixed link array size can be exceeded if program count grows. Some probes may fail on kernels without matching symbols. Running on hot paths can perturb performance.

Test signals: attach output shows links, map dump includes spinlock symbols with positive counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/spintest_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/syscall_nrs.c -->
# sources/distributed-fs/ceph-client/samples/bpf/syscall_nrs.c

Purpose: kbuild helper source for generating syscall number definitions for BPF samples.

Important APIs/types/functions: includes `<uapi/linux/unistd.h>` and `<linux/kbuild.h>`, defines `SYSNR(_NR) DEFINE(SYS##_NR, _NR)`, and `syscall_defines` emits selected syscall constants such as `__NR_write`.

Control flow: compiled to assembly and processed by kbuild `filechk` to produce `syscall_nrs.h`.

State and persistence: generated header persists in the build object directory.

Dependencies and integration: used by the BPF Makefile for samples needing architecture-specific syscall numbers.

Risks: generated output depends on target architecture UAPI headers. Missing syscall macros break generation.

Test signals: `samples/bpf/syscall_nrs.h` is generated and included by dependent BPF samples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/syscall_nrs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/syscall_tp_kern.c -->
# sources/distributed-fs/ceph-client/samples/bpf/syscall_tp_kern.c

Purpose: BPF tracepoint sample counting `open`, `openat`, and `openat2` syscall enter/exit events.

Important APIs/types/functions: syscall tracepoint argument structs, two BPF maps for counts, helper `count`, and handlers for `sys_enter_open`, `sys_enter_openat`, `sys_enter_openat2`, `sys_exit_open`, `sys_exit_openat`, and `sys_exit_openat2`.

Control flow: each handler calls `count` on the appropriate map, which increments a shared counter key for enter or exit events.

State and persistence: counts live in BPF maps while attached.

Dependencies and integration: loaded by `syscall_tp_user.c`, depends on syscall tracepoints and BPF tracepoint support.

Risks: tracepoint struct layouts must match kernel format. Some architectures may not expose all syscall variants the same way.

Test signals: user program runs test opens and verifies map counts match expected enter/exit counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/syscall_tp_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/syscall_tp_user.c -->
# sources/distributed-fs/ceph-client/samples/bpf/syscall_tp_user.c

Purpose: userspace test harness for syscall tracepoint BPF counters.

Important APIs/types/functions: `usage`, `verify_map`, `test`, and `main`. Uses libbpf object load/attach APIs, map lookups, and repeated `open` calls against a filename.

Control flow: parses number of parallel test objects, loads and attaches the BPF object(s), performs controlled `open` syscalls, then verifies each map counter against expected values.

State and persistence: BPF objects, links, and maps live during test execution. Test files are opened and closed by the process.

Dependencies and integration: pairs with `syscall_tp_kern.c`, requires syscall tracepoints and libbpf.

Risks: concurrent system activity can add open syscalls and disturb counts if tracepoints are global and maps are not filtered. Multiple loaded objects multiply event counts.

Test signals: `verify_map` succeeds for configured `nr_tests`; failures indicate attach/load/count mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/syscall_tp_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/task_fd_query_kern.c -->
# sources/distributed-fs/ceph-client/samples/bpf/task_fd_query_kern.c

Purpose: minimal BPF kprobe/kretprobe object used to demonstrate querying BPF program attachment information through task file descriptors.

Important APIs/types/functions: `SEC("kprobe/blk_mq_start_request") int bpf_prog1` and `SEC("kretprobe/__blk_account_io_done") int bpf_prog2`.

Control flow: both probe handlers return immediately; their purpose is attachment presence rather than data collection.

State and persistence: no maps or persistent BPF state beyond loaded programs and links/events.

Dependencies and integration: paired with `task_fd_query_user.c` in the broader sample suite; depends on block-layer symbols existing for kprobe attachment.

Risks: target symbols may be absent or renamed on some kernels/configs. Because handlers are no-ops, correctness is in attach/query behavior rather than runtime effects.

Test signals: user query sample can attach these probes and retrieve expected task FD query metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/task_fd_query_kern.c -->
