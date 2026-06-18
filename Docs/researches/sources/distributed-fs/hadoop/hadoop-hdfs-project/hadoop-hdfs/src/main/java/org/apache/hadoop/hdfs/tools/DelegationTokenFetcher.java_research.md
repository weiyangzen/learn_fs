# `sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/DelegationTokenFetcher.java`

## Purpose

`DelegationTokenFetcher` implements the legacy `fetchdt` utility for fetching, printing, renewing, or canceling HDFS delegation tokens stored in a local token file. It works with the default filesystem or an explicitly supplied WebHDFS/SWebHDFS URL.

## Important APIs, Types, and Functions

- `main(Configuration, String[])` builds Commons CLI options, parses generic Hadoop options, validates mode selection, resolves the local output token path, and runs the requested action as the current user.
- `getFileSystem` maps `http://` and `https://` webservice URLs to `webhdfs://` and `swebhdfs://` schemes for backward compatibility.
- `saveDelegationToken` calls `FileSystem.getDelegationToken`, writes a `Credentials` file in writable token-storage format, and logs debug details.
- `cancelTokens` and `renewTokens` iterate token storage and call `cancel` or `renew` only for managed tokens.
- `printTokensToString` decodes identifiers and prints a stable or verbose delegation-token identifier string.
- `printUsage` emits help and calls `ExitUtil.terminate(1)`.

## Control Flow

The CLI accepts at most one of `--cancel`, `--renew`, and `--print`; with none of those, it fetches a new token. It requires exactly one non-option token file name and resolves it against the local filesystem working directory. All actions run in a `UserGroupInformation.doAs` block. Fetch mode obtains the target filesystem from config or `--webservice`; other modes read the token file.

## State and Persistence Behavior

The durable artifact is the token storage file. Fetch mode writes or overwrites that file with a single fetched token. Renew and cancel mutate server-side token state for managed tokens. Print mode is read-only. No long-lived process state is kept.

## Dependencies and Integration Points

The class integrates with Hadoop `FileSystem` delegation-token APIs, `Credentials` token storage, HDFS delegation token identifiers for stable printing, WebHDFS constants, `GenericOptionsParser`, `UserGroupInformation`, and `ExitUtil`.

## Risks and Edge Cases

- Invalid usage often returns from `main(Configuration, ...)` after printing rather than terminating, except `printUsage` itself calls `ExitUtil.terminate(1)`.
- Fetch mode silently does not write a file if `getDelegationToken` returns null and only prints an error.
- `remaining[0].charAt(0)` assumes the remaining token filename is non-empty.
- `printTokensToString` calls `decodeIdentifier`; unknown token formats can throw.
- Renew/cancel only act on managed tokens, so a mixed token file may leave some tokens untouched without explicit user output.

## Test Signals

Tests should cover mutually exclusive mode validation, webservice URL scheme conversion, local token path resolution, token file serialization format, stable versus verbose token printing, managed/unmanaged renew/cancel behavior, and `ExitUtil` behavior under disabled system exit.
