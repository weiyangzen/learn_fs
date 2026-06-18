# File Research: sources/cow-pools/bcachefs-tools/debian/gbp.conf

- Git-buildpackage configuration.
- Disables pristine-tar, uses upstream tags `v%(version)s`, ignores branch, exports to a sibling directory, runs `cargo vendor-filterer --versioned-dirs` after export, and uses xz level 9 compression.
