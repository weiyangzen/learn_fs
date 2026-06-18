# sources/distributed-fs/openafs/src/config/mc.c

Purpose: conditional copier used by `config.c` to turn Makefile prototypes into concrete platform Makefiles.

Important APIs/types/functions: defines token list `struct token`, `ParseLine`, `GetLine`, `FreeTokens`, and exported `mc_copy(FILE *ain, FILE *aout, char *alist[])`. Tags beginning with `-` become `TOK_DONTUSE` exclusions.

Control flow: `mc_copy` reads input line by line. Lines beginning with `<` are parsed as option tags, reset copying to false, and enable copying if any requested token matches unless a matching negative token disables it. Ordinary lines are written to the output only while copying is enabled. The initial mode copies until the first tag line.

State and persistence: state is local to the current copy operation: active token list and copying flag. Output persistence is the generated file written by the caller.

Dependencies and integration: linked into the `config` tool and used with sysname token lists generated from `config.c`.

Risks and test signals: risks include fixed `MAXLINELEN` and `MAXTOKLEN`, simplistic token delimiters, comments only handled indirectly by prototype format, and memory allocation without null checks. Signals are prototype sections selected by full sysname, `all`, architecture-only, OS-only, and negative tags, plus overlong-line handling.
