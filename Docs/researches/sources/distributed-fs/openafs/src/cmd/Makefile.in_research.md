# sources/distributed-fs/openafs/src/cmd/Makefile.in

Purpose: builds the OpenAFS command parsing library, its PIC/shared variants, generated command error table files, and tests.

Important targets: `generated` creates `cmd.h` and `cmd_errors.c` from `cmd_errors.et` using `compile_et`. `all` installs `libcmd.a`, `libcmd_pic.a`, `cmd.h`, and `liboafs_cmd.la`. `all64` additionally builds 64-bit object/library variants. `config_file.lo` compiles Heimdal `config_file.c` against `krb5_locl.h` to provide raw config parsing APIs.

Dependencies and integration: depends on com_err (`liboafs_comerr.la`), roken, libtool fragments, pthread make config, and generated `AFS_component_version_number.c`. It exports `<afs/cmd.h>` to the top include directory for consumers.

Risks and tests: generated headers are central to many tools, so `compile_et` behavior affects this build. The clean target removes generated files and local test binaries. Test coverage is delegated to `src/cmd/test`.
