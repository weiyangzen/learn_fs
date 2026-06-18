# sources/cloud-native/containerd/internal/cri/opts/spec_windows.go

## Purpose

This Windows-only file implements Windows process command-line/args composition, including Docker `ArgsEscaped` compatibility.

## Important APIs, Types, and Functions

`escapeAndCombineArgsWindows` escapes args with `windows.EscapeArg`. `WithProcessCommandLineOrArgsForWindows` chooses between setting a single command line and setting OCI process args depending on image `ArgsEscaped`. `getArgs` merges image entrypoint/cmd with CRI command/args and reports whether the first arg came from the image.

## Control Flow

When `ArgsEscaped` is true, the option gets merged args. If the first arg came from the image, it keeps that first element as already escaped and escapes/joins the rest; otherwise it escapes all args. It then sets `Process.CommandLine`. When `ArgsEscaped` is false, it sets `Process.Args`. `getArgs` follows Docker-like override behavior and errors when no command remains.

## State and Persistence Behavior

The returned options mutate only the in-memory OCI process fields.

## Dependencies and Integration Points

It depends on Windows arg escaping, image specs, CRI configs, and containerd OCI helpers. Windows spec construction uses this instead of `WithProcessArgs`.

## Risks and Edge Cases

Nil versus empty command slices affect override semantics. `ArgsEscaped` is deprecated but needed for Windows image compatibility. Incorrect escaping can change container entrypoint execution.

## Test Signals

Windows tests should cover image-only, CRI override, image `ArgsEscaped`, no-command errors, and command-line versus args field selection.
