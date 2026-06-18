# sources/distributed-fs/coda/coda-src/auth2/ctokens.c

## Purpose
Command-line token inspector that asks Venus/cache manager for Coda tokens and prints authentication status, Vice user id, and expiration time for a selected realm or all mounted realms.

## APIs, Types, and Functions
`GetTokens()` calls `U_GetLocalTokens()` into `ClearToken` and `EncryptedSecretToken`, checks `clear.EndTimestamp`, and formats `ctime()`. `main()` uses `SplitRealmFromName()`, `codaconf_init()`, `CODACONF_STR()`, `opendir()`, `readdir()`, and passwd/getlogin helpers.

## Control Flow, State, and Persistence
With an argument, it extracts a realm and queries only that realm. Without one, it reads the configured Coda mount point from `venus.conf`, enumerates non-dot entries below it, and treats each as a realm. It prints a header for the effective user, calls `GetTokens()` for each realm, and exits failure if the selected realm query failed. It does not persist data; state comes from Venus token storage.

## Dependencies and Integration
Depends on auth2 Venus APIs from `avenus.h`, Coda realm naming under the mount point, passwd APIs, and platform-specific Cygwin mount handling. It complements `clog` and `cunlog`.

## Risks and Test Signals
Risks include assuming realm names are direct mount entries, username may print as null if passwd lookup fails, expiration is checked only against local time, and multi-realm failures are ignored in the no-argument path. Test signals are `Not Authenticated` for `-ENOTCONN`, correct expiration formatting, and successful enumeration of configured mount roots.
