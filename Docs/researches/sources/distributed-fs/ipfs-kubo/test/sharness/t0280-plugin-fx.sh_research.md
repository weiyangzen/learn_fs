## sources/distributed-fs/ipfs-kubo/test/sharness/t0280-plugin-fx.sh

Purpose: verifies that the fx-based test plugin path is invoked during daemon startup when the test environment enables it.

Important commands and control flow: initializes a repo, exports `GOLOG_LOG_LEVEL=fxtestplugin=debug` and `TEST_FX_PLUGIN=1`, launches the daemon, then searches `daemon_err` for the expected log entry `invoked test fx function`.

State and persistence: only environment variables and daemon logs are involved; no repo content is written beyond initialization.

Dependencies and integration points: depends on sharness daemon helpers, Kubo's fx dependency-injection/plugin hook, go-log output routing, and the test plugin compiled into the binary under the `TEST_FX_PLUGIN` gate.

Risks and test signals: the test is a concise startup integration signal. It is sensitive to log message text, logger name/level, and changes in where daemon stderr is captured.
