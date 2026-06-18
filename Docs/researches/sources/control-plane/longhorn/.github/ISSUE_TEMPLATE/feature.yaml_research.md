## sources/control-plane/longhorn/.github/ISSUE_TEMPLATE/feature.yaml

### Purpose
`feature.yaml` defines the GitHub issue form for new Longhorn feature requests.

### Important APIs, Types, And Functions
It sets title prefix `[FEATURE]`, issue type `Feature`, and labels `kind/feature`, `require/lep`, `require/doc`, `require/auto-e2e-test`, and `require/manual-test-plan`. It includes problem, desired solution, alternatives, and additional context fields.

### Control Flow
Only the problem field is required. Labels drive downstream automation for documentation, test planning, LEP requirements, and automation-test issue creation.

### State, Persistence, And Dependencies
The template persists metadata defaults and depends on GitHub issue form schema plus repository labels.

### Integration Points
`create-issue.yml` watches `require/auto-e2e-test`; other issue workflows add project status and milestones.

### Risks
Defaulting every feature to automation and manual test requirements can create follow-up noise for non-testable features. Label renames would break automation.

### Test Signals
New feature issues should get the expected type, labels, and title prefix; auto-test issue automation should trigger when labels are applied.
