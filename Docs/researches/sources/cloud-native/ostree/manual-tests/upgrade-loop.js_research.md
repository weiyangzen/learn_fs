# sources/cloud-native/ostree/manual-tests/upgrade-loop.js

Purpose: This GJS manual test repeatedly alternates deployment targets to stress OSTree sysroot upgrade/downgrade behavior. It is designed for an external supervisor to kill and restart the script and verify sysroot consistency.

Important APIs and functions: It imports `imports.gi.OSTree`, creates `OSTree.Sysroot.new_default()`, loads deployments, gets the active deployment checksum and origin, parses the origin refspec with `OSTree.parse_refspec`, pulls the remote ref, resolves the newest revision, and then loops through `sysroot.cleanup`, commit parent lookup, `repo.pull`, `sysroot.origin_new_from_refspec`, `sysroot.deploy_tree`, `sysroot.write_deployments`, `sysroot.load`, and another cleanup.

Control flow and state: Initial state is the current booted/default deployment. If the starting revision is current, the target is the parent commit, otherwise the target is the newly resolved revision. Each loop writes a two-entry deployment list `[newDeployment, firstDeployment]`, then reloads sysroot state and repeats from the new default.

Dependencies and integration points: Depends on GJS GI bindings, libostree sysroot APIs, repository pull/resolve/load_variant behavior, commit parent metadata, deployment origin keyfiles, and bootloader/sysroot deployment persistence. It exercises the same deployment model documented in `ostree(1)`.

Risks: The loop is intentionally infinite and mutates system deployment state, so it must only run in controlled test machines or VMs. It assumes at least one deployment, a valid origin refspec, a pullable remote, and a parent commit when downgrading. It does not install signal handlers or transactional external assertions itself.

Test signals: The visible markers `DEPLOY BEGIN revision=...` and `DEPLOY END revision=...` let a harness observe progress. A robust test harness should reboot or restart mid-loop, then check deployment list integrity and `ostree admin status`/`fsck`.
