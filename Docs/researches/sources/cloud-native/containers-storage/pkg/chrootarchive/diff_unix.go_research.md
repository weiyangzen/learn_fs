<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/diff_unix.go -->
# sources/cloud-native/containers-storage/pkg/chrootarchive/diff_unix.go

Purpose: Unix non-Windows/non-Darwin reexec implementation for applying layer diffs inside a chroot.

Important APIs/types/functions: `applyLayerResponse`, child entrypoint `applyLayer`, and parent `applyLayerHandler`.

Control flow: parent cleans dest, optionally decompresses, defaults options/rootless `InUserNS`, marshals options into `OPT` env, starts `storage-applyLayer` with dest as root/chroot target, streams layer on stdin, and decodes JSON response containing layer size. Child locks OS thread, detects rootless state, chroots, sets umask zero, unmarshals `OPT`, creates a temporary extraction dir under `/`, sets `TMPDIR`, calls `archive.UnpackLayer("/", os.Stdin, options)`, removes temp dir, JSON-encodes size, flushes stdin, and exits.

State/persistence: mutates the chrooted destination root, creates/removes a temp directory inside it, and uses process environment for options IPC.

Dependencies/integration: uses `reexec`, `archive.DecompressStream`, `archive.UnpackLayer`, `system.Umask`, `unshare`, and `jsoniter`.

Risks: options are passed through environment, unlike untar options; very large option sets could hit env limits here. Error output is captured and included. Chroot/pivot correctness is inherited from platform `chroot`.

Test signals: `archive_test.go` covers chroot apply of slow empty tar and safe `..` filename, while archive diff tests cover lower-level layer semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/diff_unix.go -->
