# sources/cloud-native/containers-storage/pkg/system/lstat_unix.go

Purpose: implements Unix `Lstat` returning the package's portable `StatT` abstraction.

Important APIs, types, and functions: `Lstat(path string) (*StatT, error)`.

Control flow: calls `syscall.Lstat` into `syscall.Stat_t`; on error returns an `os.PathError`, otherwise converts with `fromStatT`.

State and persistence: reads filesystem metadata without following symlinks.

Dependencies and integration points: depends on `os` and `syscall`; selected for non-Windows builds. `fromStatT` and `StatT` are defined in other system files.

Risks and edge cases: conversion correctness depends on platform-specific `fromStatT`. Errors are wrapped with operation `"Lstat"`.

Test signals: `lstat_unix_test.go` verifies success for existing files and error/nil stat for missing files.
