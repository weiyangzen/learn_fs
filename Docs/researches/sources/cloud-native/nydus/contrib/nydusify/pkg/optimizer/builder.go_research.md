# sources/cloud-native/nydus/contrib/nydusify/pkg/optimizer/builder.go

Purpose: wraps the external `nydus-image optimize` command used to build an optimized bootstrap and prefetch blob.

Important APIs/types/functions: package logger, `isSignalKilled`, `BuildOption`, `outputJSON`, and `Build`.

Control flow: `Build` constructs optimize arguments from prefetch file, bootstrap, output blob dir, output bootstrap, and output JSON paths. For `localfs` it passes `--blob-dir`; otherwise it passes backend type/config. It optionally runs under a timeout context, streams stdout/stderr to logrus, reads the output JSON, unmarshals blob IDs, and returns the last blob ID as the prefetch blob.

State and persistence: outputs are written by the external command into configured blob/bootstrap/output JSON paths. No internal persistence exists beyond reading `OutputJSONPath`.

Dependencies and integration points: `os/exec`, context timeouts, logrus, JSON output contract from `nydus-image`, and optimizer `Optimize`.

Risks and test signals: if `output.Blobs` is missing or empty, indexing the last element panics. Timeout detection is string-based on `"signal: killed"`. Backend config is passed on command line, which can expose secrets in process listings/logs.
