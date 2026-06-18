# subset-b-009216 Research

Grouped source-tree-aligned research for the requested Connectathon test files. Each section preserves the source path in its title and is delimited for deterministic reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/basic/console/test1.mak -->
# sources/test-tools/cthon04/basic/console/test1.mak

Purpose: Visual C++ 2.0 NMAKE project for the Win32 console build of test1, the Connectathon basic file and directory creation test.

Important APIs/types/functions: this is generated make syntax, not C code. Key macros are CFG, CPP, RSC, OUTDIR, INTDIR, CPP_PROJ, BSC32_FLAGS, LINK32_FLAGS, and LINK32_OBJS. It builds ..\TEST1.C plus the shared support object; test1 compiles ..\SUBR.C in the project itself. The linked executable is test1.exe/upper-case variant under WinRel or WinDebug.

Control flow: CFG defaults to "Win32 Debug", validates Release/Debug, creates the output directory, compiles C sources with cl.exe into WinRel or WinDebug, optionally emits browser .SBR/.BSC files with bscmake.exe, and links with link.exe as a console subsystem target.

State and persistence behavior: creates build products under local WinRel/WinDebug directories: .OBJ, .SBR, .BSC, .PDB, and .EXE. It does not run the test or manage NFSTESTDIR; runtime filesystem changes come from the built C program.

Dependencies and integration points: depends on Microsoft Visual C++ command-line tools and Win32 system libraries. The source program exercises dirtree(), creat(), mkdir/chdir wrappers. It integrates with tests.h/unixdos.h and the shared SUBR implementation or object.

Risks: generated path casing is inconsistent, especially the debug SUBR object path in many projects; stale SUBR.OBJ can make tests link against old helper behavior; /W0 hides compiler warnings; generated files target old MSVC flags such as /GX and /ML.

Test signals: build success is production of the executable and optional browser database. Runtime success must be observed by launching the executable and checking for the per-test "ok" line from complete().
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/basic/console/test1.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/basic/console/test2.mak -->
# sources/test-tools/cthon04/basic/console/test2.mak

Purpose: Visual C++ 2.0 NMAKE project for the Win32 console build of test2, the Connectathon basic file and directory removal test.

Important APIs/types/functions: this is generated make syntax, not C code. Key macros are CFG, CPP, RSC, OUTDIR, INTDIR, CPP_PROJ, BSC32_FLAGS, LINK32_FLAGS, and LINK32_OBJS. It builds ..\TEST2.C plus the shared support object; links against .\WinRel\SUBR.OBJ and .\WINDEBUG\SUBR.OBJ rather than compiling SUBR.C in this project. The linked executable is test2.exe/upper-case variant under WinRel or WinDebug.

Control flow: CFG defaults to "Win32 Debug", validates Release/Debug, creates the output directory, compiles C sources with cl.exe into WinRel or WinDebug, optionally emits browser .SBR/.BSC files with bscmake.exe, and links with link.exe as a console subsystem target.

State and persistence behavior: creates build products under local WinRel/WinDebug directories: .OBJ, .SBR, .BSC, .PDB, and .EXE. It does not run the test or manage NFSTESTDIR; runtime filesystem changes come from the built C program.

Dependencies and integration points: depends on Microsoft Visual C++ command-line tools and Win32 system libraries. The source program exercises rmdirtree(), unlink(), rmdir(), system("test1 -s ..."). It integrates with tests.h/unixdos.h and the shared SUBR implementation or object.

Risks: generated path casing is inconsistent, especially the debug SUBR object path in many projects; stale SUBR.OBJ can make tests link against old helper behavior; /W0 hides compiler warnings; generated files target old MSVC flags such as /GX and /ML.

Test signals: build success is production of the executable and optional browser database. Runtime success must be observed by launching the executable and checking for the per-test "ok" line from complete().
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/basic/console/test2.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/basic/console/test3.mak -->
# sources/test-tools/cthon04/basic/console/test3.mak

Purpose: Visual C++ 2.0 NMAKE project for the Win32 console build of test3, the Connectathon basic lookup across mount points test.

Important APIs/types/functions: this is generated make syntax, not C code. Key macros are CFG, CPP, RSC, OUTDIR, INTDIR, CPP_PROJ, BSC32_FLAGS, LINK32_FLAGS, and LINK32_OBJS. It builds ..\TEST3.C plus the shared support object; links against .\WinRel\SUBR.OBJ and .\WINDEBUG\SUBR.OBJ rather than compiling SUBR.C in this project. The linked executable is test3.exe/upper-case variant under WinRel or WinDebug.

Control flow: CFG defaults to "Win32 Debug", validates Release/Debug, creates the output directory, compiles C sources with cl.exe into WinRel or WinDebug, optionally emits browser .SBR/.BSC files with bscmake.exe, and links with link.exe as a console subsystem target.

State and persistence behavior: creates build products under local WinRel/WinDebug directories: .OBJ, .SBR, .BSC, .PDB, and .EXE. It does not run the test or manage NFSTESTDIR; runtime filesystem changes come from the built C program.

Dependencies and integration points: depends on Microsoft Visual C++ command-line tools and Win32 system libraries. The source program exercises getcwd(), stat(). It integrates with tests.h/unixdos.h and the shared SUBR implementation or object.

Risks: generated path casing is inconsistent, especially the debug SUBR object path in many projects; stale SUBR.OBJ can make tests link against old helper behavior; /W0 hides compiler warnings; generated files target old MSVC flags such as /GX and /ML.

Test signals: build success is production of the executable and optional browser database. Runtime success must be observed by launching the executable and checking for the per-test "ok" line from complete().
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/basic/console/test3.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/basic/console/test4.mak -->
# sources/test-tools/cthon04/basic/console/test4.mak

Purpose: Visual C++ 2.0 NMAKE project for the Win32 console build of test4, the Connectathon basic setattr/getattr/lookup test.

Important APIs/types/functions: this is generated make syntax, not C code. Key macros are CFG, CPP, RSC, OUTDIR, INTDIR, CPP_PROJ, BSC32_FLAGS, LINK32_FLAGS, and LINK32_OBJS. It builds ..\TEST4.C plus the shared support object; links against .\WinRel\SUBR.OBJ and .\WINDEBUG\SUBR.OBJ rather than compiling SUBR.C in this project. The linked executable is test4.exe/upper-case variant under WinRel or WinDebug.

Control flow: CFG defaults to "Win32 Debug", validates Release/Debug, creates the output directory, compiles C sources with cl.exe into WinRel or WinDebug, optionally emits browser .SBR/.BSC files with bscmake.exe, and links with link.exe as a console subsystem target.

State and persistence behavior: creates build products under local WinRel/WinDebug directories: .OBJ, .SBR, .BSC, .PDB, and .EXE. It does not run the test or manage NFSTESTDIR; runtime filesystem changes come from the built C program.

Dependencies and integration points: depends on Microsoft Visual C++ command-line tools and Win32 system libraries. The source program exercises chmod(), stat(), dirtree(). It integrates with tests.h/unixdos.h and the shared SUBR implementation or object.

Risks: generated path casing is inconsistent, especially the debug SUBR object path in many projects; stale SUBR.OBJ can make tests link against old helper behavior; /W0 hides compiler warnings; generated files target old MSVC flags such as /GX and /ML.

Test signals: build success is production of the executable and optional browser database. Runtime success must be observed by launching the executable and checking for the per-test "ok" line from complete().
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/basic/console/test4.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/basic/console/test4a.mak -->
# sources/test-tools/cthon04/basic/console/test4a.mak

Purpose: Visual C++ 2.0 NMAKE project for the Win32 console build of test4a, the Connectathon basic getattr/lookup test.

Important APIs/types/functions: this is generated make syntax, not C code. Key macros are CFG, CPP, RSC, OUTDIR, INTDIR, CPP_PROJ, BSC32_FLAGS, LINK32_FLAGS, and LINK32_OBJS. It builds ..\TEST4A.C plus the shared support object; links against .\WinRel\SUBR.OBJ and .\WINDEBUG\SUBR.OBJ rather than compiling SUBR.C in this project. The linked executable is test4a.exe/upper-case variant under WinRel or WinDebug.

Control flow: CFG defaults to "Win32 Debug", validates Release/Debug, creates the output directory, compiles C sources with cl.exe into WinRel or WinDebug, optionally emits browser .SBR/.BSC files with bscmake.exe, and links with link.exe as a console subsystem target.

State and persistence behavior: creates build products under local WinRel/WinDebug directories: .OBJ, .SBR, .BSC, .PDB, and .EXE. It does not run the test or manage NFSTESTDIR; runtime filesystem changes come from the built C program.

Dependencies and integration points: depends on Microsoft Visual C++ command-line tools and Win32 system libraries. The source program exercises stat(), dirtree(). It integrates with tests.h/unixdos.h and the shared SUBR implementation or object.

Risks: generated path casing is inconsistent, especially the debug SUBR object path in many projects; stale SUBR.OBJ can make tests link against old helper behavior; /W0 hides compiler warnings; generated files target old MSVC flags such as /GX and /ML.

Test signals: build success is production of the executable and optional browser database. Runtime success must be observed by launching the executable and checking for the per-test "ok" line from complete().
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/basic/console/test4a.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/basic/console/test5.mak -->
# sources/test-tools/cthon04/basic/console/test5.mak

Purpose: Visual C++ 2.0 NMAKE project for the Win32 console build of test5, the Connectathon basic read and write test.

Important APIs/types/functions: this is generated make syntax, not C code. Key macros are CFG, CPP, RSC, OUTDIR, INTDIR, CPP_PROJ, BSC32_FLAGS, LINK32_FLAGS, and LINK32_OBJS. It builds ..\TEST5.C plus the shared support object; links against .\WinRel\SUBR.OBJ and .\WINDEBUG\SUBR.OBJ rather than compiling SUBR.C in this project. The linked executable is test5.exe/upper-case variant under WinRel or WinDebug.

Control flow: CFG defaults to "Win32 Debug", validates Release/Debug, creates the output directory, compiles C sources with cl.exe into WinRel or WinDebug, optionally emits browser .SBR/.BSC files with bscmake.exe, and links with link.exe as a console subsystem target.

State and persistence behavior: creates build products under local WinRel/WinDebug directories: .OBJ, .SBR, .BSC, .PDB, and .EXE. It does not run the test or manage NFSTESTDIR; runtime filesystem changes come from the built C program.

Dependencies and integration points: depends on Microsoft Visual C++ command-line tools and Win32 system libraries. The source program exercises open()/creat(), write(), read(), stat(), optional mmap/msync. It integrates with tests.h/unixdos.h and the shared SUBR implementation or object.

Risks: generated path casing is inconsistent, especially the debug SUBR object path in many projects; stale SUBR.OBJ can make tests link against old helper behavior; /W0 hides compiler warnings; generated files target old MSVC flags such as /GX and /ML.

Test signals: build success is production of the executable and optional browser database. Runtime success must be observed by launching the executable and checking for the per-test "ok" line from complete().
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/basic/console/test5.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/basic/console/test5a.mak -->
# sources/test-tools/cthon04/basic/console/test5a.mak

Purpose: Visual C++ 2.0 NMAKE project for the Win32 console build of test5a, the Connectathon basic write path test.

Important APIs/types/functions: this is generated make syntax, not C code. Key macros are CFG, CPP, RSC, OUTDIR, INTDIR, CPP_PROJ, BSC32_FLAGS, LINK32_FLAGS, and LINK32_OBJS. It builds ..\TEST5A.C plus the shared support object; links against .\WinRel\SUBR.OBJ and .\WINDEBUG\SUBR.OBJ rather than compiling SUBR.C in this project. The linked executable is test5a.exe/upper-case variant under WinRel or WinDebug.

Control flow: CFG defaults to "Win32 Debug", validates Release/Debug, creates the output directory, compiles C sources with cl.exe into WinRel or WinDebug, optionally emits browser .SBR/.BSC files with bscmake.exe, and links with link.exe as a console subsystem target.

State and persistence behavior: creates build products under local WinRel/WinDebug directories: .OBJ, .SBR, .BSC, .PDB, and .EXE. It does not run the test or manage NFSTESTDIR; runtime filesystem changes come from the built C program.

Dependencies and integration points: depends on Microsoft Visual C++ command-line tools and Win32 system libraries. The source program exercises open()/creat(), write(), read validation, stat(). It integrates with tests.h/unixdos.h and the shared SUBR implementation or object.

Risks: generated path casing is inconsistent, especially the debug SUBR object path in many projects; stale SUBR.OBJ can make tests link against old helper behavior; /W0 hides compiler warnings; generated files target old MSVC flags such as /GX and /ML.

Test signals: build success is production of the executable and optional browser database. Runtime success must be observed by launching the executable and checking for the per-test "ok" line from complete().
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/basic/console/test5a.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/basic/console/test5b.mak -->
# sources/test-tools/cthon04/basic/console/test5b.mak

Purpose: Visual C++ 2.0 NMAKE project for the Win32 console build of test5b, the Connectathon basic read path test.

Important APIs/types/functions: this is generated make syntax, not C code. Key macros are CFG, CPP, RSC, OUTDIR, INTDIR, CPP_PROJ, BSC32_FLAGS, LINK32_FLAGS, and LINK32_OBJS. It builds ..\TEST5B.C plus the shared support object; links against .\WinRel\SUBR.OBJ and .\WINDEBUG\SUBR.OBJ rather than compiling SUBR.C in this project. The linked executable is test5b.exe/upper-case variant under WinRel or WinDebug.

Control flow: CFG defaults to "Win32 Debug", validates Release/Debug, creates the output directory, compiles C sources with cl.exe into WinRel or WinDebug, optionally emits browser .SBR/.BSC files with bscmake.exe, and links with link.exe as a console subsystem target.

State and persistence behavior: creates build products under local WinRel/WinDebug directories: .OBJ, .SBR, .BSC, .PDB, and .EXE. It does not run the test or manage NFSTESTDIR; runtime filesystem changes come from the built C program.

Dependencies and integration points: depends on Microsoft Visual C++ command-line tools and Win32 system libraries. The source program exercises open(), read(), optional mmap/msync, unlink(). It integrates with tests.h/unixdos.h and the shared SUBR implementation or object.

Risks: generated path casing is inconsistent, especially the debug SUBR object path in many projects; stale SUBR.OBJ can make tests link against old helper behavior; /W0 hides compiler warnings; generated files target old MSVC flags such as /GX and /ML.

Test signals: build success is production of the executable and optional browser database. Runtime success must be observed by launching the executable and checking for the per-test "ok" line from complete().
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/basic/console/test5b.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/basic/console/test6.mak -->
# sources/test-tools/cthon04/basic/console/test6.mak

Purpose: Visual C++ 2.0 NMAKE project for the Win32 console build of test6, the Connectathon basic readdir test.

Important APIs/types/functions: this is generated make syntax, not C code. Key macros are CFG, CPP, RSC, OUTDIR, INTDIR, CPP_PROJ, BSC32_FLAGS, LINK32_FLAGS, and LINK32_OBJS. It builds ..\TEST6.C plus the shared support object; links against .\WinRel\SUBR.OBJ and .\WINDEBUG\SUBR.OBJ rather than compiling SUBR.C in this project. The linked executable is test6.exe/upper-case variant under WinRel or WinDebug.

Control flow: CFG defaults to "Win32 Debug", validates Release/Debug, creates the output directory, compiles C sources with cl.exe into WinRel or WinDebug, optionally emits browser .SBR/.BSC files with bscmake.exe, and links with link.exe as a console subsystem target.

State and persistence behavior: creates build products under local WinRel/WinDebug directories: .OBJ, .SBR, .BSC, .PDB, and .EXE. It does not run the test or manage NFSTESTDIR; runtime filesystem changes come from the built C program.

Dependencies and integration points: depends on Microsoft Visual C++ command-line tools and Win32 system libraries. The source program exercises opendir(), rewinddir(), readdir(), closedir(), unlink(). It integrates with tests.h/unixdos.h and the shared SUBR implementation or object.

Risks: generated path casing is inconsistent, especially the debug SUBR object path in many projects; stale SUBR.OBJ can make tests link against old helper behavior; /W0 hides compiler warnings; generated files target old MSVC flags such as /GX and /ML.

Test signals: build success is production of the executable and optional browser database. Runtime success must be observed by launching the executable and checking for the per-test "ok" line from complete().
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/basic/console/test6.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/basic/console/test7.mak -->
# sources/test-tools/cthon04/basic/console/test7.mak

Purpose: Visual C++ 2.0 NMAKE project for the Win32 console build of test7, the Connectathon basic rename and link test.

Important APIs/types/functions: this is generated make syntax, not C code. Key macros are CFG, CPP, RSC, OUTDIR, INTDIR, CPP_PROJ, BSC32_FLAGS, LINK32_FLAGS, and LINK32_OBJS. It builds ..\TEST7.C plus the shared support object; links against .\WinRel\SUBR.OBJ and .\WINDEBUG\SUBR.OBJ rather than compiling SUBR.C in this project. The linked executable is test7.exe/upper-case variant under WinRel or WinDebug.

Control flow: CFG defaults to "Win32 Debug", validates Release/Debug, creates the output directory, compiles C sources with cl.exe into WinRel or WinDebug, optionally emits browser .SBR/.BSC files with bscmake.exe, and links with link.exe as a console subsystem target.

State and persistence behavior: creates build products under local WinRel/WinDebug directories: .OBJ, .SBR, .BSC, .PDB, and .EXE. It does not run the test or manage NFSTESTDIR; runtime filesystem changes come from the built C program.

Dependencies and integration points: depends on Microsoft Visual C++ command-line tools and Win32 system libraries. The source program exercises rename(), link(), unlink(), stat(). It integrates with tests.h/unixdos.h and the shared SUBR implementation or object.

Risks: generated path casing is inconsistent, especially the debug SUBR object path in many projects; stale SUBR.OBJ can make tests link against old helper behavior; /W0 hides compiler warnings; generated files target old MSVC flags such as /GX and /ML.

Test signals: build success is production of the executable and optional browser database. Runtime success must be observed by launching the executable and checking for the per-test "ok" line from complete().
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/basic/console/test7.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/basic/console/test7a.mak -->
# sources/test-tools/cthon04/basic/console/test7a.mak

Purpose: Visual C++ 2.0 NMAKE project for the Win32 console build of test7a, the Connectathon basic rename test.

Important APIs/types/functions: this is generated make syntax, not C code. Key macros are CFG, CPP, RSC, OUTDIR, INTDIR, CPP_PROJ, BSC32_FLAGS, LINK32_FLAGS, and LINK32_OBJS. It builds ..\TEST7A.C plus the shared support object; links against .\WinRel\SUBR.OBJ and .\WINDEBUG\SUBR.OBJ rather than compiling SUBR.C in this project. The linked executable is test7a.exe/upper-case variant under WinRel or WinDebug.

Control flow: CFG defaults to "Win32 Debug", validates Release/Debug, creates the output directory, compiles C sources with cl.exe into WinRel or WinDebug, optionally emits browser .SBR/.BSC files with bscmake.exe, and links with link.exe as a console subsystem target.

State and persistence behavior: creates build products under local WinRel/WinDebug directories: .OBJ, .SBR, .BSC, .PDB, and .EXE. It does not run the test or manage NFSTESTDIR; runtime filesystem changes come from the built C program.

Dependencies and integration points: depends on Microsoft Visual C++ command-line tools and Win32 system libraries. The source program exercises rename(), stat(), rmdirtree(). It integrates with tests.h/unixdos.h and the shared SUBR implementation or object.

Risks: generated path casing is inconsistent, especially the debug SUBR object path in many projects; stale SUBR.OBJ can make tests link against old helper behavior; /W0 hides compiler warnings; generated files target old MSVC flags such as /GX and /ML.

Test signals: build success is production of the executable and optional browser database. Runtime success must be observed by launching the executable and checking for the per-test "ok" line from complete().
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/basic/console/test7a.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/basic/console/test7b.mak -->
# sources/test-tools/cthon04/basic/console/test7b.mak

Purpose: Visual C++ 2.0 NMAKE project for the Win32 console build of test7b, the Connectathon basic link test.

Important APIs/types/functions: this is generated make syntax, not C code. Key macros are CFG, CPP, RSC, OUTDIR, INTDIR, CPP_PROJ, BSC32_FLAGS, LINK32_FLAGS, and LINK32_OBJS. It builds ..\TEST7B.C plus the shared support object; links against .\WinRel\SUBR.OBJ and .\WINDEBUG\SUBR.OBJ rather than compiling SUBR.C in this project. The linked executable is test7b.exe/upper-case variant under WinRel or WinDebug.

Control flow: CFG defaults to "Win32 Debug", validates Release/Debug, creates the output directory, compiles C sources with cl.exe into WinRel or WinDebug, optionally emits browser .SBR/.BSC files with bscmake.exe, and links with link.exe as a console subsystem target.

State and persistence behavior: creates build products under local WinRel/WinDebug directories: .OBJ, .SBR, .BSC, .PDB, and .EXE. It does not run the test or manage NFSTESTDIR; runtime filesystem changes come from the built C program.

Dependencies and integration points: depends on Microsoft Visual C++ command-line tools and Win32 system libraries. The source program exercises link(), unlink(), stat(); rename fallback on DOS/Win32. It integrates with tests.h/unixdos.h and the shared SUBR implementation or object.

Risks: generated path casing is inconsistent, especially the debug SUBR object path in many projects; stale SUBR.OBJ can make tests link against old helper behavior; /W0 hides compiler warnings; generated files target old MSVC flags such as /GX and /ML.

Test signals: build success is production of the executable and optional browser database. Runtime success must be observed by launching the executable and checking for the per-test "ok" line from complete().
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/basic/console/test7b.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/basic/console/test8.mak -->
# sources/test-tools/cthon04/basic/console/test8.mak

Purpose: Visual C++ 2.0 NMAKE project for the Win32 console build of test8, the Connectathon basic symlink and readlink test.

Important APIs/types/functions: this is generated make syntax, not C code. Key macros are CFG, CPP, RSC, OUTDIR, INTDIR, CPP_PROJ, BSC32_FLAGS, LINK32_FLAGS, and LINK32_OBJS. It builds ..\TEST8.C plus the shared support object; links against .\WinRel\SUBR.OBJ and .\WINDEBUG\SUBR.OBJ rather than compiling SUBR.C in this project. The linked executable is test8.exe/upper-case variant under WinRel or WinDebug.

Control flow: CFG defaults to "Win32 Debug", validates Release/Debug, creates the output directory, compiles C sources with cl.exe into WinRel or WinDebug, optionally emits browser .SBR/.BSC files with bscmake.exe, and links with link.exe as a console subsystem target.

State and persistence behavior: creates build products under local WinRel/WinDebug directories: .OBJ, .SBR, .BSC, .PDB, and .EXE. It does not run the test or manage NFSTESTDIR; runtime filesystem changes come from the built C program.

Dependencies and integration points: depends on Microsoft Visual C++ command-line tools and Win32 system libraries. The source program exercises symlink(), lstat(), readlink(), unlink(). It integrates with tests.h/unixdos.h and the shared SUBR implementation or object.

Risks: generated path casing is inconsistent, especially the debug SUBR object path in many projects; stale SUBR.OBJ can make tests link against old helper behavior; /W0 hides compiler warnings; generated files target old MSVC flags such as /GX and /ML.

Test signals: build success is production of the executable and optional browser database. Runtime success must be observed by launching the executable and checking for the per-test "ok" line from complete().
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/basic/console/test8.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/basic/console/test9.mak -->
# sources/test-tools/cthon04/basic/console/test9.mak

Purpose: Visual C++ 2.0 NMAKE project for the Win32 console build of test9, the Connectathon basic statfs/statvfs test.

Important APIs/types/functions: this is generated make syntax, not C code. Key macros are CFG, CPP, RSC, OUTDIR, INTDIR, CPP_PROJ, BSC32_FLAGS, LINK32_FLAGS, and LINK32_OBJS. It builds ..\TEST9.C plus the shared support object; links against .\WinRel\SUBR.OBJ and .\WINDEBUG\SUBR.OBJ rather than compiling SUBR.C in this project. The linked executable is test9.exe/upper-case variant under WinRel or WinDebug.

Control flow: CFG defaults to "Win32 Debug", validates Release/Debug, creates the output directory, compiles C sources with cl.exe into WinRel or WinDebug, optionally emits browser .SBR/.BSC files with bscmake.exe, and links with link.exe as a console subsystem target.

State and persistence behavior: creates build products under local WinRel/WinDebug directories: .OBJ, .SBR, .BSC, .PDB, and .EXE. It does not run the test or manage NFSTESTDIR; runtime filesystem changes come from the built C program.

Dependencies and integration points: depends on Microsoft Visual C++ command-line tools and Win32 system libraries. The source program exercises statfs() or statvfs(). It integrates with tests.h/unixdos.h and the shared SUBR implementation or object.

Risks: generated path casing is inconsistent, especially the debug SUBR object path in many projects; stale SUBR.OBJ can make tests link against old helper behavior; /W0 hides compiler warnings; generated files target old MSVC flags such as /GX and /ML.

Test signals: build success is production of the executable and optional browser database. Runtime success must be observed by launching the executable and checking for the per-test "ok" line from complete().
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/basic/console/test9.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/basic/dos/test1.mak -->
# sources/test-tools/cthon04/basic/dos/test1.mak

Purpose: external Microsoft Visual C++ DOS makefile for TEST1, the DOS build of the Connectathon basic file and directory creation test.

Important APIs/types/functions: defines PROJ=TEST1, DEBUG, compiler/linker variables, CFLAGS_D_DEXE/CFLAGS_R_DEXE, LFLAGS_D_DEXE/LFLAGS_R_DEXE, oldnames/mlibce libraries, SBRS browser sources, and explicit .OBJ rules. It builds SUBR.C, then TEST1.C.

Control flow: selects debug or release flags from DEBUG, removes any stale MSVC.BND file, compiles the test source with cl, writes a LINK command response file $(PROJ).CRF, links $(PROJ).EXE, provides a run target, and builds $(PROJ).BSC with bscmake.

State and persistence behavior: creates DOS build artifacts in the makefile directory: .OBJ, .SBR, .PDB for debug, .CRF response file, .EXE, and .BSC. It does not create or clean the runtime test directory itself.

Dependencies and integration points: depends on the historical 16-bit/DOS Microsoft C toolchain, oldnames and mlibce libraries, ..\..\lib and ..\..\include search paths, tests.h, unixdos.h, and the shared SUBR object. The executable exercises dirtree(), creat(), mkdir/chdir wrappers through DOS compatibility wrappers where needed.

Risks: SUBR.OBJ is external for all but test1, so build order matters; fixed stack size and memory-model flags are legacy; response-file paths are relative and fragile; the makefile is generated and marked do not modify.

Test signals: build success is an executable plus browser database. Runtime pass/fail is the program's stdout/stderr summary and final "ok" marker.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/basic/dos/test1.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/basic/dos/test2.mak -->
# sources/test-tools/cthon04/basic/dos/test2.mak

Purpose: external Microsoft Visual C++ DOS makefile for TEST2, the DOS build of the Connectathon basic file and directory removal test.

Important APIs/types/functions: defines PROJ=TEST2, DEBUG, compiler/linker variables, CFLAGS_D_DEXE/CFLAGS_R_DEXE, LFLAGS_D_DEXE/LFLAGS_R_DEXE, oldnames/mlibce libraries, SBRS browser sources, and explicit .OBJ rules. It builds TEST2.C with SUBR.OBJ supplied as OBJS_EXT.

Control flow: selects debug or release flags from DEBUG, removes any stale MSVC.BND file, compiles the test source with cl, writes a LINK command response file $(PROJ).CRF, links $(PROJ).EXE, provides a run target, and builds $(PROJ).BSC with bscmake.

State and persistence behavior: creates DOS build artifacts in the makefile directory: .OBJ, .SBR, .PDB for debug, .CRF response file, .EXE, and .BSC. It does not create or clean the runtime test directory itself.

Dependencies and integration points: depends on the historical 16-bit/DOS Microsoft C toolchain, oldnames and mlibce libraries, ..\..\lib and ..\..\include search paths, tests.h, unixdos.h, and the shared SUBR object. The executable exercises rmdirtree(), unlink(), rmdir(), system("test1 -s ...") through DOS compatibility wrappers where needed.

Risks: SUBR.OBJ is external for all but test1, so build order matters; fixed stack size and memory-model flags are legacy; response-file paths are relative and fragile; the makefile is generated and marked do not modify.

Test signals: build success is an executable plus browser database. Runtime pass/fail is the program's stdout/stderr summary and final "ok" marker.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/basic/dos/test2.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/basic/dos/test3.mak -->
# sources/test-tools/cthon04/basic/dos/test3.mak

Purpose: external Microsoft Visual C++ DOS makefile for TEST3, the DOS build of the Connectathon basic lookup across mount points test.

Important APIs/types/functions: defines PROJ=TEST3, DEBUG, compiler/linker variables, CFLAGS_D_DEXE/CFLAGS_R_DEXE, LFLAGS_D_DEXE/LFLAGS_R_DEXE, oldnames/mlibce libraries, SBRS browser sources, and explicit .OBJ rules. It builds TEST3.C with SUBR.OBJ supplied as OBJS_EXT.

Control flow: selects debug or release flags from DEBUG, removes any stale MSVC.BND file, compiles the test source with cl, writes a LINK command response file $(PROJ).CRF, links $(PROJ).EXE, provides a run target, and builds $(PROJ).BSC with bscmake.

State and persistence behavior: creates DOS build artifacts in the makefile directory: .OBJ, .SBR, .PDB for debug, .CRF response file, .EXE, and .BSC. It does not create or clean the runtime test directory itself.

Dependencies and integration points: depends on the historical 16-bit/DOS Microsoft C toolchain, oldnames and mlibce libraries, ..\..\lib and ..\..\include search paths, tests.h, unixdos.h, and the shared SUBR object. The executable exercises getcwd(), stat() through DOS compatibility wrappers where needed.

Risks: SUBR.OBJ is external for all but test1, so build order matters; fixed stack size and memory-model flags are legacy; response-file paths are relative and fragile; the makefile is generated and marked do not modify.

Test signals: build success is an executable plus browser database. Runtime pass/fail is the program's stdout/stderr summary and final "ok" marker.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/basic/dos/test3.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/basic/dos/test4.mak -->
# sources/test-tools/cthon04/basic/dos/test4.mak

Purpose: external Microsoft Visual C++ DOS makefile for TEST4, the DOS build of the Connectathon basic setattr/getattr/lookup test.

Important APIs/types/functions: defines PROJ=TEST4, DEBUG, compiler/linker variables, CFLAGS_D_DEXE/CFLAGS_R_DEXE, LFLAGS_D_DEXE/LFLAGS_R_DEXE, oldnames/mlibce libraries, SBRS browser sources, and explicit .OBJ rules. It builds TEST4.C with SUBR.OBJ supplied as OBJS_EXT.

Control flow: selects debug or release flags from DEBUG, removes any stale MSVC.BND file, compiles the test source with cl, writes a LINK command response file $(PROJ).CRF, links $(PROJ).EXE, provides a run target, and builds $(PROJ).BSC with bscmake.

State and persistence behavior: creates DOS build artifacts in the makefile directory: .OBJ, .SBR, .PDB for debug, .CRF response file, .EXE, and .BSC. It does not create or clean the runtime test directory itself.

Dependencies and integration points: depends on the historical 16-bit/DOS Microsoft C toolchain, oldnames and mlibce libraries, ..\..\lib and ..\..\include search paths, tests.h, unixdos.h, and the shared SUBR object. The executable exercises chmod(), stat(), dirtree() through DOS compatibility wrappers where needed.

Risks: SUBR.OBJ is external for all but test1, so build order matters; fixed stack size and memory-model flags are legacy; response-file paths are relative and fragile; the makefile is generated and marked do not modify.

Test signals: build success is an executable plus browser database. Runtime pass/fail is the program's stdout/stderr summary and final "ok" marker.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/basic/dos/test4.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/basic/dos/test4a.mak -->
# sources/test-tools/cthon04/basic/dos/test4a.mak

Purpose: external Microsoft Visual C++ DOS makefile for TEST4A, the DOS build of the Connectathon basic getattr/lookup test.

Important APIs/types/functions: defines PROJ=TEST4A, DEBUG, compiler/linker variables, CFLAGS_D_DEXE/CFLAGS_R_DEXE, LFLAGS_D_DEXE/LFLAGS_R_DEXE, oldnames/mlibce libraries, SBRS browser sources, and explicit .OBJ rules. It builds TEST4A.C with SUBR.OBJ supplied as OBJS_EXT.

Control flow: selects debug or release flags from DEBUG, removes any stale MSVC.BND file, compiles the test source with cl, writes a LINK command response file $(PROJ).CRF, links $(PROJ).EXE, provides a run target, and builds $(PROJ).BSC with bscmake.

State and persistence behavior: creates DOS build artifacts in the makefile directory: .OBJ, .SBR, .PDB for debug, .CRF response file, .EXE, and .BSC. It does not create or clean the runtime test directory itself.

Dependencies and integration points: depends on the historical 16-bit/DOS Microsoft C toolchain, oldnames and mlibce libraries, ..\..\lib and ..\..\include search paths, tests.h, unixdos.h, and the shared SUBR object. The executable exercises stat(), dirtree() through DOS compatibility wrappers where needed.

Risks: SUBR.OBJ is external for all but test1, so build order matters; fixed stack size and memory-model flags are legacy; response-file paths are relative and fragile; the makefile is generated and marked do not modify.

Test signals: build success is an executable plus browser database. Runtime pass/fail is the program's stdout/stderr summary and final "ok" marker.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/basic/dos/test4a.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/basic/dos/test5.mak -->
# sources/test-tools/cthon04/basic/dos/test5.mak

Purpose: external Microsoft Visual C++ DOS makefile for TEST5, the DOS build of the Connectathon basic read and write test.

Important APIs/types/functions: defines PROJ=TEST5, DEBUG, compiler/linker variables, CFLAGS_D_DEXE/CFLAGS_R_DEXE, LFLAGS_D_DEXE/LFLAGS_R_DEXE, oldnames/mlibce libraries, SBRS browser sources, and explicit .OBJ rules. It builds TEST5.C with SUBR.OBJ supplied as OBJS_EXT.

Control flow: selects debug or release flags from DEBUG, removes any stale MSVC.BND file, compiles the test source with cl, writes a LINK command response file $(PROJ).CRF, links $(PROJ).EXE, provides a run target, and builds $(PROJ).BSC with bscmake.

State and persistence behavior: creates DOS build artifacts in the makefile directory: .OBJ, .SBR, .PDB for debug, .CRF response file, .EXE, and .BSC. It does not create or clean the runtime test directory itself.

Dependencies and integration points: depends on the historical 16-bit/DOS Microsoft C toolchain, oldnames and mlibce libraries, ..\..\lib and ..\..\include search paths, tests.h, unixdos.h, and the shared SUBR object. The executable exercises open()/creat(), write(), read(), stat(), optional mmap/msync through DOS compatibility wrappers where needed.

Risks: SUBR.OBJ is external for all but test1, so build order matters; fixed stack size and memory-model flags are legacy; response-file paths are relative and fragile; the makefile is generated and marked do not modify.

Test signals: build success is an executable plus browser database. Runtime pass/fail is the program's stdout/stderr summary and final "ok" marker.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/basic/dos/test5.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/basic/dos/test5a.mak -->
# sources/test-tools/cthon04/basic/dos/test5a.mak

Purpose: external Microsoft Visual C++ DOS makefile for TEST5A, the DOS build of the Connectathon basic write path test.

Important APIs/types/functions: defines PROJ=TEST5A, DEBUG, compiler/linker variables, CFLAGS_D_DEXE/CFLAGS_R_DEXE, LFLAGS_D_DEXE/LFLAGS_R_DEXE, oldnames/mlibce libraries, SBRS browser sources, and explicit .OBJ rules. It builds TEST5A.C with SUBR.OBJ supplied as OBJS_EXT.

Control flow: selects debug or release flags from DEBUG, removes any stale MSVC.BND file, compiles the test source with cl, writes a LINK command response file $(PROJ).CRF, links $(PROJ).EXE, provides a run target, and builds $(PROJ).BSC with bscmake.

State and persistence behavior: creates DOS build artifacts in the makefile directory: .OBJ, .SBR, .PDB for debug, .CRF response file, .EXE, and .BSC. It does not create or clean the runtime test directory itself.

Dependencies and integration points: depends on the historical 16-bit/DOS Microsoft C toolchain, oldnames and mlibce libraries, ..\..\lib and ..\..\include search paths, tests.h, unixdos.h, and the shared SUBR object. The executable exercises open()/creat(), write(), read validation, stat() through DOS compatibility wrappers where needed.

Risks: SUBR.OBJ is external for all but test1, so build order matters; fixed stack size and memory-model flags are legacy; response-file paths are relative and fragile; the makefile is generated and marked do not modify.

Test signals: build success is an executable plus browser database. Runtime pass/fail is the program's stdout/stderr summary and final "ok" marker.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/basic/dos/test5a.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/basic/dos/test5b.mak -->
# sources/test-tools/cthon04/basic/dos/test5b.mak

Purpose: external Microsoft Visual C++ DOS makefile for TEST5B, the DOS build of the Connectathon basic read path test.

Important APIs/types/functions: defines PROJ=TEST5B, DEBUG, compiler/linker variables, CFLAGS_D_DEXE/CFLAGS_R_DEXE, LFLAGS_D_DEXE/LFLAGS_R_DEXE, oldnames/mlibce libraries, SBRS browser sources, and explicit .OBJ rules. It builds TEST5B.C with SUBR.OBJ supplied as OBJS_EXT.

Control flow: selects debug or release flags from DEBUG, removes any stale MSVC.BND file, compiles the test source with cl, writes a LINK command response file $(PROJ).CRF, links $(PROJ).EXE, provides a run target, and builds $(PROJ).BSC with bscmake.

State and persistence behavior: creates DOS build artifacts in the makefile directory: .OBJ, .SBR, .PDB for debug, .CRF response file, .EXE, and .BSC. It does not create or clean the runtime test directory itself.

Dependencies and integration points: depends on the historical 16-bit/DOS Microsoft C toolchain, oldnames and mlibce libraries, ..\..\lib and ..\..\include search paths, tests.h, unixdos.h, and the shared SUBR object. The executable exercises open(), read(), optional mmap/msync, unlink() through DOS compatibility wrappers where needed.

Risks: SUBR.OBJ is external for all but test1, so build order matters; fixed stack size and memory-model flags are legacy; response-file paths are relative and fragile; the makefile is generated and marked do not modify.

Test signals: build success is an executable plus browser database. Runtime pass/fail is the program's stdout/stderr summary and final "ok" marker.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/basic/dos/test5b.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/basic/dos/test6.mak -->
# sources/test-tools/cthon04/basic/dos/test6.mak

Purpose: external Microsoft Visual C++ DOS makefile for TEST6, the DOS build of the Connectathon basic readdir test.

Important APIs/types/functions: defines PROJ=TEST6, DEBUG, compiler/linker variables, CFLAGS_D_DEXE/CFLAGS_R_DEXE, LFLAGS_D_DEXE/LFLAGS_R_DEXE, oldnames/mlibce libraries, SBRS browser sources, and explicit .OBJ rules. It builds TEST6.C with SUBR.OBJ supplied as OBJS_EXT.

Control flow: selects debug or release flags from DEBUG, removes any stale MSVC.BND file, compiles the test source with cl, writes a LINK command response file $(PROJ).CRF, links $(PROJ).EXE, provides a run target, and builds $(PROJ).BSC with bscmake.

State and persistence behavior: creates DOS build artifacts in the makefile directory: .OBJ, .SBR, .PDB for debug, .CRF response file, .EXE, and .BSC. It does not create or clean the runtime test directory itself.

Dependencies and integration points: depends on the historical 16-bit/DOS Microsoft C toolchain, oldnames and mlibce libraries, ..\..\lib and ..\..\include search paths, tests.h, unixdos.h, and the shared SUBR object. The executable exercises opendir(), rewinddir(), readdir(), closedir(), unlink() through DOS compatibility wrappers where needed.

Risks: SUBR.OBJ is external for all but test1, so build order matters; fixed stack size and memory-model flags are legacy; response-file paths are relative and fragile; the makefile is generated and marked do not modify.

Test signals: build success is an executable plus browser database. Runtime pass/fail is the program's stdout/stderr summary and final "ok" marker.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/basic/dos/test6.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/basic/dos/test7.mak -->
# sources/test-tools/cthon04/basic/dos/test7.mak

Purpose: external Microsoft Visual C++ DOS makefile for TEST7, the DOS build of the Connectathon basic rename and link test.

Important APIs/types/functions: defines PROJ=TEST7, DEBUG, compiler/linker variables, CFLAGS_D_DEXE/CFLAGS_R_DEXE, LFLAGS_D_DEXE/LFLAGS_R_DEXE, oldnames/mlibce libraries, SBRS browser sources, and explicit .OBJ rules. It builds TEST7.C with SUBR.OBJ supplied as OBJS_EXT.

Control flow: selects debug or release flags from DEBUG, removes any stale MSVC.BND file, compiles the test source with cl, writes a LINK command response file $(PROJ).CRF, links $(PROJ).EXE, provides a run target, and builds $(PROJ).BSC with bscmake.

State and persistence behavior: creates DOS build artifacts in the makefile directory: .OBJ, .SBR, .PDB for debug, .CRF response file, .EXE, and .BSC. It does not create or clean the runtime test directory itself.

Dependencies and integration points: depends on the historical 16-bit/DOS Microsoft C toolchain, oldnames and mlibce libraries, ..\..\lib and ..\..\include search paths, tests.h, unixdos.h, and the shared SUBR object. The executable exercises rename(), link(), unlink(), stat() through DOS compatibility wrappers where needed.

Risks: SUBR.OBJ is external for all but test1, so build order matters; fixed stack size and memory-model flags are legacy; response-file paths are relative and fragile; the makefile is generated and marked do not modify.

Test signals: build success is an executable plus browser database. Runtime pass/fail is the program's stdout/stderr summary and final "ok" marker.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/basic/dos/test7.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/basic/dos/test7a.mak -->
# sources/test-tools/cthon04/basic/dos/test7a.mak

Purpose: external Microsoft Visual C++ DOS makefile for TEST7A, the DOS build of the Connectathon basic rename test.

Important APIs/types/functions: defines PROJ=TEST7A, DEBUG, compiler/linker variables, CFLAGS_D_DEXE/CFLAGS_R_DEXE, LFLAGS_D_DEXE/LFLAGS_R_DEXE, oldnames/mlibce libraries, SBRS browser sources, and explicit .OBJ rules. It builds TEST7A.C with SUBR.OBJ supplied as OBJS_EXT.

Control flow: selects debug or release flags from DEBUG, removes any stale MSVC.BND file, compiles the test source with cl, writes a LINK command response file $(PROJ).CRF, links $(PROJ).EXE, provides a run target, and builds $(PROJ).BSC with bscmake.

State and persistence behavior: creates DOS build artifacts in the makefile directory: .OBJ, .SBR, .PDB for debug, .CRF response file, .EXE, and .BSC. It does not create or clean the runtime test directory itself.

Dependencies and integration points: depends on the historical 16-bit/DOS Microsoft C toolchain, oldnames and mlibce libraries, ..\..\lib and ..\..\include search paths, tests.h, unixdos.h, and the shared SUBR object. The executable exercises rename(), stat(), rmdirtree() through DOS compatibility wrappers where needed.

Risks: SUBR.OBJ is external for all but test1, so build order matters; fixed stack size and memory-model flags are legacy; response-file paths are relative and fragile; the makefile is generated and marked do not modify.

Test signals: build success is an executable plus browser database. Runtime pass/fail is the program's stdout/stderr summary and final "ok" marker.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/basic/dos/test7a.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/basic/dos/test7b.mak -->
# sources/test-tools/cthon04/basic/dos/test7b.mak

Purpose: external Microsoft Visual C++ DOS makefile for TEST7B, the DOS build of the Connectathon basic link test.

Important APIs/types/functions: defines PROJ=TEST7B, DEBUG, compiler/linker variables, CFLAGS_D_DEXE/CFLAGS_R_DEXE, LFLAGS_D_DEXE/LFLAGS_R_DEXE, oldnames/mlibce libraries, SBRS browser sources, and explicit .OBJ rules. It builds TEST7B.C with SUBR.OBJ supplied as OBJS_EXT.

Control flow: selects debug or release flags from DEBUG, removes any stale MSVC.BND file, compiles the test source with cl, writes a LINK command response file $(PROJ).CRF, links $(PROJ).EXE, provides a run target, and builds $(PROJ).BSC with bscmake.

State and persistence behavior: creates DOS build artifacts in the makefile directory: .OBJ, .SBR, .PDB for debug, .CRF response file, .EXE, and .BSC. It does not create or clean the runtime test directory itself.

Dependencies and integration points: depends on the historical 16-bit/DOS Microsoft C toolchain, oldnames and mlibce libraries, ..\..\lib and ..\..\include search paths, tests.h, unixdos.h, and the shared SUBR object. The executable exercises link(), unlink(), stat(); rename fallback on DOS/Win32 through DOS compatibility wrappers where needed.

Risks: SUBR.OBJ is external for all but test1, so build order matters; fixed stack size and memory-model flags are legacy; response-file paths are relative and fragile; the makefile is generated and marked do not modify.

Test signals: build success is an executable plus browser database. Runtime pass/fail is the program's stdout/stderr summary and final "ok" marker.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/basic/dos/test7b.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/basic/dos/test8.mak -->
# sources/test-tools/cthon04/basic/dos/test8.mak

Purpose: external Microsoft Visual C++ DOS makefile for TEST8, the DOS build of the Connectathon basic symlink and readlink test.

Important APIs/types/functions: defines PROJ=TEST8, DEBUG, compiler/linker variables, CFLAGS_D_DEXE/CFLAGS_R_DEXE, LFLAGS_D_DEXE/LFLAGS_R_DEXE, oldnames/mlibce libraries, SBRS browser sources, and explicit .OBJ rules. It builds TEST8.C with SUBR.OBJ supplied as OBJS_EXT.

Control flow: selects debug or release flags from DEBUG, removes any stale MSVC.BND file, compiles the test source with cl, writes a LINK command response file $(PROJ).CRF, links $(PROJ).EXE, provides a run target, and builds $(PROJ).BSC with bscmake.

State and persistence behavior: creates DOS build artifacts in the makefile directory: .OBJ, .SBR, .PDB for debug, .CRF response file, .EXE, and .BSC. It does not create or clean the runtime test directory itself.

Dependencies and integration points: depends on the historical 16-bit/DOS Microsoft C toolchain, oldnames and mlibce libraries, ..\..\lib and ..\..\include search paths, tests.h, unixdos.h, and the shared SUBR object. The executable exercises symlink(), lstat(), readlink(), unlink() through DOS compatibility wrappers where needed.

Risks: SUBR.OBJ is external for all but test1, so build order matters; fixed stack size and memory-model flags are legacy; response-file paths are relative and fragile; the makefile is generated and marked do not modify.

Test signals: build success is an executable plus browser database. Runtime pass/fail is the program's stdout/stderr summary and final "ok" marker.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/basic/dos/test8.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/basic/dos/test9.mak -->
# sources/test-tools/cthon04/basic/dos/test9.mak

Purpose: external Microsoft Visual C++ DOS makefile for TEST9, the DOS build of the Connectathon basic statfs/statvfs test.

Important APIs/types/functions: defines PROJ=TEST9, DEBUG, compiler/linker variables, CFLAGS_D_DEXE/CFLAGS_R_DEXE, LFLAGS_D_DEXE/LFLAGS_R_DEXE, oldnames/mlibce libraries, SBRS browser sources, and explicit .OBJ rules. It builds TEST9.C with SUBR.OBJ supplied as OBJS_EXT.

Control flow: selects debug or release flags from DEBUG, removes any stale MSVC.BND file, compiles the test source with cl, writes a LINK command response file $(PROJ).CRF, links $(PROJ).EXE, provides a run target, and builds $(PROJ).BSC with bscmake.

State and persistence behavior: creates DOS build artifacts in the makefile directory: .OBJ, .SBR, .PDB for debug, .CRF response file, .EXE, and .BSC. It does not create or clean the runtime test directory itself.

Dependencies and integration points: depends on the historical 16-bit/DOS Microsoft C toolchain, oldnames and mlibce libraries, ..\..\lib and ..\..\include search paths, tests.h, unixdos.h, and the shared SUBR object. The executable exercises statfs() or statvfs() through DOS compatibility wrappers where needed.

Risks: SUBR.OBJ is external for all but test1, so build order matters; fixed stack size and memory-model flags are legacy; response-file paths are relative and fragile; the makefile is generated and marked do not modify.

Test signals: build success is an executable plus browser database. Runtime pass/fail is the program's stdout/stderr summary and final "ok" marker.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/basic/dos/test9.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/basic/subr.c -->
# sources/test-tools/cthon04/basic/subr.c

Purpose: shared support library for the basic Connectathon filesystem tests. It owns test-directory setup, recursive tree creation/removal, timing, error reporting, argument parsing helpers, success exit, and DOS/Win32 compatibility shims.

Important APIs/types/functions: exports Myname and Dflag, dirtree(), rmdirtree(), error(), starttime(), endtime(), testdir(), mtestdir(), getparm(), complete(), unix_chdir(), unix_mkdir(), and compatibility replacements for lstat(), gettimeofday(), statfs(), opendir()/readdir()/rewinddir()/closedir() on DOS/Win32. It depends on tests.h constants such as TESTDIR, CHMOD_RW, FNAME, DNAME, MAXPATHLEN, and DOSorWIN32.

Control flow: dirtree() recursively creates per-level files and directories, descending through unix_chdir() and returning via "..". rmdirtree() mirrors that traversal, unlinking known generated files before recursively removing generated directories. testdir() chooses an explicit directory, NFSTESTDIR, or TESTDIR, removes any old tree with rm -r/system or rmdir on WIN16, creates it, and chdirs into it. complete() prints the ok marker, restores any DOS/Win32 drive implied by Myname, and exits.

State and persistence: the helpers intentionally mutate the filesystem beneath the selected test directory. Timing is stored in static timeval globals ts/te. DOS/Win32 directory emulation uses global find state, one open directory at a time, and heap-allocated dirent lists that are not freed by closedir(). Dflag changes generated names to include level numbers.

Dependencies and integration points: all basic test programs link against this file or a prebuilt SUBR.OBJ. It bridges Unix syscalls and Microsoft C runtime calls, making the same tests usable from Unix makefiles, DOS makefiles, and Win32 NMAKE projects.

Risks: path construction uses fixed MAXPATHLEN buffers and sprintf; testdir() shells out to rm -r on a configurable path; directory emulation allocates a fixed 512-entry list; several compatibility routines assume DOS drive-letter paths and narrow 8.3 names. These are acceptable in the historical test harness but risky outside controlled test directories.

Test signals: successful callers print a per-test summary followed by "<program> ok.". Failures call error() with the current directory, preserve errno for perror(), and exit nonzero.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/basic/subr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/basic/test1.c -->
# sources/test-tools/cthon04/basic/test1.c

Purpose: basic create benchmark and correctness test for file/directory creation on the mounted filesystem.

Important APIs/types/functions: parses -h, -t, -f, -n plus optional levels/files/dirs/fname/dname. Uses getparm(), testdir()/mtestdir(), dirtree(), starttime(), endtime(), complete(), creat(), mkdir/chdir through subr.c.

Control flow: defaults to DLEVS/DFILS/DDIRS and FNAME/DNAME, validates that multi-level trees have at least one subdirectory per level, optionally shrinks to a 2x2 functionality run, enters the test directory, then delegates recursive creation to dirtree().

State and persistence: creates a tree under NFSTESTDIR or TESTDIR and intentionally leaves it in place for removal or later tests. Totals are maintained in local counters passed by pointer to dirtree().

Dependencies and integration points: compiled by Unix, DOS, and Win32 project files with subr.c; hidden -s mode suppresses non-error output for test2's setup path.

Risks: generated names use fixed buffers in subr.c; large levels/files/dirs values can create very large trees; -n assumes the directory already exists.

Test signals: reports created file/directory counts and optional elapsed time, then complete() prints the ok marker.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/basic/test1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/basic/test2.c -->
# sources/test-tools/cthon04/basic/test2.c

Purpose: removal counterpart for the create test; verifies unlink/rmdir behavior over a generated tree.

Important APIs/types/functions: parses -h, -t, -f, -n and tree shape/name arguments. Uses mtestdir(), system("test1 -s ...") for setup when needed, rmdirtree(), starttime(), endtime(), complete().

Control flow: after argument validation, the program tries to chdir into the test directory. If absent, it invokes test1 in silent mode with the same shape parameters, then retries. It times rmdirtree() over the tree and prints removal totals.

State and persistence: removes generated files/directories beneath the selected test directory. It does not remove the test directory itself; it clears known generated names.

Dependencies and integration points: depends on the test1 executable being discoverable by system() when the tree is missing, and on subr.c for traversal/removal policy.

Risks: setup command is built with sprintf into a 256-byte buffer and includes user-provided names; mismatched parameters can leave extra files that make rmdir fail.

Test signals: success is a removal count line followed by complete(); failures identify the current directory via error().
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/basic/test2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/basic/test3.c -->
# sources/test-tools/cthon04/basic/test3.c

Purpose: repeated lookup/getcwd/stat test intended to exercise directory lookup across the mounted test point.

Important APIs/types/functions: parses -h, -t, -f, -n plus count. Uses getcwd(), stat(), testdir()/mtestdir(), timing helpers, and complete().

Control flow: enters or reuses the test directory, optionally starts a timer, then loops count times calling getcwd() into MAXPATHLEN storage and stat() on the returned path.

State and persistence: aside from optional test-directory creation, the loop is read-only and leaves no files behind.

Dependencies and integration points: depends on tests.h for MAXPATHLEN and default TESTDIR; compiled with Unix headers or DOS/Win32 time compatibility.

Risks: assumes getcwd output fits MAXPATHLEN; -n requires an existing directory; failures are fatal at first missing cwd/stat.

Test signals: prints total getcwd/stat calls and optional elapsed time before complete().
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/basic/test3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/basic/test4.c -->
# sources/test-tools/cthon04/basic/test4.c

Purpose: setattr/getattr/lookup correctness and timing test over a flat set of files.

Important APIs/types/functions: parses -h, -t, -f, -n plus files/count/fname. Uses dirtree() to create files, chmod(), stat(), CHMOD_NONE, CHMOD_RW, CHMOD_MASK, and timing helpers.

Control flow: prepares the test directory, creates one level of files, then for each pass and file toggles permissions to the no-access mask, verifies stat mode, toggles to read/write, and verifies again.

State and persistence: creates files under the test directory and does not remove them at the end, leaving cleanup to later tests or external harness logic.

Dependencies and integration points: depends on subr.c and tests.h for mode masks that differ between Unix and DOS/Win32.

Risks: no cleanup in this file; chmod semantics vary on Windows and network filesystems; exits with status 0 on some chmod failures, which can weaken failure detection.

Test signals: reports chmod/stat operation count and exits via complete() after all mode checks pass.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/basic/test4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/basic/test4a.c -->
# sources/test-tools/cthon04/basic/test4a.c

Purpose: getattr/lookup-only variant of test4 for repeated stat calls without attribute mutation.

Important APIs/types/functions: parses -h, -t, -f, -n plus files/count/fname. Uses dirtree(), stat(), timing helpers, and complete().

Control flow: creates a flat file set, then loops count times over every generated file and calls stat() to ensure it remains visible.

State and persistence: creates files under the selected test directory and leaves them in place.

Dependencies and integration points: shares tests.h defaults and subr.c setup/tree helpers; useful as a lower-mutation comparison to test4.

Risks: summary text multiplies stats by two even though only one stat is performed per file/pass; path buffers are fixed MAXPATHLEN.

Test signals: any missing stat is fatal; success prints stat count and ok marker.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/basic/test4a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/basic/test5.c -->
# sources/test-tools/cthon04/basic/test5.c

Purpose: combined write/read throughput and data integrity test for a large file.

Important APIs/types/functions: parses -h, -t, -f, -n and optionally -s when O_SYNC exists, plus size/count/fname. Uses open()/creat(), write(), read(), stat(), close(), unlink(), optional mmap/msync/munmap, MIN(), BUFSZ, DSIZE.

Control flow: enters the test directory, initializes an integer pattern buffer, writes the target file count times with truncation and size checks, opens it once to verify pattern content, then times repeated full-file reads and unlinks it.

State and persistence: creates and deletes the chosen bigfile. During execution the file is repeatedly truncated and rewritten.

Dependencies and integration points: controlled by O_SYNC, MMAP, DOSorWIN32, and tests.h DCOUNT/CHMOD_RW. It is the producer/consumer superset for test5a and test5b style workloads.

Risks: validates only complete int slots in the final partial buffer; large sizes/counts can consume substantial server I/O; O_SYNC is disabled on Windows.

Test signals: validates file size after create/write, validates read-back buffer pattern once, reports write/read rates when timing is enabled, then complete().
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/basic/test5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/basic/test5a.c -->
# sources/test-tools/cthon04/basic/test5a.c

Purpose: write-focused large-file test with a read-back integrity check.

Important APIs/types/functions: same option model as test5, including optional -s for O_SYNC. Uses open()/creat(), write(), stat(), read(), optional mmap/msync, timing helpers, and complete().

Control flow: writes the target bigfile count times, verifying zero size after create/truncate and expected final size after close. It then opens the final file once and checks the integer pattern.

State and persistence: creates or overwrites bigfile and leaves it in the test directory for a later read-only test such as test5b.

Dependencies and integration points: complements test5b; both use the same BUFSZ/DSIZE defaults and tests.h DCOUNT.

Risks: leaves generated data behind by design; very large size/count values stress disk quota and cache behavior; pattern validation has the same partial-int limitation as test5.

Test signals: failure on create/write/close/stat/read mismatch; success reports bytes written and optional throughput, then complete().
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/basic/test5a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/basic/test5b.c -->
# sources/test-tools/cthon04/basic/test5b.c

Purpose: read-focused large-file test that assumes the target file already exists.

Important APIs/types/functions: parses -h, -t, -f, -n plus size/count/fname. Uses mtestdir(), open(O_RDONLY), read(), optional mmap/msync/munmap, unlink(), and timing helpers.

Control flow: moves into the existing test directory, repeatedly opens and reads size bytes from bigfile, closes each pass, prints read throughput, then unlinks the file.

State and persistence: consumes and removes the bigfile, usually one produced by test5a. It does not create fallback data.

Dependencies and integration points: paired with test5a in harness sequencing; DOS/Win32 adds O_BINARY to reads.

Risks: -n is parsed but ignored because the program always calls mtestdir(); missing or wrong-size bigfile causes read failure; content is not validated.

Test signals: successful full-length reads and final unlink lead to complete(); open/read/unlink failures are fatal.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/basic/test5b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/basic/test6.c -->
# sources/test-tools/cthon04/basic/test6.c

Purpose: directory-read correctness test for readdir ordering/completeness across repeated rewinds while entries are removed.

Important APIs/types/functions: parses -h, -t, -f, -n, -i plus files/count/fname. Uses opendir(), rewinddir(), readdir(), closedir(), bitmap macros BIT/SETBIT/CLRBIT, unlink(), dirtree(), rmdirtree().

Control flow: validates count <= files and files <= MAXFILES, creates a flat file set, opens '.', then for each pass rewinds and checks that '.', '..', expected remaining files, and no removed files are reported. After each pass it unlinks the file matching the pass index.

State and persistence: mutates the directory during enumeration by deleting one generated file per pass, then runs rmdirtree(ignore=1) to clean remaining generated files.

Dependencies and integration points: uses native dirent on Unix and emulated dirent from subr.c/unixdos.h on DOS/Win32. -i supports running in a directory with unrelated entries.

Risks: bitmap limit caps files at 512; atoi accepts nonnumeric suffix prefixes weakly; filesystem-specific directory cache behavior can surface here.

Test signals: duplicate/missing/unexpected entries accumulate errors and fail immediately; success prints entries read and ok marker.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/basic/test6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/basic/test7.c -->
# sources/test-tools/cthon04/basic/test7.c

Purpose: combined rename and hard-link correctness test.

Important APIs/types/functions: parses -h, -t, -f, -n plus files/count/fname/nname. Uses rename(), stat(), link(), unlink(), errno/EOPNOTSUPP handling, dirtree(), rmdirtree().

Control flow: creates files, then for each pass renames each original to a new name, verifies original disappearance and new existence. On Unix-like clients it links new back to original, checks link counts at 2, unlinks new, and checks original count returns to 1. On DOS/Win32 it renames back instead.

State and persistence: mutates generated filenames heavily and cleans up with rmdirtree(ignore=1) after the timed section.

Dependencies and integration points: tests link support where available; treats EOPNOTSUPP as unsupported and exits through complete() after reporting the attempted failure.

Risks: link count semantics vary on some network or pseudo filesystems; DOS/Win32 path is a rename fallback, not a hard-link test.

Test signals: stat/link-count mismatches or rename/link/unlink failures are fatal; success reports operation count and ok marker.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/basic/test7.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/basic/test7a.c -->
# sources/test-tools/cthon04/basic/test7a.c

Purpose: rename-only correctness and timing variant.

Important APIs/types/functions: parses -h, -t, -f, -n plus files/count/fname/nname. Uses rename(), stat(), dirtree(), rmdirtree(), timing helpers.

Control flow: creates files, then repeatedly renames each file to the new prefix and back, verifying after each rename that the old name is gone and the new/current name is stat-able.

State and persistence: temporary names exist only within each iteration; cleanup removes the generated original-name files afterward.

Dependencies and integration points: narrower companion to test7 for filesystems without hard-link support concerns.

Risks: does not test overwrite rename cases; generated names use fixed buffers; failures leave partial renamed state for cleanup.

Test signals: success prints the number of renames and complete(); any failed stat/rename exits nonzero.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/basic/test7a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/basic/test7b.c -->
# sources/test-tools/cthon04/basic/test7b.c

Purpose: hard-link correctness and timing variant.

Important APIs/types/functions: parses -h, -t, -f, -n plus files/count/fname/nname. Uses link(), stat(), unlink(), errno/EOPNOTSUPP, and DOS/Win32 rename fallback.

Control flow: for each generated file, creates a second directory entry with link(), verifies both names report link count 2, removes the new name, and verifies the original link count returns to 1. DOS/Win32 performs rename out/back and expects link count 1.

State and persistence: creates transient extra names and removes them each iteration; final cleanup removes original generated files.

Dependencies and integration points: complements test7a and test7 in harnesses that split rename/link behavior.

Risks: on filesystems that do not expose stable st_nlink, this can fail despite usable data access; unsupported hard links exit through complete() after EOPNOTSUPP.

Test signals: link-count checks are the main correctness signal; success reports link count and ok marker.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/basic/test7b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/basic/test8.c -->
# sources/test-tools/cthon04/basic/test8.c

Purpose: symlink and readlink correctness test.

Important APIs/types/functions: parses -h, -t, -f, -n plus files/count/fname/sname. Uses symlink(), lstat(), readlink(), unlink(), S_IFLNK, errno/EOPNOTSUPP.

Control flow: if S_IFLNK is unavailable it prints a not-supported message and completes. Otherwise it enters the test directory, repeatedly creates a symlink name with fname prefix pointing to sname+index, verifies lstat type and readlink byte count/content, then unlinks it.

State and persistence: symlinks are transient and removed in the same iteration; no regular file tree is created.

Dependencies and integration points: depends on Unix symlink APIs; DOS/Win32 builds generally take the unsupported path.

Risks: uses readlink() without null-terminating buf but compares using returned length; absolute default target is intentionally not required to exist; unsupported filesystems are treated as skipped/ok.

Test signals: type mismatch, readlink length/content mismatch, or unlink failure is fatal; success reports operation count and complete().
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/basic/test8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/basic/test9.c -->
# sources/test-tools/cthon04/basic/test9.c

Purpose: filesystem-statistics syscall test for the mounted test directory.

Important APIs/types/functions: parses -h, -t, -f, -n plus count. Uses statvfs() on SVR4, statfs() otherwise, including SVR3 signature handling; subr.c supplies statfs on DOS/Win32.

Control flow: enters or reuses the test directory, then loops count times calling the platform filesystem-stat API on '.'.

State and persistence: read-only after optional test-directory creation.

Dependencies and integration points: header selection varies across SVR4, OSF1/BSD, generic sys/vfs, and DOS/Win32 compatibility.

Risks: only checks syscall success, not field correctness; platform-specific statfs structures make portability fragile.

Test signals: success is the count line for statfs/statvfs followed by complete(); any syscall failure exits nonzero.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/basic/test9.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/domount.c -->
# sources/test-tools/cthon04/domount.c

Purpose: tiny setuid-oriented wrapper that execs the platform mount or umount command for the Connectathon test harness.

Important APIs/types/functions: main() inspects argv[1] for -u, getenv("UMOUNT")/getenv("MOUNT"), setuid(0), execv(), and exit(). It mutates argv in place so execv receives the selected command path as argv[0] while preserving remaining arguments.

Control flow: if -u is present, the command becomes UMOUNT or /etc/umount and argv is advanced past the wrapper name; otherwise the command becomes MOUNT or /etc/mount. The process sets effective uid to root, execs the selected command, and exits 1 only if execv fails.

State and persistence behavior: does not persist data itself, but when installed setuid root it can mount or unmount filesystems and therefore changes system mount state.

Dependencies and integration points: used by harness scripts that need privileged mount/umount without embedding platform paths. It expects traditional /etc/mount and /etc/umount defaults unless overridden by environment.

Risks: setuid root plus environment-selected executable path is a major security risk outside a controlled test lab; missing string/unistd headers produce old-C implicit declarations; no diagnostics are emitted on exec failure.

Test signals: success is replacement by the mount/umount program. A direct exit status 1 means command exec failed.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/domount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/general/Makefile -->
# sources/test-tools/cthon04/general/Makefile

Purpose: makefile for the general Connectathon tests and fixtures, especially producing large1.c, large2.c, and large3.c copies from large.c.

Important APIs/types/functions: variables DESTDIR, FILES, LARGE_SRC; targets all, large1.c, large2.c, large3.c, clean, copy, and dist.

Control flow: all depends on the generated large source copies and ensures runtests is executable. Each largeN.c target removes the old copy and copies large.c. clean removes timing files, objects, stat, and generated large source copies. copy/dist refresh DESTDIR with the listed fixtures.

State and persistence behavior: creates generated source files in place and changes runtests mode. copy/dist mutate DESTDIR.

Dependencies and integration points: supports general/runtests and the large compile workload. It packages shell scripts, C fixtures, mkdummy/rmdummy, nroff input, and test makefiles.

Risks: DESTDIR defaults to /no/such/path to force explicit override; copy/dist run rm -f in DESTDIR and assume it is safe; generated copies can be mistaken for independent sources.

Test signals: after make all, large1.c-large3.c should exist and runtests should be executable.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/general/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/general/large.c -->
# sources/test-tools/cthon04/general/large.c

Purpose: historical C compiler-driver source used as a large-ish compile workload for the general tests, not as a maintained compiler frontend.

Important APIs/types/functions: global tool paths cpp/ccom/c2/as/ld/crt0; argument lists av/clist/llist/plist; flags for -S, -o, -R, -O, -p, -g/-go, -w, -E/-P, -c, -D/-I/-U/-C, -t, -B, -d. Functions include main(), idexit(), dexit(), error(), getsuf(), setsuf(), callsys(), nodup(), savestr(), and strspl().

Control flow: parses compiler-style arguments into preprocessing, compile, assemble, and link lists; optionally rewrites pass paths; creates /tmp/ctm<pid> temporary names; runs cpp, ccom, optional c2, as, and ld via fork/exec/wait; cleans temporaries on normal exit or signal.

State and persistence behavior: writes temporary files under /tmp, writes .o/.s/.i outputs according to flags, may link an executable, and removes selected temporary/object files depending on compile/link mode.

Dependencies and integration points: depends on old Unix compiler pass paths and libc calls. The general Makefile copies this source to large1.c-large3.c so large4.sh can compile four similar files in parallel.

Risks: old K&R C with implicit declarations; fixed temporary-name buffers; no robust wait error handling; hard-coded tool paths rarely exist on modern systems; primarily useful as test input.

Test signals: in this suite, the signal is successful compilation/removal by make or large4.sh rather than correctness of the compiler driver itself.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/general/large.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/general/large1.c -->
# sources/test-tools/cthon04/general/large1.c

Purpose: generated copy of general/large.c used to create an additional independent compile workload.

Important APIs/types/functions: byte-for-byte identical to large.c in this checkout, so it contains the same compiler-driver globals and functions: main(), idexit(), dexit(), error(), getsuf(), setsuf(), callsys(), nodup(), savestr(), and strspl().

Control flow: same as large.c: parse cc-like flags, run cpp/ccom/c2/as/ld passes, and clean temporary files.

State and persistence behavior: same temporary and output behavior as large.c. Its existence is itself generated state from the general Makefile.

Dependencies and integration points: created by `cp large.c large1.c`; compiled by large4.sh in parallel with large.c/large2.c/large3.c.

Risks: should not be edited independently because regeneration overwrites it; all large.c portability/security limitations apply.

Test signals: successful generation and compilation are the relevant harness signals.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/general/large1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/general/large2.c -->
# sources/test-tools/cthon04/general/large2.c

Purpose: generated copy of general/large.c used as another parallel compile input for the general workload.

Important APIs/types/functions: byte-for-byte identical to large.c here, with the same old compiler-driver functions and global pass state.

Control flow: matches large.c exactly: argument classification, compiler pass execution, optional assembly/link, and cleanup.

State and persistence behavior: generated by the Makefile and may be removed by clean; when compiled or run it has the same temporary/output behavior as large.c.

Dependencies and integration points: produced by `cp large.c large2.c` and consumed by large4.sh.

Risks: independent edits are lost on regeneration; hard-coded old Unix tool paths make runtime use unlikely on modern hosts.

Test signals: presence after make all and successful compile in large4.sh.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/general/large2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/general/large3.c -->
# sources/test-tools/cthon04/general/large3.c

Purpose: generated copy of general/large.c completing the four-way large compile workload.

Important APIs/types/functions: identical to large.c in this checkout, including main(), compiler-pass path globals, suffix helpers, fork/exec wrapper, and string-save allocator.

Control flow: same cc-like pass orchestration as large.c.

State and persistence behavior: generated source artifact; compilation creates a temporary binary that large4.sh removes.

Dependencies and integration points: produced by the general Makefile and compiled alongside large.c, large1.c, and large2.c.

Risks: regeneration overwrites local edits; old K&R assumptions and hard-coded paths apply.

Test signals: generated copy exists and compiles successfully in the general test script.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/general/large3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/general/large4.sh -->
# sources/test-tools/cthon04/general/large4.sh

Purpose: shell workload that compiles four large source files concurrently and removes the resulting executables.

Important APIs/types/functions: uses environment variables CC and CFLAGS, background jobs with &, wait, and rm.

Control flow: launches four compile commands for large.c, large1.c, large2.c, and large3.c in parallel, waits for all background compilers, then removes large, large1, large2, and large3 executables.

State and persistence behavior: transiently creates four executables in the current directory and deletes them at the end. It does not clean object files because direct compile commands do not request separate .o outputs.

Dependencies and integration points: expects the general Makefile to have generated large1.c-large3.c and expects CC/CFLAGS to be set by the surrounding runtests environment.

Risks: no `set -e`, so a failed compiler can be masked by later rm behavior; removes executable names unconditionally; first line is a historical no-op colon before the shebang, so execution depends on invoking it with a shell or permissive systems.

Test signals: the intended signal is that all background compiles finish and the script exits after cleanup; harness timing captures elapsed compile workload.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/general/large4.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/general/nroff.in -->
# sources/test-tools/cthon04/general/nroff.in

Purpose: static nroff/troff input fixture used by the general tests to exercise text processing over a realistic document.

Important APIs/types/functions: not executable code. It uses troff requests/macros such as .DA, .ds, .nr, .ps, .vs, .TL, .AU, .LP, .TS/.TE tables, .IP lists, and .SH sections.

Control flow: when processed by nroff/troff, the document defines headers/footers and typesetting parameters, emits a title/author, two tables, narrative paragraphs, conclusions, and future-work sections.

State and persistence behavior: read-only fixture; generated output is produced by whatever harness command processes it, not by this file itself.

Dependencies and integration points: consumed by general test scripts that run nroff or equivalent text-formatting tools; provides enough content and table markup to exercise parser and filesystem read paths.

Risks: content is historical sample prose with old spelling and performance data; tests depend on availability and behavior of legacy nroff/troff tools.

Test signals: successful formatter execution and expected output/timing files in the surrounding harness.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/general/nroff.in -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/general/stat.c -->
# sources/test-tools/cthon04/general/stat.c

Purpose: summarizer for timing output files produced by general tests.

Important APIs/types/functions: globals real/user/sys arrays with MAXINDEX=100, Prog, File; functions main(), getattfmt(), and prtstat(). Uses fopen(), fgetc(), ungetc(), fscanf(), fgets(), sscanf(), sqrt(), and printf().

Control flow: opens a datafile, skips non-data leading lines, detects BSD one-line time format or ATT multi-line format, parses up to MAXINDEX samples into arrays, then prints average and sample standard deviation for real/user/sys.

State and persistence behavior: read-only over the input file; stores parsed samples in process-global arrays and writes one summary line to stdout.

Dependencies and integration points: linked with libm; used by general test reporting to normalize timing files across Unix variants.

Risks: no bounds check in the BSD fscanf loop, so more than 100 samples overflows arrays; uses isdigit without including ctype.h; ATT parser assumes strict real/user/sys grouping.

Test signals: success prints three tab-separated average/stddev groups labeled real/user/sys; bad or empty input exits nonzero except SVR3 no-data compatibility.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/general/stat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/getopt.c -->
# sources/test-tools/cthon04/getopt.c

Purpose: bundled public-domain getopt implementation plus a standalone command that rewrites shell arguments in a canonical getopt output form.

Important APIs/types/functions: global getopt variables opterr, optind, optopt, optarg; function nfs_getopt(argc, argv, opts); main() wrapper. Uses ERR macro with write(), strchr()/index(), strcmp(), sprintf(), strcat(), and printf().

Control flow: nfs_getopt tracks position within grouped option strings using static sp, returns EOF at end or --, emits '?' for illegal/missing options, and sets optarg for options followed by ':' in the option spec. main() treats argv[1] as the legal option spec, calls nfs_getopt over argv[1..], builds a line containing parsed options, `--`, and remaining operands, then prints it.

State and persistence behavior: no file persistence; parsing state lives in global/static variables and is not reentrant.

Dependencies and integration points: supplied for systems lacking getopt or for harness scripts that expect the historical command-line utility behavior.

Risks: fixed BUFSIZ buffers can overflow with long argument lists; old implicit declarations for write/exit on some platforms; global state prevents concurrent independent parses.

Test signals: exit 0 with a canonical option line, exit 2 on usage or parse error.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/getopt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/lock/Makefile -->
# sources/test-tools/cthon04/lock/Makefile

Purpose: makefile for Connectathon file-locking tests, building native, Large File Summit, and 64-bit-lock variants from tlock.c.

Important APIs/types/functions: includes ../tests.init, defines DESTDIR and LIBS=-lm, and targets all, tlock, tlocklfs, tlock64, clean, copy, dist, lint, lint32lfs, lint64, lintall.

Control flow: all builds $(LOCKTESTS) and ensures runtests is executable. tlock compiles plain tlock.c; tlocklfs adds -DLF_SUMMIT; tlock64 adds -DLF_SUMMIT -DLARGE_LOCKS. copy/dist install binaries or sources to DESTDIR; lint targets run matching analysis modes.

State and persistence behavior: creates tlock/tlocklfs/tlock64 and object files in the lock directory; clean removes them; copy/dist write DESTDIR.

Dependencies and integration points: depends on tests.init for CC, CFLAGS, and LOCKTESTS selection. The produced programs integrate with lock/runtests.

Risks: recursive `make $(LOCKTESTS)` inherits environment-sensitive target names; DESTDIR defaults invalid; all variants share one source so macro-specific behavior must be tested separately.

Test signals: successful build of configured LOCKTESTS and executable runtests; lint targets provide static-analysis signals for each offset/locking mode.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/lock/Makefile -->
