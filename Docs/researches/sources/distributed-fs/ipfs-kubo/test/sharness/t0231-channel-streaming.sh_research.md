## sources/distributed-fs/ipfs-kubo/test/sharness/t0231-channel-streaming.sh

Purpose: tests that channel-streaming API output is newline-delimited rather than concatenated JSON objects.

Important APIs and helpers: defines `get_api_port` and `test_ls_cmd`, uses `random-data`, `ipfs add`, `curl http://localhost:<port>/api/v0/refs/<hash>`, `grep`, and daemon lifecycle helpers.

Control flow and state: adds a large random file, calls the refs API through the daemon, writes output to a file, and asserts the stream does not contain adjacent `}{` JSON boundaries without separators.

Dependencies and integration points: covers API port discovery, refs endpoint streaming, JSON event framing, and daemon HTTP response behavior.

Risks and test signals: catches response framing regressions that break streaming clients. Passing requires grep not finding `}{` in the response.
