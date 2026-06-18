## sources/cloud-native/moby/daemon/libnetwork/support/run.sh

Purpose: Runtime entrypoint for the libnetwork support container. It opportunistically refreshes `support.sh` from the upstream Docker/libnetwork repository, then executes it.

Important commands: Uses `wget -O support.sh.new` against the raw GitHub URL, replaces `support.sh` on success, marks it executable, otherwise prints a fallback message, then runs `./support.sh`.

Control flow and state: The only persisted runtime state is the local replacement of `/bin/support.sh` inside the container filesystem. A failed download leaves the baked script in place.

Dependencies and integration points: Requires network access to GitHub, `wget`, and the copied support script. It integrates with the Dockerfile `CMD`.

Risks: Pulling the latest upstream script at runtime makes diagnostics non-reproducible and can change behavior independent of the image. The URL references the historical `docker/libnetwork` repository, not necessarily the vendored Moby copy. There is no checksum or signature verification.

Test signals: No automated tests. Failure handling is simple and visible through stdout.
