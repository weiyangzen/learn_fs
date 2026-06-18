# sources/distributed-fs/beegfs-go/ctl/pkg/util/paths.go

## Purpose
Provides common path input handling and concurrent path-processing pipelines for CTL commands. It supports explicit path lists, recursive directory walks, and delimited stdin.

## Important APIs, Types, And Functions
Exports `PathInputType`, `PathInputMethod`, `DeterminePathInputMethod`, `ProcessPathOpts`, option helpers `RecurseLexicographically` and `FilterExpr`, `ProcessPaths`, `StreamPaths`, and `WaitForLastStage`. Internal helpers include `startProcessing`, `walkStdin`, `walkList`, `walkDir`, and `pushFilterInMountPath`.

## Control Flow
`DeterminePathInputMethod` interprets path arguments and recursion/stdin flags. `ProcessPaths` starts a path-streaming errgroup and a processing errgroup, reserving one worker for walking unless single-worker mode is requested. `StreamPaths` compiles optional filesystem filter expressions and delegates to stdin/list/recursive walkers. Walkers convert paths to mount-relative paths, apply filters, and send accepted paths with context cancellation support. `WaitForLastStage` drains upstream channels before combining upstream/downstream errors into `types.MultiError`.

## State And Persistence
No persistence. State is confined to goroutines, channels, compiled filters, and a reused filesystem provider during list/stdin walking.

## Dependencies And Integration Points
Used by many CTL commands including entry set/migrate/refresh and RST status. Depends on Viper `num-workers`, BeeGFS client provider, common filesystem filtering/walking, stdin delimiter utilities, and `errgroup`.

## Risks And Edge Cases
For list/stdin processing, the first successful/failed provider is reused for subsequent paths; mixed mount inputs may be mishandled if a single client cannot resolve all paths. When `config.BeeGFSClient` returns `filesystem.ErrUnmounted`, code still calls methods on `client`, assuming it is usable. `WaitForLastStage` drains channels in goroutines and can block forever if an upstream stage does not close. Recursive walking always converts start path into mount-relative paths before walking.

## Test Signals
No direct tests in this file. Good tests would cover input-method selection, mixed mount list handling, filter behavior, cancellation, worker errors, recursive lexicographic ordering, and multi-error composition.
