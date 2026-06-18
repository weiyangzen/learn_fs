## sources/control-plane/longhorn/.github/workflows/close-issue.yml

### Purpose
`close-issue.yml` closes generated backport or automation-test issues when their trigger labels are removed from the source issue.

### Important APIs, Types, And Functions
It reacts to `issues.unlabeled`. The `backport` job handles labels containing `backport/`; the `automation` job handles `require/automation-e2e`. It uses `xom9ikk/split` and `actions/github-script` to search generated issues and close matches.

### Control Flow
For backports, it builds a title search `[BACKPORT][v<version>]<source title>` and filters issues labeled `kind/backport` created by `github-actions[bot]`. For automation, it searches `[TEST]<source title>` issues labeled `kind/test` from the bot. Matching generated issues are closed.

### State, Persistence, And Dependencies
It mutates issue state and depends on generated title conventions, labels, and creator identity.

### Integration Points
It complements `create-issue.yml`, reversing generated issue lifecycle when labels are removed.

### Risks
Title-based matching can miss renamed generated issues or close the wrong issue if titles collide. The automation label checked is `require/automation-e2e`, while feature templates use `require/auto-e2e-test`, so naming drift is a risk.

### Test Signals
Remove backport and automation labels from test issues and verify the corresponding generated issues close.
