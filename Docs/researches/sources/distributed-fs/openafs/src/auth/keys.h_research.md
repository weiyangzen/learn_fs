# sources/distributed-fs/openafs/src/auth/keys.h

## Purpose
Declares the legacy server key file structures and limits for OpenAFS rxkad keys.

## Important APIs, Types, and Functions
Defines `AFSCONF_MAXKEYS` as 8, `struct afsconf_key` with a key version number and 8-byte key, `struct afsconf_keys` as a counted fixed array, and `AFSCONF_KEYINUSE` as a local duplicate-key error code.

## Control Flow
There is no executable control flow. The header is consumed by key management code and compatibility callers that retrieve or manage old-style rxkad keys.

## State and Persistence
The structs mirror the legacy `/usr/afs/etc/ServerKeys`/`KeyFile` model: a count followed by kvno/key pairs in network byte order on disk, represented in host memory by the structures here.

## Dependencies and Integration Points
Included by auth key code, `setkey`, and bozo build dependencies. It bridges legacy fixed-size rxkad APIs with the newer typed-key implementation in `keys.c`.

## Risks and Test Signals
The fixed 8-key and 8-byte-key model is intentionally narrow. Code using this header must not assume it can represent rxgk or multiple subtypes. Tests should verify callers handle `AFSCONF_FULL`, `AFSCONF_KEYINUSE`, and conversion from typed-key APIs without overrunning the fixed array.
