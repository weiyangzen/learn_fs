# sources/distributed-fs/openafs/src/bozo/bnode.p.h

## Purpose
Small public-template header for generated BOS bnode header content and platform-specific bosserver exit conventions.

## Important APIs, Types, and Functions
Defines `NONOTIFIER` sentinel string, Windows restart exit base `BOSEXIT_RESTART`, `BOSEXIT_DORESTART(code)` macro, and `FSSDTIME` fileserver shutdown wait limit.

## Control Flow
No executable flow. Macros are consumed by bnode creation/control code and Windows service management integration.

## State and Persistence
No state. Values influence runtime configuration semantics: notifier omission and shutdown/restart timing.

## Dependencies and Integration Points
Used by generated `bnode.h` and by BOS code that interprets notifier configuration and service restart exit codes.

## Risks and Test Signals
`NONOTIFIER` is a string protocol value, so config writers/readers must preserve exact spelling. Windows restart code matching masks low bits. Tests should verify notifier-disabled configs round-trip and Windows restart exits are classified as intended.
