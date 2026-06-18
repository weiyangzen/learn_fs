# sources/distributed-fs/ceph-client/scripts/bloat-o-meter

## Purpose
`bloat-o-meter` compares symbol sizes between two object files and reports growth, shrinkage, additions, removals, and total size delta.

## APIs, Types, And Functions
The Python script uses `argparse`, `os.popen()` to run `nm --size-sort`, and regex cleanup for generated `.NUMBER` suffixes. Main helpers are `getsizes()`, `calc()`, and `print_result()`.

## Control Flow
Arguments select text, data, combined, or categorized output and optional cross-tool prefix. The script reads old and new symbol tables, filters generated symbols, aggregates sizes by normalized name, computes common/new/removed deltas, sorts by delta, and prints summary plus per-symbol table.

## State And Persistence
State is in-memory dictionaries of symbol sizes. It does not write files.

## Dependencies And Integration Points
It depends on Python 3 and `nm` compatible output. It integrates with kernel size-regression review workflows and supports cross builds through an `nm` prefix.

## Risks And Test Signals
Risks include shell command construction with filenames, unexpected `nm` output, and name coalescing hiding distinct static symbols. Test signals are sensible totals for known object pairs and categorized output matching text/data symbol classes.
