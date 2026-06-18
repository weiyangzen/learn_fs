<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/profile2linkerlist.pl -->
# sources/distributed-fs/ceph-client/scripts/profile2linkerlist.pl

## Purpose

`profile2linkerlist.pl` converts sorted `readprofile` output into linker-script section patterns for hot function text sections.

## Important APIs, Types, and Functions

The script reads lines from stdin or file arguments, extracts a function name with a regex, and prints `*(.text.<function>)` unless the line contains `unknown` or `total`.

## Control Flow

It assumes the input has already been sorted, usually by `readprofile | sort -rn`. It processes each line independently and emits linker-consumable section patterns in input order.

## State and Persistence Behavior

It has no meaningful retained state beyond the current line. It writes only stdout.

## Dependencies and Integration Points

It depends on Perl and the expected profiler output format. It integrates with profile-guided kernel layout or linker-list experiments.

## Risks and Edge Cases

Unexpected profiler formats can produce empty or wrong function names because the regex result is not validated before printing. Duplicate symbols are not deduplicated. Stale profile data can produce ineffective ordering.

## Test Signals

Feed sorted readprofile samples with duplicates, `unknown`, `total`, malformed lines, and symbols absent from the final link. Compare emitted order with expected input order and linker acceptance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/profile2linkerlist.pl -->
