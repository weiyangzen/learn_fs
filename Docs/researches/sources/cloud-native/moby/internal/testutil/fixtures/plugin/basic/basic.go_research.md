<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/fixtures/plugin/basic/basic.go -->
# sources/cloud-native/moby/internal/testutil/fixtures/plugin/basic/basic.go

Purpose: executable fixture for a basic Docker plugin that listens on a Unix socket and serves plugin activation plus likely endpoint behavior used by plugin tests. The main API is the `main` function; it prepares the runtime path, creates a socket, starts an HTTP server, and blocks. State is the plugin socket and serving process inside a plugin rootfs. Dependencies are standard `net`, `net/http`, filesystem, and time packages. Risks include socket path creation, startup timing, platform specificity to Unix sockets, and tests depending on exact fixture routes. Test signal is end-to-end plugin lifecycle and communication behavior when bundled by `fixtures/plugin/plugin.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/fixtures/plugin/basic/basic.go -->
