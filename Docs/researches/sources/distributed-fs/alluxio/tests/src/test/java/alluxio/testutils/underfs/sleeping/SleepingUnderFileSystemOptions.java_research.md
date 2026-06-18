# Research: sources/distributed-fs/alluxio/tests/src/test/java/alluxio/testutils/underfs/sleeping/SleepingUnderFileSystemOptions.java

Purpose: fluent configuration holder for operation-specific delays used by `SleepingUnderFileSystem`. Every field is a millisecond duration and defaults to `-1`, which means no sleep.

Important APIs and control flow: the class exposes getter/setter pairs for cleanup, close, connect-from-master/worker, create, delete directory/file, exists, block size, configuration, directory status, locations, file status, fingerprint, space, status, UFS type, isDirectory/isFile, listStatus/listStatusWithOptions, mkdirs, open, rename directory/file/temporary file, setConf, setOwner, setMode, and supportsFlush. Setters mutate the field and return `this`.

State, dependencies, integration, risks, tests: state is mutable and unsynchronized; callers usually build one instance per test fixture. It has no external dependencies beyond its paired UFS. Risks include negative random values in tests being valid no-sleep values, and option fields such as `setConfMs` existing even if the current `SleepingUnderFileSystem` implementation does not override a matching method.
