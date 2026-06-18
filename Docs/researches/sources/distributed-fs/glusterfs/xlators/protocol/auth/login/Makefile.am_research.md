# sources/distributed-fs/glusterfs/xlators/protocol/auth/login/Makefile.am

## Purpose
Top-level Automake file for the login authentication module.

## Important APIs, Types, And Functions
Declares `SUBDIRS = src`.

## Control Flow
Build descends into `src`.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Integrated by `xlators/protocol/auth/Makefile.am`.

## Risks
If omitted, username/password and SSL-name auth module is not built.

## Test Signals
Recursive build should enter `auth/login/src`.
