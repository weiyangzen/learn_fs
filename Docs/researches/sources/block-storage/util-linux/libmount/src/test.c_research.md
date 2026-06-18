# File Research: sources/block-storage/util-linux/libmount/src/test.c

## Scope

Provides the small shared test-program dispatcher used by libmount files compiled with `TEST_PROGRAM`.

## Public And Internal APIs Covered

- `mnt_run_test(struct libmnt_test *tests, int argc, char *argv[])`.

## Control Flow And Behavior

- Requires at least one command argument and treats `--help` / `-h` as usage.
- Initializes libmount debugging with `mnt_init_debug(0)`.
- Searches the supplied `struct libmnt_test` array by command name and calls the matched test body with shifted argc/argv.
- Prints `FAILED [rc=%d]` for nonzero test return codes.
- Prints generated usage including every test name and usage string when no test matches or arguments are insufficient.
- Converts test result to process exit status: zero becomes `EXIT_SUCCESS`, any nonzero/usage failure becomes `EXIT_FAILURE`.

## Dependencies

- Requires `TEST_PROGRAM` mode and `mountP.h`.
- Uses `program_invocation_short_name`, `assert`, `strcmp`, and standard exit constants.

## Risks And Invariants

- Test arrays must be NULL-terminated.
- Negative return values are treated as bad usage and trigger the usage text.
- The dispatcher assumes test bodies understand the shifted argument vector where `argv[0]` is the test name.
