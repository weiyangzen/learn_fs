# sources/cloud-native/cri-o/test/default.yaml

## Purpose
Minimal YAML test configuration enabling sigstore attachments for default docker policy behavior.

## Important APIs, Types, And Functions
Defines `default-docker.use-sigstore-attachments: true`.

## Control Flow
Static data file; no executable flow.

## State And Persistence
No runtime state. It is configuration input for tests or image policy code.

## Dependencies And Integration Points
Likely consumed by containers/image or CRI-O registry config tests that need a default docker transport setting.

## Risks And Test Signals
Only two lines, so syntax drift is the main risk. No direct test in this subset.
