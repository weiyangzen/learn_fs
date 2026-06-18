# sources/distributed-fs/openafs/src/WINNT/afsclass/c_identlist.h

## Purpose

`c_identlist.h` declares `IDENTLIST`, a lightweight unique set of `LPIDENT` handles.

## Important APIs, Types, and Functions

The class exposes add/remove/remove-all, copy, count, membership check, and `HENUM`-style iteration. Its only private member is `LPHASHLIST m_lIdents`.

## Control Flow

There is no executable flow in the header; it establishes the container API used by client code and possibly selection/filter workflows.

## State and Persistence Behavior

The list stores borrowed identity pointers in memory. It owns no persistent data and no backing AFS objects.

## Dependencies and Integration Points

The header depends on `afsclass.h`, `LPIDENT`, `LPIDENTLIST`, `HENUM`, and `HASHLIST` from internal infrastructure.

## Risks and Edge Cases

The ownership contract is implicit: adding an identifier does not retain it. Callers must ensure identifiers remain valid and close enumeration handles.

## Test Signals

Compile checks plus simple unit tests for uniqueness, copy semantics, count, and enumeration close behavior are sufficient.
