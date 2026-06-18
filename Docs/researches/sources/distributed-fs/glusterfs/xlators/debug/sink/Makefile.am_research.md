# sources/distributed-fs/glusterfs/xlators/debug/sink/Makefile.am

## Purpose
Top-level Automake fragment for the `debug/sink` translator directory.

## Important APIs, types, and functions
`SUBDIRS = src` delegates build work to the implementation directory.

## Control flow
Recursive Automake enters `src` to build and install the sink translator.

## State and persistence behavior
No runtime state or persistence is defined here.

## Dependencies and integration points
Connects `xlators/debug/sink` to the broader GlusterFS build. Module-specific details are in `src/Makefile.am`.

## Risks and test signals
Build risk is limited to ensuring `src` participates in recursive builds. Test by running the automake build and confirming `sink.la` is produced.
