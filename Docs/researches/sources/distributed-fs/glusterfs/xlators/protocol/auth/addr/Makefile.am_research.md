# sources/distributed-fs/glusterfs/xlators/protocol/auth/addr/Makefile.am

## Purpose
Top-level Automake file for the address-based auth module.

## Important APIs, Types, And Functions
Declares `SUBDIRS = src`.

## Control Flow
Automake descends into `src` to build the module.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Integrated by the protocol auth build.

## Risks
If not traversed, address auth options would be documented but no module would be available.

## Test Signals
Build should enter `auth/addr/src`.
