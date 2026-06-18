# sources/cloud-native/soci-snapshotter/.github/ISSUE_TEMPLATE/config.yml

Purpose: configures GitHub issue template behavior and discussion routing.

Important APIs/types/functions: `blank_issues_enabled: true` and a contact link named “Ask a question (GitHub Discussions)” targeting the project discussions page.

Control flow: GitHub shows the discussion link alongside issue templates and still permits blank issues.

State and persistence: affects GitHub UI only.

Dependencies/integration: relies on GitHub Discussions being enabled for `awslabs/soci-snapshotter`.

Risks: blank issues can bypass structured bug/feature templates. Stale discussion URL would misroute questions.

Test signals: repository issue creation UI preview.
