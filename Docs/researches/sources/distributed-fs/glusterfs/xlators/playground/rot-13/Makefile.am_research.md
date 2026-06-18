# sources/distributed-fs/glusterfs/xlators/playground/rot-13/Makefile.am

## Purpose
Top-level Automake file for the sample `rot-13` translator.

## Important APIs, Types, And Functions
Declares `SUBDIRS = src` and empty `CLEANFILES`.

## Control Flow
If this directory is reached by the build, Automake descends into `src`.

## State And Persistence
No runtime state; build traversal only.

## Dependencies And Integration Points
Depends on parent build files choosing to include `rot-13`.

## Risks
This file is inert if no parent lists `rot-13` in `SUBDIRS`.

## Test Signals
Direct build from this directory should enter `src` and build `rot-13.la`.
