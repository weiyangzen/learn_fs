# sources/distributed-fs/openafs/src/tools/dumpscan/Makefile.in

Purpose: builds the dumpscan tools and support libraries for parsing, inspecting, extracting, and repairing AFS volume dumps.

Important targets: `libdumpscan.a` is built from parser, dump writer, directory, pathname, backup header, and stage header objects. `libxfiles.a` is built from stream abstraction objects in the adjacent files. User tools include `afsdump_scan`, `afsdump_dirlist`, `afsdump_extract`, and `dumptool`; `afsdump_xsed` has a target but is not in the default `all` target. Error-table sources/headers are generated from `.et` files via `COMPILE_ET`.

Dependencies/integration: includes OpenAFS build config and LWP make fragments, links against auth, audit, volser, vldb, ubik, rxkad, rx, hcrypto, lwp, util, opr, com_err, roken, and platform libraries. `MODULE_CFLAGS=-DNATIVE_UINT64=afs_uint64` chooses the native `dt_uint64` implementation.

Risks/test signals: object dependency rules ensure generated error headers exist, while `repair.o` disables strict aliasing. The makefile's main test signal is successful compile/link; no runtime dump fixtures are exercised here.
