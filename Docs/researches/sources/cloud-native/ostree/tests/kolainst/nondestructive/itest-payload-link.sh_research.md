<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/nondestructive/itest-payload-link.sh -->
## sources/cloud-native/ostree/tests/kolainst/nondestructive/itest-payload-link.sh

Purpose: tests payload-link/reflink behavior for duplicate large objects, unprivileged child repos, and cross-device parent repos.

Important APIs/functions: creates an archive repo with duplicate random objects, serves it with `run_tmp_webserver`, creates XFS reflink loopback filesystems, sets `core.payload-link-threshold 0`, pulls with static deltas disabled, inspects `*.payload-link`, and validates payload checksum targets.

Control flow/state: sets ACLs for user `bin`, mounts two loop devices, performs a pull on the first reflink filesystem, commits from an unprivileged bare-user child repo with parent configured, then repeats across a second filesystem to ensure payload links are not created across devices.

Dependencies/integration: requires podman HTTP helper, loop devices, XFS reflink support, ACL tools, `runuser`, and root.

Risks/test signals: resource-heavy and tagged needs-internet because of webserver image. Signals are payload-link count 1 on same device, count 0 in unprivileged/parent and cross-device cases, and checksum equality.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/nondestructive/itest-payload-link.sh -->
