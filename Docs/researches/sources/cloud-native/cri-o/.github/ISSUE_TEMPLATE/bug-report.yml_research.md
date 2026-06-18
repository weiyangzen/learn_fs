# sources/cloud-native/cri-o/.github/ISSUE_TEMPLATE/bug-report.yml

Purpose: structured GitHub issue form for CRI-O bug reports.

Important fields and flow: applies `kind/bug`, asks for actual behavior, expected behavior, minimal reproduction, optional extra data, CRI-O and Kubernetes versions, OS version, and environment details. Required fields force reporters to include operational context and version data. The problem description points security issues to private advisories.

State and persistence: creates issue metadata and body content in GitHub; no code state.

Dependencies and integration: used by GitHub issue forms. The collected `crio --version`, `kubectl version`, `/etc/os-release`, and `uname -a` outputs support maintainer triage.

Risks: required long text areas can deter reports, but they reduce underspecified issues. Security guidance is advisory and depends on reporter compliance.

Test signals: opening a new issue in GitHub validates form rendering; no CI tests.
