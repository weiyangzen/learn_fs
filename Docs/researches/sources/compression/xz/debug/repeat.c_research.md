<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/debug/repeat.c -->
# sources/compression/xz/debug/repeat.c

Purpose: emits a user-provided string repeatedly, originally useful for stress testing run-length/subblock behavior.

Important APIs/types/functions: `main` parses `COUNT` with `strtoull`, measures `STRING` with `strlen`, writes it with `fwrite`, and checks output stream errors at exit.

Control flow: validate exactly two arguments, convert count, loop until count reaches zero, writing the byte sequence each time.

State and persistence: no persistent state; output is stdout.

Dependencies and integration: only common portability includes and stdio/string conversion.

Risks: invalid numeric text is accepted as zero or partial conversion because `strtoull` end pointer and overflow are ignored. Very large counts can produce unbounded output.

Test signals: run with small counts and compare byte-for-byte output; simulate closed stdout to verify nonzero exit.
<!-- END_FILE_RESEARCH: sources/compression/xz/debug/repeat.c -->
