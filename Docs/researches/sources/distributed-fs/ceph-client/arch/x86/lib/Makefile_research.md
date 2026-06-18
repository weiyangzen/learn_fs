# sources/distributed-fs/ceph-client/arch/x86/lib/Makefile

Purpose: controls which x86 architecture library objects are built into the kernel or lib archive and how generated instruction attribute tables are produced. It is the integration map for low-level delay, memory, checksum, instruction decoding, user access, MSR, cache, KASLR, error injection, retpoline, and atomic helper files.

Important build rules: disables KCOV and KCSAN sanitization for `delay.o`, and removes ftrace from `delay.o` under KCSAN to avoid lockdep/ftrace/KCSAN/udelay recursion. Defines the `inat-tables.c` generation rule using `arch/x86/tools/gen-insn-attr-x86.awk` over `x86-opcode-map.txt`; `inat.o` depends on the generated table and `clean-files` removes it. Common `lib-y` includes delay, misc, cmdline, cpu, usercopy, getuser, putuser, memcpy, and pc-conf-reg. Conditional entries add copy-machine-check, instruction decoder, KASLR, error injection, retpoline, SMP MSR/cache helpers, and always-built MSR/IOMEM/hweight objects.

Control flow: Kbuild selects 32-bit versus 64-bit variants based on `CONFIG_X86_32` and `BITS`. On 32-bit it includes `atomic64_32.o`, CX8 or 386 atomic64 assembly, checksum/string/memmove/cmpxchg8b helpers. On 64-bit it conditionally includes non-generic checksum helpers and always includes clear/copy page, memmove/memset, user copy, cmpxchg16b emulation, and BHI code.

State and persistence behavior: build-time only. It generates `inat-tables.c` in the object tree and influences final kernel symbol availability; it does not create runtime state.

Dependencies/integration points: integrates Kbuild config symbols, awk tool generation, architecture opcode maps, and low-level library sources used by the rest of the kernel. Exported symbols from built objects are consumed by core kernel, modules, KVM, networking, and memory subsystems.

Risks: wrong conditional selection can create duplicate symbols, missing architecture helpers, instrumentation recursion, or broken instruction decoding. The generated `inat-tables.c` must stay in sync with opcode maps. Sanitizer/ftrace flags are safety-critical for delay code.

Test signals: allnoconfig/defconfig and 32/64-bit build coverage, `make clean` for generated files, instruction decoder builds with `CONFIG_INSTRUCTION_DECODER`, and configs with KCSAN/KCOV/ftrace enabled are the main signals.
