## sources/distributed-fs/ipfs-kubo/test/sharness/t0002-docker-image.sh

Purpose: end-to-end Docker image validation for Kubo container startup, init hooks, API/gateway readiness, and basic content commands.

Important control flow: gated by `DOCKER` prereq, checks Docker version, builds the image from the repo Dockerfile, writes two `/container-init.d` scripts, runs the container with API/gateway ports bound to localhost, waits for gateway and API via `pollEndpoint`, checks init script log ordering and config effects, performs `ipfs add`/`cat` inside the container, compares API `/version` commit with `ipfs version --enc json`, then stops/removes container and image.

State and dependencies: creates a Docker image/tag, container, mounted init scripts, and temporary expected/actual files. Depends on Docker, pollEndpoint, local network ports, and shell helpers.

Risks: requires Docker group access and available ports 5001/8080. Cleanup happens at script end, so early hard failures can leave images/containers. Test signals are container liveness, init ordering, config persistence, content round trip, and commit metadata consistency.
