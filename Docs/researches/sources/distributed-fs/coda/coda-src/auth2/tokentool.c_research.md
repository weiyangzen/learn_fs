# sources/distributed-fs/coda/coda-src/auth2/tokentool.c

## Purpose
Interactive utility for generating Coda token files manually from a ViceId, validity duration, shared secret, and output filename.

## APIs, Types, and Functions
Defines input helpers `read_int()`, `read_float()`, and `read_string()`. `main()` uses `rpc2_InitRandom()`, `getauth2key()`, `generate_CodaToken()`, and `WriteTokenToFile()` with `ClearToken`, `EncryptedSecretToken`, `RPC2_EncryptionKey`, and `AUTH2KEYSIZE`.

## Control Flow, State, and Persistence
The program prompts on stdin/stdout, validates only that numeric answers begin with a digit, truncates the shared secret into an RPC2 key, derives an auth2 key, strips the filename newline, generates a token valid for `duration * 3600`, and writes it. Persistence is the generated token file.

## Dependencies and Integration
Depends on RPC2 random initialization, Coda auth token generation, and tokenfile serialization. It is an offline/admin-oriented producer for tokens understood by Venus/auth2.

## Risks and Test Signals
Risks include weak input validation, `fflush(stdin)` undefined behavior, a likely bug using `sizeof(RPC2_KEYSIZE)` instead of `sizeof(token)` in `memset()`, secret truncation, heap strings retaining secrets until free, and no write-error checks. Test signals are generated token readability, expected expiration window, and successful use by token consumers.
