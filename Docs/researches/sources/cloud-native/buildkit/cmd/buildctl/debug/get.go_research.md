# Research: sources/cloud-native/buildkit/cmd/buildctl/debug/get.go

Purpose: implements `buildctl debug get`, a low-level content-store blob retrieval command. It streams a blob addressed by digest from the daemon content service to stdout.

Important APIs and flow: `get` requires a digest argument, parses it, resolves the BuildKit client, creates a proxy content store over `c.ContentClient()`, opens a `ReaderAt` with an OCI descriptor, and copies the content to stdout using a 1 MiB buffer.

State and dependencies: no local persistence. It reads daemon content-store state and depends on containerd content/proxy APIs, OCI descriptors, digest parsing, and app context.

Risks and test signals: stdout receives raw blob bytes, so users can corrupt terminals if retrieving binary content. Errors are mainly invalid digest or missing content. There are no direct tests in this group.
