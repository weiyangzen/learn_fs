# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/Makefile

## Purpose
This Makefile descends into the Chips&Media Coda and Wave5 codec driver subdirectories.

## Important APIs, Types, and Functions
The rules are `obj-y += coda/` and `obj-y += wave5/`.

## Control Flow
Kbuild always enters both subdirectories when this directory is visited; the child Makefiles then conditionally build objects according to their Kconfig symbols.

## State and Persistence
There is no runtime state. Build composition is controlled by child Makefiles and selected configuration.

## Dependencies and Integration Points
It must stay aligned with child directories and the corresponding sourced Kconfig files.

## Risks and Edge Cases
Removing a subdirectory entry would prevent enabled child symbols from building. Stale directory names break Kbuild traversal.

## Test Signals
Use allmodconfig and targeted `VIDEO_CODA`/Wave5 builds to confirm child objects are reached.
