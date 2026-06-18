## sources/control-plane/longhorn/.github/ISSUE_TEMPLATE/config.yml

### Purpose
`config.yml` configures repository issue-template behavior.

### Important APIs, Types, And Functions
It disables blank issues and provides a contact link to GitHub Discussions for usage questions.

### Control Flow
GitHub reads this file when presenting issue creation choices. Users cannot open a blank issue through the standard UI.

### State, Persistence, And Dependencies
It persists repository issue intake policy and depends on GitHub issue-template config syntax.

### Integration Points
Structured issue forms and issue-management automations rely on users selecting one of the defined templates rather than bypassing metadata.

### Risks
Disabling blank issues can block legitimate reports that do not fit templates. The discussion link must remain valid.

### Test Signals
Manual GitHub UI verification should show no blank issue option and the Discussions contact link.
