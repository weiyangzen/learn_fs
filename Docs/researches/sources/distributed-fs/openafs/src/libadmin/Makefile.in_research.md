## sources/distributed-fs/openafs/src/libadmin/Makefile.in

Purpose: this makefile installs the top-level AFS admin public header.

Important targets: `all` ensures `${TOP_INCDIR}/afs/afs_Admin.h` is installed from `afs_Admin.h`. `install` and `dest` install the same header into package include directories. `clean` has no commands.

State and persistence: only installed header artifacts.

Dependencies and integration points: includes top-level config and pthread make fragments, indicating admin libraries are pthread-aware even though this makefile only handles the public header.

Risks: no library build happens here; subdirectories such as `adminutil` own utility library construction. Consumers expecting `make` in this directory to build all admin components must rely on higher-level orchestration.

Test signals: successful header installation.
