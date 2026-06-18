# sources/cloud-native/ostree/tests/test-bsdiff.c

Purpose: verifies bundled bsdiff/bspatch integration can create and apply a binary patch.

Important APIs/functions: `bsdiff`, `bspatch`, custom `bzdiff_write()` appending to `GMemoryOutputStream`, `bzpatch_read()` reading from `GMemoryInputStream`, and GLib byte stream helpers.

Control flow: defines old/new byte arrays, runs `bsdiff` into an in-memory stream, closes it, feeds the patch through `bspatch`, and asserts generated output byte-for-byte matches the target.

State/persistence: all state is in memory; no repository or filesystem writes. Dependencies include GLib and the bsdiff implementation headers.

Integration/risk/test signals: protects static delta binary diff primitives. Risks are narrow fixed fixture size and lack of error-path coverage. A single GLib `/bsdiff` test reports success.
