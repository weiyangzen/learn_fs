# sources/distributed-fs/alluxio/core/server/pom.xml

## Purpose
This Maven POM defines the `alluxio-core-server` aggregator module. It groups Alluxio core server submodules under a single Maven parent and keeps build path properties available when Maven is invoked from this subtree.

## Important APIs, Types, and Functions
The file is declarative XML rather than executable code. Its important elements are the parent `org.alluxio:alluxio-core:2.10.0-SNAPSHOT`, artifact ID `alluxio-core-server`, packaging `pom`, and modules `common`, `master`, `proxy`, and `worker`.

## Control Flow, State, and Persistence
There is no runtime control flow. Maven uses the module list to order reactor builds and test execution. The `build.path` property points back to the repository `build` directory through `${project.parent.parent.basedir}`.

## Dependencies and Integration Points
This POM integrates the core server subtree with the broader Alluxio build. Its child modules include the master tests and proxy sources researched in this work item.

## Risks
Changing module names or ordering can break Maven reactor builds and downstream modules that rely on this aggregation. The relative `build.path` property exists to support running Maven from sub-project directories; changing it can break local submodule builds.

## Test Signals
Signals are Maven reactor commands from `core/server` or the repository root, for example compiling or testing `common`, `master`, `proxy`, and `worker` through this aggregator.
