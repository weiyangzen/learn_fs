<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/stack/compress.go -->
# sources/cloud-native/buildkit/util/stack/compress.go

Purpose: reduces redundant stack traces by removing duplicate or shared suffix frames.

Important APIs and types: `compressStacks`, `subFrames`, and `Frame.Equal`.

Control flow: stack traces are sorted longest-first. Each later stack is compared against already-kept stacks from the bottom frame upward. Full duplicate stacks from the same pid/version/cmdline are skipped. Partial shared suffixes are trimmed before appending.

State and persistence: mutates `Frames` slices of stack objects passed in; no external state.

Dependencies and integration: used by `Traces` in `stack.go` before formatting or serializing stack traces.

Risks: input order is not preserved because stacks are sorted by frame length. Partial trimming mutates the original stack object, which may surprise callers holding references.

Test signals: `compress_test.go` validates full duplicate removal and partial suffix trimming.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/stack/compress.go -->
