# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tdc_batch.py

## Purpose
Generates a `tc -batch` style file containing many flower filter commands for performance and scaling tests.

## Important APIs, Types, and Functions
Arguments include `device`, output `file`, `--number`, `--handle_start`, `--skip_sw`, `--share_action`, `--prio`, `--operation`, and `--mac_prefix`. Formatter functions are `format_add_filter`, `format_rep_filter`, and `format_del_filter`.

## Control Flow
After parsing arguments, it selects skip mode (`skip_hw` by default or `skip_sw`), action sharing, priority behavior, and operation formatter. It iterates three bytes of source/destination MAC suffix space, writes one command per handle, and exits after the requested line count.

## State and Persistence Behavior
The script writes the requested batch file and no other persistent state. Handles and MAC addresses are deterministic from `handle_start`, `number`, and `mac_prefix`.

## Dependencies and Integration Points
Depends on Python argparse and the file system. Generated commands target `tc filter add|replace|del ... flower ... action drop` and integrate with TDC batch/offload tests.

## Risks and Edge Cases
The output file is opened without context-manager cleanup except explicit close on normal completion. `--prio` caps `number` to `0x4000`; without it, very large counts can generate huge files. Delete formatter ignores MAC/action parameters, which is intentional but easy to misread.

## Test Signals
Signals are deterministic line count, correct handle range, expected skip mode, unique MAC generation, and valid `tc` batch syntax for add/replace/delete operations.
