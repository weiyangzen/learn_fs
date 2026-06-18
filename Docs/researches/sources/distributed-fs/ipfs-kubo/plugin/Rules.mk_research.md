<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/Rules.mk -->
# sources/distributed-fs/ipfs-kubo/plugin/Rules.mk

## Purpose

This Make fragment wires plugin subdirectories into the Kubo build.

## Important APIs, Types, and Functions

It includes `mk/header.mk`, sets `dir` to `$(d)/loader` and `$(d)/plugins`, includes each subdirectory `Rules.mk`, then includes `mk/footer.mk`.

## Control Flow, State, and Integration

The fragment participates in recursive Make directory tracking and delegates all concrete plugin build logic to loader and plugins rules.

## Dependencies, Risks, and Test Signals

Dependencies are the make header/footer convention and both child rules files. Build target discovery validates it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/Rules.mk -->
