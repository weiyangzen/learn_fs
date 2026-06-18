# sources/distributed-fs/openafs/src/libadmin/test/util.c

## Purpose

`util.c` implements utility commands for the `afscp` libadmin test client. These commands expose error-code translation, database server discovery, and hostname-to-address conversion from `afs_utilAdmin`.

## Important APIs, Types, and Functions

`DoUtilErrorTranslate` calls `util_AdminErrorCodeTranslate` and prints the numeric code and text. `DoUtilDatabaseServerList` uses `util_DatabaseServerGetBegin`, `util_DatabaseServerGetNext`, and `util_DatabaseServerGetDone` to enumerate database servers for a named cell. `DoUtilNameToAddress` calls `util_AdminServerAddressGetFromName` and prints the IPv4 address. `SetupUtilAdminCmd` registers these three commands.

## Control Flow

The control flow is linear. The database-server list command follows the standard libadmin iterator pattern and treats `ADMITERATORDONE` as normal completion. Address output converts host-order integer addresses to network order before passing them to `inet_ntoa`.

## State and Persistence Behavior

These commands are read-only. They do not mutate local files or OpenAFS databases. The only state is transient iterator state allocated by the util admin library.

## Dependencies and Integration Points

The file includes `util.h`, which provides OpenAFS util admin declarations, socket address headers on Unix, and test-harness helpers. Only `UtilDatabaseServerList` adds common cell/auth arguments; error translation and name lookup intentionally omit common arguments because they do not need a cell handle.

## Risks and Edge Cases

`DoUtilErrorTranslate` parses errors with `atoi`, so malformed input silently becomes zero. `DoUtilDatabaseServerList` assumes the iterator is cleaned up only on successful begin; if a later next call fails, it reports through the fatal macro before explicitly reaching done. `inet_ntoa` returns static storage, which is fine for immediate printing but not reusable.

## Test Signals

Useful checks include translating known admin errors, resolving a valid server name, rejecting an invalid server name with the expected status, and listing database servers for a test cell while confirming iterator completion and address formatting.
