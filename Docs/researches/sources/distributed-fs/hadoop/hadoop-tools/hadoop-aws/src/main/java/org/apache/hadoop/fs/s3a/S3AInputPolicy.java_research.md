# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3AInputPolicy.java

## Purpose

`S3AInputPolicy` is the internal enum that reduces Hadoop open-file read-policy strings into the three S3A read strategies used by S3A input streams: normal/adaptive, random, and sequential. It gives S3A a compact policy object while accepting a broader set of public option names for file formats and access patterns.

## Important APIs, Types, and Functions

The enum values are `Normal`, `Random`, and `Sequential`. Each stores the external policy string, whether the policy should be treated as random IO, and whether it is adaptive. `toString`, `getPolicy`, `isRandomIO`, and `isAdaptive` expose those fields inside the package. Static `getPolicy(String, S3AInputPolicy)` parses a single policy name with a fallback. Static `getFirstSupportedPolicy(Collection<String>, S3AInputPolicy)` scans ordered candidate names and returns the first recognized policy.

## Control Flow

`getPolicy` trims and lowercases its input using `Locale.ENGLISH`, then switches over Hadoop open-file read-policy constants and the older S3A `INPUT_FADV_NORMAL` name. Adaptive/default/normal map to `Normal`. HBase, random, vector, columnar, ORC, and Parquet names map to `Random`. Avro, CSV, JSON, sequential, and whole-file names map to `Sequential`. Unknown names return the supplied default, which may be null. `getFirstSupportedPolicy` simply calls `getPolicy` with a null default for each candidate and returns the first non-null result, otherwise the fallback.

## State and Persistence Behavior

The enum is immutable process-local state. It does not persist anything and has no external side effects. The `policy` strings come from Hadoop option constants and are used for display and option propagation.

## Dependencies and Integration Points

It depends on `Options.OpenFileOptions` read-policy constants, `Constants.INPUT_FADV_NORMAL`, Java collections/locales, and `@Nullable`. `S3AFileSystem.initialize` uses it to parse `fs.s3a.experimental.input.fadvise`/default read policy. `OpenFileSupport` and read contexts propagate selected policies into S3A input streams. `S3AInputStream` checks `isAdaptive` and policy value to decide when to switch from normal sequential-like range requests to random range requests.

## Risks and Edge Cases

`getPolicy` assumes `name` is non-null; callers must supply a real string. Unknown mandatory open options need validation elsewhere because this enum silently returns the fallback. Many format-specific names currently collapse to either random or sequential, so adding a new format-specific strategy later could change performance behavior. `Normal` is adaptive and initially treated like sequential by the stream, switching to random after backward seek or unbuffer; this distinction is important when interpreting `isRandomIO`.

## Test Signals

Tests should cover every public read-policy constant, case and whitespace normalization, fallback behavior for unknown names, null fallback returning null, first-supported selection order, and the adaptive/random/sequential boolean flags. Integration tests should verify that filesystem defaults and open-file options choose the expected stream request-limit behavior.
