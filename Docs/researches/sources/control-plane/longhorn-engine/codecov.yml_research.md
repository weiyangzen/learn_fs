# sources/control-plane/longhorn-engine/codecov.yml

## Purpose
Configures Codecov reporting policy for the Longhorn Engine repository.

## Important APIs, Types, and Functions
- `comment: off` disables Codecov PR comments.
- `coverage.status.project.default.informational: true` makes project coverage informational.
- `coverage.status.patch: off` disables patch coverage status.

## Control Flow
Declarative YAML consumed by Codecov; no executable code.

## State and Persistence Behavior
No runtime state. It affects CI coverage status behavior for submitted reports.

## Dependencies and Integration Points
Integrates with Codecov service and CI upload configuration elsewhere.

## Risks and Edge Cases
Because coverage gates are informational/off, regressions may not block merges through Codecov status. YAML is minimal and sensitive to indentation.

## Test Signals
Not tested by application tests; validation would be through CI/Codecov behavior.
