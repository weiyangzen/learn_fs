# File Research: sources/cow-pools/bcachefs-tools/fs/sb/errors.h

This header declares superblock/fsck error accounting APIs.

Key responsibilities:
- Includes runtime error types.
- Exposes `bch2_sb_error_strs[]`.
- Declares:
  - `bch2_sb_error_id_to_text()`
  - `bch2_fs_errors_to_text()`
  - `bch2_sb_error_count()`
  - `bch2_sb_errors_from_cpu()`
  - `bch2_sb_errors_to_cpu()`
- Exposes `bch_sb_field_ops_errors`.

Research notes:
- This is the small public interface between validators/fsck paths and persistent error count storage.
