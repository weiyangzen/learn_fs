# sources/distributed-fs/ceph-client/scripts/diffconfig

## Purpose
`diffconfig` compares two Linux `.config` files and prints sorted semantic configuration changes instead of raw line diffs.

## Important APIs, Types, and Functions
`readconfig()` parses `CONFIG_FOO=value` and `# CONFIG_FOO is not set` into dictionaries without the `CONFIG_` prefix, mapping unset symbols to `n`. `print_config()` emits normal or merge-style output. `show_diff()` handles options, default filenames, comparison, and sorting.

## Control Flow and State
The script accepts `-h`, `-m`, zero config paths, or two config paths. With no paths it compares `.config.old` to `.config`, prefixed by `$KBUILD_OUTPUT` when present. It computes removed, changed, and added keys and prints them in sorted order. State is in memory only.

## Dependencies and Integration
It depends on Python 3 and config file syntax. It is a kernel developer utility for reviewing configuration deltas.

## Risks and Test Signals
Parsing assumes every non-comment config line that starts with `CONFIG_` contains `=` and every unset line ends with ` is not set`. It mutates dictionaries during iteration in a way that is safe for the currently used loops over one dict while deleting from another or after collecting keys, but should be regression-tested. Test normal and merge output, default files, `KBUILD_OUTPUT`, strings with `=`, removed-only, added-only, and broken file errors.
