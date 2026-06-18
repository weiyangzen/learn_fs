<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/snapshot/mount_option.go -->
## sources/cloud-native/nydus-snapshotter/snapshot/mount_option.go

Purpose: builds special mount options for nydus-overlayfs and Kata Containers volumes, including proxy-mode guest pulls and tarfs raw block volumes with optional dm-verity.

Important APIs/types: `ExtraOption`, `remoteMountWithExtraOptions`, `mountWithKataVolume`, `mountWithProxyVolume`, `mountWithTarfsVolume`, `prepareKataVirtualVolume`, `parseTarfsDmVerityInfo`, `DmVerityInfo`, volume structs, `KataVirtualVolume`, parsing/encoding helpers, and volume type constants.

Control flow and state: `remoteMountWithExtraOptions` locates the bootstrap, daemon/instance config, detects fs version from bootstrap header, base64-encodes source/config/snapshotdir/version as `extraoption=...`, and returns a `fuse.nydus-overlayfs` mount. `mountWithKataVolume` augments overlay options with proxy and/or tarfs volume descriptors. Proxy volumes embed RAFS annotations as image-pull metadata. Tarfs volumes pick image-level or layer-level block annotations, resolve disk image paths, and encode volume descriptors, walking parent snapshots for layer raw blocks. `DmVerityInfo.Validate` checks hash algorithm, hash length, block counts/sizes, and hash offset alignment/range.

Dependencies/integration: tightly integrated with RAFS global cache, filesystem daemon lookup, snapshot metadata, nydus labels, daemon config dumping, bootstrap fs-version detection, and Kata runtime option contracts.

Risks and test signals: sensitive config is base64-encoded into mount options for nydus-overlayfs. `validateBlockSize` checks only range, not power-of-two despite test comments. Logging encoded volume JSON may expose metadata. Tests cover validation and parse/encode helpers, but not live mount construction with real snapshot metadata.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/snapshot/mount_option.go -->
