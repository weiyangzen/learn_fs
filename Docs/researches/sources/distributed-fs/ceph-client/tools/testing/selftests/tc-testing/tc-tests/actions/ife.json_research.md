# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/actions/ife.json

## Purpose
Defines 50 tests for the IFE tc action, covering encode/decode modes, metadata selection, controls, boundaries, cookies, delete/replace, invalid input handling, and JSON verification for metadata updates.

## Important APIs, Types, And Functions
Cases cover encode with `mark`, `prio`, and `tcindex`; controls `pass`, `pipe`, `continue`, `drop`, `reclassify`, and `jump`; 32-bit mark/prio boundaries; 16-bit tcindex boundaries; source/destination MAC parameters; custom EtherType; max and oversized action indexes; decode controls; invalid controls/arguments/type/MACs; invalid goto-chain replacement; delete valid/invalid index; and replacing decode actions into encode metadata using `matchJSON`.

## Control Flow
All cases use `nsPlugin`. Commands add, replace, delete, or get IFE actions. Most verification uses regexes over `tc actions get/list`; the final update cases use `tc -j actions get` with JSON matching to verify encoded metadata fields after replacement.

## State And Persistence
State is per-namespace IFE action metadata including mode, allowed/used metadata, MAC addresses, EtherType, control action, cookies, and indexes. Teardown clears created actions where specified.

## Dependencies And Integration Points
Depends on `NET_ACT_IFE` and metadata modules `NET_IFE_SKBMARK`, `NET_IFE_SKBPRIO`, and `NET_IFE_SKBTCINDEX`, plus tc JSON/text output and namespace setup.

## Risks
The suite is highly parser-output sensitive: metadata ordering, EtherType case, default decode allow-list, and JSON field names can change. There is a duplicated name for two tcindex/continue cases, though ids differ. Invalid input tests must ensure rejected actions do not leave stale prior state under reused indexes.

## Test Signals
Pass signals are accepted valid metadata/control combinations, rejected out-of-range or malformed metadata, correct boundary acceptance at max values, preserved cookies, correct delete behavior, and JSON evidence that replace operations update IFE encode metadata.
