# sources/distributed-fs/glusterfs/xlators/protocol/auth/Makefile.am

## Purpose
Top-level Automake file for protocol authentication modules.

## Important APIs, Types, And Functions
Declares `SUBDIRS = addr login`.

## Control Flow
Build descends into address-based and login-based auth modules.

## State And Persistence
No runtime state; build traversal only.

## Dependencies And Integration Points
Integrated by `xlators/protocol/Makefile.am`.

## Risks
Omitting either subdir removes an authentication backend from the build.

## Test Signals
Recursive build should produce both `addr.la` and `login.la`.
