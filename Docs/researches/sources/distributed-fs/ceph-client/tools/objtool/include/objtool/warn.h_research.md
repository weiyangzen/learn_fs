# sources/distributed-fs/ceph-client/tools/objtool/include/objtool/warn.h

Purpose: Defines objtool diagnostic macros that format object, ELF, glibc, function, instruction, and backtrace messages.

Important APIs/types/functions: `unindent`, `_WARN_H`, `___WARN`, `__WARN`, `__WARN_LINE`, `__WARN_ELF`, `__WARN_GLIBC`, `__WARN_FUNC`, `WARN_STR`, `WARN`, `WARN_FUNC`, `WARN_INSN`.

Control flow: Macros build location strings with section/symbol offsets, optionally include disassembly, honor `opts.werror`, and increment warning counters through shared builtin state.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Uses ELF symbol lookup, checker instruction formatting, libelf/libc error APIs, and objtool option globals.

Risks: Location formatting allocates memory in warning paths; missing symbols degrade diagnostics; `werror` changes severity strings without changing call sites.

Test signals: Warnings for raw messages, ELF errors, function offsets, instructions with/without disassembly, and `--werror` behavior.

Source coverage: researched from the complete local file (162 lines, 4735 bytes).
