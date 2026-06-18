# sources/distributed-fs/coda/coda-src/auth2/pwsupport.h

## Purpose
Public declarations for the auth2 password support implementation used by auth server code and related administration paths.

## APIs, Types, and Functions
Declares global `RPC2_EncryptionKey FileKey`, `char *PWFile`, and functions `InitPW()`, `PWGetKeys()`, `PWChangePasswd()`, `PWNewUser()`, `PWDeleteUser()`, and `PWChangeUser()`. Interfaces use RPC2 handles, counted byte strings, ViceIds, encryption keys, and RPC strings.

## Control Flow, State, and Persistence
No runtime control flow in the header. It exposes the persistent password-file lifecycle through `InitPW()` and append-based mutation functions.

## Dependencies and Integration
Requires auth2/RPC2 type definitions to be visible before inclusion. It binds auth RPC handlers to the password-file backend in `pwsupport.c`.

## Risks and Test Signals
Risks include exposing mutable globals and omitting prototypes for some non-static helpers used elsewhere. Test signals are compile-time linkage against auth2 handlers and matching signatures with RPC stubs.
