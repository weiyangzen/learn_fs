# sources/distributed-fs/alluxio/underfs/swift/pom.xml

## Purpose
This Maven descriptor builds the OpenStack Swift under file system module.

## Important APIs, Types, And Functions
The artifact is `alluxio-underfs-swift`. It depends on external `org.javaswift:joss`, provided `alluxio-core-common`, and the Alluxio core common test jar.

## Control Flow
The module inherits the parent build and configures shade and copy-rename plugins. Dependency packaging is primarily controlled by parent plugin configuration.

## State And Persistence
The POM has no runtime state. It controls Swift adapter compilation, test classpath, and packaging.

## Dependencies And Integration Points
It integrates Swift/JOSS support into the Alluxio underfs reactor and service-provider packaging.

## Risks
JOSS dependency compatibility and Keystone authentication behavior are the main module-level risks. Shading must preserve service metadata and avoid conflicts with HTTP/Jackson dependencies.

## Test Signals
Build success and Swift-specific tests elsewhere validate module wiring; this subset includes source for Keystone and input range handling.
