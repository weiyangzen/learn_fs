# subset-b-000629 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/ev6-stxncpy.S -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/ev6-stxncpy.S

Purpose: EV6/21264-tuned bounded string copy core for `strncpy`, `stpncpy`, and `strncat`, copying at most `COUNT` bytes and returning internal state to callers. Important APIs/types/functions: exports internal `__stxncpy` and `stxncpy_aligned` entry points using Alpha register conventions (`a0/a1/a2`, `t9`, `t10`, `t12`). Control flow: computes destination/source alignment, chooses co-aligned or unaligned paths, copies quadwords with `ldq_u`/`stq_u`, detects NUL bytes with `cmpbge`, and merges partial final words with `zap` masks. State and persistence: no persistent state; writes destination memory and returns last-word/count masks. Dependencies/integration: included by Alpha string wrapper files and depends on `asm/regdef.h`. Risks: very sensitive to count-zero precondition, unaligned exception avoidance, and EV6 scheduling nops. Test signals: kernel string tests, Alpha boot, `strncpy`/`strncat` boundary cases, and fault-injection near page ends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/ev6-stxncpy.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/ev67-strcat.S -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/ev67-strcat.S

Purpose: EV67/21264 implementation of `strcat`, appending a NUL-terminated source string to the end of destination. Important APIs/types/functions: exports `strcat`; uses internal `__stxcpy` after locating the destination terminator. Control flow: saves original destination in `v0`, scans destination by aligned quadwords, uses `cmpbge` and `cttz` to find the first NUL, then branches into the copy helper with `t9`/`$23` as the internal return address. State and persistence: mutates only destination buffer and has no global state. Dependencies/integration: exported to kernel modules and depends on the Alpha string helper selection in `stycpy.S`. Risks: reads destination until NUL and walks source in the helper, so bad strings can fault; comments note the source is effectively read after a separate destination scan. Test signals: string selftests, module link checks for `EXPORT_SYMBOL(strcat)`, and Alpha EV67 boot workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/ev67-strcat.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/ev67-strchr.S -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/ev67-strchr.S

Purpose: EV67 implementation of `strchr`, returning the first matching character or NULL before the string terminator. Important APIs/types/functions: exports `strchr`; replicates the target byte across a quadword using Alpha byte-insert operations. Control flow: masks garbage bytes before the initial pointer, compares both NUL and target bytes with `cmpbge`, loops aligned quadword loads, then uses `cttz` and conditional move to return NULL when the first special byte is a terminator rather than a match. State and persistence: stateless; reads the string only. Dependencies/integration: uses `asm/regdef.h` and is exported for common kernel string users. Risks: precise first-quad masking and target-vs-NUL ordering are correctness-critical; over-reading into an unmapped page would be a fault risk. Test signals: `strchr` unit cases for misaligned starts, searching for `'\0'`, and no-match strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/ev67-strchr.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/ev67-strlen.S -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/ev67-strlen.S

Purpose: EV67 `strlen` optimized for Alpha quadword scanning. Important APIs/types/functions: exports `strlen`; relies on `cmpbge` to test eight bytes at once and `cttz` to locate the first zero byte. Control flow: unaligned-loads the first quadword, masks bytes before the original pointer, scans aligned quadwords until a zero byte appears, computes the NUL address, and subtracts the original pointer. State and persistence: read-only and stateless. Dependencies/integration: linked into the Alpha architecture string library and exported to modules. Risks: assumes a valid NUL-terminated string and depends on correct masking to ignore bytes before the input pointer. Test signals: kernel string tests covering aligned/misaligned addresses, empty strings, and page-boundary strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/ev67-strlen.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/ev67-strncat.S -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/ev67-strncat.S

Purpose: EV67 `strncat`, appending at most `COUNT` characters and always preserving kernel semantics that do not write past count. Important APIs/types/functions: exports `strncat`; calls internal `__stxncpy`, then adjusts the final stored word to ensure NUL termination. Control flow: handles zero count, scans destination to its NUL using quadword comparison and `cttz`, enters bounded copy, then writes or masks the trailing NUL based on helper-returned count and bit masks. State and persistence: mutates destination buffer only. Dependencies/integration: integrates with EV6/EV67 helper selection via `styncpy.S`. Risks: count semantics differ from some libc behavior; final mask handling is easy to regress. Test signals: append tests for count zero, short source, exact count, and misaligned destination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/ev67-strncat.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/ev67-strrchr.S -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/ev67-strrchr.S

Purpose: EV67 `strrchr`, returning the last occurrence of a byte in a NUL-terminated string. Important APIs/types/functions: exports `strrchr`; uses replicated search-byte masks plus `ctlz` to locate the highest matching byte in the last matching quadword. Control flow: masks pre-string garbage in the first quad, loops through aligned loads while saving the most recent match mask/address, stops at the terminator, masks matches after NUL, and computes the final pointer or NULL. State and persistence: no persistent state; tracks last match in registers. Dependencies/integration: uses `asm/regdef.h` and common exported string ABI. Risks: last-match tracking and terminator masking must handle search character `'\0'` correctly. Test signals: `strrchr` tests with repeated characters, no match, misalignment, and searching for NUL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/ev67-strrchr.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/fls.c -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/fls.c

Purpose: provides the Alpha lookup table used by bit-scan helpers to implement `fls(x)-1` efficiently per byte. Important APIs/types/functions: defines and exports `const unsigned char __flsm1_tab[256]`. Control flow: no runtime control flow beyond table lookup by users; entries encode the highest set-bit index within an 8-bit value, with zero mapped to zero. State and persistence: immutable read-only table exported to the kernel/module symbol table. Dependencies/integration: includes `linux/bitops.h` and `linux/module.h`; consumed by Alpha bit operations. Risks: any table entry error corrupts all callers using the optimized bit-scan path. Test signals: bitops selftests, compile/export checks, and edge cases for values 0, powers of two, and 0xff.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/fls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/fpreg.c -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/fpreg.c

Purpose: reads and writes Alpha floating-point registers for emulator, ptrace-like, and architecture support code. Important APIs/types/functions: exports `alpha_read_fp_reg`, `alpha_write_fp_reg`, `alpha_read_fp_reg_s`, and `alpha_write_fp_reg_s`; uses `STT/LDT/STS/LDS` macros that differ for EV6/EV67. Control flow: validates register number, disables preemption, chooses saved thread FP state when `TS_SAVED_FP` is set or accesses live FP registers through inline assembly, and marks `TS_RESTORE_FP` when modifying saved state. State and persistence: updates per-thread `thread_info()->fp[]` and status flags; otherwise reads/writes live CPU FP registers. Dependencies/integration: depends on `asm/fpu.h`, `asm/thread_info.h`, and preemption control. Risks: preemption discipline, register 31 behavior, and single-vs-double conversion must remain exact. Test signals: FP emulator tests, signal/ptrace FP state checks, and preempt-enabled stress on Alpha.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/fpreg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/memchr.S -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/memchr.S

Purpose: optimized Alpha `memchr`, finding a byte within a bounded memory range. Important APIs/types/functions: exports `memchr`; constructs a quadword repeated-byte pattern and uses `cmpbge` for parallel byte equality detection. Control flow: handles zero length, crops huge lengths to avoid address overflow, treats short searches in a combined first/last quad path, scans aligned quadwords with unrolled prefetching for longer ranges, and binary-searches the match mask to compute the pointer. State and persistence: stateless read-only routine. Dependencies/integration: exported generic memory primitive for kernel and modules. Risks: must not read outside the allowed minimum quadword envelope; length overflow and page-boundary behavior are critical. Test signals: KUnit/lib tests for zero length, all alignments, not found, last-byte match, and `(size_t)-1`-like bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/memchr.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/memcpy.c -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/memcpy.c

Purpose: C/inline-assembly Alpha `memcpy` optimized for aligned destination stores and unaligned source reconstruction. Important APIs/types/functions: exports `memcpy`; internal helpers include `__memcpy_aligned_up`, `__memcpy_unaligned_up`, and unused/downward variants. Control flow: chooses aligned vs unaligned path by low address bits, aligns the destination byte-by-byte, copies quadwords using `ldq` or `ldq_u` plus `extql/extqh`, then copies tail bytes. State and persistence: writes the destination range and has no persistent state. Dependencies/integration: includes `linux/string.h` and provides the architecture override for kernel memory copying. Risks: not overlap-safe, despite downward helper leftovers; alignment macros return early only after local copy state. Test signals: memcpy selftests over alignments, sizes around 0/1/7/8/9, and overlap tests proving callers must use `memmove`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/memcpy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/memmove.S -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/memmove.S

Purpose: Alpha EV5-style `memmove` supporting overlapping memory copies. Important APIs/types/functions: exports `memmove`; delegates to `memcpy` when ranges cannot overlap. Control flow: computes source/destination end addresses, branches to `memcpy` for safe forward copy, otherwise selects forward or backward loops based on address ordering and co-alignment, using byte loops to reach alignment and quadword loops for bulk aligned copies. State and persistence: mutates only the destination range. Dependencies/integration: depends on `memcpy` symbol and Alpha unaligned load/store instructions. Risks: overlapping boundary tests, co-alignment detection, and backward tail loops are common regression points; non-coaligned paths fall back to slower byte movement. Test signals: memmove tests where destination starts inside source, source inside destination, equal pointers, and all low-bit alignments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/memmove.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/memset.S -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/memset.S

Purpose: Alpha assembly implementation of `memset` and related constant-width variants. Important APIs/types/functions: exports `memset`, `__memset`, and `__memset16`; aliases `memset = ___memset`. Control flow: expands an 8-bit or 16-bit pattern to a quadword, handles within-one-quad and misaligned head cases with masks, writes aligned quadwords in bulk, and masks tail bytes to preserve neighboring memory. State and persistence: writes only the requested destination bytes. Dependencies/integration: architecture memory primitive exported to kernel modules. Risks: partial-head/tail masking must avoid modifying adjacent bytes; pattern replication differs for byte and 16-bit callers. Test signals: memset tests for all lengths around cache-line and quadword boundaries, misaligned addresses, and non-byte `__memset16` patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/memset.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/srm_printk.c -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/srm_printk.c

Purpose: formats text for SRM firmware console output. Important APIs/types/functions: defines `srm_printk(const char *fmt, ...)`, uses static `buf[1024]`, `vsprintf`, and `srm_puts`. Control flow: formats into the static buffer, counts line feeds, expands each `\n` into `\r\n` in-place from the end, writes through SRM callback, and returns the original formatted length. State and persistence: uses a static shared buffer, so output is non-reentrant and transient. Dependencies/integration: depends on `asm/console.h`; used by early Alpha console paths. Risks: `vsprintf` can overflow the fixed buffer, and concurrent callers can corrupt output. Test signals: early boot console smoke, newline conversion checks, and long-format fuzzing under debug builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/srm_printk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/srm_puts.c -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/srm_puts.c

Purpose: writes a byte string to the Alpha SRM console callback once callbacks are initialized. Important APIs/types/functions: defines `srm_puts(const char *str, long len)`, uses `callback_init_done` and `callback_puts`. Control flow: returns success-like `len` before callback initialization, otherwise loops until all bytes are reported written, masking the firmware return to 32 bits and advancing the pointer. State and persistence: no local persistent state; depends on global callback initialization and firmware-side console state. Dependencies/integration: called by `srm_printk` and early console code. Risks: no progress guard if firmware returns zero repeatedly; ignores callback errors after masking. Test signals: SRM boot console output and tests that partial callback writes advance correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/srm_puts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/stacktrace.c -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/stacktrace.c

Purpose: simple Alpha stack traceback helper that decodes function prologues to print saved registers and return PCs. Important APIs/types/functions: defines `stacktrace`, with helpers `seek_prologue`, `stack_increment`, and `display_stored_regs`; uses Alpha instruction masks for stack allocation and `stq` pushes. Control flow: starts from current stack pointer and the `stacktrace` prologue, prints saved registers until a basic-block terminator, derives the caller frame size, seeks the next prologue from the return PC, and continues while in kernel text. State and persistence: read-only stack/code inspection with printk output. Dependencies/integration: depends on Alpha calling conventions and `START_ADDR`. Risks: fragile against compiler prologue changes, corrupt stacks, and missing frame patterns; `display_stored_regs` advances only through recognized instructions. Test signals: oops stack output, synthetic call chains, and builds with different compiler optimization levels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/stacktrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/strcat.S -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/strcat.S

Purpose: baseline Alpha `strcat`, appending source to destination after scanning for the destination NUL. Important APIs/types/functions: exports `strcat`; calls internal `__stxcpy`. Control flow: scans destination with unaligned first quadword masking and aligned quadword loads, isolates the first zero-byte mask through arithmetic/binary search, adjusts the destination pointer, then branches into copy helper while preserving the original destination as return value. State and persistence: writes destination only. Dependencies/integration: selected for non-EV67 builds and exported to modules. Risks: duplicate scan/copy cost, NUL requirement, and final byte-offset search correctness. Test signals: generic string tests across alignments and appended empty/nonempty source.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/strcat.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/strchr.S -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/strchr.S

Purpose: baseline Alpha `strchr`, returning the first matching character before the string terminator. Important APIs/types/functions: exports `strchr`; uses byte replication, `cmpbge`, and binary mask search. Control flow: zero-extends and replicates target byte, masks pre-pointer bytes in the first quad, compares both target and NUL bytes per quadword, exits at the first relevant byte, returns NULL if that byte was only the terminator, otherwise computes the matching address. State and persistence: no writes or persistent state. Dependencies/integration: common exported string primitive. Risks: the target-vs-terminator decision is subtle, especially for `c == 0`. Test signals: empty strings, search for NUL, no match, first-byte match, and misaligned inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/strchr.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/strcpy.S -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/strcpy.S

Purpose: small public wrapper for Alpha `strcpy`. Important APIs/types/functions: exports `strcpy` and delegates all copy mechanics to `__stxcpy`. Control flow: sets the C return value to original destination, moves the real return address into the helper convention register, and branches to the internal copy routine. State and persistence: destination memory is modified by the helper; wrapper has no state. Dependencies/integration: depends on `__stxcpy` being linked from the selected helper file. Risks: wrapper correctness depends entirely on internal linkage conventions and helper preserving `v0`. Test signals: symbol export/link tests plus generic `strcpy` behavior for aligned and misaligned buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/strcpy.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/strlen.S -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/strlen.S

Purpose: baseline Alpha `strlen` using quadword scanning. Important APIs/types/functions: exports `strlen`; uses `cmpbge` for byte-zero detection and a small binary search to locate the zero byte. Control flow: handles a misaligned first load by masking earlier bytes, scans aligned quadwords until a zero byte appears, fast-paths zero in byte 0, otherwise computes byte offset from the match mask and subtracts the original address. State and persistence: stateless read-only routine. Dependencies/integration: common kernel string primitive. Risks: unsafe for unterminated strings; first-quad masking and offset arithmetic are correctness-critical. Test signals: all starting alignments, empty string, long string, and strings ending at page boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/strlen.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/strncat.S -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/strncat.S

Purpose: baseline Alpha `strncat`, appending a bounded number of source characters and ensuring termination under kernel semantics. Important APIs/types/functions: exports `strncat`; uses `__stxncpy` and returned masks/word counters. Control flow: returns immediately for zero count, scans destination for its NUL, calls the bounded copy helper, then either writes a final NUL in the current word or handles multiword count leftovers. State and persistence: mutates destination only. Dependencies/integration: selected for non-EV67 builds and depends on `stxncpy.S` or EV6 variant. Risks: final terminator placement and count interpretation are easy to break. Test signals: count-zero, exact-count, short-source, and destination alignment tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/strncat.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/strncpy.S -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/strncpy.S

Purpose: Alpha `strncpy` wrapper and tail-zeroing logic. Important APIs/types/functions: exports `strncpy`; calls internal `__stxncpy`. Control flow: handles zero length, delegates bounded copy, then uses helper masks and remaining full-word count to zero-fill bytes after the copied NUL up to count, including single-word and multiword paths. State and persistence: writes destination buffer and zero-padding bytes. Dependencies/integration: relies on `__stxncpy` register results (`t0`, `t10`, `t12`, `a2`) and Alpha mask operations. Risks: comments note modified ANSI behavior history, but current code zeroes remaining count; mask boundaries are sensitive. Test signals: source shorter than count, source exactly count, zero count, and misaligned destination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/strncpy.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/strrchr.S -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/strrchr.S

Purpose: baseline Alpha `strrchr`, finding the last occurrence of a character. Important APIs/types/functions: exports `strrchr`; stores last match address and byte mask in registers while scanning. Control flow: builds a repeated target byte, masks first-quad garbage, loops over aligned quadwords until a NUL byte appears, records the most recent quadword containing target matches, masks matches after the terminator, and binary-searches the highest retained match. State and persistence: no persistent state; only reads string memory. Dependencies/integration: common exported string function. Risks: last-match mask selection differs from first-match functions and must handle `c == '\0'`. Test signals: repeated matches, NUL search, no-match strings, and all starting alignments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/strrchr.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/stxcpy.S -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/stxcpy.S

Purpose: internal Alpha string-copy engine for unbounded NUL-terminated copies used by `strcpy`, `stpcpy`, and `strcat`. Important APIs/types/functions: defines `__stxcpy` and `stxcpy_aligned` with custom register return values such as final-byte mask in `t12`. Control flow: detects co-aligned source/destination fast path, otherwise builds aligned destination words from two unaligned source loads, avoids reading beyond the source page when misalignments cross, loops quadwords, and masks the final partial store. State and persistence: writes destination; exposes final address/mask to callers. Dependencies/integration: included by string wrapper selection files. Risks: page-fault avoidance in unaligned startup and destination word read avoidance are delicate. Test signals: `strcpy`/`strcat` tests crossing alignment and page boundaries, plus stpcpy-style return validation where used.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/stxcpy.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/stxncpy.S -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/stxncpy.S

Purpose: baseline internal bounded string-copy engine for `strncpy`, `stpncpy`, and `strncat`. Important APIs/types/functions: defines `__stxncpy` and `stxncpy_aligned`; returns last word, count-end bit, final byte bit, final word address, and remaining full-word count in registers. Control flow: biases count by destination misalignment, selects co-aligned or unaligned assembly, detects source NUL and count end via masks, writes full words in loops, and combines final source/destination bytes for partial stores. State and persistence: destination writes only; all additional state is returned in registers. Dependencies/integration: shared by public string wrappers and included conditionally by `styncpy.S`. Risks: count must be nonzero; off-by-one in count-end mask causes over/under-write. Test signals: bounded copy tests for every count modulo eight and misaligned source/destination pairs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/stxncpy.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/stycpy.S -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/stycpy.S

Purpose: composition file that selects the concrete unbounded Alpha string-copy and concatenation implementations for the build. Important APIs/types/functions: includes `strcpy.S`, either `ev67-strcat.S` or `strcat.S`, and either `ev6-stxcpy.S` or `stxcpy.S`. Control flow: entirely preprocessor-driven based on `CONFIG_ALPHA_EV67` and `CONFIG_ALPHA_EV6`; no runtime code of its own. State and persistence: none. Dependencies/integration: controls which object code supplies `strcpy`, `strcat`, and `__stxcpy`. Risks: include order and duplicate symbol selection must stay mutually exclusive across CPU configs. Test signals: Alpha defconfig matrix builds for EV6, EV67, and generic configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/stycpy.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/styncpy.S -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/styncpy.S

Purpose: composition file that selects bounded Alpha string-copy implementations. Important APIs/types/functions: includes `strncpy.S`, either `ev67-strncat.S` or `strncat.S`, and either `ev6-stxncpy.S` or `stxncpy.S`. Control flow: preprocessor-only CPU feature dispatch; no independent runtime logic. State and persistence: none beyond included symbols. Dependencies/integration: ensures `strncpy`, `strncat`, and `__stxncpy` implementations are built consistently for the selected Alpha CPU family. Risks: mismatched EV67 wrapper with wrong helper variant could violate internal register/scheduling assumptions. Test signals: build matrix plus string tests exercising `strncpy` and `strncat` under all Alpha config combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/styncpy.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/udelay.c -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/udelay.c

Purpose: Alpha busy-wait delay primitives using the processor cycle counter and calibrated loops-per-jiffy. Important APIs/types/functions: exports `__delay`, `udelay`, and `ndelay`; selects per-CPU `LPJ` on SMP. Control flow: `__delay` samples `rpcc`, computes a target, loops while signed cycle delta remains positive; `udelay`/`ndelay` scale requested time by `HZ`, time units, and `LPJ`, then call `__delay`. State and persistence: reads global/per-CPU calibration state; no persistent local state. Dependencies/integration: used by generic delay APIs and drivers. Risks: intended for very small delays; 32-bit active cycle counter and signed delta limit long waits. Test signals: delay calibration, boot-time timer sanity, and driver tests around microsecond/nanosecond waits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/udelay.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/udiv-qrnnd.S -->
# sources/distributed-fs/ceph-client/arch/alpha/lib/udiv-qrnnd.S

Purpose: Alpha implementation of GCC/GMP-style `__udiv_qrnnd`, dividing a two-word unsigned numerator by a one-word divisor and returning quotient plus remainder. Important APIs/types/functions: exports `__udiv_qrnnd(unsigned long *rem, unsigned long n1, unsigned long n0, unsigned long d)`. Control flow: branches between normal and large-divisor algorithms, performs unrolled shift/subtract quotient generation, stores remainder through `rem_ptr`, and fixes the odd large-divisor case with correction steps. State and persistence: writes only the caller-provided remainder pointer. Dependencies/integration: used by soft-fp utilities and compiler arithmetic support. Risks: divide-by-zero is not guarded here; carry/correction logic is hard to audit. Test signals: compiler runtime division tests, soft-fp conversion tests, and randomized 128/64-style division comparisons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/lib/udiv-qrnnd.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/math-emu/Makefile -->
# sources/distributed-fs/ceph-client/arch/alpha/math-emu/Makefile

Purpose: builds Alpha floating-point software emulation support. Important APIs/types/functions: sets `ccflags-y := -w`, adds `math-emu.o` under `CONFIG_MATHEMU`, and maps `math-emu-objs := math.o`. Control flow: kbuild-only conditional object inclusion. State and persistence: no runtime state. Dependencies/integration: ties `math.c` into the Alpha kernel or module build when math emulation is enabled. Risks: suppressing warnings can hide emulator issues; object naming must match module-init behavior in `math.c`. Test signals: `CONFIG_MATHEMU=y/m/n` builds and module load/unload when built as a module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/math-emu/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/math-emu/math.c -->
# sources/distributed-fs/ceph-client/arch/alpha/math-emu/math.c

Purpose: Alpha floating-point instruction emulator and imprecise-trap completer. Important APIs/types/functions: defines `alpha_fp_emul(pc)` and `alpha_fp_emul_imprecise(regs, write_mask)`, module hook save/restore, opcode/function constants, and soft-fp operations for single/double/quad conversions. Control flow: fetches the trapping instruction with `get_user`, decodes source/destination/function/mode, updates rounding from FPCR when dynamic, reads FP regs, executes soft-fp arithmetic/comparison/conversion, writes destination regs, updates software/hardware exception state, and returns SIGFPE codes or `-1` for bad opcodes. State and persistence: mutates current thread IEEE state, FPCR, and FP register state; module mode patches global emulator function pointers. Dependencies/integration: depends on `sfp-util.h`, Linux soft-fp headers, Alpha FP register helpers, and trap entry code. Risks: instruction decoding, exception mapping, and trap-shadow replay are architecture-critical. Test signals: FP exception suites, denormal/NaN comparisons, conversion overflow tests, and module hook lifecycle checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/math-emu/math.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/math-emu/sfp-util.h -->
# sources/distributed-fs/ceph-client/arch/alpha/math-emu/sfp-util.h

Purpose: Alpha support glue for the generic Linux soft-fp library. Important APIs/types/functions: defines `add_ssaaaa`, `sub_ddmmss`, `umul_ppmm`, `udiv_qrnnd`, declares `__udiv_qrnnd`, sets `UDIV_NEEDS_NORMALIZATION`, maps `abort()` to `bad_insn`, and forces little-endian soft-fp byte order. Control flow: macro-only arithmetic helpers used by included soft-fp code. State and persistence: no state; operations are inline register computations. Dependencies/integration: included by `math.c` before soft-fp headers and tied to `udiv-qrnnd.S`. Risks: endian assumptions and macro side effects must match Alpha ABI and soft-fp expectations. Test signals: emulator arithmetic tests, soft-fp compile coverage, and division helper edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/math-emu/sfp-util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/mm/Makefile -->
# sources/distributed-fs/ceph-client/arch/alpha/mm/Makefile

Purpose: kbuild file for Alpha memory-management objects. Important APIs/types/functions: sets `obj-y := init.o fault.o tlbflush.o`. Control flow: unconditional object inclusion for the architecture MM directory. State and persistence: no runtime state. Dependencies/integration: ensures page-table setup, page fault handling, and TLB migration flush helpers are linked into Alpha kernels. Risks: omitting one object breaks boot or fault handling; ordering is simple but all three are required. Test signals: Alpha architecture builds and link checks for MM symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/mm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/mm/fault.c -->
# sources/distributed-fs/ceph-client/arch/alpha/mm/fault.c

Purpose: Alpha page-fault and MM context reload handling. Important APIs/types/functions: defines `__load_new_mm_context`, `do_page_fault`, global `last_asn` on non-SMP, and fixup helper macro `dpf_reg`. Control flow: handles prefetch-load suppression into `$31`, rejects faults without a valid context, optionally mirrors vmalloc PGD entries, locks/fetches VMA, checks access permissions by fault cause, calls `handle_mm_fault`, handles retry/completed/error cases, searches exception tables for kernel fixups, or signals/kills as appropriate. State and persistence: updates `mm->context[cpu]`, PCB ASN/PTBR, process signal state, and page tables for vmalloc faults. Dependencies/integration: depends on generic MM, exception tables, perf page-fault events, Alpha PAL/thread reload. Risks: locking paths, fault retry unlock semantics, and user/kernel signal distinction are critical. Test signals: page-fault selftests, copy_to_user fixups, vmalloc fault paths, OOM faults, and instruction-fetch permission tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/mm/fault.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/mm/init.c -->
# sources/distributed-fs/ceph-client/arch/alpha/mm/init.c

Purpose: Alpha page-table, SRM console remap, and paging initialization. Important APIs/types/functions: defines `pgd_alloc`, `callback_init`, `arch_zone_limits_init`, `paging_init`, `srm_paging_stop`, and `protection_map`. Control flow: allocates PGDs with kernel/VPTB mappings, switches to the kernel system map, records original PCB, remaps SRM console callback pages into vmalloc space, registers early VM areas, initializes zone PFN limits and zero page, and can restore SRM console page tables on shutdown. State and persistence: mutates `swapper_pg_dir`, HWRPB VPTB/checksum, `init_thread_info.pcb`, `original_pcb`, `callback_init_done`, zone globals, and console CRB mappings. Dependencies/integration: depends on memblock/vmalloc, Alpha HWRPB/console/PAL code, and generic MM protection mapping. Risks: early memory allocation and SRM remapping are boot-critical; PAE/vmalloc layout assumptions are fragile. Test signals: Alpha boot on SRM and non-SRM platforms, reboot path, vmalloc mapping checks, and page-protection tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/mm/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/mm/tlbflush.c -->
# sources/distributed-fs/ceph-client/arch/alpha/mm/tlbflush.c

Purpose: Alpha helper for page migration/compaction that combines MM context handling with immediate per-page TLB invalidation. Important APIs/types/functions: defines `migrate_flush_tlb_page`; SMP path uses `struct tlb_mm_and_addr` and `ipi_flush_mm_and_page`. Control flow: selects data-only or instruction+data TBI by `VM_EXEC`, refreshes the current MM context or invalidates other contexts, issues `tbi`, and on SMP synchronously runs the combined handler on all CPUs with `on_each_cpu`, then clears remote context entries for single-user mms. State and persistence: mutates mm context/ASN state and per-CPU TLB contents. Dependencies/integration: used by migration/compaction paths that cannot rely on lazy shootdowns. Risks: preemption, ASN lock checks, and executable mapping barriers are correctness-critical. Test signals: page migration under executable mappings, SMP stress, compaction tests, and stale-TLB fault detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/mm/tlbflush.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/Kbuild -->
# sources/distributed-fs/ceph-client/arch/arc/Kbuild

Purpose: top-level ARC architecture kbuild traversal. Important APIs/types/functions: adds `kernel/`, `mm/`, and `net/` to `obj-y`; adds `boot` to `subdir-` for cleaning. Control flow: build-system directory inclusion only. State and persistence: no runtime state. Dependencies/integration: controls which ARC architecture subtrees participate in kernel build and clean. Risks: missing subtree entries produce unresolved symbols or incomplete architecture support. Test signals: ARC allmodconfig/defconfig builds and `make clean` behavior for boot artifacts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arc/Kconfig

Purpose: declares ARC architecture feature selection, platform menus, CPU/ISA choices, memory model, cache, DSP/FPU, debugging, and boot options. Important APIs/types/functions: config symbols include `ARC`, `ISA_ARCOMPACT`, `ISA_ARCV2`, `ARC_CPU_770`, `ARC_CPU_HS`, `SMP`, `ARC_CACHE`, `ARC_MMU_V3/V4`, `ARC_HAS_LLSC`, `ARC_HAS_LL64`, `ARC_DSP_*`, `HIGHMEM`, `ARC_HAS_PAE40`, `ARC_DW2_UNWIND`, and `BUILTIN_DTB_NAME`. Control flow: Kconfig dependencies/selects shape compiler flags, object inclusion, and header behavior. State and persistence: persists in `.config` and generated headers. Dependencies/integration: feeds ARC Makefile, entry code, atomics, MMU, FPU/DSP, and platform submenus. Risks: symbol combinations must match real hardware; wrong LLSC, page size, endian, or DSP settings can break boot or userspace ABI. Test signals: broad config matrix builds and boot tests across ARC700/HS, endian, SMP, highmem, and DSP variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/Makefile -->
# sources/distributed-fs/ceph-client/arch/arc/Makefile

Purpose: ARC architecture makefile that sets cross compiler, ISA/compiler flags, linker flags, libraries, platform directories, and boot image targets. Important APIs/types/functions: defines `KBUILD_DEFCONFIG`, `CROSS_COMPILE`, `cflags-y`, `tune-mcpu-def-*`, `LIBGCC`, `boot_targets`, and `uImage` target. Control flow: selects `-mcpu`, unaligned access, LL64, div/rem, current-in-gp, DWARF unwind, endian, module long calls, libgcc, and platform directories based on config. State and persistence: build artifacts and symlinked `arch/arc/boot/uImage`; no runtime state. Dependencies/integration: feeds kbuild, compiler, assembler, linker, platform subtrees, and boot image generation. Risks: compiler feature probes and fallback flags must match toolchain; module call range flags are ABI-sensitive. Test signals: ARC cross-builds with old/new toolchains and image target builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/boot/Makefile -->
# sources/distributed-fs/ceph-client/arch/arc/boot/Makefile

Purpose: builds ARC raw and U-Boot image formats from `vmlinux`. Important APIs/types/functions: defines `OBJCOPYFLAGS`, `LINUX_START_TEXT`, `UIMAGE_LOADADDR`, `UIMAGE_ENTRYADDR`, targets `vmlinux.bin`, compressed variants, and `uImage.*`. Control flow: objcopies `vmlinux` to binary, compresses with gzip/lzma, reads entry address with `readelf`, and invokes kbuild `uimage` command with compression type. State and persistence: creates boot artifacts under `arch/arc/boot`. Dependencies/integration: depends on host `mkimage` support and top-level `boot_targets`. Risks: entry/load address mismatch breaks boot; missing mkimage or readelf output changes fail image generation. Test signals: `make uImage`, compressed image builds, and bootloader load tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/boot/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/boot/dts/Makefile -->
# sources/distributed-fs/ceph-client/arch/arc/boot/dts/Makefile

Purpose: builds ARC device tree blobs for builtin DTB support and all-DTB testing. Important APIs/types/functions: sets `dtb-y` from `CONFIG_BUILTIN_DTB_NAME`, `dtb-` from all local `.dts` files, and `DTC_FLAGS_hsdk += --pad 20`. Control flow: kbuild DTB list generation only. State and persistence: generated `.dtb` files. Dependencies/integration: consumed by generic DTB build logic and ARC builtin DTB selection. Risks: wrong DTB name or missing padding can break platform boot. Test signals: `make dtbs`, `CONFIG_OF_ALL_DTBS`, and HSDK boot with padded DTB.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/boot/dts/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/Kbuild -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/Kbuild

Purpose: declares ARC generated and generic asm header fallbacks. Important APIs/types/functions: adds `syscall_table_32.h` to `syscall-y`; generic headers include `extable.h`, `kvm_para.h`, `mcs_spinlock.h`, `parport.h`, `user.h`, and `text-patching.h`. Control flow: kbuild header installation/generation only. State and persistence: generated include artifacts. Dependencies/integration: lets generic kernel code include standard asm interfaces not implemented specially by ARC. Risks: wrong generic fallback can hide missing architecture-specific behavior. Test signals: header install, syscall table generation, and full ARC builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/arcregs.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/arcregs.h

Purpose: central ARC auxiliary-register, status, exception, build-configuration, and hardware feature definitions. Important APIs/types/functions: defines register numbers (`ARC_REG_*`, `AUX_*`), status/ECR masks, DSP/AGU registers, many BCR bitfield structs, and helpers `is_isa_arcv2`/`is_isa_arcompact`. Control flow: header-only constants and compile-time helpers; bitfield layout changes with endian config. State and persistence: describes hardware register state but stores none itself. Dependencies/integration: included by entry, IRQ, cache, MMU, DSP, and platform probing code. Risks: register-number or bitfield mistakes corrupt hardware probing and exception decoding. Test signals: boot hardware-feature printouts, config checks, endian builds, and exception-path tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/arcregs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/asm-offsets.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/asm-offsets.h

Purpose: forwarding header that exposes generated structure offsets to ARC assembly. Important APIs/types/functions: includes `<generated/asm-offsets.h>`. Control flow: no logic beyond include indirection. State and persistence: generated offsets are build artifacts, not runtime state. Dependencies/integration: used by ARC entry/linkage assembly macros for `pt_regs`, `thread_info`, and task offsets. Risks: stale generated offsets cause stack/register save corruption. Test signals: clean rebuilds and entry-path boot tests after structure layout changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/asm-offsets.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/asserts.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/asserts.h

Purpose: configuration-vs-hardware validation helpers for ARC optional features. Important APIs/types/functions: declares `chk_opt_strict`, `chk_opt_weak`, and macros `CHK_OPT_STRICT`/`CHK_OPT_WEAK`. Control flow: macros pass the option name, probed hardware existence, and `IS_ENABLED()` value to runtime checking functions. State and persistence: no state here; called checks may warn or panic. Dependencies/integration: used by DSP and other feature probing code to validate `.config`. Risks: choosing strict vs weak incorrectly either panics unnecessarily or allows unsupported hardware use. Test signals: boot on hardware with/without optional DSP/AGU/FPU features and negative config tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/asserts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/atomic-llsc.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/atomic-llsc.h

Purpose: ARC 32-bit atomic operations using hardware load-locked/store-conditional. Important APIs/types/functions: defines `arch_atomic_set`, generated `arch_atomic_add/sub/and/or/xor/andnot`, return variants, and fetch variants. Control flow: each operation loops on `llock`, performs the arithmetic/logical update, tries `scond`, and retries while store-conditional fails. State and persistence: atomically mutates `atomic_t->counter`; no other state. Dependencies/integration: included by `atomic.h` when `CONFIG_ARC_HAS_LLSC` is enabled. Risks: memory ordering relies on generic wrappers for non-relaxed operations; address mode and early-clobber constraints are essential. Test signals: atomic selftests, SMP stress, and lock-free data structure tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/atomic-llsc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/atomic-spinlock.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/atomic-spinlock.h

Purpose: emulates ARC atomic read-modify-write operations using the architecture atomic-ops lock when LLSC is unavailable. Important APIs/types/functions: defines `arch_atomic_set`, arithmetic/logical operations, fetch operations, and return variants. Control flow: each operation acquires `atomic_ops_lock(flags)`, reads/modifies `v->counter`, then releases the lock; lock/unlock provide barriers. State and persistence: mutates atomic counters and uses lock/IRQ state managed by `asm/smp.h`. Dependencies/integration: selected by `atomic.h` for non-LLSC configurations. Risks: must interoperate with any hardware atomic users; missing locking in `atomic_set` could clobber emulated operations. Test signals: UP/non-LLSC atomic tests, IRQ-preempt stress, and spinlock recursion checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/atomic-spinlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/atomic.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/atomic.h

Purpose: ARC atomic API selection wrapper. Important APIs/types/functions: defines `arch_atomic_read`, includes `cmpxchg.h`, `barrier.h`, `smp.h`, then selects `atomic-llsc.h` or `atomic-spinlock.h`, and selects generic or ARCv2 64-bit atomics. Control flow: compile-time dispatch based on `CONFIG_ARC_HAS_LLSC` and `CONFIG_GENERIC_ATOMIC64`. State and persistence: no state itself. Dependencies/integration: public architecture implementation consumed by Linux atomic API. Risks: config selection must match hardware and ABI alignment requirements for `atomic64_t`. Test signals: full atomic API selftests across LLSC, non-LLSC, generic atomic64, and ARCv2 LL64 configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/atomic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/atomic64-arcv2.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/atomic64-arcv2.h

Purpose: ARCv2 native 64-bit atomic operations using `LLOCKD/SCONDD` and 64-bit load/store instructions. Important APIs/types/functions: defines aligned `atomic64_t`, `arch_atomic64_read/set`, generated add/sub/and/or/xor/andnot operations, cmpxchg64, xchg, and add-unless. Control flow: update paths loop on doubleword LL/SC, with carry-aware `add.f/adc` and `sub.f/sbc` for 64-bit arithmetic; stronger operations add `smp_mb()` around relaxed primitives where needed. State and persistence: atomically mutates 8-byte aligned counters. Dependencies/integration: selected when generic atomic64 is disabled and ARC has LL64+LLSC. Risks: alignment is mandatory; low/high register constraints and memory barriers are fragile. Test signals: `atomic64` selftests, slab alignment checks, SMP counter stress, and cmpxchg64 validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/atomic64-arcv2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/barrier.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/barrier.h

Purpose: ARC memory-barrier definitions, especially for ARCv2 weakly ordered microarchitectural buffering. Important APIs/types/functions: supplies architecture barrier primitives before including `asm-generic/barrier.h`. Control flow: compile-time conditional definitions for ISA variants; generic wrappers fill standard Linux barrier API. State and persistence: orders memory and device operations but stores no data. Dependencies/integration: used by atomics, IO accessors, futexes, and synchronization code. Risks: under-barriering causes DMA/MMIO and SMP ordering bugs; over-barriering hurts performance. Test signals: memory-model litmus tests, driver DMA tests, futex/atomic stress, and ARCv2 SMP boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/barrier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/bitops.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/bitops.h

Purpose: ARC bit-scan helpers and generic bitops integration. Important APIs/types/functions: defines `clz`, `constant_fls`, `fls`, `__fls`, `ffs`, `__ffs`, `ffz`, and includes generic hweight/fls64/sched/lock/atomic/non-atomic/le/ext2 helpers. Control flow: ARCompact uses `norm.f` and constant folding; ARCv2 uses `fls.f`, `ffs.f`, and `__builtin_arc_fls`. State and persistence: no persistent state. Dependencies/integration: included only through `linux/bitops.h` and used broadly by kernel code. Risks: zero input semantics differ across instructions and APIs; direct inclusion is forbidden. Test signals: bitops selftests for zero, all-one, powers of two, constant expressions, and both ISA configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/bitops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/bug.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/bug.h

Purpose: ARC architecture hook for BUG/WARN behavior. Important APIs/types/functions: includes or defines architecture BUG support around generic mechanisms in the small header. Control flow: compile-time macro definitions only. State and persistence: none beyond trap/debug side effects when macros are used elsewhere. Dependencies/integration: consumed by `linux/bug.h` and exception handling. Risks: wrong trap encoding or missing metadata prevents oops decoding. Test signals: build coverage and intentional WARN/BUG smoke tests on ARC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/bug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/cache.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/cache.h

Purpose: ARC cache geometry, uncached access helpers, alignment policy, and cache auxiliary register definitions. Important APIs/types/functions: defines `L1_CACHE_SHIFT/BYTES`, `SMP_CACHE_BYTES`, `ARCH_DMA_MINALIGN`, optional `ARCH_SLAB_MINALIGN`, `arc_read_uncached_32`, `arc_write_uncached_32`, cache control register constants, and IO coherency registers. Control flow: inline assembly helpers perform `ld.di/st.di`; preprocessor adapts to cache-line config and LL64/LLSC. State and persistence: describes and accesses hardware cache/MMIO state; globals `ioc_enable`, `perip_base`, and `perip_end` are extern. Dependencies/integration: used by DMA, cacheflush, memory allocation, and platform setup. Risks: wrong alignment breaks DMA or atomic64; wrong register constants break cache maintenance. Test signals: DMA coherency tests, cache-line build variants, and atomic64 alignment selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/cacheflush.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/cacheflush.h

Purpose: ARC cache-maintenance API declarations and page-copy hooks. Important APIs/types/functions: declares `flush_cache_all`, `flush_icache_range`, `__sync_icache_dcache`, `flush_dcache_page/folio`, DMA cache maintenance, and defines `PG_dc_clean`, `copy_to_user_page`, and no-op VMA cache flush hooks. Control flow: macro hooks copy bytes and sync I-cache for executable mappings; most range/MM hooks are no-ops on non-aliasing VIPT D-cache. State and persistence: manipulates cache state and page flag `PG_arch_1`. Dependencies/integration: used by MM, DMA, executable page modification, and page cache. Risks: stale I-cache after writing executable user pages and driver PIO dirtiness are key concerns. Test signals: breakpoints/gdbserver, module/text patching, DMA tests, and executable mmap modification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/cacheflush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/cachetype.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/cachetype.h

Purpose: exposes ARC cache aliasing properties to generic MM code. Important APIs/types/functions: defines `cpu_dcache_is_aliasing()` as false and `cpu_icache_is_aliasing()` as true. Control flow: constant inline-like macros only. State and persistence: none. Dependencies/integration: consumed by generic cache/TLB and MM decisions. Risks: incorrect aliasing claims cause either stale instruction fetches or unnecessary flushes. Test signals: executable page coherency tests and cacheflush path coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/cachetype.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/checksum.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/checksum.h

Purpose: ARC-optimized IP checksum helpers. Important APIs/types/functions: defines `csum_fold`, `ip_fast_csum`, and `csum_tcpudp_nofold`, then includes generic checksum fallback. Control flow: `ip_fast_csum` uses ARC inline assembly with load-address-update, loop counter, and carry-add instructions; TCP/UDP pseudo-header checksum uses chained `adc.f` and endian-dependent length placement. State and persistence: stateless arithmetic. Dependencies/integration: used by networking stack for IPv4/TCP/UDP checksums. Risks: carry folding, endian handling, and inline-asm clobbers are correctness-critical. Test signals: network checksum selftests, packet send/receive validation, big-endian builds, and odd header length tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/checksum.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/cmpxchg.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/cmpxchg.h

Purpose: ARC compare-exchange and exchange primitives. Important APIs/types/functions: defines `arch_cmpxchg_relaxed` for LLSC, lock-based `arch_cmpxchg` fallback, `arch_xchg_relaxed`/`arch_xchg`, and uses `cmpxchg_emu_u8` for byte cmpxchg. Control flow: LLSC cmpxchg loops on `llock`/`scond`; non-LLSC protects updates with `atomic_ops_lock`; exchange uses `ex` and may be lock-protected for non-LLSC interoperability. State and persistence: atomically mutates pointed memory. Dependencies/integration: used by atomics, locks, futexes, and lockless lists. Risks: one macro references `_val_` from the wrapper scope and is constraint-sensitive; missing barriers in non-relaxed users would be severe. Test signals: cmpxchg/xchg selftests, byte cmpxchg emulation, and lockless list stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/cmpxchg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/current.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/current.h

Purpose: provides fast access to the current task pointer on ARC. Important APIs/types/functions: defines current-task access around `CONFIG_ARC_CURR_IN_REG`, where `gp` may be reserved as the current-task register, with fallback through `_current_task`. Control flow: header/macros only; behavior depends on compiler include and fixed-register flags set by the ARC Makefile. State and persistence: reads per-CPU or global current task state; `gp` is maintained by entry/context-switch macros. Dependencies/integration: force-included by the Makefile when enabled and used throughout scheduler/task code. Risks: any code compiled without fixed `gp` discipline can corrupt current-task access. Test signals: context-switch stress, SMP current consistency, and builds with/without `ARC_CURR_IN_REG`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/current.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/delay.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/delay.h

Purpose: ARC busy-wait delay implementation using the loop counter register and calibrated `loops_per_jiffy`. Important APIs/types/functions: defines inline `__delay`, inline `__udelay`, `udelay(n)` constant-range wrapper, extern `loops_per_jiffy`, and extern `__bad_udelay`. Control flow: `__delay` loads `lp_count` and executes an ARC zero-overhead loop containing `nop`; `__udelay` computes loops with 64-bit multiply by `usecs * 4295 * HZ * loops_per_jiffy >> 32`; `udelay` rejects constant delays above 20000 usec via `__bad_udelay`. State and persistence: reads calibrated global delay state but stores none. Dependencies/integration: included by `linux/delay.h` and driver delay users. Risks: calibration, loop-counter clobbering, and large constant rejection affect hardware timing. Test signals: boot calibration, delay selftests, and peripheral initialization timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/delay.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/disasm.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/disasm.h

Purpose: ARC instruction decoding helpers for exception, kprobe, and unaligned-access handling. Important APIs/types/functions: defines instruction-size/opcode extraction helpers and decode constants used to classify ARC compact/regular instructions. Control flow: header-only bit decoding over instruction words. State and persistence: stateless. Dependencies/integration: used by low-level fault/debug code that must inspect trapped instructions. Risks: decoder drift from ISA encodings causes wrong fault emulation or probe handling. Test signals: kprobe tests, unaligned access emulation, and instruction error paths across 16-bit and 32-bit instruction forms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/disasm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/dma.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/dma.h

Purpose: ARC legacy DMA address boundary definition. Important APIs/types/functions: defines `MAX_DMA_ADDRESS` as `0xC0000000`. Control flow: constant macro only. State and persistence: none. Dependencies/integration: used by memory-zone and DMA allocation code to distinguish directly DMA-addressable memory. Risks: platform memory maps that differ from this constant may misclassify DMA memory. Test signals: DMA allocation tests and platform boot with devices constrained below the boundary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/dsp-impl.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/dsp-impl.h

Purpose: ARC DSP/AGU save-restore and configuration validation implementation. Important APIs/types/functions: assembly macros `DSP_EARLY_INIT`, `DSP_SAVE_REGFILE_IRQ`, `DSP_RESTORE_REGFILE_IRQ`; C helpers `dsp_save_restore`, `dsp_exist`, `agu_exist`, and `dsp_config_check`. Control flow: early init disables DSP_CTRL if present; IRQ macros either reset userspace DSP state or save/restore `PT_DSP_CTRL`; context-switch helper swaps AUX registers with task-thread storage using `aex`; config check compares hardware BCRs with Kconfig. State and persistence: mutates DSP AUX registers and per-task `thread.dsp` state. Dependencies/integration: included by entry macros and switch code. Risks: field names must match AUX macro construction; missing save/restore leaks userspace DSP state. Test signals: DSP userspace context-switch tests, IRQ entry tests, and hardware/config mismatch boot checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/dsp-impl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/dsp.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/dsp.h

Purpose: defines saved ARC DSP/AGU register layout for task context. Important APIs/types/functions: `struct dsp_callee_regs` with `ACC0_GLO`, `ACC0_GHI`, `DSP_BFLY0`, `DSP_FFT_CTRL`, and optional AGU fields. Control flow: structure declaration only. State and persistence: per-task thread state persists DSP/AGU callee registers across context switches when enabled. Dependencies/integration: field names are consumed by `DSP_AUX_SAVE_RESTORE` macro generation in `dsp-impl.h`. Risks: renaming or reordering fields without offset updates corrupts save/restore. Test signals: DSP register preservation across schedule, fork/exec, and signal delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/dsp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/dwarf.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/dwarf.h

Purpose: abstracts DWARF CFI directives for ARC assembly. Important APIs/types/functions: defines `CFI_STARTPROC`, `CFI_ENDPROC`, `CFI_DEF_CFA`, `CFI_OFFSET`, and related macros either as real directives or ignored comments based on `ARC_DW2_UNWIND_AS_CFI`. Control flow: preprocessor-only assembly macro selection. State and persistence: affects emitted unwind metadata in object files. Dependencies/integration: used by ARC assembly linkage/entry code and controlled by Makefile assembler feature probing. Risks: absent or wrong CFI metadata weakens stack unwinding and debugging. Test signals: stacktrace/unwind tests and builds with assemblers that do and do not support CFI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/dwarf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/elf.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/elf.h

Purpose: ARC ELF ABI definitions for executable loading, modules, and core dumps. Important APIs/types/functions: defines `EM_ARC_INUSE`, relocation numbers `R_ARC_*`, `ELF_ARCH`, `ELF_CLASS`, `ELF_DATA`, `elf_check_arch`, `CORE_DUMP_USE_REGSET`, `ELF_ET_DYN_BASE`, `ELF_PLAT_INIT`, `ELF_HWCAP`, and `ELF_PLATFORM`. Control flow: compile-time ABI constants plus external architecture check. State and persistence: influences process image setup and core file metadata. Dependencies/integration: used by binfmt_elf, module relocation, and userspace ABI. Risks: wrong ISA/endian architecture checks can execute incompatible binaries. Test signals: ELF exec tests, module relocation tests, coredump inspection, and endian/ISA matrix builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/elf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/entry-arcv2.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/entry-arcv2.h

Purpose: ARCv2 interrupt/exception entry and exit assembly macros. Important APIs/types/functions: defines `INTERRUPT_PROLOGUE`, `INTERRUPT_EPILOGUE`, `EXCEPTION_EPILOGUE`, `FAKE_RET_FROM_EXCPN`, register save/restore macros, CPU/current-thread helpers, and ABI callee-save macros. Control flow: entry macros account for hardware auto-save, optional no-autosave, user-vs-kernel SP handling, DSP save/restore, ACCL/ACCH registers, loop registers, and return state restoration. State and persistence: saves/restores `pt_regs`, AUX return registers, user SP, current task in `gp`, DSP state, and interrupt status. Dependencies/integration: included by `entry.h` for ARCv2 trap/IRQ assembly. Risks: stack layout offsets, auto-save assumptions, and status flag interpretation are fatal if wrong. Test signals: syscall/interrupt/exception boot tests, nested IRQs, signal return, and unwinder validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/entry-arcv2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/entry-compact.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/entry-compact.h

Purpose: ARCompact interrupt/exception entry and exit assembly macros. Important APIs/types/functions: defines stack switching, `EXCEPTION_PROLOGUE`, `EXCEPTION_PROLOGUE_KEEP_AE`, `EXCEPTION_EPILOGUE`, `INTERRUPT_PROLOGUE`, `INTERRUPT_EPILOGUE`, save/restore macros, and CPU/current helpers. Control flow: frees a scratch register, inspects status to decide user/kernel stack switching, handles L1/L2 interrupt corner cases, saves GPRs/AUX return state/loop registers, fakes return from exception to re-enable exceptions, and restores state in reverse. State and persistence: saves `pt_regs`, current task register, stack pointer, ECR, eret/erstatus, interrupt link/status registers, and zero-overhead loop state. Dependencies/integration: selected by `entry.h` for `CONFIG_ISA_ARCOMPACT`. Risks: nested interrupt stack switching and prologue scratch storage are fragile. Test signals: ARCompact boot, nested IRQ tests, syscall/signal tests, and unaligned-access exception paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/entry-compact.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/entry.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/entry.h

Purpose: common ARC entry header selecting ISA-specific low-level macros and declaring C exception handlers. Important APIs/types/functions: includes `entry-compact.h` or `entry-arcv2.h`, defines generic callee-save macros, current-task stack/current helpers, and declares handlers such as `do_signal`, `do_page_fault`, `do_misaligned_access`, and `do_machine_check_fault`. Control flow: assembler side abstracts common save/restore and current-task access; C side exposes handler prototypes. State and persistence: stack/current state is manipulated by included macros. Dependencies/integration: bridge between assembly entry code and C trap/fault implementation. Risks: mismatch between prototypes, pt_regs layout, and assembly call conventions breaks exception handling. Test signals: boot, syscall, signal, trap, kprobe, and page-fault paths on both ISA families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/entry.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/exec.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/exec.h

Purpose: ARC process-exec stack alignment policy. Important APIs/types/functions: defines `arch_align_stack(p)` to align down to a 16-byte boundary. Control flow: single macro applied during exec stack setup. State and persistence: affects initial userspace stack pointer. Dependencies/integration: used by generic exec/binfmt code. Risks: ABI breakage if alignment changes unexpectedly. Test signals: userspace ABI tests, dynamic loader startup, and stack alignment checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/exec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/fpu.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/fpu.h

Purpose: ARC FPU state type and save/restore hooks. Important APIs/types/functions: when `CONFIG_ARC_FPU_SAVE_RESTORE` is enabled, defines `struct arc_fpu` differently for ARCompact DPFP aux pairs and ARCv2 `ctrl/status`, and declares `fpu_init_task` plus `fpu_save_restore`; otherwise defines them as no-ops. Control flow: compile-time configuration only in this header. State and persistence: per-task FPU state persists across context switches when enabled. Dependencies/integration: scheduler/context switch and signal/task initialization code. Risks: wrong struct for ISA leaks or corrupts FPU exception/rounding state. Test signals: floating-point context-switch tests, signal tests, and configs with/without FPU save-restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/fpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/futex.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/futex.h

Purpose: ARC futex atomic operations on user memory. Important APIs/types/functions: defines `arch_futex_atomic_op_inuser` and `futex_atomic_cmpxchg_inatomic`, with `__futex_atomic_op` inline-assembly macro for LLSC and non-LLSC paths. Control flow: validates user access, optionally disables preemption for non-LLSC atomicity, surrounds operations with memory barriers, performs set/add/or/andn/xor or cmpxchg, and uses exception-table fixups to return `-EFAULT`. State and persistence: atomically mutates user-space futex words and returns old values. Dependencies/integration: used by generic futex syscall code. Risks: user access fixups, preemption discipline, and memory ordering are critical. Test signals: futex selftests, robust futex tests, page-fault fault injection, and SMP contention tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/futex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/highmem.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/highmem.h

Purpose: ARC highmem fixmap and pkmap layout definitions. Important APIs/types/functions: defines `FIXMAP_SIZE`, `PKMAP_SIZE`, `FIXMAP_BASE`, `FIX_KMAP_*`, `FIXADDR_TOP`, `__fix_to_virt`, `__virt_to_fix`, `PKMAP_BASE`, `LAST_PKMAP`, `PKMAP_ADDR`, `PKMAP_NR`, `kmap_init`, `arch_kmap_local_post_unmap`, and `flush_cache_kmaps`. Control flow: active only under `CONFIG_HIGHMEM`; local unmap flushes a kernel TLB range. State and persistence: describes persistent virtual mapping regions and flushes cache/TLB state. Dependencies/integration: used by highmem/kmap generic code and cacheflush. Risks: layout arithmetic must not overlap vmalloc, pkmap, or fixmap; TLB flush after local unmap is required. Test signals: highmem boot, kmap_local stress, PAE40 builds, and highmem page copy tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/highmem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/hugepage.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/hugepage.h

Purpose: ARC transparent hugepage PMD helpers. Important APIs/types/functions: defines `HPAGE_SHIFT/SIZE/MASK`, converters `pmd_pte`/`pte_pmd`, PMD permission/state helpers, `pmd_trans_huge`, `pfn_pmd`, `pmd_modify`, `set_pmd_at`, `update_mmu_cache_pmd`, `flush_pmd_tlb_range`, and `pmdp_establish`. Control flow: wraps PTE helpers to operate on PMD values and preserves `_PAGE_HW_SZ` for huge mappings. State and persistence: mutates PMD entries and MMU/TLB state via external hooks. Dependencies/integration: used by generic THP and hugetlb-related MM code on `ARC_MMU_V4`. Risks: losing the hardware-size bit or wrong PFN/protection encoding breaks huge mappings. Test signals: THP fault/collapse/split tests and hugepage TLB flush validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/hugepage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/io.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/io.h

Purpose: ARC MMIO and port-I/O accessors with endian conversion and ordering. Important APIs/types/functions: declares `ioremap`, defines `ioport_map/unmap`, big-endian accessors, raw read/write helpers for 8/16/32-bit and string IO, ordered `read*`/`write*`, relaxed accessors, and includes `asm-generic/io.h`. Control flow: raw helpers use inline assembly load/store forms; string helpers handle possibly unaligned buffers with `get_unaligned`; ordered helpers apply `__iormb`/`__iowmb` on ARCv2. State and persistence: reads/writes device memory and maps IO ranges. Dependencies/integration: used by all ARC drivers and DMA/MMIO code. Risks: barrier placement and fixed little-endian MMIO semantics are critical for devices; unaligned buffer handling differs by CPU. Test signals: driver MMIO tests, endian builds, DMA doorbell ordering, and ioremap smoke.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/irq.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/irq.h

Purpose: ARC IRQ namespace and architecture IRQ entry declarations. Important APIs/types/functions: defines `NR_IRQS` as 512, ARCv2 platform interrupt numbers `IPI_IRQ`, `SOFTIRQ_IRQ`, `FIRST_EXT_IRQ`, and declares `arc_init_IRQ` plus `arch_do_IRQ`. Control flow: constants and prototypes only. State and persistence: IRQ descriptor state is managed elsewhere. Dependencies/integration: included by interrupt controllers and generic IRQ code. Risks: insufficient `NR_IRQS` or wrong reserved IRQ numbers break SMP/IPI and device interrupt routing. Test signals: interrupt controller init, SMP IPI tests, softirq trigger tests, and platform device IRQ enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/irqflags-arcv2.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/irqflags-arcv2.h

Purpose: ARCv2 interrupt enable/disable and status flag helpers. Important APIs/types/functions: defines status/CLRI bits, AUX IRQ registers, default priority, `ISA_INIT_STATUS_BITS`, and inline functions `arch_local_irq_save`, `arch_local_irq_restore`, `arch_local_irq_enable`, `arch_local_irq_disable`, `arch_local_save_flags`, `arch_irqs_disabled_flags`, and `arch_irqs_disabled`. Control flow: uses `clri`/`seti`, clears active IRQ bits before enabling, and encodes flags in CLRI/SETI-compatible format. State and persistence: mutates STATUS32 and IRQ AUX state. Dependencies/integration: used by generic irqflags, lockdep, atomics fallback, and entry code. Risks: flag encoding must match tracing/restore expectations; unaligned-access AD bit is part of initial status. Test signals: lockdep IRQ tracing, nested interrupt tests, and irq enable/disable selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/irqflags-arcv2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/irqflags-compact.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/irqflags-compact.h

Purpose: ARCompact interrupt flag helpers for level-1/level-2 interrupt enable state. Important APIs/types/functions: defines status bits/masks (`STATUS_E1/E2/A1/A2/AE`), AUX IRQ registers, `ISA_INIT_STATUS_BITS`, and local IRQ save/restore/enable/disable/query routines. Control flow: inline assembly reads/modifies `status32` and uses compiler memory clobbers so IRQ-protected read-modify-write sequences are not reordered. State and persistence: mutates interrupt enable bits in status registers. Dependencies/integration: selected by `irqflags.h` for ARCompact and used by locks, atomics, and entry code. Risks: nested L1/L2 semantics are subtle; incorrect flags break critical sections and tracing. Test signals: interrupt nesting, lockdep, non-LLSC atomic emulation, and ARCompact boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/irqflags-compact.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/irqflags.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/irqflags.h

Purpose: selects the correct ARC irqflags implementation for the configured ISA. Important APIs/types/functions: includes `irqflags-compact.h` for `CONFIG_ISA_ARCOMPACT` or `irqflags-arcv2.h` otherwise. Control flow: preprocessor-only dispatch. State and persistence: none directly; included file mutates IRQ state. Dependencies/integration: public `asm/irqflags.h` consumed by generic interrupt and locking code. Risks: wrong ISA selection would emit unsupported instructions or wrong status-bit logic. Test signals: compile matrix for ARCompact/ARCv2 and basic IRQ enable/disable tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/irqflags.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/jump_label.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/jump_label.h

Purpose: ARC static key/jump label instruction layout. Important APIs/types/functions: defines `JUMP_LABEL_NOP_SIZE`, `arch_static_branch`, `arch_static_branch_jump`, `jump_label_t`, and `struct jump_entry`. Control flow: emits aligned `nop` or branch plus `__jump_table` entries using `asm goto`; runtime patching code later rewrites the aligned instruction. State and persistence: creates persistent jump-table metadata and patchable text. Dependencies/integration: used by Linux static keys and tracing/feature toggles. Risks: patch instruction must not cross cache/fetch boundaries; alignment choice affects both safety and padding overhead. Test signals: static key selftests, runtime patching under SMP, and ARCv2 non-BE32 config builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/jump_label.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/kdebug.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/kdebug.h

Purpose: ARC die-notifier reason codes. Important APIs/types/functions: defines `enum die_val` values `DIE_UNUSED`, `DIE_TRAP`, `DIE_IERR`, and `DIE_OOPS`. Control flow: type definition only. State and persistence: no state; values annotate exception reporting. Dependencies/integration: used by die/oops/debug notifier paths. Risks: mismatched reason codes reduce diagnostic accuracy. Test signals: trap/oops notifier tests and intentional fault diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/kdebug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/kgdb.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/kgdb.h

Purpose: ARC KGDB register numbering and breakpoint support. Important APIs/types/functions: when `CONFIG_KGDB`, defines `GDB_MAX_REGS`, `BREAK_INSTR_SIZE`, `CACHE_FLUSH_IS_SAFE`, `NUMREGBYTES`, `BUFMAX`, `arch_kgdb_breakpoint`, `kgdb_trap`, and `enum arc_linux_regnums`; otherwise makes `kgdb_trap` a no-op. Control flow: breakpoint emits `trap_s 0x4`; KGDB trap handling is external. State and persistence: exposes register layout for debugger packets. Dependencies/integration: used by KGDB core and ARC trap code. Risks: register numbering must match GDB ARC expectations; breakpoint size affects patching. Test signals: KGDB connect/break/continue, register read/write, and trap handling tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/kgdb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/kprobes.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/kprobes.h

Purpose: ARC kprobes architecture definitions. Important APIs/types/functions: defines `kprobe_opcode_t`, `UNIMP_S_INSTRUCTION`, `TRAP_S_2_INSTRUCTION`, `MAX_INSN_SIZE`, `MAX_STACK_SIZE`, `struct arch_specific_insn`, `struct prev_kprobe`, `struct kprobe_ctlblk`, and prototypes for kprobe fault/trap/trampoline functions. Control flow: header describes how prepared instruction slots and trap handling are represented; generic fallback applies when disabled. State and persistence: per-probe instruction copies and per-CPU control blocks persist while probes are armed. Dependencies/integration: used by kprobes core and ARC trap decoder. Risks: instruction-size handling and trap opcode selection must match ARC ISA encodings. Test signals: kprobe/kretprobe selftests, probes on short and long instructions, and fault-in-probe tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/kprobes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/linkage.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/linkage.h

Purpose: ARC assembly linkage, alignment, paired register save/load, and fast-memory section annotations. Important APIs/types/functions: defines `ASM_NL`, `__ALIGN`, assembler macros `ST2`, `LD2`, `ARCFP_DATA`, `ARCFP_CODE`, `ENTRY_CFI`, `END_CFI`, and C attributes `__arcfp_code`/`__arcfp_data`. Control flow: macros choose `std/ldd` when LL64 exists or two 32-bit accesses otherwise; code/data section macros choose ICCM/DCCM sections by config. State and persistence: affects emitted object sections and stack stores. Dependencies/integration: used by ARC assembly entry and optimized routines. Risks: wrong paired-store offsets corrupt `pt_regs`; section annotations must match linker script support. Test signals: assembly build, unwind metadata, context-save tests, and ICCM/DCCM config builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/linkage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/mach_desc.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/mach_desc.h

Purpose: ARC machine descriptor definitions used to bind platform setup to device-tree compatible strings. Important APIs/types/functions: defines `struct machine_desc` and macros/sections for declaring machine descriptions. Control flow: compile-time descriptors are placed in a dedicated table and selected during early boot by compatible matching. State and persistence: descriptor table persists in kernel image; selected descriptor drives platform callbacks. Dependencies/integration: used by ARC platform code and early OF setup. Risks: missing or wrong compatible strings prevent platform initialization. Test signals: boot on each ARC platform DT, descriptor matching logs, and linker section validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/mach_desc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/mmu-arcv2.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/mmu-arcv2.h

Purpose: ARC MMUv3/MMUv4 register definitions, TLB command constants, and ASID/PGD setup helpers. Important APIs/types/functions: defines `ARC_REG_TLBPD*`, `ARC_REG_TLBINDEX`, `ARC_REG_TLBCOMMAND`, `ARC_REG_PID`, TLB command values, PTE bit masks, `is_pae40_enabled`, `mmu_setup_asid`, `mmu_setup_pgd`, and assembly macro `ARC_MMU_REENABLE`. Control flow: compile-time register numbers differ for MMUv3 vs MMUv4; setup helpers write AUX PID and scratch PGD registers. State and persistence: mutates hardware MMU PID, TLB enable bits, and cached PGD register. Dependencies/integration: used by `mmu_context.h`, TLB miss handlers, and page-table code. Risks: wrong register selection or PAE40 assumptions break address translation. Test signals: TLB miss/fault tests, context switches, PAE40 builds, and MMUv3/MMUv4 boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/mmu-arcv2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/mmu.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/mmu.h

Purpose: ARC MM context type and shared MMU declarations. Important APIs/types/functions: defines `mm_context_t` as per-CPU ASID array and declares `do_tlb_overlap_fault`, then includes `mmu-arcv2.h`. Control flow: type/declaration header only. State and persistence: each `mm_struct` persists ASID generation per CPU. Dependencies/integration: used by scheduler MM switching, TLB code, and fault handling. Risks: ASID array size and per-CPU semantics must match TLB shootdown design. Test signals: SMP context switch tests and duplicate/overlap TLB fault paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/mmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/mmu_context.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/mmu_context.h

Purpose: ARC ASID allocation and MM context switching. Important APIs/types/functions: defines ASID masks/cycle constants, per-CPU `asid_cache`, helpers `asid_mm`, `hw_pid`, `get_new_mmu_context`, `init_new_context`, `destroy_context`, and `switch_mm`. Control flow: under local IRQ disable, validates whether an mm ASID belongs to the current generation, allocates a new ASID on generation mismatch, flushes local TLB on 8-bit rollover, writes MMU PID, records mm in `mm_cpumask`, caches PGD, and switches context. State and persistence: mutates `mm->context.asid[cpu]`, per-CPU ASID cache, MMU PID/PGD registers, and mm CPU mask. Dependencies/integration: scheduler, TLB flushing, and generic MM hooks. Risks: stale ASIDs, rollover flush, and intentionally aggregating `mm_cpumask` are correctness-critical. Test signals: fork/exec/context-switch stress, SMP TLB shootdown, ASID rollover tests, and munmap stale-entry checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/mmu_context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/module.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/module.h

Purpose: ARC per-module architecture metadata. Important APIs/types/functions: includes `asm-generic/module.h` and defines `struct mod_arch_specific` with optional DWARF unwind fields `unw_info`/`unw_sec_idx` and section-string pointer `secstr`. Control flow: data-structure definition only; module loader code fills and consumes the fields. State and persistence: metadata persists for each loaded module. Dependencies/integration: used by generic module loading and ARC DWARF unwind support when `CONFIG_ARC_DW2_UNWIND` is enabled. Risks: wrong unwind section index or section-string storage breaks module stack unwinding and relocation diagnostics. Test signals: module build/load/unload, module stacktrace unwinding, and configs with/without DWARF unwind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/module.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/page.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/page.h

Purpose: ARC page geometry, physical address masks, page copy/clear helpers, and page-table scalar types. Important APIs/types/functions: defines `MAX_POSSIBLE_PHYSMEM_BITS`, `PAGE_MASK_PHYS`, `clear_page`, `copy_page`, `copy_user_page`, `copy_user_highpage`, `clear_user_page`, `pgd_t`/optional higher-level table types, `virt_to_pfn`, `virt_to_page`, `virt_addr_valid`, `VMA_DATA_DEFAULT_FLAGS`, and generic memory model inclusion. Control flow: compile-time PAE40 and page-table-level conditionals; runtime helpers delegate to memcpy/memset or external highpage functions. State and persistence: mutates page contents and describes page-table entries. Dependencies/integration: used by MM, pgtable, highmem, and fault code. Risks: comments warn `virt_to_pfn` can truncate PAE40 if misused for physical addresses. Test signals: PAE40 builds, page copy/clear tests, NX data VMA checks, and memory model tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/page.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/pci.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/pci.h

Purpose: ARC PCI core constants for resource assignment. Important APIs/types/functions: defines `PCIBIOS_MIN_IO` as `0x100`, `PCIBIOS_MIN_MEM` as `0x100000`, and `pcibios_assign_all_busses()` as true. Control flow: macro-only policy consumed by PCI setup. State and persistence: PCI bus/device state is managed by the PCI core, not this header. Dependencies/integration: used when `CONFIG_PCI` is enabled and platform PCI host support enumerates devices. Risks: minimum resource windows and forced bus assignment must match platform firmware/host bridge expectations. Test signals: PCI enumeration, BAR resource assignment, config-space access, and DMA-capable PCI device tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/perf_event.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/perf_event.h

Purpose: ARC performance-counter register and event ID definitions. Important APIs/types/functions: defines `ARC_PERF_MAX_COUNTERS`, CC/PCT auxiliary register numbers, PCT config/control bits, endian-aware `arc_reg_pct_build` and `arc_reg_cc_build` bitfields, ARC-specific hardware event IDs such as `PERF_COUNT_ARC_DCLM`, and `perf_arch_bpf_user_pt_regs`. Control flow: header-only constants and build-register layouts; runtime PMU code programs the registers. State and persistence: hardware counters and perf core state live outside this header. Dependencies/integration: selected by `HAVE_PERF_EVENTS` and consumed by ARC PMU/perf code and eBPF perf register access. Risks: wrong register or bitfield definitions cause bad event discovery, sampling, or overflow handling. Test signals: `perf stat`, `perf record`, overflow interrupt tests, endian builds, and PMU availability probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/perf_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/pgalloc.h -->
# sources/distributed-fs/ceph-client/arch/arc/include/asm/pgalloc.h

Purpose: ARC page-table allocation/population helpers. Important APIs/types/functions: defines `pmd_populate_kernel`, `pmd_populate`, `pgd_alloc`, optional `p4d_populate`, `pud_populate`, and TLB-free macros for PUD/PMD/PTE pages. Control flow: populates upper levels with pointer-valued entries, allocates PGD through generic allocator, copies kernel/vmalloc PGD ranges from `swapper_pg_dir`, and adapts to page-table level count. State and persistence: allocates and initializes per-mm page tables. Dependencies/integration: used by generic MM page-table allocation and ARC vmalloc mapping. Risks: PAE40 comment notes PTE tables must remain in low memory; copying wrong PGD range breaks vmalloc/module mappings. Test signals: fork/exec/vmalloc tests, page-table accounting, multi-level build configs, and highmem/PAE40 builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/include/asm/pgalloc.h -->
