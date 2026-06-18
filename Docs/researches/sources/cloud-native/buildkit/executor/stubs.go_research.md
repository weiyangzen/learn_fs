# Research: sources/cloud-native/buildkit/executor/stubs.go

## Purpose
Mount-stub cleanup helper.

## Important APIs, Types, and Functions
`MountStubsCleaner` returns a cleanup closure for mount destination stubs.

## Control Flow
After execution it scans requested mount destinations and removes empty files/directories or recursive stubs while avoiding mounted paths.

## State and Persistence
Mutates temporary rootfs contents only.

## Dependencies and Integration Points
Depends on continuity fs helpers, syscall mount checks, and path safety. Used by runc executor rootfs cleanup.

## Risks and Edge Cases
Must not escape rootfs or remove real content; recursive cleanup is sensitive.

## Test Signals
Integration tests should catch leaks/unsafe removal.
