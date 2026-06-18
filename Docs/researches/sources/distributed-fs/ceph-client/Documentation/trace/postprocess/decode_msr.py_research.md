<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/trace/postprocess/decode_msr.py -->
# sources/distributed-fs/ceph-client/Documentation/trace/postprocess/decode_msr.py

## Purpose
Streaming trace postprocessor that annotates `read_msr` and `write_msr` trace lines with symbolic MSR names from an `msr-index.h`-style header.

## Important APIs, Types, And Functions
- Top-level `msrs` dictionary maps numeric MSR values to macro names.
- Header parser matches `#define MSR_* 0x...` lines.
- `extra_ranges` synthesizes names for last-branch-record and LBR info MSR ranges not necessarily present as individual defines.
- The stdin loop searches for `(read|write)_msr:` trace events and replaces the raw numeric token with `NAME(hex)`.

## Control Flow
At startup the script opens the first CLI argument or `msr-index.h`, builds the lookup table, then processes stdin line by line. For each matching trace event, it parses the MSR number, checks direct defines, checks the synthetic ranges, optionally rewrites the line, and prints the resulting line.

## State And Persistence
State is in memory only. The script does not mutate files; it is intended for pipelines such as `decode_msr.py arch/x86/include/asm/msr-index.h < trace`.

## Dependencies And Integration Points
Depends on Python, regex support, a Linux x86 MSR index header, and trace output containing `read_msr:` or `write_msr:` records with lowercase hexadecimal IDs. It integrates with ftrace/perf text streams.

## Risks And Edge Cases
It assumes a header argument exists or `msr-index.h` is in the current directory. Regexes only match `MSR_` macros with hex literals and trace IDs matching `[0-9a-f]+`. `print(j)` adds an extra newline because input lines already include one, so output may be double-spaced.

## Test Signals
Feed a small synthetic header and trace containing direct MSR hits, range hits, unknown MSRs, and non-MSR lines. Expected output preserves nonmatches and annotates only recognized IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/trace/postprocess/decode_msr.py -->
