# sources/distributed-fs/ipfs-kubo/test/bin/checkflags

Purpose: POSIX shell helper that prints a message only when a persisted flag value changes. It is used as a small stateful gate for test or build messages.

Important interface: `checkflags FILE VALUES MSG...`. It validates at least three arguments, assigns the first argument to `FLAG_FILE`, the second to `FLAG_VALS`, and the remainder to `FLAG_MSGS`. If the file does not exist it is touched. The script compares `x"$FLAG_VALS"` to `x"$(cat "$FLAG_FILE")`; the `x` prefix prevents values that begin with `-` or are empty from being interpreted specially by `test`.

Control flow is linear: validate arguments, ensure the state file exists, compare stored and new values, then echo the message and overwrite the file on change. State and persistence are exactly the contents of `FLAG_FILE`. Dependencies are `/bin/sh`, `cat`, `touch`, and shell redirection. Risks include an unquoted `test -f $FLAG_FILE` path, so paths with whitespace or glob characters are unsafe, and concurrent writers can race because updates are not atomic. Test signal is minimal; correctness is observable by repeated invocations with changed or unchanged values.
