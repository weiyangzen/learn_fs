# sources/control-plane/longhorn-engine/pkg/meta/version.go

Purpose: centralizes engine build metadata and compatibility/version constants for CLI, controller API, and replica data format.

Important APIs/types/functions: constants define `CLIAPIVersion`, `CLIAPIMinVersion`, `ControllerAPIVersion`, `ControllerAPIMinVersion`, `DataFormatVersion`, and `DataFormatMinVersion`. Build variables `Version`, `GitCommit`, and `BuildDate` are filled externally by main/build flags. `VersionOutput` is the JSON shape returned to callers. `GetVersion` assembles the current output.

Control flow: no dynamic control beyond returning a struct literal.

State and persistence: build variables are process globals; no persistence.

Dependencies and integration points: consumed by CLI/API version reporting and compatibility checks with longhorn-manager and instance-manager.

Risks: compatibility depends on keeping min/current constants aligned with released components. Build variables default to empty strings if linker flags are missing. Comments note version history but enforcement lives elsewhere.

Test signals: no direct tests. A simple test could lock `GetVersion` field mapping but version values are release-managed.
