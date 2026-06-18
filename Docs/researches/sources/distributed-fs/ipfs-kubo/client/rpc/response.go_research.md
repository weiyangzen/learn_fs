# sources/distributed-fs/ipfs-kubo/client/rpc/response.go

## Purpose
This file sends low-level HTTP requests and decodes Kubo command responses.

## Important APIs, Types, And Functions
`Response` wraps output and command error. `trailerReader` turns stream error trailers into read errors. `Response.Close`, `Cancel`, and `decode` manage response bodies. `Request.Send` creates POST requests, sets multipart headers, maps HTTP errors to `cmds.Error`, and `getURL` builds query strings.

## Control Flow
`Send` posts to `/api/v0/<command>?arg=...`, copies custom headers, performs the request, parses content type, wraps successful bodies, and handles error bodies as text, JSON, not found, rate-limited, forbidden, or implementation errors.

## State And Persistence Behavior
State is per-response body/trailer state. `Close` drains bodies to support connection cleanup; `Cancel` aborts without draining.

## Dependencies And Integration Points
It integrates go-ipfs-cmds HTTP conventions, stream error trailers, Boxo multipart readers, and all RPC sub-APIs.

## Risks And Test Signals
Risks include failing on missing/invalid content type, body drain behavior, stderr warnings from library code, and trailer-only errors surfacing late. Signals are correct error codes/messages and clean streaming response closure.
