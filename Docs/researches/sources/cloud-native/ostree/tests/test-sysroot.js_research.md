# sources/cloud-native/ostree/tests/test-sysroot.js

## Purpose
This GJS integration test validates sysroot deployment lifecycle through libostree introspection bindings: initial empty deployments, remote setup, pull, deploy, write deployments, delete deployments, upgrade deployment, and boot checksum behavior.

## Important APIs, Types, And Functions
It uses `libtestExec()` to source `libtest.sh`, `OSTree.Repo`, `OSTree.Sysroot`, `sysroot.get_repo`, `remote_add`, `pull`, `get_merge_deployment`, `origin_new_from_refspec`, `deploy_tree`, `write_deployments`, `get_deployments`, `get_deployment_directory`, and deployment getters `get_csum` and `get_bootcsum`.

## Control Flow
The script creates an OS repository with syslinux fixture, enables mutable-deployments debug mode, opens the upstream repo and resolves the runtime ref, loads an empty sysroot, adds a file remote to the sysroot repo, and pulls. It deploys one tree, writes deployments, verifies the directory exists, then writes an empty deployment list and confirms deletion. It redeploys, creates a new upstream commit, pulls it, deploys an upgrade using the previous deployment as merge deployment, verifies two deployments and different boot/content checksums, creates a third commit with a flag that preserves boot checksum, deploys it, and verifies three deployments.

## State And Persistence
State includes upstream `testos-repo`, sysroot repo config and objects, deployment directories, origin metadata, boot checksums, and deployment lists written to sysroot state.

## Dependencies And Integration Points
This integrates GJS bindings, sysroot deployment internals, remote pull, OS repository fixture helpers, boot checksum generation, and mutable deployment cleanup.

## Risks
Deployment list ordering and directory cleanup must be correct. Merge deployment selection influences boot checksum reuse. JS binding tuple returns must be handled correctly.

## Test Signals
The script prints `1..1` but has multiple internal assertions and status prints: one deployment, empty deployments, two deployments, and final `ok test-sysroot`.
