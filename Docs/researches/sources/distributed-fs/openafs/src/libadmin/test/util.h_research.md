# sources/distributed-fs/openafs/src/libadmin/test/util.h

## Purpose

`util.h` declares the utility command handlers and setup function for the `afscp` libadmin test client.

## Important APIs, Types, and Functions

The header includes OpenAFS admin/util headers, command parsing, RX headers, socket/IP headers for non-Windows builds, pthreads, and `common.h`. It declares `DoUtilErrorTranslate`, `DoUtilDatabaseServerList`, `DoUtilNameToAddress`, and `SetupUtilAdminCmd`.

## Control Flow

There is no executable control flow. The declarations allow the test-client command registration code and individual command implementations to share signatures.

## State and Persistence Behavior

No state is stored here. Utility command state is transient and read-only.

## Dependencies and Integration Points

This header is part of the shared test-client build. Its comment says "bos" functions, but the declarations are util functions; that mismatch is documentation drift rather than functional behavior.

## Risks and Test Signals

The header mixes networking headers with OpenAFS admin headers, so portability tests should compile it on Windows and Unix configurations. Command registration tests catch signature mismatches for exported handler declarations.
