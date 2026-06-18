<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/manager/transformer.go -->
# sources/cloud-native/containerd/core/mount/manager/transformer.go

Purpose: defines shared transformer type-prefix handling for mount manager internal transforms.

Important APIs/types/functions: constants `prefixMkdir = "X-containerd.mkdir."` and `prefixMkfs = "X-containerd.mkfs."`; `typeTransformer` embeds `mount.Transformer` and stores the final `mountType`.

Control flow: `typeTransformer.Transform` delegates to the embedded transformer and then overwrites the returned mount's `Type` with the stripped type selected by `manager.go` while parsing chains such as `format/mkdir/overlay`.

State and persistence: no state beyond wrapper fields; only mutates the returned mount value.

Dependencies and integration points: used by `manager.go` to compose built-in transforms while preserving the eventual concrete mount type for handler lookup or system mounting.

Risks: transform ordering is determined by slash-prefix order in the mount type; an unknown transform breaks the chain and logs a warning in the manager. The wrapper assumes the embedded transformer should not control final type.

Test signals: covered indirectly by manager and format/mkdir tests that use transformed mount types and expect final system mounts to be concrete types.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/manager/transformer.go -->
