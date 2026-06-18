## sources/cloud-native/moby/daemon/internal/idtools/idtools.go

Purpose: Defines a small daemon-local identity value.

Important type: `Identity` holds either Unix `UID`/`GID` or Windows `SID`, with the comment specifying that both modes should not be used at once.

Control flow and state: Data-only struct, no methods.

Dependencies and integration: Used wherever daemon internals need to pass identity data across platform-specific code without importing a broader idtools package.

Risks: The exclusivity invariant is documented but not enforced by constructors or validation. Zero values can mean root/root on Unix or unset depending on context.

Persistence and tests: No persistence logic and no tests in this file.
