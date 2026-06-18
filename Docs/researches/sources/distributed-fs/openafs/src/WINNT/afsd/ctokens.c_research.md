# sources/distributed-fs/openafs/src/WINNT/afsd/ctokens.c

## Purpose

`ctokens.c` is a small Windows command-line utility that lists Kerberos/AFS tokens currently held by the cache manager. It is equivalent in role to a `tokens` command: enumerate token services and print client identity, service principal, and expiration status.

## Important APIs, Types, and Functions

The program's single `main()` initializes Winsock, validates that only optional help-style usage is requested, loops with `ktc_ListTokens()`, fetches each token with `ktc_GetToken()`, and formats `ktc_principal` and `ktc_token` data. It handles `KTC_NOENT` as end-of-list, `KTC_NOCM` as cache-manager-not-started, and any other nonzero code as unexpected.

## Control Flow

After printing a heading, the program starts at token index zero. `ktc_ListTokens()` returns the next service principal and updates the cursor. For each service, `ktc_GetToken()` retrieves the token and client principal. The display name is built from client name and optional instance, with special formatting for empty users, `AFS ID...`, and `Unix UID...`. Expired tokens are detected by comparing `token.endTime` with `time(NULL)`; unexpired tokens use `ctime()` with day/seconds/year trimmed.

## State and Persistence Behavior

The program is read-only. It does not store tokens, mutate cache-manager state, or persist configuration. All state is stack-local except for the cache manager token state accessed through the `ktc_*` API.

## Dependencies and Integration Points

It depends on Windows Winsock initialization, OpenAFS auth/ktc libraries, roken/stds compatibility headers, and the running AFS cache manager. It integrates with users and scripts as a diagnostic CLI.

## Risks and Edge Cases

String assembly uses fixed 100-byte `userName` with `strcpy()`/`strcat()`, so unexpectedly long principal pieces would be unsafe. `ctime()` returns a shared static buffer and the code mutates it in place, which is fine for this single-threaded utility but brittle. Command-line handling prints usage for any extra argument rather than interpreting `-help` specifically. Errors fetching one token are reported and enumeration continues.

## Test Signals

Tests should cover no cache manager, no tokens, one valid token, one expired token, token with instance, anonymous/empty display, `AFS ID` and `Unix UID` formatting, `ktc_GetToken()` failure for a listed service, and long principal/cell names if hardened.
