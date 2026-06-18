# sources/cloud-native/containerd/.github/workflows/windows-periodic-trigger.yml

## Purpose
This scheduled/manual trigger delegates to the upstream reusable Windows process-isolated integration workflow.

## Important APIs, Types, And Functions
It triggers daily at 01:00 UTC or manually, gates to the upstream repository, and calls `containerd/containerd/.github/workflows/windows-periodic.yml@main` with Azure secrets.

## Control Flow
The single job invokes the reusable workflow using `workflow_call` semantics.

## State And Persistence
All runtime state is owned by the called workflow.

## Dependencies And Integration Points
It depends on GitHub reusable workflow support and configured Azure secrets.

## Risks
Hard-coded upstream workflow reference limits fork use and means the trigger always follows main's reusable workflow.

## Test Signals
Successful invocation and completion of the delegated workflow validate this file.
