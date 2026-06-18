## sources/control-plane/longhorn/.github/workflows/update-branch-image-tags.yaml

### Purpose
This release workflow updates Longhorn image tags in a repository branch to `<branch>-head`, regenerates manifests, and opens an auto-merge PR.

### Important APIs, Types, And Functions
It accepts a `branch` input, creates a GitHub App token, checks out that branch, installs `snapd` and `yq`, updates `deploy/longhorn-images.txt` via a shell `replace_images_tags` function, updates `chart/values.yaml` with `yq`, runs `scripts/generate-longhorn-yaml.sh`, creates a signed PR with `peter-evans/create-pull-request`, and enables automerge.

### Control Flow
The shell replacement scans lines for known `longhornio/*` images and rewrites tags. Chart values are updated field-by-field. Manifest regeneration then incorporates chart changes before PR creation.

### State, Persistence, And Dependencies
It mutates a branch through a generated PR. Dependencies are app secrets, snap/yq availability, chart values paths, deploy image list format, manifest generation script, and pinned PR actions.

### Integration Points
Used during release/branch maintenance to point deployment artifacts at branch-head images.

### Risks
The unused `repos_dir` and `modified` variable suggest script drift. Regex replacement is line-oriented and can mis-handle unusual image formats. Snap install can be slow or fail on GitHub runners.

### Test Signals
Manual dispatch on a test branch should produce a PR with expected image tag changes and regenerated manifests only.
