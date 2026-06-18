# sources/cloud-native/ostree/tests/test-composefs.sh

Purpose: tests composefs metadata generation and composefs checkout modes.

Important APIs/functions: `skip_without_ostree_feature composefs`, `setup_test_repository bare-user`, `commit --generate-composefs-metadata`, `show --print-metadata-key ostree.composefs.digest.v0`, `checkout --composefs`, `checkout --composefs-noverity`, `composefs-info dump`, and corrupted digest validation.

Control flow: commits a checkout with and without composefs metadata, verifies deterministic digest, performs verity and noverity composefs checkouts, validates image digests and dumped file metadata, then commits a deliberately bad digest and expects checkout to fail.

State/persistence: writes commits, composefs image files, and dump/error files. Dependencies include composefs support, composefs-info, and user xattrs.

Integration/risk/test signals: protects composefs metadata determinism and checkout integrity. Risks include hard-coded digest values and external tool output format. TAP cases cover metadata, checkout, noverity, and bad digest.
