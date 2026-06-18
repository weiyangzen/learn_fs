# sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest/prefix.pl

`prefix.pl` converts streamed test output into TAP comments by prefixing each line with `# `. It is used by the selftest runner to keep arbitrary stdout/stderr from being parsed as TAP results.

The script uses Perl `sysread()` one byte at a time, binary stdin/stdout modes, `IO::Handle`, and stdout autoflush. It tracks whether the next byte starts a new line.

Control flow loops until EOF. At the beginning of each line it prints `# `, then echoes bytes unchanged; newline marks the next byte as needing a prefix. State is only the boolean line-start flag.

Dependencies are Perl and a pipeline from `runner.sh`. The main risk is byte-at-a-time overhead on huge logs, but it preserves unbuffered streaming. Pass signal is every output line appearing as a TAP comment without delaying until process exit.
