# sources/distributed-fs/ceph-client/scripts/recordmcount.pl

Purpose: `recordmcount.pl` is the older Perl implementation of the ftrace mcount-table generator. It parses `nm` and `objdump` output, emits temporary assembly containing `__mcount_loc` entries, compiles that assembly, and links it back into the original object.

Important APIs, types, and functions: the script is driven by twelve positional arguments: architecture, endian, bit width, tool paths for objdump/objcopy/cc/ld/nm/rm/mv, module flag, and input object. Architecture blocks define `$local_regex`, `$weak_regex`, `$section_regex`, `$function_regex`, `$mcount_regex`, `$mcount_adjust`, `$alignment`, `$section_type`, and assembly data directive `$type`. `update_funcs()` writes pending offsets relative to a chosen reference function and records local symbols that must be globalized during the link.

Control flow: it skips `kernel/trace/ftrace.o`, normalizes x86 arch names, configures architecture-specific objdump and linker options, runs `nm` to collect local and weak symbols, then runs `objdump -hdr` to find executable sections, functions, and mcount call relocations. For each section, it selects a safe reference function, writes offset expressions to a temporary `.s`, compiles it, and either links it directly or first globalizes local reference symbols, links, then localizes them again.

State and persistence: the script mutates the input object by creating temporary files in the input object's directory: `.tmp_mc_*.s`, `.tmp_mc_*.o`, `.tmp_gl_*`, and `.tmp_mx_*`. Successful processing overwrites or moves the linked result back to the input path. It keeps transient hash state for local, weak, and converted symbols.

Dependencies and integration points: it depends on exact `nm` and `objdump` textual formats, assembler syntax, `objcopy` symbol transformations, and `ld -r`. It supports many architecture-specific patterns including x86, s390, sh, powerpc, arm, arm64, sparc64, mips, microblaze, riscv, and csky.

Risks: textual disassembly parsing is fragile across binutils versions and architectures. Backtick command invocations do not check every exit code directly. Temporary file names are predictable per object prefix. The duplicate `__mcount_loc` check exits with failure, unlike the C path's graceful already-done signal.

Test signals: run against representative objects for each supported architecture, compare `__mcount_loc` output against the C tool, verify local-symbol conversion round trips, and test duplicate processing. Link-time ftrace selftests and inspection of temp-free successful builds are the primary integration checks.
