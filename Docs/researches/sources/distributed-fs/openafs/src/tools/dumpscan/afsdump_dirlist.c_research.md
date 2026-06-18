# sources/distributed-fs/openafs/src/tools/dumpscan/afsdump_dirlist.c

Purpose: command-line utility that lists entries from an AFS directory data file, not a full volume dump.

Important APIs/functions: `parse_options` handles `-h`, `-q`, and `-v`, defaulting input to `-` for stdin. `my_error_cb` counts parse errors and emits com_err messages unless quiet. `main` initializes relevant OpenAFS error tables, opens the input as an `XFILE`, sets `dp.print_flags = DSPRINT_DIR`, marks `DSFLAG_SEEK` when possible, and calls `ParseDirectory(&input_file, &dp, 0, 1)` where `toeof=1` means parse directory pages until EOF.

State/dependencies: no persistent output; it reads only. It depends on `libdumpscan`, `libxfiles`, OpenAFS error tables, and directory format definitions from `directory.c`/`dumpfmt.h`.

Risks/test signals: the process exits zero even if `ParseDirectory` returns an error after printing `*** FAILED`, so callers must inspect output/stderr rather than only exit status. Directory corruption is reported through callbacks, but quiet mode suppresses details.
