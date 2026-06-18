# sources/cloud-native/overlayfs-tools/path.c

Purpose: implements path joining and base-relative path extraction helpers for overlayfs-tools.

Important APIs/types/functions: `joinname` and `basename2`.

Control flow: `joinname` normalizes leading `./`, handles empty/dot inputs, removes duplicate boundary slashes, allocates a new combined string, and returns `"."` for empty results. `basename2` strips a base directory prefix without modifying inputs and returns `"."` when path equals base.

State and persistence: `joinname` allocates memory that callers must free; `basename2` returns a pointer into the input path or a static dot string.

Dependencies/integration: used heavily by fsck lookup/redirect code and scan context initialization.

Risks: does not resolve `..`, middle duplicate slashes, or NULL input. `basename2` prefix matching is lexical, so callers must supply normalized paths.

Test signals: unit tests for root, dot, slash, mismatched prefix, exact prefix, and redirect path combinations.
