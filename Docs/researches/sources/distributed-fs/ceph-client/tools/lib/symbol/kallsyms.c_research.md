# sources/distributed-fs/ceph-client/tools/lib/symbol/kallsyms.c

Purpose: Parses Linux kallsyms-style symbol files and maps kallsyms symbol type letters to ELF type/function classification.

Important APIs/types/functions: `kallsyms2elf_type()` maps text/weak text to `STT_FUNC`, otherwise `STT_OBJECT`. `kallsyms__is_function()` identifies `T`/`W` symbols. `kallsyms__parse()` reads symbols and calls a user callback. Internal `read_to_eol()` skips malformed lines.

Control flow: `kallsyms__parse()` opens the file, initializes buffered `io`, reads a hex address, type char, separating spaces, then up to `KSYM_NAME_LEN` chars of name until newline. Each parsed symbol is passed to `process_symbol(arg, name, type, start)` and parsing stops on callback error.

State and persistence: Stateless except for file descriptor and local buffers. Callback owns persistence of parsed data.

Dependencies/integration: Uses `symbol/kallsyms.h`, `api/io.h`, ELF constants, file open/close APIs, and Linux types/ctype from the header.

Risks: Symbol names longer than `KSYM_NAME_LEN` are truncated and remaining line content is not explicitly discarded before the next loop, which can misparse overlong lines. Open failure returns `-1` without errno detail. Callback errors stop parsing immediately.

Test signals: Fixtures with valid symbols, malformed lines, lowercase/uppercase types, weak symbols, overlong names, callback stop behavior, and missing file.
