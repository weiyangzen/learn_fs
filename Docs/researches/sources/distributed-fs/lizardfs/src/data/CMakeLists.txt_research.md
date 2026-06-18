# sources/distributed-fs/lizardfs/src/data/CMakeLists.txt

Purpose: installs sample data/configuration files and optionally builds the C client example.

Important APIs/functions: `configure_file` generates configured sample configs from `.in` templates; `install(FILES ...)` places metadata, master/chunkserver/client/metalogger/uRaft examples, and shell completion; test-enabled block creates mock installed headers and `c-client-example`.

Control flow: configure-time substitutions produce `mfsmaster.cfg`, `mfschunkserver.cfg`, `mfsmetalogger.cfg`, and `postinst`; install rules map each example to its component subdirectory. Under `BUILD_TESTS`, symlinked headers preserve example include paths, the C example is compiled, linked with `lizardfs-client stdc++ m`, and installed as a binary.

State and persistence: no runtime state; produces build-tree configured files and install-tree examples.

Dependencies and integration: uses CMake variables such as `DATA_SUBDIR`, `MFSMASTER_EXAMPLES_SUBDIR`, `DEFAULT_USER`, `DATA_PATH`, and library target `lizardfs-client`; passes `POSTINST_SCRIPT` to the parent scope.

Risks: example build depends on symlink support and on client headers staying at the referenced source paths. Install destinations are driven by packaging variables, so misconfigured paths affect package layout.

Test signals: `BUILD_TESTS` compiles `liblizardfs-client-example.c`, providing a syntax/link check for the public C client API.
