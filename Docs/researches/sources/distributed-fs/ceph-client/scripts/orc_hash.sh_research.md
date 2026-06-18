<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/orc_hash.sh -->
# sources/distributed-fs/ceph-client/scripts/orc_hash.sh

## Purpose

`orc_hash.sh` computes a preprocessor byte list hash from ORC unwind ABI definitions. It is intended to hash the parts of headers that define `ORC_REG_*`, `ORC_TYPE_*`, and `struct orc_entry`.

## Important APIs, Types, and Functions

The script is a stdin-to-stdout shell pipeline. It prints `#define ORC_HASH `, extracts matching lines with awk, hashes them with `sha1sum`, and formats each digest byte as `0xNN,`.

## Control Flow

It streams input through awk. The awk program prints ORC register/type defines and the complete `struct orc_entry` block, then the shell pipeline hashes and byte-formats that text.

## State and Persistence Behavior

It does not write persistent state; callers include or compare the emitted define text.

## Dependencies and Integration Points

It depends on shell, awk, `sha1sum`, `cut`, and `sed`. It integrates with ORC unwind format change detection in kernel builds.

## Risks and Edge Cases

Hash stability depends on the input being the expected header/preprocessor text. Renaming defines, changing struct formatting, or using a platform without compatible `sha1sum`/sed behavior can change or break output.

## Test Signals

Hash unchanged ORC header text, then change an ORC register define, type define, and `struct orc_entry` field to confirm digest changes. Verify non-ORC input changes are ignored.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/orc_hash.sh -->
