# sources/distributed-fs/ceph-client/scripts/unifdef.c

Purpose: `unifdef.c` removes or preserves C preprocessor conditional blocks according to supplied `-D`, `-U`, `-iD`, and `-iU` symbols. It is a standalone source-filtering utility imported from Tony Finch's unifdef.

Important APIs, types, and functions: key enums model line types (`Linetype`), conditional processing states (`Ifstate`), comment states, and line parser states. Global options implement `-b`, `-B`, `-c`, `-d`, `-e`, `-K`, `-k`, `-n`, `-s`, `-S`, `-t`, and output file behavior. `main()` parses options and sets up input/output, using a temp file when overwriting. `process()` drives the `trans_table` state machine. `parseline()` classifies preprocessor lines while tracking comments. `ifeval()`, `eval_table()`, and `eval_unary()` evaluate a subset of preprocessor expressions. `flushline()`, `keywordedit()`, `nest()`, and `unnest()` implement output and nesting behavior.

Control flow: after setup, `process()` repeatedly parses a line and invokes a state transition function indexed by current `Ifstate` and `Linetype`. Known true/false blocks are dropped or printed, unknown blocks pass through, and some `#elif`/`#else` lines are rewritten to maintain valid nesting after deletion. The expression parser supports numeric constants, `defined`, identifiers, `!`, parentheses, comparison, equality, `&&`, and `||`, with strict or short-circuit ambiguity rules.

State and persistence: it streams input to stdout or an output file. In overwrite mode, it writes a temp file with the original mode and renames it only after successful close. Exit status is 1 if any lines were deleted, 0 if unchanged, and 2 for errors.

Dependencies and integration points: used by build/config tooling that needs conditional source pruning. Depends only on libc/POSIX file APIs.

Risks: fixed limits (`MAXLINE`, `MAXDEPTH`, `MAXSYMS`) can reject extreme inputs. "Dodgy" directives with continuations/comments are intentionally conservative and may error. `debug()` uses `vwarnx` with a `va_list` in a way that merits portability review. Expression support is not a full C preprocessor.

Test signals: nested if/elif/else cases, ignored symbols, complement mode, symlist modes, CRLF input, overwrite mode, malformed directives, comments/strings containing preprocessor-looking text, and ambiguous expressions under `-K` and default mode.
