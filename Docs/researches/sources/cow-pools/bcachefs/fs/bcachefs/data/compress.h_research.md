# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/compress.h

Public compression API and compact compression-option encoding.

Key contents:
- `union bch_compression_opt` packs type and level into one byte using endian-aware bitfields.
- Validation rejects unknown types and nonzero level for `none`.
- Declares bio compression/decompression, compression feature initialization, option parse/to-text/validate helpers.
- Defines `bch2_opt_compression` as the option-function descriptor.

Dependencies and interactions:
- Maps user-facing compression options to on-disk compression types.
- Included by extent/write paths that need compression choice or encoded extent decoding.
