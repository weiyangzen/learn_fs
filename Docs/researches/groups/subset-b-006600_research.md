# subset-b-006600 Research

Grouped research for the x86 perf test and utility files in subset-b-006600. Each file section is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/insn-x86-dat-src.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/insn-x86-dat-src.c

Purpose: This is the source corpus for perf's "x86 instruction decoder - new instructions" test. It is a synthetic C file whose `main()` body contains thousands of `asm volatile()` instructions bracketed by `rdtsc` start/stop markers. `tools/perf/arch/x86/tests/gen-insn-x86-dat.sh` compiles this source in 64-bit and 32-bit modes, disassembles the object, and pipes the result through `gen-insn-x86-dat.awk` to produce `insn-x86-dat-64.c` and `insn-x86-dat-32.c`, which are then included by `insn-x86.c`.

Important APIs, types, and functions: The only C function is `int main(void)`, but the file's real API is its generated test-data contract. Inline comments of the form `Expecting: <op> <branch> <rel>` are parsed by the generator and become expected Intel PT instruction classification fields. The `rdtsc` marker comments are hard integration points for the awk script and must not be renamed. The emitted data ultimately maps instruction bytes to expected length, relative target displacement, operation class, branch class, and objdump text.

Control flow: The control flow is deliberately inert. The generated program is not meant to execute meaningful logic; it is compiled so objdump can emit bytes for the inline assembly between the start and stop markers. The file has an `#ifdef __x86_64__` block for x86-64-specific encodings and an `#else` block for 32-bit alternatives, then a shared tail of instructions. Several branch labels and `.byte` sequences are present only to force specific encodings, such as the `jmpabs` workaround where gas lacks a mnemonic.

Coverage and state: The corpus covers AVX-512 opcode-map collisions, mask-register operations, EVEX/VEX encodings, gathers/scatters, broadcast/compress/expand, FMA and AES/GFNI families, MPX `bnd*` forms, branch prefixes (`bnd`, `notrack`), PTWRITE, waitpkg, MOVDIR, ENQCMD, CET shadow-stack and ENDBR instructions, AMX, user interrupts, AVX512-FP16, Key Locker, remote atomics, APX/REX2 extended registers and three-operand integer forms, suppress-status-flags forms, AVX VNNI/IFMA/SHA/SM3/SM4, prefetch variants, MSR-list and user MSR operations, SGX, PCONFIG, WBNOINVD, SERIALIZE, HRESET, and TSX load-address tracking instructions. State is build-time only: edits to this source must be regenerated into the two included data files before the test sees them.

Dependencies and integration points: It depends on assembler support for the listed mnemonics and on objdump output remaining compatible with `gen-insn-x86-dat.awk`. It is integrated by `insn-x86.c`, not linked into perf as a runtime test body. Comments with `Expecting:` are semantically significant and feed the Intel PT branch classifier expectations. The generated data also depends on mode-specific operand and addressing choices, so the same mnemonic can have different relative-displacement expectations in 32-bit and 64-bit builds.

Risks: The biggest risk is silent drift between this source and `insn-x86-dat-32.c`/`insn-x86-dat-64.c` if a contributor changes this file without regenerating and committing outputs. Toolchain variance is also a risk: unsupported mnemonics, different objdump formatting, or assembler syntax changes can break regeneration. Because the file exercises cutting-edge ISA features, older build environments may fail before perf tests run. Branch expectations are fragile around instruction length, prefixes, and relative offsets.

Test signals: The direct signal is `perf test "x86 instruction decoder - new instructions"`, implemented by `test__insn_x86`. A strong maintenance signal is that regenerating the data files from this source should yield the committed `insn-x86-dat-32.c` and `insn-x86-dat-64.c` without unexpected diffs. Failures usually appear as mismatched decoded length, Intel PT op/branch class, or relative displacement in verbose perf test output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/insn-x86-dat-src.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/insn-x86.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/insn-x86.c

Purpose: This file implements the runtime perf test for x86 instruction decoding and Intel PT instruction classification. It consumes the generated instruction byte tables from `insn-x86-dat-32.c` and `insn-x86-dat-64.c`, decodes each instruction in the kernel x86 instruction decoder, and cross-checks Intel PT's higher-level operation and branch categorization.

Important APIs, types, and functions: `struct test_data` stores the bytes, expected decoded length, expected relative target, expected Intel PT op string, expected branch string, and assembler rendering. `get_op()` maps strings such as `call`, `ret`, `jcc`, `syscall`, `vmentry`, `erets`, and `eretu` to `enum intel_pt_insn_op` values. `get_branch()` maps `indirect`, `conditional`, and `unconditional` strings to Intel PT branch classes. `test_data_item()` performs one decode and comparison. `test_data_set()` iterates a sentinel-terminated array. `test__insn_x86()` is the exported test-suite entry point.

Control flow: `test__insn_x86()` runs the 32-bit data set with `INSN_MODE_32`, then the 64-bit data set with `INSN_MODE_64`. For each item, `insn_decode()` validates instruction length, then `intel_pt_get_insn()` validates the Intel PT operation, branch type, and relative displacement. The loop continues through all entries even if one item fails, preserving multiple debug messages before returning failure.

State and persistence: State is local to the test invocation. The static arrays are generated at build time and included into the binary. No external files are read at runtime, and no persistent state is written. The sentinel item with `expected_length == 0` terminates each array.

Dependencies and integration points: The test depends on `arch/x86/include/asm/insn.h` for `struct insn` and `insn_decode()`, `intel-pt-decoder/intel-pt-insn-decoder.h` for `intel_pt_get_insn()`, and perf test infrastructure headers for result conventions and debug logging. It is registered through the x86 arch test suite (`arch-tests.c`) under "x86 instruction decoder - new instructions". It also depends on the generator pipeline documented in the source-data file.

Risks: String-to-enum maps must stay synchronized with Intel PT decoder enum additions; new operation classes require updates here or generated expectations will fail with `-1`. The test assumes generated data files match the current source corpus and current decoder behavior. Unsupported instruction bytes or mode-specific decode changes can cause length or relative-address mismatches.

Test signals: `perf test -v "x86 instruction decoder - new instructions"` shows per-instruction "Decoded ok" or detailed failure messages for length, op, branch, or `rel`. Build failures can indicate stale generated files or missing enum support for a new expected op.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/insn-x86.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/intel-pt-test.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/intel-pt-test.c

Purpose: This file provides two x86 perf tests for Intel Processor Trace. The first validates the Intel PT packet decoder against hand-written packet byte sequences. The second validates that Intel PT capabilities on hybrid x86 systems remain compatible across CPUs relative to CPU 0.

Important APIs, types, and functions: `struct test_data` describes packet input length, bytes, initial packet context, expected `struct intel_pt_pkt`, expected new context, and whether context must remain unchanged. `dump_packet()`, `decoding_failed()`, and `fail()` produce verbose diagnostics. `test_one()` calls `intel_pt_get_packet()` and validates decoded length, type, count, payload, and context. `test__intel_pt_pkt_decoder()` iterates the static packet table. For hybrid checks, `struct cpuid_result` and `struct pt_caps` hold CPUID leaf 20 subleaf values. `setaffinity()`, `get_pt_caps()`, `is_hybrid()`, `compare_caps()`, and `test__intel_pt_hybrid_compat()` implement the cross-CPU capability test.

Control flow: The packet test walks a sentinel-terminated table covering PAD, TNT, TIP, PGE/PGD/FUP, PIP, MODE, TRACESTOP, CBR, TSC, MTC, TMA, CYC, VMCS, OVF, PSB/PSBEND, MNT, PTWRITE, EXSTOP, MWAIT, power packets, block packets, CFE, and EVD. Each row seeds the packet context, decodes one packet, optionally verifies that context update logic leaves all contexts unchanged for packets that should not affect context, then compares fields. The hybrid test first checks CPUID leaf 7 bit 15 for hybrid support, skips on non-hybrid hosts, snapshots CPU 0 PT caps, then iterates CPUs and compares masked capability subsets.

State and persistence: The packet decoder test is pure and in-memory. The hybrid test temporarily changes process CPU affinity with `sched_setaffinity()` to query CPUID on specific CPUs; it does not restore affinity explicitly in this file. No state is persisted. Skip reason is stored in the current `test_suite` entry when the system is not hybrid.

Dependencies and integration points: It depends on `intel-pt-decoder/intel-pt-pkt-decoder.h` for packet types and decoder functions, `../util/cpuid.h` for the inline CPUID wrapper, `cpumap.h` for CPU enumeration, and perf test/debug infrastructure. The tests are registered in the x86 Intel PT suite as "Intel PT packet decoder" and "Intel PT hybrid CPU compatibility".

Risks: Packet expectations are bit-exact; any legitimate decoder semantic change must update the table. Context-transition bugs are especially easy to miss if a packet is incorrectly marked `ctx_unchanged`. The hybrid test is hardware-dependent, can be affected by offline CPUs or affinity restrictions, and assumes CPU 0 is a sufficient baseline. The CPUID comparison masks only selected fields, so it intentionally does not prove full equality.

Test signals: `perf test -v "Intel PT packet decoder"` should decode all rows and print decoded packet descriptions. Hybrid systems should run `perf test -v "Intel PT hybrid CPU compatibility"`; non-hybrid systems should skip with reason "not hybrid". Failures point to the mismatched packet field, CPUID subleaf/register, or address-filter count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/intel-pt-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/regs_load.S -->
# sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/regs_load.S

Purpose: This assembly file implements `perf_regs_load`, a test helper that snapshots general-purpose registers into a caller-provided `u64` register array. It is used by x86 perf unwind/register tests to seed expected register state.

Important APIs, types, and functions: The exported symbol is `perf_regs_load`, declared by the x86 perf registers header and defined with `SYM_FUNC_START`/`SYM_FUNC_END`. The file defines byte offsets for AX, BX, CX, DX, SI, DI, BP, SP, IP, FLAGS, segment registers, and x86-64-only R8 through R15. It has separate implementations under `HAVE_ARCH_X86_64_SUPPORT` and the 32-bit fallback.

Control flow: On x86-64, `%rdi` points at the destination array. The function stores all general registers, records the caller stack pointer as `8(%rsp)` to exclude the helper call frame, records the return address from `0(%rsp)` as IP, zeroes flags and segment slots, stores R8-R15, and returns. On 32-bit, it saves the incoming destination pointer from the stack into `%edi`, handles `%edi` specially via a push/pop sequence so the original DI value is captured, stores 32-bit registers into 64-bit-spaced slots, records stack and return IP, zeroes unavailable metadata slots, and returns.

State and persistence: The function writes only to the destination register buffer supplied by the caller. It clobbers scratch registers as part of the snapshot process and intentionally records an adjusted SP/IP view. No persistent state exists.

Dependencies and integration points: It depends on Linux `linkage.h` symbol macros and on the register-index ABI expected by `arch/x86/include/perf_regs.h` and dwarf-unwind tests. The `.note.GNU-stack` section declares a non-executable stack for the assembled object.

Risks: Offset constants must stay aligned with perf's register numbering. The helper is ABI-sensitive: changing stack adjustment from `8(%rsp)` or `4(%esp)` would change unwind-test expectations. The 32-bit path's DI save/restore is easy to break because `%edi` is both an input pointer and a register under test.

Test signals: x86 `perf test` dwarf unwind/register tests using `perf_regs_load()` should pass on both 32-bit and 64-bit builds. Linker warnings about executable stack would indicate the GNU-stack marker was lost.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/regs_load.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/topdown.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/topdown.c

Purpose: This file implements the "x86 topdown" perf test. It scans core PMU events and verifies that topdown slots and topdown metric classification helpers report the expected categories for parsed PMU event names.

Important APIs, types, and functions: `event_cb()` is the per-PMU-event callback. It constructs a parse string of the form `pmu/name/`, parses it into an `evlist`, and inspects each `evsel`. It uses `arch_is_topdown_slots()`, `arch_is_topdown_metrics()`, `evsel__name()`, `parse_events()`, `perf_pmu__for_each_event()`, and `perf_pmus__scan_core()`. `test__x86_topdown()` gates on `topdown_sys_has_perf_metrics()` and registers through `DEFINE_SUITE("x86 topdown", x86_topdown)`.

Control flow: If the system lacks topdown perf metrics, the test returns success without work. Otherwise it scans each core PMU and invokes `event_cb()` for every PMU event. The callback parses the event, then classifies names containing specific non-topdown slot-like strings as not topdown, generic `slots` names as topdown slots only on the core raw PMU, `topdown` names as topdown metrics only on the core raw PMU, and all other names as neither. Any mismatch sets shared state to `TEST_FAIL`.

State and persistence: State is limited to the integer result pointer passed into callbacks and temporary `evlist` instances. Each parsed evlist is deleted before returning. No files or persistent settings are modified.

Dependencies and integration points: It depends on the x86 topdown helper API in `arch/x86/util/topdown.h`, PMU event scanning, parse-events infrastructure, and perf test macros. It validates the metadata used by x86 `arch_evlist__cmp()`, `arch_evlist__add_required_events()`, and topdown event grouping behavior.

Risks: The test is name-pattern based, so new event aliases containing `slots` or `topdown` may need classification updates. It assumes `PERF_TYPE_RAW` corresponds to the core PMU that supports topdown metrics. It also only runs meaningful checks on systems exposing topdown perf metrics, leaving non-supporting machines with a no-op pass.

Test signals: `perf test -v "x86 topdown"` should complete without "Broken topdown information" messages on systems with topdown metrics. Parse errors print via `parse_events_error__print()` and mark the test failed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/topdown.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/auxtrace.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/auxtrace.c

Purpose: This x86-specific AUX tracing entry point selects the appropriate Intel AUX trace recorder for `perf record`. It recognizes Intel PT and Intel BTS PMU selections and returns an initialized `struct auxtrace_record` for the active tracing mode.

Important APIs, types, and functions: `auxtrace_record__init()` is the exported arch hook. It obtains the minimum CPU from the evlist's CPU map, calls `get_cpuid()`, and dispatches only for CPUID strings beginning with `GenuineIntel,`. `auxtrace_record__init_intel()` finds `intel_pt` and `intel_bts` PMUs, scans evsels for matching PMU types, rejects simultaneous PT and BTS use, and calls `intel_pt_recording_init()` or `intel_bts_recording_init()`.

Control flow: Initialization starts with `*err = 0`. CPUID failure propagates through `*err` and returns NULL. Non-Intel CPUs return NULL with no error. Intel systems scan the evlist, set `found_pt` and `found_bts`, reject the invalid combination with `-EINVAL`, then return the chosen recorder or NULL if no supported AUX PMU was selected.

State and persistence: The function does not persist state. It returns an allocated recorder object from the Intel PT/BTS subsystem when tracing is active. Error state is reported through the caller-provided `int *err`.

Dependencies and integration points: It integrates with generic `util/auxtrace.h`, `builtin-record.c` via `auxtrace_record__init()`, PMU discovery through `perf_pmus__find()`, CPUID formatting from `header.c`, and Intel PT/BTS recorder implementations. It depends on evsel `core.attr.type` matching PMU type numbers.

Risks: Vendor detection is a string prefix check and therefore depends on x86 `get_cpuid()` formatting. Mixed Intel PT and BTS selection is explicitly unsupported. If evlist CPU maps are empty or CPUID on the minimum CPU fails, AUX trace initialization is skipped with an error. Non-Intel future AUX providers require new dispatch logic.

Test signals: Parsing and recording commands using `intel_pt//` or `intel_bts//` should initialize AUX tracing on Intel systems. Combining both should emit "intel_pt and intel_bts may not be used together" and fail with `EINVAL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/auxtrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/cpuid.h -->
# sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/cpuid.h

Purpose: This header provides a small x86 CPUID wrapper for perf's user-space arch code. It preserves the ABI-sensitive EBX/RBX register while exposing CPUID leaf/subleaf results through output pointers.

Important APIs, types, and functions: `cpuid(unsigned int op, unsigned int op2, unsigned int *a, unsigned int *b, unsigned int *c, unsigned int *d)` is a static inline helper. It declares output constraints for EAX, EDI-as-saved-EBX, ECX, and EDX, with inputs in EAX and ECX. `get_cpuid_0(char *vendor, unsigned int *lvl)` is declared for the implementation in `header.c`.

Control flow: On x86-64, inline assembly moves `%rbx` to `%rdi`, executes `cpuid`, then exchanges `%rdi` and `%rbx` so the CPUID EBX result is captured through the `=D` output while RBX is restored. On 32-bit, it pushes `%ebx`, executes `cpuid`, moves `%ebx` into `%edi`, then pops the saved `%ebx`.

State and persistence: The helper has no persistent state. Its state contract is register preservation, especially for PIC/GOT usage and dynamic alloca cases where RBX may be important to the compiler.

Dependencies and integration points: It is included by x86 perf utility and test code such as `header.c`, `intel-pt-test.c`, and TSC-related utilities. The wrapper supports `get_cpuid()`, PMU event matching, Intel PT capability checks, and CPU vendor/family/model extraction.

Risks: Inline assembly constraints are delicate. Breaking RBX preservation can corrupt position-independent code or compiler-generated stack addressing. The helper assumes x86 CPUID availability and is only suitable for x86 arch builds.

Test signals: CPUID-dependent tests and features should produce stable vendor, family, model, and feature data. Failures in PMU event matching, Intel PT hybrid checks, or crashes under PIC builds can indicate wrapper regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/cpuid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/event.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/event.c

Purpose: This x86-64 utility synthesizes extra kernel mmap events for perf sessions. It emits `PERF_RECORD_MMAP` records for special kernel maps so tools can resolve symbols beyond the primary kernel map.

Important APIs, types, and functions: The implementation is compiled only under `__x86_64__`. `struct perf_event__synthesize_extra_kmaps_cb_args` carries the perf tool, callback, machine, and reusable event buffer. `perf_event__synthesize_extra_kmaps_cb()` formats one synthetic mmap record for maps accepted by `__map__is_extra_kernel_map()`. `perf_event__synthesize_extra_kmaps()` allocates the event buffer, iterates kernel maps via `maps__for_each_map()`, and frees the buffer.

Control flow: The public function gets `machine__kernel_maps(machine)`, allocates enough space for an mmap event plus ID header, then iterates maps. The callback skips non-extra maps, computes record size from filename length and `machine->id_hdr_size`, zeroes the buffer, fills header type/size/misc, start/len/pgoff/pid, copies the kmap name, and sends the event to `perf_tool__process_synth_event()`.

State and persistence: State is transient. The function reuses one allocated union event buffer while iterating maps and emits synthesized events into the current perf processing pipeline. It does not alter the map structures.

Dependencies and integration points: It overrides the weak generic `perf_event__synthesize_extra_kmaps()` used by `util/synthetic-events.c`. It depends on `machine`, `maps`, `map`, `kmap`, `perf_tool`, and synthetic event processing APIs. The host-vs-guest distinction controls `PERF_RECORD_MISC_KERNEL` versus `PERF_RECORD_MISC_GUEST_KERNEL`.

Risks: Incorrect size calculation can corrupt synthetic event processing because the filename has variable aligned length plus optional ID header. The x86-64 guard means 32-bit builds use generic behavior. Misclassifying extra kernel maps would either omit useful symbol coverage or emit duplicate/confusing mmap records.

Test signals: Perf sessions on x86-64 with extra kernel maps should include synthetic mmap records with correct kernel/guest misc flags and filenames. Symbol-resolution tests or verbose synthetic-event traces can reveal missing extra maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/evlist.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/evlist.c

Purpose: This file provides x86-specific evlist ordering and required-event injection for perf event parsing, primarily to keep topdown metrics and slots events in a hardware-valid grouping order.

Important APIs, types, and functions: `arch_evlist__cmp()` is the architecture comparator used by parse-events sorting. It relies on `topdown_sys_has_perf_metrics()`, `arch_evsel__must_be_in_group()`, `arch_is_topdown_slots()`, `arch_is_topdown_metrics()`, `evsel->core.leader`, `evsel->retire_lat`, and `evsel->core.idx`. `arch_evlist__add_required_events()` scans an event list and calls `topdown_insert_slots_event()` when topdown metrics require an implicit slots event.

Control flow: The comparator first handles topdown systems. If either side must be grouped, it forces slots before metrics and, when events are not already in the same group, moves topdown metrics before unrelated events. It then ensures retire-latency events are not group leaders by sorting them later. Otherwise it preserves insertion order by `core.idx`. Required-event injection scans list entries, exits if a slots event already exists, remembers the first topdown metric, and inserts slots immediately after the scanned prefix if needed.

State and persistence: The comparator is stateless. `arch_evlist__add_required_events()` mutates the in-memory parse event list by inserting a required slots evsel. No persistent state is written.

Dependencies and integration points: The functions override weak generic arch hooks used by `util/parse-events.c`. They integrate with x86 `topdown.h`, the local `evsel.h` declaration for `evsel__sys_has_perf_metrics()`, and the topdown slots insertion helper. Their behavior is tested indirectly by parsing topdown events and by the x86 topdown test.

Risks: Event ordering is subtle because grouped and ungrouped user requests must preserve meaning while satisfying PMU constraints. Incorrect sorting can make slots fail as a non-leader or separate duplicate topdown metrics incorrectly. The logic assumes topdown metrics are only valid when `topdown_sys_has_perf_metrics()` is true.

Test signals: `perf stat` topdown examples with grouped and ungrouped `instructions`, `slots`, and `topdown-*` events should be regrouped into valid order. `perf test "x86 topdown"` and parse-events tests provide regression signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/evlist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/evsel.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/evsel.c

Purpose: This file implements x86-specific evsel behavior for sampling weight, topdown grouping support, hardware event naming, automatic counter reset masks, AMD IBS warnings/errors, and Intel topdown open-error diagnostics.

Important APIs, types, and functions: `arch_evsel__set_sample_weight()` requests `WEIGHT_STRUCT`. `evsel__sys_has_perf_metrics()` checks that system topdown metrics exist and the evsel PMU type is `PERF_TYPE_RAW`. `arch_evsel__must_be_in_group()` returns true for topdown slots or metrics on supporting PMUs. `arch_evsel__hw_name()` formats hardware event names with optional PMU prefix. `arch_evsel__apply_ratio_to_prev()` sets `config2` ACR masks across a ratio event and its previous event. `arch__post_evsel_config()` warns once for AMD IBS L3-miss-only sampling-period skew. `arch_evsel__open_strerror()` dispatches to AMD IBS or Intel topdown-specific error explanation.

Control flow: Topdown helpers first gate on `topdown_sys_has_perf_metrics()` and PMU lookup. Hardware naming extracts event and PMU bits from `attr.config`. Ratio application verifies PMU `acr_mask` format support, finds the previous evsel, ensures previous `config2` is unused, computes masks from group index, and writes both attrs. Post-config warning exits unless AMD, finds IBS PMUs, checks L3-miss bits, and prints once. Open-error formatting emits AMD privilege-filter guidance for precise IBS events, or Intel topdown messages for invalid slots leadership or duplicate metric events.

State and persistence: The file mutates in-memory `perf_event_attr` fields, evsel sample bits, and one static `warned_once` flag. It emits warnings/errors but writes no persistent files. Its behavior affects subsequent `perf_event_open()` calls through attr configuration and error text.

Dependencies and integration points: It integrates with generic evsel configuration (`util/evsel.c` weak arch hooks), PMU format helpers, x86 CPU detection (`env.h`), topdown helpers, evlist formatting, and stat configuration. AMD IBS constants define config bits for `ibs_fetch` and `ibs_op`. Intel diagnostics depend on evsel group relationships and topdown event identity helpers.

Risks: ACR mask computation is group-index-sensitive and can misconfigure reset-on-overflow behavior if event order changes. The topdown PMU check assumes raw PMU type identifies the core PMU. Error messages must not mask unrelated `EINVAL` causes. The AMD warning is intentionally once-per-process, so later affected evsels will not repeat the message.

Test signals: Topdown `perf stat` groups should open with slots as leader and no duplicate metric events. AMD IBS commands with unsupported privilege filters should show the tailored message. IBS L3-miss-only sampling should print the skew warning once. Hardware event names should include PMU names on hybrid platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/evsel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/evsel.h -->
# sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/evsel.h

Purpose: This local x86 perf utility header exposes the topdown capability predicate implemented in `evsel.c` to neighboring x86 util files.

Important APIs, types, and functions: The only declaration is `bool evsel__sys_has_perf_metrics(const struct evsel *evsel);`. The header relies on including code to have a visible declaration of `struct evsel` and `bool` from other headers.

Control flow: There is no runtime control flow in this header. It provides an include guard `_EVSEL_H` and a function prototype.

State and persistence: No state is stored or persisted.

Dependencies and integration points: `arch/x86/util/evlist.c` includes this header to call the predicate while sorting and inserting topdown events. The implementation lives in `arch/x86/util/evsel.c`.

Risks: The generic name `_EVSEL_H` is broad and could collide if include ordering changes, although it is local to the x86 util directory. Any signature change must be synchronized with the implementation and callers.

Test signals: Build success is the main signal. Topdown parse and grouping tests exercise the caller side of this declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/evsel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/header.c -->
# sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/header.c

Purpose: This file implements x86 CPUID string generation and matching for perf headers, PMU event table selection, metric expressions, and architecture-specific feature dispatch.

Important APIs, types, and functions: `get_cpuid_0()` reads CPUID leaf 0 and formats the vendor string. `__get_cpuid()` is the shared formatter for vendor, family, model, and stepping. `get_cpuid()` emits `vendor,family,model,step` for perf metadata. `get_cpuid_str()` allocates and returns `vendor-family-model-stepping`, with model and stepping in hex formatting. `is_full_cpuid()` checks whether a CPUID pattern contains three dashes. `strcmp_cpuid_str()` compiles the map CPUID as an extended regex and returns 0 only for an accepted full-string match.

Control flow: `__get_cpuid()` always reads vendor/largest basic leaf, conditionally reads leaf 1 for family/model/stepping, applies Intel/AMD extended-family and extended-model rules, then writes into a caller buffer using a sentinel `$` at the end of the format. If the sentinel fits, it is removed and success is returned; otherwise `ENOBUFS` is returned. `strcmp_cpuid_str()` rejects incomplete runtime IDs when a full map CPUID is required, rejects invalid regexes, executes the regex, adjusts match length to ignore stepping when the map pattern is not full but the runtime ID is full, and returns 0 only if the match covers the intended full length.

State and persistence: `get_cpuid_str()` allocates a 128-byte string that callers must free. Other functions write into caller-provided buffers. No persistent state is stored.

Dependencies and integration points: It depends on the inline CPUID wrapper in `cpuid.h`, perf debug logging, regex APIs, and weak generic header hooks in `util/header.c`. PMU event code, metric expressions, AUX tracing, and x86 PMU utilities use these functions to identify CPU-specific tables and capabilities.

Risks: The sentinel-fit check depends on `scnprintf()` writing the trailing `$`; if formatting changes, truncation detection can break. `strcmp_cpuid_str()` treats map strings as regexes, so unescaped metacharacters are meaningful. Full CPUID enforcement prevents ambiguous platform selection but can reject incomplete environment overrides. Family/model extraction must stay consistent with x86 CPUID rules.

Test signals: PMU event table lookup should select the expected x86 CPU map. Expression tests using `strcmp_cpuid_str()` should pass. `perf report --header` or debug output should show stable x86 CPUID strings, and invalid CPUID regexes should produce informative `pr_info()` messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/arch/x86/util/header.c -->
