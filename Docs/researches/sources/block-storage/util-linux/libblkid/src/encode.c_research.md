# File Research: sources/block-storage/util-linux/libblkid/src/encode.c

## Purpose
Provides public string-encoding helpers for safe udev-compatible label and UUID path components.

## Main Components
- UTF-8 helpers validate encoded character length, decode codepoints, reject invalid ranges, and prevent overlong encodings.
- `is_whitelisted()` permits ASCII alphanumerics and selected punctuation.
- `blkid_encode_string()` copies valid UTF-8 sequences, preserves safe ASCII, and encodes unsafe bytes as `\xNN`.
- `blkid_safe_string()` normalizes whitespace, permits printable ASCII/valid UTF-8/hex escapes, replaces whitespace and invalid bytes with `_`, and guarantees NUL termination.

## Dependencies and Interactions
Used by evaluation code when constructing `/dev/disk/by-*` symlink paths. It also uses util-linux whitespace normalization from `strutils.h`.

## Research Notes
`blkid_encode_string()` requires enough output space for expansion and returns `-1` on truncation. `blkid_safe_string()` is lossy by design and replaces unsafe data rather than hex-encoding it.
