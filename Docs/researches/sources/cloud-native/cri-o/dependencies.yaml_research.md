# sources/cloud-native/cri-o/dependencies.yaml

## Purpose
Dependency metadata listing CRI-O component versions and external source dependencies for build/release automation.

## Important APIs, Types, and Functions
YAML entries define dependencies, names, versions/commits, and source locations used by automation.

## Control Flow
Tools parse the file to resolve or report dependency versions.

## State and Persistence
No runtime state; source of truth for dependency tracking.

## Dependencies
Depends on repository-specific dependency parser and upstream component availability.

## Integration Points
Integrates with release, CI, and update workflows needing synchronized component versions.

## Risks and Edge Cases
Stale pins, unavailable upstream refs, or schema drift can break automated dependency updates.

## Test Signals
Validation is parser success and build/release jobs using declared versions.
