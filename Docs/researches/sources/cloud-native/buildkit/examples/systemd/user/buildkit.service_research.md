# Research: sources/cloud-native/buildkit/examples/systemd/user/buildkit.service

## Purpose
systemd unit example for a user BuildKit service.

## Important APIs, Types, and Functions
Uses standard `[Unit]`, `[Service]`/`[Socket]`, and `[Install]` sections. It runs BuildKit in a rootless-compatible user systemd session.

## Control Flow
systemd loads/enables the unit, creates sockets when applicable, and starts services on demand or target activation.

## State and Persistence
BuildKit daemon state lives under configured BuildKit roots; systemd stores enablement and runtime socket state.

## Dependencies and Integration Points
Depends on systemd, installed BuildKit binaries, runtime directory permissions, and user-service support for rootless units. Integrates with local buildctl clients through Unix sockets and OS service management.

## Risks and Edge Cases
Wrong socket paths or user/cgroup permissions cause connection failures; rootless units depend on session/lingering behavior.

## Test Signals
No tests; validate with systemctl and `buildctl debug workers`.
