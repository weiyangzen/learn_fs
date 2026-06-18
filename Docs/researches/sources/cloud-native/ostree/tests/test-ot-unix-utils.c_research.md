<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-ot-unix-utils.c -->
# sources/cloud-native/ostree/tests/test-ot-unix-utils.c

## Purpose
`test-ot-unix-utils.c` validates Unix utility helpers for path/filename validation and human-readable durations.

## Important APIs, Types, And Functions
It tests `ot_util_path_split_validate`, `ot_util_filename_validate`, and `ot_format_human_duration` or equivalent duration formatting from `ot-unix-utils.h` and `ot-gio-utils.h`.

## Control Flow
The path test validates accepted relative paths and rejects empty, absolute, parent-traversal, or malformed paths. The filename test checks single path component constraints. The duration test checks formatting for seconds/minutes/hours style values.

## State And Persistence
No persistent state exists; all data are local strings, arrays, and errors.

## Dependencies And Integration Points
These utilities protect repository object/path handling and user-facing time formatting in CLI output.

## Risks And Test Signals
Path validation is security-sensitive because it prevents traversal or invalid names. Passing signals include rejection of dangerous path forms and stable human-duration strings.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-ot-unix-utils.c -->
