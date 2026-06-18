<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/testdata/default-1.7.toml -->
# sources/cloud-native/containerd/integration/client/testdata/default-1.7.toml

## Purpose
Fixture for containerd 1.7 default config migration. It captures the 1.7 default shape with comments marking settings whose defaults changed or whose keys were removed in newer releases.

## APIs, Types, And Functions
The file is TOML input to `containerd config migrate` in `migration_test.go`. It includes CRI settings such as CDI directories, unprivileged network defaults, sandbox image, CNI setup options, runtime sandbox mode, NRI plugin settings, transfer plugin settings, snapshotter settings, and timeouts.

## Control Flow And State
No code runs in the file itself. Migration should transform it to the current default config on supported builds, adding current defaults and omitting obsolete keys while keeping the expected normalized ordering and values.

## Persistence And Integration Points
The fixture represents persistent daemon config stored on disk. It integrates with migration code as an exact golden input for defaults around CRI, runtime v2 task, NRI, transfer, and snapshotters.

## Risks And Test Signals
The risk is fixture rot when defaults change intentionally. Test failures are useful signals for default migration drift, especially around sandbox image updates, CDI/NRI enablement, removed tracing/runtime-v1/zfs/aufs sections, and transfer unpack config behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/testdata/default-1.7.toml -->
