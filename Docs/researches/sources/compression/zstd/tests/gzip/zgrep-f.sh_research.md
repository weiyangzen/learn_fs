<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/gzip/zgrep-f.sh -->
## sources/compression/zstd/tests/gzip/zgrep-f.sh

Purpose: Tests `zgrep -f -` pattern-file-from-stdin behavior and related edge cases.

Important APIs and functions: Sources `init.sh`, uses `zgrep`, `gzip`, `compare`, and optionally bash process substitution.

Control flow: It writes pattern file `n`, duplicates it as `haystack`, compresses `haystack`, then runs `zgrep -f - haystack.gz < n` and requires output equal to `n`. In bash outside POSIX mode it additionally checks process substitution with two compressed haystacks. Finally it checks `echo a-b | zgrep -e -` succeeds, covering literal dash patterns.

State and persistence: Creates `n`, `haystack.gz`, optional `nn`, and `out`.

Dependencies and integration points: Exercises `zgrep` stdin handling where both the pattern source and compressed data may involve `-` semantics or shell redirection.

Risks: The process-substitution branch is bash-specific and skipped in most POSIX shells. `compare out n` intentionally reverses expected/actual names but comparison is symmetric for equality.

Test signals: `zgrep -f -` must return zero and output the two matching lines; dash pattern handling must not be mistaken for an option.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/gzip/zgrep-f.sh -->
