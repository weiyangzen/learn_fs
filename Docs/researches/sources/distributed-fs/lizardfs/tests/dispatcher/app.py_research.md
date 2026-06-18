# sources/distributed-fs/lizardfs/tests/dispatcher/app.py

## Purpose
`dispatcher/app.py` provides a small Flask service that coordinates distributed test execution. It stores per-build, per-suite queues of test names and hands out the next test atomically within the single-process Flask app.

## Important APIs, Types, and Functions
`create_app()` builds the Flask app, initializes `current_app.config["tests"]`, and registers `/`, `/push_list`, and `/next_test`. Type aliases document the nested shape: build id -> suite -> list of tests.

## Control Flow
`GET /` returns the current in-memory queue map. `POST /push_list` reads JSON with `build_id`, `test_suite`, and `tests`, rejects duplicate suite lists for the same build with HTTP 412, and stores the queue. `GET /next_test` validates query arguments, returns an empty detail for missing queues, pops the first queued test, and removes empty suite/build containers.

## State and Persistence Behavior
All state is in Flask process memory. Restarting the service loses queues; concurrent access relies on the deployment being single-threaded or externally serialized. The provided Dockerfile runs waitress with one thread, matching that assumption.

## Dependencies and Integration Points
It depends on Flask and JSON. The dispatcher client posts gtest-derived test lists and asks for next tests from build agents.

## Risks and Edge Cases
The code uses `assert json_data is not None`, which can be disabled under optimized Python and yields 500-style behavior for bad payloads. There is no authentication, persistence, locking, or schema validation. Running with multiple workers/threads would race list mutation.

## Test Signals
HTTP tests should cover duplicate push, missing args, empty queues, pop order, cleanup of empty build/suite entries, bad JSON, and multi-client behavior under the intended one-thread deployment.
