# sources/distributed-fs/glusterfs/xlators/protocol/Makefile.am

## Purpose
Top-level Automake file for protocol translators and authentication modules.

## Important APIs, Types, And Functions
Declares `SUBDIRS = auth client server`.

## Control Flow
Recursive builds descend into auth modules, protocol client, and protocol server directories.

## State And Persistence
No runtime state; build traversal only.

## Dependencies And Integration Points
Connects protocol components into the broader xlator build.

## Risks
Removing a subdir here excludes a core protocol component from builds.

## Test Signals
Parent build should visit auth, client, and server.
