## sources/distributed-fs/beegfs/client_module/dkms.conf.in

### Purpose
Template for DKMS configuration of the BeeGFS client kernel module.

### Important APIs, Types, and Functions
- Template variables: `__NAME__`, `__VERSION__`, and `__MODNAME__`.
- `BUILT_MODULE_NAME[0]`, `BUILT_MODULE_LOCATION[0]`, and `DEST_MODULE_LOCATION[0]` describe the built module.
- `MAKE[0]` runs `make -C build module` with `KDIR=$kernel_source_dir`, target module name, and version.
- `CLEAN` invokes `make -C build clean`.
- `AUTOINSTALL="yes"` requests automatic rebuild/install for new kernels.

### Control Flow and State
DKMS substitutes variables and executes the configured make/clean commands when building or removing modules. State is managed by DKMS outside this file.

### Dependencies and Integration Points
Used by CMake/package scripts to generate installable DKMS metadata. Depends on the client module `build` Makefile supporting `module` and `clean` targets.

### Risks and Edge Cases
Quoting in `MAKE[0]` must survive DKMS shell handling. Kernel source directory correctness is delegated to DKMS. Template mismatch with actual module target names breaks DKMS builds.

### Test Signals
DKMS add/build/install tests on supported distributions validate the template.
