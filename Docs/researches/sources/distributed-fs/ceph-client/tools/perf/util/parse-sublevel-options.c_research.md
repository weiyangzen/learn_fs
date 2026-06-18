
# sources/distributed-fs/ceph-client/tools/perf/util/parse-sublevel-options.c

Purpose: parses comma-separated sublevel option strings of the form `name` or `name=value` into integer fields supplied by the caller.

Important APIs/types/functions: `parse_one_sublevel_option` duplicates one token, splits optional `=`, finds the matching `struct sublevel_option` by exact name, defaults value to 1, converts explicit values with `atoi`, and writes `*value_ptr`. Public `perf_parse_sublevel_options` tokenizes the input with `strtok` and applies the helper.

Control flow: the top-level function duplicates the whole string, iterates comma tokens, aborts on unknown names or allocation failure, frees temporary storage, and returns 0 or -1.

State and persistence: mutates caller-owned integer targets. No global state.

Dependencies: libc string/stdlib/stdio and perf debug logging.

Integration points: used by perf options that have nested sub-options, such as feature-specific mode strings.

Risks: `atoi` provides no validation for malformed or overflowing values, so callers must validate resulting integers if needed. Empty tokens are skipped by `strtok`. Test signals include known option names with and without values, unknown-name diagnostics, and malformed numeric value behavior.
