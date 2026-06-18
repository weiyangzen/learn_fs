# sources/cloud-native/moby/integration/system/disk_usage_prune_test.go

## Purpose
Regression coverage for concurrent `DiskUsage` calls while images are being removed from a containerd image-store daemon.

## Important APIs, Types, And Functions
- `TestDiskUsageConcurrentPrune` loads ten synthetic images with ten layers each, launches five `DiskUsage` goroutines, and concurrently removes images.
- Uses `specialimage.MultiLayerCustom`, `image.Load`, `client.DiskUsageOptions{Images: true}`, `sync.WaitGroup`, and an error channel.

## Control Flow
The test skips Windows, remote daemons, and non-snapshotter environments, starts a fresh daemon, loads unique multilayer images, schedules cleanup, then starts concurrent disk-usage readers after a removal goroutine closes a start channel. All goroutines complete before errors are asserted.

## State And Persistence
Creates many images and snapshots in an isolated daemon. Image deletion races with snapshot accounting. Cleanup force-removes images after the test.

## Dependencies And Integration Points
Integrates image build/load helpers, containerd image store snapshot metadata, daemon disk usage accounting, image removal, and Go concurrency primitives.

## Risks And Edge Cases
Race reproduction is probabilistic; more layers/images raise odds but increase runtime. The test only applies to the containerd image store. Ignored image-remove errors during the race are intentional because the regression target is `DiskUsage` returning errors.

## Test Signals
Passing means none of the concurrent `DiskUsage` calls returns an error while image removal is active.
