<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-help.sh -->
# sources/cloud-native/ostree/tests/test-help.sh

## Purpose
`test-help.sh` recursively verifies that OSTree CLI commands and subcommands expose usable help and usage output. It is a smoke test for command table wiring.

## Important APIs, Types, And Functions
The script defines `test_usage_output` and `test_recursive`, invokes `${CMD_PREFIX} ostree ... --help`, parses "Builtin Commands:" and subcommand sections, and uses shell conditionals plus TAP output.

## Control Flow
`test_recursive` walks command help text, finds listed subcommands, and recursively checks each subcommand's help. `test_usage_output` asserts usage/help content for the command being inspected. The script tracks whether expected subcommand sections were found and fails if the command tree cannot be traversed.

## State And Persistence
State is transient shell variables and captured help text. No repository or filesystem state is modified beyond temporary output files if the harness uses them.

## Dependencies And Integration Points
This test integrates the main `ostree` command dispatcher, builtin subcommand tables, option parser help generation, and shell parsing assumptions about help formatting.

## Risks And Test Signals
The test is intentionally wording-sensitive because it guards the user-facing help structure. Passing the single TAP test signals that top-level and nested commands accept `--help`, print usage information, and expose parseable subcommand lists.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-help.sh -->
