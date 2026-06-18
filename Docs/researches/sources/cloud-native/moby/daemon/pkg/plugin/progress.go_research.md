<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/progress.go -->
# sources/cloud-native/moby/daemon/pkg/plugin/progress.go

## Purpose
Tracks plugin push jobs and converts containerd upload tracker state into Docker progress messages.

## Important APIs, Types, And Functions
`newPushJobs`, `pushJobs.add`, `pushJobs.status`, and `contentStatus` are the main items.

## Control Flow
`add` de-duplicates upload job IDs and stores a display name. `status` locks the job list, queries `docker.StatusTracker`, maps missing status to `Waiting`, and reports uploading or upload-complete state based on `UploadUUID`.

## State, Dependencies, And Integration Points
State is an in-memory job list and ID-to-name map protected by a mutex. It integrates with `backend_linux.go` push progress goroutines and containerd's Docker remotes tracker.

## Risks And Test Signals
Status polling depends on tracker keys matching `remotes.MakeRefKey`. No direct tests exist; plugin push integration output is the signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/progress.go -->
