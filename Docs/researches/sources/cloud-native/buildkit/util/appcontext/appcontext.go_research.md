# sources/cloud-native/buildkit/util/appcontext/appcontext.go

## Purpose
Process-wide application context for CLI tools. It creates static Context and Shutdown contexts that react to termination signals.

## Important APIs, Types, And Functions
Package: `appcontext`. Build tags: `none`. Key declarations observed in the file: `Context, Shutdown, initContexts`.

## Control Flow, State, And Persistence
sync.Once initializes signal.Notify on platform-specific terminationSignals, runs registered initializers, cancels appContext on first signal, cancels shutdownContext on second, and fatally logs on third. State is process-global only.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/moby/buildkit/util/bklog, github.com/pkg/errors`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is global lifetime/orphan goroutine behavior and late Register calls after initialization having no effect. No local tests.
