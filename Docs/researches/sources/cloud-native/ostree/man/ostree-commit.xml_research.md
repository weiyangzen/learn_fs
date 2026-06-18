# sources/cloud-native/ostree/man/ostree-commit.xml

Purpose: documents `ostree commit`, which creates a new repository commit from a directory, tar, existing ref, or derived base.

Important APIs/types: required `--branch` unless `--orphan`; major options include subject/body/editor, parent/tree/base, metadata and detached metadata, owner uid/gid, xattr policy, SELinux labeling epoch, bootable metadata, hardlink speedups, tar parent creation, skip-if-unchanged, consume, statoverride, skip-list, table output, size metadata, GPG/signature options, timestamp, orphan, fsync policy, `--sign-type`, `--sign-from-file`, and deprecated/risky `--sign`.

Control flow: builds a commit message, determines parent/ref behavior, overlays input trees, applies metadata/modifiers/ownership/SELinux/statoverride/skip lists, writes objects and commit metadata, optionally signs, updates the branch unless orphaned, and prints checksum or table output.

State and persistence: writes repository objects, refs, commit metadata, detached metadata, signatures, and possibly consumes/deletes or renames source content.

Dependencies and integration: central repository write path; integrates GVariant metadata parsing, GPGME, ed25519/spki/dummy signature engines, SELinux, tar import, xattrs, fsync, and size generation used by `ostree show`.

Risks and test signals: high-risk options include private keys on command line, `--consume`, parent/ref defaults, metadata parsing, fsync disabling, and SELinux labeling. Signals are commit/checkout round trips, ref updates, signing verification, tar import tests, skip-if-unchanged behavior, and generated size metadata shown by `ostree show`.
