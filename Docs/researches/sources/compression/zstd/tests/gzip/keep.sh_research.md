<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/gzip/keep.sh -->
## sources/compression/zstd/tests/gzip/keep.sh

Purpose: Tests gzip `--keep` behavior for both compression and decompression, plus verbose logging for kept inputs.

Important APIs and functions: Sources `init.sh`; uses `gzip`, `compare`, shell `eval` for source-existence assertions, and `Exit`.

Control flow: It creates `in` and `orig`, then loops over `--keep` and default behavior. For compression, `--keep` must retain `in` while default compression must remove it; for decompression, `--keep` must retain `in.gz` while default decompression must remove it. It then checks that `gzip -kv in` logs creation of `in.gz`.

State and persistence: Creates and removes `in`, `orig`, and `in.gz` within the temp directory. `orig` persists until cleanup as the comparison source.

Dependencies and integration points: Exercises zstd's gzip-compatible source removal/retention and verbose messages when invoked as `gzip`.

Risks: Uses `eval` to apply `&&`/`||` logic stored in `op`; safe here because values are hardcoded. Exact verbose substring `created in.gz` can be sensitive to message changes.

Test signals: File existence must match keep/default semantics and decompressed `in` must match `orig`.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/gzip/keep.sh -->
