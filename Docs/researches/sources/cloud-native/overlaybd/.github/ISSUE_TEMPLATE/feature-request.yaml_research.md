<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/.github/ISSUE_TEMPLATE/feature-request.yaml -->
# sources/cloud-native/overlaybd/.github/ISSUE_TEMPLATE/feature-request.yaml

Purpose: GitHub issue form for OverlayBD enhancement requests. It collects version, desired behavior, justification, and contributor willingness, then applies the `enhancement` label.

APIs and control flow: This is declarative GitHub issue-form YAML. The `body` sequence defines markdown, input, textarea, and checkbox widgets. The two substantive textareas are required.

State and persistence: Submitted answers become issue body content in GitHub; there is no repository runtime state.

Dependencies and integration: GitHub Issues consumes the schema. Links point users to OverlayBD releases and CNCF Slack.

Risks and test signals: The final checkbox option lacks an explicit `required` block by design. YAML linting and creating a test issue are the main validation signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/.github/ISSUE_TEMPLATE/feature-request.yaml -->
