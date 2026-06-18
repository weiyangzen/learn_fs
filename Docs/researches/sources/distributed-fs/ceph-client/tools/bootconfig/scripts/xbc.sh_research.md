<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bootconfig/scripts/xbc.sh -->
# sources/distributed-fs/ceph-client/tools/bootconfig/scripts/xbc.sh

Purpose: this file is a small shell adapter around the `bootconfig -l` flattened output format. It gives other bootconfig scripts key lookup, branch detection, value extraction, and subkey enumeration.

Important APIs/functions: initialization resolves `BOOTCONFIG` from the sibling build output or `PATH`. `xbc_init()` creates a temporary file, traps cleanup, and stores `bootconfig -l FILE` output. `xbc_get_val()` extracts values for a key and uses `sed`/`xargs` to split bootconfig arrays into one value per line, optionally limited by `xargs -L`. `xbc_has_key()` and `xbc_has_branch()` are grep probes. `xbc_subkeys()` computes prefix depth and extracts child key names.

Control flow: callers source the file, call `xbc_init BCONF`, then issue grep-based queries against `$XBC_TMPFILE`. Cleanup removes the temporary file on exit or termination.

State and persistence: the only state is `$XBC_TMPFILE`, `$BOOTCONFIG`, and helper-local shell variables. The temporary flattened bootconfig file is removed by `xbc_cleanup()` unless the process is killed in a way that bypasses traps.

Dependencies and integration points: it depends on a compatible `bootconfig` binary, `mktemp`, `grep`, `cut`, `sed`, `xargs`, and POSIX shell. `bconf2ftrace.sh` depends on its key model and assumes flattened keys are emitted as `key = value`.

Risks: key names are interpolated directly into grep regular expressions, so regex metacharacters in keys can change matching semantics. Values are split through `xargs`, which strips quoting and can transform whitespace. `mktemp bconf-XXXX` creates the file in the current directory rather than a private temp directory. The error message spells "Erorr", and command lookup via `which` can be non-portable.

Test signals: tests should cover scalar values, arrays with spaces and quotes, nested keys, duplicate/same-key append behavior, missing keys, branch prefixes that are substrings of other prefixes, and cleanup of the temporary file after normal and signal exits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/bootconfig/scripts/xbc.sh -->
