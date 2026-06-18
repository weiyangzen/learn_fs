# sources/cloud-native/nydus-snapshotter/.github/workflows/optimizer.yml

Purpose: end-to-end optimizer NRI plugin test.

Flow: provisions crictl, containerd, runc, CNI, builds optimizer plugin/server, installs NRI config, restarts containerd, runs an nginx pod whose entrypoint reads a file list, then verifies the optimizer output file has at least the expected number of lines.

State/dependencies: writes under `/opt/nri/optimizer/results`, installs system files, uses Rust cache and external release downloads.

Integration points: validates `cmd/optimizer-nri-plugin`, optimizer server, NRI, crictl examples, and `misc/optimizer` manifests.

Risks/tests: heavily depends on host service mutation and downloaded versions. Failure dump captures containerd journal for diagnosis.
