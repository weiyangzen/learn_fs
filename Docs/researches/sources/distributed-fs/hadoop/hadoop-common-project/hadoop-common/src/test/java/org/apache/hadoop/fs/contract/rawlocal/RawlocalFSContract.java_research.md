# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/RawlocalFSContract.java

## Purpose
`RawlocalFSContract` describes the raw local filesystem, bypassing the checksum wrapper used by `LocalFileSystem`.

## Important APIs, Types, And Functions
It extends `LocalFSContract`, sets `RAW_CONTRACT_XML = "contract/rawlocal.xml"`, overrides `getContractXml()`, overrides `getLocalFS()` to return `FileSystem.getLocal(getConf()).getRawFileSystem()`, and exposes `getTestDirectory()` as a `java.io.File`.

## Control Flow
Construction delegates to `LocalFSContract`, but contract XML resolution uses rawlocal XML. During initialization, inherited `LocalFSContract.init()` calls the overridden `getLocalFS()`, producing the raw filesystem before platform adjustment.

## State And Persistence
State is inherited `fs`/test directory. Persistent files are direct OS files with no Hadoop checksum side files.

## Dependencies And Integration Points
Raw local contract test classes use this contract to compare direct OS filesystem behavior with checked local FS behavior.

## Risks
Raw local behavior exposes platform-specific semantics directly, especially Windows open-file rename and case sensitivity. Tests must not assume checksum files exist.

## Test Signals
Signals are a `file` scheme raw filesystem and contract behavior matching `contract/rawlocal.xml`.
