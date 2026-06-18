<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/.github/dependabot.yml -->
## sources/cloud-native/ostree/.github/dependabot.yml

### Purpose
This Dependabot config keeps git submodules and GitHub Actions dependencies fresh.

### APIs, Types, and Control Flow
It uses config `version: 2` and declares two update ecosystems: `gitsubmodule` at repository root on a daily schedule, and `github-actions` at repository root on a weekly schedule.

### State, Dependencies, and Integration
Dependabot opens PRs against dependency metadata; it does not update code at runtime. It integrates with the submodule commit-message gate in `ci/ci-commitmessage-submodules.sh`, which explicitly exempts Dependabot-authored submodule bumps from the manual `Update submodule: path` message requirement.

### Risks and Test Signals
Submodule updates can affect vendored C/build behavior and should be covered by the full CI matrix. Actions updates can alter runner behavior. Test signals are Dependabot PR CI results and the submodule gate.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/.github/dependabot.yml -->
