# sources/cloud-native/ostree/man/ostree-checksum.xml

Purpose: documents `ostree checksum`, which computes an OSTree checksum for a file or directory.

Important APIs/types: required `PATH`; option `--ignore-xattrs`.

Control flow: traverses file/directory content and metadata to produce a checksum, optionally omitting extended attributes.

State and persistence: read-only over local filesystem input.

Dependencies and integration: tied to OSTree object checksum semantics and xattr handling.

Risks and test signals: risks include xattr-sensitive reproducibility and directory traversal ordering. Signals are checksum golden tests for files, dirs, and xattr inclusion/exclusion.
