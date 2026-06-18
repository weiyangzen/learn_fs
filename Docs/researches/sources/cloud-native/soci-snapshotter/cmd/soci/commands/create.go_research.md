## sources/cloud-native/soci-snapshotter/cmd/soci/commands/create.go

Purpose: implements `soci create`, generating SOCI indexes and zTOCs for an existing containerd image.

Important APIs/types/functions: `CreateCommand`, `createZtocFlags`, and constants for span size, min layer size, optimizations, force, and GC label.

Control flow: validate image ref, parse optimizations and prefetch paths, connect to containerd, get image, open configured content store, resolve platforms, open artifacts DB, build `soci.IndexBuilder`, then for each platform open a batch, build the index, and label the source image with the SOCI index digest.

State and persistence: writes SOCI layer/index artifacts to selected store, updates artifacts DB, and mutates containerd image labels for GC rooting.

Dependencies and integration: containerd client/image service, SOCI builder/store/DB, global root flag, platform helpers.

Risks and test signals: `defer done(ctx)` inside the platform loop delays all batch cleanup until command return. `is.Update` errors are ignored. No direct tests here.
