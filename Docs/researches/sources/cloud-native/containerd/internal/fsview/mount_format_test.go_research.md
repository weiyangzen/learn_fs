# sources/cloud-native/containerd/internal/fsview/mount_format_test.go

## Purpose
Tests `format/overlay` mount template handling in fsview.

## Important APIs, Types, And Functions
Tests exercise `{{ overlay start end }}`, reversed ranges, `{{ mount i }}`, unsupported mount types, and suffix handling through `FSMounts`.

## Control Flow
Temporary EROFS layers or bind roots are assembled, then format overlay mounts reference preceding mounts. Tests read files, check whiteouts, and expect `errdefs.ErrNotImplemented` for unsupported types.

## State And Persistence
Creates temporary layer files/directories and closes returned views.

## Dependencies And Integration Points
Uses containerd mount types, fsview, EROFS test helpers, `io/fs`, and testify.

## Risks
Many cases depend on EROFS helper availability and plugin registration. Template tests do not cover malformed template syntax exhaustively.

## Test Signals
Strong signal for template-based composition of layered filesystem views.
