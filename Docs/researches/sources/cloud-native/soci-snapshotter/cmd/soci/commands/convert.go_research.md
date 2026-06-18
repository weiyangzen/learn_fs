## sources/cloud-native/soci-snapshotter/cmd/soci/commands/convert.go

Purpose: implements `soci convert`, creating SOCI-enabled OCI images either in containerd or standalone OCI-layout mode.

Important APIs/types/functions: `ConvertCommand`, `verifyRef`, `runStandaloneConvert`, and `parseBuilderOptions`.

Control flow: validate source/destination, branch to standalone when requested, otherwise connect to containerd, load source image, open selected SOCI/content store and artifacts DB, build index builder options, resolve platforms, call `builder.Convert`, then create or update the destination image with the converted descriptor.

State and persistence: mutates containerd image metadata/content store and SOCI artifacts DB. Standalone mode creates temp OCI/artifact dirs, loads tar/dir input, converts into ORAS-backed layout, and writes tar or directory output.

Dependencies and integration: containerd image/content services, SOCI builder/store/DB, platform and prefetch helpers, OCI archive utilities.

Risks and test signals: destination validation rejects digest refs. Standalone temp directory behavior depends on `/tmp` availability. No direct tests in this subset.
