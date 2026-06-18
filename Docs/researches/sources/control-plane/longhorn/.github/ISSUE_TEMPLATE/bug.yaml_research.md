## sources/control-plane/longhorn/.github/ISSUE_TEMPLATE/bug.yaml

### Purpose
`bug.yaml` defines the GitHub issue form for Longhorn bug reports.

### Important APIs, Types, And Functions
The template sets title prefix `[BUG]`, issue type `Bug`, labels `kind/bug`, `require/qa-review-coverage`, and `require/backport`, and contains required fields for bug description, expected behavior, support bundle, and environment. Optional fields cover reproduction, additional context, and workaround/mitigation.

### Control Flow
GitHub renders the YAML as a structured issue form when users choose "Bug report". Required validations block submission until core fields are provided.

### State, Persistence, And Dependencies
It persists issue metadata defaults and form schema. Dependencies are GitHub issue forms and the label/type names configured in the repository.

### Integration Points
Issue automation workflows consume labels and issue type to add projects, create backport tasks, and update sprint state.

### Risks
Required support bundles can discourage reports when users cannot generate one. Label changes can trigger automation unexpectedly. The empty assignee entry is inert but odd.

### Test Signals
Validation is through GitHub issue form rendering and checking newly created bug issues have expected labels/type/title prefix.
