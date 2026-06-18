# sources/distributed-fs/glusterfs/xlators/debug/trace/Makefile.am

## Purpose
Top-level Automake fragment for the `debug/trace` translator directory.

## Important APIs, types, and functions
`SUBDIRS = src` delegates build work to the trace implementation directory. `CLEANFILES =` is empty.

## Control flow
Recursive Automake descends into `src` to build the trace xlator.

## State and persistence behavior
No runtime state or persistence is defined in this file.

## Dependencies and integration points
Connects `xlators/debug/trace` into the recursive GlusterFS build. The implementation and private headers are defined by `src/Makefile.am`.

## Risks and test signals
Build risk is limited to directory inclusion. Test by confirming recursive builds enter `src` and produce `trace.la`.
