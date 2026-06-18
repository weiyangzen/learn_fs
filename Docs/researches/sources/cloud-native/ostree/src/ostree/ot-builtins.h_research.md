# sources/cloud-native/ostree/src/ostree/ot-builtins.h

## Purpose
Declares the public builtin function prototypes for the `ostree` CLI command table. It provides a uniform signature for command implementations across this directory.

## Important APIs, Types, And Functions
The `BUILTINPROTO(name)` macro expands to `gboolean ostree_builtin_name(int argc, char **argv, OstreeCommandInvocation *invocation, GCancellable *cancellable, GError **error)`. The header declares builtins for admin, cat, config, checkout, checksum, commit, diff, export, find-remotes, create-usb, optional gpg-sign, init, log, pull, pull-local, ls, prune, refs, reset, fsck, sign, show, static-delta, summary, rev-parse, remote, and write-refs.

## Control Flow
There is no runtime control flow. The preprocessor includes `config.h` and `ot-main.h`, defines the macro, emits declarations, conditionally includes `gpg_sign` when GPGME is enabled, undefines the macro, and closes GLib extern "C" guards.

## State And Persistence
The header has no runtime state or persistence. Its compile-time state is the feature-gated declaration set controlled by configuration macros.

## Dependencies And Integration Points
It is included by builtin implementation files and the main command registration code. The uniform signature aligns all CLI functions with `OstreeCommandInvocation`, cancellation, and GLib error propagation.

## Risks And Edge Cases
Feature gates must match command table entries and implementation compilation or builds will fail. Adding/removing a builtin requires updating this header, the command table, docs, and shell completion. The macro hides the full signature, so readers must expand it mentally when navigating.

## Test Signals
Build coverage is the primary signal: all declared builtins must link under each feature matrix. CLI smoke tests for command availability should match declarations, especially GPGME-disabled builds.
