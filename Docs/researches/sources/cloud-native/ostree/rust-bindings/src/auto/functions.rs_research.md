# sources/cloud-native/ostree/rust-bindings/src/auto/functions.rs

Purpose: Generated free-function bindings for libostree utility APIs that are not methods on a generated object.

Important APIs: Functions cover hardlink breaking, version checks, checksum variant conversion, commit metadata queries, bootable metadata generation, content file/stream parsing, directory metadata creation, directory diffing/printing, xattr reads, GPG error quark, metadata variant type lookup, object name serialization/deserialization, refspec parsing, archive/content stream conversion, and validation of checksums, collection IDs, remote names, revs, commits, dirmeta, dirtree, file modes, and object types.

Control flow and state: Most functions are synchronous FFI calls using GLib error pointers converted to `Result`. Some return owned strings, variants, streams, file info, xattrs, vectors, or tuple out-parameters. `break_hardlink` and xattr/content parse functions touch filesystem state; validation and serialization functions are pure.

Dependencies and integration points: Depends on Gio files/streams/file info/cancellables, GLib variants and errors, generated `DiffFlags`, `DiffItem`, `ObjectType`, and feature-gated `CommitSizesEntry`. These utilities underpin repository object parsing, validation, and filesystem conversion.

Risks: Array parameters for `diff_dirs` are subtle because C APIs may expect mutable output arrays while the generated signature accepts slices; this should be verified. Trust booleans in content parsing are security-sensitive. Out-parameter handling uses `MaybeUninit` and assumes C fills values on success.

Test signals: Unit/integration tests should cover validation failures, checksum/object round trips, refspec parse cases, content parse trusted/untrusted behavior, xattr reads, diff generation, and feature-gated commit size extraction.
