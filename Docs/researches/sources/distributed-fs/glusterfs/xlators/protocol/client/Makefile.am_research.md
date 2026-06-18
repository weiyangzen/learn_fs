# sources/distributed-fs/glusterfs/xlators/protocol/client/Makefile.am

## Purpose
Top-level Automake file for the protocol client translator.

## Important APIs, Types, And Functions
Declares `SUBDIRS = src`.

## Control Flow
Recursive build descends into `src`.

## State And Persistence
No runtime state; build traversal only.

## Dependencies And Integration Points
Integrated by `xlators/protocol/Makefile.am`.

## Risks
If omitted, the protocol client xlator is not built.

## Test Signals
Build should enter `protocol/client/src`.
