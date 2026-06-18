# sources/distributed-fs/alluxio/underfs/web/pom.xml

## Purpose
This Maven module packages the read-only Web UFS implementation as `alluxio-underfs-web`.

## Important Configuration
The module inherits from `alluxio-underfs`, sets `build.path`, depends on provided `alluxio-core-common`, and adds `org.jsoup:jsoup:1.15.3` for HTML parsing. It uses the shared shade and copy-rename Maven plugins.

## Build and Integration
The dependency set is intentionally small because Web UFS relies on Alluxio HTTP utilities and Jsoup rather than a cloud SDK. Shading makes the implementation deployable as an Alluxio UFS extension.

## Risks and Test Signals
The explicit Jsoup version can age independently of parent dependency management. The module supports network-facing HTML parsing, so dependency security matters. Tests in this subset include factory support and a live-style check against an Apache archive URL.
