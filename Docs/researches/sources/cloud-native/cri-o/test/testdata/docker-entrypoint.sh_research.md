<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/docker-entrypoint.sh -->
# sources/cloud-native/cri-o/test/testdata/docker-entrypoint.sh

Purpose: Redis-compatible entrypoint included in the CRI-O CI image.

Important flow: if the first argument looks like an option or `.conf`, prepends `redis-server`. If running `redis-server` as root, it chowns the current directory to the Redis user and re-execs through `su-exec`; otherwise it executes the provided command.

State and integration: mutates ownership of the working directory inside the container and then replaces the shell process. Risks include recursive re-exec assumptions, dependency on `su-exec`, and ownership changes on mounted volumes. Test signal comes from Redis container fixture startup.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/docker-entrypoint.sh -->
