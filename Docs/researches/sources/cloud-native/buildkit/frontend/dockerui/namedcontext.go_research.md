# sources/cloud-native/buildkit/frontend/dockerui/namedcontext.go

## Purpose

This file implements Docker UI named contexts: build option entries such as `context:<name>` are converted into lazy `llb.State` sources that frontends can use as additional build contexts. It supports image, Git, HTTP, OCI layout, local, and gateway input sources while preserving platform-aware names and optional digest capture.

## Important APIs, Types, And Functions

- `NamedContext` stores the raw context specifier, owning `*Client`, logical names, shared local-directory key, and `ContextOpt`.
- `(*Client).namedContext` looks up `context:<nameWithPlatform>` in build options and returns `nil` when the named context is absent.
- `(*NamedContext).Load` calls `load(ctx, 0)` and is the public loading entry point.
- `(*NamedContext).load` parses the `<scheme>:<payload>` context source and dispatches to source-specific LLB construction.
- `asyncLocalOutput` is an `llb.Output` wrapper that delays constructing `llb.Local` until `ToInput` or `Vertex` is called.
- `(*asyncLocalOutput).do` builds the local source with session ID, shared key hint, dockerignore exclusions, and optional caller-provided local options.

## Control Flow

`Load` validates `scheme:payload`, normalizes legacy `git@` SSH-style prefixes to `git`, then switches by scheme. `docker-image` resolves and unmarshals image config, converts non-image resolution results into recursively reloaded named contexts, returns scratch for `EmptyImageName`, and tags the LLB image with custom display names and platform constraints. `git`, `http`, and `https` delegate Git URL detection first; non-Git HTTP sources become `llb.HTTP` states. `oci-layout` parses the store ID and digest, resolves image config through the client session-backed OCI layout resolver, and returns `llb.OCILayout`.

For `local`, the code first solves a small LLB that only follows `.dockerignore`, reads and parses ignore rules unless disabled, then returns an `llb.NewState` around `asyncLocalOutput`. The actual local source is constructed later, which lets `ContextOpt.AsyncLocalOpts` run after initial context configuration is known. For `input`, the gateway client input definitions are loaded by name and optional `input-metadata:<name>` JSON supplies image config metadata.

## State And Persistence Behavior

The code mutates `bc.bopts.Opts[context:<name>]` only when image resolution reports `ResolveToNonImageError`; this encodes an updated non-image source and retries with a recursion limit of 10. Local source state depends on session IDs and shared key hints rather than durable repository state. `asyncLocalOutput` uses `sync.Once` to make lazy source construction idempotent and thread-safe for both `ToInput` and `Vertex`.

## Dependencies And Integration Points

It integrates with `llb` source constructors, `sourceresolver` image/OCI metadata, gateway `client.Client` solve/input APIs, BuildKit exporter image config metadata, Docker image spec structs, distribution reference parsing, image source-policy rewrite errors, and `.dockerignore` parsing from `patternmatcher/ignorefile`.

## Risks And Edge Cases

Incorrect context specifier formatting fails early. Recursive source-policy rewrites can loop, so `maxContextRecursion` is a key guard. Local `.dockerignore` parsing errors fail the context, but missing `.dockerignore` is ignored. OCI layout requires both a named reference and digest. `input` metadata JSON and image config JSON are trust boundaries and can fail parsing. Mutating build options during load means callers sharing a `Client` observe rewritten context specs.

## Test Signals

No direct tests are in this file, but gateway and frontend integration tests exercise reference reads and input/solve behavior that named contexts depend on. Strong targeted coverage would include source-policy image-to-Git/HTTP rewrites, OCI layout digest validation, local dockerignore parsing, and async local option invocation.
