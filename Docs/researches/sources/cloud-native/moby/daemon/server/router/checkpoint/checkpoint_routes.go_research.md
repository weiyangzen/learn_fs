# sources/cloud-native/moby/daemon/server/router/checkpoint/checkpoint_routes.go

## Purpose
Implements HTTP handlers for creating, listing, and deleting container checkpoints.

## Important APIs, Types, And Functions
`postContainerCheckpoint`, `getContainerCheckpoints`, and `deleteContainerCheckpoint` parse requests and call the checkpoint backend. They use `httputils.ParseForm`, `httputils.ReadJSON`, `httputils.WriteJSON`, and backend checkpoint option structs.

## Control Flow
Create parses form and JSON body into `checkpoint.CreateRequest`, calls `CheckpointCreate`, and returns 201. List parses form, calls `CheckpointList` with optional `dir`, normalizes nil results to an empty slice, and writes JSON 200. Delete parses form, calls `CheckpointDelete` with route checkpoint ID and optional dir, and returns 204.

## State And Persistence
Handlers mutate checkpoint state only through backend calls. They write HTTP response status/body.

## Dependencies And Integration Points
Connects experimental checkpoint routes to daemon checkpoint implementation and API checkpoint types.

## Risks And Edge Cases
`ReadJSON` allows an empty body for create, so backend must validate required fields. Directory parameters are passed through from form data.

## Test Signals
Checkpoint API tests should cover status codes, empty list normalization, JSON parsing, and backend error propagation.
