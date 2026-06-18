# sources/distributed-fs/ceph-client/tools/perf/util/addr2line.h

## Purpose

`addr2line.h` declares perf's source-line resolution entry point backed by external addr2line tools.

## Important APIs, Types, and Functions

It forward-declares `struct dso`, `struct inline_node`, and `struct symbol`, and declares `cmd__addr2line` with parameters for DSO path, address, output file/line, DSO cache, inline unwinding, inline output node, and symbol.

## Control Flow and State

No runtime behavior exists. The declaration exposes a function that can both return a direct file/line and populate inline frame state.

## Dependencies and Integration Points

It is used by srcline and annotation code that need file/line data.

## Risks and Test Signals

Risks are signature drift with callers and ownership expectations for returned strings. Build tests plus srcline/annotation resolution tests validate it.
