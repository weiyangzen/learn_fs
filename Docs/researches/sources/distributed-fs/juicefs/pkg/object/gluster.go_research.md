# sources/distributed-fs/juicefs/pkg/object/gluster.go


Purpose: implements GlusterFS object storage behind the `gluster` build tag, registering `gluster`.

Important APIs and flow: `gluster` holds one or more `gfapi.Volume` clients and selects them round-robin through an atomic counter. `Head`, `Get`, `Put`, `Delete`, `List`, `Chmod`, and metadata conversion map JuiceFS object operations to gfapi calls. `Put` creates directories as needed, writes through a 1 MiB buffer, calls `Sync`, and removes partial files on errors. `readDirSorted` filters `.`/`..`, handles symlinks when requested, filters non-regular files, and sorts entries.

State and persistence: persistent state lives in the Gluster volume. Local state is the mounted gfapi clients and selected log configuration.

Dependencies and integration: depends on `github.com/juicedata/gogfapi/gfapi`, shared `mEntry`, `file`, `bufPool`, and Unix owner/group helpers. `newGluster` parses `gluster://host[,host]/volume`, supports `JFS_NUM_GLUSTER_CLIENTS`, log level, and log path.

Risks: build requires Gluster support. `Chtimes` and `Chown` are not supported. Writes are not temp-renamed like `filestore`, so partial files can be visible until error cleanup. Host ports are noted as unsupported. Listing uses filepath joins and slash normalization carefully but remains path-sensitive.

Test signals: `gluster_test.go` runs shared storage and filesystem tests only when built with `gluster` and `GLUSTER_VOLUME` is set.
