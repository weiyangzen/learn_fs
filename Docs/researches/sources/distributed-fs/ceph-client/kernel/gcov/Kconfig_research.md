<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/gcov/Kconfig -->
# sources/distributed-fs/ceph-client/kernel/gcov/Kconfig

Purpose: defines configuration options for gcov-based kernel profiling and coverage export. It lets builds enable kernel gcov support, optionally instrument the whole kernel, and documents per-file/per-directory Makefile controls.

Important APIs/types/functions: configuration symbols are `GCOV_KERNEL`, `ARCH_HAS_GCOV_PROFILE_ALL`, and `GCOV_PROFILE_ALL`. `GCOV_KERNEL` depends on `DEBUG_FS` and either architectures that do not require disabling profiling instrumentation or compiler support for `no_profile_fn` attributes; it selects `CONSTRUCTORS`. `GCOV_PROFILE_ALL` depends on `GCOV_KERNEL`, architecture opt-in, and not `COMPILE_TEST`.

Control flow: this is build-time Kconfig logic only. Enabling `GCOV_KERNEL` includes the gcov support code and debugfs interface. Enabling `GCOV_PROFILE_ALL` asks the build to instrument the entire kernel, while Makefile variables such as `GCOV_PROFILE_foo.o := y/n` and `GCOV_PROFILE := y/n` select or exclude narrower scopes.

State and persistence behavior: no runtime state is stored by Kconfig, but enabled options cause runtime coverage counters and debugfs-visible gcov data to exist. Profiling data is accessed through mounted debugfs and is not persistent across reboot unless external tooling saves it.

Dependencies and integration points: integrates with compiler instrumentation, kernel constructors, debugfs, architecture support, and the `kernel/gcov` build files. It also interacts with every profiled object because instrumentation changes code size and runtime overhead.

Risks: whole-kernel profiling increases image size and slows execution. Instrumenting objects not linked into the final kernel can create linker errors, as the help text warns. Missing architecture/compiler support can create recursive instrumentation or profiling of code that must not be instrumented.

Test signals: Kconfig dependency tests across GCC/Clang and architectures, builds with `GCOV_KERNEL=y`, targeted `GCOV_PROFILE` builds, `GCOV_PROFILE_ALL` architecture builds, debugfs coverage extraction smoke tests, and negative build tests for excluded objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/gcov/Kconfig -->
