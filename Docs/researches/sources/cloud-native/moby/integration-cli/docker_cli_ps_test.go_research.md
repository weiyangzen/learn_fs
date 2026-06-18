# sources/cloud-native/moby/integration-cli/docker_cli_ps_test.go

Purpose: extensive `docker ps` behavior coverage for ordering, limits, filters, sizes, image display, ports, mounts, networks, labels, health, status, and link-name cleanup.

Important APIs and functions: `DockerCLIPsSuite`, `assertContainerList`, `checkPsAncestorFilterOutput`, `ExistingContainerIDs/Names`, `RemoveOutputForExistingElements`, `runSleepingContainer`, `cli.BuildCmd`, `units.FromHumanSize`, `stringid.TruncateID`, `waitForHealthStatus`, and `icmd`.

Control flow: the base test creates running/exited containers and verifies `ps`, `ps -a`, `-n`, `since`, and `before` ordering. Other tests parse `ps -s`, filter by status/health/id/name/ancestor/label/exited/created/network/ports/volume, verify image reference display after retag/commit, hide ports for stopped containers, display mounts and support volume filters, maintain deterministic order, and remove deleted container link aliases from names.

State and persistence: creates many containers, labels, healthchecks, custom images, volumes, bind mounts, networks, port mappings, commits images, and retags images. It uses current daemon state as a baseline and filters out pre-existing resources.

Dependencies and integration points: busybox, BuildKit gating for ancestor ordering, healthcheck state transitions, Docker output table formatting, image graph ancestry, mount and network inspect data, and platform-specific size behavior.

Risks: output table parsing is brittle; tests are sensitive to parallel containers despite baseline filtering; health and size checks can be timing/filesystem dependent; Windows paths and pause behavior require skips.

Test signals: `docker ps` must present correct containers in stable order, apply filters with correct AND/OR semantics, report accurate size/mount/port/network/image data, and avoid stale link names after linked containers are deleted.
