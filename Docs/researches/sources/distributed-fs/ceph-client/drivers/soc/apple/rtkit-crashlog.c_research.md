# sources/distributed-fs/ceph-client/drivers/soc/apple/rtkit-crashlog.c

## Purpose
This file parses and dumps Apple RTKit crashlog buffers after a coprocessor crash.

## Important APIs, Types, And Functions
It defines crashlog fourcc constants, packed/on-wire structs for headers, mailbox history, and register dumps, and a single exported-to-folder function `apple_rtkit_crashlog_dump()`. Helpers dump string, version, time, mailbox, and register sections.

## Control Flow
`apple_rtkit_crashlog_dump()` copies and validates the crashlog header, clamps parsing to the declared size, then walks sections. Each section dispatches by fourcc to a decoder. A repeated header marks end-of-log. Unknown sections are logged and skipped by their section size.

## State, Persistence, And Dependencies
The function is stateless and operates on a shadow buffer supplied by `rtkit.c`. It depends on RTKit internal state for device logging and on ARM64 PSR mode constants, with fallback defines for compile-test on other architectures.

## Integration Points
`apple_rtkit_crashlog_rx()` copies crashlog shared memory into normal memory and calls this decoder before notifying client `crashed` callbacks.

## Risks
Parsing trusts section headers enough to add `section_size` to `offset`; malformed zero or undersized section sizes could cause poor progress or reading beyond section payload intent. Most strings are printed directly from firmware-provided buffers, relying on crashlog format to include termination. It logs sensitive register/message history to the kernel log.

## Test Signals
Feed valid crashlogs with every section type, unknown sections, truncated headers, oversized declared size, too-small regs section, footer present/missing, and malformed section sizes under KUnit or targeted fixtures.
