# sources/cloud-native/ostree/man/ostree-show.xml

Purpose: documents `ostree show`, which prints metadata for commits or objects.

Important APIs/types: required `OBJECT`; options `--print-related`, `--print-variant-type=TYPE`, `--list-metadata-keys`, `--print-metadata-key=KEY`, `--list-detached-metadata-keys`, `--print-detached-metadata-key=KEY`, `--print-sizes`, `--raw`, and `--gpg-homedir`.

Control flow: resolves object or revision, decodes metadata/GVariant content, optionally lists or prints selected metadata keys, size metadata, detached metadata, related commits, or raw variant output.

State and persistence: read-only over objects, detached metadata, and keyrings.

Dependencies and integration: integrates commit metadata, detached metadata, `ostree commit --generate-sizes`, GPG verification display, and GVariant decoding.

Risks and test signals: risks include raw format stability, missing size metadata, and metadata key type assumptions. Signals are show output tests for commits, metadata keys, detached metadata, sizes, and raw variant files.
