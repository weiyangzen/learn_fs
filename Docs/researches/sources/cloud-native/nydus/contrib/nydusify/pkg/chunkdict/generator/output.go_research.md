# sources/cloud-native/nydus/contrib/nydusify/pkg/chunkdict/generator/output.go

Purpose: writes parsed Nydus image metadata and extracts its bootstrap to disk as generator input.

Important APIs and flow: `prettyDump` writes indented JSON to a path. `(*Generator).Output` optionally dumps image index, dumps Nydus manifest and config, calls the source parser's `PullNydusBootstrap`, and unpacks `utils.BootstrapFileNameInLayer` from the bootstrap layer into `nydus_bootstrap`. If the parsed source lacks `NydusImage`, it returns an error naming the source ref.

State and persistence: creates JSON files and a raw bootstrap file under the per-source output directory. It consumes a streamed bootstrap layer and closes it after unpacking.

Dependencies and integration: depends on parser output shape and `utils.UnpackFile`. It is called by `Generator.pull` before `nydus-image chunkdict generate`.

Risks and test signals: assumes output directory exists. Failure to close the bootstrap reader after unpack is deferred but close errors are not surfaced. Non-Nydus sources are rejected early.
