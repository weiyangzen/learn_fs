<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/misc/performance/nydusd_config.json -->
# sources/cloud-native/nydus/misc/performance/nydusd_config.json

## Purpose

This nydusd JSON config supports local performance tests using a registry backend and blobcache.

## Important APIs, Types, and Functions

It configures registry backend scheme `http`, host `localhost:5077`, skip verify, timeouts, retry limit, blobcache workdir under the containerd Nydus snapshotter cache, direct mode, disabled digest validation, enabled xattrs, disabled IO/access tracing, and disabled fs prefetch.

## Control Flow

Nydusd reads the config when launched by the snapshotter and fetches blobs from a local registry endpoint.

## State and Persistence Behavior

Blob cache persists under `/var/lib/containerd/io.containerd.snapshotter.v1.nydus/cache`.

## Dependencies and Integration Points

It is referenced by `snapshotter_config.toml` as the daemon config and installed by `prepare.sh` to `/etc/nydus/nydusd-config.fusedev.json`.

## Risks and Test Signals

The config assumes a local registry on port 5077 and disables validation/prefetch for benchmark isolation. It is not production-ready.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/misc/performance/nydusd_config.json -->
