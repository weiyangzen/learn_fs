## sources/distributed-fs/ipfs-kubo/test/sharness/t0003-docker-migrate.sh

Purpose: Docker image migration-path test verifying an old repo triggers migration download from configured distribution sources.

Important control flow: gated by Docker, builds the image, configures migration source variables, stages a fake HTTP response, mutates repo version metadata to simulate an old repo, starts a fake distribution server, runs the container, verifies the container attempted to pull the expected migration asset, inspects logs, stops the container, kills the fake server, and checks the requested version.

State and dependencies: manipulates a test repo, Docker container/image state, netcat or equivalent fake server state, and migration config files. It integrates Kubo container startup with fs-repo migration logic.

Risks: depends on networking, Docker, migration naming conventions, and precise HTTP request behavior. Process cleanup for the fake server is important. Test signals are observed migration request path/version and expected container log behavior.
