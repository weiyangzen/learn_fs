## sources/control-plane/longhorn/.github/workflows/validate-yamls.yaml

### Purpose
`validate-yamls.yaml` validates selected Longhorn YAML files on pull requests.

### Important APIs, Types, And Functions
It triggers on PR open/edit/synchronize/reopen, checks out the repo, installs `yamllint`, creates a local `.yamllint` config extending defaults while disabling line length, trailing spaces, document start, and empty-line rules, then runs `yamllint -c .yamllint chart/questions.yaml`.

### Control Flow
The workflow fails when `yamllint` finds syntax or enabled rule violations in `chart/questions.yaml`.

### State, Persistence, And Dependencies
It writes a temporary `.yamllint` in the runner workspace only. Dependencies are apt, yamllint, and checkout.

### Integration Points
Protects Helm/Rancher question YAML from syntax regressions.

### Risks
Only `chart/questions.yaml` is validated despite the workflow name implying broader YAML coverage. Many style rules are disabled.

### Test Signals
PRs with invalid YAML in `chart/questions.yaml` should fail; valid YAML should pass.
