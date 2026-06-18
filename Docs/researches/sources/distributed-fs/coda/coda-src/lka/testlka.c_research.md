# sources/distributed-fs/coda/coda-src/lka/testlka.c

Purpose: interactive harness for registering LKA databases and trying lookaside hits for user-entered files. It supplies a dummy `LWP_DispatchProcess` so SHA helpers can link outside Venus.

Flow: starts by passing the quoted command string to `LKParseAndExecute`, then loops prompting for filenames. For each file it computes SHA, creates a temporary container, calls `LookAsideAndFillContainer`, reports hit/miss/error text, and removes the temporary file.

Risks and test signals: useful for manual validation of database creation and lookup, but not an automated test. It uses `printf(em)` directly, which is a format-string risk if error text contains percent sequences. It does not compare copied container bytes itself, relying on LKA verification.
