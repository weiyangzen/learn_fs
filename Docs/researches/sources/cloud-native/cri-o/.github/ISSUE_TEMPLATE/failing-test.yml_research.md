# sources/cloud-native/cri-o/.github/ISSUE_TEMPLATE/failing-test.yml

Purpose: structured issue form for continuously failing CRI-O CI tests or jobs.

Important fields and flow: applies `kind/failing-test`, requires failing job names, failing tests, and when failure started; optional fields capture Testgrid link, suspected reason, and additional context.

State and persistence: produces GitHub issue body content and labels.

Dependencies and integration: supports CI triage workflows and release health tracking by collecting consistent failure metadata.

Risks: the template relies on users distinguishing continuous failures from one-off flakes. It does not enforce links to logs or workflow runs.

Test signals: GitHub issue-form rendering is the validation mechanism.
