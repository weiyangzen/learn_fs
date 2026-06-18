<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/mk/footer.mk -->
# sources/distributed-fs/ipfs-kubo/mk/footer.mk

## Purpose

This makefile fragment restores directory-tracking variables for Kubo's recursive make include pattern.

## Important APIs, Types, and Functions

It sets `d := $(dirstack_$(sp))` and `sp := $(basename $(sp))`.

## Control Flow, State, and Integration

Included at the end of nested make fragments, it unwinds the `d` and `sp` state established by `header.mk`.

## Dependencies, Risks, and Test Signals

Dependency is GNU Make variable expansion. Risks are include-order errors and corrupted directory context for subsequent fragments. Build targets depending on nested `Rules.mk` files validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/mk/footer.mk -->
