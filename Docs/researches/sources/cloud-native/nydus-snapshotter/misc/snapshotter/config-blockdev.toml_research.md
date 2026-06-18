# sources/cloud-native/nydus-snapshotter/misc/snapshotter/config-blockdev.toml

Purpose: snapshotter config for blockdev/tarfs mode.

Flow/state: sets daemon mode `none`, fs driver `blockdev`, Nydus image path, skip SSL verify, Kata volume insertion, and enables tarfs with `image_block_with_verity` export mode.

Integration points: used for runtime stacks where Kata or block device handoff manages mounts without nydusd serving RAFS.

Risks/tests: requires kernel EROFS/tarfs support and Nydus image service compatibility. Misuse on unsupported hosts will fail at mount/runtime integration, not config parse alone.
