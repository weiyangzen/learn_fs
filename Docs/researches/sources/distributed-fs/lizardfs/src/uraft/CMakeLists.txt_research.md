# sources/distributed-fs/lizardfs/src/uraft/CMakeLists.txt

Purpose: Build and install configuration for the `lizardfs-uraft` high-availability helper daemon and shell helper script.

Important APIs/types/functions: `configure_file(lizardfs-uraft-helper.in ...)`; `collect_sources(URAFT)`; executable `lizardfs-uraft`; link libraries `${Boost_LIBRARIES}`, `${RT_LIBRARY}`, `pthread`; install rules.

Control flow: CMake configures the helper script with install-time paths, collects sources plus `time_utils.cc`, builds the daemon, links dependencies, and installs the binary and helper.

State and persistence: Build/install state only.

Dependencies and integration: Integrates uRaft controller code with Boost, pthreads, and the installed LizardFS service management scripts.

Risks and test signals: Missing path substitutions can break the helper script. Link dependencies are platform-sensitive because of realtime and pthread libraries.
