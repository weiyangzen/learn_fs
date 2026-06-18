## sources/distributed-fs/ipfs-kubo/test/sharness/t0322-pubsub-http-rpc.sh

Purpose: validates HTTP RPC input validation for `/api/v0/pubsub/pub` topic arguments.

Important commands and control flow: initializes and launches a daemon with pubsub enabled. It posts multipart data to `pubsub/pub?arg=foobar` and expects an error that URL args must be multibase encoded. It then posts with a regular base64 multibase prefix and expects an error requiring URL-safe base64url.

State and persistence: only daemon runtime pubsub/API state and temporary data/result files are used.

Dependencies and integration points: depends on HTTP API routing, pubsub command argument parsing, multibase validation, `curl`, and sharness `test_should_contain`.

Risks and test signals: targeted regression coverage for browser/HTTP-safe pubsub topic encoding. Sensitive to exact error text.
