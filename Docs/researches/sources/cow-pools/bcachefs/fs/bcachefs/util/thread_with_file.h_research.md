# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/thread_with_file.h

## Summary
Declares the fd-backed kthread and stdio-redirection interfaces.

## Main Contents
- `struct thread_with_file` with task pointer, return code, and done flag.
- `struct thread_with_stdio_ops` with `exit`, thread `fn`, and optional `unlocked_ioctl`.
- `struct thread_with_stdio`, embedding `thread_with_file`, `stdio_redirect`, and ops pointer.
- Public APIs for running file-backed threads, stdio-backed threads, stdout-only threads, and stdio read/write/printf helpers.

## Important Behavior
The comments define two tiers: low-level custom `file_operations`, where the caller owns release cleanup, and high-level stdio redirection with implemented polling and pipe-like shutdown semantics.

## Risks
The header’s API contract is lifetime-sensitive: lower-level users must stop the kthread on fd release, while higher-level users must initialize buffers and provide an exit hook suitable for release-time cleanup.
