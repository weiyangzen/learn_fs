## sources/cloud-native/containers-storage/pkg/fileutils/reflink_unsupported.go

Purpose: non-Linux fallback for reflink-or-copy.

Important APIs/types/functions: `ReflinkOrCopy`.

Control flow: directly calls `io.Copy(dst, src)`.

State and persistence: writes destination file contents.

Dependencies and integration points: portable implementation for platforms without Linux file clone ioctl.

Risks: same offset assumptions as Linux fallback; no CoW optimization.

Test signals: no direct selected tests.
