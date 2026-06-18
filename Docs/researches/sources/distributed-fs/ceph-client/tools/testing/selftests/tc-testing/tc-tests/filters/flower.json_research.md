<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/filters/flower.json -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/filters/flower.json

## Purpose
This fixture contains 12 high-scale and concurrency-focused tests for the `flower` classifier. Unlike the parser-heavy fixtures, this file stresses large rule counts, parallel `tc -b` execution, duplicate-key handling, shared action reference accounting, maximum handle display, and terse dump behavior. Categories include `filter/flower` and `filter/flower/concurrency`.

## Important APIs, Types, And Functions
The main API is `tc filter ... flower` on `$DEV2` ingress. The fixture also depends on helper scripts `tdc_multibatch.py` and `tdc_batch.py`, `$BATCH_DIR`, `$BATCH_FILE`, `find`, `xargs`, and parallel `tc -b` execution. Commands add, delete, or replace generated batches using `xargs -n 1 -P 10 $TC -b`, sometimes with `$TC -f -b` to force continuation on delete races. Single-rule cases use fields such as `handle 0xffffffff`, MAC/IP/TCP flower keys, `action ok`, and `action drop`. Terse dump uses `$TC -br filter show`.

## Control Flow
High-scale cases create `$BATCH_DIR`, install ingress on `$DEV2`, generate batch files for add/delete/replace workloads, execute those batches in parallel, and verify counts from `tc -s filter show dev $DEV2 ingress`. The first three tests add, delete, and replace 1 million filters. Two tests concurrently replace or delete the same 100k range from 10 tc instances. Two mixed tests add/delete or replace/delete from the same tcf_proto concurrently and expect half a million remaining filters. Other cases add a max-handle filter, add 1 million filters sharing one action, attempt a duplicate-key add, and verify terse dump content.

## State And Persistence Behavior
The persisted state is large flower filter tables under `$DEV2` ingress plus referenced gact action state. Count-based assertions expect exactly 1,000,000, 500,000, 100,000, zero, or one flower dump entries depending on the workload. The shared-action case verifies one gact action at index `1` with `ref 1000000 bind 1000000`, proving that many filters can bind the same action without creating separate actions. Duplicate-key handling expects the second add to fail with exit `2` and only one filter remaining. Terse dump state must show a filter handle but omit detailed keys such as `dst_mac`.

## Dependencies And Integration Points
This file depends heavily on helper scripts in the tc-testing directory, batch-file generation, shell utilities, parallel process scheduling, `$DEV2`, ingress qdisc support, flower classifier scaling, action reference counting, and iproute2 terse and statistics dump modes. It integrates with kernel classifier locking and concurrency paths more than with packet-match semantics.

## Risks
These tests are resource-intensive by design. Adding or replacing 1 million filters can consume significant CPU, memory, time, and kernel table resources, and parallel batches may expose timing-dependent failures. Count assertions are only as reliable as the generated batch files and cleanup. The expected exit `123` for forced parallel delete is from `xargs`, not directly from `tc`, so environment differences can change it. Terse dump assertions are sensitive to iproute2 output policy.

## Test Signals
Strong signals include successful million-rule add/delete/replace, safe concurrent replace/delete behavior on the same range, predictable mixed add/delete and replace/delete outcomes, maximum 32-bit flower handle display, shared gact action reference scaling to one million binds, duplicate-key rejection, and terse dump suppression of key details. Passing this fixture gives confidence in flower scalability, locking, reference accounting, and dump modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/filters/flower.json -->
