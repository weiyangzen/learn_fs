# subset-b-006764 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/hwmon_pmu.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/hwmon_pmu.h

Purpose: declares perf's userspace hwmon PMU interface. It models Linux hwmon sysfs files named like `<type><num>_<item>` as perf PMU events, so sensors can be discovered, parsed, exposed as event aliases, opened, and read through perf's PMU/evsel paths.

Important APIs and types: `enum hwmon_type` lists supported sysfs type prefixes such as `temp`, `fan`, `power`, `energy`, and `cpu`; `enum hwmon_item` lists suffix items such as `input`, `max`, `crit`, `alarm`, and `label`; `union hwmon_pmu_event_key` packs a 16-bit number and 8-bit type into a `long` key for event grouping. Public functions include `parse_hwmon_filename()`, `hwmon_pmu__new()`, `hwmon_pmu__exit()`, event iteration/count/existence helpers, parse-events term validation/configuration helpers, `perf_pmus__read_hwmon_pmus()`, and evsel open/read hooks.

Control flow: discovery starts from `perf_pmus__read_hwmon_pmus()`, which populates a PMU list using `hwmon_pmu__new()`. Parser and alias callbacks translate user event names into `perf_event_attr`/terms. Runtime evsels are identified by `perf_pmu__is_hwmon()` and `evsel__is_hwmon()`, opened with `evsel__hwmon_pmu_open()`, and sampled/read with `evsel__hwmon_pmu_read()`.

State and persistence: the header defines no storage directly, but the event-key union implies an internal event map keyed by type/number, with item metadata maintained by the corresponding implementation. No persistent disk writes are declared; persistent input is hwmon sysfs.

Dependencies and integration: depends on perf core PMU types, parse-events structures, evsel, `list_head`, and thread maps. It integrates the kernel hwmon sysfs ABI into perf PMU enumeration and event parsing.

Risks: filename parsing must match the hwmon ABI precisely, including alarms and labels. The bitfield union is endian-sensitive and explicitly exposed for testing. Sensor files are not perf events in the kernel sense, so open/read behavior must avoid assumptions made for hardware counters.

Test signals: focused tests should cover parse cases for all supported type/item names, alarm detection, big-endian key layout, alias validation errors, event iteration counts, and read/open behavior against temporary sysfs-like fixtures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/hwmon_pmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/include/asm/asm-offsets.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/include/asm/asm-offsets.h

Purpose: a two-line perf tools stub used to satisfy kernel assembly includes that expect `asm/asm-offsets.h`. It has no real offsets because the tools build is not compiling kernel objects that need generated structure offsets.

Important APIs and types: none. The only content is the SPDX tag and a `/* stub */` comment.

Control flow: none at runtime or compile time beyond successful inclusion.

State and persistence: none.

Dependencies and integration: exists under perf's local `util/include/asm` compatibility include tree. It lets imported architecture assembly, especially x86 helper assembly, include kernel-like paths without pulling generated kernel build artifacts into the tools build.

Risks: adding real definitions here could create divergence from generated kernel offsets and hide build problems. Removing it can break imported assembly includes.

Test signals: a tools/perf build that compiles imported assembly is the relevant signal. No unit-level behavior exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/include/asm/asm-offsets.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/include/asm/cpufeature.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/include/asm/cpufeature.h

Purpose: a perf tools compatibility header for kernel assembly that expects `asm/cpufeature.h`. It provides just enough symbol surface to include `arch/x86/lib/memcpy_64.S` in the userspace tools build.

Important APIs and types: defines include guard `PERF_CPUFEATURE_H` and `X86_FEATURE_REP_GOOD` as `0`. No functions or types are exported.

Control flow: compile-time only. Assembly or C preprocessor users can test or reference `X86_FEATURE_REP_GOOD`, but this tools stub does not implement runtime CPU feature probing.

State and persistence: none.

Dependencies and integration: part of perf's local kernel-header shim layer. It integrates with x86 assembly imports by satisfying a narrow macro dependency without carrying the kernel's full cpufeature system.

Risks: the dummy value is intentionally not a real feature bit. Any new users that treat it as real feature state would be wrong. The header should stay minimal and scoped to imported assembly compatibility.

Test signals: successful perf tools builds on x86 with imported memcpy assembly. A regression would usually surface as missing macro build failures or incorrect accidental use in non-stub code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/include/asm/cpufeature.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/include/asm/dwarf2.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/include/asm/dwarf2.h

Purpose: supplies no-op DWARF CFI annotation macros needed when perf tools include kernel x86 assembly such as `memcpy` or `memset` implementations. Userspace perf does not need the kernel's assembler CFI macro implementation for these imported files.

Important APIs and types: defines `CFI_STARTPROC`, `CFI_ENDPROC`, `CFI_REMEMBER_STATE`, and `CFI_RESTORE_STATE` as empty macros under guard `PERF_DWARF2_H`.

Control flow: compile-time macro expansion only. It strips CFI annotations from assembly sources in the tools context.

State and persistence: none.

Dependencies and integration: used by architecture assembly pulled into perf. It deliberately avoids depending on the kernel's full `asm/dwarf2.h`.

Risks: because CFI macros are empty, generated object unwind metadata may differ from kernel builds. That is acceptable for the imported helper usage but risky if broader assembly code starts relying on these macros for unwind correctness.

Test signals: assembler builds of imported x86 library code, plus smoke tests that exercise the copied routines if they are linked into tools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/include/asm/dwarf2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/include/asm/swab.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/include/asm/swab.h

Purpose: placeholder `asm/swab.h` for the perf tools include tree. It satisfies include paths that expect an architecture byte-swap header.

Important APIs and types: none; the file contains only `/* stub */`.

Control flow: none.

State and persistence: none.

Dependencies and integration: relies on other userspace or Linux helper headers to provide actual byte-swap APIs. This file's integration role is include compatibility, not functionality.

Risks: future code that expects architecture-specific swab definitions from this header would silently get nothing. Keep real byte-order behavior in explicit endian/byteswap headers.

Test signals: build coverage for source files that include kernel-like `asm/swab.h` through perf's compatibility include path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/include/asm/swab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/include/asm/system.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/include/asm/system.h

Purpose: empty compatibility header for code imported into perf tools that includes `asm/system.h`.

Important APIs and types: none.

Control flow: none.

State and persistence: none.

Dependencies and integration: belongs to the local tools include shim layer. It prevents userspace perf builds from depending on removed or kernel-only `asm/system.h` content.

Risks: because it is empty, it is safe only for includes that do not require actual barrier, system, or architecture operations. New code should include the precise userspace or Linux helper header it needs.

Test signals: compile-only. Any real dependency would surface as missing macro/function build errors in consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/include/asm/system.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/include/asm/uaccess.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/include/asm/uaccess.h

Purpose: userspace perf shim for kernel `asm/uaccess.h`. It provides trivial user-access macros to allow imported kernel-style code to compile when the "user" pointer is just an address perf can dereference in its own process context.

Important APIs and types: `__get_user(src, dest)` assigns `*dest` to `src` and returns `0`; `get_user` aliases `__get_user`; `access_ok(addr, size)` always returns `1`.

Control flow: macro-only. `__get_user` expands to a GNU statement expression with a direct load and success return.

State and persistence: no stored state; it may read pointed-to process memory directly.

Dependencies and integration: used by perf's imported helper code that references kernel uaccess primitives. It bypasses kernel access checks because perf tools run in userspace.

Risks: `access_ok()` always succeeding means invalid pointers are not guarded here. Direct dereference can segfault if used on untrusted or remote addresses. This must remain limited to code paths where the pointer is known to be valid in the perf process.

Test signals: build coverage plus sanitizer or crash tests for any consumer that could pass invalid pointers. Review signal is more important than unit tests because the macros are intentionally unsafe outside their narrow compatibility context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/include/asm/uaccess.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/include/dwarf-regs.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/include/dwarf-regs.h

Purpose: central declaration point for converting architecture register names and perf register numbers to DWARF register numbers, and for mapping DWARF register numbers to ftrace register strings when libdw support is available.

Important APIs and types: defines missing ELF machine constants for AArch64, C-SKY, and LoongArch; computes `EM_HOST` and `EF_HOST` from compiler architecture macros; defines sentinel pseudo-registers `DWARF_REG_PC` and `DWARF_REG_FB`. With `HAVE_LIBDW_SUPPORT`, it declares `get_dwarf_regstr()`, `get_dwarf_regnum()`, `get_dwarf_regnum_for_perf_regnum()`, architecture-specific conversion helpers, and `get_powerpc_regs()`. Without libdw, it provides inline no-op/failure fallbacks for `get_dwarf_regnum()` and `get_powerpc_regs()`.

Control flow: architecture selection happens at compile time. Runtime dispatch is delegated to implementation files through `machine`/`flags` arguments and architecture-specific helper functions.

State and persistence: none in this header. Conversions are deterministic from architecture, ABI flags, and input register name/number.

Dependencies and integration: includes `annotate.h` and `<elf.h>`, and integrates with perf annotation, probe, unwinding, and register display code. C-SKY ABI flags are handled explicitly because register numbering differs by ABI.

Risks: host architecture detection can fall back to `EM_NONE` on new architectures, reducing feature support. Stub fallbacks under no-libdw builds return failure, so callers must handle missing DWARF conversion. Mismatched ELF flags can yield wrong register mappings.

Test signals: architecture-specific conversion tests, no-libdw build tests, probe/annotation tests that resolve register operands, and cross-build coverage for every `EM_HOST` branch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/include/dwarf-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/include/linux/linkage.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/include/linux/linkage.h

Purpose: perf tools copy of kernel linkage annotation macros needed by imported assembly, especially x86 library assembly. It gives assembler sources macros for global/local/weak function labels, alignment, type, size, aliases, and PIC aliases without depending on the full kernel header stack.

Important APIs and types: defines `ASM_NL`, `__ALIGN`, `__ALIGN_STR`, `SYM_T_FUNC`, `SYM_A_ALIGN`, `SYM_L_GLOBAL/WEAK/LOCAL`, `ALIGN`, generic `SYM_ENTRY`, `SYM_START`, `SYM_END`, `SYM_ALIAS`, function-specific `SYM_FUNC_START*`, `SYM_FUNC_END`, `SYM_FUNC_ALIAS*`, `SYM_FUNC_ALIAS_MEMFUNC`, `SYM_TYPED_START`, `SYM_TYPED_FUNC_START`, and `SYM_PIC_ALIAS`.

Control flow: compile/assembly macro expansion only. Macro pairs emit symbol declarations and labels at start/end points and calculate `.size` metadata via assembler expressions.

State and persistence: no runtime state. Generated object metadata persists into object files through symbol type/size/alias directives.

Dependencies and integration: compatible with GNU assembler syntax and kernel imported assembly. The comments note a simplified non-CFI `SYM_TYPED_START` behavior for tools.

Risks: alignment is fixed to `.align 4,0x90`, which is x86-oriented. Variadic macro syntax and assembler directives assume a compatible assembler. Divergence from kernel linkage macros can break newly imported assembly that expects newer semantics.

Test signals: assembly build tests for imported perf routines, symbol table inspection for function type/size/alias correctness, and link tests around PIC aliases where used.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/include/linux/linkage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/intel-bts.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/intel-bts.c

Purpose: implements perf auxtrace support for Intel Branch Trace Store (BTS). It consumes AUX trace buffers containing fixed-size branch records, orders them, decodes source instructions when possible, feeds thread-stack call/return tracking, and synthesizes perf branch samples or auxtrace errors.

Important APIs and types: `struct intel_bts` owns auxtrace callbacks, queues, heap, PMU metadata, TSC conversion, synthesis options, branch event metadata, and event counters. `struct intel_bts_queue` tracks one auxtrace queue's current buffer, thread identity, CPU, instruction decode cache, and sample flags. `struct branch` is the on-trace record with little-endian `from`, `to`, and `misc`. The public entry point is `intel_bts_process_auxtrace_info()`.

Control flow: auxtrace-info parsing allocates `intel_bts`, installs callbacks into `session->auxtrace`, reads private metadata, configures itrace synth options, synthesizes a branch event if requested, and processes indexed queues. AUXTRACE events add buffers unless index data has already populated queues. Ordered perf events call `intel_bts_process_event()`, which converts event time to TSC, updates queues, drains heap entries up to that timestamp, flushes on thread exit, and reports lost trace on truncated AUX. Buffer processing maps data, optionally removes snapshot overlap, walks branch records, decodes instruction type through the Intel PT instruction decoder, updates thread-stack state, filters by call/return options, and delivers synthetic samples.

State and persistence: queue state persists across ordered events through `auxtrace_queue->priv`. Heap ordering persists pending buffer references. Snapshot overlap mutates `use_data/use_size`; data mappings are dropped after processing. No durable writes are made.

Dependencies and integration: depends on perf auxtrace queues/heaps, sessions, evlists, evsels, machines, threads, `thread-stack`, synthetic events, TSC conversion, and `intel-pt-insn-decoder`.

Risks: requires ordered events; split buffers are unsupported; instruction lookup can fail and optionally emits errors; overlap removal is byte-pattern based; no KVM support is noted by using host machine only. Endian conversion is manual for trace records.

Test signals: decode BTS samples with branch synthesis on/off, snapshot overlap fixtures, truncated AUX error delivery, thread-exit flushing, call/return filtering, big-endian record conversion, and instruction lookup failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/intel-bts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/intel-bts.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/intel-bts.h

Purpose: public interface and AUXTRACE private metadata contract for perf's Intel BTS support.

Important APIs and types: defines `INTEL_BTS_PMU_NAME` as `"intel_bts"`. The anonymous enum defines indices into the auxtrace-info private array: PMU type, time conversion fields, `cap_user_time_zero`, snapshot mode, and max. `INTEL_BTS_AUXTRACE_PRIV_SIZE` expresses the private payload size in bytes. Declares `intel_bts_recording_init()` for recording setup and `intel_bts_process_auxtrace_info()` for report/inject decode setup.

Control flow: record-side code uses the PMU name and private indices to serialize metadata. Process-side code passes AUXTRACE_INFO events to `intel_bts_process_auxtrace_info()`, which installs the runtime auxtrace callbacks implemented in `intel-bts.c`.

State and persistence: the enum is a persisted file-format contract inside perf.data auxtrace-info records. Reordering or changing indices breaks compatibility with existing recordings.

Dependencies and integration: forward-declares perf session/tool/event and auxtrace types to keep the header light. Integrates perf record metadata generation with perf report/inject decode.

Risks: comment text says "Intel Processor Trace support" although this header is BTS-specific, which can confuse readers. The private array layout must stay stable.

Test signals: perf record/report round trips for BTS data, validation of private payload size, and compatibility tests against old perf.data files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/intel-bts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/intel-pt-decoder/intel-pt-decoder.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/intel-pt-decoder/intel-pt-decoder.c

Purpose: full Intel Processor Trace packet stream decoder. It turns raw PT packets and caller-provided instruction walking into `intel_pt_state` samples: branches, instruction samples, transaction events, PTWRITE, power/events, PSB events, block items, cycle/timestamp data, trace begin/end, and decode errors.

Important APIs and types: public functions are `intel_pt_decoder_new()`, `intel_pt_decoder_free()`, `intel_pt_decode()`, `intel_pt_fast_forward()`, `intel_pt_find_overlap()`, `intel_pt__strerror()`, and `intel_pt_set_first_timestamp()`. Internally `struct intel_pt_decoder` stores callbacks, current buffer, compressed IP state, TNT packet state, return-compression stack, packet context, PSB sync state, timing conversion state, CBR/CYC/MTC/TMA data, VMCS/TSC correlation data, pending FUP-attached event flags, block item state, and loop protection counters.

Control flow: construction copies callback parameters and timing configuration. `intel_pt_decode()` dispatches on `pkt_state`: synchronize to PSB, synchronize to IP after errors, walk normal trace, continue TNT/TIP/FUP handling, resample, or run VM time correlation. Packet walking uses `intel_pt_get_next_packet()` and the packet decoder. TNT drives conditional branch decisions; TIP handles indirect branches and trace enable/disable; FUP attaches asynchronous events and may be followed by TIP; PSB/PSBEND resynchronize and collect side-band timing/mode data. Instruction walking is delegated to `params->walk_insn`, while `get_trace` supplies buffers and `lookahead` supports fast-forward.

State and persistence: all decode progress is in-memory. It mutates decoder state heavily across calls, including IP, last-IP compression, return stack, transaction flags, timestamps, cycle counts, and pending event payloads. VM time correlation can rewrite mmap-backed trace bytes for translated guest TSC unless dry-run is set.

Dependencies and integration: depends on auxtrace alignment constants, PT packet decoder, x86 instruction decoder, PT log, and consumer callbacks supplied by higher perf auxtrace code.

Risks: high state-machine complexity, many recovery paths, packet split handling, timestamp wrap/slip heuristics, VM TSC offset guessing, infinite-loop protection, and unsupported/malformed packet cases. Callback correctness is critical; bad instruction walking produces mismatches or resync.

Test signals: packet-stream fixtures for TNT/TIP/FUP/PSB/OVF/PTWRITE/power/block events, timestamp conversion cases, VM correlation dry-run and rewrite cases, overlap detection with and without TSC, fast-forward positioning, error-code mapping, and loop-limit behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/intel-pt-decoder/intel-pt-decoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/intel-pt-decoder/intel-pt-decoder.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/intel-pt-decoder/intel-pt-decoder.h

Purpose: public contract for the Intel PT decoder. It defines sample types, error codes, parameter callbacks, decoded state layout, PT block item storage, VMCS timing metadata, and public decoder functions.

Important APIs and types: `enum intel_pt_sample_type`, `enum intel_pt_period_type`, error enums, `enum intel_pt_param_flags`, block type enums and `intel_pt_blk_type_pos()`, `struct intel_pt_blk_items`, `struct intel_pt_vmcs_info`, `struct intel_pt_evd`, `struct intel_pt_state`, `struct intel_pt_buffer`, `struct intel_pt_params`, and opaque `struct intel_pt_decoder`. Function declarations cover lifecycle, decode, fast-forward, overlap detection, error text, and first timestamp.

Control flow: callers fill `intel_pt_params` with `get_trace`, `walk_insn`, optional `pgd_ip`, `lookahead`, and `findnew_vmcs_info` callbacks plus configuration flags. They repeatedly call `intel_pt_decode()` and consume the returned stable pointer until an error/no-data state is reported.

State and persistence: `intel_pt_state` is the per-sample output and is owned by the decoder until the next decode call. `intel_pt_vmcs_info` nodes are stored by the caller, typically in an rb-tree, and carry learned VMCS TSC offsets.

Dependencies and integration: includes Linux rbtree and the PT instruction decoder. It is consumed by perf Intel PT auxtrace integration and, indirectly, by tooling that needs branch/instruction synthesis.

Risks: flags overlap intentionally (`INTEL_PT_IFLAG` and `INTEL_PT_ASYNC` both use bit 2 in different contexts), so consumers must interpret them by sample type. Struct layout is broad and easy to misuse if fields are read without checking `type` bits.

Test signals: compile/API tests, decode consumer tests that validate state fields for each sample type, VMCS info storage tests, and ABI review before changing enum values or struct semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/intel-pt-decoder/intel-pt-decoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/intel-pt-decoder/intel-pt-insn-decoder.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/intel-pt-decoder/intel-pt-insn-decoder.c

Purpose: classifies decoded x86 instructions for Intel PT and BTS consumers. It identifies branch operation kind, branch target encoding, instruction length, relative displacement, and perf IP flag mapping.

Important APIs and types: exports `intel_pt_get_insn()`, `arch_is_uncond_branch()`, `dump_insn()`, `intel_pt_insn_name()`, `intel_pt_insn_desc()`, and `intel_pt_insn_type()`. Internally `intel_pt_insn_decoder()` maps x86 opcode bytes and ModRM extension fields to `INTEL_PT_OP_*` and `INTEL_PT_BR_*`.

Control flow: `intel_pt_get_insn()` calls the kernel x86 `insn_decode()` helper in 32- or 64-bit mode, rejects bad or truncated instructions, then classifies opcodes. Conditional and relative unconditional branches copy the immediate displacement with endian handling. `intel_pt_insn_type()` converts operation classes into `PERF_IP_FLAG_*` combinations used by synthesized branch samples.

State and persistence: no global mutable state except the static `branch_name` table. Each call fills a caller-owned `struct intel_pt_insn` and copies up to 16 bytes of instruction data.

Dependencies and integration: uses `arch/x86/include/asm/insn.h`, perf event/sample headers, and dump instruction helpers. It is called by Intel PT decode walking and Intel BTS branch classification.

Risks: x86 opcode coverage must track new branch-like instructions. AVX/XOP are explicitly treated as non-branch. `dump_insn()` updates `left` incorrectly by subtracting cumulative `n`, which is a possible formatting robustness issue if changed or extended. `branch_name[op]` assumes valid enum input.

Test signals: opcode fixtures for calls, returns, jcc, loops, jumps, syscall/sysret, interrupts, vmlaunch/vmresume, ERETS/ERETU, jmpabs, invalid/truncated bytes, endian displacement handling, and perf flag mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/intel-pt-decoder/intel-pt-insn-decoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/intel-pt-decoder/intel-pt-insn-decoder.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/intel-pt-decoder/intel-pt-insn-decoder.h

Purpose: declares the instruction classification surface used by Intel PT and BTS code.

Important APIs and types: defines `INTEL_PT_INSN_DESC_MAX`, `INTEL_PT_INSN_BUF_SZ`, `enum intel_pt_insn_op`, `enum intel_pt_insn_branch`, and `struct intel_pt_insn` with operation, branch class, emulated PTWRITE flag, length, relative displacement, and copied bytes. Declares decode, name, description, and perf-flag conversion functions.

Control flow: consumers call `intel_pt_get_insn()` with raw x86 bytes and execution mode, then inspect `op`, `branch`, `length`, and `rel`. Formatting helpers are for logs/UI; `intel_pt_insn_type()` feeds perf sample flags.

State and persistence: no persistent state. The copied instruction buffer in `struct intel_pt_insn` lets later sample/log code retain bytes after the source memory is gone.

Dependencies and integration: includes standard size/int headers; implementations integrate with the x86 instruction decoder and perf sample flags.

Risks: buffer size is fixed at 16 bytes, matching x86 maximum instruction length; changing it affects sample storage assumptions. `bool` is used without including `<stdbool.h>` here, so this header relies on transitive includes in current build contexts.

Test signals: standalone include/build checks, decode fixtures, and consumers verifying the instruction buffer remains valid in synthesized events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/intel-pt-decoder/intel-pt-insn-decoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/intel-pt-decoder/intel-pt-log.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/intel-pt-decoder/intel-pt-log.c

Purpose: optional debug logging backend for Intel PT decoding. It prints decoded packets, decoded instructions, and formatted messages either to stdout, to a named log file, or into an in-memory circular buffer that can be dumped on error.

Important APIs and types: global state includes `intel_pt_enable_logging`, file pointer `f`, `log_name`, dump-on-error settings, and `struct log_buf`. Public functions enable/disable logging, set log name, expose the file pointer, dump buffered logs, and emit packet/instruction/message records through `__intel_pt_log*` functions.

Control flow: logging macros in the header guard calls with `intel_pt_enable_logging`. First real log lazily opens the backend. If dump-on-error is enabled, `fopencookie()` routes writes into `log_buf__write()`; `intel_pt_log_dump_buf()` flushes and writes the circular buffer to the backend. Packet/instruction printers format raw bytes plus decoder descriptions.

State and persistence: logging is process-global, not per decoder. File-backed logs persist as `<name>.log`; buffered logs persist only until dumped or closed. `intel_pt_log_disable()` flushes but does not close the file.

Dependencies and integration: uses packet and instruction description helpers, stdio, GNU `fopencookie`, and Linux allocation helpers. Integrated throughout `intel-pt-decoder.c`.

Risks: global state is not thread-safe; `intel_pt_log_set_name()` uses `strncpy` plus `strcat` and assumes enough NUL termination from the static zeroed buffer; repeated enable/open behavior can retain an old file pointer. Circular buffer drops partial first lines after wrap.

Test signals: logging disabled no-op behavior, file-name creation, packet/instruction formatting, circular wrap and dump behavior, and error-path dump-on-error tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/intel-pt-decoder/intel-pt-log.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/intel-pt-decoder/intel-pt-log.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/intel-pt-decoder/intel-pt-log.h

Purpose: declares Intel PT logging controls and provides low-overhead logging macros that compile into cheap enabled checks.

Important APIs and types: declares `intel_pt_log_fp()`, `intel_pt_log_enable()`, `intel_pt_log_disable()`, `intel_pt_log_set_name()`, `intel_pt_log_dump_buf()`, packet and instruction logging functions, and formatted `__intel_pt_log()`. Macros `intel_pt_log`, `intel_pt_log_packet`, `intel_pt_log_insn`, and `intel_pt_log_insn_no_data` call the backing functions only when `intel_pt_enable_logging` is true. Inline helpers log common "at", "to", and variable messages.

Control flow: decoder code invokes macros freely; when disabled, only a boolean branch is paid. When enabled, work is delegated to `intel-pt-log.c`.

State and persistence: declares external global `intel_pt_enable_logging`; actual file/buffer state is in the C file.

Dependencies and integration: includes Linux compiler attributes for printf checking and standard integer formatting macros. It is included by the packet/instruction decoder logging paths and main PT decoder.

Risks: macros evaluate arguments only when enabled, which is intended but can hide side effects if callers pass expressions with side effects. Global logging configuration applies to all decoders.

Test signals: compile-time printf attribute warnings, disabled macro side-effect expectations, and integration tests confirming logs appear only after enable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/intel-pt-decoder/intel-pt-log.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/intel-pt-decoder/intel-pt-pkt-decoder.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/intel-pt-decoder/intel-pt-pkt-decoder.c

Purpose: low-level Intel PT packet decoder. It parses raw bytes into `struct intel_pt_pkt` records, maintains minimal block-packet context, and formats packet descriptions for logs.

Important APIs and types: exports `intel_pt_pkt_name()`, `intel_pt_get_packet()`, `intel_pt_upd_pkt_ctx()`, and `intel_pt_pkt_desc()`. Static helpers parse long/short TNT, IP packets, CYC, PIP, TSC, TMA, MODE, MTC, VMCS, PSB/PSBEND, CBR, OVF, MNT, PTWRITE, EXSTOP, MWAIT/PWRE/PWRX, BBP/BIP/BEP, CFE, and EVD packets.

Control flow: `intel_pt_get_packet()` calls `intel_pt_do_get_packet()` using the current context. If a packet is decoded, it absorbs trailing PAD bytes up to eight bytes, then updates context. In block context, byte patterns with low bits matching BIP are decoded as 4- or 8-byte BIP instead of TNT. Description formatting switches by packet type to produce human-readable payload details.

State and persistence: the decoder itself is stateless except for the caller-owned `enum intel_pt_pkt_ctx`, which tracks whether BIP packets are valid between BBP and BEP. Parsed packet data is returned in caller-owned storage.

Dependencies and integration: uses Linux unaligned helpers, endian conversion, compiler fallthrough, and constants from the header. The main PT decoder uses it for every packet and the log layer uses descriptions.

Risks: packet length/count handling is security-sensitive because input is trace data. Need-more-bytes and bad-packet distinctions drive resync behavior. Context mistakes can misclassify BIP as TNT. Some payload extraction uses partial little-endian copies, so big-endian behavior depends on helper correctness.

Test signals: byte fixtures for every packet type, boundary lengths returning `INTEL_PT_NEED_MORE_BYTES`, malformed encodings returning `INTEL_PT_BAD_PACKET`, BBP/BIP/BEP context transitions, trailing PAD absorption, and description string checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/intel-pt-decoder/intel-pt-pkt-decoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/intel-pt-decoder/intel-pt-pkt-decoder.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/intel-pt-decoder/intel-pt-pkt-decoder.h

Purpose: public packet-level Intel PT decoder interface and raw packet constants.

Important APIs and types: defines description and packet size limits, error return values `INTEL_PT_NEED_MORE_BYTES` and `INTEL_PT_BAD_PACKET`, PSB byte string/length, VMX NR flag, `enum intel_pt_pkt_type`, `struct intel_pt_pkt`, and `enum intel_pt_pkt_ctx`. Declares packet name, decode, context update, and description functions.

Control flow: callers maintain a packet context, pass a byte buffer to `intel_pt_get_packet()`, advance by the positive returned length, and feed the same context back for later packets. `intel_pt_upd_pkt_ctx()` is exposed for users that need to update context manually.

State and persistence: no global state. The packet context is the only cross-call state and exists to disambiguate BIP encodings while inside block payloads.

Dependencies and integration: consumed by `intel-pt-decoder.c` and `intel-pt-log.c`. It is deliberately independent of perf session structures.

Risks: enum values are used in large switch statements across the decoder and logger, so additions require exhaustive updates. Callers must treat negative returns as non-lengths and must not advance incorrectly on partial packets.

Test signals: header compile tests, exhaustive switch warnings when adding packet types, and packet stream tests that verify caller context is preserved across BBP/BIP/BEP sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/intel-pt-decoder/intel-pt-pkt-decoder.h -->
