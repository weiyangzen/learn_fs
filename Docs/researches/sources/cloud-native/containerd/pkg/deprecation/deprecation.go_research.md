<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/deprecation/deprecation.go -->
# sources/cloud-native/containerd/pkg/deprecation/deprecation.go

Purpose: central registry of deprecation warning identifiers and human-readable messages.

Important APIs and types: `Warning`, `Prefix`, `EnvPrefix`, warning constants such as `CRIRegistryMirrors`, `CgroupV1`, `CRIEnableCDI`, and helper functions `Valid` and `Message`.

Control flow and state: a static `messages` map stores warning text. `Valid` checks membership; `Message` returns text and presence flag.

Dependencies and integration: no external dependencies. Other packages can use warning IDs for plugin exports, logs, config validation, and environment gates.

Risks and test signals: string constants are API-like because users and config tooling may depend on them. No local tests in this file; changes need review for wording, removal dates, and backward compatibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/deprecation/deprecation.go -->
