# sources/cloud-native/ostree/tests/test-corruption.sh

Purpose: tests `ostree fsck` detection and cleanup behavior for corrupted or missing objects and path traversal dirtrees.

Important APIs/functions: `setup_test_repository bare`, `$OSTREE fsck -q`, `fsck --delete`, `fsck -a --delete`, object path helpers, manual chmod/truncation/deletion/corruption, and checkout of path traversal fixture.

Control flow: creates repos, damages object permissions and metadata, deletes commits, verifies path traversal fsck and checkout errors, removes or corrupts file objects, confirms commits are marked partial, and checks `--all` reports multiple corrupted files.

State/persistence: intentionally mutates `repo/objects`, `repo/state/*.commitpartial`, and extracted `ostree-path-traverse` fixture data. Dependencies include object layout helpers and tar fixture.

Integration/risk/test signals: protects repository integrity checks and partial-commit marking. Risks are exact error string matching and direct object layout coupling. TAP ok lines cover each corruption class.
