# File Research: sources/cow-pools/bcachefs-tools/fs/scripts/getdents-layout.sh

Build helper script that generates layout-check macros for a copied `getdents_callback64` structure used by `fs/dirent.c`. It supports trusted in-tree mode when no vmlinux is available, verified external/DKMS mode when `pahole` can inspect `getdents_callback64`, and unverified fallback mode that disables the fast path.

The script writes to a temp file, emits either trust/verify/unverified macros plus offsets/size from `pahole`, and only replaces the output if content changed.
