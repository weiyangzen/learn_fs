<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-otcore.c -->
# sources/cloud-native/ostree/tests/test-otcore.c

## Purpose
`test-otcore.c` unit-tests core helpers for Ed25519 key handling and root argument/config preparation.

## Important APIs, Types, And Functions
The file includes `otcore.h` and defines tests such as `test_ed25519`, `test_prepare_root_cmdline`, and `test_prepare_root_config`.

## Control Flow
The Ed25519 test validates expected parsing/formatting behavior for public key material. The root command-line and config tests build input strings/config snippets and verify helper output for prepared root arguments, including expected substitutions and defaults.

## State And Persistence
All state is local GLib strings, variants/config objects, and errors. No repository or sysroot is modified.

## Dependencies And Integration Points
The helpers are used by signature verification and boot/root preparation paths in OSTree core code.

## Risks And Test Signals
Passing signals include valid key parsing, rejection of malformed data, and stable root argument generation. Regressions here can affect boot configuration and signature-related command behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-otcore.c -->
