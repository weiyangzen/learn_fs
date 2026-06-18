# sources/distributed-fs/coda/coda-src/auth2/tokenfile.h

## Purpose
Header for token-file serialization helpers.

## APIs, Types, and Functions
Includes `auth2.h` and declares `WriteTokenToFile(char *filename, ClearToken *cToken, EncryptedSecretToken sToken)` and `ReadTokenFromFile(char *filename, ClearToken *cToken, EncryptedSecretToken sToken)`.

## Control Flow, State, and Persistence
No runtime behavior. The declared functions persist token pairs in a base64 file and read them back.

## Dependencies and Integration
Used by `tokentool.c` and implemented by `tokenfile.c`; requires auth2 token structures.

## Risks and Test Signals
Risks are signature-level: mutable `char *` filenames and array-like token parameters do not express constness or sizes. Test signals are successful compilation and tokenfile round trips.
