# sources/distributed-fs/ceph-client/tools/objtool/builtin-check.c

Purpose: command-line entry for `objtool <actions> [options] file.o`, option parsing, validation, backup handling, output-copy handling, and orchestration of the `check()` pipeline.

Important APIs/types/functions: global `opts`, `objname`, `orig_argc`; `cmd_parse_options()` handles environment and CLI options; `opts_valid()` enforces option combinations; `copy_file()` and `make_backup()` preserve object files; `objtool_run()` opens the object, runs `check()`, writes changes, and closes ELF state.

Control flow: parses `OBJTOOL_ARGS` first, then `OBJTOOL_VERBOSE`, then CLI args. It validates actions, supports `--dump=orc` fast path, copies to `--output` when needed, opens the ELF, rejects linked objects without `--link`, runs `check(file)`, and writes only when not dry-run and ELF changed.

State and persistence behavior: `opts` is global process state. `copy_file()` persists output or `.orig` backup files. `objtool_run()` persists modified ELF data through `elf_write()`.

Dependencies and integration points: depends on `subcmd/parse-options`, `objtool_open_read()`, `check()`, `orc_dump()`, warning infrastructure, and the ELF writer.

Risks: `OBJTOOL_ARGS` parsing splits only on spaces and mutates the environment string. Some file descriptors in error paths may leak in `copy_file()`, though process lifetime is short. Option validation must stay aligned with feature dependencies.

Test signals: CLI tests should cover required-action errors, invalid combinations, env options, dry-run/output behavior, backup command reconstruction, `--dump=orc`, and `--werror` warning promotion.
