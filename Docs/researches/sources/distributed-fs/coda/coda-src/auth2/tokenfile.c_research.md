# sources/distributed-fs/coda/coda-src/auth2/tokenfile.c

## Purpose
Serialization helper for Coda token files. It writes and reads a `ClearToken` plus `EncryptedSecretToken` as base64 with network-byte-order fields.

## APIs, Types, and Functions
Exports `WriteTokenToFile()` and `ReadTokenFromFile()`. Internal `export()` converts `ClearToken` integer fields with `htonl()`, and `import()` converts them back with `ntohl()`. Uses `coda_base64_encode()` and `coda_base64_decode()`.

## Control Flow, State, and Persistence
Writing allocates a combined binary buffer, temporarily converts the caller's clear token to network order, copies clear and secret tokens, restores host order, sets `umask(0177)`, writes a `*** Coda Token ***` marker and base64 payload, then frees the buffer. Reading opens the file, skips the first line, decodes base64, validates the exact combined size, copies data into caller buffers, converts the clear token to host order, and exits on failure. Token files are the persistent artifact.

## Dependencies and Integration
Used by `tokentool.c` and any offline token import/export path. Depends on auth2 token types and base64 utilities.

## Risks and Test Signals
Risks include no `malloc()`/`fopen()` checks on write, process-global `umask()` side effects, fatal `exit()` inside a library helper, and mutating the caller's token during serialization. Test signals are round-trip byte equality, mode restricted by umask, corrupt-size detection, and endian-stable files across hosts.
