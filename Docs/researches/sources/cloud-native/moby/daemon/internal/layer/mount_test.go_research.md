## sources/cloud-native/moby/daemon/internal/layer/mount_test.go

Purpose: Tests writable layer mount behavior.

Important tests: `TestMountInit` verifies an init layer can alter file content and permissions visible in the mounted RW layer. `TestMountSize` verifies init-layer changes are excluded from mutable layer size while newly written RW data is counted. `TestMountChanges` verifies modify/delete/add changes relative to base/init parent are reported. `TestMountApply` applies a diff tar to a RW layer and verifies the new file appears. Helpers `assertChange`, `sortChanges`, and `changeSorter` normalize change ordering.

Control flow and state: Tests create base layers, optional init functions, RW layers, mount paths, direct filesystem mutations, graphdriver diff/change calls through `RWLayer` methods, and unmount/release paths inherited from helpers.

Dependencies and integration: Exercises `CreateRWLayer`, `Mount`, `Size`, `Changes`, `ApplyDiff`, graphdriver vfs, archive change types, and local chmod support. Skips Windows.

Risks covered: Init-layer parent selection, size accounting excluding init content, change detection, and applying tar diffs. Gaps include mount labels, storage options, repeated mount reference counting, and cleanup after failed init/apply.

Persistence: Temporary graphdriver/layerdb state.
