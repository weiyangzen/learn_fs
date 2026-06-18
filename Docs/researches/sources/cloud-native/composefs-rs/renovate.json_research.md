# sources/cloud-native/composefs-rs/renovate.json

Purpose: configures Renovate for composefs-rs by extending a shared bootc-dev infrastructure preset.

Important APIs/types/functions: JSON schema URL and `extends: ["local>bootc-dev/infra:renovate-shared-config.json"]`.

Control flow: Renovate loads the shared local preset to determine dependency update behavior.

State/persistence: repository automation configuration only.

Dependencies/integration: depends on Renovate and the referenced shared config repository/preset.

Risks/test signals: if the local preset is unavailable or renamed, dependency automation fails. No runtime tests.
