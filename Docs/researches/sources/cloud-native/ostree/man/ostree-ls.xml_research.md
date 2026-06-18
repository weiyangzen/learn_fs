# sources/cloud-native/ostree/man/ostree-ls.xml

Purpose: documents `ostree ls`, which lists file paths and metadata within a commit.

Important APIs/types: required `COMMIT`, optional `PATHS`; options `--dironly/-d`, `--recursive/-R`, `--checksum/-C`, `--xattrs/-X`, and `--nul-filenames-only`.

Control flow: resolves commit, walks requested paths, formats type/mode/uid/gid/size/path, optionally recursing, adding checksums/xattrs, or emitting NUL-separated filenames.

State and persistence: read-only over repository object data.

Dependencies and integration: integrates tree traversal, metadata decoding, xattrs, and script-friendly output.

Risks and test signals: risks include output format drift used by scripts, xattr decoding, and NUL mode behavior. Signals are golden output tests for file types, recursion, xattrs, and missing paths.
