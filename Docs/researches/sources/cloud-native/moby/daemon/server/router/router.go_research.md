# sources/cloud-native/moby/daemon/server/router/router.go

## Purpose
`router.go` defines the minimal interfaces shared by all daemon HTTP routers.

## Important APIs, Types, And Functions
`Router` exposes `Routes() []Route`. `Route` exposes `Handler() httputils.APIFunc`, `Method() string`, and `Path() string`.

## Control Flow
Individual router packages return a `Router`; the server iterates each route and registers versioned and unversioned paths with gorilla/mux.

## State And Persistence
No state is stored in the interfaces themselves.

## Dependencies And Integration Points
This is the central contract between route packages and `daemon/server.Server`.

## Risks
Any interface change affects every router package and server registration code.

## Test Signals
Compilation across all router packages and `server.CreateMux` tests provide coverage.
