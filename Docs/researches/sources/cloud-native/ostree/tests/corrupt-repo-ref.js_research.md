<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/corrupt-repo-ref.js -->
## sources/cloud-native/ostree/tests/corrupt-repo-ref.js

Purpose: GJS helper that corrupts random objects referenced by an OSTree ref to test fsck/pull corruption detection.

Important APIs/functions: uses GI `OSTree.Repo`, `Gio.File`, and `GLib`. `listObjectChecksumsRecurse()` resolves repo files recursively, recording dirtree, dirmeta, and filez objects. The main path reads a commit, chooses a random referenced object, opens the loose object read-write, changes 10 random bytes, and writes `corrupted-status.txt`.

Control flow/state: mutates repository object contents in place and persists a status log in the current directory. It randomly chooses both object and byte offsets.

Dependencies/integration: requires GJS with OSTree GI bindings and a loose-object repo. It is intended for tests that expect subsequent verification to fail.

Risks/test signals: randomness may hit small objects or offsets near bounds; `random_int_range(0, size)` must avoid invalid EOF reads. Signal is printed corruption detail plus downstream corruption errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/corrupt-repo-ref.js -->
