# sources/distributed-fs/ceph-client/tools/objtool/include/objtool/checksum.h

Purpose: Provides objtool symbol checksum declarations or inline helpers used by livepatch diffing to decide whether functions changed.

Important APIs/types/functions: `checksum_init`, `checksum_update`, `checksum_finish`, `_OBJTOOL_CHECKSUM_H`.

Control flow: When `BUILD_CHECKSUM` is enabled, helpers initialize per-symbol checksum state, feed instruction bytes/data, and finish into `.discard.sym_checksum`; otherwise they compile away.

State and persistence behavior: Stores per-symbol checksum fields in `struct checksum`/`struct sym_checksum`; emitted discard sections are temporary build artifacts.

Dependencies and integration points: Uses `struct symbol`, `struct instruction`, Linux objtool checksum types, and the livepatch diff consumer.

Risks: Disabled builds silently omit checksum data, which makes `klp diff` reject inputs; architecture instruction normalization must remain stable to avoid false changes.

Test signals: Build with and without `BUILD_CHECKSUM`; verify `.discard.sym_checksum` size and livepatch diff changed/unchanged function detection.

Source coverage: researched from the complete local file (44 lines, 1088 bytes).
