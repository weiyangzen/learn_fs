# sources/distributed-fs/glusterfs/xlators/playground/Makefile.am

## Purpose
Top-level Automake file for playground translators.

## Important APIs, Types, And Functions
Declares `SUBDIRS = template` and empty `CLEANFILES`.

## Control Flow
The build descends only into `template` from this directory.

## State And Persistence
No runtime state; build traversal only.

## Dependencies And Integration Points
Integrated by the broader xlator build. The sibling `rot-13` directory has its own Makefile but is not listed here.

## Risks
Because `rot-13` is omitted from `SUBDIRS`, a normal recursive build from `playground` will not build that sample unless another parent includes it separately.

## Test Signals
Automake traversal should build `template` only from this level; verify whether that exclusion is intended for `rot-13`.
