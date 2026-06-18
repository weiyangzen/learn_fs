# sources/distributed-fs/glusterfs/xlators/playground/template/Makefile.am

## Purpose
Top-level Automake file for the playground template translator.

## Important APIs, Types, And Functions
Declares `SUBDIRS = src`.

## Control Flow
Automake descends into `src` to build the template module.

## State And Persistence
No runtime state; build traversal only.

## Dependencies And Integration Points
Integrated by `xlators/playground/Makefile.am`.

## Risks
No `CLEANFILES` is declared here; not an issue unless future generated files are added.

## Test Signals
Recursive build from playground should enter `template/src`.
