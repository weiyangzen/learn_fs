<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/vm.yml -->
# sources/cloud-native/moby/.github/workflows/vm.yml

## Purpose
Top-level VM workflow that runs DCO validation and delegates selected integration tests to the reusable Lima VM workflow.

## Important APIs, Types, And Functions
- Triggers on manual dispatch, pushes to master/release branches, and PRs.
- `validate-dco` reuses `.dco.yml`.
- `vm` job calls `.vm.yml` with a matrix containing `template:oraclelinux-8` and integration directories focused on container, build, and system tests.

## Control Flow
DCO runs first. The reusable VM workflow then starts Oracle Linux 8 via Lima and runs the targeted integration directories, unless PR label rules in the child workflow skip validate-only PRs.

## State And Persistence
No state is written by this wrapper beyond child workflow artifacts.

## Dependencies And Integration Points
Depends on `.vm.yml` for actual VM setup and testing. The selected template preserves cgroup v1 coverage until support is formally deprecated.

## Risks And Edge Cases
The matrix currently has one template, so coverage is focused rather than broad. Comments document known AlmaLinux 8 port-forwarding issues and the reason Oracle Linux 8 remains.

## Test Signals
Wrapper success depends on DCO plus the child VM workflow's integration report artifacts and summary.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/vm.yml -->
