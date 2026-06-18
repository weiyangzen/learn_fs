# sources/cloud-native/overlaybd/src/tools/overlaybd-commit.cpp

Purpose: CLI that commits an OverlayBD mutable layer into a read-only commit file, with optional zfile compression, tar wrapping, TurboOCI warp-file mode, sealing, and registry upload.

Important APIs/types/functions: uses LSMT `open_file_rw`, `open_warpfile_rw`, `open_file_ro`, `CommitArgs`, `IFileRW::commit`, `IFileRW::close_seal`, zfile `CompressOptions`/`CompressArgs`/`new_zfile_builder`, `create_uploader`, and `registry_uploader_fini`.

Control flow: after CLI parsing and Photon init, it opens data/index files as normal LSMT, TurboOCI warp, or already-sealed input. `--seal` only closes/seals the layer and exits. Otherwise it creates the output file, optionally wraps it in tar, registry uploader, and zfile builder, populates UUID/parent UUID/user tag commit args, commits through LSMT, closes output, finalizes upload, prints digest, and releases resources.

State and persistence: creates the commit output, may unlink an existing output with `-f`, may upload a blob to a registry, and may mutate the input by sealing it. UUID and parent UUID are stored in commit metadata.

Dependencies/integration: links Photon localfs, LSMT, zfile, tar adaptor, registryfs, and CLI11.

Risks: `algorithm`/block-size validation is tied to `-z`; without `-z`, `block_size` defaults to `-1` but the warning compares against `0`. Upload and tar are rejected together in commit mode. UUID strings are copied without validating length against the fixed buffer.

Test signals: useful coverage includes normal commit, TurboOCI commit, sealed commit, seal-only, invalid compression options, duplicate output with/without `-f`, and upload finalization.
