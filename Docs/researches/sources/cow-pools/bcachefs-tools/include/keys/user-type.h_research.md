# File Research: sources/cow-pools/bcachefs-tools/include/keys/user-type.h

Purpose: minimal key subsystem compatibility header.

Key contents:
- Include guard.
- Includes `<linux/key.h>`.
- No additional declarations.

Important interactions:
- Satisfies kernel-style includes for code that references user key types.
