# sources/control-plane/longhorn/scripts/update-chart-questions.sh

## Purpose
Updates image tag defaults inside `chart/questions.yaml` from `deploy/longhorn-images.txt`.

## Important APIs and Functions
`check_yq` requires the mikefarah `yq` implementation. For each image line, the script parses `repo`, `tag`, and `component`, maps recognized Longhorn/CSI component names to chart question variable keys, then runs `yq eval -i` to update matching `.questions[].subquestions[]` defaults.

## Control Flow
After yq validation, the script loops through the image list. Recognized components update a specific chart variable; unrecognized components print a message and continue.

## State and Persistence
Mutates `chart/questions.yaml` in place. No cluster or runtime state is touched.

## Dependencies and Integration Points
Depends on mikefarah/yq, the chart question schema, and `deploy/longhorn-images.txt` component naming. Integrates with release automation that keeps image tags synchronized across manifests and Rancher chart questions.

## Risks
Component mapping is duplicated across other update scripts and can drift. Missing variables in questions.yaml do not appear to fail the script. Image lines without tags or non-`longhornio/` prefixes can parse incorrectly.

## Test Signals
Run after modifying `deploy/longhorn-images.txt`, inspect `chart/questions.yaml` diff, and validate with chart packaging/tests. Add coverage for every recognized component and an unknown component.
