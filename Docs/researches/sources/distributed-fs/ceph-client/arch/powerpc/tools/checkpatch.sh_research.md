# sources/distributed-fs/ceph-client/arch/powerpc/tools/checkpatch.sh

## Purpose
This script is a PowerPC wrapper around the kernel `scripts/checkpatch.pl` tool with architecture-maintainer preferred options and ignores.

## Important APIs, Types, And Functions
It computes `script_base` with `realpath $(dirname $0)` and `exec`s the top-level `scripts/checkpatch.pl` with `--subjective`, `--no-summary`, `--show-types`, and a curated set of `--ignore` rules. Arguments from the caller are appended unchanged with `$@`.

## Control Flow
The wrapper immediately replaces itself with checkpatch. There is no intermediate validation; all patch/file arguments are handled by the upstream script.

## State And Persistence
No state is persisted. Output and exit status are those of `checkpatch.pl`.

## Dependencies And Integration Points
It depends on bash, `realpath`, the kernel source tree layout relative to `arch/powerpc/tools`, Perl checkpatch, and PowerPC contribution workflows.

## Risks
Ignored warning categories encode local policy and can hide issues if used outside PowerPC review. The unquoted `dirname $0` command substitution is conventional here but could misbehave for paths containing whitespace. Any move in tree layout breaks the relative checkpatch path.

## Test Signals
Running the wrapper on a known patch should show typed checkpatch diagnostics without the ignored classes and should return checkpatch's status.
