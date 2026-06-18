# sources/cloud-native/ostree/src/ostree/ot-remote-builtin-gpg-import.c

Purpose: implements `ostree remote gpg-import`, importing GPG keys into a remote keyring from stdin or one or more keyring files.

Important APIs/functions: `open_source_stream()` returns a `GInputStream` from stdin or a chained stream of all `--keyring` files using `OstreeChainInputStream`. `ot_remote_builtin_gpg_import()` validates `NAME`, disallows `--stdin` with `--keyring`, passes optional key IDs, calls `ostree_repo_remote_gpg_import()`, and prints an imported count.

Control flow: parse repo options, validate remote name and mutually exclusive source options, create source stream, import selected or all keys, print result.

State/persistence: writes remote GPG keyring state in the repository. It does not persist source streams or local temp files.

Dependencies/integration: uses `gio/gunixinputstream.h`, libglnx, `ostree-chain-input-stream.h`, and libostree remote GPG import APIs.

Risks: with no `--stdin` and no keyrings, the chained stream is built from an empty array; library behavior determines whether that means no keys or an error. Stdin is not closed by the stream. Errors can occur late while reading chained keyrings.

Test signals: GPG import is typically covered by remote GPG tests. This subset includes `admin-test.sh` remote operations but not explicit GPG import checks.
