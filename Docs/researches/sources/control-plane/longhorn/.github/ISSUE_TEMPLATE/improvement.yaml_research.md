## sources/control-plane/longhorn/.github/ISSUE_TEMPLATE/improvement.yaml

### Purpose
`improvement.yaml` defines the issue form for improvements to existing Longhorn features.

### Important APIs, Types, And Functions
It sets title prefix `[IMPROVEMENT]`, issue type `Improvement`, labels `kind/improvement`, `require/doc`, `require/manual-test-plan`, and `require/backport`, and asks for related feature/problem, desired solution, alternatives, and additional context.

### Control Flow
GitHub enforces the related-feature/problem field as required and applies default metadata at issue creation.

### State, Persistence, And Dependencies
It persists issue intake schema and depends on configured labels and issue types.

### Integration Points
Default backport and documentation/test labels feed issue management workflows and release planning.

### Risks
Automatically requiring backports for all improvements may create unnecessary backport tasks. Empty assignee entry is harmless but untidy.

### Test Signals
Issue form rendering and metadata on created improvement issues validate the file.
