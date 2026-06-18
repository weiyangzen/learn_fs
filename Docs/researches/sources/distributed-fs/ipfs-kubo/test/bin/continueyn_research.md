# sources/distributed-fs/ipfs-kubo/test/bin/continueyn

Purpose: interactive shell confirmation helper that exits successfully for yes and unsuccessfully for no, with non-interactive contexts treated as yes.

Important interface: no arguments are used. The script first checks `test -t 1 || exit 0`, so when stdout is not a terminal it exits 0 immediately. In interactive use it prompts with `read -p "continue? [y/N] " REPLY`, emits a blank line, and returns 0 only for replies beginning with `Y` or `y`; all other replies return 1.

Control flow and state are trivial; there is no persistence. Dependencies are `/bin/sh` and a shell supporting `read -p`, which is common but not strictly POSIX in all shells. Integration points are build/test scripts that want opt-in pauses for human runs but must not block automation. Risks include checking stdout rather than stdin for terminal detection, shell portability of `read -p`, and default-deny behavior in terminals. Test signal is manual or wrapper-level: automated use should observe a zero exit without blocking.
