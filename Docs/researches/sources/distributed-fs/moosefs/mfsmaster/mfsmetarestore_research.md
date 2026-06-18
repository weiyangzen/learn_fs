## sources/distributed-fs/moosefs/mfsmaster/mfsmetarestore

Purpose: shell compatibility stub for the removed `mfsmetarestore` command.

Important behavior: the script has a `/bin/sh` shebang and prints one message: `mfsmetarestore has been removed in version 1.7, use mfsmaster -a instead`.

Control flow: there is no option parsing or branching; every invocation emits the message and exits with the shell's status for `echo`, normally zero.

State and persistence behavior: no state is read or written. It does not invoke `mfsmaster -a`; it only informs the user.

Dependencies and integration points: depends only on POSIX shell and `echo`. Packaging or install rules may still ship it to preserve user-facing command compatibility.

Risks: returning success may confuse automation that expects a restore attempt. If scripts parse stderr, note the message is written to stdout.

Test signals: execute the script and assert exact message text and expected zero exit status, or deliberately change exit behavior if product policy requires failure for removed commands.
