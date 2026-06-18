<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/mk/header.mk -->
# sources/distributed-fs/ipfs-kubo/mk/header.mk

## Purpose

This makefile fragment saves recursive make directory context before entering an included subdirectory rules file.

## Important APIs, Types, and Functions

It computes `p := $(sp).x`, stores `dirstack_$(sp) := $(d)`, and sets `d := $(dir)`.

## Control Flow, State, and Integration

Included at the beginning of make fragments, it pushes directory state that `footer.mk` later restores.

## Dependencies, Risks, and Test Signals

Dependency is GNU Make. Risks include incorrect `sp` or `dir` values causing targets to be generated under the wrong path. Any recursive build using `Rules.mk` validates this convention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/mk/header.mk -->
