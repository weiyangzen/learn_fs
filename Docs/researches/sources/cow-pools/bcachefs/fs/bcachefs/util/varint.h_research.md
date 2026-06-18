# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/varint.h

## Summary
Declares bcachefs varint encode/decode APIs.

## Main Contents
- Checked encode/decode declarations.
- Fast encode/decode declarations.

## Risks
The header does not document the fast-path padding requirements; callers must know them from `varint.c`.
