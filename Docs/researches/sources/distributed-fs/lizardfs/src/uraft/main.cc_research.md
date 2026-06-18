# sources/distributed-fs/lizardfs/src/uraft/main.cc

Purpose: Main program for `lizardfs-uraft`, a Boost.Asio-based uRaft controller daemon for LizardFS high availability.

Important APIs/types/functions: `parseOptions`; `getSeed`; `daemonize`; `makePidFile`; `main`; `uRaftController::Options`; Boost.Program_options hidden config keys for node id, node addresses, election/heartbeat timing, local master, command timeouts, elector mode, and status port.

Control flow: `parseOptions` reads command-line options, opens and parses the config file, validates node id and node address list, and fills options/pidfile/daemon flags. `main` opens syslog, seeds randomness, optionally daemonizes with double fork and `/dev/null` stdio, creates Boost.Asio IO service and signal handlers, configures and initializes `uRaftController`, writes pidfile, and runs the event loop.

State and persistence: May write a pidfile. As a daemon it changes working directory, umask, stdio fds, and syslog state. Runtime cluster state is managed by `uRaftController`.

Dependencies and integration: Depends on `uraftcontroller.h`, Boost.Asio, Boost.Program_options, syslog, POSIX daemon APIs, and configured `ETC_PATH`. Integrates with the helper script through controller command options.

Risks and test signals: Config parsing accepts hidden options from config files and command line; missing node addresses or invalid ids are fatal. Daemonization closes stdio and writes pidfile after controller options are accepted. Signal handling requires Boost version >= 1.47 for async stop. No direct tests in this subset.
