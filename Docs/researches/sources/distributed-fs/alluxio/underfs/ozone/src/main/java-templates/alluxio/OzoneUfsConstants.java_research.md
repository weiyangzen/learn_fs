# sources/distributed-fs/alluxio/underfs/ozone/src/main/java-templates/alluxio/OzoneUfsConstants.java

## Purpose
This template generates a compile-time constant exposing the Ozone UFS dependency version.

## Important APIs, Types, And Functions
It defines final class `OzoneUfsConstants` with public static `UFS_OZONE_VERSION = "${ufs.ozone.version}"` and a private constructor.

## Control Flow
There is no runtime control flow. The Maven templating plugin replaces the property placeholder into generated Java sources.

## State And Persistence
The generated class holds a single immutable string constant.

## Dependencies And Integration Points
It is consumed by `OzoneUnderFileSystemFactory.getVersion` to report the module's Ozone version.

## Risks
If templating is skipped or the property is missing, the literal placeholder may leak into runtime version reporting.

## Test Signals
The main signal is successful Maven templating and compilation of the Ozone module.
