# sources/cloud-native/moby/cmd/dockerd/winresources/event_messages.h

## Purpose
Contains generated Windows message resource constants and documentation for event-message IDs.

## APIs, Types, And Functions
The file is a generated C header from `windmc`. It documents the 32-bit event identifier layout with severity, customer, reserved, facility, and code fields, and defines generated symbolic message IDs elsewhere in the header.

## Control Flow, State, And Integration
There is no runtime control flow; the header participates in Windows resource compilation. Its state is generated source that must match the `.mc` message definition and produced binary resources.

## Risks And Test Signals
Risks include manual edits, stale generated IDs, and mismatch between header and event message binary. Integration is with Windows Event Log resources for dockerd.
