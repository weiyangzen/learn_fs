# sources/distributed-fs/coda/coda-src/vtools/codaconfedit.c

## Purpose

`codaconfedit.c` is a small configuration-file lookup and rewrite utility for Coda config files. It locates a config file, optionally copies a `.ex` template, reads variable values, and rewrites variables while preserving nearby comments and older definitions.

## Important APIs, Types, and Functions

`main()` implements three modes: print resolved config path, print variable value, or set variable value. `write_val()` emits `name="value words"` lines. `match_var()` recognizes variable assignments with leading whitespace. `do_rewrite()` writes a `.bak`, writes a `.new` with previous active assignments commented out, inserts the new value after the last related line, and renames `.new` over the original. `copy_template()` locates `<confbase>.ex` using `codaconf_file()` and copies it with `copyfile_byname()`.

## Control Flow

The utility resolves the config path with `codaconf_file()`. Missing files in set/lookup modes trigger template copying. For reads, it initializes only that config file and calls `codaconf_lookup()`. For writes, it compares the existing value to the requested argv words and skips rewriting if already equal; otherwise it performs the two-pass rewrite.

## State and Persistence Behavior

It writes `<conffile>.bak`, `<conffile>.new`, and finally replaces the target config file. It sets `umask(022)` for the generated file. It may create a real config from a template even for lookup, so a read-like operation can persist data.

## Dependencies and Integration Points

It depends on Coda `codaconf_file`, `codaconf_init_one`, `codaconf_lookup`, and the local `copyfile` helper. It assumes Coda config syntax of `key=value` with optional quotes.

## Risks and Test Signals

`MAXLINELEN` truncates long lines during rewrite. `write_val()` does not escape quotes or shell metacharacters in values. The value comparison loop references `argv[i]` through `i <= argc`, which can read one past the final valid argument. `rename()` replacement is not followed by permission/ownership preservation. Tests should cover missing templates, long lines, comments, multiple existing definitions, quoted values, idempotent set, write failures, and values containing quotes or spaces.
