# File Research: sources/cow-pools/bcachefs-tools/include/linux/static_key.h

Defines minimal static-key structures and branch macros. Enable/disable are no-ops, `static_key_enabled()` always returns false, while `static_branch_likely/unlikely()` inspect the embedded integer field.

This is a compile compatibility shim, not a jump-label implementation.
