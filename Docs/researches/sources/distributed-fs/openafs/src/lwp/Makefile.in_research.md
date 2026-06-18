## sources/distributed-fs/openafs/src/lwp/Makefile.in

Purpose: Builds the legacy LWP cooperative threading library, compatibility shared/PIC libraries, installs LWP headers, and runs LWP tests.

Important targets and variables: `LIBOBJS`, `LT_objs`, `LT_deps`, `all`, `depinstall`, `liblwp.a`, `liboafs_lwpcompat.la`, `liblwpcompat_pic.la`, `process.o`, `test`, `install`, `dest`, `buildtools`, and `clean`.

Control flow: Builds core objects `lwp.o`, `process.o`, `iomgr.o`, `timer.o`, `threadname.o`, and version object into `liblwp.a`, with libtool objects `waitkey`, `fasttime`, and `lock` added from `.lwp`. `process.o` is selected through a large `SYS_NAME` case that chooses architecture-specific assembly or C context-switch implementation. Header install targets publish `afs_lock.h`, `lwp.h`, and version source.

State and persistence: Produces static/PIC/shared compatibility artifacts, installed headers, generated `process.s` intermediates, and test binaries.

Dependencies and integration: Includes LWP-specific make config and tool config, assembler/preprocessor toolchain, opr library, and platform-specific process context files.

Risks: `process.o` selection is highly platform-sensitive. Assembly preprocessing leaves many architecture branches with custom cleanup. Darwin universal builds rely on `lipo` and arch flags. Static archive rule reaches into `.lwp/` libtool object paths.

Test signals: Build across representative sysnames, LWP test directory, header install, process assembly cleanup, shared/PIC compatibility link, and `AFS_LWP_STACK_SIZE` runtime tests.
