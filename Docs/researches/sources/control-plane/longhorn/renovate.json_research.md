<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/renovate.json -->
# sources/control-plane/longhorn/renovate.json

Purpose: repository Renovate configuration inheritance.

Important APIs/types/functions: JSON object with `extends: ["github>longhorn/release:renovate-default"]`.

Control flow: Renovate loads this config, resolves the shared Longhorn release preset from GitHub, and applies preset rules for dependency update discovery and PR creation.

State and persistence: no runtime state; Renovate creates update branches/PRs externally when run.

Dependencies/integration points: depends on Renovate, GitHub preset resolution, and the `longhorn/release` repository.

Risks/test signals: shared preset changes affect this repo without local diff, and unavailable GitHub preset resolution breaks Renovate. Test signals are `renovate-config-validator`, dry-run logs showing loaded preset, and expected dependency update PR behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/renovate.json -->
