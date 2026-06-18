# sources/distributed-fs/ipfs-kubo/cmd/ipfs/kubo/debug.go

## Purpose
This file registers an HTTP debug endpoint that dumps all goroutine stacks.

## Important APIs, Types, And Functions
`init` registers `/debug/stack` on `http.DefaultServeMux` and writes `profile.WriteAllGoroutineStacks` to the response.

## Control Flow
Registration happens at package init time. `daemon.go` exposes the default mux under the API debug routes.

## State And Persistence Behavior
It mutates global `http.DefaultServeMux` handler registration.

## Dependencies And Integration Points
It integrates Kubo profiling utilities, `net/http`, and daemon debug API serving.

## Risks And Test Signals
Risks include exposing sensitive goroutine stacks on the RPC API and global mux collisions. Signal is `/debug/stack` returning stack dumps when API debug routes are available.
