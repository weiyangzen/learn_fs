<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/zizmor.yml -->
# sources/cloud-native/moby/.github/workflows/zizmor.yml

## Purpose
Runs the zizmor GitHub Actions security scanner through a shared workflow with medium severity/confidence thresholds and the pedantic persona.

## Important APIs, Types, And Functions
- Triggers on manual dispatch, pushes, tags, and PRs.
- Uses `crazy-max/.github/.github/workflows/zizmor.yml@v1.10.0`.
- Grants `security-events: write` for SARIF/code-scanning output.
- Inputs: `min-severity: medium`, `min-confidence: medium`, and `persona: pedantic`.

## Control Flow
The workflow delegates all scanning to the external reusable workflow. Concurrency cancels stale PR runs only.

## State And Persistence
Scanner findings may persist in GitHub security/code-scanning surfaces. No local artifacts are defined in this wrapper.

## Dependencies And Integration Points
Complements inline zizmor annotations in workflows, such as the labeler `pull_request_target` justification. It depends on the external `crazy-max/.github` workflow pin.

## Risks And Edge Cases
Delegating to an external workflow centralizes scanner behavior but makes this repo dependent on that workflow's interface. Medium thresholds may intentionally ignore low-confidence findings.

## Test Signals
Successful scanner run and any generated security findings are the signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/zizmor.yml -->
