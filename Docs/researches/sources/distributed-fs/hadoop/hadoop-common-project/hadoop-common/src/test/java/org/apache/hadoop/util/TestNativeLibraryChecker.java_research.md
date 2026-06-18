# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestNativeLibraryChecker.java

Purpose: tests the command-line `NativeLibraryChecker` utility without allowing it to terminate the JVM.

Important APIs and types: `NativeLibraryChecker.main`, `ExitUtil.disableSystemExit`, `ExitUtil.ExitException`, `ExitUtil.resetFirstExitException`, `NativeCodeLoader.isNativeCodeLoaded`, `Shell.WINDOWS`, and captured `System.out`.

Control flow: help (`-h`) should return normally; illegal argument combinations and unknown args should call exit. With no arguments, the utility returns only if native Hadoop is loaded, otherwise exits. Output tests run `-a` and no-arg modes, capture stdout, and assert platform-relevant lines such as `winutils: true` on Windows and `hadoop:  true` when native code is loaded.

State and persistence: mutates global `ExitUtil` state and temporarily replaces `System.out`; it restores output in `finally`.

Dependencies and integration points: validates admin-facing diagnostics for native Hadoop, zlib, OpenSSL, and Windows support.

Risks: global exit/out state can leak across tests if reset/restore is missed; output text is formatting-sensitive. Test signals are trapped `ExitException`s and substring checks in captured output.
