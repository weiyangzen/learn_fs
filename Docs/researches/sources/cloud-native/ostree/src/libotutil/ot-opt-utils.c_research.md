# sources/cloud-native/ostree/src/libotutil/ot-opt-utils.c

## Purpose
Provides a CLI option helper for reporting usage errors with full help text.

## Important APIs, Types, And Functions
`ot_util_usage_error(context, message, error)` prints `g_option_context_get_help` output to stderr and sets a `G_IO_ERROR_FAILED` error with the provided message.

## Control Flow
The function obtains help text, prints it, frees it, and sets the error literal. It does not return a boolean; callers decide their error flow after invoking it.

## State And Persistence Behavior
No persistent state. It writes help text to stderr and populates a `GError`.

## Dependencies And Integration Points
Depends on GLib option parsing and GIO error domains. Used by command-line tools that want consistent usage output on invalid options.

## Risks
Always prints to stderr, which can be undesirable in library-like contexts or tests expecting quiet error construction. If `error` is NULL, `g_set_error_literal` is not called but help still prints.

## Test Signals
CLI tests should verify help text is printed and the expected error message/domain/code is set for invalid arguments.
