<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-ot-tool-util.c -->
# sources/cloud-native/ostree/tests/test-ot-tool-util.c

## Purpose
`test-ot-tool-util.c` unit-tests small command-line parsing helpers used by OSTree tools.

## Important APIs, Types, And Functions
The file tests `ot_parse_boolean` and `ot_parse_keyvalue` from `ot-tool-util.h`, using GLib assertions and error checks.

## Control Flow
`test_ot_parse_boolean` checks accepted boolean spellings and invalid values. `test_ot_parse_keyvalue` checks splitting of `key=value` strings, missing separator errors, empty values or keys as applicable, and returned allocations.

## State And Persistence
All state is local strings, booleans, and `GError` instances.

## Dependencies And Integration Points
These helpers are used by CLI and remote/config option parsing, where consistent key/value and boolean handling prevents ambiguous user input.

## Risks And Test Signals
Passing signals include correct parse results, allocated key/value outputs, and errors for malformed inputs. The main risk is relaxing parsing in a way that silently accepts bad CLI options.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-ot-tool-util.c -->
